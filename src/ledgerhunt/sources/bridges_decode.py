"""Pure decoders for the case-001 bridge segments: USDT0 / LayerZero OFT, Rango, NEAR Intents 1Click.

No network access here. Every decoder takes raw chain data (EVM-style logs with ``address``,
``topics``, ``data``; TRON logs use the same layout with 40-hex addresses without 0x/41) and
returns plain dicts with integer amounts (convert with ``format_amount`` before writing).

Event signatures were checked against case-001 raw logs on 2026-10-14 (topic0 of each event
equals keccak256 of the signature below; see stage2/bridges.py for the live check):
- OFTSent(bytes32 indexed guid, uint32 dstEid, address indexed fromAddress, uint256 amountSentLD,
  uint256 amountReceivedLD)                     TRON tx b49b0157..., USDT0 OFT TFG4wB...
- OFTReceived(bytes32 indexed guid, uint32 srcEid, address indexed toAddress, uint256 amountReceivedLD)
                                                Ethereum tx 0x8ea2..., USDT0 OFT 0x1F748c...
- PacketSent(bytes encodedPayload, bytes options, address sendLibrary)   LayerZero EndpointV2
- RangoBridgeInitiated(address indexed requestId, address bridgeToken, uint256 bridgeAmount,
  address receiver, uint256 destinationChainId, bool hasInterchainMessage, bool hasDestinationSwap,
  uint8 indexed bridgeId, uint16 indexed dAppTag, string dAppName)        Rango Diamond 0x6946...
- Routed(address indexed token, address indexed from, address indexed to, uint256 amount)
- FeeInfo(address token, address indexed affiliatorAddress, uint256 affiliateFee, uint8 indexed feeType,
  uint16 indexed dAppTag)
"""

from __future__ import annotations

from typing import Any, Iterable

from ..core.evm import (
    TRANSFER_TOPIC,
    bytes_to_ascii,
    decode_dynamic_bytes,
    decode_dynamic_string,
    event_topic,
    hex_to_bytes,
    is_address,
    normalize_address,
    split_words,
    strip0x,
    to_checksum_address,
    uint_to_ascii,
    word_to_address,
    word_to_uint,
)
from ..core.tron import hex_to_b58, is_valid_address

# ---------------------------------------------------------------- signatures / topics

SIG_OFT_SENT = "OFTSent(bytes32,uint32,address,uint256,uint256)"
SIG_OFT_RECEIVED = "OFTReceived(bytes32,uint32,address,uint256)"
SIG_PACKET_SENT = "PacketSent(bytes,bytes,address)"
SIG_PACKET_DELIVERED = "PacketDelivered((uint32,bytes32,uint64),address)"
SIG_RANGO_BRIDGE_INITIATED = (
    "RangoBridgeInitiated(address,address,uint256,address,uint256,bool,bool,uint8,uint16,string)"
)
SIG_RANGO_ROUTED = "Routed(address,address,address,uint256)"
SIG_RANGO_FEE_INFO = "FeeInfo(address,address,uint256,uint8,uint16)"
SIG_RANGO_SEND_TOKEN = "SendToken(address,uint256,address)"

TOPIC_OFT_SENT = event_topic(SIG_OFT_SENT)
TOPIC_OFT_RECEIVED = event_topic(SIG_OFT_RECEIVED)
TOPIC_PACKET_SENT = event_topic(SIG_PACKET_SENT)
TOPIC_PACKET_DELIVERED = event_topic(SIG_PACKET_DELIVERED)
TOPIC_RANGO_BRIDGE_INITIATED = event_topic(SIG_RANGO_BRIDGE_INITIATED)
TOPIC_RANGO_ROUTED = event_topic(SIG_RANGO_ROUTED)
TOPIC_RANGO_FEE_INFO = event_topic(SIG_RANGO_FEE_INFO)
TOPIC_RANGO_SEND_TOKEN = event_topic(SIG_RANGO_SEND_TOKEN)

# ---------------------------------------------------------------- registry (verified sources in docs)

