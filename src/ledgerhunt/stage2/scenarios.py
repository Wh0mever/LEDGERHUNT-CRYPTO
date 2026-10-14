"""Stage 2 area 'scenarios': 4.6 Test scenario set with known answers and the held-out split.

``python -m ledgerhunt stage2 scenarios [extra flags]`` (or ``python run_stage2.py --only scenarios``):

1. regenerates the development set (54 synthetic scenarios + case-001 reference) in
   tests/scenarios/dev/ and its manifest; reports whether anything changed;
2. validates every development scenario (schema, store integrity, replay through the real
   clients, answer consistency, self-score);
3. checks the held-out set: file hashes against its manifest and, when the seed is
   available, a regeneration into a temporary directory compared hash-by-hash; then a
   structural validation reported as counts only. The held-out set is never rewritten here;
   ``--create-holdout`` creates it only when it does not exist. Only README.md and
   manifest.json of the held-out set are in git: without the content (kept by the owners)
   the check is skipped with a message, not failed;
4. compares the synthetic raw formats with real responses recorded in data/http-store;
5. writes everything to results/stage-2/scenarios/<run_id>/.

No network access unless ``--capture-format-refs`` is given: then the real USDT0 send of
case-001 (events, receipt, transaction) is fetched once in cache mode as a format reference.
"""

from __future__ import annotations

import argparse
import time
from collections import Counter
from pathlib import Path
from typing import Any

from ..core.paths import repo_root
from ..core.results import start_run

AREA = "scenarios"
FORMAT_REF_TX = "b49b0157d5327ca4b25683d2100d77c9b0c2c13584fdc96deea17a8c93057f6f"


