"""Persistent cost ledger with a hard spending cap for the paid Claude benchmark.

Rules
- Before every paid call the caller reserves the call's maximum possible cost (prompt tokens counted
  with the free count_tokens endpoint plus a margin, and the whole ``max_tokens`` at the output price).
- A reservation is refused (BudgetExceeded) when spent + open reservations + this reservation would
  exceed the cap, so the cap can never be crossed by the calls the ledger allows.
- After the call the reservation is settled with the exact cost computed from ``usage`` (or released
  when the API rejected the request before processing, e.g. HTTP 400, which is not billed).
- The ledger file is append-only JSONL and shared by all runs of the benchmark, so the cap applies to
  the whole benchmark, not to one run. Reservations left open by a crashed run count as spent at
  their reserved amount (conservative).

Amounts are Decimal and written as strings. No secrets are written.
"""

from __future__ import annotations

import json
import threading
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any

from ..core.filelock import FileLock


class BudgetExceeded(RuntimeError):
    """The next call could exceed the hard cap; nothing was sent."""


@dataclass
class Reservation:
    call_id: str
    model: str
    reserved_usd: Decimal
    run_id: str
    meta: dict[str, Any] = field(default_factory=dict)
    closed: bool = False


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


class CostLedger:
    def __init__(self, path: Path | str, cap_usd: Decimal | str, *, run_id: str) -> None:
        self.path = Path(path)
        self.cap = Decimal(str(cap_usd))
        self.run_id = run_id
        self._lock = threading.Lock()
        self._file_lock = FileLock(self.path.with_suffix(self.path.suffix + ".lock"))
        self.path.parent.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------ state from file
    def _rows(self) -> list[dict[str, Any]]:
        if not self.path.is_file():
            return []
        rows = []
        with open(self.path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    rows.append(json.loads(line))
        return rows

    @staticmethod
    def _state(rows: list[dict[str, Any]]) -> dict[str, Any]:
        reserved: dict[str, Decimal] = {}
        settled = Decimal(0)
        settled_calls = 0
        released_calls = 0
        for r in rows:
            cid = r["call_id"]
            if r["event"] == "reserve":
                reserved[cid] = Decimal(r["reserved_usd"])
            elif r["event"] == "settle":
                settled += Decimal(r["actual_usd"])
                settled_calls += 1
                reserved.pop(cid, None)
            elif r["event"] == "release":
                released_calls += 1
                reserved.pop(cid, None)
        open_total = sum(reserved.values(), Decimal(0))
        return {
            "settled_usd": settled,
            "open_reserved_usd": open_total,
            "open_reservations": len(reserved),
            "settled_calls": settled_calls,
            "released_calls": released_calls,
        }

    def _append(self, row: dict[str, Any]) -> None:
        with open(self.path, "a", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(row, ensure_ascii=False, sort_keys=True, default=str) + "\n")

    # ------------------------------------------------------------ API
    def committed_usd(self) -> Decimal:
        """Settled spend plus open reservations (from all runs)."""
        with self._lock, self._file_lock:
            st = self._state(self._rows())
        return st["settled_usd"] + st["open_reserved_usd"]

    def remaining_usd(self) -> Decimal:
        return self.cap - self.committed_usd()

    def reserve(self, call_id: str, model: str, max_cost_usd: Decimal, **meta: Any) -> Reservation:
        max_cost_usd = Decimal(str(max_cost_usd))
        if max_cost_usd < 0:
            raise ValueError("negative reservation")
        with self._lock, self._file_lock:
            st = self._state(self._rows())
            committed = st["settled_usd"] + st["open_reserved_usd"]
            if committed + max_cost_usd > self.cap:
                raise BudgetExceeded(
                    f"call {call_id} ({model}) could cost up to ${max_cost_usd}; committed ${committed} "
                    f"of the ${self.cap} cap"
                )
            self._append({
                "event": "reserve", "ts_utc": _now(), "run_id": self.run_id, "call_id": call_id,
                "model": model, "reserved_usd": str(max_cost_usd), "committed_before_usd": str(committed),
                "cap_usd": str(self.cap), "meta": meta,
            })
        return Reservation(call_id, model, max_cost_usd, self.run_id, dict(meta))

    def settle(self, res: Reservation, actual_usd: Decimal, *, usage: dict[str, Any] | None = None,
               status: str = "ok", note: str = "") -> None:
        if res.closed:
            return
        actual_usd = Decimal(str(actual_usd))
        with self._lock, self._file_lock:
            self._append({
                "event": "settle", "ts_utc": _now(), "run_id": res.run_id, "call_id": res.call_id,
                "model": res.model, "reserved_usd": str(res.reserved_usd), "actual_usd": str(actual_usd),
                "exceeded_reservation": actual_usd > res.reserved_usd, "status": status, "usage": usage,
                "note": note,
            })
        res.closed = True

    def release(self, res: Reservation, *, status: str, note: str = "") -> None:
        """Close a reservation without spend (request rejected before processing, not billed)."""
        if res.closed:
            return
        with self._lock, self._file_lock:
            self._append({
                "event": "release", "ts_utc": _now(), "run_id": res.run_id, "call_id": res.call_id,
                "model": res.model, "reserved_usd": str(res.reserved_usd), "status": status, "note": note,
            })
        res.closed = True

    def close_stale(self, run_id: str, *, note: str) -> list[dict[str, str]]:
        """Settle every open reservation of ``run_id`` at its reserved amount (usage unknown: upper bound).

        Used when a run crashed after sending requests whose usage was never received. Only call it when no
        process of that run is still running.
        """
        closed = []
        with self._lock, self._file_lock:
            rows = self._rows()
            open_: dict[str, dict[str, Any]] = {}
            for r in rows:
                if r.get("run_id") != run_id:
                    continue
                if r["event"] == "reserve":
                    open_[r["call_id"]] = r
                else:
                    open_.pop(r["call_id"], None)
            for cid, r in open_.items():
                self._append({
                    "event": "settle", "ts_utc": _now(), "run_id": run_id, "call_id": cid, "model": r["model"],
                    "reserved_usd": r["reserved_usd"], "actual_usd": r["reserved_usd"], "exceeded_reservation": False,
                    "status": "unknown_usage_upper_bound", "usage": None, "note": note,
                })
                closed.append({"call_id": cid, "model": r["model"], "upper_bound_usd": r["reserved_usd"]})
        return closed

    def upper_bound_calls(self, run_id: str) -> list[dict[str, str]]:
        """Settled calls of ``run_id`` whose cost is an upper bound (usage unknown)."""
        with self._lock, self._file_lock:
            rows = self._rows()
        return [{"call_id": r["call_id"], "model": r["model"], "upper_bound_usd": r["actual_usd"], "note": r.get("note", "")}
                for r in rows if r.get("run_id") == run_id and r["event"] == "settle"
                and r.get("status") == "unknown_usage_upper_bound"]

    def summary(self, run_id: str | None = None) -> dict[str, Any]:
        with self._lock, self._file_lock:
            rows = self._rows()
        st = self._state(rows)
        out: dict[str, Any] = {
            "ledger": self.path.name,
            "cap_usd": str(self.cap),
            "settled_usd_all_runs": str(st["settled_usd"]),
            "open_reserved_usd_all_runs": str(st["open_reserved_usd"]),
            "open_reservations_all_runs": st["open_reservations"],
            "committed_usd_all_runs": str(st["settled_usd"] + st["open_reserved_usd"]),
            "remaining_usd": str(self.cap - st["settled_usd"] - st["open_reserved_usd"]),
            "settled_calls_all_runs": st["settled_calls"],
            "released_calls_all_runs": st["released_calls"],
        }
        if run_id is not None:
            run_rows = [r for r in rows if r.get("run_id") == run_id]
            rst = self._state(run_rows)
            per_model: dict[str, Decimal] = {}
            for r in run_rows:
                if r["event"] == "settle":
                    per_model[r["model"]] = per_model.get(r["model"], Decimal(0)) + Decimal(r["actual_usd"])
            upper = sum((Decimal(r["actual_usd"]) for r in run_rows if r["event"] == "settle"
                         and r.get("status") == "unknown_usage_upper_bound"), Decimal(0))
            out["run"] = {
                "run_id": run_id,
                "settled_usd": str(rst["settled_usd"]),
                "exact_usd_from_usage": str(rst["settled_usd"] - upper),
                "upper_bound_usd_unknown_usage": str(upper),
                "settled_calls": rst["settled_calls"],
                "released_calls": rst["released_calls"],
                "open_reservations": rst["open_reservations"],
                "settled_usd_by_model": {k: str(v) for k, v in sorted(per_model.items())},
            }
        return out
