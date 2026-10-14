"""Deterministic generator of the development and held-out scenario sets.

Layout of one scenario directory (``tests/scenarios/<split>/<scenario_id>/``)::

    input.json     what a tracer gets: start TXID, parameters, context (labels, supported
                   bridges), store location, request profile. Neutral: no category, no hints.
    expected.json  the answer (schema ledgerhunt.scenario-result/1) plus meta (category, variant).
    world.json     the generator's full ground truth (all transactions, outages, bridge messages).
    http-store/    raw responses recorded through the real foundation clients
                   (index.jsonl + objects/<sha[:2]>/<sha256>), replayable with
                   RecordingClient(mode="replay", store_dir=<scenario>/http-store).

Recorded request profile ``scenario-profile/1`` (every address and transaction of the world):
- TronGridClient(api_key=None).trc20_transfers(addr)          all pages, limit=200, asc, USDT
- TronGridClient.account_transactions(addr)                    all pages, limit=200, asc
- TronGridClient.trc20_balance_of(addr)                        triggerconstantcontract balanceOf
- TronGridClient.transaction_events(txid)
- TronGridClient.get_transaction_by_id(txid) / get_transaction_info_by_id(txid)
- TronNodeClient() (PublicNode, the second operator) get_transaction_by_id / get_transaction_info_by_id
- LayerZeroScanClient.messages_by_tx(txid) / message_by_guid(guid) for every OFT send
Requests outside the profile are not in the store (replay raises ReplayMiss); use
``ScenarioServer(world).transport()`` for other query shapes.
"""

from __future__ import annotations

import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ..core.http import RecordingClient
from ..core.ratelimit import DEFAULT_RATE_LIMITS, RateLimiter
from ..sources import LayerZeroScanClient, SourceError, TronGridClient, TronNodeClient
from .builder import Builder
from .rng import DetRng
from .server import ScenarioServer
from .templates import CATEGORIES
from .world import World

GENERATOR_VERSION = "scenario-generator/1"
REQUEST_PROFILE = "scenario-profile/1"
DEV_SEED = "ledgerhunt/scenarios/dev/2026-10-14"
DEV_PREFIX = "dev"
HOLDOUT_PREFIX = "hold"
HOLDOUT_PER_CATEGORY = 3
START_MIN_MS = 1_769_904_000_000  # 2026-02-01 00:00:00 UTC
START_SPAN_S = 200 * 86_400
PROVIDERS = {"primary_index": "trongrid", "secondary_receipts": "tron_publicnode", "bridge_api": "layerzero_scan"}


def dumps(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, indent=1) + "\n"


def plan(split: str, seed: str) -> list[dict[str, Any]]:
    """Which (category, variant) each scenario of a split uses, in a seeded shuffled order."""
    rng = DetRng(seed).fork("plan")
    items: list[tuple[str, int]] = []
    for cat, variants in CATEGORIES.items():
        if split == "dev":
            items.extend((cat, i) for i in range(len(variants)))
        else:
            items.extend((cat, i) for i in sorted(rng.fork(cat).sample(range(len(variants)), HOLDOUT_PER_CATEGORY)))
    rng.shuffle(items)
    prefix = DEV_PREFIX if split == "dev" else HOLDOUT_PREFIX
    return [{"scenario_id": f"{prefix}-{n:03d}", "category": c, "variant_index": v, "variant": CATEGORIES[c][v][0]}
            for n, (c, v) in enumerate(items, 1)]


def build(split: str, seed: str, item: dict[str, Any]) -> tuple[dict[str, Any], World, dict[str, Any]]:
    sid, cat, vi = item["scenario_id"], item["category"], item["variant_index"]
    variant, template = CATEGORIES[cat][vi]
    rng = DetRng(seed).fork(f"{cat}/{variant}")
    start_ms = START_MIN_MS + 1000 * rng.randint(0, START_SPAN_S)
    b = Builder(rng.fork("world"), sid, start_ms=start_ms)
    title_ru, description = template(b)
    world, expected = b.finalize()
    expected["meta"] = {"category": cat, "variant": variant, "title_ru": title_ru, "description": description,
                        "split": split, "generator": GENERATOR_VERSION, "max_depth": b.max_depth,
                        "affected_by_source_failure": bool(expected["outages"])}
    inp = {
        "schema": "ledgerhunt.scenario-input/1",
        "scenario_id": sid,
        "split": split,
        "synthetic": True,
        "start": {"chain": "tron", "txid": b.start_txid},
        "params": {"max_depth": b.max_depth, "asset": "USDT-TRC20", "token_contract": "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t",
                   "snapshot_utc": _iso_ms(world.snapshot_ms)},
        "context": {"labels": world.labels, "supported_bridges": [{"protocol": "usdt0_oft", "dst_eids": [30101]}]},
        "store": "http-store",
        "request_profile": REQUEST_PROFILE,
        "providers": PROVIDERS,
        "reference": None,
    }
    return inp, world, expected


