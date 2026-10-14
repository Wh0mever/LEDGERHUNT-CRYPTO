"""The benchmark grid: model x effort x task x repeat, with prompt caching, the cost ledger and replay.

Order: one worker per (model, effort) group; inside a group tasks run one after another and the repeats
of a task run back to back, so the cached system prompt is reused (the effort level is rendered into the
prompt, so different efforts never share a cache entry). Groups run in parallel threads.

Live mode stores, per call, the request metadata (hashes of the system prompt, schema, input and image),
the response metadata (id, model, stop_reason, stop_details, usage, content block summary), the output
text, timings and the exact cost. Replay mode re-scores the stored outputs of an earlier run without any
API call.
"""

from __future__ import annotations

import json
import statistics
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any, Callable

from .client import CallResult, count_tokens, stream_call
from .ledger import BudgetExceeded, CostLedger
from .pricing import cost_breakdown, max_cost_usd, no_cache_cost_usd
from .prompts import SYSTEM_PROMPT_SHA256, system_blocks
from .tasks import Task, score_output


@dataclass(frozen=True)
class WorkItem:
    model: str
    effort: str
    task: Task
    rep: int

    @property
    def key(self) -> str:
        return f"{self.model}|{self.effort}|{self.task.task_id}|{self.rep}"


def plan(tasks: list[Task], models: list[str], repeats: dict[str, int],
         efforts_override: dict[str, tuple[str, ...]] | None = None) -> dict[tuple[str, str, str], list[WorkItem]]:
    """Group work items by (model, effort, kind); inside a group: task order, repeats back to back.

    The cached prefix includes the output schema (measured in the smoke run: each task writes its own cache
    entry), so splitting groups by task kind does not lose cache reuse and shortens the wall-clock time.
    """
    groups: dict[tuple[str, str, str], list[WorkItem]] = {}
    for model in models:
        for task in tasks:
            efforts = (efforts_override or {}).get(task.kind, task.efforts)
            for effort in efforts:
                for rep in range(1, repeats.get(model, 1) + 1):
                    groups.setdefault((model, effort, task.kind), []).append(WorkItem(model, effort, task, rep))
    order = {"low": 0, "medium": 1, "high": 2, "xhigh": 3, "max": 4}
    kinds = {"report": 0, "decision": 1, "screenshot": 2}
    return dict(sorted(groups.items(), key=lambda kv: (kinds.get(kv[0][2], 9), models.index(kv[0][0]), order.get(kv[0][1], 9))))


def request_params(item: WorkItem) -> dict[str, Any]:
    t = item.task
    return {
        "model": item.model,
        "max_tokens": t.max_tokens,
        "system": system_blocks(cache=True),
        "messages": [{"role": "user", "content": t.user_content()}],
        "output_config": {"effort": item.effort, "format": {"type": "json_schema", "schema": t.schema}},
    }


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


