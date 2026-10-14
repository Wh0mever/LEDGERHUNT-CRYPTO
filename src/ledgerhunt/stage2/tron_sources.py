"""Stage 2 area 'tron_sources' (decisions 4.1): TRON data sources measured on case-001.

Sources (switched on automatically by what .env holds; only presence booleans are recorded):
  trongrid_key      TronGrid with TRONGRID_API_KEY (v1 index + node API + /jsonrpc)
  trongrid_keyless  TronGrid forced keyless (same endpoints)
  publicnode        keyless java-tron at tron-rpc.publicnode.com (development reserve)
  paid_rpc(_2)      paid TRON provider from TRON_RPC_URL(_2); otherwise «не измерено: нет ключа»

Phases (record = replayable from data/http-store; live = time-dependent, raw rows kept in the run dir):
  F freshness    (record, not replayed)  head vs solidified block per node, TronGrid v1 index lag
  D depth        (record, not replayed)  oldest block PublicNode serves (binary search), silent-gap check
  A agreement    (record, replayed)      same tx from several operators: tx + receipt byte/field equality;
                                         v1 events vs receipt logs
  C completeness (record, replayed)      TronGrid v1 TRC20 history vs node eth_getLogs over the same block
                                         window for case-001 addresses; event_index vs receipt log ordinal
  P pagination   (record, replayed)      fingerprint paging on a hot wallet and the hub (page cap)
  L load         (live, not replayed)    controlled ramp to the first 429, penalty probe, sustained run,
                                         latency p50/p95 and error share per source

Run:    python -m ledgerhunt stage2 tron_sources [--skip-load] [--phases F,D,A,C,P,L]
Replay: python -m ledgerhunt stage2 tron_sources --replay
        (A, C, P re-run from the recorded responses; F, D, L are re-summarised from the raw rows of the
        newest live run, see latest-live.json)
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from ..core.config import has_secret, secrets_presence
from ..core.http import ReplayMiss, RequestFailed
from ..core.paths import rel_to_root, repo_root, results_root
from ..core.results import start_run
from ..core.tron import USDT_TRC20
from ..sources import SourceError, is_empty
from ..sources.eth_rpc import JsonRpcError
from ..sources.tron_bench_clients import (
    BenchSource,
    block_header,
    is_result_limit_error,
    paid_source,
    publicnode_source,
    raw_request,
    transfer_from_jsonrpc_log,
    transfer_from_v1_row,
    transfers_from_receipt,
    transfers_from_v1_events,
    trongrid_source,
)
from ..sources.tron_bench_load import first_429_context, open_loop, penalty_probe, percentile, step_stats

AREA = "tron_sources"
RESULTS_AREA = "tron-sources"
FIXTURE = "tests/fixtures/case-001/case-001-ground-truth.json"
BLOCKS_PER_DAY = 28_800  # 3 s slots
GETLOGS_MAX_RANGE = 5_000  # java-tron default maxBlockRange; we stay within it

# ---------------------------------------------------------------- case-001 configuration

A_VICTIM = "TNakrL7VUMLNN4EEpi64HKjj5YqafR5tUx"
A_PAYER = "TBY9jt5TJJQnJNWudTm3AGPJ3e2FcevgQL"
A_FEE = "TDii6vao7xyWg2rKPbCPWVRpSmne8xcqYx"
A_HOP1 = "TYGdh7qysHLr3A4gVGivcRwSg79PpVzgNn"
A_HOP2 = "TYn3YpDxmduw6fuKmFE3qkRHEoE2zeCfx3"
A_BRIDGE_OUT = "TUrQNNez22bPosc9NUuNvu7pxVWbziKFYU"
A_CUT = "TRUJEtAFzBWReAUu5L83wFRvxWtrVw3sAz"
A_DUST = "TMU9a6ZWhxJNfZen7YRZ81cvVx2Go1xZTA"
A_PAYOUT = "TX5XiRXdyz7sdFwF5mnhT1QoGCpbkncpke"
A_HUB = "TYHeH2HQn7pM5fe6aYwGabz9x4yizJbwp6"
A_DEP1 = "TNJSC23oMcb5ws9tppANFTGtEDcKQgQBYQ"
A_DEP2 = "TCiwRNyeUK7JwkEgF5W3AExFpZ2ErRZG4C"
A_HOT = "TWBPGLwQw2EbqYLLw1DJnTDt2ZQ9yJW1JJ"
A_OUT3 = "TWx6Z8roV3nWTqp8FjTKZSWdWLGbcJyxxw"
A_OUT4 = "TP5KYiUg6pT6LF6ar88UpCV2Q6wnFSgHdE"
THEFT_BLOCK = 86439360
THEFT_TX = "98f3ffca9d141f2172d28f46905c08e5f32fc6ce8d23f9a37b731fe2a6c1d1bb"

CASE_WINDOWS: list[dict[str, Any]] = [
    {"id": "w1_theft_day", "from_block": 86438000, "to_block": 86444999,
     "note": "2026-09-21 ~10:24-16:14 UTC: incoming payments, theft, hops, bridge-out, NEAR payout, first hub outflows",
     "addresses": [A_VICTIM, A_PAYER, A_HOP1, A_HOP2, A_BRIDGE_OUT, A_CUT, A_DUST, A_HUB, A_DEP1, A_OUT3, A_OUT4,
                   A_PAYOUT]},
    {"id": "w2_next_day", "from_block": 86464000, "to_block": 86464999,
     "note": "2026-09-22 ~07:45-08:35 UTC: hub outflow to the second WhiteBIT deposit address",
     "addresses": [A_DEP2, A_HUB]},
    {"id": "hv_hot_wallet", "from_block": 86441900, "to_block": 86442099,
     "note": "WhiteBIT hot wallet TWBPGL, 10 min around the first exchange sweep (step 19)",
     "addresses": [A_HOT]},
    {"id": "hv_fee_collector", "from_block": 86439300, "to_block": 86439419,
     "note": "energy-rental fee collector TDii6v, 6 min around the theft (>10 000 incoming logs per 5 000 blocks)",
     "addresses": [A_FEE]},
]
# Relative windows for the cross-operator comparison (PublicNode keeps only ~11 days).
RECENT_WINDOWS: list[dict[str, Any]] = [
    {"id": "recent_1d", "offset_blocks": 30_000, "length": 5_000, "addresses": [A_HUB, A_PAYOUT],
     "note": "about 1 day before the run, 5 000 blocks"},
    {"id": "recent_1d_hv", "offset_blocks": 30_000, "length": 200, "addresses": [A_HOT, A_FEE],
     "note": "about 1 day before the run, 200 blocks, high-volume addresses"},
]
PUBLICNODE_SILENT_CHECK = [A_HOP1, A_HUB]  # case window asked from PublicNode to show its behaviour
PAGINATION_TARGETS = [
    {"id": "hot_wallet_desc", "address": A_HOT, "order_by": "block_timestamp,desc", "max_pages": 60,
     "note": "WhiteBIT hot wallet, newest first, up to 60 pages of 200"},
    {"id": "hub_asc", "address": A_HUB, "order_by": "block_timestamp,asc", "max_pages": 50,
     "note": "hub TYHeH2, full history from creation, up to 50 pages of 200"},
]
PAGINATION_MAX_TS = 1_791_936_000_000  # 2026-10-14T00:00:00Z: fixed upper bound -> stable and replayable

RAMP: dict[str, dict[str, Any]] = {
    "trongrid_keyless": {"steps": [1, 2, 3, 4, 5, 6, 8], "step_s": 10, "pause_s": 3, "sustained_s": 60},
    "trongrid_key": {"steps": [5, 10, 15, 20, 25, 30, 40], "step_s": 10, "pause_s": 3, "sustained_s": 45},
    "publicnode": {"steps": [2, 4, 6, 8, 10], "step_s": 8, "pause_s": 3, "sustained_s": 40},
    "paid_rpc": {"steps": [5, 10, 15, 20, 25], "step_s": 10, "pause_s": 3, "sustained_s": 60},
    "paid_rpc_2": {"steps": [5, 10, 15, 20], "step_s": 10, "pause_s": 3, "sustained_s": 60},
}
PENALTY_OFFSETS = [1, 2, 3, 4, 5, 6, 7, 8, 10, 12, 15, 20, 30]
EVENT_INDEX_CAP = 25  # txids per (address, window) for the event_index check
DIAG_CAP = 10  # unmatched transfers diagnosed per side per (address, window)
V1_MAX_PAGES = 40

LIVE_POINTER = "latest-live.json"
_DECLARED_RPS = re.compile(r"(?:allowed_rps|frequency limit)\((\d+)\)")
_DECLARED_PENALTY = re.compile(r"suspended for (\d+) ?s")


def _declared(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Limit and suspension declared in the body of the first 429 (TronGrid states both)."""
    for r in rows:
        if r.get("status") == 429 and r.get("body_snippet"):
            m1 = _DECLARED_RPS.search(r["body_snippet"])
            m2 = _DECLARED_PENALTY.search(r["body_snippet"])
            return {"declared_limit_rps": int(m1.group(1)) if m1 else None,
                    "declared_suspension_s": int(m2.group(1)) if m2 else None}
    return {"declared_limit_rps": None, "declared_suspension_s": None}


# ---------------------------------------------------------------- small helpers


