"""Stage 2 area 'case001' (decisions 3 and 4.5): raw re-fetch, fact check, deterministic reference run.

    python -m ledgerhunt stage2 case001            # live: records into tests/fixtures/case-001/raw/
    python -m ledgerhunt stage2 case001 --replay   # offline from the recorded raw responses

Steps
1. Re-fetch raw responses for every identifier of tests/fixtures/case-001/case-001-ground-truth.json
   (TronGrid node + v1 APIs, PublicNode TRON as an independent node, Blockscout, public Ethereum
   RPC, LayerZero Scan, NEAR Intents 1Click, one TronScan account lookup).
2. Fact check: every checkable fixture fact vs raw data (confirmed / mismatch / not verifiable).
3. Reference run (baseline.tracer, no AI) starting only from the theft TXID.
4. Comparison with ground_truth; request counts and timings per source and per step.

Results: results/stage-2/case-001/<run_id>/. Extra options (after the area name):
  --skip-refetch      run steps 3-4 only
  --update-expected   overwrite tests/fixtures/case-001/raw/expected/reference-run.json with this run
"""

from __future__ import annotations

import argparse
import json
import os
import time
from collections import Counter
from typing import Any

from ..core.paths import rel_to_root, repo_root
from ..core.results import dumps, start_run
from ..baseline.compare import compare, coverage
from ..baseline.factcheck import FactChecker, summarize
from ..baseline.fetch import CaseSources
from ..baseline.refetch import Refetcher, build_inventory
from ..baseline.registry import ALGORITHM_VERSION, THRESHOLDS
from ..baseline.report import manifest_md, report_md
from ..baseline.tracer import ReferenceTracer, semantic_view

AREA = "case-001"
THEFT_TXID = "98f3ffca9d141f2172d28f46905c08e5f32fc6ce8d23f9a37b731fe2a6c1d1bb"


def fixture_paths() -> dict[str, Any]:
    base = repo_root() / "tests" / "fixtures" / "case-001"
    raw = base / "raw"
    return {
        "fixture": base / "case-001-ground-truth.json",
        "raw": raw,
        "store": raw / "http-store",
        "tronscan_store": raw / "tronscan-pending-consent",
        "expected": raw / "expected" / "reference-run.json",
        "manifest": raw / "MANIFEST.md",
    }