def _parse(extra: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(prog="stage2 scenarios", add_help=False)
    p.add_argument("--create-holdout", action="store_true")
    p.add_argument("--skip-holdout-regeneration", action="store_true")
    p.add_argument("--capture-format-refs", action="store_true")
    ns, _unknown = p.parse_known_args(extra or [])
    return ns


def _capture_format_refs(ctx, http_mode: str | None) -> dict[str, Any]:
    from ..sources import TronGridClient

    # cache: fetch once, then reuse; under --replay never touch the network (a miss raises ReplayMiss)
    http = ctx.http_client(mode="replay" if http_mode == "replay" else "cache")
    tg = TronGridClient(http, api_key=None)
    out = {}
    for name, fn in (("events", tg.transaction_events), ("receipt", tg.get_transaction_info_by_id),
                     ("transaction", tg.get_transaction_by_id)):
        f = fn(FORMAT_REF_TX)
        out[name] = {"status": f.status, "from_replay": f.from_replay, "raw": f.ref_dict()}
    return out


def _md(summary: dict[str, Any]) -> str:
    g, v, h, s = summary["dev_generation"], summary["dev_validation"], summary["holdout"], summary["self_score_dev"]
    lines = [
        "# 4.6 Тестовые сценарии — итог прогона",
        "",
        f"- Набор для разработки: {g['synthetic_scenarios']} синтетических сценариев + эталон case-001; "
        f"категорий {len(g['by_category'])}, по {min(g['by_category'].values())}–{max(g['by_category'].values())} в каждой.",
        f"- Генерация: {g['seconds']} с; файлов {g['files_count']}, объём {g['bytes_total']} байт; "
        f"изменения относительно прошлой версии: {g['changed_vs_previous']}.",
        f"- Проверка набора для разработки: прошли {v['ok']} из {v['scenarios']} (ошибок {v['failed']}); "
        f"проверка воспроизведения через клиентов фундамента в режиме replay включена.",
        f"- Самопроверка оценщика (эталон как кандидат): сценариев засчитано {s['scenarios_passed']} из "
        f"{s['scenarios_counted']}, полнота фактов {s['fact_recall']}, ложных фактов {s['facts_false']}; "
        f"сценариев с отказом источника {s['scenarios_with_source_failure']} (вне знаменателя).",
    ]
    ss = summary["scorer_sanity"]
    lines.append(
        f"- Проверка оценщика на всём наборе: пустой результат — засчитано {ss['empty_candidate']['scenarios_passed']} "
        f"сценариев; один выдуманный факт в идеальном результате — засчитано "
        f"{ss['one_invented_fact']['scenarios_passed']}, ложных фактов {ss['one_invented_fact']['facts_false']}.")
    if h.get("present"):
        lines.append(
            f"- Отложенный набор: {h['synthetic_scenarios']} сценариев; хеши файлов совпали {h['files_matching']} из "
            f"{h['files_listed']}; повторная генерация: {h.get('regeneration')}; структурная проверка: "
            f"{h.get('validation_ok')} из {h['synthetic_scenarios']}. Содержимое отложенного набора в отчёт не выводится.")
    elif h.get("content") == "absent":
        lines.append(f"- Отложенный набор: {h['message']} (в git только README.md и manifest.json; по манифесту "
                     f"{h['manifest_synthetic_scenarios']} сценариев).")
    else:
        lines.append("- Отложенный набор отсутствует (создаётся владельцем флагом --create-holdout).")
    lines += ["", "## Сверка форматов с реальными ответами (data/http-store)", "",
              "| Источник | Эндпоинт | Реальных | Синтетических | Нет в синтетике | Лишнее в синтетике |",
              "|---|---|---|---|---|---|"]
    for r in summary["format_parity"]:
        miss = "не проверено" if r["missing_in_synthetic"] is None else (", ".join(r["missing_in_synthetic"][:6]) or "—")
        extra = "не проверено" if r["extra_in_synthetic"] is None else (", ".join(r["extra_in_synthetic"][:6]) or "—")
        lines.append(f"| {r['provider']} | `{r['endpoint']}` | {r['real_samples']} | {r['synthetic_samples']} | {miss} | {extra} |")
    notes = [r for r in summary["format_parity"] if r.get("note")]
    if notes:
        lines += [""] + [f"- {r['provider']} `{r['endpoint']}`: {r['note']}." for r in notes]
    lines += ["", "Подробности: `raw/` в папке прогона; описание набора — docs/stage-2/test-scenarios.md."]
    return "\n".join(lines) + "\n"


def run(args: argparse.Namespace) -> int:
    from ..scenarios import generator as G
    from ..scenarios.schema import TraceResult
    from ..scenarios.scorer import aggregate, candidate_from_expected, score_scenario
    from ..scenarios.sets import create_holdout, regenerate_dev, scenarios_root, verify_holdout
    from ..scenarios.validate import format_parity, validate_scenario
    from ..scenarios.world import World
    from ..core.restricted import absent_message, is_restricted, store_status

    opts = _parse(getattr(args, "extra", []) or [])
    root = scenarios_root()
    ctx = start_run(AREA, config={
        "dev_seed": G.DEV_SEED,
        "holdout_seed": "tests/scenarios/holdout/seed.txt (or env LEDGERHUNT_HOLDOUT_SEED); only its sha256 is recorded",
        "generator": G.GENERATOR_VERSION,
        "request_profile": G.REQUEST_PROFILE,
        "holdout_per_category": G.HOLDOUT_PER_CATEGORY,
        "scenarios_root": root.relative_to(repo_root()).as_posix(),
        "options": vars(opts),
    }, reproduce="python run_stage2.py --only scenarios")
    status_ok = True
    summary: dict[str, Any] = {}

    if opts.capture_format_refs:
        summary["format_refs"] = _capture_format_refs(ctx, getattr(args, "http_mode", None))

    t0 = time.perf_counter()
    dev = regenerate_dev(root)
    gen_s = round(time.perf_counter() - t0, 2)
    rows = dev["rows"]
    ctx.write_jsonl("raw/dev-generation.jsonl", rows)
    m = dev["manifest"]
    summary["dev_generation"] = {
        "synthetic_scenarios": len(rows), "by_category": m["by_category"], "seconds": gen_s,
        "files_count": m["files_count"], "bytes_total": m["bytes_total"], "tree_sha256": m["tree_sha256"],
        "changed_vs_previous": dev["changed_vs_previous"],
        "http_requests_recorded": sum(r["requests"] for r in rows),
        "designed_failures_recorded": sum(r["failed_by_design"] for r in rows),
    }

    dev_dirs = sorted(d for d in (root / "dev").iterdir() if d.is_dir() and (d / "expected.json").is_file())
    t1 = time.perf_counter()
    val = [validate_scenario(d) for d in dev_dirs]
    ctx.write_jsonl("raw/dev-validation.jsonl", val)
    bad = [v for v in val if not v["ok"]]
    status_ok &= not bad
    summary["dev_validation"] = {"scenarios": len(val), "ok": len(val) - len(bad), "failed": len(bad),
                                 "failed_ids": [v["scenario_id"] for v in bad],
                                 "seconds": round(time.perf_counter() - t1, 2)}

    scores, empty_scores, invented_scores = [], [], []
    for d in dev_dirs:
        exp = TraceResult.model_validate_json((d / "expected.json").read_text(encoding="utf-8"))
        if (exp.meta or {}).get("counts_toward_metrics") is False:
            continue
        world = World.load(d / "world.json")
        perfect = candidate_from_expected(exp)
        scores.append(score_scenario(exp, perfect, world))
        empty_scores.append(score_scenario(exp, TraceResult(scenario_id=exp.scenario_id), world))
        invented = perfect.model_copy(deep=True)
        invented.transfers.append(invented.transfers[0].model_copy(update={"txid": "f" * 64, "event_index": 0}))
        invented_scores.append(score_scenario(exp, invented, world))
    agg = aggregate(scores)
    ctx.write_json("raw/self-score-dev.json", {"aggregate": agg, "scenarios": [s.to_dict() for s in scores]})
    summary["self_score_dev"] = agg
    sanity = {"perfect_candidate": agg, "empty_candidate": aggregate(empty_scores),
              "one_invented_fact": aggregate(invented_scores)}
    ctx.write_json("raw/scorer-sanity-dev.json", sanity)
    summary["scorer_sanity"] = {k: {"pass_rate": v["pass_rate"], "scenarios_passed": v["scenarios_passed"],
                                    "source_failure_scenarios_handled": v["source_failure_scenarios_handled"],
                                    "fact_recall": v["fact_recall"], "facts_false": v["facts_false"]}
                                for k, v in sanity.items()}
    status_ok &= agg["facts_false"] == 0 and agg["scenarios_passed"] == agg["scenarios_counted"]
    status_ok &= sanity["empty_candidate"]["scenarios_passed"] == 0 and sanity["one_invented_fact"]["scenarios_passed"] == 0

    hdir = root / "holdout"
    if opts.create_holdout and not (hdir / "manifest.json").exists():
        summary["holdout_created"] = create_holdout(root)
    hv = verify_holdout(root, regenerate=not opts.skip_holdout_regeneration)
    if hv.get("present"):
        hdirs = sorted(d for d in hdir.iterdir() if d.is_dir() and (d / "expected.json").is_file())
        hval = [validate_scenario(d) for d in hdirs]
        hv["validation_ok"] = sum(1 for v in hval if v["ok"])
        hv["validation_failed"] = len(hval) - hv["validation_ok"]
        status_ok &= hv["integrity_ok"] and hv["validation_failed"] == 0 and hv.get("regeneration") != "differs"
    summary["holdout"] = hv
    ctx.write_json("raw/holdout-verification.json", hv)

    real_store = repo_root() / "data" / "http-store"
    parity = format_parity(real_store, dev_dirs)
    restricted_status = store_status(real_store)
    for r in parity:
        if is_restricted(r["provider"]) and r["real_samples"] == 0 and restricted_status.listed > restricted_status.present:
            r["note"] = f"{absent_message([r['provider']])}: реальных образцов нет, сверка формата не проведена"
            print(f"[{AREA}] {r['provider']}: {r['note']}", flush=True)
    ctx.write_json("raw/format-parity.json", parity)
    summary["format_parity"] = parity
    summary["counts"] = {
        "dev_synthetic": len(rows), "dev_reference": 1, "holdout": hv.get("synthetic_scenarios", 0),
        "dev_by_category": dict(Counter(r["category"] for r in rows)),
    }
    ctx.finish(summary, _md(summary), status="ok" if status_ok else "failed")
    hold_txt = (hv["message"] if hv.get("content") == "absent" else
                f"{hv.get('synthetic_scenarios', 0)} (integrity {hv.get('integrity_ok')}, regeneration "
                f"{hv.get('regeneration')})")
    print(f"[{AREA}] dev {len(rows)} (+case-001), validation ok {len(val) - len(bad)}/{len(val)}, "
          f"holdout {hold_txt}; results: {ctx.rel_dir}")
    return 0 if status_ok else 1
