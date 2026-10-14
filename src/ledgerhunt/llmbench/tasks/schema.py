"""Tiny helpers to write structured-output JSON schemas (every property required, no extra properties)."""

from __future__ import annotations

from typing import Any


def obj(**props: dict[str, Any]) -> dict[str, Any]:
    return {"type": "object", "properties": props, "required": list(props), "additionalProperties": False}


def s(desc: str | None = None) -> dict[str, Any]:
    d: dict[str, Any] = {"type": "string"}
    if desc:
        d["description"] = desc
    return d


def b(desc: str | None = None) -> dict[str, Any]:
    d: dict[str, Any] = {"type": "boolean"}
    if desc:
        d["description"] = desc
    return d


def i(desc: str | None = None) -> dict[str, Any]:
    d: dict[str, Any] = {"type": "integer"}
    if desc:
        d["description"] = desc
    return d


def e(*values: str, desc: str | None = None) -> dict[str, Any]:
    d: dict[str, Any] = {"type": "string", "enum": list(values)}
    if desc:
        d["description"] = desc
    return d


def arr(items: dict[str, Any], desc: str | None = None) -> dict[str, Any]:
    d: dict[str, Any] = {"type": "array", "items": items}
    if desc:
        d["description"] = desc
    return d
