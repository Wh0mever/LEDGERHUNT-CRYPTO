"""Aggregate benchmark calls into tables: per cell, per kind, screenshots, caching, recommendations and
the cost of one standard investigation. Amounts are Decimal and serialised as strings."""

from __future__ import annotations

import statistics
from collections import defaultdict
from decimal import ROUND_HALF_UP, Decimal
from typing import Any, Iterable

from . import MODELS

Q6 = Decimal("0.000001")
EFFORT_ORDER = {"low": 0, "medium": 1, "high": 2, "xhigh": 3, "max": 4}
DECISIONS = ("D1_mechanism", "D2_split", "D3_usdt0_exit", "D4_rango", "D5_near_intents", "D6_hub", "D7_exchange", "D8_funder")


def d(x: Any) -> Decimal:
    return Decimal(str(x)) if x not in (None, "") else Decimal(0)


def q(x: Decimal) -> str:
    return str(x.quantize(Q6, rounding=ROUND_HALF_UP))


def _mean(xs: list[float]) -> float | None:
    return round(statistics.fmean(xs), 4) if xs else None


def _median(xs: list[float]) -> float | None:
    return round(statistics.median(xs), 1) if xs else None


def _u(row: dict[str, Any], key: str) -> int:
    u = row.get("usage") or {}
    if key == "thinking_tokens":
        return int((u.get("output_tokens_details") or {}).get("thinking_tokens") or 0)
    return int(u.get(key) or 0)


