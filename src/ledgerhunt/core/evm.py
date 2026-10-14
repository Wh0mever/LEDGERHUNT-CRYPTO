"""Ethereum / EVM helpers: keccak, EIP-55, topics, ABI words, ASCII decoding."""

from __future__ import annotations

import re
from typing import Any

from Crypto.Hash import keccak as _keccak

_ADDR_RE = re.compile(r"^(0x)?[0-9a-fA-F]{40}$")


def keccak256(data: bytes | str) -> bytes:
    """Keccak-256 (Ethereum flavour, not NIST SHA3-256)."""
    if isinstance(data, str):
        data = data.encode("utf-8")
    h = _keccak.new(digest_bits=256)
    h.update(data)
    return h.digest()


def strip0x(value: str) -> str:
    return value[2:] if value[:2] in ("0x", "0X") else value


def hex_to_bytes(value: str) -> bytes:
    h = strip0x(value)
    if len(h) % 2:
        h = "0" + h
    return bytes.fromhex(h)


# ---------------------------------------------------------------- addresses


def is_address(value: Any) -> bool:
    return isinstance(value, str) and bool(_ADDR_RE.match(value))


def to_checksum_address(value: str) -> str:
    """EIP-55 checksum form of a 20-byte hex address (accepts any case, with/without 0x)."""
    if not is_address(value):
        raise ValueError(f"not a 20-byte hex address: {value!r}")
    lower = strip0x(value).lower()
    digest = keccak256(lower.encode("ascii")).hex()
    return "0x" + "".join(c.upper() if c.isalpha() and int(digest[i], 16) >= 8 else c for i, c in enumerate(lower))


def is_checksum_address(value: str) -> bool:
    return is_address(value) and value.startswith("0x") and to_checksum_address(value) == value


def normalize_address(value: str) -> str:
    """Lowercase 0x-prefixed form, for comparisons and dictionary keys."""
    if not is_address(value):
        raise ValueError(f"not a 20-byte hex address: {value!r}")
    return "0x" + strip0x(value).lower()


# ---------------------------------------------------------------- topics / selectors


def event_topic(signature: str) -> str:
    """'Transfer(address,address,uint256)' -> 0x-prefixed topic0."""
    return "0x" + keccak256(signature.replace(" ", "")).hex()


def function_selector(signature: str) -> str:
    """'balanceOf(address)' -> '70a08231' (4 bytes, no 0x)."""
    return keccak256(signature.replace(" ", ""))[:4].hex()


TRANSFER_TOPIC = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
APPROVAL_TOPIC = "0x8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925"
USDT_ERC20 = "0xdAC17F958D2ee523a2206206994597C13D831ec7"
USDT_ERC20_DECIMALS = 6


# ---------------------------------------------------------------- ABI words


def split_words(data: str | bytes) -> list[str]:
    """ABI data -> list of 64-hex-char words (no 0x). Trailing partial word is an error."""
    h = data.hex() if isinstance(data, bytes) else strip0x(data)
    if len(h) % 64:
        raise ValueError(f"ABI data length {len(h)} is not a multiple of 64 hex chars")
    return [h[i : i + 64] for i in range(0, len(h), 64)]


def word_to_uint(word: str) -> int:
    return int(strip0x(word) or "0", 16)


def word_to_int(word: str) -> int:
    """Two's-complement signed int256."""
    n = word_to_uint(word)
    return n - (1 << 256) if n >= (1 << 255) else n


def word_to_address(word: str) -> str:
    """32-byte word / topic -> EIP-55 address (high 12 bytes must be zero)."""
    h = strip0x(word).rjust(64, "0")
    if int(h[:24], 16) != 0:
        raise ValueError(f"word has non-zero high bytes, not an address: {word!r}")
    return to_checksum_address("0x" + h[24:])


def word_to_bytes32(word: str) -> str:
    return "0x" + strip0x(word).rjust(64, "0").lower()


def decode_dynamic_bytes(data: str | bytes, offset_word_index: int) -> bytes:
    """Read an ABI dynamic ``bytes``/``string`` whose offset sits in word ``offset_word_index``."""
    raw = data if isinstance(data, bytes) else hex_to_bytes(data)
    offset = int.from_bytes(raw[offset_word_index * 32 : offset_word_index * 32 + 32], "big")
    length = int.from_bytes(raw[offset : offset + 32], "big")
    start = offset + 32
    if start + length > len(raw):
        raise ValueError("dynamic bytes run past the end of data")
    return raw[start : start + length]


def decode_dynamic_string(data: str | bytes, offset_word_index: int) -> str:
    return decode_dynamic_bytes(data, offset_word_index).decode("utf-8", errors="replace")


def uint_to_ascii(n: int) -> str | None:
    """Big-endian bytes of an integer as printable ASCII, else None. 1414680398 -> 'TRON'."""
    if n <= 0:
        return None
    b = n.to_bytes((n.bit_length() + 7) // 8, "big")
    return bytes_to_ascii(b)


def bytes_to_ascii(b: bytes, *, strip_nul: bool = True) -> str | None:
    """Bytes as printable ASCII (NUL padding stripped), else None."""
    if strip_nul:
        b = b.strip(b"\x00")
    if not b or any(c < 0x20 or c > 0x7E for c in b):
        return None
    return b.decode("ascii")


def decode_erc20_transfer(log: dict[str, Any]) -> dict[str, Any] | None:
    """Standard ERC-20 Transfer log (topics[0]=TRANSFER_TOPIC, 3 topics) -> {token, from, to, value(int)}.

    Accepts JSON-RPC style logs: {'address', 'topics': [...], 'data'}. Returns None if not a Transfer.
    """
    topics = log.get("topics") or []
    if len(topics) != 3 or str(topics[0]).lower() != TRANSFER_TOPIC:
        return None
    data = log.get("data") or "0x"
    return {
        "token": to_checksum_address(log["address"]) if is_address(log.get("address")) else log.get("address"),
        "from": word_to_address(topics[1]),
        "to": word_to_address(topics[2]),
        "value": word_to_uint(data),
    }
