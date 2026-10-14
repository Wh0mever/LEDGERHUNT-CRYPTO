"""Stage 2 area 'llm_models': 4.4 Claude model cost/quality benchmark (paid: runs only with --llm).

    python run_stage2.py --only llm_models --llm                  (live run, spends money, hard cap $20 total)
    python run_stage2.py --only llm_models --llm --replay         (offline: re-score the latest live run)
    python -m ledgerhunt stage2 llm_models --llm [options]

Options (after the stage2 flags; unknown to the shared parser, so they reach this module):
  --models haiku,sonnet,opus       models to run (default: all three)
  --tasks D1_mechanism,S1_...      task ids (default: all 14)
  --kinds decision,screenshot,report
  --repeats haiku=5,sonnet=3,opus=3
  --cap-usd 20                      hard cap for the whole benchmark (cannot be raised above 20)
  --workers 10                      parallel (model, effort, task kind) groups
  --no-checks / --checks-only       skip / only run the API behaviour checks
  --plan-only                       count tokens (free) and print reservations; no paid calls
  --replay-from <run dir>           replay source (default: latest live run with raw/calls.jsonl)
  --resume <run dir>|latest         complete a crashed live run: sends only the calls without an HTTP 200 row

Results: results/stage-2/llm/<run_id>/ ; cumulative cost ledger: results/stage-2/llm/cost-ledger.jsonl.
The Anthropic client is created only through ledgerhunt.core.config.make_anthropic_client (base_url is
always https://api.anthropic.com). No key value is printed or stored.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import threading
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any

AREA = "llm_models"
RESULTS_AREA = "llm"
HARD_CAP_USD = Decimal("20.00")
DEFAULT_REPEATS = {"claude-haiku-5-5": 5, "claude-sonnet-5-5": 3, "claude-opus-5-5": 3}
ALIASES = {"haiku": "claude-haiku-5-5", "sonnet": "claude-sonnet-5-5", "opus": "claude-opus-5-5"}


def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="stage2 llm_models", add_help=False)
    p.add_argument("--models", default="haiku,sonnet,opus")
    p.add_argument("--tasks", default=None)
    p.add_argument("--kinds", default=None)
    p.add_argument("--repeats", default=None)
    p.add_argument("--cap-usd", default=str(HARD_CAP_USD))
    p.add_argument("--workers", type=int, default=10)
    p.add_argument("--no-checks", action="store_true")
    p.add_argument("--checks-only", action="store_true")
    p.add_argument("--plan-only", action="store_true")
    p.add_argument("--replay-from", default=None)
    p.add_argument("--resume", default=None, help="run directory (or 'latest') to complete after a crash")
    return p


def _models(spec: str) -> list[str]:
    out = []
    for m in spec.split(","):
        m = m.strip()
        if m:
            out.append(ALIASES.get(m, m))
    from ..llmbench import MODELS

    bad = [m for m in out if m not in MODELS]
    if bad:
        raise SystemExit(f"unknown model(s): {bad}; known: {MODELS}")
    return out


def _repeats(spec: str | None) -> dict[str, int]:
    reps = dict(DEFAULT_REPEATS)
    if spec:
        for part in spec.split(","):
            k, _, v = part.partition("=")
            reps[ALIASES.get(k.strip(), k.strip())] = int(v)
    return reps


def _ledger_path() -> Path:
    from ..core.paths import results_root

    return results_root() / RESULTS_AREA / "cost-ledger.jsonl"


def _latest_live_run() -> Path | None:
    from ..core.paths import results_root

    base = results_root() / RESULTS_AREA
    if not base.is_dir():
        return None
    for d in sorted((p for p in base.iterdir() if p.is_dir()), reverse=True):
        cfg = d / "config.json"
        if (d / "raw" / "calls.jsonl").is_file() and cfg.is_file():
            mode = json.loads(cfg.read_text(encoding="utf-8")).get("config", {}).get("mode")
            if mode == "live":
                return d
    return None


def _write_static(ctx: Any, tasks: list[Any]) -> None:
    from ..llmbench import pricing
    from ..llmbench.docs_verified import DOC_CHECKS, VERIFIED_UTC
    from ..llmbench.prompts import SYSTEM_PROMPT

    ctx.write_text("inputs/system_prompt.txt", SYSTEM_PROMPT)
    ctx.write_json("inputs/prices.json", {"verified_utc": pricing.PRICES_VERIFIED_UTC, "sources": pricing.PRICE_SOURCES,
                                          "usd_per_mtok": pricing.price_table()})
    ctx.write_json("inputs/docs_verified.json", {"verified_utc": VERIFIED_UTC, "checks": DOC_CHECKS})
    for t in tasks:
        ctx.write_text(f"inputs/tasks/{t.task_id}.user.txt", t.user_text())
        ctx.write_json(f"inputs/tasks/{t.task_id}.schema.json", t.schema)
        ctx.write_json(f"inputs/tasks/{t.task_id}.expected.json", {
            "expected": t.expected, "efforts": t.efforts, "max_tokens": t.max_tokens,
            "image": t.image_path.name if t.image_path else None, "image_sha256": t.image_sha256(),
            "input_sha256": t.input_sha256(), "schema_sha256": t.schema_sha256(),
        })


def run(args: argparse.Namespace) -> int:
    llm_enabled = bool(getattr(args, "llm", False)) or os.environ.get("LEDGERHUNT_LLM_ENABLED") == "1"
    if not llm_enabled:
        print(f"[{AREA}] пропущено: платные вызовы Claude запускаются только с флагом --llm")
        return 2
    opts, unknown = _parser().parse_known_args(list(getattr(args, "extra", []) or []))
    if unknown:
        print(f"[{AREA}] неизвестные параметры: {unknown}")
        return 2
    replay_mode = bool(getattr(args, "replay", False)) or getattr(args, "http_mode", None) == "replay"

    from ..core.results import start_run
    from ..llmbench.tasks import EFFORTS_BY_KIND, get_tasks

    tasks = get_tasks(
        ids=[t.strip() for t in opts.tasks.split(",")] if opts.tasks else None,
        kinds=[k.strip() for k in opts.kinds.split(",")] if opts.kinds else None,
    )
    models = _models(opts.models)
    repeats = _repeats(opts.repeats)
    cap = min(Decimal(opts.cap_usd), HARD_CAP_USD)
    reproduce = "python run_stage2.py --only llm_models --llm" + (" --replay" if replay_mode else "")

    if replay_mode:
        return _run_replay(opts, tasks, reproduce)

    from ..core.config import has_secret

    if not has_secret("ANTHROPIC_API_KEY"):
        print(f"[{AREA}] не измерено: ключ ANTHROPIC_API_KEY не задан (.env)")
        return 2
    if os.environ.get("ANTHROPIC_AUTH_TOKEN"):
        print(f"[{AREA}] ОСТАНОВЛЕНО: в окружении задан ANTHROPIC_AUTH_TOKEN; проект использует только ключ из .env")
        return 2

    from ..core.config import make_anthropic_client
    from ..llmbench.api_checks import models_snapshot, run_checks
    from ..llmbench.ledger import CostLedger
    from ..llmbench.runner import GridRunner, dedupe_calls, load_calls, plan, request_params

    logging.getLogger("httpx2").setLevel(logging.WARNING)  # the SDK transport logs every request at INFO

    resumed_note: dict[str, Any] | None = None
    if opts.resume:
        ctx = _resume_context(opts.resume)
        cfg = ctx.config["config"]
        models, repeats = cfg["models"], {k: int(v) for k, v in cfg["repeats"].items()}
        tasks = get_tasks(ids=cfg["tasks"])
        print(f"[{AREA}] продолжение запуска {ctx.rel_dir}")
    else:
        config = {
            "mode": "plan" if opts.plan_only else "live",
            "models": models, "repeats": repeats, "tasks": [t.task_id for t in tasks],
            "efforts_by_kind": {k: list(v) for k, v in EFFORTS_BY_KIND.items()},
            "cap_usd_whole_benchmark": str(cap), "ledger": "results/stage-2/llm/cost-ledger.jsonl",
            "workers": opts.workers, "api_checks": not opts.no_checks, "checks_only": opts.checks_only,
            "anthropic_base_url": "https://api.anthropic.com", "prompt_cache": "system prompt, explicit 5-minute breakpoint",
            "thinking": "not set (adaptive by default on all three models), display omitted (default)",
            "output": "structured outputs: output_config.format json_schema",
        }
        ctx = start_run(RESULTS_AREA, config=config, reproduce=reproduce)
        print(f"[{AREA}] run {ctx.rel_dir}")
        _write_static(ctx, tasks)

    run_id = f"{RESULTS_AREA}/{ctx.run_id}"
    client = make_anthropic_client(max_retries=4, timeout=600.0)
    ledger = CostLedger(_ledger_path(), cap, run_id=run_id)
    if opts.resume:
        closed = ledger.close_stale(run_id, note="the run process crashed before this call's usage arrived; cost unknown, "
                                                 "counted at the reserved upper bound")
        resumed_note = {"resumed_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                        "closed_stale_reservations": closed}
        ctx.config.setdefault("resumes", []).append(resumed_note)
    print(f"[{AREA}] бюджет: лимит ${cap}, уже потрачено и зарезервировано ${ledger.committed_usd()}")

    groups = plan(tasks, models, repeats)
    if not opts.resume:
        ctx.write_json("raw/models_api.json", models_snapshot(client, tuple(models)))

    if opts.plan_only:
        from ..llmbench.client import count_tokens
        from ..llmbench.pricing import max_cost_usd

        rows, total = [], Decimal(0)
        seen: dict[tuple[str, str, str], int] = {}
        for (model, effort, _kind), items in groups.items():
            for it in items:
                key = (model, effort, it.task.task_id)
                if key not in seen:
                    seen[key] = count_tokens(client, request_params(it))
                res = max_cost_usd(model, seen[key], it.task.max_tokens)
                total += res
                rows.append({"model": model, "effort": effort, "task_id": it.task.task_id, "rep": it.rep,
                             "input_tokens_counted": seen[key], "max_tokens": it.task.max_tokens, "reservation_usd": str(res)})
        ctx.write_jsonl("plan.jsonl", rows)
        summary = {"calls": len(rows), "sum_of_reservations_usd": str(total), "cap_usd": str(cap),
                   "note": "reservation = worst case (all input at the 1-hour cache-write price, full max_tokens as output)"}
        print(f"[{AREA}] план: {len(rows)} вызовов, сумма резервов ${total} (верхняя граница)")
        ctx.finish(summary, f"# План\n\nВызовов: {len(rows)}; сумма резервов (верхняя граница) ${total}; лимит ${cap}.\n")
        return 0

    checks_path = ctx.dir / "raw" / "api_checks.jsonl"
    if opts.resume:
        checks = load_calls(checks_path) if checks_path.is_file() else []
    else:
        checks = []
        if not opts.no_checks:
            print(f"[{AREA}] проверки поведения API:")
            checks = run_checks(client, ledger, log=print)
            ctx.write_jsonl("raw/api_checks.jsonl", checks)

    calls_path = ctx.dir / "raw" / "calls.jsonl"
    if not opts.checks_only:
        if opts.resume and calls_path.is_file():
            done = {(r["model"], r["effort"], r["task_id"], r["rep"]) for r in load_calls(calls_path)
                    if r.get("http_status") == 200}
            groups = {k: [it for it in v if (it.model, it.effort, it.task.task_id, it.rep) not in done]
                      for k, v in groups.items()}
            groups = {k: v for k, v in groups.items() if v}
        sink_lock = threading.Lock()

        def sink(row: dict[str, Any]) -> None:
            with sink_lock:
                ctx.append_jsonl("raw/calls.jsonl", row)

        n = sum(len(v) for v in groups.values())
        print(f"[{AREA}] сетка: {n} вызовов в {len(groups)} группах (модель x effort x тип задачи)")
        runner = GridRunner(client, ledger, run_id=run_id, sink=sink, log=print, max_workers=opts.workers)
        runner.run(groups)
        if resumed_note is not None:
            resumed_note["calls_sent"] = n

    raw_rows = load_calls(calls_path) if calls_path.is_file() else []
    return _finish_live(ctx, raw_rows, checks, ledger, run_id, cap)


def _resume_context(spec: str) -> Any:
    from ..core.paths import repo_root
    from ..core.results import RunContext

    d = _latest_live_run() if spec == "latest" else Path(spec)
    if d is not None and not d.is_absolute():
        d = repo_root() / d
    if d is None or not (d / "config.json").is_file():
        raise SystemExit(f"--resume: run directory not found: {spec}")
    cfg = json.loads((d / "config.json").read_text(encoding="utf-8"))
    started = datetime.strptime(cfg["started_utc"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    return RunContext(RESULTS_AREA, d, cfg["run_id"], started, cfg)


def _finish_live(ctx: Any, raw_rows: list[dict[str, Any]], checks: list[dict[str, Any]], ledger: Any, run_id: str,
                 cap: Decimal) -> int:
    from ..llmbench.runner import dedupe_calls, failed_attempts
    from ..llmbench.summarize import markdown, summarize

    rows = dedupe_calls(raw_rows)
    summary = summarize(rows) if rows else {}
    summary["failed_attempts_all"] = failed_attempts(raw_rows)
    check_cost = sum((Decimal(str(c.get("cost_usd") or 0)) for c in checks), Decimal(0))
    summary["api_checks"] = [{k: c.get(k) for k in ("id", "model", "claim", "expect", "http_status", "error_message",
                                                     "expectation_met", "cost_usd")} for c in checks]
    summary["api_checks_cost_usd"] = str(check_cost)
    summary["ledger"] = ledger.summary(run_id=run_id)
    summary["upper_bound_calls"] = ledger.upper_bound_calls(run_id)
    md = markdown(summary) if rows else "# Замер моделей Claude\n\nТолько проверки API.\n"
    if checks:
        md += ("\n## Проверки поведения API\n\n| Проверка | Модель | Ожидание | HTTP | Совпало с документацией | Сообщение |\n"
               "|---|---|---|---|---|---|\n")
        for c in checks:
            msg = (c.get("error_message") or "").replace("|", "/")[:160]
            md += f"| {c['id']} | {c['model']} | {c['expect']} | {c.get('http_status')} | {c.get('expectation_met')} | {msg} |\n"
    if summary.get("failed_attempts_all") or summary.get("upper_bound_calls"):
        md += "\n## Сбои вызовов\n\n"
        for f in summary.get("failed_attempts_all", []):
            md += (f"- {f['model']} @{f['effort']} {f['task_id']} r{f['rep']}: {f['status']} {f.get('error_type') or ''} "
                   f"{(f.get('error_message') or '')[:120]}\n")
        for u in summary.get("upper_bound_calls", []):
            md += f"- оплата неизвестна, учтена верхняя граница ${u['upper_bound_usd']}: {u['call_id']}\n"
    run = summary["ledger"]["run"]
    md += (f"\n## Бюджет\n\nЛимит на весь замер: ${summary['ledger']['cap_usd']}. В этом запуске: точно по usage "
           f"${run['exact_usd_from_usage']}; вызовы с неизвестным usage (обрыв соединения) учтены по верхней границе "
           f"${run['upper_bound_usd_unknown_usage']}. Всего по журналу (с верхними границами): "
           f"${summary['ledger']['settled_usd_all_runs']}; остаток ${summary['ledger']['remaining_usd']}.\n")
    ctx.finish(summary, md)
    print(f"[{AREA}] запуск: точно ${run['exact_usd_from_usage']} + верхняя граница ${run['upper_bound_usd_unknown_usage']}; "
          f"всего по журналу ${summary['ledger']['settled_usd_all_runs']} из ${cap}")
    print(f"[{AREA}] результаты: {ctx.rel_dir}")
    return 0


def _run_replay(opts: argparse.Namespace, tasks: list[Any], reproduce: str) -> int:
    from ..core.results import start_run
    from ..llmbench.runner import dedupe_calls, load_calls, replay
    from ..llmbench.summarize import markdown, summarize

    src = Path(opts.replay_from) if opts.replay_from else _latest_live_run()
    if src is None or not (src / "raw" / "calls.jsonl").is_file():
        print(f"[{AREA}] replay: нет записанного живого запуска (results/stage-2/llm/<run>/raw/calls.jsonl)")
        return 3
    calls = dedupe_calls(load_calls(src / "raw" / "calls.jsonl"))
    rows = replay(calls, tasks)
    from ..core.paths import rel_to_root

    ctx = start_run(RESULTS_AREA, config={"mode": "replay", "source_run": rel_to_root(src), "calls": len(calls)},
                    reproduce=reproduce)
    ctx.write_jsonl("raw/calls.replayed.jsonl", rows)
    stale = [r for r in rows if r.get("replay_status", "").startswith("stale")]
    summary = summarize([r for r in rows if r.get("replay_status") in ("rescored", "no_response")])
    summary["replay"] = {"source_run": rel_to_root(src), "rescored": sum(r.get("replay_status") == "rescored" for r in rows),
                         "stale": len(stale), "note": "no API calls; cost and latency are the recorded values"}
    ctx.finish(summary, markdown(summary, title="Замер моделей Claude (повтор из записи)"))
    print(f"[{AREA}] replay из {rel_to_root(src)}: пересчитано {summary['replay']['rescored']}, устаревших входов {len(stale)}")
    return 0