def completed(rows: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    return [r for r in rows if r.get("http_status") == 200]


def cell_stats(rows: list[dict[str, Any]]) -> dict[str, Any]:
    done = completed(rows)
    scores = [r["score"] for r in done if r.get("score")]
    costs = [d(r.get("cost_usd")) for r in done]
    nocache = [d(r.get("no_cache_cost_usd")) for r in done]
    out = {
        "attempted": len([r for r in rows if r.get("status") not in ("skipped_budget",)]),
        "completed": len(done),
        "http_errors": len([r for r in rows if r.get("http_status") not in (200, None)]),
        "refusals": len([r for r in done if r.get("stop_reason") == "refusal"]),
        "refusal_categories": sorted({(r.get("stop_details") or {}).get("category") or "null" for r in done if r.get("stop_reason") == "refusal"}),
        "max_tokens_stops": len([r for r in done if r.get("stop_reason") == "max_tokens"]),
        "schema_valid_share": _mean([1.0 if s.get("schema_valid") else 0.0 for s in scores]),
        "mean_score": _mean([s.get("score", 0.0) for s in scores]),
        "pass_rate": _mean([1.0 if s.get("passed") else 0.0 for s in scores]),
        "invented_identifier_calls": len([s for s in scores if s.get("invented_identifiers")]),
        "mean_input_tokens": _mean([_u(r, "input_tokens") for r in done]),
        "mean_cache_write_tokens": _mean([_u(r, "cache_creation_input_tokens") for r in done]),
        "mean_cache_read_tokens": _mean([_u(r, "cache_read_input_tokens") for r in done]),
        "mean_output_tokens": _mean([_u(r, "output_tokens") for r in done]),
        "mean_thinking_tokens": _mean([_u(r, "thinking_tokens") for r in done]),
        "mean_cost_usd": q(sum(costs, Decimal(0)) / len(costs)) if costs else None,
        "mean_no_cache_cost_usd": q(sum(nocache, Decimal(0)) / len(nocache)) if nocache else None,
        "total_cost_usd": q(sum(costs, Decimal(0))),
        "total_no_cache_cost_usd": q(sum(nocache, Decimal(0))),
        "median_latency_ms": _median([r["latency_ms"] for r in done if r.get("latency_ms") is not None]),
        "max_latency_ms": max([r["latency_ms"] for r in done if r.get("latency_ms") is not None], default=None),
        "median_ttft_text_ms": _median([r["ttft_text_ms"] for r in done if r.get("ttft_text_ms") is not None]),
    }
    return out


def group_by(rows: list[dict[str, Any]], *keys: str) -> dict[tuple, list[dict[str, Any]]]:
    g: dict[tuple, list[dict[str, Any]]] = defaultdict(list)
    for r in rows:
        g[tuple(r.get(k) for k in keys)].append(r)
    return dict(g)


def _sort_key(k: tuple) -> tuple:
    model = k[0]
    return (MODELS.index(model) if model in MODELS else 9, EFFORT_ORDER.get(k[1], 9), *map(str, k[2:]))


def screenshot_accuracy(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    shots = [r for r in completed(rows) if r.get("kind") == "screenshot" and r.get("score")]
    checks = ("txid_recall", "txid_precision", "address_recall", "address_precision", "amount_recall",
              "time_utc_correct", "no_invented_utc_time", "seed_flagged", "seed_not_reproduced", "phone_flagged",
              "phone_not_reproduced", "compromise_advice", "injection_flagged", "no_recovery_claim", "target_address_kept",
              "no_false_injection_flag", "no_false_seed_flag", "no_invented_identifiers")
    for (model, effort), rs in sorted(group_by(shots, "model", "effort").items(), key=lambda kv: _sort_key(kv[0])):
        row: dict[str, Any] = {"model": model, "effort": effort, "calls": len(rs)}
        for c in checks:
            vals = [r["score"]["checks"][c] for r in rs if c in (r["score"].get("checks") or {})]
            row[c] = _mean(vals)
        row["pass_rate"] = _mean([1.0 if r["score"].get("passed") else 0.0 for r in rs])
        row["mean_cost_usd"] = q(sum((d(r.get("cost_usd")) for r in rs), Decimal(0)) / len(rs))
        out.append(row)
    return out


def cache_effect(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    done = completed(rows)
    for (model, effort), rs in sorted(group_by(done, "model", "effort").items(), key=lambda kv: _sort_key(kv[0])):
        prompt = sum(_u(r, "input_tokens") + _u(r, "cache_creation_input_tokens") + _u(r, "cache_read_input_tokens") for r in rs)
        read = sum(_u(r, "cache_read_input_tokens") for r in rs)
        actual = sum((d(r.get("cost_usd")) for r in rs), Decimal(0))
        nocache = sum((d(r.get("no_cache_cost_usd")) for r in rs), Decimal(0))
        first_of_task = [r for r in rs if r.get("rep") == 1 and (r.get("order_in_group") or 0) > 1]
        repeats = [r for r in rs if (r.get("rep") or 1) > 1]
        out.append({
            "model": model, "effort": effort, "calls": len(rs),
            "prompt_tokens": prompt, "cache_read_tokens": read,
            "cache_write_tokens": sum(_u(r, "cache_creation_input_tokens") for r in rs),
            "cache_read_share": round(read / prompt, 4) if prompt else None,
            "cost_actual_usd": q(actual), "cost_without_cache_usd": q(nocache),
            "saving_usd": q(nocache - actual),
            "saving_share": round(float((nocache - actual) / nocache), 4) if nocache else None,
            "first_call_of_new_task_mean_cache_read": _mean([_u(r, "cache_read_input_tokens") for r in first_of_task]),
            "repeat_call_mean_cache_read": _mean([_u(r, "cache_read_input_tokens") for r in repeats]),
        })
    return out


def recommendations(cells: dict[tuple, dict[str, Any]]) -> list[dict[str, Any]]:
    """Per task: the cheapest (model, effort) whose every repeat passed with mean score >= 0.95."""
    by_task: dict[str, list[tuple[tuple, dict[str, Any]]]] = defaultdict(list)
    for k, st in cells.items():
        if st["completed"]:
            by_task[k[2]].append((k, st))
    out = []
    for task_id in sorted(by_task):
        cands = by_task[task_id]
        good = [(k, st) for k, st in cands if (st["pass_rate"] or 0) >= 1.0 and (st["mean_score"] or 0) >= 0.95]
        if good:
            k, st = min(good, key=lambda kv: d(kv[1]["mean_cost_usd"]))
            basis = "cheapest cell where every repeat passed (mean score >= 0.95)"
        else:
            k, st = max(cands, key=lambda kv: ((kv[1]["pass_rate"] or 0), (kv[1]["mean_score"] or 0), -float(d(kv[1]["mean_cost_usd"]))))
            basis = "no cell passed every repeat; best pass rate / score shown"
        out.append({"task_id": task_id, "model": k[0], "effort": k[1], "mean_score": st["mean_score"],
                    "pass_rate": st["pass_rate"], "mean_cost_usd": st["mean_cost_usd"],
                    "median_latency_ms": st["median_latency_ms"], "basis": basis,
                    "passing_cells": [f"{kk[0]}@{kk[1]}" for kk, _ in sorted(good, key=lambda kv: _sort_key(kv[0]))]})
    return out


def _mean_cost(cells: dict[tuple, dict[str, Any]], model: str, effort: str, task_ids: Iterable[str],
               key: str = "mean_cost_usd") -> Decimal | None:
    vals = [d(cells[(model, effort, t)][key]) for t in task_ids
            if (model, effort, t) in cells and cells[(model, effort, t)].get(key) is not None]
    return sum(vals, Decimal(0)) / len(vals) if vals else None


SHOTS = ("S1_wallet_detail", "S2_explorer_tx", "S3_chat_buyer", "S4_chat_seed_phone", "S5_chat_injection")


def investigation_cost(cells: dict[tuple, dict[str, Any]], recs: list[dict[str, Any]] | None = None,
                       *, planning_calls: int = 5, routine_calls: int = 30, screenshots: int = 4) -> list[dict[str, Any]]:
    """Cost of one standard investigation built from measured per-call means.

    Shape from the owner's estimate (decision 1.2): ~5 planning/verification decisions, 1 report,
    ~30 routine calls and 3-5 screenshots (4 used). Planning = mean measured cost of a decision call (D1-D8)
    of the given model/effort. Routine calls were not measured separately: the proxy is the mean measured
    cost of a Claude Haiku 5.5 @medium decision call (it carries the ~1.5k-token system prompt, the output
    schema and 0.6-2.5k tokens of case data, so it is an upper bound for a short routine call). Screenshots =
    mean Claude Haiku 5.5 @low screenshot call. Two totals: as measured (system prompt + schema read from
    the prompt cache on repeated calls of the same task type) and without any cache hit.
    """
    scenarios = []

    def part(model: str, effort: str, tasks: Iterable[str], n: int) -> tuple[Decimal | None, Decimal | None]:
        a = _mean_cost(cells, model, effort, tasks)
        b = _mean_cost(cells, model, effort, tasks, key="mean_no_cache_cost_usd")
        return (a * n if a is not None else None, b * n if b is not None else None)

    def add(name: str, plan: tuple[str, str], report: tuple[str, str], owner: str | None) -> None:
        parts = {
            "planning": part(plan[0], plan[1], DECISIONS, planning_calls),
            "report": part(report[0], report[1], ("R1_report",), 1),
            "routine": part("claude-haiku-5-5", "medium", DECISIONS, routine_calls),
            "screenshots": part("claude-haiku-5-5", "low", SHOTS, screenshots),
        }
        total = sum((v[0] for v in parts.values() if v[0] is not None), Decimal(0))
        total_nc = sum((v[1] for v in parts.values() if v[1] is not None), Decimal(0))
        scenarios.append({
            "scenario": name, "planning": f"{plan[0]}@{plan[1]} x{planning_calls}",
            "report": f"{report[0]}@{report[1]}", "routine": f"claude-haiku-5-5@medium (proxy) x{routine_calls}",
            "screenshots": f"claude-haiku-5-5@low x{screenshots}",
            "parts_usd": {k: (q(v[0]) if v[0] is not None else None) for k, v in parts.items()},
            "total_usd": q(total), "total_no_cache_usd": q(total_nc),
            "complete": all(v[0] is not None for v in parts.values()), "owner_estimate_usd": owner,
        })

    O, S, H = "claude-opus-5-5", "claude-sonnet-5-5", "claude-haiku-5-5"
    add("Opus 5.5 @medium: решения и отчёт", (O, "medium"), (O, "medium"), "0.50")
    add("Opus 5.5 @high: решения и отчёт", (O, "high"), (O, "high"), "0.50")
    add("Sonnet 5.5 @medium: решения и отчёт", (S, "medium"), (S, "medium"), "0.30")
    add("Sonnet 5.5 @high: решения и отчёт", (S, "high"), (S, "high"), "0.30")
    add("Sonnet 5.5: решения @high, отчёт @medium", (S, "high"), (S, "medium"), None)
    add("Haiku 5.5 @medium: решения; Sonnet 5.5 @medium: отчёт", (H, "medium"), (S, "medium"), None)
    add("Haiku 5.5 @medium: решения и отчёт", (H, "medium"), (H, "medium"), None)

    # Proposed mix (docs/stage-2/llm-models.md): per decision point; planning = mean over D1-D8 of the chosen cells.
    chosen = [_mean_cost(cells, m, e, (t,)) for t, (m, e) in PROPOSED.items()]
    chosen_nc = [_mean_cost(cells, m, e, (t,), key="mean_no_cache_cost_usd") for t, (m, e) in PROPOSED.items()]
    if all(c is not None for c in chosen + chosen_nc):
        plan_m = sum(chosen, Decimal(0)) / len(chosen) * planning_calls
        plan_nc = sum(chosen_nc, Decimal(0)) / len(chosen_nc) * planning_calls
        rep = part(*PROPOSED_REPORT, ("R1_report",), 1)
        rout = part(H, "medium", DECISIONS, routine_calls)
        shot = part(*PROPOSED_SCREENSHOTS, SHOTS, screenshots)
        parts = {"planning": (plan_m, plan_nc), "report": rep, "routine": rout, "screenshots": shot}
        scenarios.append({
            "scenario": "Предлагаемый набор по точкам решений", "planning": "per decision point (PROPOSED), mean x5",
            "report": "@".join(PROPOSED_REPORT), "routine": f"claude-haiku-5-5@medium (proxy) x{routine_calls}",
            "screenshots": "@".join(PROPOSED_SCREENSHOTS) + f" x{screenshots}",
            "parts_usd": {k: (q(v[0]) if v[0] is not None else None) for k, v in parts.items()},
            "total_usd": q(sum((v[0] for v in parts.values() if v[0] is not None), Decimal(0))),
            "total_no_cache_usd": q(sum((v[1] for v in parts.values() if v[1] is not None), Decimal(0))),
            "complete": all(v[0] is not None for v in parts.values()), "owner_estimate_usd": None,
        })
    return scenarios


# Proposed model/effort per decision point (see docs/stage-2/llm-models.md for the reasoning).
PROPOSED: dict[str, tuple[str, str]] = {
    "D1_mechanism": ("claude-haiku-5-5", "medium"),
    "D2_split": ("claude-sonnet-5-5", "high"),
    "D3_usdt0_exit": ("claude-sonnet-5-5", "high"),
    "D4_rango": ("claude-sonnet-5-5", "high"),
    "D5_near_intents": ("claude-sonnet-5-5", "high"),
    "D6_hub": ("claude-sonnet-5-5", "high"),
    "D7_exchange": ("claude-haiku-5-5", "medium"),
    "D8_funder": ("claude-sonnet-5-5", "high"),
}
PROPOSED_REPORT = ("claude-sonnet-5-5", "medium")
PROPOSED_SCREENSHOTS = ("claude-haiku-5-5", "low")


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    cells = {k: cell_stats(v) for k, v in group_by(rows, "model", "effort", "task_id").items()}
    kinds = {k: cell_stats(v) for k, v in group_by(rows, "model", "effort", "kind").items()}
    recs = recommendations(cells)
    done = completed(rows)
    total = sum((d(r.get("cost_usd")) for r in done), Decimal(0))
    return {
        "calls_total": len(rows),
        "calls_completed": len(done),
        "calls_skipped_budget": len([r for r in rows if r.get("status") == "skipped_budget"]),
        "http_errors": [{k: r.get(k) for k in ("model", "effort", "task_id", "rep", "http_status", "error_type", "error_message")}
                        for r in rows if r.get("http_status") not in (200, None)],
        "refusals": [{k: r.get(k) for k in ("model", "effort", "task_id", "rep", "stop_details")}
                     for r in done if r.get("stop_reason") == "refusal"],
        "spend_usd_from_usage": q(total),
        "cells": [{"model": k[0], "effort": k[1], "task_id": k[2], **v} for k, v in sorted(cells.items(), key=lambda kv: _sort_key(kv[0]))],
        "by_kind": [{"model": k[0], "effort": k[1], "kind": k[2], **v} for k, v in sorted(kinds.items(), key=lambda kv: _sort_key(kv[0]))],
        "by_model": [{"model": m, "calls": len(completed(rs)),
                      "cost_usd": q(sum((d(r.get("cost_usd")) for r in completed(rs)), Decimal(0))),
                      "input_tokens": sum(_u(r, "input_tokens") for r in completed(rs)),
                      "cache_write_tokens": sum(_u(r, "cache_creation_input_tokens") for r in completed(rs)),
                      "cache_read_tokens": sum(_u(r, "cache_read_input_tokens") for r in completed(rs)),
                      "output_tokens": sum(_u(r, "output_tokens") for r in completed(rs)),
                      "thinking_tokens": sum(_u(r, "thinking_tokens") for r in completed(rs)),
                      "refusals": len([r for r in completed(rs) if r.get("stop_reason") == "refusal"]),
                      "max_tokens_stops": len([r for r in completed(rs) if r.get("stop_reason") == "max_tokens"])}
                     for (m,), rs in sorted(group_by(rows, "model").items(), key=lambda kv: MODELS.index(kv[0][0]) if kv[0][0] in MODELS else 9)],
        "screenshots": screenshot_accuracy(rows),
        "cache": cache_effect(rows),
        "recommendations": recs,
        "investigation_cost": investigation_cost(cells, recs),
    }


# ---------------------------------------------------------------- markdown


def _short(model: str) -> str:
    return model.replace("claude-", "").replace("-5-5", " 5.5")


def _f(x: Any, nd: int = 2) -> str:
    if x is None:
        return "—"
    if isinstance(x, float):
        return f"{x:.{nd}f}"
    return str(x)


def markdown(summary: dict[str, Any], *, title: str = "Замер моделей Claude") -> str:
    L: list[str] = [f"# {title}", ""]
    L.append(f"Вызовов: {summary['calls_total']}, завершено (HTTP 200): {summary['calls_completed']}, "
             f"пропущено из-за лимита бюджета: {summary['calls_skipped_budget']}. "
             f"Расход по полям usage: ${summary['spend_usd_from_usage']}.")
    L.append("")
    L.append("## По типам задач")
    L.append("")
    L.append("| Модель | effort | Тип | Вызовов | Схема валидна | Средний балл | Доля пройденных | Отказы | Вход (некеш.) | Запись в кеш | Чтение из кеша | Выход (вкл. мышление) | Мышление | Средняя стоимость, $ | Медиана задержки, с |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for r in summary["by_kind"]:
        L.append(f"| {_short(r['model'])} | {r['effort']} | {r['kind']} | {r['completed']} | {_f(r['schema_valid_share'])} | "
                 f"{_f(r['mean_score'])} | {_f(r['pass_rate'])} | {r['refusals']} | {_f(r['mean_input_tokens'], 0)} | "
                 f"{_f(r['mean_cache_write_tokens'], 0)} | {_f(r['mean_cache_read_tokens'], 0)} | {_f(r['mean_output_tokens'], 0)} | "
                 f"{_f(r['mean_thinking_tokens'], 0)} | {r['mean_cost_usd']} | {_f((r['median_latency_ms'] or 0) / 1000, 1)} |")
    L.append("")
    L.append("## По точкам решений и задачам")
    L.append("")
    L.append("| Задача | Модель | effort | n | Балл | Пройдено | Выход, ток. | Стоимость, $ | Задержка, с |")
    L.append("|---|---|---|---|---|---|---|---|---|")
    for r in sorted(summary["cells"], key=lambda c: (c["task_id"], MODELS.index(c["model"]) if c["model"] in MODELS else 9, EFFORT_ORDER.get(c["effort"], 9))):
        L.append(f"| {r['task_id']} | {_short(r['model'])} | {r['effort']} | {r['completed']} | {_f(r['mean_score'])} | "
                 f"{_f(r['pass_rate'])} | {_f(r['mean_output_tokens'], 0)} | {r['mean_cost_usd']} | {_f((r['median_latency_ms'] or 0) / 1000, 1)} |")
    L.append("")
    L.append("## Рекомендация по каждой задаче (самая дешёвая ячейка, где все повторы прошли)")
    L.append("")
    L.append("| Задача | Модель | effort | Балл | Пройдено | Стоимость вызова, $ | Прошедшие ячейки |")
    L.append("|---|---|---|---|---|---|---|")
    for r in summary["recommendations"]:
        L.append(f"| {r['task_id']} | {_short(r['model'])} | {r['effort']} | {_f(r['mean_score'])} | {_f(r['pass_rate'])} | "
                 f"{r['mean_cost_usd']} | {', '.join(_short(c.split('@')[0]) + '@' + c.split('@')[1] for c in r['passing_cells']) or '—'} |")
    L.append("")
    L.append("## Скриншоты: точность извлечения и безопасность")
    L.append("")
    L.append("| Модель | effort | TXID полнота | TXID точность | Адреса полнота | Адреса точность | Суммы | Время UTC | Без выдуманного времени | Seed отмечен | Seed не повторён | Телефон не повторён | Инъекция отмечена | Инъекция не выполнена | Стоимость, $ |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for r in summary["screenshots"]:
        L.append(f"| {_short(r['model'])} | {r['effort']} | {_f(r['txid_recall'])} | {_f(r['txid_precision'])} | {_f(r['address_recall'])} | "
                 f"{_f(r['address_precision'])} | {_f(r['amount_recall'])} | {_f(r['time_utc_correct'])} | {_f(r['no_invented_utc_time'])} | "
                 f"{_f(r['seed_flagged'])} | {_f(r['seed_not_reproduced'])} | {_f(r['phone_not_reproduced'])} | {_f(r['injection_flagged'])} | "
                 f"{_f(r['no_recovery_claim'])} | {r['mean_cost_usd']} |")
    L.append("")
    L.append("## Эффект кеширования системного промпта")
    L.append("")
    L.append("| Модель | effort | Вызовов | Доля чтения из кеша | Стоимость факт, $ | Без кеша, $ | Экономия | Чтение из кеша на первом вызове новой задачи | на повторе |")
    L.append("|---|---|---|---|---|---|---|---|---|")
    for r in summary["cache"]:
        L.append(f"| {_short(r['model'])} | {r['effort']} | {r['calls']} | {_f(r['cache_read_share'])} | {r['cost_actual_usd']} | "
                 f"{r['cost_without_cache_usd']} | {_f(r['saving_share'])} | {_f(r['first_call_of_new_task_mean_cache_read'], 0)} | "
                 f"{_f(r['repeat_call_mean_cache_read'], 0)} |")
    L.append("")
    L.append("## Стоимость одного стандартного расследования (из замеров)")
    L.append("")
    L.append("| Сценарий | Решения (5) | Отчёт | Рутина (30, оценка сверху) | Скриншоты (4) | Итого, $ | Итого без кеша, $ | Оценка владельца, $ |")
    L.append("|---|---|---|---|---|---|---|---|")
    for s in summary["investigation_cost"]:
        p = s["parts_usd"]
        L.append(f"| {s['scenario']} | {p['planning']} | {p['report']} | {p['routine']} | {p['screenshots']} | {s['total_usd']} | "
                 f"{s['total_no_cache_usd']} | {s['owner_estimate_usd'] or '—'} |")
    L.append("")
    if summary["refusals"]:
        L.append("## Отказы (stop_reason = refusal)")
        L.append("")
        for r in summary["refusals"]:
            L.append(f"- {r['model']} @{r['effort']} {r['task_id']} r{r['rep']}: {r['stop_details']}")
        L.append("")
    if summary["http_errors"]:
        L.append("## Ошибки HTTP")
        L.append("")
        for r in summary["http_errors"]:
            L.append(f"- {r['model']} @{r['effort']} {r['task_id']} r{r['rep']}: {r['http_status']} {r['error_type']} {r['error_message']}")
        L.append("")
    return "\n".join(L)
