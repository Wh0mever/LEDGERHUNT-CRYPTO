"""Per-host rate limiter (GCRA / virtual-scheduling token bucket).

By default the state is shared between processes through small files under
``.cache/ratelimit/`` so that several agents on one IP stay within one budget
per host. ``state_dir=None`` keeps the state in memory (tests, single process).
"""

from __future__ import annotations

import hashlib
import json
import re
import threading
import time
from pathlib import Path
from typing import Callable

from .filelock import FileLock
from .log import get_logger
from .redact import redact

log = get_logger(__name__)

# Requests per second per host. Keyless TronGrid tolerates ~3 rps per IP and
# applies a ~5 s penalty after HTTP 429, so we stay at 1 rps without a key.
DEFAULT_RATE_LIMITS: dict[str, float] = {
    "api.trongrid.io": 1.0,
    "apilist.tronscanapi.com": 1.0,
    "eth.blockscout.com": 3.0,
}
DEFAULT_RPS: float = 2.0
TRONGRID_RPS_WITH_KEY: float = 10.0


def _host_file_stem(host: str) -> str:
    if redact(host) != host:  # never put a secret-looking host into a file name
        return "h-" + hashlib.sha256(host.encode()).hexdigest()[:16]
    return re.sub(r"[^A-Za-z0-9._-]", "_", host)


class RateLimiter:
    """GCRA limiter. ``acquire(host)`` blocks until the next slot and returns the seconds waited."""

    def __init__(
        self,
        rates: dict[str, float] | None = None,
        *,
        default_rps: float = DEFAULT_RPS,
        burst: int = 1,
        state_dir: Path | str | None = None,
        clock: Callable[[], float] = time.time,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self.rates: dict[str, float] = dict(DEFAULT_RATE_LIMITS)
        if rates:
            self.rates.update(rates)
        self.default_rps = default_rps
        self.burst = max(1, int(burst))
        self.state_dir = Path(state_dir) if state_dir is not None else None
        self.clock = clock
        self.sleep = sleep
        self._mem: dict[str, float] = {}
        self._mem_lock = threading.Lock()

    # -- configuration -------------------------------------------------
    def rate_for(self, host: str) -> float:
        return self.rates.get(host.lower(), self.default_rps)

    def set_rate(self, host: str, rps: float) -> None:
        self.rates[host.lower()] = rps

    # -- state ----------------------------------------------------------
    def _paths(self, host: str) -> tuple[Path, Path]:
        assert self.state_dir is not None
        stem = _host_file_stem(host.lower())
        return self.state_dir / f"{stem}.json", self.state_dir / f"{stem}.lock"

    def _update(self, host: str, fn: Callable[[float, float], tuple[float, float]]) -> float:
        """Atomically apply fn(tat, now) -> (new_tat, result) and return result."""
        if self.state_dir is None:
            with self._mem_lock:
                now = self.clock()
                new_tat, result = fn(self._mem.get(host, 0.0), now)
                self._mem[host] = new_tat
                return result
        state, lock = self._paths(host)
        with FileLock(lock):
            now = self.clock()
            tat = 0.0
            try:
                tat = float(json.loads(state.read_text(encoding="utf-8")).get("tat", 0.0))
            except (FileNotFoundError, ValueError, OSError):
                tat = 0.0
            new_tat, result = fn(tat, now)
            tmp = state.with_suffix(".tmp")
            tmp.write_text(json.dumps({"tat": new_tat}), encoding="utf-8")
            tmp.replace(state)
            return result

    # -- API ------------------------------------------------------------
    def reserve(self, host: str) -> float:
        """Reserve the next slot for ``host``; return seconds to wait before sending (no sleep)."""
        rps = self.rate_for(host)
        if not rps or rps <= 0:
            return 0.0
        interval = 1.0 / rps
        tolerance = (self.burst - 1) * interval

        def fn(tat: float, now: float) -> tuple[float, float]:
            tat = max(tat, now)
            wait = max(0.0, tat - now - tolerance)
            return tat + interval, wait

        return self._update(host.lower(), fn)

    def acquire(self, host: str) -> float:
        wait = self.reserve(host)
        if wait > 0:
            self.sleep(wait)
        return wait

    def penalize(self, host: str, seconds: float) -> None:
        """Push the host's next slot at least ``seconds`` into the future (e.g. after HTTP 429)."""
        if seconds <= 0:
            return
        rps = self.rate_for(host)
        tolerance = (self.burst - 1) / rps if rps and rps > 0 else 0.0

        def fn(tat: float, now: float) -> tuple[float, float]:
            return max(tat, now + seconds + tolerance), 0.0

        self._update(host.lower(), fn)
        log.info("rate limiter: host %s penalized for %.1fs", host, seconds)
