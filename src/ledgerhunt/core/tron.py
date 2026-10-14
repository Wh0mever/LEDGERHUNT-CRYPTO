"""TRON address and amount helpers.

Address forms:
- base58check: ``T...`` (34 chars), payload = 0x41 + 20 bytes, checksum = sha256d[:4]
- hex with TRON prefix: ``41`` + 40 hex (what java-tron returns with visible=false)
- EVM-style hex: ``0x`` + 40 hex (event logs, ABI words; no 0x41 prefix)
"""

from __future__ import annotations

import hashlib
import re
from decimal import Decimal, InvalidOperation

import base58

USDT_TRC20 = "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"
USDT_TRC20_HEX = "41a614f803b6fd780986a42c78ec9c7f77e6ded13c"
USDT_DECIMALS = 6
TRX_DECIMALS = 6  # 1 TRX = 1_000_000 sun

ADDRESS_PREFIX = 0x41
_B58_RE = re.compile(r"^T[1-9A-HJ-NP-Za-km-z]{33}$")
_HEX_RE = re.compile(r"^[0-9a-fA-F]+$")


class InvalidTronAddress(ValueError):
    pass


def _sha256d(data: bytes) -> bytes:
    return hashlib.sha256(hashlib.sha256(data).digest()).digest()


def b58_to_bytes(address: str) -> bytes:
    """Decode a base58check TRON address to its 21-byte payload (0x41 + 20 bytes); validates checksum."""
    if not isinstance(address, str) or not _B58_RE.match(address):
        raise InvalidTronAddress(f"not a base58 TRON address: {address!r}")
    raw = base58.b58decode(address)
    if len(raw) != 25:
        raise InvalidTronAddress(f"bad length {len(raw)} for {address!r}")
    payload, checksum = raw[:21], raw[21:]
    if _sha256d(payload)[:4] != checksum:
        raise InvalidTronAddress(f"bad checksum: {address!r}")
    if payload[0] != ADDRESS_PREFIX:
        raise InvalidTronAddress(f"bad prefix 0x{payload[0]:02x}: {address!r}")
    return payload


def _hex_payload(value: str) -> bytes:
    """Accept '41'+40hex, '0x'+40hex, '0x41'+40hex or 40hex; return the 21-byte payload."""
    h = value.strip()
    if h.startswith(("0x", "0X")):
        h = h[2:]
    if not _HEX_RE.match(h):
        raise InvalidTronAddress(f"not hex: {value!r}")
    if len(h) == 40:
        h = "41" + h
    elif len(h) == 64:  # 32-byte ABI word
        if int(h[:24], 16) != 0:
            raise InvalidTronAddress(f"ABI word has non-zero high bytes: {value!r}")
        h = "41" + h[24:]
    if len(h) != 42 or h[:2].lower() != "41":
        raise InvalidTronAddress(f"expected 41 + 20 bytes: {value!r}")
    return bytes.fromhex(h)


def hex_to_b58(value: str) -> str:
    """'41..'/'0x..'/40-hex/32-byte word -> base58check 'T...'."""
    payload = _hex_payload(value)
    return base58.b58encode(payload + _sha256d(payload)[:4]).decode("ascii")


def b58_to_hex(address: str) -> str:
    """'T...' -> '41' + 40 lowercase hex."""
    return b58_to_bytes(address).hex()


def b58_to_evm_hex(address: str) -> str:
    """'T...' -> '0x' + 40 lowercase hex (the 20-byte account id, as in event logs)."""
    return "0x" + b58_to_bytes(address)[1:].hex()


def to_b58(value: str) -> str:
    """Normalize any supported address form to base58check (validates)."""
    if isinstance(value, str) and value.startswith("T"):
        b58_to_bytes(value)
        return value
    return hex_to_b58(value)


def is_valid_address(value: str) -> bool:
    try:
        to_b58(value)
        return True
    except (InvalidTronAddress, ValueError, TypeError):
        return False


def word_to_b58(word: str) -> str:
    """32-byte ABI word / topic (hex, optional 0x) -> 'T...'."""
    return hex_to_b58(word)


def address_to_word(address: str) -> str:
    """'T...' or hex address -> 64-hex ABI word (no 0x) for triggerconstantcontract parameters."""
    payload = _hex_payload(address) if not address.startswith("T") else b58_to_bytes(address)
    return payload[1:].hex().rjust(64, "0")


# ---------------------------------------------------------------- amounts


def format_amount(raw: int | str, decimals: int = USDT_DECIMALS) -> str:
    """Raw integer amount -> fixed-point decimal string with exactly ``decimals`` places.

    format_amount(13041400772) == '13041.400772'; never goes through float.
    """
    if isinstance(raw, bool):
        raise TypeError("bool is not an amount")
    if isinstance(raw, str):
        raw = raw.strip()
        if not re.fullmatch(r"-?\d+", raw):
            raise ValueError(f"raw amount must be an integer string: {raw!r}")
        n = int(raw)
    elif isinstance(raw, int):
        n = raw
    else:
        raise TypeError(f"raw amount must be int or str, not {type(raw).__name__}")
    sign = "-" if n < 0 else ""
    n = abs(n)
    if decimals == 0:
        return f"{sign}{n}"
    q, r = divmod(n, 10**decimals)
    return f"{sign}{q}.{r:0{decimals}d}"


def parse_amount(value: str | Decimal, decimals: int = USDT_DECIMALS) -> int:
    """Decimal string -> raw integer. Raises if it has more than ``decimals`` fractional digits."""
    if isinstance(value, float):
        raise TypeError("floats are not accepted for amounts")
    try:
        d = Decimal(str(value).strip())
    except InvalidOperation as exc:
        raise ValueError(f"not a decimal amount: {value!r}") from exc
    scaled = d.scaleb(decimals)
    if scaled != scaled.to_integral_value():
        raise ValueError(f"{value!r} has more than {decimals} decimal places")
    return int(scaled)


def to_decimal(raw: int | str, decimals: int = USDT_DECIMALS) -> Decimal:
    """Raw integer amount -> exact Decimal."""
    return Decimal(format_amount(raw, decimals))


def sun_to_trx(raw: int | str) -> str:
    return format_amount(raw, TRX_DECIMALS)
