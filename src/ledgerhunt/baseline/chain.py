"""Plain parsing helpers over raw source responses (TRON java-tron / TronGrid v1, Ethereum logs).

All amounts stay integers in token base units (USDT: 6 decimals) until they are formatted
with ``fmt`` for output; nothing goes through float.
"""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from ..core.evm import (
    bytes_to_ascii,
    decode_dynamic_string,
    hex_to_bytes,
    split_words,
    strip0x,
    to_checksum_address,
    uint_to_ascii,
    word_to_uint,
)
from ..core.tron import format_amount, hex_to_b58, to_b58
from .registry import EVENT_ABIS, SELECTORS, TOKENS, TOPIC_TO_EVENT

# ---------------------------------------------------------------- time


def ts_utc(ms: int | None) -> str | None:
    """Milliseconds since epoch -> 'YYYY-MM-DD HH:MM:SS' (UTC)."""
    if ms is None:
        return None
    return datetime.fromtimestamp(int(ms) / 1000, timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def parse_ts(text: str) -> int:
    """'YYYY-MM-DD HH:MM:SS' or ISO 8601 (Blockscout) -> milliseconds since epoch (UTC)."""
    t = text.strip().replace("T", " ").rstrip("Z")
    if "." in t:
        t = t.split(".", 1)[0]
    return int(datetime.strptime(t, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc).timestamp() * 1000)


def fmt(raw: int, decimals: int = 6) -> str:
    return format_amount(int(raw), decimals)


def dec(raw: int, decimals: int = 6) -> Decimal:
    return Decimal(int(raw)).scaleb(-decimals)


def trunc_share(raw: int, share: str) -> int:
    """floor(raw * share) for a decimal-string share, exact integer arithmetic."""
    d = Decimal(share)
    num, den = d.as_integer_ratio()
    return raw * num // den


def round_share(raw: int, share: str) -> int:
    """raw * share rounded half-up to an integer, exact integer arithmetic."""
    num, den = Decimal(share).as_integer_ratio()
    return (2 * raw * num + den) // (2 * den)


def is_exact_cut(value: int, base: int, share: str) -> bool:
    """value equals base * share at the token precision, truncated or rounded half-up."""
    return value in (trunc_share(base, share), round_share(base, share))


def asset_of(chain: str, token: str) -> str | None:
    key = (chain, token if chain == "tron" else token.lower())
    entry = TOKENS.get(key)
    return str(entry["asset"]) if entry else None


# ---------------------------------------------------------------- addresses


def tron_addr(value: str) -> str:
    """Any TRON address form (base58, 41-hex, 0x-hex, 32-byte word) -> base58."""
    return to_b58(value)


def evm_addr(value: str) -> str:
    return to_checksum_address(value)


def same_evm(a: str | None, b: str | None) -> bool:
    return bool(a and b) and a.lower() == b.lower()


# ---------------------------------------------------------------- ABI event decoding


def _decode_value(abi_type: str, word: str, chain: str) -> Any:
    if abi_type == "address":
        h = strip0x(word).rjust(64, "0")
        if int(h[:24], 16) != 0:
            return "0x" + h  # not a clean address word; keep raw
        return hex_to_b58("41" + h[24:]) if chain == "tron" else to_checksum_address("0x" + h[24:])
    if abi_type == "bytes32":
        return "0x" + strip0x(word).rjust(64, "0").lower()
    if abi_type == "bool":
        return word_to_uint(word) != 0
    if abi_type.startswith("uint"):
        return word_to_uint(word)
    raise ValueError(f"unsupported static ABI type {abi_type}")


def decode_event(topics: list[str], data: str, chain: str) -> dict[str, Any] | None:
    """Decode a raw log (topics + data hex) with the registry ABIs. None when topic0 is unknown.

    Address parameters come out as base58 on TRON and EIP-55 on EVM chains. Raw extras:
    ``_raw_address_hex`` for address params (needed when an 'address' carries ASCII bytes).
    """
    if not topics:
        return None
    name = TOPIC_TO_EVENT.get(strip0x(topics[0]).lower())
    if name is None:
        return None
    _, params = EVENT_ABIS[name]
    indexed = [strip0x(t) for t in topics[1:]]
    words = split_words(data or "0x") if strip0x(data or "") else []
    out: dict[str, Any] = {"event": name}
    raw_hex: dict[str, str] = {}
    i_idx = 0
    w_idx = 0
    for pname, ptype, is_indexed in params:
        if is_indexed:
            if i_idx >= len(indexed):
                return None  # same topic0, different indexing: not our ABI
            word = indexed[i_idx]
            i_idx += 1
        else:
            if w_idx >= len(words):
                return None
            word = words[w_idx]
            w_idx += 1
        if ptype == "string":
            out[pname] = decode_dynamic_string(data, w_idx - 1)
            continue
        out[pname] = _decode_value(ptype, word, chain)
        if ptype == "address":
            raw_hex[pname] = "0x" + strip0x(word)[-40:].lower()
    if i_idx != len(indexed):
        return None
    out["_raw_address_hex"] = raw_hex
    return out


def ascii_of_address_bytes(hex20: str) -> str | None:
    """20 address bytes read as ASCII (Rango puts non-EVM receivers there), else None."""
    return bytes_to_ascii(hex_to_bytes(hex20))


def ascii_of_uint(n: int) -> str | None:
    return uint_to_ascii(n)


# ---------------------------------------------------------------- TRON transactions


def tron_logs(info: dict[str, Any]) -> list[dict[str, Any]]:
    """Decoded logs of a gettransactioninfobyid answer, each with its emitter (base58) and index."""
    out = []
    for i, lg in enumerate(info.get("log") or []):
        emitter = hex_to_b58("41" + lg["address"]) if lg.get("address") else None
        ev = decode_event(lg.get("topics") or [], lg.get("data") or "", "tron")
        out.append({"log_index": i, "emitter": emitter, "topic0": (lg.get("topics") or [None])[0],
                    "decoded": ev})
    return out


def tron_token_transfers(info: dict[str, Any]) -> list[dict[str, Any]]:
    """Transfer events of known tokens in a TRON receipt: [{token, asset, from, to, value, log_index}]."""
    out = []
    for lg in tron_logs(info):
        ev = lg["decoded"]
        if ev and ev["event"] == "Transfer":
            out.append({"token": lg["emitter"], "asset": asset_of("tron", lg["emitter"]), "from": ev["from"],
                        "to": ev["to"], "value": ev["value"], "log_index": lg["log_index"]})
    return out


def tron_contract(tx: dict[str, Any]) -> dict[str, Any]:
    """Main fields of the first contract of a gettransactionbyid (visible=true) answer."""
    raw = tx.get("raw_data") or {}
    contracts = raw.get("contract") or []
    if not contracts:
        return {}
    c = contracts[0]
    v = (c.get("parameter") or {}).get("value") or {}
    out: dict[str, Any] = {
        "type": c.get("type"),
        "permission_id": c.get("Permission_id"),  # absent -> 0 (owner permission)
        "owner": v.get("owner_address"),
        "ret": ((tx.get("ret") or [{}])[0]).get("contractRet"),
        "signature_count": len(tx.get("signature") or []),
        "contract_count": len(contracts),
    }
    t = c.get("type")
    if t == "TransferContract":
        out.update({"to": v.get("to_address"), "amount_sun": int(v.get("amount") or 0)})
    elif t in ("DelegateResourceContract", "UnDelegateResourceContract"):
        out.update({"to": v.get("receiver_address"), "balance_sun": int(v.get("balance") or 0),
                    "resource": v.get("resource", "BANDWIDTH")})
    elif t == "TriggerSmartContract":
        out.update({"contract": v.get("contract_address"), "call_value_sun": int(v.get("call_value") or 0)})
        out["call"] = decode_call(v.get("data") or "", "tron")
    elif t == "AccountPermissionUpdateContract":
        out["permission_update"] = True
    return out


def decode_call(data: str, chain: str) -> dict[str, Any]:
    """Known calldata: TRC-20 transfer/approve/transferFrom and OFT send(SendParam,...)."""
    h = strip0x(data)
    sel = h[:8]
    name = SELECTORS.get(sel)
    out: dict[str, Any] = {"selector": sel, "method": name}
    body = h[8:]
    if not name or len(body) % 64:
        return out
    words = split_words(body)
    conv = (lambda w: hex_to_b58("41" + w[24:])) if chain == "tron" else (lambda w: to_checksum_address("0x" + w[24:]))
    try:
        if name in ("transfer", "approve"):
            out.update({"to": conv(words[0]), "value": word_to_uint(words[1])})
        elif name == "transferFrom":
            out.update({"from": conv(words[0]), "to": conv(words[1]), "value": word_to_uint(words[2])})
        elif name == "oft_send":
            # send(SendParam calldata, MessagingFee calldata, address refund): SendParam is dynamic,
            # its head offset is word 0; inside: dstEid, to (bytes32), amountLD, minAmountLD, ...
            base = word_to_uint(words[0]) // 32
            out.update({
                "dstEid": word_to_uint(words[base]),
                "to_bytes32": "0x" + words[base + 1],
                "amountLD": word_to_uint(words[base + 2]),
                "minAmountLD": word_to_uint(words[base + 3]),
                "nativeFee": word_to_uint(words[1]),
            })
    except (IndexError, ValueError):
        out["decode_error"] = True
    return out


# ---------------------------------------------------------------- TronGrid v1 rows


def v1_transfer_rows(rows: list[dict[str, Any]], token: str) -> list[dict[str, Any]]:
    """TronGrid v1 trc20 rows of type Transfer for ``token``, normalized and in chain order."""
    out = []
    for r in rows:
        if r.get("type") != "Transfer":
            continue
        if (r.get("token_info") or {}).get("address") != token:
            continue
        out.append({
            "txid": r["transaction_id"],
            "ts": int(r["block_timestamp"]),
            "from": r["from"],
            "to": r["to"],
            "value": int(r["value"]),
        })
    return out


def v1_native_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """TronGrid v1 account transactions -> [{txid, ts, type, owner, to, amount_sun, ret}]."""
    out = []
    for r in rows:
        if "txID" not in r:
            continue
        c = ((r.get("raw_data") or {}).get("contract") or [{}])[0]
        v = (c.get("parameter") or {}).get("value") or {}
        to = v.get("to_address") or v.get("receiver_address") or v.get("contract_address")
        amount = v.get("amount")
        if amount is None:
            amount = v.get("balance")
        out.append({
            "txid": r["txID"],
            "ts": int(r.get("block_timestamp") or 0),
            "type": c.get("type"),
            "owner": _safe_b58(v.get("owner_address")),
            "to": _safe_b58(to),
            "amount_sun": int(amount) if amount is not None else None,
            "resource": v.get("resource"),
            "ret": ((r.get("ret") or [{}])[0]).get("contractRet"),
        })
    return out


def _safe_b58(value: str | None) -> str | None:
    if not value:
        return None
    try:
        return to_b58(value)
    except ValueError:
        return value


# ---------------------------------------------------------------- Ethereum


def evm_logs_from_blockscout(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Blockscout /logs items -> [{log_index, emitter, decoded}] decoded with OUR registry ABIs (raw topics/data)."""
    out = []
    for it in items:
        topics = [t for t in (it.get("topics") or []) if t]
        emitter = to_checksum_address((it.get("address") or {}).get("hash"))
        out.append({"log_index": int(it.get("index")), "emitter": emitter, "topic0": topics[0] if topics else None,
                    "decoded": decode_event(topics, it.get("data") or "0x", "ethereum")})
    return sorted(out, key=lambda x: x["log_index"])


def evm_logs_from_receipt(receipt: dict[str, Any]) -> list[dict[str, Any]]:
    """JSON-RPC receipt logs -> same shape as ``evm_logs_from_blockscout``."""
    out = []
    for lg in receipt.get("logs") or []:
        topics = lg.get("topics") or []
        out.append({"log_index": int(lg["logIndex"], 16), "emitter": to_checksum_address(lg["address"]),
                    "topic0": topics[0] if topics else None,
                    "decoded": decode_event(topics, lg.get("data") or "0x", "ethereum")})
    return sorted(out, key=lambda x: x["log_index"])


def evm_token_transfers(logs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    for lg in logs:
        ev = lg["decoded"]
        if ev and ev["event"] == "Transfer":
            out.append({"token": lg["emitter"], "asset": asset_of("ethereum", lg["emitter"]), "from": ev["from"],
                        "to": ev["to"], "value": ev["value"], "log_index": lg["log_index"]})
    return out


def blockscout_transfer_rows(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Blockscout address token-transfers items -> [{txid, ts, block, log_index, from, to, value, token}]."""
    out = []
    for it in items:
        total = it.get("total") or {}
        if total.get("value") is None:
            continue
        out.append({
            "txid": it["transaction_hash"],
            "ts": parse_ts(it["timestamp"]),
            "block": int(it["block_number"]),
            "log_index": int(it.get("log_index") or 0),
            "from": to_checksum_address(it["from"]["hash"]),
            "to": to_checksum_address(it["to"]["hash"]),
            "value": int(total["value"]),
            "token": to_checksum_address((it.get("token") or {}).get("address_hash")
                                         or (it.get("token") or {}).get("address")),
        })
    return sorted(out, key=lambda r: (r["block"], r["log_index"]))
