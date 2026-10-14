"""Deterministic random stream for the scenario generator.

``random.Random`` is deterministic too, but its helper methods have changed between
Python releases. This counter-mode SHA-256 stream depends only on the seed text, so the
same seed produces byte-identical scenario sets on any platform and Python version.
"""

from __future__ import annotations

import hashlib
from typing import Sequence, TypeVar

T = TypeVar("T")


class DetRng:
    """Counter-mode SHA-256 byte stream with a few sampling helpers."""

    def __init__(self, seed: str) -> None:
        self.seed = seed
        self._key = hashlib.sha256(b"ledgerhunt-detrng/1|" + seed.encode("utf-8")).digest()
        self._counter = 0
        self._buf = b""

    def fork(self, label: str) -> "DetRng":
        """Independent child stream (does not consume this stream)."""
        return DetRng(f"{self.seed}/{label}")

    def bytes(self, n: int) -> bytes:
        while len(self._buf) < n:
            self._buf += hashlib.sha256(self._key + self._counter.to_bytes(8, "big")).digest()
            self._counter += 1
        out, self._buf = self._buf[:n], self._buf[n:]
        return out

    def hex(self, n_bytes: int) -> str:
        return self.bytes(n_bytes).hex()

    def randbelow(self, n: int) -> int:
        if n <= 0:
            raise ValueError("n must be positive")
        k = n.bit_length()
        nbytes = (k + 7) // 8
        while True:
            r = int.from_bytes(self.bytes(nbytes), "big") >> (nbytes * 8 - k)
            if r < n:
                return r

    def randint(self, a: int, b: int) -> int:
        """Uniform integer in [a, b] (inclusive)."""
        if b < a:
            raise ValueError("empty range")
        return a + self.randbelow(b - a + 1)

    def chance(self, num: int, den: int) -> bool:
        """True with probability num/den."""
        return self.randbelow(den) < num

    def choice(self, seq: Sequence[T]) -> T:
        if not seq:
            raise IndexError("choice from empty sequence")
        return seq[self.randbelow(len(seq))]

    def shuffle(self, items: list[T]) -> None:
        for i in range(len(items) - 1, 0, -1):
            j = self.randbelow(i + 1)
            items[i], items[j] = items[j], items[i]

    def sample(self, seq: Sequence[T], k: int) -> list[T]:
        pool = list(seq)
        self.shuffle(pool)
        return pool[:k]

    def amount(self, low: int, high: int) -> int:
        """Raw USDT amount (6 decimals) uniformly in [low, high] raw units."""
        return self.randint(low, high)