def _iso_ms(ms: int) -> str:
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def record_store(world: World, store_dir: Path, *, tag: str) -> dict[str, int]:
    """Record the request profile through the real clients into ``store_dir`` (deterministic)."""
    if store_dir.exists():
        shutil.rmtree(store_dir)
    server = ScenarioServer(world)
    limiter = RateLimiter({h: 0.0 for h in DEFAULT_RATE_LIMITS}, default_rps=0.0, state_dir=None)
    http = RecordingClient(mode="record", store_dir=store_dir, limiter=limiter, transport=server.transport(),
                           max_attempts=1, sleep=lambda s: None, tag=tag)
    tg = TronGridClient(http, api_key=None)
    pn = TronNodeClient(http)
    lz = LayerZeroScanClient(http)
    failures = 0

    def attempt(fn, *a, **kw) -> None:
        nonlocal failures
        try:
            fn(*a, **kw)
        except SourceError:
            failures += 1

    try:
        for addr in world.addresses():
            attempt(tg.trc20_transfers, addr)
            attempt(tg.account_transactions, addr)
            attempt(tg.trc20_balance_of, addr)
        for tx in world.txs:
            txid = tx["txid"]
            attempt(tg.transaction_events, txid)
            attempt(tg.get_transaction_by_id, txid)
            attempt(tg.get_transaction_info_by_id, txid)
            attempt(pn.get_transaction_by_id, txid)
            attempt(pn.get_transaction_info_by_id, txid)
        for txid, msg in sorted(world.lz.items()):
            attempt(lz.messages_by_tx, txid)
            attempt(lz.message_by_guid, "0x" + msg["guid"])
    finally:
        http.close()
    _normalise_index(store_dir / "index.jsonl", world.snapshot_ms)
    lock = store_dir / ".index.lock"
    if lock.exists():
        lock.unlink()
    return {"requests": server.requests, "failed_by_design": failures}


def _normalise_index(path: Path, snapshot_ms: int) -> None:
    """Make the index byte-identical between runs: fixed timestamp, zero latency."""
    ts = datetime.fromtimestamp(snapshot_ms / 1000, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000000Z")
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        for r in rows:
            r["ts_utc"] = ts
            r["latency_ms"] = 0.0
            fh.write(json.dumps(r, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n")


def write_scenario(directory: Path, inp: dict[str, Any], world: World, expected: dict[str, Any], *,
                   tag: str) -> dict[str, Any]:
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "input.json").write_text(dumps(inp), encoding="utf-8", newline="\n")
    (directory / "world.json").write_text(dumps(world.to_dict()), encoding="utf-8", newline="\n")
    (directory / "expected.json").write_text(dumps(expected), encoding="utf-8", newline="\n")
    stats = record_store(world, directory / "http-store", tag=tag)
    return {"txs": len(world.txs), "addresses": len(world.addresses()), "routes": len(expected["routes"]), **stats}


def generate_split(split: str, seed: str, out_dir: Path) -> list[dict[str, Any]]:
    """Generate every scenario of a split into ``out_dir/<scenario_id>/``; return per-scenario stats."""
    out_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for item in plan(split, seed):
        inp, world, expected = build(split, seed, item)
        stats = write_scenario(out_dir / item["scenario_id"], inp, world, expected,
                               tag=f"scenarios/{split}/{item['scenario_id']}")
        rows.append({**item, **stats})
    return rows


def seed_digest(seed: str) -> str:
    return hashlib.sha256(seed.encode("utf-8")).hexdigest()
