"""Step 4: compare the reference run with the fixture's ground_truth, item by item.

Verdicts: ``match`` / ``partial`` / ``mismatch``. Differences are reported, never adjusted.
"""

from __future__ import annotations

import re
from decimal import Decimal
from typing import Any

_ADDR = re.compile(r"(0x[0-9a-fA-F]{40}|T[1-9A-HJ-NP-Za-km-z]{33})")
_PREFIX = re.compile(r"\b(T[1-9A-HJ-NP-Za-km-z]{4,}|0x[0-9a-fA-F]{4,})\.\.\.")
_AMOUNT = re.compile(r"\b\d+\.\d+\b")


def _lc(a: str | None) -> str:
    return (a or "").lower()


def _row(item: str, expected: Any, observed: Any, verdict: str, note: str | None = None) -> dict[str, Any]:
    return {"item": item, "expected": expected, "observed": observed, "verdict": verdict, "note": note}


def compare(fx: dict[str, Any], ref: dict[str, Any]) -> list[dict[str, Any]]:
    gt = fx["ground_truth"]
    r = ref["result"]
    rows: list[dict[str, Any]] = []

    # -- route
    exp_route = []
    for s in gt["expected_route"]:
        via = re.match(r"\[(.+?)\]", s)
        exp_route.append({"address": _ADDR.findall(s)[-1], "via": via.group(1) if via else None})
    obs_route = [{"address": x["address"], "via": x.get("via"), "role": x.get("role")} for x in r["route"]]
    same = [_lc(a["address"]) for a in exp_route] == [_lc(b["address"]) for b in obs_route]
    rows.append(_row("route (addresses in order)", [a["address"] for a in exp_route],
                     [b["address"] for b in obs_route], "match" if same else "mismatch"))
    exp_labels = {a["address"]: a["via"] for a in exp_route if a["via"]}
    obs_labels = {b["address"]: b["via"] for b in obs_route if b["via"]}
    all_found = all(lbl in obs_labels.values() for lbl in exp_labels.values())
    rows.append(_row("route: bridge labels on cross-chain hops", exp_labels, obs_labels,
                     "match" if all_found and exp_labels == {k: v for k, v in obs_labels.items() if k in exp_labels}
                     else ("partial" if all_found else "mismatch"),
                     "the reference run labels each address with the hop that delivered funds INTO it; the fixture "
                     "may place a label on a neighbouring address"))

    # -- side branches
    side = r["side_branches"]

    def side_found(prefix: str, amount: str) -> dict[str, Any] | None:
        return next((s for s in side if (s.get("to") or "").startswith(prefix) and s.get("amount") == amount), None)

    for s in gt["expected_side_branches"]:
        pref = _PREFIX.findall(s)
        amounts = _AMOUNT.findall(s)
        if pref and amounts:
            hits = {a: side_found(pref[0], a) for a in amounts}
            ok = all(hits.values())
            rows.append(_row(f"side branch: {s}", amounts,
                             {a: (h["branch"] if h else None) for a, h in hits.items()}, "match" if ok else "mismatch"))
        else:  # "bridge fees"
            fees = [x for x in side if x.get("branch") == "bridge fee"]
            rows.append(_row(f"side branch: {s}", "bridge fees on each bridge hop",
                             [f"{x['protocol']}: {x['amount']}" for x in fees], "match" if len(fees) >= 2 else "partial"))

    # -- cross-chain detection
    xc = r["cross_chain"]
    oft = next((x for x in xc if x["protocol"].startswith("USDT0")), None)
    rows.append(_row("cross-chain: USDT0 OFT TRON->Ethereum (dstEid 30101)", "dstEid 30101, tron->ethereum",
                     f"dstEid {oft['dstEid']}, {oft['src_chain']}->{oft['dst_chain']}, recipient {oft.get('recipient')}, "
                     f"LayerZero Scan {oft.get('layerzero_scan_status')}" if oft else None,
                     "match" if oft and oft["dstEid"] == 30101 and oft["dst_chain"] == "ethereum" else "mismatch"))
    rg = next((x for x in xc if x["protocol"].startswith("Rango")), None)
    rows.append(_row("cross-chain: Rango destinationChainId=1414680398 ('TRON') and ASCII receiver",
                     "1414680398 / TRON / ASCII receiver",
                     f"{rg['destinationChainId']} / {rg['destinationChainId_ascii']} / {rg['receiver_ascii']}" if rg else None,
                     "match" if rg and rg["destinationChainId"] == 1414680398 and rg["destinationChainId_ascii"] == "TRON"
                     and rg["receiver_ascii"] else "mismatch",
                     "the ASCII receiver holds only the first 20 characters of the TRON address; the full recipient "
                     "comes from the NEAR Intents 1Click status"))
    ni = next((x for x in xc if x["protocol"].startswith("NEAR")), None)
    exp_dep = next(t["from"] for t in fx["transactions"] if t.get("near_intents"))
    rows.append(_row("cross-chain: NEAR Intents 1Click deposit address", exp_dep,
                     f"{ni['deposit_address']} -> {ni['recipient']} (dst tx {ni.get('dst_tx_onchain')})" if ni else None,
                     "match" if ni and _lc(ni["deposit_address"]) == _lc(exp_dep) else "mismatch"))

    # -- exchange exits
    exits = r["exchange_exits"]
    exp_exit_prefixes = _PREFIX.findall(gt["expected_exchange_exits"][0])
    found = {p: next((e for e in exits if e["recipient"].startswith(p)), None) for p in exp_exit_prefixes}
    rows.append(_row("exchange exits: " + gt["expected_exchange_exits"][0], exp_exit_prefixes,
                     {p: (f"{e['exchange']} via {e['hot_wallet']} (forward {e['forward_delay_s']} s, tx "
                          f"{e['forward_txids'][0][:12]})" if e else None) for p, e in found.items()},
                     "match" if all(e and e["exchange"] == "WhiteBIT" for e in found.values()) else "mismatch",
                     "commingled hub outflows; exchange identity comes from the labelled hot wallet (TronScan tag, "
                     "pending written consent)"))
    extra = [x for x in r["hub_outflow_checks"] if x["verdict"] == "deposit_pattern_unlabelled_destination"]
    if extra:
        rows.append(_row("extra: hub outflows with a deposit-like pattern to an unlabelled address",
                         "not traced in the fixture (steps 20-21: 'Not traced further')",
                         [f"{x['recipient']} -> {x['hot_wallet']} {x['amount']} after {x['forward_delay_s']} s"
                          for x in extra], "partial", "new observation, not a contradiction: destination is not "
                                                      "labelled, so no exchange is attributed"))

    # -- freeze candidate
    fc = r["freeze_candidates"]
    exp_fc = _ADDR.findall(gt["expected_freeze_candidate"])[0]
    rows.append(_row("freeze candidate", gt["expected_freeze_candidate"],
                     [f"{x['address']} ({x['asset']}, commingled)" for x in fc],
                     "match" if any(x["address"] == exp_fc for x in fc) else "mismatch"))

    # -- mechanism
    m = r["mechanism"]
    rows.append(_row("mechanism", gt["expected_mechanism"],
                     f"signatures={m['signature_count']}, signer={m['recovered_signers']}, permission={m['permission_used']}, "
                     f"permission updates={len(m['permission_update_txids'])}, owner keys={m['owner_permission']['keys']}",
                     "match" if m["signed_by_victim_owner_key"] and m["permissions_unchanged"] else "mismatch"))

    # -- total fees
    va = r["value_accounting"]
    rows.append(_row("total_fees_lost_before_hub", gt["total_fees_lost_before_hub"], va["total_lost_before_hub"],
                     "match" if va["total_lost_before_hub"] is not None
                     and Decimal(va["total_lost_before_hub"]) == Decimal(gt["total_fees_lost_before_hub"]) else "mismatch",
                     f"components reconcile: {va['components_reconcile']}"))

    # -- common funder link (section 3 of the decisions; not in ground_truth keys)
    link = next((x for x in r["links"] if x["type"] == "common_trx_funder"), None)
    exp_link = fx["links"][0]
    rows.append(_row("common TRX funder (likely same operator, with confidence)",
                     f"{exp_link['funder']} funds {[f['addr'] for f in exp_link['funded']]}; fixture confidence: "
                     + next((a["confidence"] for a in fx["addresses"] if a["address"] == exp_link["funder"]), "?"),
                     f"{link['funder']} funds {[f['address'] for f in link['funded']]}; confidence {link['confidence']} "
                     f"(score {link['score']}; funder fan-out {link['funder_fanout_distinct_trx_recipients']} distinct "
                     f"TRX recipients)" if link else None,
                     _funder_verdict(link, exp_link, fx),
                     "funder fan-out (distinct TRX recipients) lowers the score: the funder also tops up many "
                     "other addresses, as a funding service would" if link else None))
    return rows


