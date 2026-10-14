"""Secret redaction used by logging, the HTTP recorder and the results writer.

Two layers:
1. Exact values registered with ``register_secret`` (config.py registers every
   secret it loads). URL-shaped secrets also register their long path segments,
   query values and passwords, so a key embedded in a provider URL is caught
   even when the URL is rebuilt.
2. Generic patterns: ``sk-ant-*`` strings, API-key style headers
   (TRON-PRO-API-KEY, X-API-Key, Authorization, ...), secret-looking query
   parameters (api_key, apikey, key, token, access_token, ...) and JSON fields
   with secret-looking names. Query values that are public chain addresses
   (0x + 40 hex, TRON base58) are left intact because they are filters, not keys.
"""

from __future__ import annotations

import re
import threading
from typing import Any
from urllib.parse import parse_qsl, quote, urlsplit

REDACTED = "***"

_lock = threading.Lock()
_secrets: set[str] = set()
_sorted_cache: list[str] | None = None

_MIN_LEN = 4
_URL_PART_MIN_LEN = 12

_PUBLIC_ADDRESS = re.compile(r"^(?:0x[0-9a-fA-F]{40}|T[1-9A-HJ-NP-Za-km-z]{33})$")

_SK_ANT = re.compile(r"sk-ant-[A-Za-z0-9_\-]{6,}")

_HEADER_NAMES = (
    r"tron-pro-api-key|x-api-key|x-apikey|api-key|x-auth-token|authorization|access_token|auth_token|jwt|"
    r"[A-Za-z0-9_]*(?:api_key|apikey|_secret|_jwt|password)"
)
# whole name (not a suffix of a longer word), optional closing quote, separator,
# optional opening quote, optional scheme word, value
_HEADER_LIKE = re.compile(
    r"(?i)(?<![A-Za-z0-9_-])((?:" + _HEADER_NAMES + r")[\"']?\s*[:=]\s*[\"']?)"
    r"(?:(?:bearer|basic|token)\s+)?([^\s\"',;}&)\]]+)"
)
_NOT_SECRET_VALUES = {"true", "false", "null", "none", "***"}

_QUERY_NAMES = r"api_key|api-key|apikey|key|token|access_token|auth_token|auth|secret|jwt|x-api-key"
_QUERY_PARAM = re.compile(r"(?i)([?&](?:" + _QUERY_NAMES + r")=)([^&#\s\"'<>]+)")


def register_secret(value: str | None, *, min_len: int = _MIN_LEN) -> None:
    """Register a secret value so ``redact`` replaces it everywhere. Values shorter than min_len are ignored."""
    if not value:
        return
    candidates: set[str] = set()
    v = value.strip()
    if len(v) < max(min_len, _MIN_LEN):
        return
    base = v.rstrip("/") or v  # without trailing slash, so 'URL/' + 'wallet/x' -> '***/wallet/x'
    candidates.update({base, quote(base, safe=""), quote(base, safe="/:")})
    try:
        parts = urlsplit(v)
    except ValueError:
        parts = None
    if parts is not None and parts.scheme in ("http", "https", "ws", "wss") and parts.netloc:
        if parts.password and len(parts.password) >= _MIN_LEN:
            candidates.add(parts.password)
        for seg in parts.path.split("/"):
            if len(seg) >= _URL_PART_MIN_LEN:
                candidates.add(seg)
        for _, qv in parse_qsl(parts.query, keep_blank_values=False):
            if len(qv) >= _URL_PART_MIN_LEN:
                candidates.add(qv)
    candidates = {c for c in candidates if len(c) >= _MIN_LEN}
    if not candidates:
        return
    global _sorted_cache
    with _lock:
        _secrets.update(candidates)
        _sorted_cache = None


def clear_registered_secrets() -> None:
    """Forget all registered values (tests only)."""
    global _sorted_cache
    with _lock:
        _secrets.clear()
        _sorted_cache = None


def registered_secret_count() -> int:
    with _lock:
        return len(_secrets)


def _sorted_secrets() -> list[str]:
    global _sorted_cache
    with _lock:
        if _sorted_cache is None:
            _sorted_cache = sorted(_secrets, key=len, reverse=True)
        return _sorted_cache


def _header_sub(m: re.Match[str]) -> str:
    if m.group(2).lower() in _NOT_SECRET_VALUES:
        return m.group(0)
    return m.group(1) + REDACTED


def _query_sub(m: re.Match[str]) -> str:
    if _PUBLIC_ADDRESS.match(m.group(2)):
        return m.group(0)
    return m.group(1) + REDACTED


def redact(text: Any) -> str:
    """Return ``text`` (coerced to str) with registered secrets and key-like patterns replaced by ***."""
    if text is None:
        return ""
    s = text if isinstance(text, str) else str(text)
    if not s:
        return s
    for secret in _sorted_secrets():
        if secret in s:
            s = s.replace(secret, REDACTED)
    s = _SK_ANT.sub(REDACTED, s)
    s = _HEADER_LIKE.sub(_header_sub, s)
    s = _QUERY_PARAM.sub(_query_sub, s)
    return s


def redact_obj(obj: Any) -> Any:
    """Recursively redact every string (keys and values) inside dicts, lists and tuples."""
    if isinstance(obj, str):
        return redact(obj)
    if isinstance(obj, dict):
        return {redact(k) if isinstance(k, str) else k: redact_obj(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [redact_obj(v) for v in obj]
    return obj


def contains_registered_secret(data: bytes | str) -> bool:
    """True when any registered secret value occurs in ``data`` (used before storing raw bodies)."""
    secrets = _sorted_secrets()
    if not secrets:
        return False
    if isinstance(data, bytes):
        return any(s.encode("utf-8") in data for s in secrets)
    return any(s in data for s in secrets)


def redact_bytes(data: bytes) -> bytes:
    """Replace registered secret values inside raw bytes (patterns are not applied to bodies)."""
    for s in _sorted_secrets():
        b = s.encode("utf-8")
        if b in data:
            data = data.replace(b, REDACTED.encode())
    return data
