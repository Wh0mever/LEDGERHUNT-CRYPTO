"""The 8 decision points of the case-001 trace.

Inputs come from the frozen file data/decision_inputs.json (built by build_inputs.py from the case-001
fixture and recorded raw responses). Expected answers come from the fixture's transactions and
ground_truth sections. Scorers compare exact fields; identifiers and amounts must match exactly
(hex compared case-insensitively, amounts as decimals).
"""

from __future__ import annotations

import json
from decimal import Decimal
from functools import lru_cache
from pathlib import Path
from typing import Any

from ...core.paths import repo_root
from ..build_inputs import OUT as INPUTS_PATH
from ..identifiers import contains_identifier, same_identifier
from ..scoring import (COMMINGLED_PATTERNS, HYPOTHESIS_PATTERNS, Score, all_text, amount_eq, forbidden_claims,
                       mentions_any, norm_amount)
from . import Task, TaskContext
from .schema import arr, b, e, i, obj, s

FIXTURE_PATH = Path("tests/fixtures/case-001/case-001-ground-truth.json")


@lru_cache(maxsize=1)
def fixture() -> dict[str, Any]:
    return json.loads((repo_root() / FIXTURE_PATH).read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def inputs() -> dict[str, Any]:
    return json.loads(INPUTS_PATH.read_text(encoding="utf-8"))


def step(n: int) -> dict[str, Any]:
    return next(x for x in fixture()["transactions"] if x["step"] == n)


def _get(o: Any, key: str, default: Any = None) -> Any:
    return o.get(key, default) if isinstance(o, dict) else default


def _no_forbidden(sc: Score, o: Any) -> None:
    hits = forbidden_claims(all_text(o))
    sc.add("no_recovery_or_identity_claims", not hits, hits or None)


COMMON_RULES = (
    "Base every field on the case data and the reference data in the system prompt. "
    "Use exact identifiers and exact decimal amounts. Keep 'explanation' under 80 words."
)

# ===================================================================== D1 mechanism

D1_SCHEMA = obj(
    theft_txid=s(),
    called_method=e("transfer", "transferFrom", "approve", "other"),
    signer_permission=e("owner", "active_or_custom", "unknown"),
    permission_id_present=b(),
    signature_count=i(),
    account_permissions_changed=b(),
    mechanism=e("private_key_or_seed_compromise", "permission_change_hijack", "token_approval_drain",
                "victim_initiated_transfer", "unknown"),
    confidence=e("low", "medium", "high"),
    advice_to_victim=s("one or two sentences for the victim about the wallet itself"),
    evidence=arr(s()),
    explanation=s(),
)

D1_TEXT = f"""Decision: how were the funds taken from the victim address?
Read the raw theft transaction (method selector in the call data, signer, Permission_id, signatures),
the account permissions and the timeline. Classify the mechanism. 'advice_to_victim' says what the victim
must do about this wallet. {COMMON_RULES}"""


def score_d1(o: Any, ctx: TaskContext) -> Score:
    sc = Score(critical=("mechanism", "signer_permission", "account_permissions_changed"))
    sc.add("theft_txid", same_identifier(_get(o, "theft_txid"), fixture()["theft"]["txid"]))
    sc.add("called_method", _get(o, "called_method") == "transfer")
    sc.add("signer_permission", _get(o, "signer_permission") == "owner")
    sc.add("permission_id_present", _get(o, "permission_id_present") is False)
    sc.add("signature_count", _get(o, "signature_count") == 1)
    sc.add("account_permissions_changed", _get(o, "account_permissions_changed") is False)
    sc.add("mechanism", _get(o, "mechanism") == "private_key_or_seed_compromise", _get(o, "mechanism"))
    sc.add("advice_wallet_compromised", mentions_any(_get(o, "advice_to_victim", ""),
                                                     (r"compromis", r"new wallet", r"clean device", r"stop using")))
    return sc


# ===================================================================== D2 99/1 split

D2_SCHEMA = obj(
    branches=arr(obj(
        to_address=s(), txid=s(), amount=s(), share_of_incoming_percent=s(),
        decision=e("follow_as_main_route", "record_as_side_branch", "ignore"),
        role=e("laundering_hop", "fee_collector", "exchange_deposit", "bridge", "unknown"),
    )),
    split_pattern=e("fixed_percentage_split", "even_split", "peel_chain", "single_transfer", "other"),
    amounts_reconcile=b("do the outgoing amounts add up exactly to the incoming amount"),
    main_route_next_address=s(),
    explanation=s(),
)

D2_TEXT = f"""Decision: the address under review received stolen USDT and split it. For every outgoing USDT
transfer decide whether the tracer follows it as the main route of the stolen funds, records it as a side
branch (amount noted, not traced further now) or ignores it. Give each branch's share of the incoming amount in
percent as a decimal string. {COMMON_RULES}"""


def _branch(o: Any, addr: str) -> dict[str, Any]:
    for br in _get(o, "branches", []) or []:
        if isinstance(br, dict) and same_identifier(br.get("to_address"), addr):
            return br
    return {}


def _pct_eq(v: Any, target: str) -> bool:
    d = norm_amount(str(v).replace("%", "")) if v is not None else None
    return d is not None and abs(d - Decimal(target)) <= Decimal("0.01")


def score_d2(o: Any, ctx: TaskContext) -> Score:
    main, fee = step(9), step(10)
    sc = Score(critical=("main_route_next_address", "main_branch_followed", "fee_branch_not_followed"))
    m, f = _branch(o, main["to"]), _branch(o, fee["to"])
    sc.add("main_route_next_address", same_identifier(_get(o, "main_route_next_address"), main["to"]))
    sc.add("main_branch_followed", m.get("decision") == "follow_as_main_route")
    sc.add("fee_branch_not_followed", f.get("decision") == "record_as_side_branch", f.get("decision"))
    sc.add("fee_role", f.get("role") == "fee_collector", f.get("role"))
    sc.add("main_amount", amount_eq(m.get("amount"), main["amount"]))
    sc.add("fee_amount", amount_eq(f.get("amount"), fee["amount"]))
    sc.add("main_txid", same_identifier(m.get("txid"), main["txid"]))
    sc.add("fee_txid", same_identifier(f.get("txid"), fee["txid"]))
    sc.add("shares", _pct_eq(m.get("share_of_incoming_percent"), "99") and _pct_eq(f.get("share_of_incoming_percent"), "1"))
    sc.add("split_pattern", _get(o, "split_pattern") == "fixed_percentage_split", _get(o, "split_pattern"))
    sc.add("amounts_reconcile", _get(o, "amounts_reconcile") is True)
    return sc


# ===================================================================== D3 USDT0 bridge exit

D3_SCHEMA = obj(
    is_bridge_exit=b(),
    bridge=e("USDT0_LayerZero_OFT", "Rango", "NEAR_Intents_1Click", "other", "none"),
    source_txid=s(),
    destination_chain=e("ethereum", "tron", "other", "unknown"),
    destination_endpoint_id=i(),
    layerzero_guid=s(),
    destination_txid=s(),
    destination_recipient=s(),
    amount_sent=s(),
    amount_received=s(),
    bridge_fee=s(),
    message_status=s(),
    other_outflows=arr(obj(txid=s(), to_address=s(), amount=s(),
                           decision=e("follow", "side_branch", "ignore_dust"))),
    next_action=e("continue_tracing_on_destination_chain", "continue_on_tron", "stop_evidence_boundary"),
    explanation=s(),
)

D3_TEXT = f"""Decision: did the stolen funds leave TRON from the address under review? If they did, identify the
bridge and the other side: destination chain, LayerZero GUID, destination transaction, recipient and the amount
received there (decode raw values where needed), and the bridge fee (amount_sent minus amount_received).
Classify the remaining outflows. Choose the tracer's next action. {COMMON_RULES}"""


def score_d3(o: Any, ctx: TaskContext) -> Score:
    st, lz, recv = step(12), step(12)["layerzero"], step(14)
    sc = Score(critical=("bridge", "destination_recipient", "amount_received", "next_action"))
    sc.add("is_bridge_exit", _get(o, "is_bridge_exit") is True)
    sc.add("bridge", _get(o, "bridge") == "USDT0_LayerZero_OFT", _get(o, "bridge"))
    sc.add("source_txid", same_identifier(_get(o, "source_txid"), st["txid"]))
    sc.add("destination_chain", _get(o, "destination_chain") == "ethereum")
    sc.add("destination_endpoint_id", _get(o, "destination_endpoint_id") == lz["dstEid"])
    sc.add("layerzero_guid", same_identifier(_get(o, "layerzero_guid"), lz["guid"]))
    sc.add("destination_txid", same_identifier(_get(o, "destination_txid"), recv["txid"]))
    sc.add("destination_recipient", same_identifier(_get(o, "destination_recipient"), lz["sendTo"]), _get(o, "destination_recipient"))
    sc.add("amount_sent", amount_eq(_get(o, "amount_sent"), st["amount"]))
    sc.add("amount_received", amount_eq(_get(o, "amount_received"), lz["amountReceivedLD"]), _get(o, "amount_received"))
    sc.add("bridge_fee", amount_eq(_get(o, "bridge_fee"), "3.871584"), _get(o, "bridge_fee"))
    dust = next((x for x in _get(o, "other_outflows", []) or [] if isinstance(x, dict)
                 and same_identifier(x.get("to_address"), step(13)["to"])), {})
    sc.add("dust_not_followed", dust.get("decision") in ("ignore_dust", "side_branch"), dust.get("decision"))
    sc.add("next_action", _get(o, "next_action") == "continue_tracing_on_destination_chain")
    return sc


# ===================================================================== D4 Rango log

D4_SCHEMA = obj(
    aggregator=e("Rango", "other", "unknown"),
    input_from=s(),
    input_amount=s(),
    affiliate_address=s(),
    affiliate_fee=s(),
    forwarded_to=s(),
    forwarded_amount=s(),
    amounts_reconcile=b("input_amount minus affiliate_fee equals forwarded_amount exactly"),
    destination_chain_id=i(),
    destination_chain=s("name of the destination chain"),
    receiver_field_raw=s("the receiver value exactly as it appears in the event"),
    receiver_is_ethereum_address=b(),
    receiver_on_destination_chain=s("the receiver on the destination chain as far as this data shows it (may be partial); empty if unknown"),
    receiver_is_complete_address=b(),
    next_action=e("query_bridge_status_api_for_forwarded_address", "trace_receiver_address_on_ethereum",
                  "stop_evidence_boundary"),
    explanation=s(),
)

D4_TEXT = f"""Decision: interpret this Ethereum transaction of the launderer's transit address and its event logs.
Where did the USDT go, which fees were taken, what is the destination chain and who is the receiver?
Decode raw values yourself where the decoded form is misleading. Choose the tracer's next action. {COMMON_RULES}"""


def score_d4(o: Any, ctx: TaskContext) -> Score:
    r = step(15)["rango"]
    # next_action is critical: stopping here loses the route (decision 2.3: continue through supported bridges).
    sc = Score(critical=("destination_chain", "receiver_is_ethereum_address", "receiver_on_destination_chain",
                         "forwarded_to", "next_action"))
    sc.add("aggregator", _get(o, "aggregator") == "Rango")
    sc.add("input_from", same_identifier(_get(o, "input_from"), step(15)["from"]))
    sc.add("input_amount", amount_eq(_get(o, "input_amount"), step(15)["amount"]))
    sc.add("affiliate_address", same_identifier(_get(o, "affiliate_address"), r["affiliate"]))
    sc.add("affiliate_fee", amount_eq(_get(o, "affiliate_fee"), r["affiliateFee"]))
    sc.add("forwarded_to", same_identifier(_get(o, "forwarded_to"), r["forwarded_to"]), _get(o, "forwarded_to"))
    sc.add("forwarded_amount", amount_eq(_get(o, "forwarded_amount"), r["forwarded_amount"]))
    sc.add("amounts_reconcile", _get(o, "amounts_reconcile") is True)
    sc.add("destination_chain_id", _get(o, "destination_chain_id") == r["destinationChainId"])
    sc.add("destination_chain", str(_get(o, "destination_chain", "")).strip().upper() == r["destinationChainId_ascii"],
           _get(o, "destination_chain"))
    sc.add("receiver_field_raw", same_identifier(_get(o, "receiver_field_raw"), "0x54594865483248516E37704D3566653661597747"))
    sc.add("receiver_is_ethereum_address", _get(o, "receiver_is_ethereum_address") is False)
    sc.add("receiver_on_destination_chain", str(_get(o, "receiver_on_destination_chain", "")).strip() == r["receiver_bytes_ascii"],
           _get(o, "receiver_on_destination_chain"))
    sc.add("receiver_is_complete_address", _get(o, "receiver_is_complete_address") is False)
    sc.add("next_action", _get(o, "next_action") == "query_bridge_status_api_for_forwarded_address", _get(o, "next_action"))
    return sc


# ===================================================================== D5 NEAR Intents

D5_SCHEMA = obj(
    service=e("NEAR_Intents_1Click", "Rango", "other"),
    deposit_address=s(),
    deposit_address_is_one_time=b(),
    swap_status=s(),
    destination_chain=e("tron", "ethereum", "other"),
    recipient=s(),
    recipient_matches_rango_receiver_prefix=b(),
    destination_txid=s(),
    destination_tx_confirmed_on_chain=b("the destination transaction hash matches an on-chain transfer to the recipient"),
    amount_deposited=s(),
    amount_out_reported=s("amountOut reported by the service"),
    amount_received_on_chain=s(),
    reported_and_onchain_amounts_match=b(),
    refund_address=s(),
    next_action=e("continue_tracing_on_tron_from_recipient", "trace_vault_on_ethereum", "stop_evidence_boundary"),
    explanation=s(),
)

D5_TEXT = f"""Decision: the funds were forwarded to an address on Ethereum. Using the transfers of that address, the
swap service status and the TRON transfer, determine what the forwarded address is, where the funds were
delivered, whether the delivery is confirmed on-chain and whether the reported and on-chain amounts agree.
Choose the tracer's next action. {COMMON_RULES}"""


def score_d5(o: Any, ctx: TaskContext) -> Score:
    s16, s17 = step(16), step(17)
    sc = Score(critical=("recipient", "destination_txid", "next_action"))
    sc.add("service", _get(o, "service") == "NEAR_Intents_1Click")
    sc.add("deposit_address", same_identifier(_get(o, "deposit_address"), s16["from"]))
    sc.add("deposit_address_is_one_time", _get(o, "deposit_address_is_one_time") is True)
    sc.add("swap_status", str(_get(o, "swap_status", "")).upper() == "SUCCESS")
    sc.add("destination_chain", _get(o, "destination_chain") == "tron")
    sc.add("recipient", _get(o, "recipient") == s16["near_intents"]["recipient_tron"], _get(o, "recipient"))
    sc.add("recipient_matches_prefix", _get(o, "recipient_matches_rango_receiver_prefix") is True)
    sc.add("destination_txid", same_identifier(_get(o, "destination_txid"), s17["txid"]))
    sc.add("destination_tx_confirmed_on_chain", _get(o, "destination_tx_confirmed_on_chain") is True)
    sc.add("amount_deposited", amount_eq(_get(o, "amount_deposited"), s16["amount"]))
    sc.add("amount_out_reported", amount_eq(_get(o, "amount_out_reported"), "12878.410167"))
    sc.add("amount_received_on_chain", amount_eq(_get(o, "amount_received_on_chain"), s17["amount"]))
    sc.add("amounts_mismatch_noticed", _get(o, "reported_and_onchain_amounts_match") is False)
    sc.add("refund_address", same_identifier(_get(o, "refund_address"), s16["near_intents"]["refundTo"]))
    sc.add("next_action", _get(o, "next_action") == "continue_tracing_on_tron_from_recipient", _get(o, "next_action"))
    return sc


# ===================================================================== D6 hub / freeze candidate

D6_SCHEMA = obj(
    classification=e("holds_only_stolen_funds", "commingled_hub", "exchange_deposit_address", "exchange_hot_wallet",
                     "bridge_or_service_contract", "unknown"),
    funds_commingled=b(),
    outflow_attribution=e("one_to_one_traceable", "cannot_be_determined_commingled", "not_applicable"),
    freeze_candidate=b("should a freeze request for this address be prepared"),
    freeze_asset=e("USDT-TRC20", "TRX", "none"),
    traced_amount_received=s(),
    current_balance_exceeds_traced_amount=b(),
    uncertainty_statement=s("what cannot be concluded about the stolen funds at this address"),
    recommended_next_steps=arr(s()),
    explanation=s(),
)

D6_TEXT = f"""Decision: classify the address where the traced funds arrived after the cross-chain round trip, decide
whether it is a candidate for a freeze request and state explicitly what remains uncertain about the stolen
funds there. {COMMON_RULES}"""


def score_d6(o: Any, ctx: TaskContext) -> Score:
    sc = Score(critical=("classification", "freeze_candidate", "outflow_attribution", "no_recovery_or_identity_claims"))
    sc.add("classification", _get(o, "classification") == "commingled_hub", _get(o, "classification"))
    sc.add("funds_commingled", _get(o, "funds_commingled") is True)
    sc.add("outflow_attribution", _get(o, "outflow_attribution") == "cannot_be_determined_commingled")
    sc.add("freeze_candidate", _get(o, "freeze_candidate") is True)
    sc.add("freeze_asset", _get(o, "freeze_asset") == "USDT-TRC20")
    sc.add("traced_amount", amount_eq(_get(o, "traced_amount_received"), step(17)["amount"]))
    sc.add("balance_comparison", _get(o, "current_balance_exceeds_traced_amount") is True)
    sc.add("uncertainty_states_commingling", mentions_any(_get(o, "uncertainty_statement", ""), COMMINGLED_PATTERNS))
    _no_forbidden(sc, o)
    return sc


# ===================================================================== D7 exchange deposits

D7_SCHEMA = obj(
    candidates=arr(obj(
        address=s(),
        classification=e("exchange_deposit_address", "exchange_hot_wallet", "unknown_insufficient_data",
                         "personal_or_unlabelled_wallet", "service"),
        exchange=s("exchange name, or empty"),
        forwarded_full_amount=e("yes", "no", "unknown"),
        evidence_txids=arr(s()),
    )),
    label_basis=e("third_party_tag_and_forwarding_pattern", "forwarding_pattern_only", "third_party_tag_only", "none"),
    commingled_caveat=s("what the exchange deposits do and do not prove about the stolen funds"),
    recommended_action=s(),
    explanation=s(),
)

D7_TEXT = f"""Decision: apply the exchange-deposit heuristic (a deposit address forwards the full amount to a known
exchange hot wallet within minutes) to each candidate. Classify every candidate; do not classify an address as an
exchange deposit without evidence. Name the exchange only where the data supports it. {COMMON_RULES}"""


def _cand(o: Any, addr: str) -> dict[str, Any]:
    for c in _get(o, "candidates", []) or []:
        if isinstance(c, dict) and same_identifier(c.get("address"), addr):
            return c
    return {}


def score_d7(o: Any, ctx: TaskContext) -> Score:
    tnj, tci, twx, tp5 = step(18)["to"], step(22)["to"], step(20)["to"], step(21)["to"]
    sc = Score(critical=("TNJSC23_deposit", "TCiwRN_deposit", "no_false_exchange_label"))
    for name, addr, sweep in (("TNJSC23", tnj, step(19)), ("TCiwRN", tci, step(23))):
        c = _cand(o, addr)
        sc.add(f"{name}_deposit", c.get("classification") == "exchange_deposit_address", c.get("classification"))
        sc.add(f"{name}_exchange", "whitebit" in str(c.get("exchange", "")).lower())
        sc.add(f"{name}_full_amount", c.get("forwarded_full_amount") == "yes")
        sc.add(f"{name}_sweep_evidence", contains_identifier(c.get("evidence_txids") or [], sweep["txid"]))
    unknown_ok = all(_cand(o, a).get("classification") == "unknown_insufficient_data" for a in (twx, tp5))
    sc.add("unfetched_left_unknown", unknown_ok, [_cand(o, a).get("classification") for a in (twx, tp5)])
    false_label = any(_cand(o, a).get("classification") in ("exchange_deposit_address", "exchange_hot_wallet")
                      or "whitebit" in str(_cand(o, a).get("exchange", "")).lower() for a in (twx, tp5))
    sc.add("no_false_exchange_label", not false_label)
    sc.add("label_basis", _get(o, "label_basis") == "third_party_tag_and_forwarding_pattern", _get(o, "label_basis"))
    sc.add("commingled_caveat", mentions_any(_get(o, "commingled_caveat", ""), COMMINGLED_PATTERNS))
    _no_forbidden(sc, o)
    return sc


# ===================================================================== D8 common funder

D8_SCHEMA = obj(
    link_type=e("common_trx_funder", "direct_transfer", "same_route_reuse", "none"),
    funder=s(),
    funded_addresses=arr(s()),
    funding_transfers_status=e("fact", "claimed", "hypothesis"),
    same_operator_status=e("fact", "hypothesis", "rejected"),
    confidence=e("low", "medium", "medium_high", "high"),
    identity_known=b("is the real-world identity of the operator known from this data"),
    statement_for_report=s("one or two sentences for the case report"),
    what_would_strengthen_it=arr(s()),
    explanation=s(),
)

D8_TEXT = f"""Decision: one address paid TRX (network fees) to several addresses of the traced route. Decide what this
link means, how it must be stated in the report and with what confidence. {COMMON_RULES}"""


def score_d8(o: Any, ctx: TaskContext) -> Score:
    links = fixture()["links"][0]
    want = {f["addr"] for f in links["funded"]}
    got = {a for a in (_get(o, "funded_addresses") or []) if isinstance(a, str)}
    sc = Score(critical=("same_operator_status", "identity_known", "funded_addresses"))
    sc.add("link_type", _get(o, "link_type") == "common_trx_funder")
    sc.add("funder", same_identifier(_get(o, "funder"), links["funder"]))
    sc.add("funded_addresses", got == want, sorted(got))
    sc.add("funding_transfers_fact", _get(o, "funding_transfers_status") == "fact")
    sc.add("same_operator_status", _get(o, "same_operator_status") == "hypothesis", _get(o, "same_operator_status"))
    sc.add("confidence", _get(o, "confidence") in ("medium", "medium_high"), _get(o, "confidence"))
    sc.add("identity_known", _get(o, "identity_known") is False)
    sc.add("statement_hedged", mentions_any(_get(o, "statement_for_report", ""), HYPOTHESIS_PATTERNS))
    _no_forbidden(sc, o)
    return sc


# ===================================================================== registry

SPECS = (
    ("D1_mechanism", "Механизм кражи по данным транзакции", D1_TEXT, D1_SCHEMA, score_d1),
    ("D2_split", "Какие ветки вести на развилке 99%/1%", D2_TEXT, D2_SCHEMA, score_d2),
    ("D3_usdt0_exit", "Распознать выход через мост USDT0 (LayerZero)", D3_TEXT, D3_SCHEMA, score_d3),
    ("D4_rango", "Разобрать лог Rango (TRON в ASCII, получатель в байтах)", D4_TEXT, D4_SCHEMA, score_d4),
    ("D5_near_intents", "Депозит NEAR Intents 1Click и получатель в TRON", D5_TEXT, D5_SCHEMA, score_d5),
    ("D6_hub", "TYHeH2: смешанный хаб и кандидат на заморозку", D6_TEXT, D6_SCHEMA, score_d6),
    ("D7_exchange", "Эвристика депозитных адресов биржи (TNJSC23, TCiwRN)", D7_TEXT, D7_SCHEMA, score_d7),
    ("D8_funder", "Общий источник газа TVNMa2 как гипотеза", D8_TEXT, D8_SCHEMA, score_d8),
)

EXPECTED_SUMMARY = {
    "D1_mechanism": {"mechanism": "private_key_or_seed_compromise", "signer_permission": "owner", "account_permissions_changed": False},
    "D2_split": {"main_route_next_address": "TUrQNNez22bPosc9NUuNvu7pxVWbziKFYU", "fee_branch": "TRUJEtAFzBWReAUu5L83wFRvxWtrVw3sAz record_as_side_branch"},
    "D3_usdt0_exit": {"bridge": "USDT0_LayerZero_OFT", "recipient": "0x4079047990917F3150353FBd8A13b05b6286926d", "amount_received": "12901.408416"},
    "D4_rango": {"destination_chain": "TRON", "receiver_on_destination_chain": "TYHeH2HQn7pM5fe6aYwG (partial)", "receiver_is_ethereum_address": False},
    "D5_near_intents": {"recipient": "TYHeH2HQn7pM5fe6aYwGabz9x4yizJbwp6", "destination_txid": "d3cd82b7c1ea0a828066f5bb732dd480262e5df6f4ce02f7dfe0791ff65f74c1"},
    "D6_hub": {"classification": "commingled_hub", "freeze_candidate": True, "outflow_attribution": "cannot_be_determined_commingled"},
    "D7_exchange": {"TNJSC23": "exchange_deposit_address WhiteBIT", "TCiwRN": "exchange_deposit_address WhiteBIT", "others": "unknown_insufficient_data"},
    "D8_funder": {"same_operator_status": "hypothesis", "confidence": "medium or medium_high", "identity_known": False},
}


def decision_tasks() -> list[Task]:
    data = inputs()
    return [
        Task(task_id=tid, kind="decision", title_ru=title, instructions=text, schema=schema,
             expected=EXPECTED_SUMMARY[tid], scorer=scorer, data=data[tid])
        for tid, title, text, schema, scorer in SPECS
    ]