class GridRunner:
    def __init__(self, client: Any, ledger: CostLedger, *, run_id: str, sink: Callable[[dict[str, Any]], None],
                 log: Callable[[str], None] = print, max_workers: int = 6) -> None:
        self.client = client
        self.ledger = ledger
        self.run_id = run_id
        self.sink = sink
        self.log = log
        self.max_workers = max_workers
        self._count_cache: dict[tuple[str, str, str], int] = {}
        self._lock = threading.Lock()
        self.budget_stopped = False

    def _input_estimate(self, item: WorkItem, params: dict[str, Any]) -> int:
        key = (item.model, item.effort, item.task.task_id)
        with self._lock:
            if key in self._count_cache:
                return self._count_cache[key]
        n = count_tokens(self.client, params)
        with self._lock:
            self._count_cache[key] = n
        return n

    def run_item(self, item: WorkItem, order: int) -> dict[str, Any]:
        params = request_params(item)
        row: dict[str, Any] = {
            "run_id": self.run_id, "call_id": f"{self.run_id}:{item.key}", "model": item.model, "effort": item.effort,
            "task_id": item.task.task_id, "kind": item.task.kind, "rep": item.rep, "order_in_group": order,
            "max_tokens": item.task.max_tokens, "system_prompt_sha256": SYSTEM_PROMPT_SHA256,
            "schema_sha256": item.task.schema_sha256(), "input_sha256": item.task.input_sha256(),
            "image_sha256": item.task.image_sha256(), "started_utc": _now(), "from_replay": False,
        }
        try:
            est = self._input_estimate(item, params)
        except Exception as exc:  # noqa: BLE001
            row.update({"status": "count_tokens_error", "error_message": f"{type(exc).__name__}: {getattr(exc, 'message', exc)}"[:400]})
            return row
        reserve = max_cost_usd(item.model, est, item.task.max_tokens)
        row.update({"input_tokens_counted": est, "reserved_usd": str(reserve)})
        try:
            res = self.ledger.reserve(row["call_id"], item.model, reserve, task=item.task.task_id, effort=item.effort)
        except BudgetExceeded as exc:
            self.budget_stopped = True
            row.update({"status": "skipped_budget", "error_message": str(exc)})
            return row
        r: CallResult = stream_call(self.client, params)
        if r.http_status == 200:
            bd = cost_breakdown(item.model, r.usage)
            self.ledger.settle(res, bd["total"], usage=r.usage, status=r.status)
            row["cost_usd"] = str(bd["total"])
            row["cost_breakdown_usd"] = {k: str(v) for k, v in bd.items()}
            row["no_cache_cost_usd"] = str(no_cache_cost_usd(item.model, r.usage))
        elif r.ttfb_ms is not None or r.status == "transport_error":
            # The stream started (or broke mid-way): tokens may have been generated and billed, but usage is
            # unknown. Count the whole reservation as spent (upper bound) so the cap stays safe.
            self.ledger.settle(res, res.reserved_usd, status="unknown_usage_upper_bound",
                               note=f"{r.status} {r.http_status}: {r.error_type}")
            row["cost_usd"] = "0"
            row["cost_upper_bound_usd"] = str(res.reserved_usd)
        else:
            # Rejected before processing (HTTP 4xx/5xx without a stream): not billed. Release the reservation.
            self.ledger.release(res, status=r.status, note=f"http {r.http_status}: {r.error_type}")
            row["cost_usd"] = "0"
        row.update({
            "status": r.status, "http_status": r.http_status, "error_type": r.error_type, "error_message": r.error_message,
            "stop_reason": r.stop_reason, "stop_details": r.stop_details, "model_served": r.model_served,
            "message_id": r.message_id, "usage": r.usage, "content_summary": r.content_summary,
            "latency_ms": round(r.latency_ms, 1) if r.latency_ms is not None else None,
            "ttfb_ms": round(r.ttfb_ms, 1) if r.ttfb_ms is not None else None,
            "ttft_text_ms": round(r.ttft_text_ms, 1) if r.ttft_text_ms is not None else None,
            "output_text": r.text, "finished_utc": _now(),
        })
        row["score"] = score_output(item.task, r.text, r.stop_reason) if r.http_status == 200 else None
        return row

    def run_group(self, items: list[WorkItem]) -> list[dict[str, Any]]:
        rows = []
        for order, item in enumerate(items, 1):
            if self.budget_stopped:
                row = {"run_id": self.run_id, "call_id": f"{self.run_id}:{item.key}", "model": item.model,
                       "effort": item.effort, "task_id": item.task.task_id, "kind": item.task.kind, "rep": item.rep,
                       "status": "skipped_budget"}
            else:
                t0 = time.perf_counter()
                try:
                    row = self.run_item(item, order)
                except Exception as exc:  # noqa: BLE001 - one broken call must not stop the group
                    row = {"run_id": self.run_id, "call_id": f"{self.run_id}:{item.key}", "model": item.model,
                           "effort": item.effort, "task_id": item.task.task_id, "kind": item.task.kind,
                           "rep": item.rep, "status": "runner_error",
                           "error_message": f"{type(exc).__name__}: {exc}"[:500]}
                sc = row.get("score") or {}
                u = row.get("usage") or {}
                self.log(
                    f"  {item.model:<18} {item.effort:<6} {item.task.task_id:<20} r{item.rep} {row.get('status'):<14} "
                    f"score={sc.get('score', '-')} pass={sc.get('passed', '-')} in={u.get('input_tokens', '-')} "
                    f"cw={u.get('cache_creation_input_tokens', '-')} cr={u.get('cache_read_input_tokens', '-')} "
                    f"out={u.get('output_tokens', '-')} ${row.get('cost_usd', '-')} {time.perf_counter() - t0:.1f}s"
                )
            self.sink(row)
            rows.append(row)
        return rows

    def run(self, groups: dict[tuple[str, str, str], list[WorkItem]]) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as pool:
            futures = [pool.submit(self.run_group, items) for items in groups.values()]
            for f in futures:
                out.extend(f.result())
        return out


# ---------------------------------------------------------------- replay


def load_calls(path: Path) -> list[dict[str, Any]]:
    rows = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def dedupe_calls(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """One row per (model, effort, task, repeat): the last HTTP 200 row if any, otherwise the last row.

    A resumed run appends new attempts for calls that failed (transport errors, HTTP errors); the failed
    attempts stay in raw/calls.jsonl and are reported separately.
    """
    best: dict[tuple, dict[str, Any]] = {}
    for r in rows:
        k = (r.get("model"), r.get("effort"), r.get("task_id"), r.get("rep"))
        cur = best.get(k)
        if cur is None or r.get("http_status") == 200 or cur.get("http_status") != 200:
            best[k] = r
    return list(best.values())


def failed_attempts(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    keys = ("model", "effort", "task_id", "rep", "status", "http_status", "error_type", "error_message",
            "cost_upper_bound_usd", "ttfb_ms", "latency_ms")
    return [{k: r.get(k) for k in keys} for r in rows if r.get("http_status") != 200 and r.get("status") != "skipped_budget"]


def replay(calls: list[dict[str, Any]], tasks: list[Task]) -> list[dict[str, Any]]:
    """Re-score stored outputs with the current scorers; no API calls. Stale inputs are marked, not scored."""
    by_id = {t.task_id: t for t in tasks}
    out = []
    for row in calls:
        new = dict(row)
        new["from_replay"] = True
        t = by_id.get(row.get("task_id"))
        if t is None:
            new["replay_status"] = "task_not_selected"
            continue
        if row.get("input_sha256") and row["input_sha256"] != t.input_sha256():
            new["replay_status"] = "stale_input"
            new["score"] = None
        elif row.get("schema_sha256") and row["schema_sha256"] != t.schema_sha256():
            new["replay_status"] = "stale_schema"
            new["score"] = None
        elif row.get("http_status") == 200:
            new["replay_status"] = "rescored"
            new["score"] = score_output(t, row.get("output_text"), row.get("stop_reason"))
        else:
            new["replay_status"] = "no_response"
        out.append(new)
    return out


def median(xs: list[float]) -> float | None:
    return statistics.median(xs) if xs else None


def dec(x: Any) -> Decimal:
    return Decimal(str(x)) if x not in (None, "") else Decimal(0)
