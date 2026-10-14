"""Raw response formats of the real sources, rebuilt for synthetic transactions.

Shapes, key order and whitespace follow responses recorded live on 2026-10-14
(data/http-store, case-001 transactions 98f3ffca..., b49b0157...):

- TronGrid v1 list endpoints: compact JSON ``{"data":[...],"success":true,"meta":{...}}``.
- TronGrid ``/v1/transactions/{txid}/events``: events in DESCENDING event_index order
  (observed on the USDT0 OFT transaction b49b0157..., 5 events: 4,3,2,1,0).
- java-tron node API (``/wallet``, ``/walletsolidity``): bodies end with a newline;
  ``gettransactioninfobyid`` uses ``", "``-less item separators and ``": "`` key separators
  (``{"id": "...","fee": 345000,...}``); ``gettransactionbyid`` is compact.
- A transaction id is sha256 of the protobuf-encoded ``raw_data`` (checked in tests
  against the real theft transaction 98f3ffca...), so synthetic ids are self-consistent.

What is NOT copied from a live sample is marked "assumption" in the docstrings: the
receipt of a failed transaction, the order of keys inside TronGrid v1 TriggerSmartContract
rows, and every error body (error bodies are plain text that says they are synthetic).
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

from ..core.evm import event_topic, keccak256
from ..core.tron import USDT_TRC20, b58_to_bytes, b58_to_evm_hex, b58_to_hex

TYPE_URL_PREFIX = "type.googleapis.com/protocol."
CONTRACT_TYPE_IDS = {"TransferContract": 1, "TriggerSmartContract": 31}
USDT_TOKEN_INFO = {"symbol": "USDT", "address": USDT_TRC20, "decimals": 6, "name": "Tether USD"}

# Real infrastructure contracts seen in the case-001 USDT0 send (b49b0157...). Synthetic
# scenarios reuse these public contract addresses; every EOA, txid and guid is synthetic.
USDT0_OFT_TRON_HEX = "413a08f76772e200653bb55c2a92998daca62e0e97"  # TFG4wB... (UsdtOFT)
LZ_ENDPOINT_TRON_HEX = "410af59750d5db5460e5d89e268c474d5f7407c061"  # TAy9xw... (PacketSent)
LZ_SENDLIB_TRON_HEX = "41e369d146219380b24bb5d9b9e08a5b9936f9e719"  # TWhf9v... (fee events)
USDT0_OFT_ETH_ADAPTER = "0x1f748c76de468e9d11bd340fa9d5cbadf315dfb0"  # receiver of TRON->ETH packets
LZ_EXECUTOR = "0x67de40af19c0c0a6d0278d96911889faf4ebc1bc"
LZ_DVNS = ["0x8bc1d368036ee5e726d230beb685294be191a24e", "0xe13b0667fce48d12773ead95d87dc9d1c58544df"]
TRON_EID = 30420

SIG_TRANSFER = "Transfer(address indexed from, address indexed to, uint256 value)"
SIG_APPROVAL = "Approval(address indexed owner, address indexed spender, uint256 value)"
SIG_OFTSENT = ("OFTSent(bytes32 indexed guid, uint32 dstEid, address indexed fromAddress, "
               "uint256 amountSentLD, uint256 amountReceivedLD)")
SIG_PACKETSENT = "PacketSent(bytes encodedPayload, bytes options, address sendLibrary)"
SIG_EXECUTORFEE = "ExecutorFeePaid(address executor, uint256 fee)"
SIG_DVNFEE = "DVNFeePaid(address[] requiredDVNs, address[] optionalDVNs, uint256[] fees)"


def topic(signature: str) -> str:
    """topic0 without 0x for a human-readable event signature (indexed/names stripped)."""
    name, rest = signature.split("(", 1)
    types = [p.strip().split(" ")[0] for p in rest.rstrip(")").split(",") if p.strip()]
    return event_topic(f"{name}({','.join(types)})")[2:]


SELECTOR_TRANSFER = "a9059cbb"  # transfer(address,uint256)
SELECTOR_TRANSFER_FROM = "23b872dd"  # transferFrom(address,address,uint256)
SELECTOR_APPROVE = "095ea7b3"  # approve(address,uint256)
SELECTOR_BALANCE_OF = "70a08231"  # balanceOf(address)
SELECTOR_OFT_SEND = "c7c7f5b3"  # send((uint32,bytes32,uint256,uint256,bytes,bytes,bytes),(uint256,uint256),address)
SELECTOR_BATCH = "c1a38006"  # synthetic batch-sender selector (synthetic contract; not a real ABI)


# ---------------------------------------------------------------- JSON text


def compact(obj: Any) -> str:
    return json.dumps(obj, separators=(",", ":"), ensure_ascii=False)


def java_tron(obj: Any) -> str:
    """java-tron JsonFormat style seen in gettransactioninfobyid/getaccount: '","' and '": "'."""
    return json.dumps(obj, separators=(",", ": "), ensure_ascii=False)


# ---------------------------------------------------------------- protobuf


def _varint(n: int) -> bytes:
    if n < 0:
        n &= (1 << 64) - 1
    out = bytearray()
    while True:
        b = n & 0x7F
        n >>= 7
        if n:
            out.append(b | 0x80)
        else:
            out.append(b)
            return bytes(out)


def _pb_len(field: int, payload: bytes) -> bytes:
    if not payload:
        return b""
    return _varint((field << 3) | 2) + _varint(len(payload)) + payload


def _pb_int(field: int, n: int | None) -> bytes:
    if not n:
        return b""
    return _varint(field << 3) + _varint(int(n))


def _addr_bytes(addr: str) -> bytes:
    return b58_to_bytes(addr) if addr.startswith("T") else bytes.fromhex(addr)


def encode_contract_value(ctype: str, value: dict[str, Any]) -> bytes:
    if ctype == "TriggerSmartContract":
        return (_pb_len(1, _addr_bytes(value["owner_address"]))
                + _pb_len(2, _addr_bytes(value["contract_address"]))
                + _pb_int(3, value.get("call_value"))
                + _pb_len(4, bytes.fromhex(value.get("data", ""))))
    if ctype == "TransferContract":
        return (_pb_len(1, _addr_bytes(value["owner_address"]))
                + _pb_len(2, _addr_bytes(value["to_address"]))
                + _pb_int(3, value.get("amount")))
    raise ValueError(f"unsupported contract type {ctype}")


def encode_raw_data(raw: dict[str, Any]) -> bytes:
    """Protobuf ``Transaction.raw`` from a node-style raw_data dict (visible=True or hex addresses)."""
    out = _pb_len(1, bytes.fromhex(raw["ref_block_bytes"]))
    out += _pb_len(4, bytes.fromhex(raw["ref_block_hash"]))
    out += _pb_int(8, raw.get("expiration"))
    for c in raw["contract"]:
        ctype = c["type"]
        any_msg = _pb_len(1, (TYPE_URL_PREFIX + ctype).encode()) + _pb_len(
            2, encode_contract_value(ctype, c["parameter"]["value"]))
        contract = _pb_int(1, CONTRACT_TYPE_IDS[ctype]) + _pb_len(2, any_msg)
        out += _pb_len(11, contract)
    out += _pb_int(14, raw.get("timestamp"))
    out += _pb_int(18, raw.get("fee_limit"))
    return out


def txid_of(raw_bytes: bytes) -> str:
    return hashlib.sha256(raw_bytes).hexdigest()


# ---------------------------------------------------------------- ABI helpers


def word(n: int) -> str:
    return f"{n:064x}"


def addr_word(addr: str) -> str:
    """TRON base58 or 0x EVM address -> 32-byte ABI word (hex, no 0x)."""
    if addr.startswith("T"):
        return b58_to_evm_hex(addr)[2:].rjust(64, "0")
    return addr.lower().removeprefix("0x").rjust(64, "0")


def evm(addr: str) -> str:
    """TRON base58 -> 0x + 40 hex (the form used in TronGrid decoded event results)."""
    return b58_to_evm_hex(addr)


def oft_guid(nonce: int, src_eid: int, sender_word: str, dst_eid: int, receiver_word: str) -> str:
    """LayerZero V2 guid = keccak256(nonce u64 | srcEid u32 | sender b32 | dstEid u32 | receiver b32)."""
    packed = (nonce.to_bytes(8, "big") + src_eid.to_bytes(4, "big") + bytes.fromhex(sender_word)
              + dst_eid.to_bytes(4, "big") + bytes.fromhex(receiver_word))
    return keccak256(packed).hex()


def oft_message(recipient_evm: str, amount_sd: int) -> str:
    """OFT compose-less message as observed in the real packet: 0002 | sendTo b32 | amountSD u64."""
    return "0002" + addr_word(recipient_evm) + f"{amount_sd:016x}"


def packet_encoded(nonce: int, src_eid: int, sender_word: str, dst_eid: int, receiver_word: str,
                   guid: str, message: str) -> str:
    return ("01" + f"{nonce:016x}" + f"{src_eid:08x}" + sender_word + f"{dst_eid:08x}" + receiver_word
            + guid + message)


# ---------------------------------------------------------------- node API bodies


def raw_data_dict(tx: dict[str, Any], *, visible: bool = True) -> dict[str, Any]:
    """Node-style raw_data (key order as in the live gettransactionbyid sample)."""
    conv = (lambda a: a) if visible else (lambda a: b58_to_hex(a))
    if tx["ctype"] == "TriggerSmartContract":
        value: dict[str, Any] = {"owner_address": conv(tx["owner"]), "contract_address": conv(tx["contract"])}
        if tx.get("call_value"):
            value["call_value"] = tx["call_value"]
        value["data"] = tx["data"]
    else:
        value = {"owner_address": conv(tx["owner"]), "to_address": conv(tx["to"]), "amount": tx["amount"]}
    raw: dict[str, Any] = {
        "ref_block_bytes": tx["ref_block_bytes"],
        "ref_block_hash": tx["ref_block_hash"],
        "expiration": tx["expiration"],
        "contract": [{"parameter": {"value": value, "type_url": TYPE_URL_PREFIX + tx["ctype"]},
                      "type": tx["ctype"]}],
        "timestamp": tx["created_ms"],
    }
    if tx.get("fee_limit"):
        raw["fee_limit"] = tx["fee_limit"]
    return raw


def node_transaction(tx: dict[str, Any], *, visible: bool = True) -> bytes:
    body = {
        "raw_data": raw_data_dict(tx, visible=visible),
        "signature": [tx["signature"]],
        "ret": [{"contractRet": tx["status"]}],
        "raw_data_hex": tx["raw_data_hex"],
        "txID": tx["txid"],
    }
    return (compact(body) + "\n").encode()


def receipt_log(ev: dict[str, Any]) -> dict[str, Any]:
    """Receipt log entry (hex, no 0x) for one event."""
    name, a = ev["name"], ev["args"]
    contract_hex = b58_to_hex(ev["contract"])[2:]
    if name == "Transfer":
        return {"address": contract_hex,
                "topics": [topic(SIG_TRANSFER), addr_word(a["from"]), addr_word(a["to"])],
                "data": word(int(a["value"]))}
    if name == "Approval":
        return {"address": contract_hex,
                "topics": [topic(SIG_APPROVAL), addr_word(a["owner"]), addr_word(a["spender"])],
                "data": word(int(a["value"]))}
    if name == "ExecutorFeePaid":
        return {"address": contract_hex, "topics": [topic(SIG_EXECUTORFEE)],
                "data": addr_word(a["executor"]) + word(int(a["fee"]))}
    if name == "DVNFeePaid":
        dvns, fees = a["requiredDVNs"], [int(f) for f in a["fees"]]
        data = word(0x60) + word(0x60 + 32 * (len(dvns) + 1)) + word(0x60 + 32 * (len(dvns) + 2))
        data += word(len(dvns)) + "".join(addr_word(d) for d in dvns)
        data += word(0) + word(len(fees)) + "".join(word(f) for f in fees)
        return {"address": contract_hex, "topics": [topic(SIG_DVNFEE)], "data": data}
    if name == "PacketSent":
        payload, options = a["encodedPayload"], a["options"]
        p_len, o_len = len(payload) // 2, len(options) // 2
        p_pad = payload + "0" * ((-len(payload)) % 64)
        o_pad = options + "0" * ((-len(options)) % 64)
        data = word(0x60) + word(0x60 + 32 + len(p_pad) // 2) + addr_word(a["sendLibrary"])
        data += word(p_len) + p_pad + word(o_len) + o_pad
        return {"address": contract_hex, "topics": [topic(SIG_PACKETSENT)], "data": data}
    if name == "OFTSent":
        return {"address": contract_hex,
                "topics": [topic(SIG_OFTSENT), a["guid"], addr_word(a["fromAddress"])],
                "data": word(int(a["dstEid"])) + word(int(a["amountSentLD"])) + word(int(a["amountReceivedLD"]))}
    raise ValueError(f"no log encoder for {name}")


def node_transaction_info(tx: dict[str, Any]) -> bytes:
    """gettransactioninfobyid body. Failed-transaction fields (result/resMessage) are an assumption
    from the java-tron TransactionInfo message, not copied from a live sample."""
    info: dict[str, Any] = {"id": tx["txid"]}
    if tx.get("fee"):
        info["fee"] = tx["fee"]
    info["blockNumber"] = tx["block"]
    info["blockTimeStamp"] = tx["ts_ms"]
    if tx["ctype"] == "TransferContract":
        info["contractResult"] = [""]
        info["receipt"] = {"net_usage": tx.get("net_usage", 268)}
        return (java_tron(info) + "\n").encode()
    info["contractResult"] = tx.get("contract_result") or [""]
    info["contract_address"] = b58_to_hex(tx["contract"])
    info["receipt"] = dict(tx["receipt"])
    logs = [receipt_log(ev) for ev in tx["events"]]
    if logs:
        info["log"] = logs
    if tx["status"] != "SUCCESS":
        info["result"] = "FAILED"
        info["resMessage"] = tx.get("res_message", "")
    if tx.get("internal_transactions"):
        info["internal_transactions"] = tx["internal_transactions"]
    return (java_tron(info) + "\n").encode()


def node_empty() -> bytes:
    return b"{}\n"


def trigger_balance_of(owner: str, balance: int, *, ref_block_bytes: str, ref_block_hash: str,
                       expiration: int, created_ms: int) -> bytes:
    """triggerconstantcontract balanceOf(owner) body (shape of the live sample 7305239981ea...)."""
    data = SELECTOR_BALANCE_OF + addr_word(owner)
    raw = {
        "ref_block_bytes": ref_block_bytes,
        "ref_block_hash": ref_block_hash,
        "expiration": expiration,
        "contract": [{"parameter": {"value": {"owner_address": owner, "contract_address": USDT_TRC20,
                                              "data": data},
                                    "type_url": TYPE_URL_PREFIX + "TriggerSmartContract"},
                      "type": "TriggerSmartContract"}],
        "timestamp": created_ms,
    }
    raw_hex = encode_raw_data(raw).hex()
    body = {
        "transaction": {"raw_data": raw, "ret": [{}], "raw_data_hex": raw_hex, "txID": txid_of(bytes.fromhex(raw_hex)),
                        "visible": True},
        "constant_result": [word(balance)],
        "result": {"result": True},
        "energy_used": 4062,
        "energy_penalty": 3127,
    }
    return (compact(body) + "\n").encode()


# ---------------------------------------------------------------- TronGrid v1 bodies


def v1_trc20_row(tx: dict[str, Any], ev: dict[str, Any]) -> dict[str, Any]:
    a = ev["args"]
    if ev["name"] == "Transfer":
        frm, to, typ = a["from"], a["to"], "Transfer"
    else:
        frm, to, typ = a["owner"], a["spender"], "Approval"
    return {"transaction_id": tx["txid"], "token_info": dict(USDT_TOKEN_INFO), "block_timestamp": tx["ts_ms"],
            "from": frm, "to": to, "type": typ, "value": str(int(a["value"]))}


def v1_account_tx_row(tx: dict[str, Any]) -> dict[str, Any]:
    """Row of /v1/accounts/{addr}/transactions. Assumption: key order inside the
    TriggerSmartContract value (data, owner_address, contract_address[, call_value])."""
    if tx["ctype"] == "TriggerSmartContract":
        value: dict[str, Any] = {"data": tx["data"], "owner_address": b58_to_hex(tx["owner"]),
                                 "contract_address": b58_to_hex(tx["contract"])}
        if tx.get("call_value"):
            value["call_value"] = tx["call_value"]
    else:
        value = {"amount": tx["amount"], "owner_address": b58_to_hex(tx["owner"]), "to_address": b58_to_hex(tx["to"])}
    raw: dict[str, Any] = {
        "contract": [{"parameter": {"value": value, "type_url": TYPE_URL_PREFIX + tx["ctype"]}, "type": tx["ctype"]}],
        "ref_block_bytes": tx["ref_block_bytes"],
        "ref_block_hash": tx["ref_block_hash"],
        "expiration": tx["expiration"],
    }
    if tx.get("fee_limit"):
        raw["fee_limit"] = tx["fee_limit"]
    raw["timestamp"] = tx["created_ms"]
    rec = tx.get("receipt") or {}
    return {
        "ret": [{"contractRet": tx["status"], "fee": tx.get("fee", 0)}],
        "signature": [tx["signature"]],
        "txID": tx["txid"],
        "net_usage": tx.get("net_usage", 0) if tx["ctype"] == "TransferContract" else rec.get("net_usage", 0),
        "raw_data_hex": tx["raw_data_hex"],
        "net_fee": rec.get("net_fee", 0),
        "energy_usage": rec.get("energy_usage", 0),
        "blockNumber": tx["block"],
        "block_timestamp": tx["ts_ms"],
        "energy_fee": rec.get("energy_fee", 0),
        "energy_usage_total": rec.get("energy_usage_total", 0),
        "raw_data": raw,
        "internal_transactions": [],
    }


def v1_event_row(tx: dict[str, Any], ev: dict[str, Any]) -> dict[str, Any]:
    """Decoded event row as returned by /v1/transactions/{txid}/events (live sample shapes)."""
    name, a = ev["name"], ev["args"]
    if name == "Transfer":
        f, t, v = evm(a["from"]), evm(a["to"]), str(int(a["value"]))
        result = {"0": f, "1": t, "2": v, "from": f, "to": t, "value": v}
        rtype = {"from": "address", "to": "address", "value": "uint256"}
        sig = SIG_TRANSFER
    elif name == "Approval":
        o, s, v = evm(a["owner"]), evm(a["spender"]), str(int(a["value"]))
        result = {"0": o, "1": s, "2": v, "owner": o, "spender": s, "value": v}
        rtype = {"owner": "address", "spender": "address", "value": "uint256"}
        sig = SIG_APPROVAL
    elif name == "OFTSent":
        g, d, fa = a["guid"], str(int(a["dstEid"])), evm(a["fromAddress"])
        s, r = str(int(a["amountSentLD"])), str(int(a["amountReceivedLD"]))
        result = {"0": g, "1": d, "2": fa, "3": s, "4": r, "dstEid": d, "guid": g, "fromAddress": fa,
                  "amountSentLD": s, "amountReceivedLD": r}
        rtype = {"dstEid": "uint32", "guid": "bytes32", "fromAddress": "address", "amountSentLD": "uint256",
                 "amountReceivedLD": "uint256"}
        sig = SIG_OFTSENT
    elif name == "PacketSent":
        sl = a["sendLibrary"].lower()
        result = {"0": a["encodedPayload"], "sendLibrary": sl, "1": a["options"], "2": sl,
                  "encodedPayload": a["encodedPayload"], "options": a["options"]}
        rtype = {"sendLibrary": "address", "encodedPayload": "bytes", "options": "bytes"}
        sig = SIG_PACKETSENT
    elif name == "DVNFeePaid":
        dv = "\n".join(a["requiredDVNs"])
        fees = "\n".join(str(int(x)) for x in a["fees"])
        result = {"0": dv, "1": "", "requiredDVNs": dv, "optionalDVNs": "", "2": fees, "fees": fees}
        rtype = {"requiredDVNs": "address[]", "optionalDVNs": "address[]", "fees": "uint256[]"}
        sig = SIG_DVNFEE
    elif name == "ExecutorFeePaid":
        ex, fee = a["executor"].lower(), str(int(a["fee"]))
        result = {"0": ex, "1": fee, "executor": ex, "fee": fee}
        rtype = {"executor": "address", "fee": "uint256"}
        sig = SIG_EXECUTORFEE
    else:
        raise ValueError(f"no event row for {name}")
    return {
        "block_number": tx["block"],
        "block_timestamp": tx["ts_ms"],
        "caller_contract_address": ev["contract"],
        "contract_address": ev["contract"],
        "event_index": ev["index"],
        "event_name": name,
        "result": result,
        "result_type": rtype,
        "event": sig,
        "transaction_id": tx["txid"],
    }


def v1_page(rows: list[Any], at_ms: int, *, fingerprint: str | None = None, next_url: str | None = None) -> bytes:
    meta: dict[str, Any] = {"at": at_ms}
    if fingerprint:
        meta["fingerprint"] = fingerprint
        meta["links"] = {"next": next_url}
    meta["page_size"] = len(rows)
    return compact({"data": rows, "success": True, "meta": meta}).encode()


# ---------------------------------------------------------------- LayerZero Scan bodies


LZ_RECEIVE_LIBRARY = "0xc02Ab410f0734EFa3F14628780e6e695156024C2"
LZ_SEND_LIBRARY = "0xE369D146219380B24Bb5D9B9E08a5b9936F9E719"
LZ_INBOUND_DVNS = ["0x3b0531eb02ab4ad72e7a531180beef9493a00dd2", "0x589dedbd617e0cbcb916a9223f4d1300c294236b"]
LZ_INBOUND_DVN_NAMES = ["USDT0", "LayerZero Labs"]
LZ_OUTBOUND_DVN_NAMES = ["LayerZero Labs", "USDT0"]
LZ_EXECUTOR_CHECKSUM = "0x67DE40af19C0C0a6D0278d96911889fAF4EBc1Bc"


def lz_payload_hash(guid: str, message: str) -> str:
    """keccak256(guid | message): matches the payloadHash of the live case-001 message."""
    return "0x" + keccak256(bytes.fromhex(guid + message)).hex()


def lz_message(msg: dict[str, Any]) -> dict[str, Any]:
    """One /v1/messages/* item with the same structure as the live case-001 message.

    Config, DVN and executor addresses are the real USDT0 TRON->Ethereum pathway values from
    that message; tx hashes, blocks, nonces and guids are synthetic."""
    delivered = msg["status"] == "DELIVERED"
    sender_word = USDT0_OFT_TRON_HEX[2:].rjust(64, "0")
    receiver = msg["dst_oapp"]
    header = ("0x01" + f"{msg['nonce']:016x}" + f"{TRON_EID:08x}" + sender_word + f"{msg['dst_eid']:08x}"
              + receiver[2:].rjust(64, "0"))
    dst: dict[str, Any] = {"nativeDrop": {"status": "N/A"}, "lzCompose": {"status": "N/A"}}
    if delivered:
        dst["tx"] = {"txHash": msg["dst_txid"], "blockHash": msg["dst_block_hash"], "blockNumber": msg["dst_block"],
                     "blockTimestamp": msg["dst_ts"]}
        dst["status"] = "SUCCEEDED"
    else:
        dst["status"] = "WAITING"
    dvns = {}
    for i, dvn in enumerate(LZ_INBOUND_DVNS):
        dvns[dvn] = {"txHash": msg["verify_txids"][i], "blockHash": msg["verify_block_hash"],
                     "blockNumber": msg["verify_block"], "blockTimestamp": msg["verify_ts"],
                     "proof": {"packetHeader": header, "payloadHash": lz_payload_hash(msg["guid"], msg["message"])},
                     "optional": False, "status": "SUCCEEDED"}
    dvn_cfg = {"confirmations": 5, "requiredDVNCount": 2, "optionalDVNCount": 0, "optionalDVNThreshold": 0}
    return {
        "pathway": {
            "srcEid": TRON_EID,
            "dstEid": msg["dst_eid"],
            "sender": {"address": "0x" + USDT0_OFT_TRON_HEX[2:], "id": "usdt0", "name": "USDT0", "chain": "tron"},
            "receiver": {"address": receiver, "id": "usdt0", "name": "USDT0", "chain": msg["dst_chain"]},
            "id": f"{TRON_EID}-{msg['dst_eid']}-0x{USDT0_OFT_TRON_HEX[2:]}-{receiver}",
            "nonce": msg["nonce"],
        },
        "source": {
            "status": "SUCCEEDED",
            "tx": {"txHash": "0x" + msg["src_txid"], "blockHash": msg["src_block_hash"], "blockNumber": str(msg["src_block"]),
                   "blockTimestamp": msg["src_ts"], "from": msg["src_from"],
                   "payload": "0x" + msg["message"], "readinessTimestamp": msg["src_ts"] + 15,
                   "options": {"lzReceive": {"gas": "100000", "value": "0"}, "ordered": False}},
        },
        "destination": dst,
        "verification": {
            "dvn": {"dvns": dvns, "status": "SUCCEEDED"},
            "sealer": {"tx": {"txHash": msg["sealer_txid"], "blockHash": msg["sealer_block_hash"],
                              "blockNumber": msg["sealer_block"], "blockTimestamp": msg["sealer_ts"]},
                       "status": "SUCCEEDED"},
        },
        "guid": "0x" + msg["guid"],
        "config": {
            "error": False,
            "receiveLibrary": LZ_RECEIVE_LIBRARY,
            "sendLibrary": LZ_SEND_LIBRARY,
            "inboundConfig": {**dvn_cfg, "requiredDVNs": list(LZ_INBOUND_DVNS), "requiredDVNNames": LZ_INBOUND_DVN_NAMES,
                              "optionalDVNs": [], "optionalDVNNames": []},
            "outboundConfig": {**dvn_cfg, "requiredDVNs": list(LZ_DVNS), "requiredDVNNames": LZ_OUTBOUND_DVN_NAMES,
                               "optionalDVNs": [], "optionalDVNNames": [], "executor": LZ_EXECUTOR_CHECKSUM},
            "ulnSendVersion": "V302",
            "ulnReceiveVersion": "V302",
        },
        "status": {"name": msg["status"],
                   "message": "Executor transaction confirmed" if delivered else "Waiting for verification"},
        "created": msg["created"],
        "updated": msg["updated"],
    }


def lz_found(msg: dict[str, Any]) -> bytes:
    return compact({"data": [lz_message(msg)]}).encode()


def lz_not_found(tx_hash: str) -> bytes:
    """Same text as the live 404 (case-001, hash requested without 0x)."""
    return compact({"message": f"Message not found for tx {tx_hash}!", "code": 4040}).encode()


# ---------------------------------------------------------------- errors


def synthetic_error(status: int, what: str) -> bytes:
    """Error bodies are deliberately labelled synthetic: the real providers' error bodies were not sampled."""
    return f"HTTP {status}: synthetic {what} (ledgerhunt scenario generator)\n".encode()
