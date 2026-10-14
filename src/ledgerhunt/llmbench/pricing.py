"""Verified Claude API prices and exact cost computation from ``usage``.

Prices are USD per million tokens (MTok), stored as Decimal. They were read from the official
pricing page on 2026-10-14 (see PRICE_SOURCES). Cost is computed exactly with Decimal and never
with floats.

usage fields used (Messages API):
- input_tokens                 : uncached input tokens (after the last cache breakpoint)
- cache_creation_input_tokens  : tokens written to the prompt cache (split by TTL in cache_creation)
- cache_read_input_tokens      : tokens read from the prompt cache
- output_tokens                : billed output tokens, thinking included
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Mapping

PRICES_VERIFIED_UTC = "2026-10-14"

PRICE_SOURCES: tuple[dict[str, str], ...] = (
    {
        "url": "https://platform.claude.com/docs/en/about-claude/pricing",
        "what": "model prices, cache write/read multipliers, batch prices, Haiku 5.5 long-context card",
    },
    {
        "url": "https://platform.claude.com/docs/en/about-claude/models/overview",
        "what": "model IDs, default effort, context window, max output",
    },
)

MTOK = Decimal(1_000_000)


@dataclass(frozen=True)
class ModelPrice:
    """USD per million tokens."""

    model: str
    input: Decimal
    cache_write_5m: Decimal
    cache_write_1h: Decimal
    cache_read: Decimal
    output: Decimal
    batch_input: Decimal
    batch_output: Decimal
    note: str = ""

    def to_dict(self) -> dict[str, str]:
        return {
            "model": self.model,
            "input": str(self.input),
            "cache_write_5m": str(self.cache_write_5m),
            "cache_write_1h": str(self.cache_write_1h),
            "cache_read": str(self.cache_read),
            "output": str(self.output),
            "batch_input": str(self.batch_input),
            "batch_output": str(self.batch_output),
            "note": self.note,
        }


D = Decimal

# Values copied from the pricing page table (2026-10-14).
PRICES: dict[str, ModelPrice] = {
    "claude-opus-5-5": ModelPrice(
        "claude-opus-5-5", D("4"), D("5"), D("8"), D("0.20"), D("20"), D("2"), D("10"),
        note="cache hits 0.05x base input",
    ),
    "claude-sonnet-5-5": ModelPrice(
        "claude-sonnet-5-5", D("2"), D("2.50"), D("4"), D("0.10"), D("10"), D("1"), D("5"),
        note="cache hits 0.05x base input ($0.10/MTok per the pricing page)",
    ),
    "claude-haiku-5-5": ModelPrice(
        "claude-haiku-5-5", D("0.10"), D("0.125"), D("0.20"), D("0.01"), D("0.50"), D("0.05"), D("0.25"),
        note="prompts up to 100,000 tokens",
    ),
}

# Claude Haiku 5.5 is priced by prompt length: a request whose prompt (input + cache reads + cache
# writes) is over 100,000 tokens pays the higher card.
HAIKU_LONG_THRESHOLD = 100_000
HAIKU_LONG = ModelPrice(
    "claude-haiku-5-5", D("0.50"), D("0.625"), D("1"), D("0.05"), D("2.50"), D("0.25"), D("1.25"),
    note="prompts over 100,000 tokens",
)


class UnknownModelPrice(KeyError):
    pass


def _int(v: Any) -> int:
    if v is None:
        return 0
    if isinstance(v, bool):
        raise TypeError("bool is not a token count")
    return int(v)


def prompt_tokens(usage: Mapping[str, Any]) -> int:
    return (
        _int(usage.get("input_tokens"))
        + _int(usage.get("cache_creation_input_tokens"))
        + _int(usage.get("cache_read_input_tokens"))
    )


def price_for(model: str, prompt_len: int = 0) -> ModelPrice:
    if model not in PRICES:
        raise UnknownModelPrice(model)
    if model == "claude-haiku-5-5" and prompt_len > HAIKU_LONG_THRESHOLD:
        return HAIKU_LONG
    return PRICES[model]


def _cache_write_split(usage: Mapping[str, Any]) -> tuple[int, int]:
    """(5-minute, 1-hour) cache-write tokens; all writes count as 5-minute when no split is reported."""
    total = _int(usage.get("cache_creation_input_tokens"))
    split = usage.get("cache_creation") or {}
    w5 = _int(split.get("ephemeral_5m_input_tokens")) if split else 0
    w1 = _int(split.get("ephemeral_1h_input_tokens")) if split else 0
    if w5 + w1 != total:
        # No (or inconsistent) breakdown: bill the remainder at the 5-minute rate.
        w5 = total - w1 if w1 <= total else total
        w1 = total - w5
    return w5, w1


def cost_breakdown(model: str, usage: Mapping[str, Any]) -> dict[str, Decimal]:
    """Exact USD cost per usage component (Decimal)."""
    p = price_for(model, prompt_tokens(usage))
    w5, w1 = _cache_write_split(usage)
    parts = {
        "input": _int(usage.get("input_tokens")) * p.input / MTOK,
        "cache_write_5m": w5 * p.cache_write_5m / MTOK,
        "cache_write_1h": w1 * p.cache_write_1h / MTOK,
        "cache_read": _int(usage.get("cache_read_input_tokens")) * p.cache_read / MTOK,
        "output": _int(usage.get("output_tokens")) * p.output / MTOK,
    }
    parts["total"] = sum(parts.values(), Decimal(0))
    return parts


def cost_usd(model: str, usage: Mapping[str, Any]) -> Decimal:
    return cost_breakdown(model, usage)["total"]


def no_cache_cost_usd(model: str, usage: Mapping[str, Any]) -> Decimal:
    """Counterfactual cost of the same request without prompt caching (all prompt tokens at base input)."""
    p = price_for(model, prompt_tokens(usage))
    return prompt_tokens(usage) * p.input / MTOK + _int(usage.get("output_tokens")) * p.output / MTOK


def max_cost_usd(model: str, input_tokens_estimate: int, max_tokens: int, *, margin: float = 0.10,
                 margin_tokens: int = 200) -> Decimal:
    """Upper bound used for the ledger reservation.

    Every prompt token is priced at the more expensive of base input and the 1-hour cache-write rate
    (so a cache write can never exceed the reservation), the token-count estimate gets a safety margin
    (the count_tokens endpoint returns an estimate), and the full ``max_tokens`` is priced as output.
    """
    est = int(input_tokens_estimate * (1 + margin)) + margin_tokens
    p = price_for(model, est)
    worst_in = max(p.input, p.cache_write_5m, p.cache_write_1h)
    return est * worst_in / MTOK + int(max_tokens) * p.output / MTOK


def price_table() -> list[dict[str, str]]:
    rows = [p.to_dict() for p in PRICES.values()]
    rows.append(HAIKU_LONG.to_dict())
    return rows