def _parse_extra(extra: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(prog="stage2 case001", add_help=False)
    p.add_argument("--skip-refetch", action="store_true")
    p.add_argument("--update-expected", action="store_true")
    ns, _unknown = p.parse_known_args(extra or [])
    return ns


def _client_summary(metrics: list[dict[str, Any]]) -> dict[str, Any]:
    by: dict[str, dict[str, Any]] = {}
    for m in metrics:
        p = by.setdefault(m["provider"], {"requests": 0, "errors": 0, "retries": 0, "http_429": 0, "latency_ms": 0.0,
                                          "total_ms": 0.0, "rate_wait_ms": 0.0, "bytes": 0, "replayed": 0})
        p["requests"] += 1
        p["errors"] += 1 if m["error_class"] else 0
        p["retries"] += max(0, (m["attempts"] or 1) - 1)
        p["http_429"] += sum(1 for s in m["attempt_statuses"] or [] if s == 429)
        p["latency_ms"] += m["latency_ms"] or 0.0
        p["total_ms"] += m["total_ms"] or 0.0
        p["rate_wait_ms"] += m["rate_wait_ms"] or 0.0
        p["bytes"] += m["bytes"] or 0
        p["replayed"] += 1 if m["from_replay"] else 0
    for p in by.values():
        for k in ("latency_ms", "total_ms", "rate_wait_ms"):
            p[k] = round(p[k], 1)
        p["latency_ms_mean"] = round(p["latency_ms"] / p["requests"], 1) if p["requests"] else None
    return dict(sorted(by.items()))


def run(args: argparse.Namespace) -> int:
    opts = _parse_extra(getattr(args, "extra", []) or [])
    paths = fixture_paths()
    fx = json.loads(paths["fixture"].read_text(encoding="utf-8"))
    mode = os.environ.get("LEDGERHUNT_HTTP_MODE", "record")
    replay = mode == "replay"
    ctx = start_run(AREA, config={
        "start_txid": THEFT_TXID,
        "algorithm": ALGORITHM_VERSION,
        "ai_used": False,
        "fixture": rel_to_root(paths["fixture"]),
        "raw_store": rel_to_root(paths["store"]),
        "tronscan_store": rel_to_root(paths["tronscan_store"]),
        "thresholds": THRESHOLDS,
        "skip_refetch": opts.skip_refetch,
        "note": "TronScan: one account lookup, pending written consent, not stored in any label store",
    }, reproduce="python -m ledgerhunt stage2 case001" + (" --replay" if replay else ""))
    print(f"[case001] run {ctx.run_id} mode={mode} -> {ctx.rel_dir}", flush=True)
    exit_code = 0
    summary: dict[str, Any] = {"run_id": ctx.run_id, "http_mode": mode}

    # ---------------- step 1: raw re-fetch
    facts: list[dict[str, Any]] = []
    fact_summary: dict[str, Any] = {"total": {"confirmed": 0, "mismatch": 0, "not_verifiable": 0}, "facts": 0}
    step1: dict[str, Any] = {"requests": 0, "errors": 0, "wall_s": 0}
    bundle = None
    if not opts.skip_refetch:
        print("[case001] step 1: raw re-fetch", flush=True)
        http1 = ctx.http_client(store_dir=paths["store"], tag=f"{AREA}/{ctx.run_id}/step1-refetch")
        inv = build_inventory(fx)
        ctx.write_json("step1-inventory.json", inv.__dict__)
        t0 = time.perf_counter()
        bundle = Refetcher(http1, tronscan_store=str(paths["tronscan_store"]),
                           log=lambda s: print(s, flush=True)).run(fx, inv)
        wall = time.perf_counter() - t0
        ctx.write_jsonl("step1-requests.jsonl", bundle.requests)
        errors = [r for r in bundle.requests if r.get("error")]
        step1 = {"requests": len(http1.metrics), "errors": len(errors), "wall_s": round(wall, 1),
                 "by_source": _client_summary(http1.metrics), "keys_present": bundle.keys_present,
                 "probes": bundle.probes, "replay_misses": bundle.replay_misses,
                 "empty_answers": Counter(r["provider"] for r in bundle.requests if r.get("empty"))}
        ctx.write_json("step1-summary.json", step1)
        if bundle.replay_misses:
            exit_code = 3
        print(f"[case001] step 1 done: {step1['requests']} requests, {len(errors)} errors, {wall:.1f}s", flush=True)

        # ---------------- step 2: fact check
        print("[case001] step 2: fact check", flush=True)
        checker = FactChecker(fx, bundle)
        facts = checker.run()
        fact_summary = summarize(facts)
        fact_summary["observations"] = checker.observations
        ctx.write_jsonl("step2-facts.jsonl", facts)
        ctx.write_json("step2-summary.json", fact_summary)
        print(f"[case001] step 2: {fact_summary['total']}", flush=True)

    # ---------------- step 3: reference run
    print("[case001] step 3: deterministic reference run from the theft TXID", flush=True)
    http3 = ctx.http_client(store_dir=paths["store"], tag=f"{AREA}/{ctx.run_id}/step3-reference")
    src = CaseSources(http3)
    t0 = time.perf_counter()
    ref = ReferenceTracer(src).run(THEFT_TXID)
    ref_wall = time.perf_counter() - t0
    ctx.write_json("step3-reference-run.json", ref)
    sem = semantic_view(ref)
    expected_check: dict[str, Any]
    if opts.update_expected:
        paths["expected"].parent.mkdir(parents=True, exist_ok=True)
        paths["expected"].write_text(dumps(sem) + "\n", encoding="utf-8", newline="\n")
        expected_check = {"status": "updated", "path": rel_to_root(paths["expected"])}
    elif paths["expected"].is_file():
        exp = json.loads(paths["expected"].read_text(encoding="utf-8"))
        same = exp == sem
        diff_keys = [] if same else sorted(k for k in set(exp["result"]) | set(sem["result"])
                                           if exp["result"].get(k) != sem["result"].get(k))
        expected_check = {"status": "matches" if same else "DIFFERS", "differing_result_keys": diff_keys,
                          "meta_equal": exp.get("meta") == sem.get("meta"),
                          "evidence_ids_equal": exp.get("evidence_ids") == sem.get("evidence_ids")}
    else:
        expected_check = {"status": "no expected file yet (run with --update-expected)"}
    print(f"[case001] step 3 done in {ref_wall:.1f}s; expected output: {expected_check['status']}", flush=True)

    # ---------------- step 4: comparison + timings
    cmp_rows = compare(fx, ref)
    cov = coverage(fx, ref)
    ctx.write_json("step4-comparison.json", {"comparison": cmp_rows, "coverage": cov,
                                             "expected_check": expected_check})
    timings = {
        "note": "live run: wall-clock includes waits of the shared rate limiter (all agents share one IP); "
                "rate_wait_ms shows that part. In replay mode latencies are the recorded ones.",
        "http_mode": mode,
        "step1_refetch": step1,
        "step3_reference": {**ref["timings"], "wall_s": round(ref_wall, 1),
                            "by_source_detail": _client_summary(http3.metrics)},
    }
    ctx.write_json("timings.json", timings)
    md = report_md(run_id=ctx.run_id, mode=mode, fact_summary=fact_summary, facts=facts, comparison=cmp_rows,
                   coverage=cov, ref=ref, step1=step1, expected_check=expected_check)
    ctx.write_text("report.md", md)
    if not replay and not opts.skip_refetch and bundle is not None:
        from datetime import datetime, timezone

        manifest = manifest_md([("Основное хранилище", paths["store"]),
                                ("TronScan (ожидается согласие)", paths["tronscan_store"])],
                               generated_utc=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
                               run_id=ctx.run_id, keys_present=bundle.keys_present,
                               tronscan_store_rel="tronscan-pending-consent")
        paths["manifest"].write_text(manifest, encoding="utf-8", newline="\n")

    cmp_counts = Counter(c["verdict"] for c in cmp_rows)
    summary.update({
        "facts": fact_summary.get("total"),
        "facts_count": fact_summary.get("facts"),
        "mismatches": fact_summary.get("mismatches", []),
        "comparison": dict(cmp_counts),
        "route": [x["address"] for x in ref["result"]["route"]],
        "total_lost_before_hub": ref["result"]["value_accounting"]["total_lost_before_hub"],
        "exchange_exits": [(x["recipient"], x["exchange"]) for x in ref["result"]["exchange_exits"]],
        "expected_check": expected_check,
        "requests": {"step1": step1.get("requests"), "step3": ref["timings"]["total_requests"]},
        "wall_s": {"step1": step1.get("wall_s"), "step3": round(ref_wall, 1)},
        "report": f"{ctx.rel_dir}/report.md",
    })
    short = (f"# case-001 ({ctx.run_id}, {mode})\n\nСверка фактов: {fact_summary.get('total')}. "
             f"Сравнение с ground_truth: {dict(cmp_counts)}. Ожидаемый результат: {expected_check['status']}. "
             f"Полный отчёт: report.md.\n")
    status = "ok" if exit_code == 0 else "replay_miss"
    ctx.finish(summary, short, status=status)
    if expected_check["status"] == "DIFFERS":
        print("[case001] WARNING: reference output differs from the stored expected output", flush=True)
    print(f"[case001] comparison: {dict(cmp_counts)}; results: {ctx.rel_dir}", flush=True)
    return exit_code