def _funder_verdict(link: dict[str, Any] | None, exp_link: dict[str, Any], fx: dict[str, Any]) -> str:
    if not link:
        return "mismatch"
    same_set = link["funder"] == exp_link["funder"] and sorted(f["address"] for f in link["funded"]) == sorted(
        f["addr"] for f in exp_link["funded"])
    if not same_set:
        return "mismatch"
    fixture_conf = next((a["confidence"] for a in fx["addresses"] if a["address"] == exp_link["funder"]), "")
    return "match" if fixture_conf.split(" ")[0] == link["confidence"] else "partial"


def coverage(fx: dict[str, Any], ref: dict[str, Any]) -> list[dict[str, Any]]:
    """Which fixture transactions the reference run reached, and with what values."""
    r = ref["result"]
    edges = {e["txid"].lower(): e for e in r["edges"]}
    ctx = r["theft_context"]
    ctx_ids = {(ctx.get("incoming_before_theft") or {}).get("txid")} | {x["txid"] for x in ctx["resources_received_before_theft"]}
    exits = {}
    for x in r["hub_outflow_checks"]:
        exits[x["hub_outflow_txid"]] = x
        for t in x["forward_txids"]:
            exits[t] = x
    out = []
    for t in fx["transactions"]:
        txid = t["txid"].lower()
        e = edges.get(txid)
        how = None
        obs = None
        if e:
            how = f"edge {e['n']} ({e['kind']})"
            obs = {"from": e["from"], "to": e["to"], "amount": e["amount"], "timestamp_utc": e["timestamp_utc"]}
        elif txid in ctx_ids:
            how = "theft context (victim side)"
        elif t["txid"] in exits:
            x = exits[t["txid"]]
            how = f"hub outflow check: {x['verdict']}"
            obs = {"timestamp_utc": x["hub_outflow_utc"] if x["hub_outflow_txid"] == t["txid"] else None,
                   "amount": x["amount"]}
        elif any(t["txid"] in (c.get("near_txs") or []) for c in r["cross_chain"]):
            how = "listed by a bridge API"
        diffs = []
        if obs:
            for k in ("from", "to", "amount", "timestamp_utc"):
                if obs.get(k) is not None and k in t and str(obs[k]).lower() != str(t[k]).lower():
                    diffs.append(f"{k}: fixture {t[k]} vs reference {obs[k]}")
        out.append({"step": t["step"], "txid": t["txid"], "kind": t["kind"], "reached": how is not None,
                    "how": how or "not reached (not needed by the rules)", "differences": diffs})
    return out