# LayerZero V2 endpoint ids seen in case-001 / USDT0 deployments API (docs.usdt0.to/api/deployments).
LZ_EID_CHAIN = {30101: "ethereum", 30110: "arbitrum", 30420: "tron"}
# USDT0 "Legacy Mesh" OFT contracts (USDT0 deployments API, fetched 2026-10-14).
USDT0_LEGACY_MESH = {
    "tron": "TFG4wBaDQ8sHWWP1ACeSGnoNR6RRzevLPt",
    "ethereum": "0x1F748c76dE468e9D11bd340fA9D5CBADf315dFB0",
    "arbitrum": "0x77652D5aba086137b595875263FC200182919B92",
}
# Rango Diamond on Ethereum (explorer name 'RangoDiamond'; emits RangoBridgeInitiated in case-001).
RANGO_DIAMOND_ETH = "0x69460570c93f9DE5E2edbC3052bf10125f0Ca22d"
# NEAR Intents vault on Ethereum (explorer tag in case-001 fixture; deposit addresses sweep into it).
NEAR_INTENTS_VAULT_ETH = "0x2CfF890f0378a11913B6129B2E97417a2c302680"
# NEAR Intents TRON payout wallet observed in case-001 (step 17). Observation, not an official list.
NEAR_INTENTS_TRON_PAYOUT_OBSERVED = "TX5XiRXdyz7sdFwF5mnhT1QoGCpbkncpke"
# Rango destinationChainId is the ASCII of the chain name packed into an integer: 'TRON' -> 1414680398.
RANGO_CHAIN_TRON = 1414680398


# ---------------------------------------------------------------- log normalisation


def _h(value: Any) -> str:
    """Lowercase hex with 0x prefix ('' / None -> '0x')."""
    if value is None:
        return "0x"
    s = str(value).strip().lower()
    return s if s.startswith("0x") else "0x" + s


def norm_log(log: dict[str, Any], *, source: str, default_index: int | None = None) -> dict[str, Any]:
    """One log in a common shape: {log_index:int|None, address:'0x..' lower, topics:[lower], data: lower}.

    source: 'rpc' (eth_getTransactionReceipt / eth_getLogs), 'blockscout' (/api/v2/transactions/{h}/logs),
    'etherscan' (proxy receipt or logs module), 'tron' (gettransactioninfobyid log: 40-hex address).
    """
    if source == "blockscout":
        addr = (log.get("address") or {}).get("hash") if isinstance(log.get("address"), dict) else log.get("address")
        idx = log.get("index")
        topics = [t for t in (log.get("topics") or []) if t]
    else:
        addr = log.get("address")
        idx = log.get("logIndex", log.get("log_index"))
        topics = [t for t in (log.get("topics") or []) if t]
    if isinstance(idx, str):
        idx = int(idx, 16) if idx.lower().startswith("0x") else int(idx)
    if idx is None:
        idx = default_index  # TRON receipts carry no log index: callers pass the position
    a = _h(addr)
    if source == "tron" and len(strip0x(a)) == 40:
        a = "0x" + strip0x(a)
    return {
        "log_index": idx,
        "address": a,
        "topics": [_h(t) for t in topics],
        "data": _h(log.get("data") or "0x"),
    }


def compare_log_sets(a: list[dict[str, Any]], b: list[dict[str, Any]]) -> dict[str, Any]:
    """Compare two normalised log lists by log_index. Returns counts and the differing fields."""
    ia = {x["log_index"]: x for x in a}
    ib = {x["log_index"]: x for x in b}
    diffs: list[dict[str, Any]] = []
    for idx in sorted(set(ia) | set(ib), key=lambda v: (v is None, v)):
        x, y = ia.get(idx), ib.get(idx)
        if x is None or y is None:
            diffs.append({"log_index": idx, "missing_in": "a" if x is None else "b"})
            continue
        fields = [k for k in ("address", "topics", "data") if x[k] != y[k]]
        if fields:
            diffs.append({"log_index": idx, "fields": fields})
    return {"count_a": len(a), "count_b": len(b), "equal": not diffs and len(a) == len(b), "diffs": diffs[:20]}


