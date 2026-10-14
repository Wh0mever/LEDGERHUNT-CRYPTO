import json
import logging

import httpx
import pytest

from ledgerhunt.core.http import (
    HttpStatusError,
    RecordingClient,
    ReplayMiss,
    RequestFailed,
    ResponseStore,
    canonical_request_key,
    endpoint_template,
)
from ledgerhunt.core.redact import register_secret

FAKE_KEY = "fake-trongrid-key-6f1c2b9a8d7e"
FAKE_URL_SECRET = "https://paid.example.net/fakeembeddedkey0123456789"


class Recorder:
    """Fake transport: records requests and answers from a scripted list or a function."""

    def __init__(self, responses=None, handler=None):
        self.requests: list[httpx.Request] = []
        self.responses = list(responses or [])
        self.handler = handler

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        if self.handler:
            return self.handler(request)
        item = self.responses.pop(0)
        if isinstance(item, Exception):
            raise item
        return item


def make_client(tmp_path, rec: Recorder, **kw) -> RecordingClient:
    kw.setdefault("store_dir", tmp_path / "store")
    kw.setdefault("shared_limiter", False)
    kw.setdefault("rate_limits", {"api.example.org": 0, "paid.example.net": 0})
    kw.setdefault("default_rps", 0)
    kw.setdefault("sleep", lambda s: None)
    return RecordingClient(transport=httpx.MockTransport(rec), **kw)


def ok_json(obj, status=200, headers=None):
    return httpx.Response(status, json=obj, headers=headers or {})


def test_record_then_replay_roundtrip(tmp_path):
    rec = Recorder(handler=lambda r: ok_json({"echo": r.url.params.get("a"), "amount": 1.25}))
    live = make_client(tmp_path, rec, mode="record")
    r1 = live.get("https://api.example.org/v1/accounts/TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t/x",
                  params={"b": 2, "a": "1"}, provider="example")
    assert r1.ok and r1.ref is not None and not r1.from_replay
    assert r1.json()["echo"] == "1"
    assert str(r1.json()["amount"]) == "1.25"  # Decimal, not float
    assert r1.endpoint == "v1/accounts/{address}/x"
    # body is stored content-addressed
    store = ResponseStore(tmp_path / "store")
    assert store.get_body(r1.ref.body_sha256) == r1.body
    # replay: same request with params in another order, no transport calls
    rec2 = Recorder(handler=lambda r: pytest.fail("network used in replay"))
    replay = make_client(tmp_path, rec2, mode="replay")
    r2 = replay.get("https://api.example.org/v1/accounts/TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t/x",
                    params={"a": "1", "b": 2}, provider="example")
    assert r2.from_replay and r2.body == r1.body and r2.status == 200
    assert r2.ref.body_sha256 == r1.ref.body_sha256
    assert rec2.requests == []
    # a different request is a clear miss
    with pytest.raises(ReplayMiss) as exc:
        replay.get("https://api.example.org/v1/other", provider="example")
    assert "replay miss" in str(exc.value)
    assert replay.metrics[-1]["error_class"] == "replay_miss"


def test_json_body_canonical_and_cache_mode(tmp_path):
    rec = Recorder(handler=lambda r: ok_json({"n": json.loads(r.content)["num"]}))
    c = make_client(tmp_path, rec, mode="cache")
    a = c.post("https://api.example.org/wallet/getblockbynum", json={"num": 5, "visible": True})
    b = c.post("https://api.example.org/wallet/getblockbynum", json={"visible": True, "num": 5})
    assert len(rec.requests) == 1 and b.from_replay and a.body == b.body
    k1 = canonical_request_key("POST", "https://API.example.org/w", None, {"b": 1, "a": 2}, "p")
    k2 = canonical_request_key("post", "https://api.example.org/w", None, {"a": 2, "b": 1}, "p")
    assert k1 == k2


