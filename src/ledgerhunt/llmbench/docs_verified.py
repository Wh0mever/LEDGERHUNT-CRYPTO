"""What was checked in the official Anthropic documentation before the benchmark (2026-10-14).

Each entry: the owner's statement (decisions 1.2 / 1.4), what the documentation says, the URL, and whether
they agree. The live API checks (api_checks.py) test the same statements against the API itself.
"""

from __future__ import annotations

VERIFIED_UTC = "2026-10-14"

DOC_CHECKS: list[dict[str, str]] = [
    {
        "topic": "model ids and prices",
        "owner": "claude-haiku-5-5 $0.10/$0.50, claude-sonnet-5-5 $2/$10, claude-opus-5-5 $4/$20 per 1M input/output",
        "docs": "Opus 5.5 $4/$20 (5m cache write $5, 1h $8, cache hit $0.20); Sonnet 5.5 $2/$10 (5m $2.50, 1h $4, cache hit $0.10); "
                "Haiku 5.5 $0.10/$0.50 for prompts up to 100,000 tokens (5m $0.125, 1h $0.20, hit $0.01) and $0.50/$2.50 above",
        "url": "https://platform.claude.com/docs/en/about-claude/pricing",
        "agrees": "yes; addition: Haiku 5.5 has a second price card above 100k prompt tokens",
    },
    {
        "topic": "Opus 5.5 thinking cannot be disabled; depth via output_config.effort, default medium",
        "owner": "on claude-opus-5-5 thinking cannot be disabled; control depth with output_config.effort (default medium)",
        "docs": "Opus 5.5: thinking 'disabled' and 'enabled'+budget_tokens return 400 at every effort level; default effort medium; "
                "Sonnet 5.5 default effort high, Haiku 5.5 default medium",
        "url": "https://platform.claude.com/docs/en/build-with-claude/effort ; https://platform.claude.com/docs/en/build-with-claude/thinking",
        "agrees": "yes",
    },
    {
        "topic": "forced tool_choice",
        "owner": "tool_choice any / named tool returns 400 on Opus 5.5 and Sonnet 5.5; use auto + strict tools or structured outputs",
        "docs": "pricing page lists no 'any, tool' tool-use system prompt for Opus 5.5 and Sonnet 5.5 (Haiku 5.5: 406 tokens), "
                "consistent with forced tool_choice being rejected there and accepted on Haiku 5.5; structured outputs "
                "(output_config.format) supported on all three",
        "url": "https://platform.claude.com/docs/en/about-claude/pricing ; https://platform.claude.com/docs/en/build-with-claude/structured-outputs",
        "agrees": "yes (verified live in api_checks)",
    },
    {
        "topic": "refusals",
        "owner": "always check stop_reason; on 'refusal' the investigation must not crash: enable server fallback or log a clear error",
        "docs": "refusal is HTTP 200 with stop_reason 'refusal' and stop_details.category (cyber, bio, frontier_llm, reasoning_extraction, "
                "general_harms); server-side fallback fallbacks='default' with beta server-side-fallback-2026-07-01 on the Claude API "
                "(not Batches); Claude Haiku 5.5 has NO server-side fallback; a refusal before any output is billed only for "
                "bio, frontier_llm and reasoning_extraction; asking for reasoning in an output field can trigger reasoning_extraction",
        "url": "https://platform.claude.com/docs/en/build-with-claude/refusals-and-fallback",
        "agrees": "yes; addition: fallback is not available for Haiku 5.5 and on the Batch API",
    },
    {
        "topic": "prompt caching",
        "owner": "cache stable prompt parts and read usage.cache_read_input_tokens",
        "docs": "minimum cacheable prompt 512 tokens on Opus 5.5, Sonnet 5.5 and Haiku 5.5; default TTL 5 minutes; changing "
                "output_config.effort or the thinking configuration invalidates message-level cache (and can invalidate system/tools); "
                "cache hits on Opus 5.5 and Sonnet 5.5 cost 0.05x base input",
        "url": "https://platform.claude.com/docs/en/build-with-claude/prompt-caching ; https://platform.claude.com/docs/en/build-with-claude/thinking",
        "agrees": "yes",
    },
    {
        "topic": "thinking billed as output",
        "owner": "thinking tokens are billed as output",
        "docs": "tokens spent reasoning are billed as output tokens even when the thinking text is not returned (display defaults to "
                "'omitted' on all three models); usage.output_tokens includes them; usage.output_tokens_details.thinking_tokens "
                "reports the thinking part (SDK type OutputTokensDetails)",
        "url": "https://platform.claude.com/docs/en/build-with-claude/thinking",
        "agrees": "yes",
    },
    {
        "topic": "Batch API",
        "owner": "Batch API for 50+ test scenarios (-50%)",
        "docs": "batch is 50% off input and output (Opus 5.5 $2/$10, Sonnet 5.5 $1/$5, Haiku 5.5 $0.05/$0.25); the fallbacks "
                "parameter is not supported on the Message Batches API",
        "url": "https://platform.claude.com/docs/en/about-claude/pricing ; https://platform.claude.com/docs/en/build-with-claude/refusals-and-fallback",
        "agrees": "yes; caveat: no server-side fallback inside batches",
    },
    {
        "topic": "images",
        "owner": "(not stated)",
        "docs": "image cost = ceil(width/28) x ceil(height/28) visual tokens; Claude 4.7 and later (incl. all 5.5 models) are on the "
                "high-resolution tier: long edge up to 2576 px, up to 4784 visual tokens; JPEG, PNG, GIF, WebP",
        "url": "https://platform.claude.com/docs/en/build-with-claude/vision",
        "agrees": "n/a",
    },
    {
        "topic": "API data retention and use (decision 1.4)",
        "owner": "check and record Anthropic's terms for storage and use of API data for commercial customers",
        "docs": "docs: retained data is never used for model training without express permission; conversation content is not retained "
                "by default except for Covered Models (Fable 5/5.1, Mythos 5/5.1: 30-day retention); ZDR available on request via "
                "sales, per organization; flagged content may be retained up to 2 years. Privacy Center (commercial): inputs and "
                "outputs are deleted on the backend within 30 days of receipt or generation, unless a longer-retention service is "
                "used (e.g. Files API), ZDR is agreed, Usage Policy enforcement or law requires otherwise; flagged chats up to 2 "
                "years, trust and safety scores up to 7 years",
        "url": "https://platform.claude.com/docs/en/manage-claude/api-and-data-retention ; "
               "https://privacy.claude.com/en/articles/7996866-how-long-do-you-store-my-organization-s-data",
        "agrees": "n/a (record for the lawyer; the two pages word default retention differently: 'not retained by default' vs "
                  "'deleted within 30 days')",
    },
    {
        "topic": "skill cache vs official page",
        "owner": "(not stated)",
        "docs": "the bundled claude-api skill notes (cached 2026-10-06) give Sonnet 5.5 cache reads as $0.20/MTok; the official pricing "
                "page says $0.10/MTok (0.05x of $2). The official page is used for all cost calculations",
        "url": "https://platform.claude.com/docs/en/about-claude/pricing",
        "agrees": "discrepancy recorded; official page used",
    },
]
