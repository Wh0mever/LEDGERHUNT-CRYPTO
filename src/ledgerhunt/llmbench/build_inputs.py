"""Build the frozen inputs of the case-001 decision-point tasks.

Sources (public blockchain data only):
- tests/fixtures/case-001/case-001-ground-truth.json (transactions, roles, links)
- raw responses recorded by the foundation probes in data/http-store (pinned by body sha256)

The analyst conclusions of the fixture (notes, roles, "kind" labels that give away the answer) are NOT
copied into the inputs; only observable data is. The result is written to
src/ledgerhunt/llmbench/data/decision_inputs.json and loaded at benchmark time, so the benchmark does
not depend on the http-store being present.

    python -m ledgerhunt.llmbench.build_inputs [--check]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

from ..core.paths import repo_root

FIXTURE = Path("tests/fixtures/case-001/case-001-ground-truth.json")
STORE = Path("data/http-store")
OUT = Path(__file__).with_name("data") / "decision_inputs.json"

# Raw bodies used (sha256 of the stored response body).
RAW = {
    "theft_gettransactionbyid": "1f5541ab49f7",
    "theft_gettransactioninfobyid": "77e27374c371",
    "layerzero_message_b49b": "9ac53c71e4ef",
    "eth_receipt_8ea2": "f461e80341eb",
    "blockscout_tx_41bac": "c44ac21ad801",
    "blockscout_logs_41bac": "541844f572e2",
    "oneclick_status_da39": "d25bf5a7a499",
    "tvnma2_getaccount": "656ffbb9b5c9",
}


def _store_body(prefix: str, root: Path) -> tuple[str, dict[str, Any]]:
    matches = sorted((root / "objects" / prefix[:2]).glob(prefix + "*"))
    if len(matches) != 1:
        raise FileNotFoundError(f"raw body {prefix}* not found (or ambiguous) in {root}")
    data = matches[0].read_bytes()
    return hashlib.sha256(data).hexdigest(), json.loads(data)


def _sub(a: str, b: str) -> str:
    """Exact difference of two 6-decimal amounts as a 6-decimal string."""
    from decimal import Decimal

    return format(Decimal(a) - Decimal(b), "f")


def _tx(step: dict[str, Any], *, with_block: bool = False) -> dict[str, Any]:
    row = {
        "txid": step["txid"],
        "time_utc": step["timestamp_utc"].replace(" ", "T") + "Z",
        "from": step["from"],
        "to": step["to"],
        "amount": step["amount"],
        "asset": step["asset"],
    }
    if with_block and step.get("block"):
        row["block"] = step["block"]
    return row


def build(root: Path | None = None) -> dict[str, Any]:
    root = root or repo_root()
    fx = json.loads((root / FIXTURE).read_text(encoding="utf-8"))
    steps = {s["step"]: s for s in fx["transactions"]}
    links = fx["links"][0]
    store = root / STORE
    provenance: dict[str, str] = {}
    raw: dict[str, Any] = {}
    for name, prefix in RAW.items():
        sha, body = _store_body(prefix, store)
        provenance[name] = sha
        raw[name] = body

    V = fx["victim"]["address"]
    fixture_src = "case-001 fixture (TronGrid TRC20 history, parsed)"
    eth_src = "case-001 fixture (Blockscout ERC-20 token transfers, parsed)"

    # ---------------------------------------------------------------- D1 mechanism
    d1 = {
        "victim_address": V,
        "victim_statement": {
            "provenance": "claimed by victim",
            "text": "I did not make or approve this transfer. The money left my wallet less than a minute after a large incoming payment arrived.",
        },
        "account_permissions": {
            "source": "case-001 fixture (account permission summary)",
            "owner_permission": {"threshold": 1, "keys": [V]},
            "active_permission": {"threshold": 1, "keys": [V]},
            "account_permission_update_transactions_found": 0,
        },
        "theft_transaction_raw": {"source": "TronGrid POST /wallet/gettransactionbyid", "body": raw["theft_gettransactionbyid"]},
        "theft_transaction_info_raw": {"source": "TronGrid POST /walletsolidity/gettransactioninfobyid", "body": raw["theft_gettransactioninfobyid"]},
        "victim_address_timeline": {
            "source": fixture_src,
            "rows": [
                {**_tx(steps[2]), "event": "incoming USDT transfer"},
                {**_tx(steps[1]), "event": "incoming USDT transfer"},
                {"txid": steps[3]["txid"], "time_utc": "2026-09-21T11:32:36Z", "from": steps[3]["from"], "to": V,
                 "event": "energy delegated to the victim address", "amount": "20424 TRX staked for energy"},
                {**_tx(steps[4]), "amount": "0.800000", "event": "incoming TRX transfer"},
                {**_tx(steps[5]), "event": "outgoing USDT transfer"},
                {**_tx(steps[6], with_block=True), "event": "outgoing USDT transfer"},
            ],
        },
    }

    # ---------------------------------------------------------------- D2 99%/1% split
    tyn = steps[8]["to"]
    funder = links["funder"]
    funded = {f["addr"]: f for f in links["funded"]}
    d2 = {
        "address_under_review": tyn,
        "incoming": [{**_tx(steps[8])}],
        "outgoing_usdt_after_arrival": [_tx(steps[9]), _tx(steps[10])],
        "usdt_balance_now": "0.000000",
        "trx_received_for_fees": {"from": funder, "txids": funded[tyn]["txids"]},
        "earlier_history_of_recipients": [
            {"address": steps[10]["to"],
             "observation": "received a transfer of exactly 1% of the forwarded amount in two earlier flows with the same route (2026-08-26 and 2026-08-30)"},
            {"address": steps[9]["to"], "observation": "address active since 2026-08-26; received the 99% part in those earlier flows"},
        ],
        "source": fixture_src,
    }

    # ---------------------------------------------------------------- D3 USDT0 bridge exit
    turq = steps[9]["to"]
    lz = raw["layerzero_message_b49b"]["data"][0]
    lz_trim = {
        "guid": lz["guid"],
        "pathway": {"srcEid": lz["pathway"]["srcEid"], "dstEid": lz["pathway"]["dstEid"],
                    "sender": lz["pathway"]["sender"], "receiver": lz["pathway"]["receiver"]},
        "source": {"status": lz["source"]["status"],
                   "tx": {k: lz["source"]["tx"][k] for k in ("txHash", "blockNumber", "blockTimestamp", "from", "payload")}},
        "destination": {"status": lz["destination"]["status"],
                        "tx": {k: lz["destination"]["tx"][k] for k in ("txHash", "blockNumber", "blockTimestamp")}},
        "status": lz["status"],
        "created": lz["created"],
        "updated": lz["updated"],
    }
    receipt = raw["eth_receipt_8ea2"]["result"]
    d3 = {
        "address_under_review": turq,
        "trc20_activity": {
            "source": fixture_src,
            "rows": [
                {**_tx(steps[9]), "direction": "in"},
                {"txid": steps[11]["txid"], "time_utc": "2026-09-21T11:50:54Z", "owner": turq, "spender": steps[11]["to"],
                 "allowance": steps[11]["amount"], "asset": "USDT-TRC20", "event": "Approval"},
                {**_tx(steps[12], with_block=True), "direction": "out"},
                {**_tx(steps[13]), "direction": "out"},
            ],
        },
        "layerzero_scan_message": {"source": "LayerZero Scan GET /v1/messages/tx/{source tx hash}", "body": lz_trim},
        "ethereum_receipt_logs": {
            "source": "Ethereum JSON-RPC eth_getTransactionReceipt",
            "transactionHash": receipt["logs"][0]["transactionHash"],
            "blockNumber": receipt["blockNumber"],
            "status": receipt.get("status"),
            "logs": [{k: lg[k] for k in ("address", "topics", "data", "logIndex")} for lg in receipt["logs"][:2]],
            "note": "log 1 is emitted by the Ethereum USDT0 OFT adapter (OFTReceived: guid, srcEid, toAddress, amountReceivedLD)",
        },
    }

    # ---------------------------------------------------------------- D4 Rango log
    btx = raw["blockscout_tx_41bac"]
    logs = raw["blockscout_logs_41bac"]["items"]

    def trim_log(it: dict[str, Any]) -> dict[str, Any]:
        dec = it.get("decoded") or {}
        return {
            "index": it.get("index"),
            "address": it["address"]["hash"],
            "address_name": it["address"].get("name"),
            "event": dec.get("method_call"),
            "topics": [t for t in it.get("topics", []) if t],
            "data": it.get("data"),
            "decoded_parameters": [{"name": p.get("name"), "type": p.get("type"), "value": p.get("value")}
                                   for p in dec.get("parameters", [])],
        }

    d4 = {
        "transaction": {
            "source": "Blockscout GET /api/v2/transactions/{hash}",
            "hash": btx.get("hash"),
            "block_number": btx.get("block_number") or btx.get("block"),
            "timestamp": btx.get("timestamp"),
            "status": btx.get("status"),
            "from": (btx.get("from") or {}).get("hash"),
            "to": (btx.get("to") or {}).get("hash"),
            "to_name": (btx.get("to") or {}).get("name"),
            "method": btx.get("method"),
        },
        "logs": {"source": "Blockscout GET /api/v2/transactions/{hash}/logs", "items": [trim_log(it) for it in logs]},
    }

    # ---------------------------------------------------------------- D5 NEAR Intents
    s16, s17 = steps[16], steps[17]
    d5 = {
        "previous_step_result": {
            "from_rango_log": "funds forwarded to 0xdA392553ec3602D3e650a725f847C10d04E122C0; receiver field of the Rango event decodes to the ASCII text TYHeH2HQn7pM5fe6aYwG (20 characters)",
        },
        "erc20_transfers_of_forwarded_address": {
            "source": eth_src,
            "address": s16["from"],
            "rows": [
                {"txid": steps[15]["txid"], "time_utc": "2026-09-21T11:56:35Z", "from": "0x69460570c93f9DE5E2edbC3052bf10125f0Ca22d",
                 "to": s16["from"], "amount": steps[15]["rango"]["forwarded_amount"], "asset": "USDT-ERC20", "direction": "in"},
                {**_tx(s16), "direction": "out"},
            ],
        },
        "oneclick_status": {"source": "NEAR Intents 1Click GET /v0/status?depositAddress=" + s16["from"], "body": raw["oneclick_status_da39"]},
        "tron_trc20_transfer": {"source": fixture_src, "row": _tx(s17, with_block=True)},
    }

    # ---------------------------------------------------------------- D6 hub
    hub = s17["to"]
    hub_addr = next(a for a in fx["addresses"] if a["address"] == hub)
    d6 = {
        "address_under_review": hub,
        "arrival_of_traced_funds": {**_tx(s17, with_block=True),
                                    "route_before": "victim -> 3 TRON hops -> USDT0 bridge to Ethereum -> Rango -> NEAR Intents 1Click -> this address"},
        "traced_amount": s17["amount"],
        "account_facts": {
            "activated_utc": "2026-08-06T17:47:57Z",
            "activated_by": funder,
            "usdt_balance": {"amount": hub_addr["balance_usdt"].split(" ")[0], "as_of_utc": "2026-10-14T09:00:00Z (approximately)"},
        },
        "usdt_outflows_after_arrival": {
            "source": fixture_src,
            "note": "first outflows after the traced funds arrived; the address has much more USDT activity that is not listed",
            "rows": [_tx(steps[n]) for n in (18, 20, 21, 22)],
        },
    }

    # ---------------------------------------------------------------- D7 exchange deposit heuristic
    d7 = {
        "candidates": [
            {"address": steps[18]["to"], "incoming": [_tx(steps[18])], "outgoing": [_tx(steps[19])]},
            {"address": steps[22]["to"], "incoming": [_tx(steps[22])], "outgoing": [_tx(steps[23])]},
            {"address": steps[20]["to"], "incoming": [_tx(steps[20])], "outgoing": "not fetched"},
            {"address": steps[21]["to"], "incoming": [_tx(steps[21])], "outgoing": "not fetched"},
        ],
        "address_tags": [{"address": steps[19]["to"], "tag": "WhiteBIT", "source": "third-party block explorer tag (TronScan addressTag)"}],
        "context": "all four candidates received USDT from " + hub + ", an address where the traced stolen funds were mixed with other funds",
        "source": fixture_src,
    }

    # ---------------------------------------------------------------- D8 common funder
    up = links["funder_upstream"]
    d8 = {
        "funder_account_raw": {"source": "TronGrid POST /wallet/getaccount", "body": raw["tvnma2_getaccount"]},
        "trx_transfers_from_funder": [
            {"to": f["addr"], "txids": f["txids"], **({"returned_trx_to_funder_txids": f["returns_trx_to_funder"]} if f.get("returns_trx_to_funder") else {})}
            for f in links["funded"]
        ],
        "activation": {"address": hub, "activated_utc": "2026-08-06T17:47:57Z", "activated_by": funder,
                       "funder_created_utc": "2026-08-06T17:22:48Z"},
        "funder_upstream": [
            {"txid": up["txids"][0].split(" ")[0], "from": "TMGtBUqWevfE2y1XpvzTsHEkLpSDi4bW51", "amount": "918", "asset": "TRX",
             "note": "the sender was itself funded by TSm7vUxW9DvKiwwDRcaR36X8vBjKc99Sxe"},
            {"txid": up["txids"][1].split(" ")[0], "from": "TSm7vUxW9DvKiwwDRcaR36X8vBjKc99Sxe", "amount": "849.68", "asset": "TRX"},
        ],
        "upstream_observation": "TSm7vUxW9DvKiwwDRcaR36X8vBjKc99Sxe is a high-volume USDT payout wallet active since 2024-11, no public label",
        "roles_in_traced_route": {
            steps[8]["to"]: "second hop of the stolen funds",
            steps[9]["to"]: "third hop; sent the funds into the USDT0 bridge",
            hub: "received the stolen funds after the cross-chain round trip",
        },
        "source": "case-001 fixture (TRX transfers, parsed) and raw getaccount",
    }

    # ---------------------------------------------------------------- R1 report facts
    gt = fx["ground_truth"]
    route = [steps[n] for n in (6, 8, 9, 12, 14, 15, 16, 17)]
    report_facts = {
        "case": {"theft_txid": fx["theft"]["txid"], "victim_address": V, "asset": "USDT-TRC20",
                 "amount": fx["theft"]["amount"], "time_utc": "2026-09-21T11:32:39Z", "block": fx["theft"]["block"]},
        "verified_route": [
            {"order": i + 1, **_tx(s, with_block=True), "chain": s["chain"]} for i, s in enumerate(route)
        ],
        "bridge_details": {
            "usdt0_layerzero": {"source_txid": steps[12]["txid"], "srcEid": 30420, "dstEid": 30101,
                                "guid": steps[12]["layerzero"]["guid"], "sent": steps[12]["amount"],
                                "received_on_ethereum": steps[12]["layerzero"]["amountReceivedLD"],
                                "recipient": steps[12]["layerzero"]["sendTo"], "status": "DELIVERED"},
            "rango": {"txid": steps[15]["txid"], "destinationChainId": 1414680398, "destinationChainId_ascii": "TRON",
                      "receiver_bytes_ascii": "TYHeH2HQn7pM5fe6aYwG", "affiliate": steps[15]["rango"]["affiliate"],
                      "affiliate_fee": steps[15]["rango"]["affiliateFee"], "forwarded_to": steps[15]["rango"]["forwarded_to"],
                      "forwarded_amount": steps[15]["rango"]["forwarded_amount"], "dAppName": "MoonGate"},
            "near_intents_1click": {"deposit_address": s16["from"], "status": "SUCCESS",
                                    "recipient": s16["near_intents"]["recipient_tron"],
                                    "destination_txid": s16["near_intents"]["destination_tx"],
                                    "amount_out_reported_by_1click": "12878.410167",
                                    "amount_received_on_chain": s17["amount"]},
        },
        "side_branches": [
            {"to": steps[5]["to"], "txid": steps[5]["txid"], "amount": steps[5]["amount"], "what": "energy-rental fee paid from the victim address in the theft transaction sequence"},
            {"to": steps[7]["to"], "txid": steps[7]["txid"], "amount": steps[7]["amount"], "what": "energy-rental fee paid by the first thief address"},
            {"to": steps[10]["to"], "txid": steps[10]["txid"], "amount": steps[10]["amount"], "what": "exactly 1% of 13035.640112, recurring fee collector"},
            {"to": steps[15]["rango"]["affiliate"], "txid": steps[15]["txid"], "amount": steps[15]["rango"]["affiliateFee"], "what": "Rango affiliate fee (dApp MoonGate)"},
            {"to": steps[13]["to"], "txid": steps[13]["txid"], "amount": steps[13]["amount"], "what": "dust remainder"},
            {"what": "bridge and swap fees",
             "usdt0_fee": _sub(steps[12]["amount"], steps[12]["layerzero"]["amountReceivedLD"]),
             "near_intents_difference": _sub(steps[15]["rango"]["forwarded_amount"], s17["amount"])},
        ],
        "total_lost_between_theft_and_hub": {
            "amount": gt["total_fees_lost_before_hub"],
            "computed_as": f"{fx['theft']['amount']} - {s17['amount']} = {_sub(fx['theft']['amount'], s17['amount'])}",
            "what": "fees, the 1% cut and small residues left on intermediate addresses",
        },
        "hub": {"address": hub, "received": s17["amount"], "commingled": True,
                "usdt_balance": {"amount": hub_addr["balance_usdt"].split(" ")[0], "as_of_utc": "2026-10-14T09:00:00Z (approximately)"},
                "outflows_after_arrival": [_tx(steps[n]) for n in (18, 20, 21, 22)]},
        "exchange_exits": [
            {"deposit_address": steps[18]["to"], "exchange": "WhiteBIT", "evidence": [steps[18]["txid"], steps[19]["txid"]],
             "label_source": "third-party explorer tag of the sweep destination " + steps[19]["to"]},
            {"deposit_address": steps[22]["to"], "exchange": "WhiteBIT", "evidence": [steps[22]["txid"], steps[23]["txid"]],
             "label_source": "third-party explorer tag of the sweep destination " + steps[23]["to"]},
        ],
        "freeze_candidate": {"address": hub, "asset": "USDT-TRC20", "funds": "commingled"},
        "mechanism": {"finding": "the theft transaction and the fee transfer were signed with the victim's own owner key; account permissions were never changed",
                      "interpretation": "consistent with compromise of the seed phrase or private key"},
        "links": [{"type": "common TRX funder", "funder": funder, "funded": [f["addr"] for f in links["funded"]],
                   "status": "hypothesis: probably the same operator", "confidence": "medium-high"}],
        "route_reuse": "the same route (hop -> 99% + exactly 1% -> USDT0 bridge -> 0x4079... -> Rango) was used on 2026-08-26/27 and 2026-08-30/31",
    }

    out = {
        "generated_from": {"fixture": FIXTURE.as_posix(), "fixture_sha256": hashlib.sha256((root / FIXTURE).read_bytes()).hexdigest(),
                           "raw_bodies_sha256": provenance},
        "D1_mechanism": d1, "D2_split": d2, "D3_usdt0_exit": d3, "D4_rango": d4, "D5_near_intents": d5,
        "D6_hub": d6, "D7_exchange": d7, "D8_funder": d8, "R1_report": report_facts,
    }
    return out


def dumps(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, indent=1) + "\n"


def load() -> dict[str, Any]:
    return json.loads(OUT.read_text(encoding="utf-8"))


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--check", action="store_true", help="only compare with the frozen file")
    a = p.parse_args(argv)
    built = dumps(build())
    if a.check:
        same = OUT.is_file() and OUT.read_text(encoding="utf-8") == built
        print("frozen inputs up to date" if same else "frozen inputs DIFFER from a fresh build")
        return 0 if same else 1
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(built, encoding="utf-8", newline="\n")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
