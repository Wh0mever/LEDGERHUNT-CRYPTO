"""Report generation: narrative sections of the case-001 report from verified facts.

Score: no invented identifiers; every node of the expected route (ground_truth.expected_route) and every
main-route transaction is mentioned; the three bridges are named; side-branch fees and the total loss are
right; commingling is stated as an uncertainty; the common funder is presented as a hypothesis; no claims
of recovery or identification.
"""

from __future__ import annotations

import re
from typing import Any

from ..identifiers import same_identifier
from ..scoring import (COMMINGLED_PATTERNS, HYPOTHESIS_PATTERNS, Score, all_text, amount_eq, forbidden_claims,
                       mentions_any)
from . import Task, TaskContext
from .decisions import fixture, inputs, step
from .schema import arr, i, obj, s

REPORT_SCHEMA = obj(
    title=s(),
    executive_summary=s("5-8 sentences"),
    mechanism=s(),
    route_steps=arr(obj(order=i(), chain=s(), from_address=s(), to_address=s(), txid=s(), amount=s(),
                        asset=s(), time_utc=s(), note=s())),
    cross_chain_section=s(),
    side_branches_section=s(),
    hub_and_freeze_section=s(),
    exchange_exits_section=s(),
    links_and_hypotheses_section=s(),
    uncertainties=arr(s()),
    recommended_actions=arr(s()),
    limitations=s(),
)

REPORT_TEXT = """Write the narrative sections of the investigation report for case-001 from the verified facts above.
The report will be read by the victim, by exchange security teams and by the police; an operator reviews it first.
- route_steps: one entry per transaction of the verified route, in order, with exact identifiers and amounts.
- Name each bridge or swap service and what the data shows at each cross-chain step.
- side_branches_section: the side branches with their amounts and the total lost between the theft and the hub.
- hub_and_freeze_section: why the hub address is a freeze candidate and what is uncertain about the funds there.
- exchange_exits_section: what the exchange deposits mean for the investigation.
- links_and_hypotheses_section: links between addresses with their status (fact or hypothesis) and confidence.
- recommended_actions: concrete requests (freeze request through law enforcement, exchange notification, ...).
Use only the facts provided. Plain, precise English. No promises about outcomes."""

BRIDGE_PATTERNS = {
    "usdt0_layerzero": (r"usdt0", r"layer\s?zero"),
    "rango": (r"rango",),
    "near_intents": (r"near intents", r"1click", r"near-intents"),
}


def score_report(o: Any, ctx: TaskContext) -> Score:
    fx = fixture()
    text = all_text(o)
    sc = Score(critical=("route_nodes_mentioned", "commingling_stated", "no_recovery_or_identity_claims"))
    nodes = [re.sub(r"^\[[^\]]+\]\s*", "", n) for n in fx["ground_truth"]["expected_route"]]
    lower = text.lower()
    missing = [n for n in nodes if (n.lower() not in lower if n.startswith("0x") else n not in text)]
    sc.add("route_nodes_mentioned", not missing, missing or None)
    route_txids = [step(n)["txid"] for n in (6, 8, 9, 12, 14, 15, 16, 17)]
    steps_out = [x for x in (o.get("route_steps") or []) if isinstance(x, dict)]
    got = [x.get("txid", "") for x in steps_out]
    found = [t for t in route_txids if any(same_identifier(g, t) for g in got)]
    sc.add("route_txids_in_steps", len(found) / len(route_txids), [t for t in route_txids if t not in found] or None)
    amount_ok = 0
    for n in (6, 8, 9, 12, 14, 15, 16, 17):
        st = step(n)
        row = next((x for x in steps_out if same_identifier(x.get("txid"), st["txid"])), None)
        if row is not None and amount_eq(row.get("amount"), st["amount"]):
            amount_ok += 1
    sc.add("route_amounts_exact", amount_ok / 8)
    for name, pats in BRIDGE_PATTERNS.items():
        sc.add(f"bridge_named_{name}", mentions_any(text, pats))
    sc.add("fee_1pct_amount", "130.356401" in text)
    sc.add("affiliate_fee_amount", "19.352116" in text)
    total = fx["ground_truth"]["total_fees_lost_before_hub"]
    sc.add("total_lost_amount", bool(re.search(r"162\.94587(0)?\b", text)), total)
    hub_txt = str(o.get("hub_and_freeze_section", "")) + "\n" + "\n".join(map(str, o.get("uncertainties") or []))
    sc.add("commingling_stated", mentions_any(hub_txt, COMMINGLED_PATTERNS))
    sc.add("freeze_candidate_named", "TYHeH2HQn7pM5fe6aYwGabz9x4yizJbwp6" in str(o.get("hub_and_freeze_section", "")))
    sc.add("exchange_deposits_named", all(a in text for a in ("TNJSC23oMcb5ws9tppANFTGtEDcKQgQBYQ",
                                                               "TCiwRNyeUK7JwkEgF5W3AExFpZ2ErRZG4C")))
    sc.add("funder_as_hypothesis", mentions_any(str(o.get("links_and_hypotheses_section", "")), HYPOTHESIS_PATTERNS))
    hits = forbidden_claims(text)
    sc.add("no_recovery_or_identity_claims", not hits, hits or None)
    return sc


def report_tasks() -> list[Task]:
    return [Task(
        task_id="R1_report", kind="report", title_ru="Генерация разделов отчёта по case-001",
        instructions=REPORT_TEXT, schema=REPORT_SCHEMA,
        expected={"route": fixture()["ground_truth"]["expected_route"], "total_lost": fixture()["ground_truth"]["total_fees_lost_before_hub"]},
        scorer=score_report, data=inputs()["R1_report"],
    )]
