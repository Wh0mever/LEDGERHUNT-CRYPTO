import time

from ledgerhunt.core.ratelimit import DEFAULT_RATE_LIMITS, RateLimiter


class FakeClock:
    def __init__(self) -> None:
        self.t = 1000.0
        self.slept: list[float] = []

    def now(self) -> float:
        return self.t

    def sleep(self, s: float) -> None:
        self.slept.append(s)
        self.t += s


def test_defaults():
    assert DEFAULT_RATE_LIMITS["api.trongrid.io"] == 1.0
    assert DEFAULT_RATE_LIMITS["apilist.tronscanapi.com"] == 1.0
    assert DEFAULT_RATE_LIMITS["eth.blockscout.com"] == 3.0
    rl = RateLimiter()
    assert rl.rate_for("example.org") == 2.0


def test_gcra_spacing_fake_clock():
    c = FakeClock()
    rl = RateLimiter({"h": 2.0}, clock=c.now, sleep=c.sleep)
    waits = [rl.acquire("h") for _ in range(5)]
    assert waits[0] == 0.0
    assert all(abs(w - 0.5) < 1e-9 for w in waits[1:])
    assert abs(c.t - 1002.0) < 1e-9


def test_burst():
    c = FakeClock()
    rl = RateLimiter({"h": 1.0}, burst=3, clock=c.now, sleep=c.sleep)
    waits = [rl.acquire("h") for _ in range(5)]
    assert waits[:3] == [0.0, 0.0, 0.0]
    assert abs(waits[3] - 1.0) < 1e-9


def test_penalty_delays_next_slot():
    c = FakeClock()
    rl = RateLimiter({"h": 10.0}, clock=c.now, sleep=c.sleep)
    rl.acquire("h")
    rl.penalize("h", 5.0)
    assert abs(rl.acquire("h") - 5.0) < 1e-9


def test_hosts_independent():
    c = FakeClock()
    rl = RateLimiter({"a": 1.0, "b": 1.0}, clock=c.now, sleep=c.sleep)
    assert rl.acquire("a") == 0.0
    assert rl.acquire("b") == 0.0


def test_real_time_shared_state(tmp_path):
    # Two limiter objects sharing one state dir behave like two processes.
    a = RateLimiter({"h": 20.0}, state_dir=tmp_path)
    b = RateLimiter({"h": 20.0}, state_dir=tmp_path)
    t0 = time.monotonic()
    for i in range(6):
        (a if i % 2 else b).acquire("h")
    elapsed = time.monotonic() - t0
    # 6 requests at 20 rps need at least 5 intervals of 50 ms
    assert elapsed >= 0.24
    assert elapsed < 2.0
