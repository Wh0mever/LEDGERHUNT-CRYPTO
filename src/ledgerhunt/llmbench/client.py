"""One benchmark call to the Messages API: streamed, timed, with usage, stop_reason and refusal handling.

The Anthropic SDK does not go through ledgerhunt.core.http.RecordingClient, so this module records what it
needs itself (raw response metadata, usage, timings) and the runner stores it under the run directory.
No API key, header or request id that could identify the key is stored.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

import anthropic


@dataclass
class CallResult:
    ok: bool
    status: str  # ok | refusal | max_tokens | http_error | connection_error | budget | error
    http_status: int | None = None
    error_type: str | None = None
    error_message: str | None = None
    stop_reason: str | None = None
    stop_details: dict[str, Any] | None = None
    model_served: str | None = None
    message_id: str | None = None
    usage: dict[str, Any] = field(default_factory=dict)
    text: str = ""
    content_summary: list[dict[str, Any]] = field(default_factory=list)
    latency_ms: float | None = None
    ttfb_ms: float | None = None  # first stream event
    ttft_text_ms: float | None = None  # first visible text delta
    raw: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {k: v for k, v in self.__dict__.items()}


def usage_dict(usage: Any) -> dict[str, Any]:
    if usage is None:
        return {}
    d = usage.to_dict() if hasattr(usage, "to_dict") else dict(usage)
    return {k: v for k, v in d.items() if v is not None}


def summarize_content(content: list[Any]) -> tuple[str, list[dict[str, Any]]]:
    texts, summary = [], []
    for block in content or []:
        btype = getattr(block, "type", None)
        if btype == "text":
            texts.append(block.text)
            summary.append({"type": "text", "chars": len(block.text)})
        elif btype == "thinking":
            summary.append({"type": "thinking", "chars": len(getattr(block, "thinking", "") or "")})
        elif btype == "redacted_thinking":
            summary.append({"type": "redacted_thinking"})
        elif btype == "tool_use":
            summary.append({"type": "tool_use", "name": getattr(block, "name", None), "input": getattr(block, "input", None)})
        else:
            summary.append({"type": str(btype)})
    return "".join(texts), summary


def _err_message(exc: Exception) -> str:
    msg = getattr(exc, "message", None) or str(exc)
    body = getattr(exc, "body", None)
    if isinstance(body, dict):
        err = body.get("error") if isinstance(body.get("error"), dict) else None
        if err and err.get("message"):
            msg = err["message"]
    return str(msg)[:600]


def stream_call(client: anthropic.Anthropic, params: dict[str, Any], *, timeout_s: float = 600.0) -> CallResult:
    """Send one streamed request and return a CallResult. Never raises for API errors."""
    t0 = time.perf_counter()
    first_event = first_text = None
    try:
        with client.messages.stream(**params, timeout=timeout_s) as stream:
            for event in stream:
                now = time.perf_counter()
                if first_event is None:
                    first_event = now
                if (first_text is None and getattr(event, "type", "") == "content_block_delta"
                        and getattr(getattr(event, "delta", None), "type", "") == "text_delta"):
                    first_text = now
            msg = stream.get_final_message()
    except anthropic.APIStatusError as exc:
        return CallResult(ok=False, status="http_error", http_status=exc.status_code, error_type=type(exc).__name__,
                          error_message=_err_message(exc), latency_ms=(time.perf_counter() - t0) * 1000,
                          ttfb_ms=(first_event - t0) * 1000 if first_event else None)
    except anthropic.APIConnectionError as exc:
        return CallResult(ok=False, status="connection_error", error_type=type(exc).__name__,
                          error_message=_err_message(exc), latency_ms=(time.perf_counter() - t0) * 1000,
                          ttfb_ms=(first_event - t0) * 1000 if first_event else None)
    except Exception as exc:  # noqa: BLE001 - e.g. httpx2.ReadError when the connection is reset mid-stream
        # The request was accepted and may have generated (billed) tokens before the stream broke; usage is unknown.
        return CallResult(ok=False, status="transport_error", error_type=type(exc).__name__,
                          error_message=str(exc)[:600], latency_ms=(time.perf_counter() - t0) * 1000,
                          ttfb_ms=(first_event - t0) * 1000 if first_event else None)
    t1 = time.perf_counter()
    text, summary = summarize_content(msg.content)
    stop = msg.stop_reason
    details = msg.stop_details.to_dict() if getattr(msg, "stop_details", None) is not None else None
    status = "ok" if stop in ("end_turn", "stop_sequence", "tool_use") else (stop or "unknown")
    return CallResult(
        ok=status == "ok", status=status, http_status=200, stop_reason=stop, stop_details=details,
        model_served=msg.model, message_id=msg.id, usage=usage_dict(msg.usage), text=text,
        content_summary=summary, latency_ms=(t1 - t0) * 1000,
        ttfb_ms=(first_event - t0) * 1000 if first_event else None,
        ttft_text_ms=(first_text - t0) * 1000 if first_text else None,
    )


def plain_call(client: Any, params: dict[str, Any], *, beta: bool = False) -> CallResult:
    """Non-streamed request (used by the small API checks)."""
    t0 = time.perf_counter()
    try:
        api = client.beta.messages if beta else client.messages
        msg = api.create(**params)
    except anthropic.APIStatusError as exc:
        return CallResult(ok=False, status="http_error", http_status=exc.status_code, error_type=type(exc).__name__,
                          error_message=_err_message(exc), latency_ms=(time.perf_counter() - t0) * 1000)
    except anthropic.APIConnectionError as exc:
        return CallResult(ok=False, status="connection_error", error_type=type(exc).__name__,
                          error_message=_err_message(exc), latency_ms=(time.perf_counter() - t0) * 1000)
    text, summary = summarize_content(msg.content)
    stop = msg.stop_reason
    details = msg.stop_details.to_dict() if getattr(msg, "stop_details", None) is not None else None
    status = "ok" if stop in ("end_turn", "stop_sequence", "tool_use") else (stop or "unknown")
    return CallResult(ok=status == "ok", status=status, http_status=200, stop_reason=stop, stop_details=details,
                      model_served=msg.model, message_id=msg.id, usage=usage_dict(msg.usage), text=text,
                      content_summary=summary, latency_ms=(time.perf_counter() - t0) * 1000)


def count_tokens(client: anthropic.Anthropic, params: dict[str, Any]) -> int:
    """Free token count of a request (estimate). Raises the SDK error on failure."""
    keys = ("model", "messages", "system", "tools", "tool_choice", "thinking", "output_config")
    return client.messages.count_tokens(**{k: params[k] for k in keys if k in params}).input_tokens
