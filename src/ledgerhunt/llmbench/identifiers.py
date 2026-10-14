"""Blockchain identifiers in free text and the "no invented identifiers" check.

Kinds
- tron     : TRON base58 address (T + 33 base58 chars); checksum validated separately
- evm      : 0x + 40 hex (Ethereum address)
- hex64    : 64 hex chars with or without 0x (TRON TXID, Ethereum tx hash, LayerZero GUID, ABI word)
- b58hash  : 43-44 base58 chars (NEAR transaction / intent hashes)

An identifier in a model output is *grounded* when it occurs in the input material in any
equivalent form:
- tron    : the exact base58 string, or its 20-byte body as hex (from ``41..``/``0x..``/ABI words)
- evm     : the 40 hex chars anywhere in the input, case-insensitive (also inside longer hex payloads),
            or the TRON base58 form of the same 20 bytes
- hex64   : the 64 hex chars anywhere in the input, case-insensitive
- b58hash : the exact string
Deterministic conversions (hex <-> base58, case changes, adding/removing 0x) are allowed by the task
rules; anything else that is not in the input counts as invented.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable

from ..core.tron import InvalidTronAddress, b58_to_hex, hex_to_b58, is_valid_address

B58 = "1-9A-HJ-NP-Za-km-z"
TRON_RE = re.compile(rf"(?<![{B58}])T[{B58}]{{33}}(?![{B58}])")
EVM_RE = re.compile(r"(?<![0-9a-zA-Z])0x[0-9a-fA-F]{40}(?![0-9a-fA-F])")
HEX64_RE = re.compile(r"(?<![0-9a-zA-Z])(?:0x)?[0-9a-fA-F]{64}(?![0-9a-fA-F])")
B58HASH_RE = re.compile(rf"(?<![{B58}])[{B58}]{{43,44}}(?![{B58}])")
# Near-identifiers: strings shaped like an identifier but with the wrong length (a dropped or inserted
# character). They are reported as kind "malformed" and count as invented unless they occur in the input.
MALFORMED_TRON_RE = re.compile(rf"(?<![{B58}])T[{B58}]{{28,40}}(?![{B58}])")
MALFORMED_HEX_RE = re.compile(r"(?<![0-9a-zA-Z])(?:0x)?[0-9a-fA-F]{56,72}(?![0-9a-fA-F])")
MALFORMED_EVM_RE = re.compile(r"(?<![0-9a-zA-Z])0x[0-9a-fA-F]{36,44}(?![0-9a-fA-F])")


@dataclass(frozen=True)
class Ident:
    kind: str
    value: str  # as written in the text

    @property
    def norm(self) -> str:
        return normalize(self.kind, self.value)


def normalize(kind: str, value: str) -> str:
    if kind == "evm":
        return value[2:].lower()
    if kind == "hex64":
        v = value[2:] if value[:2].lower() == "0x" else value
        return v.lower()
    return value


def extract(text: str) -> list[Ident]:
    """All identifiers in ``text`` (ordered, de-duplicated by kind+normalised value)."""
    if not text:
        return []
    found: list[Ident] = []
    seen: set[tuple[str, str]] = set()

    def add(kind: str, value: str) -> None:
        key = (kind, normalize(kind, value))
        if key not in seen:
            seen.add(key)
            found.append(Ident(kind, value))

    for m in HEX64_RE.finditer(text):
        add("hex64", m.group(0))
    for m in EVM_RE.finditer(text):
        add("evm", m.group(0))
    for m in TRON_RE.finditer(text):
        add("tron", m.group(0))
    for m in B58HASH_RE.finditer(text):
        v = m.group(0)
        if re.fullmatch(r"[0-9a-fA-F]+", v):  # pure hex is not a base58 hash
            continue
        add("b58hash", v)
    for m in MALFORMED_TRON_RE.finditer(text):
        if len(m.group(0)) != 34:
            add("malformed", m.group(0))
    for m in MALFORMED_HEX_RE.finditer(text):
        body = m.group(0)[2:] if m.group(0)[:2].lower() == "0x" else m.group(0)
        if len(body) != 64:
            add("malformed", m.group(0))
    for m in MALFORMED_EVM_RE.finditer(text):
        if len(m.group(0)) != 42:
            add("malformed", m.group(0))
    return found


def tron_hex_body(addr: str) -> str | None:
    """40-hex body (without the 0x41 prefix) of a valid TRON base58 address, else None."""
    try:
        return b58_to_hex(addr)[2:].lower()
    except (InvalidTronAddress, ValueError):
        return None


class InputCorpus:
    """Everything the model was given, indexed for grounding checks."""

    def __init__(self, texts: Iterable[str]) -> None:
        self.text = "\n".join(t for t in texts if t)
        self.lower = self.text.lower()
        self.tron: set[str] = set()
        self.tron_from_hex: set[str] = set()
        for ident in extract(self.text):
            if ident.kind == "tron":
                self.tron.add(ident.value)
        # TRON addresses that appear only in hex form (41.. / 0x.. / ABI words) in the input.
        for m in re.finditer(r"41[0-9a-fA-F]{40}", self.text):
            try:
                self.tron_from_hex.add(hex_to_b58(m.group(0)))
            except (InvalidTronAddress, ValueError):
                pass
        for m in re.finditer(r"(?<![0-9a-fA-F])(?:0x)?(?:000000000000000000000000)?([0-9a-fA-F]{40})(?![0-9a-fA-F])",
                             self.text):
            try:
                self.tron_from_hex.add(hex_to_b58("41" + m.group(1)))
            except (InvalidTronAddress, ValueError):
                pass

    def grounded(self, ident: Ident) -> bool:
        if ident.kind == "tron":
            if ident.value in self.text:
                return True
            if ident.value in self.tron_from_hex:
                return True
            body = tron_hex_body(ident.value)
            return body is not None and body in self.lower
        if ident.kind in ("evm", "hex64"):
            if ident.norm in self.lower:
                return True
            if ident.kind == "evm":
                try:
                    return hex_to_b58("41" + ident.norm) in self.text
                except (InvalidTronAddress, ValueError):
                    return False
            return False
        if ident.kind == "malformed":
            # Only a whole-token occurrence counts: a truncated copy of a longer identifier is not grounded.
            flags = re.IGNORECASE if re.fullmatch(r"(0x)?[0-9a-fA-F]+", ident.value) else 0
            pat = r"(?<![0-9A-Za-z])" + re.escape(ident.value) + r"(?![0-9A-Za-z])"
            return re.search(pat, self.text, flags) is not None
        return ident.value in self.text


def ungrounded(output_text: str, corpus: InputCorpus) -> list[dict[str, str]]:
    """Identifiers in the output that do not occur in the input in any equivalent form."""
    bad = []
    for ident in extract(output_text):
        if not corpus.grounded(ident):
            item = {"kind": ident.kind, "value": ident.value}
            if ident.kind == "tron" and not is_valid_address(ident.value):
                item["checksum"] = "invalid"
            bad.append(item)
    return bad


def same_identifier(a: str | None, b: str | None) -> bool:
    """Exact identifier match with the allowed normalisations (case for hex, optional 0x)."""
    if not a or not b:
        return False
    a, b = a.strip(), b.strip()
    if a == b:
        return True
    ha = a[2:] if a[:2].lower() == "0x" else a
    hb = b[2:] if b[:2].lower() == "0x" else b
    if re.fullmatch(r"[0-9a-fA-F]+", ha) and re.fullmatch(r"[0-9a-fA-F]+", hb):
        return ha.lower() == hb.lower()
    return False


def contains_identifier(values: Iterable[str | None], target: str) -> bool:
    return any(same_identifier(v, target) for v in values)


def identifiers_in(text: str, kinds: tuple[str, ...] = ("tron", "evm", "hex64", "b58hash")) -> list[str]:
    return [i.value for i in extract(text) if i.kind in kinds]
