"""Open-loop load generator for the TRON source benchmark (ramp, penalty probe, sustained run).

Requests are dispatched at fixed planned times t0 + i / rate from one thread and executed by a
small thread pool, so the offered rate does not depend on latency. Every request goes through the
shared RecordingClient (redaction, metrics); the caller routes the source to a dedicated limiter
bucket with rate 0 so the dispatcher alone sets the pace. No retries here (the load client uses
``max_attempts=1``): a 429 is observed, recorded and ends the ramp at once.

Each request yields one row (relative times in seconds from the phase start, latency in ms):
    {phase, source, step_rps, seq, kind, t_plan_s, t_send_s, t_done_s, ts_send_utc, latency_ms,
     status, error_class, bytes, retry_after, ratelimit{...}, body_snippet}
"""

from __future__ import annotations

import math
import threading
import time
from concurrent.futures import ThreadPoolExecutor, wait
from datetime import datetime, timezone
from typing import Any, Callable

from ..core.http import HttpResult, RequestFailed
from ..core.redact import redact

# kind, call() -> HttpResult
CallFactory = Callable[[int], tuple[str, Callable[[], HttpResult]]]


def _utc(ts: float) -> str:
    return datetime.fromtimestamp(ts, timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def _one(call_factory: CallFactory, seq: int, t0: float, t_plan: float, base: dict[str, Any]) -> dict[str, Any]:
    kind, call = call_factory(seq)
    t_send = time.perf_counter()
    ts_send = time.time()
    row: dict[str, Any] = dict(base)
    row.update({"seq": seq, "kind": kind, "t_plan_s": round(t_plan - t0, 4), "t_send_s": round(t_send - t0, 4),
                "ts_send_utc": _utc(ts_send)})
    try:
        res = call()
        row.update({
            "status": res.status,
            "latency_ms": round(res.latency_ms, 1),
            "error_class": None if 200 <= res.status < 300 else f"http_{res.status}",
            "bytes": len(res.body or b""),
            "retry_after": (res.headers or {}).get("retry-after"),
            "ratelimit": {k: v for k, v in (res.headers or {}).items() if "ratelimit" in k.lower()},
            "body_snippet": None if 200 <= res.status < 300 else redact(res.text[:300]),
        })
    except RequestFailed as exc:
        row.update({"status": None, "latency_ms": None, "error_class": exc.error_class, "bytes": 0,
                    "retry_after": None, "ratelimit": {}, "body_snippet": redact(str(exc))[:300]})
    except Exception as exc:  # noqa: BLE001 - a bench request must never kill the run
        row.update({"status": None, "latency_ms": None, "error_class": f"exception:{type(exc).__name__}",
                    "bytes": 0, "retry_after": None, "ratelimit": {}, "body_snippet": redact(str(exc))[:300]})
    row["t_done_s"] = round(time.perf_counter() - t0, 4)
    return row


def open_loop(call_factory: CallFactory, *, rate: float, duration_s: float, phase: str, source: str,
              stop_on_429: bool = True, seq0: int = 0, max_workers: int | None = None,
              stop_on_transport_errors: int = 5) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Send ``round(rate * duration_s)`` requests at fixed intervals; stop early on the first 429.

    Returns (rows sorted by seq, info{planned, sent, stopped, stop_reason, t_first_429_s, wall_s}).
    """
    n = max(1, int(round(rate * duration_s)))
    interval = 1.0 / rate
    workers = max_workers or min(64, int(math.ceil(rate * 2.0)) + 4)
    stop = threading.Event()
    state = {"reason": None, "t_429": None, "transport": 0}
    lock = threading.Lock()
    rows: list[dict[str, Any]] = []
    base = {"phase": phase, "source": source, "step_rps": rate}
    t0 = time.perf_counter()

    def task(seq: int, t_plan: float) -> None:
        row = _one(call_factory, seq, t0, t_plan, base)
        with lock:
            rows.append(row)
            if row["status"] == 429 and stop_on_429 and not stop.is_set():
                state["reason"] = "http_429"
                state["t_429"] = row["t_done_s"]
                stop.set()
            if row["status"] is None:
                state["transport"] += 1
                if state["transport"] >= stop_on_transport_errors and not stop.is_set():
                    state["reason"] = "transport_errors"
                    stop.set()

    sent = 0
    futures = []
    with ThreadPoolExecutor(max_workers=workers, thread_name_prefix=f"bench-{source}") as ex:
        for i in range(n):
            t_plan = t0 + 0.05 + i * interval
            now = time.perf_counter()
            if t_plan > now:
                # sleep in short slices so a 429 stops the dispatcher quickly
                while not stop.is_set() and time.perf_counter() < t_plan:
                    time.sleep(min(0.02, max(0.0, t_plan - time.perf_counter())))
            if stop.is_set():
                break
            futures.append(ex.submit(task, seq0 + i, t_plan))
            sent += 1
        wait(futures, timeout=120)
    wall = time.perf_counter() - t0
    rows.sort(key=lambda r: r["seq"])
    return rows, {"planned": n, "sent": sent, "stopped": stop.is_set(), "stop_reason": state["reason"],
                  "t_first_429_s": state["t_429"], "wall_s": round(wall, 3), "workers": workers,
                  "t0_utc": _utc(time.time() - wall)}


def penalty_probe(call_factory: CallFactory, *, offsets_s: list[float], source: str,
                  seq0: int = 0) -> list[dict[str, Any]]:
    """After a 429 (call immediately): one request at each offset (seconds) until the first 2xx."""
    t0 = time.perf_counter()
    rows = []
    for k, off in enumerate(offsets_s):
        target = t0 + off
        while time.perf_counter() < target:
            time.sleep(min(0.05, max(0.0, target - time.perf_counter())))
        row = _one(call_factory, seq0 + k, t0, target, {"phase": "penalty", "source": source, "step_rps": None,
                                                         "offset_s": off})
        rows.append(row)
        if row["status"] is not None and 200 <= row["status"] < 300:
            break
    return rows


# ---------------------------------------------------------------- statistics


def percentile(values: list[float], pct: float) -> float | None:
    vals = sorted(v for v in values if v is not None)
    if not vals:
        return None
    if len(vals) == 1:
        return round(vals[0], 1)
    k = (len(vals) - 1) * pct / 100.0
    lo = int(k)
    hi = min(lo + 1, len(vals) - 1)
    return round(vals[lo] + (vals[hi] - vals[lo]) * (k - lo), 1)


def step_stats(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Counts, error share, offered and achieved rate, latency p50/p95 for one group of rows."""
    if not rows:
        return {"sent": 0}
    sent = len(rows)
    ok = [r for r in rows if r["status"] is not None and 200 <= r["status"] < 300]
    n429 = sum(1 for r in rows if r["status"] == 429)
    transport = sum(1 for r in rows if r["status"] is None)
    other = sent - len(ok) - n429 - transport
    first_send = min(r["t_send_s"] for r in rows)
    last_send = max(r["t_send_s"] for r in rows)
    last_done = max(r["t_done_s"] for r in rows)
    span_send = last_send - first_send
    by_kind: dict[str, list[float]] = {}
    for r in ok:
        by_kind.setdefault(r["kind"], []).append(r["latency_ms"])
    return {
        "sent": sent,
        "ok": len(ok),
        "http_429": n429,
        "other_http_errors": other,
        "transport_errors": transport,
        "error_share": round((sent - len(ok)) / sent, 4),
        "offered_rps": round((sent - 1) / span_send, 3) if sent > 1 and span_send > 0 else None,
        "achieved_ok_rps": round(len(ok) / (last_done - first_send), 3) if last_done > first_send else None,
        "wall_s": round(last_done - first_send, 3),
        "latency_ms_p50": percentile([r["latency_ms"] for r in ok], 50),
        "latency_ms_p95": percentile([r["latency_ms"] for r in ok], 95),
        "latency_ms_max": max((r["latency_ms"] for r in ok), default=None),
        "latency_by_kind": {k: {"n": len(v), "p50": percentile(v, 50), "p95": percentile(v, 95)}
                            for k, v in sorted(by_kind.items())},
        "statuses": _status_counts(rows),
    }


def _status_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    out: dict[str, int] = {}
    for r in rows:
        k = str(r["status"]) if r["status"] is not None else (r.get("error_class") or "none")
        out[k] = out.get(k, 0) + 1
    return dict(sorted(out.items()))


def first_429_context(rows: list[dict[str, Any]]) -> dict[str, Any] | None:
    """The first 429 of a phase: when, after how many requests, how many were sent in the 1 s before it."""
    hits = [r for r in rows if r["status"] == 429]
    if not hits:
        return None
    first = min(hits, key=lambda r: r["t_send_s"])
    t = first["t_send_s"]
    prior = [r for r in rows if r["t_send_s"] < t]
    return {
        "seq": first["seq"],
        "kind": first["kind"],
        "step_rps": first.get("step_rps"),
        "t_send_s": t,
        "ts_send_utc": first.get("ts_send_utc"),
        "requests_before_in_phase": len(prior),
        "sent_in_prev_1s": sum(1 for r in prior if t - r["t_send_s"] <= 1.0),
        "sent_in_prev_3s": sum(1 for r in prior if t - r["t_send_s"] <= 3.0),
        "retry_after": first.get("retry_after"),
        "ratelimit_headers": first.get("ratelimit"),
        "body_snippet": first.get("body_snippet"),
        "http_429_total_in_phase": len(hits),
    }