def _utc_ms(ms: int | None) -> str | None:
    if ms is None:
        return None
    return datetime.fromtimestamp(ms / 1000, timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def _now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _parse_extra(extra: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(prog="stage2 tron_sources", add_help=False)
    p.add_argument("--phases", default="F,D,A,C,P,L")
    p.add_argument("--skip-load", action="store_true")
    p.add_argument("--freshness-samples", type=int, default=8)
    p.add_argument("--paid-jsonrpc-suffix", default="/jsonrpc")
    p.add_argument("--load-sources", default="", help="comma list to restrict the load phase (smoke tests)")
    p.add_argument("--load-scale", type=float, default=1.0, help="multiply step/sustained durations (smoke tests)")
    ns, _unknown = p.parse_known_args(extra or [])
    return ns


def _case_txids() -> list[str]:
    fx = json.loads((repo_root() / FIXTURE).read_text(encoding="utf-8"))
    out: list[str] = []
    for t in fx.get("transactions", []):
        if t.get("chain") == "tron" and re.fullmatch(r"[0-9a-f]{64}", t.get("txid", "")):
            out.append(t["txid"])
    for link in fx.get("links", []):
        for funded in link.get("funded", []) or []:
            out.extend(funded.get("txids", []) + funded.get("returns_trx_to_funder", []))
        for flow in link.get("flows", []) or []:
            out.extend(flow.get("txids", []))
        for t in (link.get("funder_upstream") or {}).get("txids", []):
            m = re.match(r"([0-9a-f]{64})", t)
            if m:
                out.append(m.group(1))
    seen: set[str] = set()
    return [t for t in out if not (t in seen or seen.add(t))]


def _json_diff(a: Any, b: Any, path: str = "$", out: list[str] | None = None, limit: int = 30) -> list[str]:
    out = [] if out is None else out
    if len(out) >= limit:
        return out
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a or k not in b:
                out.append(f"{path}.{k} (only in {'A' if k in a else 'B'})")
            else:
                _json_diff(a[k], b[k], f"{path}.{k}", out, limit)
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            out.append(f"{path} (length {len(a)} vs {len(b)})")
        else:
            for i, (x, y) in enumerate(zip(a, b)):
                _json_diff(x, y, f"{path}[{i}]", out, limit)
    elif a != b:
        out.append(path)
    return out


def _sample(items: list[Any], cap: int) -> list[Any]:
    """Deterministic evenly spaced sample (keeps first and last)."""
    if len(items) <= cap:
        return list(items)
    step = (len(items) - 1) / (cap - 1)
    return [items[round(i * step)] for i in range(cap)]


# ---------------------------------------------------------------- run


class Bench:
    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        self.opts = _parse_extra(getattr(args, "extra", []) or [])
        self.mode = (getattr(args, "http_mode", None) or "record").lower()
        self.replay = self.mode == "replay"
        phases = {p.strip().upper() for p in self.opts.phases.split(",") if p.strip()}
        if self.opts.skip_load:
            phases.discard("L")
        self.phases = phases
        self.ctx = start_run(RESULTS_AREA, config=self._config(),
                             reproduce="python -m ledgerhunt stage2 tron_sources" + (" --replay" if self.replay else ""))
        self.http = self.ctx.http_client()
        self.summary: dict[str, Any] = {"run_id": self.ctx.run_id, "http_mode": self.mode,
                                        "keys_present": secrets_presence(), "phases_run": sorted(self.phases)}
        self.not_measured: list[dict[str, str]] = []
        self.errors: list[str] = []
        # data-phase sources (shared default limiter buckets)
        self.tg_key = trongrid_source(self.http, keyed=True)
        self.tg_keyless = trongrid_source(self.http, keyed=False)
        self.tg = self.tg_key or self.tg_keyless  # data phases use the key when present
        self.pn = publicnode_source(self.http)
        self.paid = [s for s in (paid_source(self.http, "TRON_RPC_URL", jsonrpc_suffix=self.opts.paid_jsonrpc_suffix,
                                             rps=10.0),
                                 paid_source(self.http, "TRON_RPC_URL_2", jsonrpc_suffix=self.opts.paid_jsonrpc_suffix,
                                             rps=10.0)) if s]
        self.case_txids = _case_txids()
        self.resolved: dict[str, Any] = {}
        self.live_src: Path | None = None

    def _config(self) -> dict[str, Any]:
        return {
            "phases": self.opts.phases if hasattr(self, "opts") else None,
            "case_windows": CASE_WINDOWS,
            "recent_windows": RECENT_WINDOWS,
            "pagination_targets": PAGINATION_TARGETS,
            "pagination_max_timestamp_ms": PAGINATION_MAX_TS,
            "ramp": RAMP,
            "penalty_offsets_s": PENALTY_OFFSETS,
            "event_index_cap": EVENT_INDEX_CAP,
            "v1_max_pages": V1_MAX_PAGES,
            "getlogs_max_range": GETLOGS_MAX_RANGE,
            "default_limiter_rps": {"api.trongrid.io (keyless)": 1.0, "api.trongrid.io#key": 10.0,
                                    "tron-rpc.publicnode.com": 2.0, "paid-tron": 10.0},
            "notes": "Load phases use a separate RecordingClient in live mode (max_attempts=1) and dedicated "
                     "limiter buckets with rate 0: the dispatcher sets the pace. Data phases use the shared "
                     "default buckets.",
        }

    # ------------------------------------------------------------ orchestration
    def run(self) -> int:
        code = 0
        if self.replay:
            self.live_src = self._find_live_run()
            self.summary["live_source_run"] = rel_to_root(self.live_src) if self.live_src else None
            self.resolved = self._load_live_json("resolved.json") or {}
        steps: list[tuple[str, Callable[[], None]]] = [
            ("F", self.phase_freshness), ("D", self.phase_depth), ("A", self.phase_agreement),
            ("C", self.phase_completeness), ("P", self.phase_pagination), ("L", self.phase_load),
        ]
        for name, fn in steps:
            if name not in self.phases:
                continue
            t0 = time.perf_counter()
            print(f"[{AREA}] phase {name} ...", flush=True)
            try:
                fn()
            except ReplayMiss as exc:
                self.errors.append(f"phase {name}: ReplayMiss: {str(exc)[:300]}")
                print(f"[{AREA}] ОШИБКА replay в фазе {name}", flush=True)
                code = 3
            except Exception as exc:  # noqa: BLE001 - record and continue with the other phases
                import traceback
                msg = f"phase {name}: {type(exc).__name__}: {exc}"
                self.errors.append(msg)
                self.ctx.write_text(f"errors/phase-{name}.txt", traceback.format_exc())
                print(f"[{AREA}] ОШИБКА {msg}", flush=True)
                code = 1
            print(f"[{AREA}] phase {name} done in {time.perf_counter() - t0:.1f} s", flush=True)
        if not self.replay:
            self.ctx.write_json("resolved.json", self.resolved)
        self.summary["not_measured"] = self.not_measured
        self.summary["errors"] = self.errors
        self.summary["projection_inputs"] = self._projection_inputs()
        md = self._markdown()
        self.ctx.finish(self.summary, md, status="ok" if code == 0 else ("replay_miss" if code == 3 else "partial"))
        if not self.replay and code == 0 and "L" in self.phases:
            (results_root() / RESULTS_AREA / LIVE_POINTER).write_text(
                json.dumps({"run_id": self.ctx.run_id, "path": self.ctx.rel_dir, "finished_utc": _now_utc()},
                           indent=2) + "\n", encoding="utf-8", newline="\n")
        print(f"[{AREA}] results: {self.ctx.rel_dir}", flush=True)
        return code

    # ------------------------------------------------------------ live-run reuse (replay)
    def _find_live_run(self) -> Path | None:
        ptr = results_root() / RESULTS_AREA / LIVE_POINTER
        if ptr.is_file():
            p = repo_root() / json.loads(ptr.read_text(encoding="utf-8"))["path"]
            if p.is_dir():
                return p
        return None

    def _load_live_json(self, name: str) -> Any:
        if not self.live_src or not (self.live_src / name).is_file():
            return None
        return json.loads((self.live_src / name).read_text(encoding="utf-8"))

    def _load_live_jsonl(self, name: str) -> list[dict[str, Any]] | None:
        if not self.live_src or not (self.live_src / name).is_file():
            return None
        return [json.loads(line) for line in (self.live_src / name).read_text(encoding="utf-8").splitlines() if line]

    def _copy_live(self, name: str) -> None:
        if self.live_src and (self.live_src / name).is_file():
            shutil.copyfile(self.live_src / name, self.ctx.path(name))

    # ------------------------------------------------------------ sources
    def _node_sources(self) -> list[BenchSource]:
        out = [self.tg, self.pn] + self.paid
        return [s for s in out if s is not None]

    def _paid_not_measured(self, what: str) -> None:
        for env in ("TRON_RPC_URL", "TRON_RPC_URL_2"):
            if not has_secret(env):
                self.not_measured.append({"what": f"{what}: платный TRON RPC ({env})",
                                          "why": f"не измерено: нет ключа ({env} не задан)",
                                          "needed": f"URL узла провайдера в .env как {env}; код подхватит его сам"})

    # ============================================================ F: freshness
    def phase_freshness(self) -> None:
        if self.replay:
            rows = self._load_live_jsonl("raw/freshness.jsonl")
            if rows is None:
                self.summary["freshness"] = {"status": "нет данных живого прогона"}
                return
            self._copy_live("raw/freshness.jsonl")
        else:
            rows = []
            k = max(1, self.opts.freshness_samples)
            for i in range(k):
                t_start = time.time()
                sample: dict[str, Any] = {"sample": i, "local_utc": _now_utc(), "local_ts_ms": int(t_start * 1000)}
                for src in self._node_sources():
                    try:
                        h = block_header(src.node, None, solidity=False)
                        s = block_header(src.node, None, solidity=True)
                        sample[src.name] = {"head": h, "solid": s, "local_done_ts_ms": int(time.time() * 1000)}
                    except (SourceError, RequestFailed) as exc:
                        sample[src.name] = {"error": str(exc)[:300]}
                if self.tg is not None and self.tg.v1 is not None:
                    for label, oc in (("v1_latest_event", None), ("v1_latest_confirmed_event", True)):
                        try:
                            f = self.tg.v1.contract_events_page(USDT_TRC20, event_name="Transfer",
                                                                order_by="block_timestamp,desc", limit=1,
                                                                only_confirmed=oc)
                            ev = ((f.data or {}).get("data") or [{}])[0]
                            sample[label] = {"block": ev.get("block_number"), "ts_ms": ev.get("block_timestamp"),
                                             "meta_at": ((f.data or {}).get("meta") or {}).get("at"),
                                             "ref": f.ref_dict(), "latency_ms": f.latency_ms}
                        except (SourceError, RequestFailed) as exc:
                            sample[label] = {"error": str(exc)[:300]}
                rows.append(sample)
                left = 4.0 - (time.time() - t_start)
                if i < k - 1 and left > 0:
                    time.sleep(left)
            self.ctx.write_jsonl("raw/freshness.jsonl", rows)
            heads = [r[self.tg.name]["solid"] for r in rows if self.tg and isinstance(r.get(self.tg.name), dict)
                     and r[self.tg.name].get("solid")]
            if heads:
                self.resolved["solid_head_at_run"] = heads[-1]
        self.summary["freshness"] = self._freshness_stats(rows)
        if not self.paid:
            self._paid_not_measured("свежесть (отставание solidified)")

    def _freshness_stats(self, rows: list[dict[str, Any]]) -> dict[str, Any]:
        out: dict[str, Any] = {"samples": len(rows), "sources": {}}
        names = sorted({k for r in rows for k, v in r.items() if isinstance(v, dict) and "head" in v})
        for name in names:
            lag_b, lag_s, age_s = [], [], []
            for r in rows:
                v = r.get(name) or {}
                h, s = v.get("head"), v.get("solid")
                if h and s:
                    lag_b.append(h["num"] - s["num"])
                    lag_s.append((h["ts_ms"] - s["ts_ms"]) / 1000)
                if h and v.get("local_done_ts_ms"):
                    age_s.append((v["local_done_ts_ms"] - h["ts_ms"]) / 1000)
            out["sources"][name] = {
                "solid_lag_blocks": {"min": min(lag_b, default=None), "median": percentile(lag_b, 50),
                                     "max": max(lag_b, default=None)},
                "solid_lag_s": {"min": min(lag_s, default=None), "median": percentile(lag_s, 50),
                                "max": max(lag_s, default=None)},
                "head_age_vs_local_clock_s": {"median": percentile(age_s, 50), "max": max(age_s, default=None)},
                "n": len(lag_b),
            }
        # cross-source head difference (same sample)
        if len(names) > 1:
            base = "trongrid_key" if "trongrid_key" in names else names[0]
            for other in names:
                if other == base:
                    continue
                d = [r[base]["head"]["num"] - r[other]["head"]["num"] for r in rows
                     if (r.get(base) or {}).get("head") and (r.get(other) or {}).get("head")]
                out["sources"][other]["head_behind_" + base + "_blocks"] = {
                    "min": min(d, default=None), "median": percentile(d, 50), "max": max(d, default=None)}
        tg_name = "trongrid_key" if "trongrid_key" in names else ("trongrid_keyless" if "trongrid_keyless" in names else None)
        if tg_name:
            idx_lag, idx_lag_c = [], []
            for r in rows:
                v = r.get(tg_name) or {}
                ev, evc = r.get("v1_latest_event") or {}, r.get("v1_latest_confirmed_event") or {}
                if v.get("head") and ev.get("block"):
                    idx_lag.append(v["head"]["num"] - int(ev["block"]))
                if v.get("solid") and evc.get("block"):
                    idx_lag_c.append(v["solid"]["num"] - int(evc["block"]))
            out["trongrid_v1_index"] = {
                "latest_event_behind_head_blocks": {"min": min(idx_lag, default=None),
                                                    "median": percentile(idx_lag, 50),
                                                    "max": max(idx_lag, default=None)},
                "latest_confirmed_event_behind_solid_blocks": {"min": min(idx_lag_c, default=None),
                                                               "median": percentile(idx_lag_c, 50),
                                                               "max": max(idx_lag_c, default=None)},
                "note": "positive = the v1 index is behind the node; the latest USDT Transfer event is a proxy "
                        "(USDT has transfers in almost every block)",
            }
        return out

    # ============================================================ D: depth
    def phase_depth(self) -> None:
        if self.replay:
            rows = self._load_live_jsonl("raw/depth.jsonl")
            res = self._load_live_json("raw/depth-summary.json")
            if rows is None or res is None:
                self.summary["publicnode_depth"] = {"status": "нет данных живого прогона"}
                return
            self._copy_live("raw/depth.jsonl")
            self._copy_live("raw/depth-summary.json")
            self.summary["publicnode_depth"] = res
            return
        rows: list[dict[str, Any]] = []

        def probe(src: BenchSource, num: int, purpose: str) -> bool:
            try:
                h = block_header(src.node, num)
                ok = h is not None
                rows.append({"source": src.name, "block": num, "served": ok, "purpose": purpose,
                             "ts_ms": h["ts_ms"] if h else None, "ref": (h or {}).get("ref"), "utc": _now_utc()})
                return ok
            except (SourceError, RequestFailed) as exc:
                rows.append({"source": src.name, "block": num, "served": None, "purpose": purpose,
                             "error": str(exc)[:200], "utc": _now_utc()})
                return False

        pn = self.pn
        head = block_header(pn.node, None)
        assert head is not None, "PublicNode returned no head block"
        rows.append({"source": pn.name, "block": head["num"], "served": True, "purpose": "head", "ts_ms": head["ts_ms"],
                     "utc": _now_utc()})
        served_newest, missing_oldest = head["num"], None
        for days in (1, 3, 7, 9, 10, 11, 12, 14, 21):
            n = head["num"] - days * BLOCKS_PER_DAY
            if probe(pn, n, f"coarse -{days}d"):
                served_newest = n
            else:
                missing_oldest = n
                break
        boundary = None
        if missing_oldest is not None:
            lo, hi = missing_oldest, served_newest  # lo missing, hi served
            while hi - lo > 1:
                mid = (lo + hi) // 2
                if probe(pn, mid, "bisect"):
                    hi = mid
                else:
                    lo = mid
            boundary = hi
            consistency = []
            for n in (boundary, boundary - 1, boundary, boundary - 1, boundary, boundary - 1):
                consistency.append(probe(pn, n, "consistency"))
                time.sleep(0.3)
            later = probe(pn, boundary + 1000, "boundary+1000")
            earlier = probe(pn, boundary - 1000, "boundary-1000")
        oldest_hdr = block_header(self.tg.node, boundary) if boundary and self.tg else None
        res: dict[str, Any] = {
            "head_block": head["num"], "head_utc": _utc_ms(head["ts_ms"]),
            "oldest_served_block": boundary,
            "oldest_served_utc": _utc_ms(oldest_hdr["ts_ms"]) if oldest_hdr else None,
            "depth_blocks": head["num"] - boundary if boundary else None,
            "depth_days": round((head["ts_ms"] - oldest_hdr["ts_ms"]) / 86_400_000, 2) if oldest_hdr else None,
            "probes": len(rows),
        }
        if boundary:
            res["consistency_boundary_served_repeats"] = consistency[0::2]
            res["consistency_boundary_minus_1_served_repeats"] = consistency[1::2]
            res["boundary_plus_1000_served"] = later
            res["boundary_minus_1000_served"] = earlier
            res.update(self._depth_tx_level(boundary, head['num'], rows))
        # archival check of the other operators: theft block and an old block
        for src in [self.tg] + self.paid:
            if src is None:
                continue
            res.setdefault("archival", {})[src.name] = {
                "theft_block_86439360_served": probe(src, THEFT_BLOCK, "archival case-001"),
                "block_1000000_served": probe(src, 1_000_000, "archival 2018"),
            }
        if not self.paid:
            self._paid_not_measured("глубина истории (архивность)")
        res["probes"] = len(rows)
        self.ctx.write_jsonl("raw/depth.jsonl", rows)
        self.ctx.write_json("raw/depth-summary.json", res)
        self.resolved["publicnode_oldest_block"] = boundary
        self.summary["publicnode_depth"] = res

    def _depth_tx_level(self, boundary: int, head_num: int, rows: list[dict[str, Any]]) -> dict[str, Any]:
        """Receipt depth of PublicNode (bisection) and eth_getLogs inside / below that depth.

        A receipt probe takes the middle transaction of block n (tx hashes from TronGrid JSON-RPC
        eth_getBlockByNumber) and asks PublicNode walletsolidity/gettransactioninfobyid.
        """
        out: dict[str, Any] = {}
        tg, pn = self.tg, self.pn

        def receipt_served(num: int, purpose: str, with_tg: bool = False) -> bool | None:
            for n in (num, num + 1, num + 2):
                f = tg.jsonrpc.get_block_by_number(n, False)
                txs = (f.data or {}).get("transactions") or []
                if txs:
                    break
            else:
                return None
            txid = txs[len(txs) // 2][2:]
            info = pn.node.get_transaction_info_by_id(txid)
            row = {"source": pn.name, "block": n, "purpose": f"receipt {purpose}", "txid": txid,
                   "served": not is_empty(info), "ref": info.ref_dict(), "utc": _now_utc()}
            if with_tg:
                t = tg.node.get_transaction_info_by_id(txid)
                row["trongrid_served"] = not is_empty(t)
                row["tx_served_by_publicnode"] = not is_empty(pn.node.get_transaction_by_id(txid))
            rows.append(row)
            return row["served"]

        served, missing = head_num - 1200, None
        for days in (1, 3, 5, 7, 8, 9, 10):
            n = head_num - days * BLOCKS_PER_DAY
            if n <= boundary:
                missing = boundary
                break
            ok = receipt_served(n, f"coarse -{days}d")
            if ok:
                served = n
            else:
                missing = n
                break
        if missing is None:
            missing = boundary
        lo, hi = missing, served
        while hi - lo > 50:
            mid = (lo + hi) // 2
            if receipt_served(mid, "bisect"):
                hi = mid
            else:
                lo = mid
        rb = hi
        hdr = block_header(tg.node, rb)
        out["receipt_oldest_served_block_approx"] = rb
        out["receipt_oldest_served_utc"] = _utc_ms(hdr["ts_ms"]) if hdr else None
        out["receipt_bisect_precision_blocks"] = 50
        out["receipt_check_inside"] = receipt_served(rb + 200, "check inside +200", with_tg=True)
        out["receipt_check_outside"] = receipt_served(max(lo - 200, 1), "check outside -200", with_tg=True)
        logs: dict[str, Any] = {}
        for label, (a, b) in (("inside_receipt_history", (rb + 100, rb + 1099)),
                              ("below_receipt_history", (lo - 1100, lo - 101))):
            logs[label] = {"range": [a, b]}
            for src in (tg, pn):
                try:
                    f = src.jsonrpc.usdt_transfer_logs(from_block=a, to_block=b, sender=A_PAYOUT)
                    logs[label][src.name] = {"logs": len(f.data or []), "status": f.status, "ref": f.ref_dict()}
                except (SourceError, RequestFailed) as exc:
                    logs[label][src.name] = {"error": str(exc)[:300]}
        out["getlogs_vs_history"] = dict(logs, address=A_PAYOUT, direction="from",
                                         note="PublicNode answers 200 with [] where it has no data: a silent gap")
        return out

    # ============================================================ A: agreement
    def phase_agreement(self) -> None:
        tg = self.tg
        recent_block = self.resolved.get("agreement_block")
        if recent_block is None:
            if self.replay:
                raise RuntimeError("replay: agreement block unknown (no resolved.json from a live run)")
            solid = (self.resolved.get("solid_head_at_run") or {}).get("num") or block_header(tg.node, None, solidity=True)["num"]
            recent_block = solid - BLOCKS_PER_DAY
            self.resolved["agreement_block"] = recent_block
        f = tg.v1.contract_events_page(USDT_TRC20, event_name="Transfer", block_number=recent_block, limit=200)
        txids: list[str] = []
        for ev in (f.data or {}).get("data") or []:
            t = ev.get("transaction_id")
            if t and t not in txids:
                txids.append(t)
        recent = txids[:30]
        self.resolved["agreement_recent_txids"] = recent
        rows: list[dict[str, Any]] = []
        others = [s for s in [self.pn] + self.paid if s is not None]
        case_sample = self.case_txids if self.paid else self.case_txids[:5]
        for group, sample in (("recent", recent), ("case-001", case_sample)):
            for txid in sample:
                try:
                    rows.append(self._agree_one(txid, others, group))
                except (SourceError, RequestFailed) as exc:
                    self.errors.append(f"agreement {txid}: {str(exc)[:200]}")
        self.ctx.write_jsonl("raw/agreement.jsonl", rows)
        self.summary["agreement"] = self._agreement_stats(rows, recent_block)
        if not self.paid:
            self._paid_not_measured("совпадение транзакций с TronGrid")

    def _agree_one(self, txid: str, others: list[BenchSource], group: str) -> dict[str, Any]:
        tg = self.tg
        row: dict[str, Any] = {"txid": txid, "group": group, "by_source": {}}
        tg_tx = tg.node.get_transaction_by_id(txid)
        tg_info = tg.node.get_transaction_info_by_id(txid)
        ev = tg.v1.transaction_events(txid)
        tg_transfers = transfers_from_receipt(tg_info.data or {})
        v1_transfers = transfers_from_v1_events((ev.data or {}).get("data") or [])
        row["trongrid"] = {"tx_ref": tg_tx.ref_dict(), "info_ref": tg_info.ref_dict(), "events_ref": ev.ref_dict(),
                           "tx_empty": is_empty(tg_tx), "info_empty": is_empty(tg_info),
                           "block": (tg_info.data or {}).get("blockNumber"),
                           "receipt_result": ((tg_info.data or {}).get("receipt") or {}).get("result"),
                           "usdt_transfer_logs": len(tg_transfers)}
        row["v1_events_vs_receipt"] = self._event_index_compare(v1_transfers, tg_transfers)
        for src in others:
            try:
                o_tx = src.node.get_transaction_by_id(txid)
                o_info = src.node.get_transaction_info_by_id(txid)
            except (SourceError, RequestFailed) as exc:
                row["by_source"][src.name] = {"error": str(exc)[:300]}
                continue
            d: dict[str, Any] = {"tx_ref": o_tx.ref_dict(), "info_ref": o_info.ref_dict(),
                                 "tx_empty": is_empty(o_tx), "info_empty": is_empty(o_info)}
            if not is_empty(o_tx) and not is_empty(tg_tx):
                d["tx_equal"] = o_tx.data == tg_tx.data
                d["tx_bytes_equal"] = (o_tx.ref.body_sha256 == tg_tx.ref.body_sha256) if (o_tx.ref and tg_tx.ref) else None
                d["tx_diff"] = _json_diff(tg_tx.data, o_tx.data)
            if not is_empty(o_info) and not is_empty(tg_info):
                d["info_equal"] = o_info.data == tg_info.data
                d["info_bytes_equal"] = (o_info.ref.body_sha256 == tg_info.ref.body_sha256) if (o_info.ref and tg_info.ref) else None
                d["info_diff"] = _json_diff(tg_info.data, o_info.data)
            row["by_source"][src.name] = d
        return row

    @staticmethod
    def _event_index_compare(v1: list[dict[str, Any]], receipt: list[dict[str, Any]]) -> dict[str, Any]:
        """Match v1 Transfer events to receipt Transfer logs by (from, to, value) in order; compare indices."""
        pool = list(receipt)
        equal = differ = missing_receipt = 0
        pairs = []
        for e in v1:
            hit = next((r for r in pool if (r["from"], r["to"], r["value"]) == (e["from"], e["to"], e["value"])), None)
            if hit is None:
                missing_receipt += 1
                pairs.append({"event_index": e["event_index"], "ordinal": None})
                continue
            pool.remove(hit)
            same = e["event_index"] == hit["ordinal"]
            equal += same
            differ += not same
            pairs.append({"event_index": e["event_index"], "ordinal": hit["ordinal"]})
        return {"v1_transfers": len(v1), "receipt_transfers": len(receipt), "equal": equal, "differ": differ,
                "missing_in_receipt": missing_receipt, "missing_in_v1": len(pool), "pairs": pairs[:20]}

    @staticmethod
    def _agreement_stats(rows: list[dict[str, Any]], recent_block: int) -> dict[str, Any]:
        out: dict[str, Any] = {"recent_block": recent_block, "groups": {}}
        for group in sorted({r["group"] for r in rows}):
            gr = [r for r in rows if r["group"] == group]
            g: dict[str, Any] = {"txids": len(gr), "sources": {}}
            ev = [r["v1_events_vs_receipt"] for r in gr]
            g["trongrid_v1_events_vs_receipt"] = {
                "txids": len(ev), "transfer_events": sum(e["v1_transfers"] for e in ev),
                "event_index_equal_receipt_ordinal": sum(e["equal"] for e in ev),
                "event_index_differs": sum(e["differ"] for e in ev),
                "missing_in_receipt": sum(e["missing_in_receipt"] for e in ev),
                "missing_in_v1": sum(e["missing_in_v1"] for e in ev)}
            g["trongrid_empty_receipts"] = sum(1 for r in gr if r["trongrid"]["info_empty"])
            for name in sorted({k for r in gr for k in r["by_source"]}):
                ds = [r["by_source"][name] for r in gr if name in r["by_source"]]
                g["sources"][name] = {
                    "answered": sum(1 for d in ds if "error" not in d),
                    "empty_tx": sum(1 for d in ds if d.get("tx_empty")),
                    "empty_receipt": sum(1 for d in ds if d.get("info_empty")),
                    "tx_compared": sum(1 for d in ds if "tx_equal" in d),
                    "tx_equal": sum(1 for d in ds if d.get("tx_equal")),
                    "tx_bytes_equal": sum(1 for d in ds if d.get("tx_bytes_equal")),
                    "receipt_compared": sum(1 for d in ds if "info_equal" in d),
                    "receipt_equal": sum(1 for d in ds if d.get("info_equal")),
                    "receipt_bytes_equal": sum(1 for d in ds if d.get("info_bytes_equal")),
                    "diff_paths": sorted(Counter(p for d in ds for p in (d.get("info_diff") or []) +
                                                 (d.get("tx_diff") or [])).items())[:20],
                }
            out["groups"][group] = g
        return out

    # ============================================================ C: completeness
    def phase_completeness(self) -> None:
        windows = [dict(w, kind="case") for w in CASE_WINDOWS]
        rw = self.resolved.get("recent_windows")
        if rw is None:
            if self.replay:
                raise RuntimeError("replay: recent windows unknown (no resolved.json from a live run)")
            solid = (self.resolved.get("solid_head_at_run") or {}).get("num") or block_header(self.tg.node, None, solidity=True)["num"]
            rw = []
            for w in RECENT_WINDOWS:
                lo = solid - w["offset_blocks"]
                rw.append({"id": w["id"], "from_block": lo, "to_block": lo + w["length"] - 1,
                           "addresses": w["addresses"], "note": w["note"]})
            self.resolved["recent_windows"] = rw
        windows += [dict(w, kind="recent") for w in rw]
        headers: dict[int, dict[str, Any]] = {}

        def hdr(n: int) -> dict[str, Any]:
            if n not in headers:
                h = block_header(self.tg.node, n)
                if h is None:
                    raise RuntimeError(f"TronGrid has no header for block {n}")
                headers[n] = h
            return headers[n]

        results: list[dict[str, Any]] = []
        ev_rows: list[dict[str, Any]] = []
        for w in windows:
            h0, h1 = hdr(w["from_block"]), hdr(w["to_block"])
            for addr in w["addresses"]:
                node_srcs = [self.tg]
                if w["kind"] == "recent":
                    node_srcs.append(self.pn)
                elif addr in PUBLICNODE_SILENT_CHECK and w["id"] == "w1_theft_day":
                    node_srcs.append(self.pn)
                node_srcs += self.paid
                try:
                    res = self._complete_one(addr, w, h0, h1, node_srcs, ev_rows)
                except (SourceError, RequestFailed) as exc:
                    self.errors.append(f"completeness {w['id']} {addr}: {str(exc)[:200]}")
                    continue
                results.append(res)
                print(f"[{AREA}]   {w['id']} {addr[:8]}: v1 {res['v1_transfers']} ({res['v1_pages']} pages) / node "
                      f"{res['node_transfers']} matched {res['matched']}", flush=True)
        # repeat the v1 events request for the first 10 checked txids: is event_index stable?
        repeat = []
        for r in [e for e in ev_rows if e["source"] == self.tg.name][:10]:
            f = self.tg.v1.transaction_events(r["txid"])
            again = transfers_from_v1_events((f.data or {}).get("data") or [])
            repeat.append({"txid": r["txid"], "first": r["v1_event_indices"],
                           "second": [e["event_index"] for e in again],
                           "same": r["v1_event_indices"] == [e["event_index"] for e in again]})
        self.ctx.write_jsonl("raw/completeness.jsonl", results)
        self.ctx.write_jsonl("raw/event-index.jsonl", ev_rows)
        self.ctx.write_jsonl("raw/event-index-repeat.jsonl", repeat)
        self.summary["completeness"] = self._completeness_stats(results)
        self.summary["event_index"] = self._event_index_stats(ev_rows, repeat)
        if not self.paid:
            self._paid_not_measured("полнота истории TRC20 (логи независимого архивного узла по окну case-001)")

    def _node_logs(self, src: BenchSource, addr: str, lo: int, hi: int) -> dict[str, Any]:
        """All USDT Transfer logs with ``addr`` as sender or receiver in [lo, hi] (chunked, split on the 10k cap)."""
        logs: dict[tuple[str, int], dict[str, Any]] = {}
        requests = splits = 0
        refs: list[Any] = []
        errors: list[str] = []

        def fetch(a: int, b: int, direction: str) -> None:
            nonlocal requests, splits
            requests += 1
            try:
                kw = {"sender": addr} if direction == "from" else {"receiver": addr}
                f = src.jsonrpc.usdt_transfer_logs(from_block=a, to_block=b, **kw)
            except JsonRpcError as exc:
                if is_result_limit_error(exc) and b - a >= 10:
                    splits += 1
                    mid = (a + b) // 2
                    fetch(a, mid, direction)
                    fetch(mid + 1, b, direction)
                    return
                errors.append(f"{direction} [{a},{b}]: {str(exc)[:200]}")
                return
            except (SourceError, RequestFailed) as exc:
                errors.append(f"{direction} [{a},{b}]: {str(exc)[:200]}")
                return
            refs.append(f.ref_dict())
            for lg in f.data or []:
                t = transfer_from_jsonrpc_log(lg)
                if t:
                    logs[(t["txid"], t["log_index_block"])] = t

        for direction in ("from", "to"):
            a = lo
            while a <= hi:
                b = min(hi, a + GETLOGS_MAX_RANGE - 1)
                fetch(a, b, direction)
                a = b + 1
        return {"transfers": sorted(logs.values(), key=lambda t: (t["block"], t["log_index_block"])),
                "requests": requests, "splits_on_10k_cap": splits, "errors": errors, "refs": refs}

    def _complete_one(self, addr: str, w: dict[str, Any], h0: dict[str, Any], h1: dict[str, Any],
                      node_srcs: list[BenchSource], ev_rows: list[dict[str, Any]]) -> dict[str, Any]:
        lo, hi = w["from_block"], w["to_block"]
        paged = self.tg.v1.trc20_transfers(addr, min_timestamp=h0["ts_ms"], max_timestamp=h1["ts_ms"],
                                           order_by="block_timestamp,asc", limit=200, max_pages=V1_MAX_PAGES)
        v1_all = [transfer_from_v1_row(r) for r in paged.rows]
        v1 = [r for r in v1_all if r["type"] == "Transfer" and r["token"] == USDT_TRC20]
        v1_keys = Counter((r["txid"], r["from"], r["to"], r["value"]) for r in v1)
        res: dict[str, Any] = {
            "window": w["id"], "kind": w["kind"], "address": addr, "from_block": lo, "to_block": hi,
            "from_utc": _utc_ms(h0["ts_ms"]), "to_utc": _utc_ms(h1["ts_ms"]),
            "v1_rows": len(v1_all), "v1_transfers": len(v1), "v1_non_transfer_rows": len(v1_all) - len(v1),
            "v1_zero_value": sum(1 for r in v1 if r["value"] == 0), "v1_pages": len(paged.pages),
            "v1_complete": paged.complete, "v1_page_refs": [p.ref_dict() for p in paged.pages],
            "v1_out": sum(1 for r in v1 if r["from"] == addr), "v1_in": sum(1 for r in v1 if r["to"] == addr),
            "v1_distinct_counterparties_out": len({r["to"] for r in v1 if r["from"] == addr}),
            "node_transfers": {}, "node_requests": {}, "node_splits": {}, "node_errors": {}, "matched": {},
            "only_v1": {}, "only_node": {}, "only_v1_count": {}, "only_node_count": {}, "node_refs": {},
            "diagnosis": {},
        }
        for src in node_srcs:
            nl = self._node_logs(src, addr, lo, hi)
            keys = Counter((t["txid"], t["from"], t["to"], t["value"]) for t in nl["transfers"])
            matched = sum((v1_keys & keys).values())
            only_v1 = list((v1_keys - keys).elements())
            only_node = list((keys - v1_keys).elements())
            res["node_transfers"][src.name] = len(nl["transfers"])
            res["node_requests"][src.name] = nl["requests"]
            res["node_splits"][src.name] = nl["splits_on_10k_cap"]
            res["node_errors"][src.name] = nl["errors"]
            res["node_refs"][src.name] = nl["refs"][:12]
            res["matched"][src.name] = matched
            res["only_v1"][src.name] = [list(k) for k in only_v1[:50]]
            res["only_node"][src.name] = [list(k) for k in only_node[:50]]
            res["only_v1_count"][src.name] = len(only_v1)
            res["only_node_count"][src.name] = len(only_node)
            if src is self.tg:
                res["diagnosis"] = self._diagnose(only_v1, only_node, lo, hi)
                matched_t = [t for t in nl["transfers"] if (t["txid"], t["from"], t["to"], t["value"]) in v1_keys]
                txids = list(dict.fromkeys(t["txid"] for t in matched_t))
                res["event_index_txids"] = len(_sample(txids, EVENT_INDEX_CAP))
                self._event_index_batch(_sample(txids, EVENT_INDEX_CAP), addr, w, ev_rows,
                                        [self.tg] + ([self.pn] if w["kind"] == "recent" else []) + self.paid)
        return res

    def _diagnose(self, only_v1: list[tuple], only_node: list[tuple], lo: int, hi: int) -> dict[str, Any]:
        out: dict[str, Any] = {"only_v1": [], "only_node": []}
        for txid, frm, to, value in only_v1[:DIAG_CAP]:
            info = self.tg.node.get_transaction_info_by_id(txid)
            d = info.data or {}
            tr = transfers_from_receipt(d)
            out["only_v1"].append({"txid": txid, "block": d.get("blockNumber"),
                                   "in_window": lo <= int(d.get("blockNumber") or -1) <= hi,
                                   "receipt_result": (d.get("receipt") or {}).get("result"),
                                   "receipt_has_same_transfer": any((t["from"], t["to"], t["value"]) == (frm, to, value) for t in tr),
                                   "ref": info.ref_dict()})
        for txid, frm, to, value in only_node[:DIAG_CAP]:
            ev = self.tg.v1.transaction_events(txid)
            evs = transfers_from_v1_events((ev.data or {}).get("data") or [])
            out["only_node"].append({"txid": txid,
                                     "v1_events_have_transfer": any((e["from"], e["to"], e["value"]) == (frm, to, value) for e in evs),
                                     "v1_event_block": evs[0]["block"] if evs else None, "ref": ev.ref_dict()})
        return out

    def _event_index_batch(self, txids: list[str], addr: str, w: dict[str, Any], ev_rows: list[dict[str, Any]],
                           receipt_srcs: list[BenchSource]) -> None:
        def one(txid: str) -> list[dict[str, Any]]:
            try:
                ev = self.tg.v1.transaction_events(txid)
            except (SourceError, RequestFailed) as exc:
                return [{"txid": txid, "source": self.tg.name, "error": f"v1 events: {str(exc)[:200]}"}]
            v1 = transfers_from_v1_events((ev.data or {}).get("data") or [])
            rows = []
            for src in receipt_srcs:
                try:
                    info = src.node.get_transaction_info_by_id(txid)
                except (SourceError, RequestFailed) as exc:
                    rows.append({"txid": txid, "source": src.name, "error": str(exc)[:200]})
                    continue
                rec = transfers_from_receipt(info.data or {})
                cmp_ = self._event_index_compare(v1, rec)
                rows.append({"txid": txid, "window": w["id"], "address": addr, "source": src.name,
                             "receipt_empty": is_empty(info), "v1_event_indices": [e["event_index"] for e in v1],
                             "receipt_ordinals": [r["ordinal"] for r in rec], "compare": cmp_,
                             "receipt_log_count": len((info.data or {}).get("log") or []),
                             "events_ref": ev.ref_dict(), "receipt_ref": info.ref_dict()})
            return rows

        with ThreadPoolExecutor(max_workers=4) as ex:
            for rows in ex.map(one, txids):
                ev_rows.extend(rows)

    @staticmethod
    def _completeness_stats(results: list[dict[str, Any]]) -> dict[str, Any]:
        per_src: dict[str, dict[str, int]] = {}
        for r in results:
            for name, n in r["node_transfers"].items():
                s = per_src.setdefault(name, {"windows": 0, "node_transfers": 0, "v1_transfers_same_windows": 0,
                                              "matched": 0, "only_v1": 0, "only_node": 0, "requests": 0,
                                              "splits_on_10k_cap": 0, "errors": 0})
                s["windows"] += 1
                s["node_transfers"] += n
                s["v1_transfers_same_windows"] += r["v1_transfers"]
                s["matched"] += r["matched"][name]
                s["only_v1"] += r["only_v1_count"][name]
                s["only_node"] += r["only_node_count"][name]
                s["requests"] += r["node_requests"][name]
                s["splits_on_10k_cap"] += r["node_splits"][name]
                s["errors"] += len(r["node_errors"][name])
        table = [{k: r[k] for k in ("window", "kind", "address", "from_block", "to_block", "from_utc", "to_utc",
                                    "v1_transfers", "v1_non_transfer_rows", "v1_zero_value", "v1_pages",
                                    "v1_complete", "v1_out", "v1_in", "v1_distinct_counterparties_out",
                                    "node_transfers", "matched", "node_requests", "node_splits")}
                 | {"only_v1": dict(r["only_v1_count"]), "only_node": dict(r["only_node_count"])}
                 for r in results]
        by_kind: dict[str, dict[str, dict[str, int]]] = {}
        for r in results:
            for name, n in r["node_transfers"].items():
                k = by_kind.setdefault(name, {}).setdefault(r["kind"], {"windows": 0, "node_transfers": 0,
                                                                          "v1_transfers": 0, "matched": 0,
                                                                          "only_v1": 0, "only_node": 0})
                k["windows"] += 1
                k["node_transfers"] += n
                k["v1_transfers"] += r["v1_transfers"]
                k["matched"] += r["matched"][name]
                k["only_v1"] += r["only_v1_count"][name]
                k["only_node"] += r["only_node_count"][name]
        return {"by_source": per_src, "by_source_and_window_kind": by_kind, "by_address_window": table,
                "v1_pages_total": sum(r["v1_pages"] for r in results),
                "v1_transfers_total": sum(r["v1_transfers"] for r in results)}

    @staticmethod
    def _event_index_stats(ev_rows: list[dict[str, Any]], repeat: list[dict[str, Any]]) -> dict[str, Any]:
        out: dict[str, Any] = {}
        for name in sorted({r["source"] for r in ev_rows}):
            rs = [r for r in ev_rows if r["source"] == name and "compare" in r]
            out[name] = {
                "txids": len(rs),
                "receipt_empty": sum(1 for r in rs if r["receipt_empty"]),
                "transfer_events": sum(r["compare"]["v1_transfers"] for r in rs),
                "equal": sum(r["compare"]["equal"] for r in rs),
                "differ": sum(r["compare"]["differ"] for r in rs),
                "missing_in_receipt": sum(r["compare"]["missing_in_receipt"] for r in rs),
                "missing_in_v1": sum(r["compare"]["missing_in_v1"] for r in rs),
                "errors": sum(1 for r in ev_rows if r["source"] == name and "error" in r),
            }
        out["repeat_request_same_event_index"] = {"checked": len(repeat), "same": sum(1 for r in repeat if r["same"])}
        return out

    # ============================================================ P: pagination
    def phase_pagination(self) -> None:
        rows, summary = [], {}
        for t in PAGINATION_TARGETS:
            seen: set[tuple] = set()
            dup = 0
            order_violations = 0
            last_ts = None
            desc = t["order_by"].endswith("desc")
            fp = None
            t_start = time.perf_counter()
            pages = 0
            complete = False
            for page_no in range(1, t["max_pages"] + 1):
                f = self.tg.v1.trc20_transfers_page(t["address"], max_timestamp=PAGINATION_MAX_TS,
                                                    order_by=t["order_by"], limit=200, fingerprint=fp)
                data = f.data or {}
                prs = [transfer_from_v1_row(r) for r in data.get("data") or []]
                for r in prs:
                    key = (r["txid"], r["from"], r["to"], r["value"], r["type"])
                    if key in seen:
                        dup += 1
                    seen.add(key)
                    if last_ts is not None and ((desc and r["ts_ms"] > last_ts) or (not desc and r["ts_ms"] < last_ts)):
                        order_violations += 1
                    last_ts = r["ts_ms"]
                fp = (data.get("meta") or {}).get("fingerprint")
                pages += 1
                rows.append({"target": t["id"], "page": page_no, "rows": len(prs), "latency_ms": f.latency_ms,
                             "first_utc": _utc_ms(prs[0]["ts_ms"]) if prs else None,
                             "last_utc": _utc_ms(prs[-1]["ts_ms"]) if prs else None,
                             "has_fingerprint": bool(fp), "fingerprint_len": len(fp or ""),
                             "non_transfer": sum(1 for r in prs if r["type"] != "Transfer"),
                             "zero_value": sum(1 for r in prs if r["value"] == 0),
                             "from_replay": f.from_replay, "ref": f.ref_dict()})
                if not fp:
                    complete = True
                    break
            span = [r for r in rows if r["target"] == t["id"] and r["rows"]]
            first_utc, last_utc = (span[0]["first_utc"], span[-1]["last_utc"]) if span else (None, None)
            n_rows = len(seen) + dup
            hours = None
            if span:
                a = datetime.strptime(first_utc, "%Y-%m-%d %H:%M:%S")
                b = datetime.strptime(last_utc, "%Y-%m-%d %H:%M:%S")
                hours = abs((a - b).total_seconds()) / 3600
            lat = [r["latency_ms"] for r in rows if r["target"] == t["id"]]
            summary[t["id"]] = {
                "address": t["address"], "order_by": t["order_by"], "max_pages": t["max_pages"], "pages": pages,
                "complete": complete, "rows": n_rows, "duplicates": dup, "order_violations": order_violations,
                "span_first_utc": first_utc, "span_last_utc": last_utc,
                "span_hours": round(hours, 2) if hours is not None else None,
                "rows_per_hour": round(n_rows / hours, 1) if hours else None,
                "latency_ms_p50": percentile(lat, 50), "latency_ms_p95": percentile(lat, 95),
                "wall_s": round(time.perf_counter() - t_start, 2),
                "non_transfer_rows": sum(r["non_transfer"] for r in rows if r["target"] == t["id"]),
                "zero_value_rows": sum(r["zero_value"] for r in rows if r["target"] == t["id"]),
            }
        self.ctx.write_jsonl("raw/pagination.jsonl", rows)
        self.summary["pagination"] = summary

    # ============================================================ L: load
    def phase_load(self) -> None:
        if self.replay:
            out = {}
            for name in RAMP:
                rows = self._load_live_jsonl(f"raw/load-{name}.jsonl")
                if rows is None:
                    continue
                self._copy_live(f"raw/load-{name}.jsonl")
                out[name] = self._load_stats(name, rows)
            self.summary["load"] = out or {"status": "нет данных живого прогона"}
            self._load_not_measured()
            return
        load_http = self.ctx.http_client(mode="live", max_attempts=1)
        recent_txids = self.resolved.get("agreement_recent_txids") or []
        solid = (self.resolved.get("solid_head_at_run") or {}).get("num")
        if not solid:
            solid = block_header(self.tg.node, None, solidity=True)["num"]
        srcs: list[BenchSource] = []
        kl = trongrid_source(load_http, keyed=False)
        srcs.append(kl)
        k = trongrid_source(load_http, keyed=True)
        if k:
            srcs.append(k)
        srcs.append(publicnode_source(load_http))
        for env in ("TRON_RPC_URL", "TRON_RPC_URL_2"):
            p = paid_source(load_http, env, jsonrpc_suffix=self.opts.paid_jsonrpc_suffix)
            if p:
                srcs.append(p)
        only = {x.strip() for x in self.opts.load_sources.split(",") if x.strip()}
        if only:
            srcs = [s for s in srcs if s.name in only]
        out: dict[str, Any] = {}
        for i, src in enumerate(srcs):
            if i:
                time.sleep(10)  # cool-down between sources
            bucket = f"bench-{src.name}"
            src.set_rate_key(bucket)
            load_http.set_rate(bucket, 0)
            factory = self._mix(src, recent_txids, solid)
            cfg = dict(RAMP[src.name])
            if self.opts.load_scale != 1.0:
                cfg.update(step_s=cfg["step_s"] * self.opts.load_scale,
                           sustained_s=cfg["sustained_s"] * self.opts.load_scale)
                self.summary.setdefault("load_scale_note", f"durations scaled by {self.opts.load_scale} (smoke test)")
            rows = self._ramp_and_sustain(src, factory, cfg)
            self.ctx.write_jsonl(f"raw/load-{src.name}.jsonl", rows)
            out[src.name] = self._load_stats(src.name, rows)
            print(f"[{AREA}]   load {src.name}: first 429 at {out[src.name].get('first_429_step_rps')} rps; "
                  f"sustained {out[src.name].get('sustained', {}).get('achieved_ok_rps')} rps", flush=True)
        self.summary["load"] = out
        self._load_not_measured()

    def _load_not_measured(self) -> None:
        if not has_secret("TRONGRID_API_KEY"):
            self.not_measured.append({"what": "TronGrid с ключом: лимит, задержки, устойчивая скорость",
                                      "why": "не измерено: нет ключа (TRONGRID_API_KEY не задан)",
                                      "needed": "ключ TronGrid в .env; прогон переключится на него сам"})
        self._paid_not_measured("лимит, задержки, устойчивая скорость")

    def _mix(self, src: BenchSource, recent_txids: list[str], solid: int) -> Callable[[int], tuple[str, Callable]]:
        """Request mix for the load phases: what the tracer does per hop on this source."""
        case_txids = self.case_txids
        path_addrs = [A_VICTIM, A_HOP1, A_HOP2, A_BRIDGE_OUT, A_CUT, A_HUB]
        if src.v1 is not None:  # TronGrid: history page, receipt, events
            def factory(i: int):
                j = i // 3
                kind = ("v1_trc20", "node_txinfo", "v1_events")[i % 3]
                if kind == "v1_trc20":
                    a = path_addrs[j % len(path_addrs)]
                    params = {"contract_address": USDT_TRC20, "min_timestamp": 1_789_988_400_000,
                              "max_timestamp": 1_789_992_000_000, "order_by": "block_timestamp,asc", "limit": 20}
                    return kind, lambda: raw_request(src.v1, "GET", f"v1/accounts/{a}/transactions/trc20", params=params,
                                                     endpoint="v1/accounts/{address}/transactions/trc20")
                t = case_txids[j % len(case_txids)]
                if kind == "node_txinfo":
                    return kind, lambda: raw_request(src.node, "POST", "walletsolidity/gettransactioninfobyid",
                                                     json={"value": t}, endpoint="walletsolidity/gettransactioninfobyid")
                return kind, lambda: raw_request(src.v1, "GET", f"v1/transactions/{t}/events",
                                                 endpoint="v1/transactions/{hash}/events")
            return factory
        txs = (case_txids if src.paid else recent_txids) or case_txids

        def node_factory(i: int):
            j = i // 3
            kind = ("node_txinfo", "node_getaccount", "node_getblock")[i % 3]
            if kind == "node_txinfo":
                t = txs[j % len(txs)]
                return kind, lambda: raw_request(src.node, "POST", "walletsolidity/gettransactioninfobyid",
                                                 json={"value": t}, endpoint="walletsolidity/gettransactioninfobyid")
            if kind == "node_getaccount":
                a = path_addrs[j % len(path_addrs)]
                return kind, lambda: raw_request(src.node, "POST", "wallet/getaccount",
                                                 json={"address": a, "visible": True}, endpoint="wallet/getaccount")
            n = (THEFT_BLOCK + j) if src.paid else (solid - 1000 - j)
            return kind, lambda: raw_request(src.node, "POST", "wallet/getblock",
                                             json={"id_or_num": str(n), "detail": False}, endpoint="wallet/getblock")
        return node_factory

    def _ramp_and_sustain(self, src: BenchSource, factory: Callable, cfg: dict[str, Any]) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        seq = 0
        clean_rate = None
        hit_429 = False
        for rate in cfg["steps"]:
            r, info = open_loop(factory, rate=rate, duration_s=cfg["step_s"], phase="ramp", source=src.name, seq0=seq)
            for x in r:
                x["step_info"] = None
            if r:
                r[0]["step_info"] = info
            rows.extend(r)
            seq += len(r) + 1
            st = step_stats(r)
            if st.get("http_429"):
                hit_429 = True
                self._share_penalty(src)
                gap = round(info["wall_s"] - (info["t_first_429_s"] or info["wall_s"]), 3)
                pr = penalty_probe(factory, offsets_s=PENALTY_OFFSETS, source=src.name, seq0=seq)
                for x in pr:
                    x["probe_start_after_first_429_s"] = gap
                rows.extend(pr)
                seq += len(PENALTY_OFFSETS) + 1
                break
            if st.get("error_share", 0) > 0.2:
                rows.append({"phase": "ramp_stop", "source": src.name, "step_rps": rate, "seq": seq,
                             "reason": f"error share {st['error_share']} > 0.2 without 429"})
                break
            clean_rate = rate
            time.sleep(cfg["pause_s"])
        # sustained run at the highest clean step (one lower step if it trips)
        candidates = []
        declared = _declared(rows).get("declared_limit_rps")
        if clean_rate is not None:
            steps = cfg["steps"]
            idx = steps.index(clean_rate)
            if declared and declared - 2 > clean_rate:
                # the server states its limit: try just below it first, then the last clean ramp step
                candidates = [declared - 2, clean_rate]
            else:
                candidates = [clean_rate] + ([steps[idx - 1]] if idx > 0 else [])
        elif hit_429:
            candidates = [cfg["steps"][0] / 2]
        if hit_429:
            time.sleep(6)
        for rate in candidates:
            r, info = open_loop(factory, rate=rate, duration_s=cfg["sustained_s"], phase="sustained",
                                source=src.name, seq0=seq)
            if r:
                r[0]["step_info"] = info
            rows.extend(r)
            seq += len(r) + 1
            if not step_stats(r).get("http_429"):
                break
            self._share_penalty(src)
            gap = round(info["wall_s"] - (info["t_first_429_s"] or info["wall_s"]), 3)
            pr = penalty_probe(factory, offsets_s=PENALTY_OFFSETS, source=src.name, seq0=seq)
            for x in pr:
                x["probe_start_after_first_429_s"] = gap
            rows.extend(pr)
            seq += len(PENALTY_OFFSETS) + 1
            time.sleep(6)
        return rows

    def _share_penalty(self, src: BenchSource) -> None:
        """Tell other processes on this IP to back off the real host bucket too (shared limiter state)."""
        bucket = {"trongrid_keyless": "api.trongrid.io", "trongrid_key": "api.trongrid.io#key",
                  "publicnode": "tron-rpc.publicnode.com"}.get(src.name)
        if bucket:
            self.http.limiter.penalize(bucket, 5.0)

    @staticmethod
    def _load_stats(name: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
        ramp = [r for r in rows if r.get("phase") == "ramp"]
        steps = []
        for rate in sorted({r["step_rps"] for r in ramp}):
            rs = [r for r in ramp if r["step_rps"] == rate]
            steps.append({"step_rps": rate, **step_stats(rs)})
        first = next((s for s in steps if s.get("http_429")), None)
        first_ctx = first_429_context([r for r in ramp if r["step_rps"] == first["step_rps"]]) if first else None
        pen = [r for r in rows if r.get("phase") == "penalty"]
        pen_groups = []
        if pen:
            group: list[dict[str, Any]] = []
            for r in pen:
                if group and r["offset_s"] <= group[-1]["offset_s"]:
                    pen_groups.append(group)
                    group = []
                group.append(r)
            pen_groups.append(group)
        penalties = []
        for g in pen_groups:
            ok = next((r for r in g if r["status"] is not None and 200 <= r["status"] < 300), None)
            penalties.append({"probes": [{"offset_s": r["offset_s"], "status": r["status"]} for r in g],
                              "first_ok_offset_s": ok["offset_s"] if ok else None,
                              "last_429_offset_s": max((r["offset_s"] for r in g if r["status"] == 429), default=None)})
        sus = [r for r in rows if r.get("phase") == "sustained"]
        sus_runs = []
        for rate in sorted({r["step_rps"] for r in sus}, reverse=True):
            rs = [r for r in sus if r["step_rps"] == rate]
            st = step_stats(rs)
            st["first_429"] = first_429_context(rs)
            sus_runs.append({"rate_rps": rate, **st})
        clean = [r for r in sus_runs if not r.get("http_429")]
        last_clean_step = max((s["step_rps"] for s in steps if not s.get("http_429") and s.get("error_share", 1) <= 0.2),
                              default=None)
        all_ok = [r for r in rows if r.get("status") is not None and 200 <= r["status"] < 300 and r.get("latency_ms")]
        return {
            "requests_total": sum(1 for r in rows if "status" in r),
            **_declared(rows),
            "ramp_steps": steps,
            "first_429_step_rps": first["step_rps"] if first else None,
            "first_429": first_ctx,
            "highest_clean_step_rps": last_clean_step,
            "penalty": penalties,
            "sustained_runs": sus_runs,
            "sustained": clean[0] if clean else (sus_runs[-1] if sus_runs else {}),
            "latency_all_ok": {"n": len(all_ok), "p50": percentile([r["latency_ms"] for r in all_ok], 50),
                               "p95": percentile([r["latency_ms"] for r in all_ok], 95)},
        }

    # ============================================================ outputs
    def _projection_inputs(self) -> dict[str, Any]:
        s = self.summary
        load = s.get("load") or {}
        comp = (s.get("completeness") or {}).get("by_address_window") or []
        tg_name = self.tg.name if self.tg else "trongrid_key"

        def sustained(name: str) -> Any:
            v = (load.get(name) or {}).get("sustained") or {}
            return {"rate_rps": v.get("rate_rps"), "achieved_ok_rps": v.get("achieved_ok_rps"),
                    "error_share": v.get("error_share"), "latency_ms_p50": v.get("latency_ms_p50"),
                    "latency_ms_p95": v.get("latency_ms_p95"), "latency_by_kind": v.get("latency_by_kind"),
                    "http_429": v.get("http_429"), "sent": v.get("sent")}

        rows = []
        for r in comp:
            rows.append({"address": r["address"], "window": r["window"], "kind": r["kind"],
                         "blocks": r["to_block"] - r["from_block"] + 1, "v1_transfers": r["v1_transfers"],
                         "v1_pages": r["v1_pages"], "v1_out": r["v1_out"],
                         "v1_distinct_counterparties_out": r["v1_distinct_counterparties_out"],
                         "node_requests_trongrid": (r.get("node_requests") or {}).get(tg_name)})
        return {
            "load": {name: {"first_429_step_rps": (load.get(name) or {}).get("first_429_step_rps"),
                            "declared_limit_rps": (load.get(name) or {}).get("declared_limit_rps"),
                            "declared_suspension_s": (load.get(name) or {}).get("declared_suspension_s"),
                            "highest_clean_step_rps": (load.get(name) or {}).get("highest_clean_step_rps"),
                            "sustained": sustained(name),
                            "penalty_first_ok_offset_s": [p.get("first_ok_offset_s") for p in
                                                          (load.get(name) or {}).get("penalty") or []]}
                     for name in load if isinstance(load.get(name), dict) and "ramp_steps" in load.get(name)},
            "address_windows": rows,
            "pagination": {k: {kk: v.get(kk) for kk in ("rows", "pages", "complete", "rows_per_hour", "latency_ms_p50")}
                           for k, v in (s.get("pagination") or {}).items()},
            "freshness": s.get("freshness"),
            "publicnode_depth_days": (s.get("publicnode_depth") or {}).get("depth_days"),
        }

    def _markdown(self) -> str:
        s = self.summary
        L = [f"# tron_sources: замер источников TRON — прогон {self.ctx.run_id}", "",
             f"Режим HTTP: `{self.mode}`. Ключи (только наличие): " +
             ", ".join(f"{k} — {'есть' if v else 'нет'}" for k, v in s["keys_present"].items()
                       if k.startswith(("TRON", "TRONGRID"))) + ".", ""]
        if self.replay:
            L += [f"Офлайн-повтор: фазы A, C, P пересчитаны из записанных ответов; F, D, L — из сырых строк живого "
                  f"прогона `{s.get('live_source_run')}`.", ""]
        load = s.get("load") or {}
        if isinstance(load, dict) and load:
            L += ["## Нагрузка (ramp до первого 429, затем устойчивый прогон)", "",
                  "| Источник | Первый 429 на ступени, зап/с | Лимит / пауза в теле 429 | Последняя чистая ступень | Пауза после 429: первый успех через, с | Устойчиво, зап/с (успешных) | Ошибки | p50 / p95, мс |",
                  "|---|---|---|---|---|---|---|---|"]
            for name, v in load.items():
                if not isinstance(v, dict) or "ramp_steps" not in v:
                    continue
                su = v.get("sustained") or {}
                pen = ", ".join(str(p.get("first_ok_offset_s")) for p in v.get("penalty") or []) or "—"
                L.append(f"| {name} | {v.get('first_429_step_rps') or 'нет до потолка ступеней'} | "
                         f"{v.get('declared_limit_rps') or '—'} / {v.get('declared_suspension_s') or '—'} с | "
                         f"{v.get('highest_clean_step_rps')} | {pen} | {su.get('achieved_ok_rps')} (план {su.get('rate_rps')}) | "
                         f"{su.get('error_share')} | {su.get('latency_ms_p50')} / {su.get('latency_ms_p95')} |")
            L.append("")
        fr = (s.get("freshness") or {}).get("sources") or {}
        if fr:
            L += ["## Свежесть", "", "| Источник | Отставание solidified, блоков (медиана) | секунд (медиана) |", "|---|---|---|"]
            for name, v in fr.items():
                L.append(f"| {name} | {v['solid_lag_blocks']['median']} | {v['solid_lag_s']['median']} |")
            idx = (s.get("freshness") or {}).get("trongrid_v1_index")
            if idx:
                L.append(f"\nИндекс TronGrid v1: последнее событие USDT отстаёт от головы на "
                         f"{idx['latest_event_behind_head_blocks']['median']} блоков (медиана).")
            L.append("")
        dep = s.get("publicnode_depth") or {}
        if dep.get("oldest_served_block"):
            L += ["## Глубина истории PublicNode", "",
                  f"Самый старый отдаваемый блок {dep['oldest_served_block']} ({dep.get('oldest_served_utc')} UTC), "
                  f"глубина {dep.get('depth_days')} сут. Квитанции (gettransactioninfobyid): примерно с блока "
                  f"{dep.get('receipt_oldest_served_block_approx')} ({dep.get('receipt_oldest_served_utc')} UTC). "
                  "`eth_getLogs` (USDT Transfer от TX5XiR…): " + "; ".join(
                      f"{lab} {v.get('range')}: " + ", ".join(f"{n} {x.get('logs')}" for n, x in v.items()
                                                             if isinstance(x, dict))
                      for lab, v in (dep.get("getlogs_vs_history") or {}).items() if isinstance(v, dict)) + ".", ""]
        comp = s.get("completeness") or {}
        if comp:
            L += ["## Полнота TRC20: v1 против логов узла", "", "| Источник логов | Окон | Переводов в логах | В v1 | Совпало | Только v1 | Только логи |",
                  "|---|---|---|---|---|---|---|"]
            for name, v in (comp.get("by_source") or {}).items():
                L.append(f"| {name} | {v['windows']} | {v['node_transfers']} | {v['v1_transfers_same_windows']} | "
                         f"{v['matched']} | {v['only_v1']} | {v['only_node']} |")
            L.append("")
        ei = s.get("event_index") or {}
        if ei:
            L += ["## event_index против порядка логов в квитанции", ""]
            for name, v in ei.items():
                L.append(f"- {name}: {json.dumps(v, ensure_ascii=False)}")
            L.append("")
        ag = (s.get("agreement") or {}).get("groups") or {}
        if ag:
            L += ["## Совпадение транзакций между операторами", ""]
            for g, v in ag.items():
                L.append(f"- {g}: {json.dumps(v['sources'], ensure_ascii=False)}")
            L.append("")
        pg = s.get("pagination") or {}
        if pg:
            L += ["## Постраничная выдача", "", "| Цель | Страниц | Строк | Полная | Дубли | Нарушения порядка | Строк в час | p50, мс |",
                  "|---|---|---|---|---|---|---|---|"]
            for k, v in pg.items():
                L.append(f"| {k} | {v['pages']} | {v['rows']} | {v['complete']} | {v['duplicates']} | "
                         f"{v['order_violations']} | {v['rows_per_hour']} | {v['latency_ms_p50']} |")
            L.append("")
        if self.not_measured:
            L += ["## Не измерено", ""] + [f"- {n['what']}: {n['why']}. Нужно: {n['needed']}" for n in self.not_measured] + [""]
        if self.errors:
            L += ["## Ошибки", ""] + [f"- {e}" for e in self.errors] + [""]
        return "\n".join(L)


def run(args: argparse.Namespace) -> int:
    return Bench(args).run()
