"""Validation of scenario directories and of the synthetic raw formats.

``validate_scenario`` checks one scenario:
1. schema of input.json and expected.json;
2. store integrity: every indexed body exists and its sha256 matches its name;
3. replay: the request profile replays through the real foundation clients
   (RecordingClient mode=replay) with no ReplayMiss, and the rows equal the world
   (designed failures must fail, everything else must succeed);
4. answer consistency: every counted expected transfer exists on the synthetic chain,
   routes are connected and time-ordered, start at the input TXID and respect max_depth,
   exchange sweeps and bridge exits match the raw data, no trap is part of the answer;
5. self-score: the expected answer scored as a candidate passes with recall 1.0.

``format_parity`` compares key structures of synthetic bodies with real bodies recorded
in data/http-store (when present) per endpoint.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

from ..core.http import RecordingClient, ReplayMiss, ResponseStore
from ..core.ratelimit import DEFAULT_RATE_LIMITS, RateLimiter
from ..core.tron import parse_amount
from ..sources import LayerZeroScanClient, SourceError, TronGridClient, TronNodeClient
from ..sources.layerzero_scan import found as lz_found
from .schema import ScenarioInput, TraceResult
from .scorer import candidate_from_expected, score_scenario
from .world import World


def _client(store: Path) -> RecordingClient:
    limiter = RateLimiter({h: 0.0 for h in DEFAULT_RATE_LIMITS}, default_rps=0.0, state_dir=None)
    return RecordingClient(mode="replay", store_dir=store, limiter=limiter, sleep=lambda s: None, max_attempts=1)


def _designed(world: World, role: str, endpoint: str, target: str) -> bool:
    for o in world.outages:
        if o["role"] == role and o.get("endpoint", "*") in ("*", endpoint) and o.get("target", "*") in ("*", target):
            return True
    return False


def store_integrity(store: Path) -> tuple[int, int, int, list[str]]:
    errors: list[str] = []
    rows = ResponseStore(store).rows()
    shas = set()
    for r in rows:
        sha = r.get("body_sha256")
        if not sha:
            continue
        p = store / "objects" / sha[:2] / sha
        if not p.is_file():
            errors.append(f"missing object {sha}")
            continue
        if sha not in shas:
            shas.add(sha)
            if hashlib.sha256(p.read_bytes()).hexdigest() != sha:
                errors.append(f"object hash mismatch {sha}")
    size = sum((store / "objects" / s[:2] / s).stat().st_size for s in shas if (store / "objects" / s[:2] / s).is_file())
    return len(rows), len(shas), size, errors


def replay_check(world: World, store: Path) -> list[str]:
    errors: list[str] = []
    http = _client(store)
    tg = TronGridClient(http, api_key=None)
    pn = TronNodeClient(http)
    lz = LayerZeroScanClient(http)

    def run(label: str, designed_fail: bool, fn, *a, check=None, **kw) -> None:
        try:
            res = fn(*a, **kw)
        except ReplayMiss:
            errors.append(f"replay miss: {label}")
            return
        except SourceError:
            if not designed_fail:
                errors.append(f"unexpected source error: {label}")
            return
        if designed_fail and label.startswith("trc20 ") and getattr(res, "complete", True):
            errors.append(f"designed failure did not fail: {label}")
            return
        if check is not None:
            msg = check(res)
            if msg:
                errors.append(f"{label}: {msg}")

    try:
        for addr in world.addresses():
            listing_fail = _designed(world, "trongrid_v1", "trc20", addr)
            n_rows = len(world.trc20_rows(addr))
            run(f"trc20 {addr}", listing_fail, tg.trc20_transfers, addr,
                check=lambda p, n=n_rows: None if len(p.rows) == n else f"{len(p.rows)} rows, world has {n}")
            n_tx = len(world.account_txs(addr))
            run(f"account txs {addr}", False, tg.account_transactions, addr,
                check=lambda p, n=n_tx: None if len(p.rows) == n else f"{len(p.rows)} rows, world has {n}")
            bal = max(0, world.balance(addr))
            run(f"balance {addr}", False, tg.trc20_balance_of, addr,
                check=lambda r, b=bal: None if r[0] == b else f"balanceOf {r[0]} != {b}")
        for tx in world.txs:
            txid = tx["txid"]
            n_ev = len(world.events(txid))
            run(f"events {txid}", _designed(world, "trongrid_v1", "events", txid), tg.transaction_events, txid,
                check=lambda f, n=n_ev: None if len(f.data["data"]) == n else "event count differs")
            run(f"tg tx {txid}", False, tg.get_transaction_by_id, txid,
                check=lambda f, t=txid: None if f.data.get("txID") == t else "txID differs")
            run(f"tg info {txid}", False, tg.get_transaction_info_by_id, txid)
            run(f"pn tx {txid}", _designed(world, "secondary_node", "gettransactionbyid", txid), pn.get_transaction_by_id, txid)
            run(f"pn info {txid}", _designed(world, "secondary_node", "gettransactioninfobyid", txid),
                pn.get_transaction_info_by_id, txid,
                check=lambda f, t=txid: None if f.data.get("id") == t else "receipt id differs")
        for txid, msg in world.lz.items():
            down = _designed(world, "layerzero_scan", "messages_tx", txid)
            run(f"lz tx {txid}", down, lz.messages_by_tx, txid,
                check=lambda f, m=msg: None if lz_found(f) == bool(m["indexed"]) else "found flag differs")
    finally:
        http.close()
    return errors


def _event_path_ok(world: World, txids: list[str], start_from: str | None, terminal: str) -> str | None:
    holders = {start_from} if start_from else None
    last_ts = 0
    for i, txid in enumerate(txids):
        tx = world.tx(txid)
        if tx is None:
            return f"route txid {txid} not in world"
        if tx["ts_ms"] < last_ts:
            return f"route goes back in time at {txid}"
        last_ts = tx["ts_ms"]
        evs = [e for e in world.usdt_events(tx) if e["name"] == "Transfer" and int(e["args"]["value"]) > 0]
        if holders is not None:
            evs = [e for e in evs if e["args"]["from"] in holders]
        if not evs:
            return f"route breaks at {txid}"
        holders = {e["args"]["to"] for e in evs}
    if terminal not in (holders or set()):
        return "terminal address is not the last recipient"
    return None


def answer_check(inp: ScenarioInput, exp: TraceResult, world: World) -> list[str]:
    errors: list[str] = []
    wt = {(t["txid"], t["event_index"]): t for t in world.transfers()}
    max_depth = int(inp.params["max_depth"])
    for t in exp.transfers:
        w = wt.get((t.txid, t.event_index))
        if w is None:
            errors.append(f"expected transfer {t.txid}:{t.event_index} not in world")
            continue
        if (w["from"], w["to"]) != (t.from_address, t.to_address) or str(w["value"]) != t.amount.replace(".", "").lstrip("0") \
                and not (w["value"] == 0 and t.amount == "0.000000"):
            errors.append(f"expected transfer {t.txid}:{t.event_index} differs from world")
        if w["hidden"] and t.excluded != "source_data_gap":
            errors.append(f"hidden transfer {t.txid} counted without exclusion")
    victim = world.tx(inp.start["txid"])
    victim_addr = victim["events"][0]["args"]["from"] if victim and victim["events"] else None
    for r in exp.routes:
        if r.txids[0] != inp.start["txid"]:
            errors.append(f"route {r.route_id} does not start at the start txid")
        if len(r.txids) > max_depth:
            errors.append(f"route {r.route_id} longer than max_depth")
        msg = _event_path_ok(world, r.txids, victim_addr, r.terminal.address)
        if msg:
            errors.append(f"route {r.route_id}: {msg}")
    labels = {lab["address"]: lab for lab in world.labels}
    for d in exp.exchange_deposits:
        if labels.get(d.hot_wallet, {}).get("type") != "exchange_hot_wallet":
            errors.append(f"hot wallet of {d.deposit_address} not labelled")
        for s in d.sweep_txids:
            ok = any(t["txid"] == s and t["from"] == d.deposit_address and t["to"] == d.hot_wallet for t in world.transfers())
            if not ok:
                errors.append(f"sweep {s} is not deposit -> hot wallet")
    for b in exp.bridge_exits:
        tx = world.tx(b.txid)
        if tx is None:
            errors.append(f"bridge tx {b.txid} not in world")
            continue
        if b.protocol == "usdt0_oft":
            oft = [e for e in tx["events"] if e["name"] == "OFTSent"]
            if not oft or int(oft[0]["args"]["dstEid"]) != b.dst_eid:
                errors.append(f"bridge {b.txid}: OFTSent missing or dstEid differs")
    trap_keys = {(t.txid, t.event_index) for t in exp.traps}
    for t in exp.transfers:
        if not t.excluded and ((t.txid, t.event_index) in trap_keys or (t.txid, None) in trap_keys):
            errors.append(f"trap {t.txid} is part of the answer")
    return errors


def validate_scenario(sdir: Path, *, replay: bool = True) -> dict[str, Any]:
    out: dict[str, Any] = {"scenario_id": sdir.name, "ok": False, "errors": []}
    try:
        inp = ScenarioInput.model_validate(json.loads((sdir / "input.json").read_text(encoding="utf-8")))
        exp = TraceResult.model_validate(json.loads((sdir / "expected.json").read_text(encoding="utf-8")))
    except Exception as exc:  # noqa: BLE001 - report any schema problem
        out["errors"].append(f"schema: {type(exc).__name__}: {str(exc)[:300]}")
        return out
    if inp.reference:  # reference scenario (case-001): no synthetic world
        out.update(ok=True, reference=True)
        return out
    world = World.load(sdir / "world.json")
    store = sdir / (inp.store or "http-store")
    rows, objects, size, errs = store_integrity(store)
    out["errors"].extend(errs)
    if replay:
        out["errors"].extend(replay_check(world, store))
    out["errors"].extend(answer_check(inp, exp, world))
    sc = score_scenario(exp, candidate_from_expected(exp), world)
    if not sc.passed or sc.counts["missed"] or sc.counts["weaker"]:
        out["errors"].append("self-score: expected answer does not score 100% against itself")
    out["category"] = (exp.meta or {}).get("category")
    out["stats"] = {
        "txs": len(world.txs), "addresses": len(world.addresses()), "routes": len(exp.routes),
        "max_route_len": max((len(r.txids) for r in exp.routes), default=0),
        "transfers_counted": sum(1 for t in exp.transfers if not t.excluded),
        "facts_excluded": sum(1 for t in exp.transfers if t.excluded),
        "store_rows": rows, "store_objects": objects, "store_bytes": size,
        "designed_failures": len(exp.outages),
    }
    out["ok"] = not out["errors"]
    return out


# ---------------------------------------------------------------- format parity


_ADDR_KEY = re.compile(r"^0x[0-9a-fA-F]{40}$")


def _shape(obj: Any, prefix: str = "", skip: tuple[str, ...] = ()) -> set[str]:
    """Key paths of a JSON body; address-shaped keys (e.g. DVN maps) become '{address}'."""
    paths: set[str] = set()
    if any(prefix == s or prefix.startswith(s + ".") for s in skip):
        return paths
    if isinstance(obj, dict):
        for k, v in obj.items():
            k = "{address}" if _ADDR_KEY.match(k) else k
            p = f"{prefix}.{k}" if prefix else k
            paths.add(p)
            paths |= _shape(v, p, skip)
    elif isinstance(obj, list):
        for v in obj:
            paths |= _shape(v, prefix + "[]", skip)
    return paths


PARITY_ENDPOINTS = [
    ("trongrid", "v1/accounts/{address}/transactions/trc20", ()),
    ("trongrid", "v1/accounts/{address}/transactions", ("data[].raw_data.contract[].parameter.value",)),
    ("trongrid", "v1/transactions/{hash}/events", ()),
    ("trongrid", "wallet/gettransactionbyid", ("raw_data.contract[].parameter.value",)),
    ("trongrid", "walletsolidity/gettransactioninfobyid", ()),
    ("trongrid", "wallet/triggerconstantcontract", ()),
    ("layerzero_scan", "v1/messages/tx/{hash}", ()),
]


def _bodies(store: Path, provider: str, endpoint: str, *, limit: int = 400) -> list[Any]:
    out = []
    for r in ResponseStore(store).rows():
        if r.get("provider") == provider and r.get("endpoint") == endpoint and r.get("status") == 200 and r.get("body_sha256"):
            p = store / "objects" / r["body_sha256"][:2] / r["body_sha256"]
            try:
                out.append(json.loads(p.read_bytes()))
            except (OSError, ValueError):
                continue
            if len(out) >= limit:
                break
    return out


def format_parity(real_store: Path, scenario_dirs: list[Path]) -> list[dict[str, Any]]:
    """Per endpoint: key paths present in real recorded bodies but not in synthetic ones, and vice versa."""
    report = []
    for provider, endpoint, skip in PARITY_ENDPOINTS:
        real = _bodies(real_store, provider, endpoint) if real_store.is_dir() else []
        synth: list[Any] = []
        for d in scenario_dirs:
            synth.extend(_bodies(d / "http-store", provider, endpoint, limit=50))
        if endpoint.endswith("/events"):
            real = [x for x in real if x.get("data")]
            synth = [x for x in synth if x.get("data")]
        rs = set().union(*(_shape(b, skip=skip) for b in real)) if real else set()
        ss = set().union(*(_shape(b, skip=skip) for b in synth)) if synth else set()
        report.append({
            "provider": provider, "endpoint": endpoint, "real_samples": len(real), "synthetic_samples": len(synth),
            "checked": bool(real and synth),
            "missing_in_synthetic": sorted(rs - ss) if real and synth else None,
            "extra_in_synthetic": sorted(ss - rs) if real and synth else None,
        })
    return report
