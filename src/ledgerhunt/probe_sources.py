"""Foundation probes: confirm each source endpoint with a few keyless case-001 requests.

Writes results/stage-2/foundation-probes/<run_id>/ (probes.jsonl, summary.json, summary.md,
http-metrics.jsonl). Checks compare a few observed fields with the case-001 fixture; a
mismatch is recorded as such, never adjusted.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from typing import Any, Callable

from .core.paths import repo_root
from .core.redact import redact
from .core.results import start_run
from .core.tron import USDT_TRC20, format_amount
from .sources import (
    BlockscoutClient,
    EthRpcClient,
    LayerZeroScanClient,
    NearIntentsClient,
    TronGridClient,
    TronNodeClient,
)
from .sources.base import Fetched, Paged

THEFT_TX = "98f3ffca9d141f2172d28f46905c08e5f32fc6ce8d23f9a37b731fe2a6c1d1bb"
BRIDGE_OUT_TX = "b49b0157d5327ca4b25683d2100d77c9b0c2c13584fdc96deea17a8c93057f6f"
LZ_GUID = "0xba20537a6870e4ba2538d40ae16772f198f02d88d24c47d016b53863a7337bf8"
ETH_BRIDGE_IN_TX = "0x8ea2bdef31c5eefb89569a239d5208cdff99a7bb9a7fe2f48c168b16b9d73c15"
ETH_RANGO_TX = "0x41bac088520409376e60709fd7114b7b3d670abeedfb01a68b7ee42a84ec515a"
ETH_TRANSIT = "0x4079047990917F3150353FBd8A13b05b6286926d"
NEAR_DEPOSIT = "0xdA392553ec3602D3e650a725f847C10d04E122C0"
VICTIM = "TNakrL7VUMLNN4EEpi64HKjj5YqafR5tUx"
THIEF1 = "TYGdh7qysHLr3A4gVGivcRwSg79PpVzgNn"
GAS_FUNDER = "TVNMa2ZrUWE9sdBawJoQ8aN6LPFjv9ZppZ"
HUB = "TYHeH2HQn7pM5fe6aYwGabz9x4yizJbwp6"


def _ms(s: str) -> int:
    return int(datetime.strptime(s, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc).timestamp() * 1000)


def run(args: argparse.Namespace) -> int:
    fixture = json.loads((repo_root() / "tests/fixtures/case-001/case-001-ground-truth.json").read_text(encoding="utf-8"))
    run_ctx = start_run(
        "foundation-probes",
        config={"purpose": "confirm endpoint shapes with keyless case-001 requests", "keys_used": False},
        reproduce="python -m ledgerhunt probe-sources" + (" --replay" if getattr(args, "replay", False) else ""),
    )
    http = run_ctx.http_client()
    tg = TronGridClient(http, api_key=None)  # keyless on purpose
    pn = TronNodeClient(http)
    bs = BlockscoutClient(http, api_key=None)
    eth = EthRpcClient(http)
    lz = LayerZeroScanClient(http)
    ni = NearIntentsClient(http, jwt=None)

    rows: list[dict[str, Any]] = []

    def probe(name: str, fn: Callable[[], Fetched | Paged], check: Callable[[Any], dict[str, Any]]) -> None:
        row: dict[str, Any] = {"probe": name}
        try:
            res = fn()
            pages = res.pages if isinstance(res, Paged) else [res]
            data = res.rows if isinstance(res, Paged) else res.data
            row.update({
                "status": [p.status for p in pages],
                "pages": len(pages),
                "latency_ms": [p.latency_ms for p in pages],
                "attempts": [p.attempts for p in pages],
                "from_replay": all(p.from_replay for p in pages),
                "url": pages[0].url,
                "refs": [p.ref_dict() for p in pages],
            })
            if isinstance(res, Paged):
                row["complete"] = res.complete
            row["check"] = check(data)
        except Exception as exc:  # noqa: BLE001 - recorded as a failed probe
            row["error"] = f"{type(exc).__name__}: {redact(exc)}"
            row["check"] = {"pass": False}
        rows.append(row)
        run_ctx.append_jsonl("probes.jsonl", row)
        mark = "OK " if row["check"].get("pass") else "FAIL"
        print(f"  [{mark}] {name}", flush=True)

    def eq(observed: Any, expected: Any) -> dict[str, Any]:
        return {"observed": observed, "expected": expected, "pass": observed == expected}

    theft = next(t for t in fixture["transactions"] if t["txid"] == THEFT_TX)

    # -- TronGrid v1 ------------------------------------------------------
    def trc20_check(rows_: list[dict[str, Any]]) -> dict[str, Any]:
        hit = [r for r in rows_ if r.get("transaction_id") == THEFT_TX]
        obs = None
        if hit:
            obs = {"from": hit[0]["from"], "to": hit[0]["to"], "amount": format_amount(hit[0]["value"])}
        return eq(obs, {"from": theft["from"], "to": theft["to"], "amount": theft["amount"]})

    probe("trongrid.v1.trc20_transfers (limit=2, fingerprint pagination)",
          lambda: tg.trc20_transfers(THIEF1, min_timestamp=_ms("2026-09-21 11:00:00"),
                                     max_timestamp=_ms("2026-09-21 12:00:00"), limit=2, max_pages=3),
          trc20_check)
    probe("trongrid.v1.account_transactions",
          lambda: tg.account_transactions_page(VICTIM, min_timestamp=_ms("2026-09-21 11:32:00"),
                                               max_timestamp=_ms("2026-09-21 11:33:00"), limit=2),
          lambda d: {"observed_rows": len(d.get("data", [])), "has_txID": all("txID" in r for r in d.get("data", [])),
                     "pass": bool(d.get("data")) and all("txID" in r for r in d["data"])})
    probe("trongrid.v1.transaction_events",
          lambda: tg.transaction_events(THEFT_TX),
          lambda d: eq([(e.get("event_name"), e.get("block_number"), e.get("event_index")) for e in d.get("data", [])],
                       [("Transfer", theft["block"], 0)]))
    probe("trongrid.v1.contract_events (USDT Transfer, block 86439360)",
          lambda: tg.contract_events_page(USDT_TRC20, event_name="Transfer", block_number=theft["block"], limit=2),
          lambda d: {"observed_blocks": sorted({e.get("block_number") for e in d.get("data", [])}),
                     "pass": bool(d.get("data")) and all(e.get("block_number") == theft["block"] for e in d["data"])})
    # -- TronGrid node API ----------------------------------------------------
    probe("trongrid.wallet/gettransactionbyid",
          lambda: tg.get_transaction_by_id(THEFT_TX),
          lambda d: eq({"ret": (d.get("ret") or [{}])[0].get("contractRet"),
                        "owner": d["raw_data"]["contract"][0]["parameter"]["value"].get("owner_address"),
                        "permission_id": d["raw_data"]["contract"][0].get("Permission_id")},
                       {"ret": "SUCCESS", "owner": VICTIM, "permission_id": None}))
    probe("trongrid.walletsolidity/gettransactioninfobyid",
          lambda: tg.get_transaction_info_by_id(THEFT_TX),
          lambda d: eq({"block": d.get("blockNumber"), "energy": (d.get("receipt") or {}).get("energy_usage_total"),
                        "fee_trx": format_amount(d.get("fee", 0))},
                       {"block": theft["block"], "energy": 130285, "fee_trx": "0.345000"}))
    probe("trongrid.wallet/getaccount",
          lambda: tg.get_account(GAS_FUNDER),
          lambda d: {"observed_address": d.get("address"), "has_create_time": "create_time" in d,
                     "pass": d.get("address") == GAS_FUNDER and "create_time" in d})
    probe("trongrid.wallet/triggerconstantcontract (USDT balanceOf hub)",
          lambda: tg.trc20_balance_of(HUB)[1],
          lambda d: {"observed_balance_now": format_amount(int(d["constant_result"][0], 16))
                     if d.get("constant_result") else None,
                     "note": "live value, changes constantly; fixture had 238766.644069 at ~2026-10-14 09:00 UTC",
                     "pass": bool(d.get("constant_result")) and (d.get("result") or {}).get("result") is True})
    # -- PublicNode TRON ----------------------------------------------------
    probe("tron_publicnode.wallet/getaccount",
          lambda: pn.get_account(GAS_FUNDER),
          lambda d: {"pass": d.get("address") == GAS_FUNDER})
    probe("tron_publicnode.walletsolidity/getaccount",
          lambda: pn.get_account(GAS_FUNDER, solidity=True),
          lambda d: {"pass": d.get("address") == GAS_FUNDER})
    probe("tron_publicnode.walletsolidity/gettransactioninfobyid (case-001 theft, expected to be outside history)",
          lambda: pn.get_transaction_info_by_id(THEFT_TX),
          lambda d: {"observed_empty_object": d == {}, "pass": True,
                     "note": "{} = node has no data for this tx (pruned history); recorded, not a pass/fail of the API"})
    # -- Blockscout ----------------------------------------------------------
    probe("blockscout.transaction (Rango tx)",
          lambda: bs.transaction(ETH_RANGO_TX),
          lambda d: eq({"block": d.get("block_number"), "status": d.get("status"), "method": d.get("method")},
                       {"block": 26025727, "status": "ok", "method": "genericBridge"}))
    probe("blockscout.transaction_token_transfers",
          lambda: bs.transaction_token_transfers(ETH_RANGO_TX),
          lambda d: {"observed_items": len(d), "pass": len(d) > 0})
    probe("blockscout.transaction_logs",
          lambda: bs.transaction_logs(ETH_RANGO_TX),
          lambda d: {"observed_items": len(d), "pass": len(d) > 0})
    probe("blockscout.address_token_transfers (1 page)",
          lambda: bs.address_token_transfers_page(ETH_TRANSIT),
          lambda d: {"observed_items": len(d.get("items", [])), "next_page_params": d.get("next_page_params"),
                     "pass": "items" in d})
    # -- Ethereum JSON-RPC ------------------------------------------------------
    probe("eth_rpc.eth_getTransactionReceipt (USDT0 bridge-in)",
          lambda: eth.get_transaction_receipt(ETH_BRIDGE_IN_TX),
          lambda d: eq({"block": int(d["blockNumber"], 16), "status": d.get("status")},
                       {"block": 26025709, "status": "0x1"}))
    probe("eth_rpc.eth_getTransactionByHash",
          lambda: eth.get_transaction_by_hash(ETH_BRIDGE_IN_TX),
          lambda d: {"pass": (d or {}).get("hash") == ETH_BRIDGE_IN_TX})
    probe("eth_rpc.eth_getBlockByNumber(26025709)",
          lambda: eth.get_block_by_number(26025709),
          lambda d: {"observed_timestamp_utc": datetime.fromtimestamp(int(d["timestamp"], 16), timezone.utc)
                     .strftime("%Y-%m-%d %H:%M:%S"), "pass": int(d["number"], 16) == 26025709})
    # -- LayerZero Scan ---------------------------------------------------------
    lz_fix = next(t for t in fixture["transactions"] if t["txid"] == BRIDGE_OUT_TX)["layerzero"]
    probe("layerzero_scan.messages_by_tx (TRON tx, 0x added)",
          lambda: lz.messages_by_tx(BRIDGE_OUT_TX),
          lambda d: eq([(m.get("guid"), (m.get("pathway") or {}).get("srcEid"), (m.get("pathway") or {}).get("dstEid"),
                         (m.get("status") or {}).get("name")) for m in d.get("data", [])],
                       [(lz_fix["guid"], lz_fix["srcEid"], lz_fix["dstEid"], lz_fix["status"])]))
    probe("layerzero_scan.message_by_guid",
          lambda: lz.message_by_guid(LZ_GUID),
          lambda d: {"observed_messages": len(d.get("data", [])), "pass": len(d.get("data", [])) == 1})
    # -- NEAR Intents 1Click -------------------------------------------------------
    ni_fix = next(t for t in fixture["transactions"] if t.get("near_intents"))["near_intents"]
    probe("near_intents.status(depositAddress)",
          lambda: ni.status(NEAR_DEPOSIT),
          lambda d: eq({"status": d.get("status"),
                        "recipient": ((d.get("quoteResponse") or {}).get("quoteRequest") or {}).get("recipient"),
                        "destination_tx": [h.get("hash") for h in (d.get("swapDetails") or {})
                                           .get("destinationChainTxHashes", [])]},
                       {"status": ni_fix["status"], "recipient": ni_fix["recipient_tron"],
                        "destination_tx": [ni_fix["destination_tx"]]}))

    passed = sum(1 for r in rows if r["check"].get("pass"))
    summary = {"probes": len(rows), "passed": passed, "failed": len(rows) - passed,
               "failed_probes": [r["probe"] for r in rows if not r["check"].get("pass")],
               "http": http.metrics_summary()}
    lines = [
        "# Проверка эндпоинтов источников (foundation)",
        "",
        f"Запуск: `{run_ctx.run_id}`, режим HTTP: `{http.mode}`. Запросы без ключей, идентификаторы case-001.",
        "",
        "| Проба | Статус | Проверка |",
        "|---|---|---|",
    ]
    for r in rows:
        status = ",".join(str(s) for s in r.get("status", [])) or r.get("error", "")[:60]
        lines.append(f"| {r['probe']} | {status} | {'пройдена' if r['check'].get('pass') else 'не пройдена'} |")
    lines += ["", f"Итого: {passed} из {len(rows)} проверок пройдены.", ""]
    run_ctx.finish(summary, "\n".join(lines))
    print(f"foundation probes: {passed}/{len(rows)} passed -> {run_ctx.rel_dir}")
    return 0 if passed == len(rows) else 1
