"""Claude model cost and quality benchmark (Stage 2, decision 4.4).

Modules
- pricing     : verified per-model prices (Decimal, USD per million tokens) and cost from ``usage``
- ledger      : persistent cost ledger with a hard cap; reserves the maximum cost of a call before it is sent
- identifiers : extraction of TXIDs / addresses / hashes and the "no invented identifiers" check
- scoring     : amount / time normalisation, claim detectors, a minimal JSON-schema validator
- prompts     : the stable (cached) system prompt
- tasks       : decision points of case-001, screenshot extraction, report generation (inputs, schemas, scorers)
- client      : one streamed Messages API call with timing, usage, stop_reason and refusal handling
- api_checks  : cheap probes of documented API behaviour (400 on forced tool_choice, etc.)
- runner      : the grid (model x effort x task x repeat), ordering for prompt caching, replay
- summarize   : tables, cost per investigation, Markdown summary

Nothing here builds the product tracer. All task inputs are public blockchain data from the
case-001 fixture / recorded raw responses, or synthetic screenshots.
"""

from __future__ import annotations

MODELS: tuple[str, ...] = ("claude-haiku-5-5", "claude-sonnet-5-5", "claude-opus-5-5")
