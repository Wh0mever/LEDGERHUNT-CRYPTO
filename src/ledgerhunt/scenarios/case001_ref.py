"""case-001 as a development reference scenario (tests/scenarios/dev/case-001/).

It points to tests/fixtures/case-001/case-001-ground-truth.json and restates its
ground_truth section in the result schema so the same scorer can be used. It is NOT
synthetic, has no world.json and no own store (the real raw responses live in the shared
data/http-store, recorded by the case001/bridges areas), is never part of the held-out
set and does not count toward the set metrics.

Caveat carried over from the fixture: its values came from a tool that returned parsed
fields; until the case001 area re-verifies every fact from raw responses, this expected
answer is "fixture-derived, not re-verified". Event indexes are unknown for most hops
(``event_index: null`` matches any index of that TXID).
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from ..core.paths import repo_root

FIXTURE = "tests/fixtures/case-001/case-001-ground-truth.json"


def _fixture() -> dict[str, Any]:
    return json.loads((repo_root() / FIXTURE).read_text(encoding="utf-8"))


def _tx(fx: dict[str, Any], step: int) -> dict[str, Any]:
    return next(t for t in fx["transactions"] if t["step"] == step)


def _transfer(t: dict[str, Any], *, event_index: int | None = None, role: str, taint: str = "traced") -> dict[str, Any]:
    chain = t["chain"]
    return {"chain": chain, "txid": t["txid"].lower(), "event_index": event_index, "from": t["from"], "to": t["to"],
            "amount": t["amount"], "asset": "USDT-TRC20" if chain == "tron" else "USDT-ERC20", "taint": taint,
            "verification": "second_source_confirmed", "role": role, "excluded": None}


def build_case001() -> tuple[dict[str, Any], dict[str, Any]]:
    fx = _fixture()
    sha = hashlib.sha256((repo_root() / FIXTURE).read_bytes()).hexdigest()
    theft, hop1, hop2, bridge_out = _tx(fx, 6), _tx(fx, 8), _tx(fx, 9), _tx(fx, 12)
    eth_in, rango, near_dep, tron_in = _tx(fx, 14), _tx(fx, 15), _tx(fx, 16), _tx(fx, 17)
    fee_thief, fee_1pct = _tx(fx, 7), _tx(fx, 10)
    lz = bridge_out["layerzero"]
    rg = rango["rango"]
    ni = near_dep["near_intents"]
    main_txids = [t["txid"].lower() for t in (theft, hop1, hop2, bridge_out, eth_in, rango, near_dep, tron_in)]
    hub = tron_in["to"]
    inp = {
        "schema": "ledgerhunt.scenario-input/1",
        "scenario_id": "case-001",
        "split": "dev",
        "synthetic": False,
        "start": {"chain": "tron", "txid": theft["txid"]},
        "params": {"max_depth": 20, "asset": "USDT-TRC20", "token_contract": "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"},
        "context": {"labels": [], "supported_bridges": [{"protocol": "usdt0_oft", "dst_eids": [30101]},
                                                        {"protocol": "rango"}, {"protocol": "near_intents_1click"}]},
        "store": None,
        "request_profile": "live-sources (shared data/http-store)",
        "providers": {"primary_index": "trongrid", "secondary_receipts": "paid TRON RPC (TRON_RPC_URL)",
                      "bridge_api": "layerzero_scan, near_intents_1click", "ethereum": "blockscout_eth, eth_publicnode"},
        "reference": {"fixture": FIXTURE, "fixture_sha256": sha, "counts_toward_metrics": False,
                      "status": "fixture-derived, not re-verified from raw responses (see results/stage-2/case001)"},
    }
    transfers = [
        _transfer(theft, event_index=0, role="main"),  # event_index 0 confirmed from the recorded events response
        _transfer(hop1, role="main"),
        _transfer(hop2, role="main"),
        _transfer(bridge_out, event_index=0, role="main"),  # Transfer is event 0 in the recorded events response
        _transfer(eth_in, role="main"),
        _transfer(rango, role="main"),
        _transfer(near_dep, role="main"),
        _transfer(tron_in, role="main"),
        _transfer(fee_thief, role="side_branch"),
        _transfer(fee_1pct, role="side_branch"),
        {"chain": "ethereum", "txid": rango["txid"].lower(), "event_index": None, "from": rango["to"],
         "to": rg["affiliate"], "amount": rg["affiliateFee"], "asset": "USDT-ERC20", "taint": "traced",
         "verification": "second_source_confirmed", "role": "side_branch", "excluded": None},
    ]
    routes = [
        {"route_id": "r01", "kind": "main", "txids": main_txids,
         "terminal": {"chain": "tron", "address": hub, "reason": "commingled"}, "excluded": None},
        {"route_id": "r02", "kind": "side_branch", "txids": [theft["txid"], fee_thief["txid"]],
         "terminal": {"chain": "tron", "address": fee_thief["to"], "reason": "known_service"}, "excluded": None},
        {"route_id": "r03", "kind": "side_branch", "txids": [theft["txid"], hop1["txid"], fee_1pct["txid"]],
         "terminal": {"chain": "tron", "address": fee_1pct["to"], "reason": "funds_at_rest"}, "excluded": None},
    ]
    exchange = []
    for out_step, sweep_step in ((18, 19), (22, 23)):
        o, s = _tx(fx, out_step), _tx(fx, sweep_step)
        exchange.append({"chain": "tron", "deposit_address": o["to"], "exchange": "WhiteBIT", "hot_wallet": s["to"],
                         "sweep_txids": [s["txid"]], "excluded": None})
    bridges = [
        {"chain": "tron", "txid": bridge_out["txid"], "protocol": "usdt0_oft", "dst_eid": lz["dstEid"],
         "dst_chain": lz["dst_chain"], "supported": True, "sender": bridge_out["from"], "recipient": lz["sendTo"].lower(),
         "amount_sent": bridge_out["amount"], "amount_received": lz["amountReceivedLD"], "guid": lz["guid"],
         "dst_txid": eth_in["txid"].lower(), "excluded": None},
        {"chain": "ethereum", "txid": rango["txid"].lower(), "protocol": "rango", "dst_eid": None, "dst_chain": "tron",
         "supported": True, "sender": rango["from"].lower(), "recipient": None, "amount_sent": rango["amount"],
         "amount_received": None, "guid": None, "dst_txid": None, "excluded": None},
        {"chain": "ethereum", "txid": near_dep["txid"].lower(), "protocol": "near_intents_1click", "dst_eid": None,
         "dst_chain": "tron", "supported": True, "sender": near_dep["from"].lower(), "recipient": ni["recipient_tron"],
         "amount_sent": near_dep["amount"], "amount_received": tron_in["amount"], "guid": None,
         "dst_txid": ni["destination_tx"], "excluded": None},
    ]
    expected = {
        "schema": "ledgerhunt.scenario-result/1",
        "scenario_id": "case-001",
        "result_type": "expected",
        "transfers": transfers,
        "routes": routes,
        "exchange_deposits": exchange,
        "bridge_exits": bridges,
        "merges": [{"chain": "tron", "address": hub, "attribution": "uncertain", "traced_inflow_txids": [tron_in["txid"]],
                    "foreign_inflow_txids": [], "excluded": None}],
        "limitations": [],
        "allowed": {"transfers": [_transfer(_tx(fx, 13), role="dust", taint="uncertain")],
                    "exchange_deposits": [], "bridge_exits": [], "merges": []},
        "traps": [{"txid": _tx(fx, 1)["txid"], "event_index": None, "reason": "pre_theft_inflow"},
                  {"txid": _tx(fx, 2)["txid"], "event_index": None, "reason": "pre_theft_inflow"},
                  {"txid": _tx(fx, 11)["txid"], "event_index": None, "reason": "approval_not_transfer"}],
        "outages": [],
        "evidence_boundaries": [],
        "notes": [
            "Reference answer restated from the fixture ground_truth; values are not re-verified here.",
            "Exchange exits follow the owners' expectation (expected_exchange_exits) although they come after the "
            "commingled hub; synthetic scenarios treat such facts as allowed, not required.",
            "Open question from the foundation probe: 1Click lists 0x41bac... (Rango) as origin tx; the fixture's "
            "step 16 (0x224f...) is the deposit-address -> vault sweep. The bridges area should settle which TXID "
            "represents the NEAR Intents exit.",
            "0x4079... sent 12901.411000 to Rango after receiving 12901.408416 (reused EOA): a 0.002584 USDT mix on "
            "Ethereum is ignored here.",
            f"Expected mechanism: {fx['ground_truth']['expected_mechanism']}",
            f"Expected freeze candidate: {fx['ground_truth']['expected_freeze_candidate']}",
            f"Total fees lost before hub (fixture): {fx['ground_truth']['total_fees_lost_before_hub']}",
            "Common TRX funder TVNMa2... is a 'probably same operator' link with a confidence level, not a fact.",
        ],
        "meta": {"category": "reference_real", "variant": "case-001", "title_ru": "Эталонный реальный кейс case-001",
                 "description": "real theft 2026-09-21, TRON -> USDT0 -> Ethereum -> Rango/NEAR Intents -> TRON",
                 "split": "dev", "counts_toward_metrics": False},
    }
    return inp, expected


def write_case001(directory: Path) -> None:
    inp, expected = build_case001()
    directory.mkdir(parents=True, exist_ok=True)
    for name, obj in (("input.json", inp), ("expected.json", expected)):
        (directory / name).write_text(json.dumps(obj, ensure_ascii=False, indent=1) + "\n", encoding="utf-8",
                                      newline="\n")
    readme = (
        "# case-001 — эталон для разработки\n\n"
        "Реальный кейс, а не синтетический сценарий. Исходные данные — "
        "[tests/fixtures/case-001/case-001-ground-truth.json](../../../fixtures/case-001/case-001-ground-truth.json).\n\n"
        "- `input.json` — старт по TXID кражи и параметры; сырые ответы лежат в общем хранилище `data/http-store/`.\n"
        "- `expected.json` — раздел ground_truth эталона в схеме результата; значения не перепроверены "
        "(перепроверку делает раздел `case001`).\n"
        "- В отложенный набор не входит и в метриках набора не учитывается.\n"
    )
    (directory / "README.md").write_text(readme, encoding="utf-8", newline="\n")
