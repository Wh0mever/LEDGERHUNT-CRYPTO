"""Cheap probes of the API behaviour the owner's decisions rely on (verified against the live API).

Requests expected to fail are rejected with HTTP 400 before processing (not billed). Requests expected to
succeed use tiny prompts and small max_tokens. Every call goes through the cost ledger.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any, Callable

from .client import CallResult, count_tokens, plain_call
from .ledger import BudgetExceeded, CostLedger
from .pricing import cost_usd, max_cost_usd

OPUS, SONNET, HAIKU = "claude-opus-5-5", "claude-sonnet-5-5", "claude-haiku-5-5"

TOOL = {
    "name": "record_txid",
    "description": "Record a TRON transaction ID mentioned by the user.",
    "input_schema": {"type": "object", "properties": {"txid": {"type": "string"}}, "required": ["txid"],
                     "additionalProperties": False},
}
TXID = "98f3ffca9d141f2172d28f46905c08e5f32fc6ce8d23f9a37b731fe2a6c1d1bb"
MSG_OK = [{"role": "user", "content": "Reply with the single word OK."}]
MSG_TOOL = [{"role": "user", "content": f"Record this transaction ID with the record_txid tool: {TXID}"}]


def _checks() -> list[dict[str, Any]]:
    return [
        {"id": "opus_thinking_disabled", "model": OPUS, "expect": "400",
         "claim": "Opus 5.5: thinking cannot be disabled (thinking.type=disabled -> 400)",
         "params": {"max_tokens": 64, "messages": MSG_OK, "thinking": {"type": "disabled"}}},
        {"id": "opus_budget_tokens", "model": OPUS, "expect": "400",
         "claim": "Opus 5.5: manual thinking budget (enabled + budget_tokens) -> 400",
         "params": {"max_tokens": 4096, "messages": MSG_OK, "thinking": {"type": "enabled", "budget_tokens": 1024}}},
        {"id": "opus_tool_choice_any", "model": OPUS, "expect": "400",
         "claim": "Opus 5.5: forced tool_choice any -> 400",
         "params": {"max_tokens": 256, "messages": MSG_TOOL, "tools": [TOOL], "tool_choice": {"type": "any"}}},
        {"id": "sonnet_tool_choice_named", "model": SONNET, "expect": "400",
         "claim": "Sonnet 5.5: forced tool_choice {type: tool} -> 400",
         "params": {"max_tokens": 256, "messages": MSG_TOOL, "tools": [TOOL],
                    "tool_choice": {"type": "tool", "name": "record_txid"}}},
        {"id": "sonnet_thinking_disabled", "model": SONNET, "expect": "400",
         "claim": "Sonnet 5.5: thinking.type=disabled -> 400 (between_tools is the lowest setting)",
         "params": {"max_tokens": 64, "messages": MSG_OK, "thinking": {"type": "disabled"}}},
        {"id": "haiku_tool_choice_named", "model": HAIKU, "expect": "200_tool_use",
         "claim": "Haiku 5.5 accepts forced tool_choice (docs: the response then has no thinking block)",
         "params": {"max_tokens": 256, "messages": MSG_TOOL, "tools": [TOOL],
                    "tool_choice": {"type": "tool", "name": "record_txid"}}},
        {"id": "opus_strict_tool_auto", "model": OPUS, "expect": "200_tool_use",
         "claim": "Opus 5.5: tool_choice auto + strict tool works and the tool is called when the prompt asks",
         "params": {"max_tokens": 2048, "messages": MSG_TOOL, "tools": [{**TOOL, "strict": True}],
                    "tool_choice": {"type": "auto"}, "output_config": {"effort": "low"}}},
        {"id": "sonnet_strict_tool_auto", "model": SONNET, "expect": "200_tool_use",
         "claim": "Sonnet 5.5: tool_choice auto + strict tool works",
         "params": {"max_tokens": 2048, "messages": MSG_TOOL, "tools": [{**TOOL, "strict": True}],
                    "tool_choice": {"type": "auto"}, "output_config": {"effort": "low"}}},
        {"id": "opus_fallbacks_default", "model": OPUS, "expect": "200", "beta": True,
         "claim": "Opus 5.5: server-side fallback fallbacks='default' with beta server-side-fallback-2026-07-01 is accepted",
         "params": {"max_tokens": 1024, "messages": MSG_OK, "output_config": {"effort": "low"},
                    "fallbacks": "default", "betas": ["server-side-fallback-2026-07-01"]}},
        {"id": "haiku_fallbacks_list", "model": HAIKU, "expect": "400", "beta": True,
         "claim": "Haiku 5.5 has no server-side fallback (a list of fallback models -> 400)",
         "params": {"max_tokens": 64, "messages": MSG_OK, "fallbacks": [{"model": SONNET}],
                    "betas": ["server-side-fallback-2026-06-01"]}},
    ]


def _expectation_met(expect: str, r: CallResult) -> bool:
    if expect == "400":
        return r.http_status == 400
    if expect == "200":
        return r.http_status == 200
    if expect == "200_tool_use":
        return r.http_status == 200 and any(b.get("type") == "tool_use" for b in r.content_summary)
    return False


def run_checks(client: Any, ledger: CostLedger, *, log: Callable[[str], None] = print) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for chk in _checks():
        params = {"model": chk["model"], **chk["params"]}
        row: dict[str, Any] = {k: chk[k] for k in ("id", "model", "expect", "claim")}
        # count_tokens also validates tool_choice on these models; fall back to a rough bound when it rejects.
        try:
            est = count_tokens(client, {k: v for k, v in params.items() if k not in ("fallbacks", "betas")})
            row["count_tokens"] = est
        except Exception as exc:  # noqa: BLE001
            est = 2000
            row["count_tokens_error"] = f"{type(exc).__name__}: {getattr(exc, 'status_code', '')}"
        reserve = max_cost_usd(chk["model"], est, params["max_tokens"])
        try:
            res = ledger.reserve(f"check:{chk['id']}", chk["model"], reserve, kind="api_check")
        except BudgetExceeded as exc:
            row.update({"result": "skipped", "reason": str(exc)})
            rows.append(row)
            continue
        r = plain_call(client, params, beta=bool(chk.get("beta")))
        if r.http_status == 200:
            cost = cost_usd(chk["model"], r.usage)
            ledger.settle(res, cost, usage=r.usage, status=r.status)
        else:
            cost = Decimal(0)
            ledger.release(res, status=f"http_{r.http_status}", note="rejected before processing; not billed")
        row.update({
            "http_status": r.http_status, "error_type": r.error_type, "error_message": r.error_message,
            "stop_reason": r.stop_reason, "content": r.content_summary, "usage": r.usage,
            "model_served": r.model_served, "cost_usd": str(cost), "latency_ms": round(r.latency_ms or 0, 1),
            "expectation_met": _expectation_met(chk["expect"], r),
        })
        log(f"  check {chk['id']}: HTTP {r.http_status} -> {'as documented' if row['expectation_met'] else 'DIFFERS'}")
        rows.append(row)
    return rows


def models_snapshot(client: Any, models: tuple[str, ...]) -> list[dict[str, Any]]:
    """Models API entries (free): context window, max output, capabilities."""
    out = []
    for m in models:
        try:
            info = client.models.retrieve(m)
            d = info.to_dict() if hasattr(info, "to_dict") else dict(info)
            out.append({"model": m, "ok": True, "info": d})
        except Exception as exc:  # noqa: BLE001
            out.append({"model": m, "ok": False, "error": f"{type(exc).__name__}: {getattr(exc, 'status_code', '')}"})
    return out
