"""End-to-end secret hygiene: fake keys go in through config, never come out.

Fake secrets are set as real environment variables (they take precedence over .env),
loaded through ledgerhunt.core.config, used by the real source clients over a mock
transport that echoes them back (bodies, 4xx/5xx, transport errors), and then every
artefact is scanned: the HTTP store (index + bodies), metrics, the results run folder
(config.json, raw files, summary) and the log stream including tracebacks.
"""

from __future__ import annotations

import io
import json
import logging

import httpx
import pytest

from ledgerhunt.core import config
from ledgerhunt.core.http import RecordingClient, RequestFailed
from ledgerhunt.core.log import RedactingFilter, RedactingFormatter
from ledgerhunt.core.results import start_run
from ledgerhunt.sources import NearIntentsClient, SourceError, TronGridClient, TronNodeClient
from ledgerhunt.sources.case001_etherscan import EtherscanNameTag

FAKE = {
    "TRONGRID_API_KEY": "e2e-fake-trongrid-0f9e8d7c6b5a4",
    "ETHERSCAN_API_KEY": "E2EFAKEETHERSCANKEY0123456789AB",
    "NEAR_INTENTS_JWT": "e2e.fake-jwt-payload-9a8b7c6d5e4f.sig",
    "TRON_RPC_URL": "https://paid-tron.example.net/e2e-fake-path-key-77aa88bb99cc",
}
URL_KEY_PART = "e2e-fake-path-key-77aa88bb99cc"
TXID = "98f3ffca9d141f2172d28f46905c08e5f32fc6ce8d23f9a37b731fe2a6c1d1bb"


def _echo(request: httpx.Request) -> httpx.Response:
    """Echo whatever secret-bearing parts the request carried."""
    echoed = {
        "url": str(request.url),
        "auth": request.headers.get("Authorization"),
        "tron_key": request.headers.get("TRON-PRO-API-KEY"),
    }
    host = request.url.host
    if host == "api.trongrid.io" and "events" in request.url.path:
        return httpx.Response(429, json={"Error": f"key {echoed['tron_key']} over limit", **echoed})
    if host == "api.etherscan.io":
        raise httpx.ConnectError(f"connection refused while fetching {request.url}")
    if host == "paid-tron.example.net":
        return httpx.Response(500, text=f"upstream failure at {request.url}")
    return httpx.Response(200, json={"ok": True, **echoed})


def _scan(tmp_path) -> dict[str, list[str]]:
    leaks: dict[str, list[str]] = {}
    for p in tmp_path.rglob("*"):
        if not p.is_file():
            continue
        data = p.read_bytes()
        needles = [*FAKE.items(), ("TRON_RPC_URL (path part)", URL_KEY_PART)]
        for name, needle in needles:
            if needle.encode() in data:
                leaks.setdefault(name, []).append(p.relative_to(tmp_path).as_posix())
    return leaks


def test_fake_secrets_from_config_never_reach_artefacts(tmp_path, monkeypatch):
    for name, value in FAKE.items():
        monkeypatch.setenv(name, value)
    config.load_env(force=True)
    presence = config.secrets_presence()
    assert all(presence[n] is True for n in FAKE)

    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(RedactingFormatter("%(levelname)s %(name)s: %(message)s"))
    handler.addFilter(RedactingFilter())
    root = logging.getLogger()
    root.addHandler(handler)
    old_level = root.level
    root.setLevel(logging.DEBUG)
    try:
        ctx = start_run("e2e-secrets", root=tmp_path / "results",
                        argv=["prog", "--key", FAKE["TRONGRID_API_KEY"], f"--url={FAKE['TRON_RPC_URL']}"],
                        config={"note": f"configured with {FAKE['ETHERSCAN_API_KEY']}"})
        http = RecordingClient(mode="record", store_dir=tmp_path / "store", shared_limiter=False, default_rps=0,
                               rate_limits={"api.trongrid.io": 0, "api.trongrid.io#key": 0}, max_attempts=2,
                               sleep=lambda s: None, transport=httpx.MockTransport(_echo), tag="e2e")
        ctx.track_client(http)

        tg = TronGridClient(http)  # keyed through config
        assert tg.has_key
        ok = tg.trc20_transfers_page("TNakrL7VUMLNN4EEpi64HKjj5YqafR5tUx")
        rows = [{"data": ok.data, "url": ok.url, "raw": ok.ref_dict()}]
        with pytest.raises(SourceError) as e429:
            tg.transaction_events(TXID)
        paid = TronNodeClient.from_env("TRON_RPC_URL", http)
        with pytest.raises(SourceError) as e500:
            paid.get_now_block()
        near = NearIntentsClient(http)
        st = near.status("TCiwRNyeUK7JwkEgF5W3AExFpZ2ErRZG4C")
        rows.append({"data": st.data, "url": st.url})
        es = EtherscanNameTag(http)
        with pytest.raises(RequestFailed) as efail:
            es.address_tag("0x4079a0e8d4a8a2a7d5e3a1b6c0f9e8d7c6b5926d")
        log = logging.getLogger("ledgerhunt.e2e")
        for exc in (e429.value, e500.value, efail.value):
            try:
                raise exc
            except Exception:  # noqa: BLE001
                log.exception("source failed: %s", exc)
        log.warning("raw secret in a message: %s / %s", FAKE["NEAR_INTENTS_JWT"], FAKE["TRON_RPC_URL"])
        ctx.write_jsonl("raw/rows.jsonl", rows)
        ctx.write_text("raw/errors.txt", "\n".join(str(x.value) for x in (e429, e500, efail)))
        ctx.finish({"errors": [str(e429.value), str(e500.value), str(efail.value)], "secret": FAKE})
        http.dump_metrics(tmp_path / "metrics.jsonl")
    finally:
        root.removeHandler(handler)
        root.setLevel(old_level)
    (tmp_path / "log.txt").write_text(stream.getvalue(), encoding="utf-8")

    assert "source failed" in stream.getvalue() and "Traceback" in stream.getvalue()
    assert (tmp_path / "store" / "index.jsonl").stat().st_size > 0
    assert _scan(tmp_path) == {}
    cfg = json.loads(next((tmp_path / "results" / "e2e-secrets").glob("*/config.json")).read_text(encoding="utf-8"))
    assert all(isinstance(v, bool) for v in cfg["secrets_present"].values())