def erc20_transfers_from_logs(logs: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    """ERC-20 Transfer events from normalised logs: [{log_index, token, from, to, value:int}] (addresses lower)."""
    out = []
    for lg in logs:
        t = lg["topics"]
        if len(t) == 3 and t[0] == TRANSFER_TOPIC:
            out.append({
                "log_index": lg["log_index"],
                "token": lg["address"],
                "from": "0x" + t[1][-40:],
                "to": "0x" + t[2][-40:],
                "value": word_to_uint(lg["data"]) if strip0x(lg["data"]) else 0,
            })
    return out


def blockscout_token_transfers(items: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    """Blockscout /token-transfers items in the same shape as erc20_transfers_from_logs (ERC-20 only)."""
    out = []
    for it in items:
        if (it.get("token_type") or (it.get("token") or {}).get("type")) not in (None, "ERC-20"):
            continue
        tok = it.get("token") or {}
        token = tok.get("address_hash") or tok.get("address")
        total = it.get("total") or {}
        value = total.get("value")
        out.append({
            "log_index": it.get("log_index"),
            "token": token.lower() if isinstance(token, str) else token,
            "from": ((it.get("from") or {}).get("hash") or "").lower(),
            "to": ((it.get("to") or {}).get("hash") or "").lower(),
            "value": int(value) if value is not None else None,
        })
    return out


def compare_transfer_sets(a: list[dict[str, Any]], b: list[dict[str, Any]]) -> dict[str, Any]:
    key = lambda r: (r["log_index"], r["token"], r["from"], r["to"], r["value"])  # noqa: E731
    sa, sb = {key(r) for r in a}, {key(r) for r in b}
    return {"count_a": len(sa), "count_b": len(sb), "equal": sa == sb,
            "only_a": sorted(map(str, sa - sb))[:10], "only_b": sorted(map(str, sb - sa))[:10]}


# ---------------------------------------------------------------- address helpers


def tron_word_to_b58(word: str) -> str:
    """32-byte word or 20-byte hex holding a TRON address body -> base58 'T...'."""
    return hex_to_b58("41" + strip0x(word)[-40:])


def evm_or_tron(word_or_hex: str, chain: str) -> str:
    """Render the low 20 bytes of a word as an address of ``chain`` ('tron' -> base58, else EIP-55)."""
    body = strip0x(word_or_hex)[-40:]
    if chain == "tron":
        return hex_to_b58("41" + body)
    return to_checksum_address("0x" + body)


# ---------------------------------------------------------------- LayerZero / USDT0


def decode_oft_sent(log: dict[str, Any], *, chain: str = "tron") -> dict[str, Any] | None:
    """OFTSent from a normalised log. chain is the SOURCE chain (address rendering)."""
    t = log["topics"]
    if len(t) != 3 or t[0] != TOPIC_OFT_SENT:
        return None
    w = split_words(log["data"])
    if len(w) < 3:
        return None
    dst_eid = word_to_uint(w[0])
    return {
        "event": "OFTSent",
        "oft": evm_or_tron(log["address"], chain),
        "guid": t[1],
        "from": evm_or_tron(t[2], chain),
        "dst_eid": dst_eid,
        "dst_chain": LZ_EID_CHAIN.get(dst_eid),
        "amount_sent_ld": word_to_uint(w[1]),
        "amount_received_ld": word_to_uint(w[2]),
        "log_index": log.get("log_index"),
    }


def decode_oft_received(log: dict[str, Any], *, chain: str = "ethereum") -> dict[str, Any] | None:
    """OFTReceived from a normalised log. chain is the DESTINATION chain."""
    t = log["topics"]
    if len(t) != 3 or t[0] != TOPIC_OFT_RECEIVED:
        return None
    w = split_words(log["data"])
    if len(w) < 2:
        return None
    src_eid = word_to_uint(w[0])
    return {
        "event": "OFTReceived",
        "oft": evm_or_tron(log["address"], chain),
        "guid": t[1],
        "to": evm_or_tron(t[2], chain),
        "src_eid": src_eid,
        "src_chain": LZ_EID_CHAIN.get(src_eid),
        "amount_received_ld": word_to_uint(w[1]),
        "log_index": log.get("log_index"),
    }


def decode_oft_message(message_hex: str, *, dst_chain: str | None) -> dict[str, Any]:
    """Decode an OFT message (the app payload inside a LayerZero packet).

    Observed USDT0 Legacy Mesh format (case-001, 42 bytes): uint16 0x0002 | bytes32 sendTo | uint64 amountSD.
    The meaning of the 2-byte prefix is not verified against contract source; it is reported as-is.
    The standard LayerZero OFT codec is bytes32 sendTo | uint64 amountSD [| bytes32 composeFrom | composeMsg].
    """
    b = hex_to_bytes(message_hex)
    out: dict[str, Any] = {"length": len(b)}
    if len(b) == 42:
        out["format"] = "usdt0_legacy_mesh_42"
        out["prefix_hex"] = b[:2].hex()
        body = b[2:]
    elif len(b) >= 40:
        out["format"] = "oft_standard" if len(b) == 40 else "oft_with_compose"
        body = b
    else:
        out["format"] = "unknown"
        return out
    send_to = body[:32]
    out["send_to_word"] = "0x" + send_to.hex()
    out["send_to"] = evm_or_tron(send_to.hex(), dst_chain or "ethereum") if send_to[:12] == bytes(12) else None
    out["amount_sd"] = int.from_bytes(body[32:40], "big")
    if len(body) > 40:
        out["compose_bytes"] = len(body) - 40
    return out


def decode_packet_sent(log: dict[str, Any]) -> dict[str, Any] | None:
    """LayerZero EndpointV2 PacketSent: decode the encoded packet header, guid and OFT message."""
    t = log["topics"]
    if not t or t[0] != TOPIC_PACKET_SENT:
        return None
    try:
        packet = decode_dynamic_bytes(log["data"], 0)
    except (ValueError, IndexError):
        return None
    if len(packet) < 113:
        return None
    src_eid = int.from_bytes(packet[9:13], "big")
    dst_eid = int.from_bytes(packet[45:49], "big")
    src_chain = LZ_EID_CHAIN.get(src_eid)
    dst_chain = LZ_EID_CHAIN.get(dst_eid)
    message = packet[113:]
    return {
        "event": "PacketSent",
        "version": packet[0],
        "nonce": int.from_bytes(packet[1:9], "big"),
        "src_eid": src_eid,
        "sender": evm_or_tron(packet[13:45].hex(), src_chain or "ethereum"),
        "dst_eid": dst_eid,
        "receiver": evm_or_tron(packet[49:81].hex(), dst_chain or "ethereum"),
        "guid": "0x" + packet[81:113].hex(),
        "message_hex": "0x" + message.hex(),
        "oft_message": decode_oft_message(message.hex(), dst_chain=dst_chain),
    }


def lz_message_summary(msg: dict[str, Any]) -> dict[str, Any]:
    """Fields we need from one LayerZero Scan message (GET /v1/messages/tx|guid)."""
    pw = msg.get("pathway") or {}
    src = msg.get("source") or {}
    dst = msg.get("destination") or {}
    src_tx = src.get("tx") or {}
    dst_tx = dst.get("tx") or {}
    dst_eid = pw.get("dstEid")
    payload = src_tx.get("payload")
    return {
        "guid": msg.get("guid"),
        "src_eid": pw.get("srcEid"),
        "dst_eid": dst_eid,
        "src_chain": (pw.get("sender") or {}).get("chain"),
        "dst_chain": (pw.get("receiver") or {}).get("chain"),
        "sender_oapp": (pw.get("sender") or {}).get("address"),
        "sender_name": (pw.get("sender") or {}).get("name"),
        "receiver_oapp": (pw.get("receiver") or {}).get("address"),
        "nonce": pw.get("nonce"),
        "src_tx": src_tx.get("txHash"),
        "src_block": src_tx.get("blockNumber"),
        "src_timestamp": src_tx.get("blockTimestamp"),
        "src_from": src_tx.get("from"),
        "dst_tx": dst_tx.get("txHash"),
        "dst_block": dst_tx.get("blockNumber"),
        "dst_timestamp": dst_tx.get("blockTimestamp"),
        "status": (msg.get("status") or {}).get("name"),
        "source_status": src.get("status"),
        "destination_status": dst.get("status"),
        "payload": decode_oft_message(payload, dst_chain=LZ_EID_CHAIN.get(dst_eid)) if payload else None,
        "created": msg.get("created"),
        "updated": msg.get("updated"),
    }


# ---------------------------------------------------------------- Rango


def rango_request_uuid(request_id_addr: str) -> str | None:
    """RangoBridgeInitiated.requestId is an address-typed field; in case-001 its low 16 bytes form a UUIDv4.

    Returns the UUID text when the top 4 bytes are zero and the version nibble is 4, else None.
    This is an observation about the encoding, not documented by Rango.
    """
    h = strip0x(request_id_addr).lower()
    if len(h) != 40 or h[:8] != "00000000":
        return None
    u = h[8:]
    if u[12] != "4":
        return None
    return f"{u[:8]}-{u[8:12]}-{u[12:16]}-{u[16:20]}-{u[20:]}"


def decode_rango_bridge_initiated(log: dict[str, Any]) -> dict[str, Any] | None:
    t = log["topics"]
    if len(t) != 4 or t[0] != TOPIC_RANGO_BRIDGE_INITIATED:
        return None
    w = split_words(log["data"])
    if len(w) < 7:
        return None
    receiver_raw = bytes.fromhex(strip0x(w[2])[-40:])
    dest_chain_id = word_to_uint(w[3])
    request_id = word_to_address(t[1])
    try:
        dapp_name = decode_dynamic_string(log["data"], 6)
    except (ValueError, IndexError):
        dapp_name = None
    receiver_ascii = bytes_to_ascii(receiver_raw)
    return {
        "event": "RangoBridgeInitiated",
        "emitter": to_checksum_address(log["address"]),
        "request_id": request_id,
        "request_uuid": rango_request_uuid(request_id),
        "bridge_token": word_to_address(w[0]),
        "bridge_amount": word_to_uint(w[1]),
        "receiver_hex": "0x" + receiver_raw.hex(),
        "receiver_evm": to_checksum_address("0x" + receiver_raw.hex()),
        "receiver_ascii": receiver_ascii,
        "destination_chain_id": dest_chain_id,
        "destination_chain_ascii": uint_to_ascii(dest_chain_id),
        "has_interchain_message": bool(word_to_uint(w[4])),
        "has_destination_swap": bool(word_to_uint(w[5])),
        "bridge_id": word_to_uint(t[2]),
        "dapp_tag": word_to_uint(t[3]),
        "dapp_name": dapp_name,
        "log_index": log.get("log_index"),
    }


def decode_rango_routed(log: dict[str, Any]) -> dict[str, Any] | None:
    t = log["topics"]
    if len(t) != 4 or t[0] != TOPIC_RANGO_ROUTED:
        return None
    return {
        "event": "Routed",
        "emitter": to_checksum_address(log["address"]),
        "token": word_to_address(t[1]),
        "from": word_to_address(t[2]),
        "to": word_to_address(t[3]),
        "amount": word_to_uint(log["data"]),
        "log_index": log.get("log_index"),
    }


def decode_rango_fee_info(log: dict[str, Any]) -> dict[str, Any] | None:
    t = log["topics"]
    if len(t) != 4 or t[0] != TOPIC_RANGO_FEE_INFO:
        return None
    w = split_words(log["data"])
    if len(w) < 2:
        return None
    return {
        "event": "FeeInfo",
        "token": word_to_address(w[0]),
        "affiliator": word_to_address(t[1]),
        "affiliate_fee": word_to_uint(w[1]),
        "fee_type": word_to_uint(t[2]),
        "dapp_tag": word_to_uint(t[3]),
        "log_index": log.get("log_index"),
    }


def tron_prefix_candidates(prefix: str | None) -> bool:
    """True when ``prefix`` looks like the start of a TRON base58 address (Rango packs 20 ASCII bytes)."""
    if not prefix or not prefix.startswith("T") or len(prefix) < 10:
        return False
    alphabet = set("123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz")
    return all(c in alphabet for c in prefix)


def blockscout_decoded_params(item: dict[str, Any]) -> dict[str, Any] | None:
    """{name: value} of Blockscout's 'decoded' block of one log item (None when not decoded)."""
    d = item.get("decoded") or {}
    if not d:
        return None
    return {"method_call": d.get("method_call"), **{p.get("name"): p.get("value") for p in d.get("parameters") or []}}


# ---------------------------------------------------------------- NEAR Intents 1Click


def oneclick_summary(data: dict[str, Any] | None) -> dict[str, Any] | None:
    """Fields we need from GET /v0/status (None when the body is not a status object)."""
    if not isinstance(data, dict) or "status" not in data:
        return None
    sd = data.get("swapDetails") or {}
    qr = data.get("quoteResponse") or {}
    req = qr.get("quoteRequest") or {}
    quote = qr.get("quote") or {}
    return {
        "status": data.get("status"),
        "updated_at": data.get("updatedAt"),
        "recipient": req.get("recipient"),
        "recipient_type": req.get("recipientType"),
        "refund_to": req.get("refundTo"),
        "origin_asset": req.get("originAsset"),
        "destination_asset": req.get("destinationAsset"),
        "referral": req.get("referral"),
        "deposit_address": quote.get("depositAddress"),
        "amount_in": sd.get("amountIn"),
        "amount_in_formatted": sd.get("amountInFormatted"),
        "amount_out": sd.get("amountOut"),
        "amount_out_formatted": sd.get("amountOutFormatted"),
        "refunded_amount": sd.get("refundedAmount"),
        "withdraw_fee": sd.get("withdrawFee"),
        "refund_fee": sd.get("refundFee"),
        "intent_hashes": sd.get("intentHashes"),
        "near_tx_hashes": sd.get("nearTxHashes"),
        "origin_chain_tx_hashes": [h.get("hash") for h in sd.get("originChainTxHashes") or []],
        "destination_chain_tx_hashes": [h.get("hash") for h in sd.get("destinationChainTxHashes") or []],
    }


def is_tron_address(value: Any) -> bool:
    return isinstance(value, str) and is_valid_address(value)


def is_evm_address(value: Any) -> bool:
    return is_address(value)


def lower_or_none(addr: str | None) -> str | None:
    return normalize_address(addr) if is_address(addr) else None