def test_secrets_never_reach_index_metrics_or_logs(tmp_path, caplog):
    register_secret(FAKE_KEY)
    register_secret(FAKE_URL_SECRET)
    seen_headers = []

    def handler(r: httpx.Request) -> httpx.Response:
        seen_headers.append(r.headers.get("TRON-PRO-API-KEY"))
        if len(seen_headers) == 1:
            return ok_json({"error": "slow down"}, status=429, headers={"Retry-After": "0"})
        # server echoes the key back in the body: it must be scrubbed before storing
        return ok_json({"echo": FAKE_KEY, "ok": True})

    rec = Recorder(handler=handler)
    c = make_client(tmp_path, rec, mode="record")
    caplog.set_level(logging.DEBUG)
    r = c.post(FAKE_URL_SECRET + "/wallet/getnowblock", json={}, provider="paid",
               secret_headers={"TRON-PRO-API-KEY": FAKE_KEY}, secret_params={"apikey": FAKE_KEY})
    assert r.ok and r.attempts == 2
    assert seen_headers == [FAKE_KEY, FAKE_KEY]  # sent on the wire
    assert rec.requests[0].url.params.get("apikey") == FAKE_KEY
    # stored body scrubbed
    assert FAKE_KEY.encode() not in r.body and r.meta["body_redacted"]
    index_text = (tmp_path / "store" / "index.jsonl").read_text(encoding="utf-8")
    metrics_path = c.dump_metrics(tmp_path / "metrics.jsonl")
    metrics_text = metrics_path.read_text(encoding="utf-8")
    for text in (index_text, metrics_text, caplog.text, r.url, json.dumps(c.metrics_summary())):
        assert FAKE_KEY not in text
        assert "fakeembeddedkey0123456789" not in text
    assert "***/wallet/getnowblock" in index_text
    assert "429" in caplog.text  # the retry was logged (redacted)


def test_retry_on_5xx_and_timeouts_then_fail(tmp_path):
    rec = Recorder([
        httpx.Response(503, text="busy"),
        httpx.ReadTimeout("t"),
        ok_json({"ok": 1}),
    ])
    sleeps = []
    c = make_client(tmp_path, rec, mode="record", sleep=sleeps.append)
    r = c.get("https://api.example.org/x")
    assert r.ok and r.attempts == 3 and len(sleeps) == 2
    assert c.metrics[-1]["attempt_statuses"] == [503, None, 200]

    rec2 = Recorder([httpx.ConnectError("down")] * 3)
    c2 = make_client(tmp_path, rec2, mode="record", max_attempts=3)
    with pytest.raises(RequestFailed) as exc:
        c2.get("https://api.example.org/y")
    assert exc.value.error_class == "connect_error" and exc.value.attempts == 3
    assert c2.metrics[-1]["error_class"] == "connect_error"


def test_non_2xx_returned_and_raise_for_status(tmp_path):
    rec = Recorder([httpx.Response(404, json={"message": "not found"})])
    c = make_client(tmp_path, rec, mode="record")
    r = c.get("https://api.example.org/missing")
    assert r.status == 404 and not r.ok and r.ref is not None
    with pytest.raises(HttpStatusError):
        r.raise_for_status()
    assert c.metrics_summary()[0]["errors"] == 1


def test_429_penalty_uses_limiter(tmp_path):
    rec = Recorder([httpx.Response(429), ok_json({})])
    c = make_client(tmp_path, rec, mode="live", penalty_429={"api.example.org": 5.0})
    calls = []
    c.limiter.penalize = lambda key, s: calls.append((key, s))
    r = c.get("https://api.example.org/z")
    assert r.ok and calls and calls[0][0] == "api.example.org" and calls[0][1] >= 5.0
    assert r.ref is None  # live mode stores nothing


def test_endpoint_template():
    assert endpoint_template("/v1/transactions/" + "a" * 64 + "/events") == "v1/transactions/{hash}/events"
    assert endpoint_template("/api/v2/addresses/0x" + "b" * 40) == "api/v2/addresses/{address}"
    assert endpoint_template("/wallet/getblockbynum") == "wallet/getblockbynum"


def test_replay_process_refuses_live_requests(tmp_path, monkeypatch):
    from ledgerhunt.core.http import LiveRequestInReplay

    monkeypatch.setenv("LEDGERHUNT_HTTP_MODE", "replay")
    for mode in ("live", "record", "cache"):
        c = RecordingClient(mode=mode, store_dir=tmp_path / "store", shared_limiter=False, default_rps=0,
                            sleep=lambda s: None, max_attempts=1)
        with pytest.raises(LiveRequestInReplay) as exc:
            c.get("https://example.invalid/v1/x", params={"a": 1})
        assert isinstance(exc.value, ReplayMiss) and mode in str(exc.value)
        assert c.metrics[-1]["error_class"] == "live_request_in_replay"
    # in-process transports (tests, synthetic scenario server) stay allowed
    rec = Recorder(handler=lambda r: ok_json({"ok": True}))
    assert make_client(tmp_path, rec, mode="record").get("https://api.example.org/x").ok
