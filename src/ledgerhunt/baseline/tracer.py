"""Deterministic reference tracer (no AI): reconstructs a theft route from one TXID using raw data.

Input: a starting TXID (TRON USDT transfer signed by the victim), the registry in
``registry.py`` (known tokens, bridge contracts/APIs, exchange hot-wallet labels with sources,
thresholds). Output: a JSON-ready dict with the route, side branches, cross-chain hops, hub /
freeze candidate, exchange exits, the common-funder link (with a confidence level, not a fact),
value accounting, the mechanism check and the evidence (raw response hashes) behind each item.

Generic rules (all thresholds in ``registry.THRESHOLDS``):

1. Start: decode the transaction and its receipt; the token Transfer sent by the signer is the
   theft. Mechanism: count signatures, Permission_id, recover the signer from the signature,
   read the victim's permissions and look for permission updates in its history.
2. Follow (per holder H, tainted amount A that arrived at time T): take H's outgoing USDT
   transfers after T in time order until their sum reaches A*(1-tolerance) (same-second batch
   included). Each taken outflow: >= 20% of A -> followed branch; == A*1% at token precision
   (floor or half-up) -> exact cut;
   <= 1 USDT -> dust; otherwise side branch. Not taken: left on H (residual).
3. Bridges are detected by events in the receipt of a followed transfer (OFTSent,
   RangoBridgeInitiated) or by a bridge API that recognises the holder as a deposit address
   (NEAR Intents 1Click). The other side is read only for the bridge segment.
4. Hub (stop): H has >= 10 distinct USDT counterparties or >= 5*A other USDT volume in the 24 h
   after arrival. A TRON hub holding USDT-TRC20 is a freeze candidate (commingled).
5. Exchange exit: a hub outflow whose recipient forwards >= 99% of it within 1 h to a single
   address with few counterparties is a deposit pattern; it is an exchange exit when that
   address is a labelled hot wallet (label and its source are inputs).
6. Common TRX funder: senders of the activation transfer or of >= 1 TRX to >= 2 thief-side
   holders, excluding funders of the victim; scored into a confidence level.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any

from ..core.evm import USDT_ERC20
from ..core.tron import USDT_TRC20
from ..sources.layerzero_scan import messages as lz_messages
from .chain import (
    ascii_of_address_bytes,
    ascii_of_uint,
    blockscout_transfer_rows,
    evm_logs_from_blockscout,
    evm_logs_from_receipt,
    evm_token_transfers,
    fmt,
    is_exact_cut,
    parse_ts,
    same_evm,
    trunc_share,
    tron_contract,
    tron_logs,
    tron_token_transfers,
    ts_utc,
    v1_native_rows,
    v1_transfer_rows,
)
from .fetch import CaseSources
from .registry import (
    ALGORITHM_VERSION,
    BRIDGE_REGISTRY,
    EVENT_SOURCES,
    EXCHANGE_HOT_WALLETS,
    FUNDER_CONFIDENCE_LEVELS,
    LAYERZERO_EIDS,
    NEAR_ASSET_CHAINS,
    THRESHOLDS,
)
from .sigcheck import check_tron_signatures

USDT_BY_CHAIN = {"tron": USDT_TRC20, "ethereum": USDT_ERC20}
ASSET_BY_CHAIN = {"tron": "USDT-TRC20", "ethereum": "USDT-ERC20"}


@dataclass
class Holder:
    """An address that received tainted funds: where to continue tracing."""

    chain: str
    address: str
    amount: int  # tainted amount that arrived (6-decimal base units)
    ts: int  # arrival time, ms since epoch
    via_txid: str
    via: str | None = None  # bridge / protocol that delivered the funds, None for a plain transfer
    segment: int = 0  # number of cross-chain hops before this holder
    hint: dict[str, Any] = field(default_factory=dict)


def _same(chain: str, a: str | None, b: str | None) -> bool:
    return same_evm(a, b) if chain != "tron" else a == b


class ReferenceTracer:
    def __init__(self, src: CaseSources, *, thresholds: dict[str, Any] | None = None,
                 hot_wallets: dict[str, dict[str, str]] | None = None) -> None:
        self.src = src
        self.t = dict(THRESHOLDS if thresholds is None else thresholds)
        self.hot_wallets = dict(EXCHANGE_HOT_WALLETS if hot_wallets is None else hot_wallets)
        self.edges: list[dict[str, Any]] = []
        self.side_branches: list[dict[str, Any]] = []
        self.cross_chain: list[dict[str, Any]] = []
        self.route: list[dict[str, Any]] = []
        self.holders: list[Holder] = []
        self.accounting: list[dict[str, Any]] = []
        self.boundaries: list[str] = []
        self.hubs: list[dict[str, Any]] = []
        self.exits: list[dict[str, Any]] = []
        self.hub_outflow_checks: list[dict[str, Any]] = []
        self.links: list[dict[str, Any]] = []
        self.live: dict[str, Any] = {}
        self._visited: set[tuple[str, str, str]] = set()

    # ================================================================ public
    def run(self, start_txid: str) -> dict[str, Any]:
        with self.src.step("1 start: theft transaction"):
            start, first = self._start(start_txid)
        with self.src.step("2 victim: mechanism and theft context"):
            mechanism = self._mechanism(start)
            context = self._theft_context(start)
        queue = [first]
        n = 0
        while queue:
            h = queue.pop(0)
            key = (h.chain, h.address.lower(), h.via_txid)
            if key in self._visited:
                continue
            self._visited.add(key)
            n += 1
            with self.src.step(f"3.{n} holder {h.chain}:{h.address}"):
                queue.extend(self._visit(h))
        with self.src.step("4 hub outflows: exchange exit heuristic"):
            for hub in self.hubs:
                self._hub_exits(hub)
        with self.src.step("5 common TRX funder"):
            self._common_funder(start)
        with self.src.step("6 freeze candidate: live balance (informational)"):
            freeze = self._freeze_candidates()
        accounting = self._value_accounting(start)
        result = {
            "start": start,
            "victim": start["from"],
            "mechanism": mechanism,
            "theft_context": context,
            "route": self.route,
            "edges": self.edges,
            "side_branches": self.side_branches,
            "cross_chain": self.cross_chain,
            "hubs": [{k: v for k, v in h.items() if not k.startswith("_")} for h in self.hubs],
            "freeze_candidates": freeze,
            "exchange_exits": self.exits,
            "hub_outflow_checks": self.hub_outflow_checks,
            "links": self.links,
            "value_accounting": accounting,
            "evidence_boundaries": self.boundaries,
        }
        return {
            "meta": {
                "algorithm": ALGORITHM_VERSION,
                "start_txid": start_txid,
                "thresholds": self.t,
                "bridge_registry": BRIDGE_REGISTRY,
                "event_sources": EVENT_SOURCES,
                "layerzero_eids": {str(k): v for k, v in LAYERZERO_EIDS.items()},
                "exchange_hot_wallet_labels": self.hot_wallets,
                "ai_used": False,
            },
            "result": result,
            "evidence": self.src.evidence,
            "live_observations": self.live,
            "timings": self.src.timings(),
        }

    # ================================================================ 1. start
    def _start(self, txid: str) -> tuple[dict[str, Any], Holder]:
        tx, e_tx = self.src.tron_tx(txid)
        info, e_info = self.src.tron_info(txid)
        c = tron_contract(tx)
        signer = c.get("owner")
        transfers = [t for t in tron_token_transfers(info) if t["asset"] == "USDT-TRC20" and t["from"] == signer]
        if not transfers:
            raise ValueError(f"start transaction {txid} has no USDT-TRC20 transfer sent by its signer")
        t = transfers[0]
        call = c.get("call") or {}
        start = {
            "txid": txid,
            "chain": "tron",
            "block": info.get("blockNumber"),
            "timestamp_utc": ts_utc(info.get("blockTimeStamp")),
            "from": t["from"],
            "to": t["to"],
            "amount": fmt(t["value"]),
            "asset": t["asset"],
            "contract_ret": c.get("ret"),
            "receipt_result": (info.get("receipt") or {}).get("result"),
            "calldata_matches_log": call.get("method") == "transfer" and call.get("to") == t["to"]
                                    and call.get("value") == t["value"],
            "fee_trx": fmt(int(info.get("fee") or 0)),
            "energy_usage_total": (info.get("receipt") or {}).get("energy_usage_total"),
            "evidence": [e_tx, e_info],
        }
        self.route.append({"chain": "tron", "address": t["from"], "role": "victim", "via": None})
        self._edge("tron", txid, t["from"], t["to"], t["value"], info.get("blockTimeStamp"), info.get("blockNumber"),
                   "theft", [e_tx, e_info])
        first = Holder("tron", t["to"], t["value"], int(info["blockTimeStamp"]), txid)
        return start, first

    def _mechanism(self, start: dict[str, Any]) -> dict[str, Any]:
        victim = start["from"]
        tx, e_tx = self.src.tron_tx(start["txid"])
        c = tron_contract(tx)
        sig = check_tron_signatures(tx)
        acct, e_acct = self.src.tron_account(victim)
        owner = acct.get("owner_permission") or {}
        actives = acct.get("active_permission") or []
        rows, complete, e_hist = self.src.account_txs(victim, only_from=True, limit=200,
                                                      max_pages=int(self.t["max_pages"]))
        updates = [r["txid"] for r in v1_native_rows(rows) if r["type"] == "AccountPermissionUpdateContract"]
        keys_self = all(k.get("address") == victim for k in (owner.get("keys") or [])) and all(
            k.get("address") == victim for p in actives for k in (p.get("keys") or []))
        pid = c.get("permission_id") or 0
        signed_by_owner = sig["signers"] == [victim] and pid == 0
        unchanged = keys_self and not updates and owner.get("threshold") == 1
        return {
            "signature_count": sig["signature_count"],
            "txid_matches_raw_data": sig["txid_matches_raw_data"],
            "recovered_signers": sig["signers"],
            "permission_id": pid,
            "permission_used": "owner" if pid == 0 else f"permission id {pid}",
            "owner_permission": {"threshold": owner.get("threshold"),
                                 "keys": [k.get("address") for k in owner.get("keys") or []]},
            "active_permissions": [{"id": p.get("id"), "threshold": p.get("threshold"),
                                    "keys": [k.get("address") for k in p.get("keys") or []]} for p in actives],
            "permission_update_txids": updates,
            "outgoing_history_complete": complete,
            "outgoing_history_rows": len(rows),
            "signed_by_victim_owner_key": signed_by_owner,
            "permissions_unchanged": unchanged,
            "conclusion": ("transaction signed with the victim's own owner key; permissions never changed -> "
                           "key/seed compromise (not a permission takeover)")
            if signed_by_owner and unchanged else "inconclusive: see fields",
            "evidence": [e_tx, e_acct, e_hist],
        }

    def _theft_context(self, start: dict[str, Any]) -> dict[str, Any]:
        victim = start["from"]
        ts = parse_ts(start["timestamp_utc"])
        w = int(self.t["theft_context_window_s"]) * 1000
        look = int(self.t["incoming_lookback_s"]) * 1000
        native_rows, _, e_native = self.src.account_txs(victim, min_ms=ts - w, max_ms=ts + w, limit=50)
        trc_rows, _, e_trc = self.src.trc20_window(victim, USDT_TRC20, ts - look, ts + w,
                                                    limit=int(self.t["trc20_page_limit"]),
                                                    max_pages=int(self.t["max_pages"]))
        transfers = v1_transfer_rows(trc_rows, USDT_TRC20)
        incoming = [r for r in transfers if r["to"] == victim and r["ts"] <= ts]
        last_in = incoming[-1] if incoming else None
        resources = []
        for r in v1_native_rows(native_rows):
            if r["to"] == victim and r["owner"] != victim and r["ts"] <= ts:
                resources.append({"txid": r["txid"], "type": r["type"], "from": r["owner"],
                                  "timestamp_utc": ts_utc(r["ts"]), "amount_sun": r["amount_sun"],
                                  "resource": r["resource"], "seconds_before_theft": (ts - r["ts"]) // 1000})
        other_out = []
        for r in transfers:
            if r["from"] == victim and r["txid"] != start["txid"] and abs(r["ts"] - ts) <= w:
                tx, e_tx = self.src.tron_tx(r["txid"])
                sig = check_tron_signatures(tx)
                pid = tron_contract(tx).get("permission_id") or 0
                item = {"txid": r["txid"], "from": victim, "to": r["to"], "amount": fmt(r["value"]),
                        "asset": "USDT-TRC20", "timestamp_utc": ts_utc(r["ts"]), "kind": "victim_side_outflow",
                        "signed_by": sig["signers"], "permission_id": pid, "evidence": [e_trc, e_tx]}
                other_out.append(item)
                self.side_branches.append({**item, "branch": "victim-side outflow signed with the victim key "
                                                             "in the theft window", "counted_in_theft_loss": False})
                self._edge("tron", r["txid"], victim, r["to"], r["value"], r["ts"], None, "victim_side_outflow",
                           [e_trc, e_tx])
        return {
            "incoming_before_theft": {
                "txid": last_in["txid"], "from": last_in["from"], "amount": fmt(last_in["value"]),
                "timestamp_utc": ts_utc(last_in["ts"]), "seconds_before_theft": (ts - last_in["ts"]) // 1000,
            } if last_in else None,
            "resources_received_before_theft": resources,
            "other_victim_outflows_in_window": other_out,
            "evidence": [e_native, e_trc],
        }

    # ================================================================ 2. follow
    def _visit(self, h: Holder) -> list[Holder]:
        self.holders.append(h)
        if h.chain == "tron":
            return self._visit_tron(h)
        return self._visit_evm(h)

    def _route_add(self, h: Holder, role: str) -> None:
        self.route.append({"chain": h.chain, "address": h.address, "role": role, "via": h.via,
                           "arrived_amount": fmt(h.amount), "arrived_utc": ts_utc(h.ts), "arrived_txid": h.via_txid})

    def _hub_check(self, h: Holder, transfers: list[dict[str, Any]], complete: bool) -> dict[str, Any]:
        end = h.ts + int(self.t["hub_window_s"]) * 1000
        others = [r for r in transfers if r["txid"] != h.via_txid and h.ts <= r["ts"] <= end]
        cps = {(r["to"] if _same(h.chain, r["from"], h.address) else r["from"]) for r in others}
        volume = sum(r["value"] for r in others)
        by_cp = len(cps) >= int(self.t["hub_min_counterparties"])
        by_vol = volume >= int(self.t["hub_volume_multiple"]) * h.amount
        return {"window_utc": [ts_utc(h.ts), ts_utc(end)], "other_transfers": len(others),
                "distinct_counterparties": len(cps), "other_volume": fmt(volume),
                "volume_multiple_of_tainted": str((Decimal(volume) / Decimal(h.amount)).quantize(Decimal("0.01")))
                if h.amount else None,
                "rule_counterparties": by_cp, "rule_volume": by_vol, "is_hub": by_cp or by_vol,
                "listing_complete": complete}

    def _allocate(self, h: Holder, outflows: list[dict[str, Any]]) -> tuple[list[dict], list[dict], int]:
        """Chronological drain allocation. Returns (taken with class, remainder dust, residual)."""
        tol = trunc_share(h.amount, str(self.t["drain_tolerance_share"]))
        target = h.amount - tol
        taken: list[dict[str, Any]] = []
        cum = 0
        done_ts = None
        for r in outflows:
            if done_ts is not None and r["ts"] != done_ts:
                break
            taken.append(dict(r))
            cum += r["value"]
            if done_ts is None and cum >= target:
                done_ts = r["ts"]
        dust_max = int(Decimal(str(self.t["dust_max_amount"])).scaleb(6))
        remainder = []
        if done_ts is not None:
            rem_end = done_ts + int(self.t["remainder_window_s"]) * 1000
            remainder = [dict(r) for r in outflows[len(taken):] if r["ts"] <= rem_end and r["value"] <= dust_max]
        else:
            self.boundaries.append(f"{h.chain}:{h.address}: outflows in the follow window do not reach the tainted "
                                   f"amount {fmt(h.amount)}; the rest stays unallocated")
        follow_min = Decimal(str(self.t["follow_min_share"]))
        for r in taken:
            cut = next((s for s in self.t["exact_cut_shares"] if is_exact_cut(r["value"], h.amount, s)), None)
            if r["value"] <= dust_max:
                r["class"] = "dust"
            elif cut is not None:
                r["class"] = "exact_cut"
                r["cut_share"] = cut
            elif Decimal(r["value"]) >= follow_min * Decimal(h.amount):
                r["class"] = "follow"
            else:
                r["class"] = "side"
        residual = h.amount - sum(r["value"] for r in taken)
        return taken, remainder, residual

    def _visit_tron(self, h: Holder) -> list[Holder]:
        end = h.ts + int(self.t["hub_window_s"]) * 1000
        rows, complete, e_list = self.src.trc20_window(h.address, USDT_TRC20, h.ts, end,
                                                       limit=int(self.t["trc20_page_limit"]),
                                                       max_pages=int(self.t["max_pages"]))
        transfers = v1_transfer_rows(rows, USDT_TRC20)
        hub = self._hub_check(h, transfers, complete)
        if hub["is_hub"]:
            self._route_add(h, "hub (stop)")
            self.hubs.append({"chain": h.chain, "address": h.address, "arrived_amount": fmt(h.amount),
                              "arrived_utc": ts_utc(h.ts), "arrived_txid": h.via_txid, "metrics": hub,
                              "decision": "stop: high-volume address, stolen funds commingled",
                              "evidence": [e_list], "_holder": h, "_transfers": transfers})
            return []
        self._route_add(h, "holder")
        follow_end = h.ts + int(self.t["follow_window_s"]) * 1000
        outflows = [r for r in transfers if r["from"] == h.address and h.ts <= r["ts"] <= follow_end
                    and r["txid"] != h.via_txid]
        taken, remainder, residual = self._allocate(h, outflows)
        out: list[Holder] = []
        for r in taken:
            if r["class"] != "follow":
                self._side(h, r, e_list)
                continue
            out.extend(self._follow_tron_outflow(h, r, e_list))
        for r in remainder:
            r["class"] = "remainder_dust"
            self._side(h, r, e_list)
        self._account(h, taken, residual)
        return out

    def _follow_tron_outflow(self, h: Holder, r: dict[str, Any], e_list: str) -> list[Holder]:
        info, e_info = self.src.tron_info(r["txid"])
        logs = tron_logs(info)
        confirmed = any(t["from"] == h.address and t["to"] == r["to"] and t["value"] == r["value"]
                        for t in tron_token_transfers(info))
        oft = [lg for lg in logs if lg["decoded"] and lg["decoded"]["event"] == "OFTSent"]
        if oft:
            self._edge("tron", r["txid"], h.address, r["to"], r["value"], r["ts"], info.get("blockNumber"),
                       "bridge_out", [e_list, e_info], confirmed_by_receipt=confirmed)
            return self._resolve_oft_from_tron(h, r, info, oft[0], e_info)
        unknown = [lg for lg in logs if lg["decoded"] is None]
        if unknown:
            self.boundaries.append(f"tron tx {r['txid']}: {len(unknown)} log(s) from contract(s) not in the "
                                   f"registry; treated as a plain transfer")
        self._edge("tron", r["txid"], h.address, r["to"], r["value"], r["ts"], info.get("blockNumber"), "hop",
                   [e_list, e_info], confirmed_by_receipt=confirmed)
        return [Holder("tron", r["to"], r["value"], r["ts"], r["txid"], None, h.segment)]

    # ---------------------------------------------------------------- bridges
    def _resolve_oft_from_tron(self, h: Holder, r: dict[str, Any], info: dict[str, Any],
                               oft_log: dict[str, Any], e_info: str) -> list[Holder]:
        ev = oft_log["decoded"]
        tx, e_tx = self.src.tron_tx(r["txid"])
        call = tron_contract(tx).get("call") or {}
        dst_chain = LAYERZERO_EIDS.get(ev["dstEid"])
        known = next((b for b in BRIDGE_REGISTRY if b["chain"] == "tron" and b["address"] == oft_log["emitter"]), None)
        lzf, e_lz = self.src.lz_by_tx(r["txid"])
        msg = next((m for m in lz_messages(lzf) if (m.get("guid") or "").lower() == ev["guid"]), None)
        dst_tx = (((msg or {}).get("destination") or {}).get("tx") or {}).get("txHash")
        item: dict[str, Any] = {
            "protocol": known["protocol"] if known else "LayerZero OFT (unregistered contract)",
            "detected_by": "event OFTSent in the TRON receipt",
            "src_chain": "tron",
            "src_tx": r["txid"],
            "src_contract": oft_log["emitter"],
            "src_contract_registered": known is not None,
            "from": h.address,
            "guid": ev["guid"],
            "dstEid": ev["dstEid"],
            "dst_chain": dst_chain,
            "srcEid": ((msg or {}).get("pathway") or {}).get("srcEid"),
            "amount_sent": fmt(ev["amountSentLD"]),
            "amount_received": fmt(ev["amountReceivedLD"]),
            "bridge_fee": fmt(ev["amountSentLD"] - ev["amountReceivedLD"]),
            "send_calldata_to": call.get("to_bytes32"),
            "send_calldata_dstEid": call.get("dstEid"),
            "layerzero_scan_status": ((msg or {}).get("status") or {}).get("name"),
            "dst_tx": dst_tx,
            "evidence": [e_info, e_tx, e_lz],
        }
        self.cross_chain.append(item)
        self.accounting.append({"what": "bridge fee (USDT0/LayerZero OFT: amountSentLD - amountReceivedLD)",
                                "at": f"{item['protocol']} {r['txid']}",
                                "amount": ev["amountSentLD"] - ev["amountReceivedLD"]})
        self.side_branches.append({"branch": "bridge fee", "protocol": item["protocol"], "txid": r["txid"],
                                   "amount": item["bridge_fee"], "asset": "USDT", "counted_in_theft_loss": True,
                                   "evidence": [e_info]})
        if dst_chain != "ethereum" or not dst_tx:
            self.boundaries.append(f"OFT message {ev['guid']}: destination chain {dst_chain} / tx {dst_tx} not "
                                   f"supported for continuation")
            return []
        logs_items, e_dlogs = self.src.eth_logs(dst_tx)
        dlogs = evm_logs_from_blockscout(logs_items)
        recv = next((lg for lg in dlogs if lg["decoded"] and lg["decoded"]["event"] == "OFTReceived"
                     and lg["decoded"]["guid"] == ev["guid"]), None)
        btx, e_btx = self.src.eth_tx(dst_tx)
        rcpt, e_rcpt = self.src.eth_receipt(dst_tx)
        rlogs = evm_logs_from_receipt(rcpt)
        recv2 = next((lg for lg in rlogs if lg["decoded"] and lg["decoded"]["event"] == "OFTReceived"
                      and lg["decoded"]["guid"] == ev["guid"]), None)
        item["evidence"] += [e_dlogs, e_btx, e_rcpt]
        if recv is None:
            self.boundaries.append(f"OFT message {ev['guid']}: no OFTReceived with this guid in {dst_tx}")
            return []
        to = recv["decoded"]["toAddress"]
        amount = recv["decoded"]["amountReceivedLD"]
        token_in = [t for t in evm_token_transfers(dlogs) if same_evm(t["to"], to) and t["value"] == amount]
        dst_known = next((b for b in BRIDGE_REGISTRY if b["chain"] == "ethereum"
                          and same_evm(b["address"], recv["emitter"])), None)
        ts = parse_ts(btx["timestamp"])
        item.update({
            "recipient": to,
            "dst_contract": recv["emitter"],
            "dst_contract_registered": dst_known is not None,
            "dst_amount_received": fmt(amount),
            "dst_block": btx.get("block_number"),
            "dst_timestamp_utc": ts_utc(ts),
            "dst_status": btx.get("status"),
            "recipient_matches_send_calldata": (item["send_calldata_to"] or "")[-40:].lower() == to[2:].lower(),
            "dst_token_transfer_found": bool(token_in),
            "dst_confirmed_by_second_source": (recv2 is not None and recv2["decoded"]["toAddress"] == to
                                               and recv2["decoded"]["amountReceivedLD"] == amount) if rcpt else None,
            "second_source": "ethereum-rpc.publicnode.com eth_getTransactionReceipt"
                             + ("" if rcpt else ": returned null (no data)"),
        })
        if not rcpt:
            self.boundaries.append(f"ethereum tx {dst_tx}: public RPC receipt returned null; Blockscout only")
        self._edge("ethereum", dst_tx, recv["emitter"], to, amount, ts, btx.get("block_number"), "bridge_in",
                   [e_dlogs, e_btx, e_rcpt], confirmed_by_receipt=item["dst_confirmed_by_second_source"])
        return [Holder("ethereum", to, amount, ts, dst_tx, "USDT0/LayerZero", h.segment + 1)]

    def _visit_evm(self, h: Holder) -> list[Holder]:
        status, e_1c = self.src.oneclick_status(h.address)
        data = status.data if isinstance(status.data, dict) else {}
        if status.status == 200 and data.get("status"):
            return self._resolve_1click(h, data, e_1c)
        rows, complete, e_list = self.src.eth_address_transfers(h.address, USDT_ERC20,
                                                                max_pages=int(self.t["blockscout_max_pages"]),
                                                                stop_before_ms=h.ts)
        transfers = [r for r in blockscout_transfer_rows(rows) if same_evm(r["token"], USDT_ERC20)]
        hub = self._hub_check(h, transfers, complete)
        if hub["is_hub"]:
            self._route_add(h, "hub (stop)")
            self.hubs.append({"chain": h.chain, "address": h.address, "arrived_amount": fmt(h.amount),
                              "arrived_utc": ts_utc(h.ts), "arrived_txid": h.via_txid, "metrics": hub,
                              "decision": "stop: high-volume address", "evidence": [e_list], "_holder": h,
                              "_transfers": transfers})
            return []
        self._route_add(h, "holder")
        follow_end = h.ts + int(self.t["follow_window_s"]) * 1000
        outflows = [r for r in transfers if same_evm(r["from"], h.address) and h.ts <= r["ts"] <= follow_end
                    and r["txid"] != h.via_txid]
        taken, remainder, residual = self._allocate(h, outflows)
        out: list[Holder] = []
        for r in taken:
            if r["class"] != "follow":
                self._side(h, r, e_list)
                continue
            out.extend(self._follow_evm_outflow(h, r, e_list, e_1c))
        for r in remainder:
            r["class"] = "remainder_dust"
            self._side(h, r, e_list)
        self._account(h, taken, residual)
        return out

    def _follow_evm_outflow(self, h: Holder, r: dict[str, Any], e_list: str, e_1c: str) -> list[Holder]:
        items, e_logs = self.src.eth_logs(r["txid"])
        logs = evm_logs_from_blockscout(items)
        rango = next((lg for lg in logs if lg["decoded"] and lg["decoded"]["event"] == "RangoBridgeInitiated"), None)
        if rango is None:
            self._edge("ethereum", r["txid"], h.address, r["to"], r["value"], r["ts"], r["block"], "hop",
                       [e_list, e_logs])
            return [Holder("ethereum", r["to"], r["value"], r["ts"], r["txid"], None, h.segment)]
        ev = rango["decoded"]
        diamond = rango["emitter"]
        known = next((b for b in BRIDGE_REGISTRY if b["chain"] == "ethereum" and same_evm(b["address"], diamond)), None)
        transfers = evm_token_transfers(logs)
        from_diamond = [t for t in transfers if same_evm(t["from"], diamond)]
        forward = next((t for t in from_diamond if t["value"] == ev["bridgeAmount"]), None)
        routed = next((lg["decoded"] for lg in logs if lg["decoded"] and lg["decoded"]["event"] == "Routed"
                       and lg["decoded"]["amount"] == ev["bridgeAmount"]), None)
        fee_infos = [lg["decoded"] for lg in logs if lg["decoded"] and lg["decoded"]["event"] == "FeeInfo"]
        rcpt, e_rcpt = self.src.eth_receipt(r["txid"])
        rlogs = evm_logs_from_receipt(rcpt)
        rango2 = next((lg["decoded"] for lg in rlogs if lg["decoded"]
                       and lg["decoded"]["event"] == "RangoBridgeInitiated"), None)
        receiver_hex = ev["_raw_address_hex"]["receiver"]
        item: dict[str, Any] = {
            "protocol": "Rango (aggregator)",
            "detected_by": "event RangoBridgeInitiated in the transaction logs",
            "src_chain": "ethereum",
            "src_tx": r["txid"],
            "src_contract": diamond,
            "src_contract_registered": known is not None,
            "from": h.address,
            "input_amount": fmt(r["value"]),
            "bridge_amount": fmt(ev["bridgeAmount"]),
            "bridge_token": ev["bridgeToken"],
            "destinationChainId": ev["destinationChainId"],
            "destinationChainId_ascii": ascii_of_uint(ev["destinationChainId"]),
            "receiver_raw": receiver_hex,
            "receiver_ascii": ascii_of_address_bytes(receiver_hex),
            "bridgeId": ev["bridgeId"],
            "dAppTag": ev["dAppTag"],
            "dAppName": ev["dAppName"],
            "hasInterchainMessage": ev["hasInterchainMessage"],
            "hasDestinationSwap": ev["hasDestinationSwap"],
            "forwarded_to": forward["to"] if forward else None,
            "routed_to": routed["to"] if routed else None,
            "affiliate_fees": [{"affiliate": f["affiliatorAddress"], "amount": fmt(f["affiliateFee"]),
                                "dAppTag": f["dAppTag"], "feeType": f["feeType"]} for f in fee_infos],
            "confirmed_by_second_source": (rango2 is not None and rango2["bridgeAmount"] == ev["bridgeAmount"]
                                           and rango2["destinationChainId"] == ev["destinationChainId"])
            if rcpt else None,
            "second_source": "ethereum-rpc.publicnode.com eth_getTransactionReceipt"
                             + ("" if rcpt else ": returned null (no data)"),
            "evidence": [e_list, e_logs, e_rcpt],
        }
        if r["value"]:
            share = Decimal(sum(f["affiliateFee"] for f in fee_infos)) / Decimal(r["value"])
            item["affiliate_fee_share_of_input"] = str((share * 100).quantize(Decimal("0.0001"))) + "%"
        self.cross_chain.append(item)
        self._edge("ethereum", r["txid"], h.address, diamond, r["value"], r["ts"], r["block"], "bridge_out",
                   [e_list, e_logs, e_rcpt], confirmed_by_receipt=item["confirmed_by_second_source"])
        for t in from_diamond:
            if forward is not None and t is forward:
                continue
            self.side_branches.append({"branch": "Rango affiliate fee" if any(
                same_evm(t["to"], f["affiliatorAddress"]) for f in fee_infos) else "Rango side transfer",
                "txid": r["txid"], "from": diamond, "to": t["to"], "amount": fmt(t["value"]), "asset": t["asset"],
                "counted_in_theft_loss": True, "evidence": [e_logs]})
            self.accounting.append({"what": "Rango side transfer (affiliate fee)", "at": r["txid"],
                                    "amount": t["value"]})
        if forward is None:
            self.boundaries.append(f"Rango tx {r['txid']}: no transfer of bridgeAmount from the Diamond found")
            return []
        self._edge("ethereum", r["txid"], diamond, forward["to"], forward["value"], r["ts"], r["block"],
                   "aggregator_forward", [e_logs])
        hint = {"destination_chain_ascii": item["destinationChainId_ascii"], "receiver_ascii": item["receiver_ascii"]}
        return [Holder("ethereum", forward["to"], forward["value"], r["ts"], r["txid"], "Rango", h.segment, hint)]

    def _resolve_1click(self, h: Holder, data: dict[str, Any], e_1c: str) -> list[Holder]:
        sd = data.get("swapDetails") or {}
        qr = ((data.get("quoteResponse") or {}).get("quoteRequest")) or {}
        dest_asset = qr.get("destinationAsset") or ""
        chain_key = dest_asset.split(":", 1)[-1].split("-", 1)[0] if ":" in dest_asset else ""
        dest_chain = NEAR_ASSET_CHAINS.get(chain_key)
        recipient = qr.get("recipient")
        dest_txs = [x.get("hash") for x in sd.get("destinationChainTxHashes") or [] if x.get("hash")]
        origin_txs = [x.get("hash") for x in sd.get("originChainTxHashes") or [] if x.get("hash")]
        self._route_add(h, "bridge deposit address")
        # how the deposit address was emptied on the origin chain (the swap's input leg)
        rows, complete, e_list = self.src.eth_address_transfers(h.address, USDT_ERC20,
                                                                max_pages=int(self.t["blockscout_max_pages"]),
                                                                stop_before_ms=h.ts)
        transfers = [r for r in blockscout_transfer_rows(rows) if same_evm(r["token"], USDT_ERC20)]
        sweeps = [r for r in transfers if same_evm(r["from"], h.address) and r["ts"] >= h.ts]
        for s in sweeps:
            self._edge("ethereum", s["txid"], h.address, s["to"], s["value"], s["ts"], s["block"],
                       "bridge_deposit_sweep", [e_list])
        receiver_ascii = h.hint.get("receiver_ascii")
        item: dict[str, Any] = {
            "protocol": "NEAR Intents 1Click",
            "detected_by": "1Click status API recognises the address as a deposit address",
            "deposit_address": h.address,
            "deposit_chain": h.chain,
            "status": data.get("status"),
            "amount_in": fmt(int(sd.get("amountIn") or 0)) if sd.get("amountIn") else None,
            "amount_out_reported": fmt(int(sd.get("amountOut") or 0)) if sd.get("amountOut") else None,
            "origin_chain_txs": origin_txs,
            "deposit_sweep_txs": [{"txid": s["txid"], "to": s["to"], "amount": fmt(s["value"]),
                                   "timestamp_utc": ts_utc(s["ts"])} for s in sweeps],
            "destination_asset": dest_asset,
            "dst_chain": dest_chain,
            "recipient": recipient,
            "refund_to": qr.get("refundTo"),
            "referral": qr.get("referral"),
            "intent_hashes": sd.get("intentHashes") or [],
            "near_txs": sd.get("nearTxHashes") or [],
            "dst_txs": dest_txs,
            "matches_previous_hop_hint": {
                "destination_chain_ascii": h.hint.get("destination_chain_ascii"),
                "receiver_ascii_prefix": receiver_ascii,
                "recipient_starts_with_prefix": bool(receiver_ascii and recipient
                                                     and recipient.startswith(receiver_ascii)),
            } if h.hint else None,
            "evidence": [e_1c, e_list],
        }
        self.cross_chain.append(item)
        if dest_chain != "tron" or not dest_txs or not recipient:
            self.boundaries.append(f"1Click deposit {h.address}: destination {dest_chain} not supported or no "
                                   f"destination tx")
            return []
        out: list[Holder] = []
        for dtx in dest_txs:
            info, e_info = self.src.tron_info(dtx)
            pays = [t for t in tron_token_transfers(info) if t["to"] == recipient and t["asset"] == "USDT-TRC20"]
            item["evidence"].append(e_info)
            if not pays:
                self.boundaries.append(f"1Click destination tx {dtx}: no USDT-TRC20 transfer to {recipient}")
                continue
            p = pays[0]
            ts = int(info["blockTimeStamp"])
            item.update({"dst_tx_onchain": dtx, "dst_block": info.get("blockNumber"), "dst_timestamp_utc": ts_utc(ts),
                         "dst_payout_from": p["from"], "dst_amount_onchain": fmt(p["value"]),
                         "amount_out_reported_minus_onchain": fmt(int(sd.get("amountOut") or 0) - p["value"])
                         if sd.get("amountOut") else None})
            fee = h.amount - p["value"]
            self.accounting.append({"what": "NEAR Intents 1Click: deposit - on-chain payout", "at": h.address,
                                    "amount": fee})
            self.side_branches.append({"branch": "bridge fee", "protocol": "NEAR Intents 1Click",
                                       "txid": dtx, "amount": fmt(fee), "asset": "USDT",
                                       "counted_in_theft_loss": True, "evidence": [e_1c, e_info]})
            self._edge("tron", dtx, p["from"], recipient, p["value"], ts, info.get("blockNumber"), "bridge_in",
                       [e_1c, e_info], confirmed_by_receipt=True)
            out.append(Holder("tron", recipient, p["value"], ts, dtx, "Rango->NEAR Intents"
                              if h.via == "Rango" else "NEAR Intents 1Click", h.segment + 1))
        return out

    # ---------------------------------------------------------------- side branches / accounting
    def _side(self, h: Holder, r: dict[str, Any], e_list: str) -> None:
        names = {"dust": "dust", "exact_cut": f"exact {Decimal(r.get('cut_share', '0')) * 100:.0f}% cut",
                 "side": "side outflow (fee-like)", "remainder_dust": "remainder dust after the drain"}
        self.side_branches.append({
            "branch": names.get(r["class"], r["class"]), "chain": h.chain, "txid": r["txid"], "from": h.address,
            "to": r["to"], "amount": fmt(r["value"]), "asset": ASSET_BY_CHAIN[h.chain],
            "timestamp_utc": ts_utc(r["ts"]), "share_of_tainted": str((Decimal(r["value"]) / Decimal(h.amount) * 100)
                                                                       .quantize(Decimal("0.0001"))) + "%",
            "counted_in_theft_loss": r["class"] != "remainder_dust", "evidence": [e_list]})
        self._edge(h.chain, r["txid"], h.address, r["to"], r["value"], r["ts"], r.get("block"), r["class"], [e_list])

    def _account(self, h: Holder, taken: list[dict[str, Any]], residual: int) -> None:
        for r in taken:
            if r["class"] in ("dust", "exact_cut", "side"):
                self.accounting.append({"what": f"side outflow ({r['class']})", "at": f"{h.chain}:{h.address}",
                                        "amount": r["value"], "txid": r["txid"]})
        if residual > 0:
            self.accounting.append({"what": "left on holder (not moved in the follow window)",
                                    "at": f"{h.chain}:{h.address}", "amount": residual})
        elif residual < 0:
            self.accounting.append({"what": "holder sent more than the tainted arrival (pre-existing balance mixed in)",
                                    "at": f"{h.chain}:{h.address}", "amount": residual})

    def _value_accounting(self, start: dict[str, Any]) -> dict[str, Any]:
        start_amount = int(Decimal(start["amount"]).scaleb(6))
        final = [hb for hb in self.hubs]
        arrived = sum(int(Decimal(hb["arrived_amount"]).scaleb(6)) for hb in final)
        total = start_amount - arrived if final else None
        comp_sum = sum(c["amount"] for c in self.accounting)
        return {
            "stolen_amount": fmt(start_amount),
            "arrived_at_hub": fmt(arrived) if final else None,
            "total_lost_before_hub": fmt(total) if total is not None else None,
            "components": [{**c, "amount": fmt(c["amount"])} for c in self.accounting],
            "components_sum": fmt(comp_sum),
            "components_reconcile": total is not None and comp_sum == total,
        }

    def _edge(self, chain: str, txid: str, frm: str, to: str, value: int, ts: int | None, block: Any, kind: str,
              evidence: list[str], *, confirmed_by_receipt: bool | None = None) -> None:
        receipt_source = None
        if confirmed_by_receipt is not None:
            receipt_source = ("TronGrid node API receipt (same provider as the v1 index)" if chain == "tron"
                              else "public Ethereum RPC receipt (independent of Blockscout)")
        self.edges.append({"n": len(self.edges) + 1, "chain": chain, "txid": txid, "from": frm, "to": to,
                           "amount": fmt(value), "asset": ASSET_BY_CHAIN.get(chain), "timestamp_utc": ts_utc(ts),
                           "block": block, "kind": kind, "confirmed_by_receipt": confirmed_by_receipt,
                           "receipt_source": receipt_source, "evidence": evidence})

    # ================================================================ 4. hub exits
    def _hub_exits(self, hub: dict[str, Any]) -> None:
        h: Holder = hub["_holder"]
        if h.chain != "tron":
            self.boundaries.append(f"hub {h.address} on {h.chain}: exchange-exit heuristic implemented for TRON only")
            return
        end = h.ts + int(self.t["hub_window_s"]) * 1000
        outs = [r for r in hub["_transfers"] if r["from"] == h.address and h.ts <= r["ts"] <= end]
        checked = outs[: int(self.t["exit_max_checks"])]
        if len(outs) > len(checked):
            self.boundaries.append(f"hub {h.address}: {len(outs) - len(checked)} later outflows in the window not "
                                   f"checked (exit_max_checks)")
        for r in checked:
            res = self._deposit_check(h, r)
            self.hub_outflow_checks.append(res)
            if res["verdict"] == "exchange_exit":
                self.exits.append(res)

    def _deposit_check(self, hub: Holder, r: dict[str, Any]) -> dict[str, Any]:
        addr = r["to"]
        end = r["ts"] + int(self.t["deposit_window_s"]) * 1000
        rows, complete, e_list = self.src.trc20_window(addr, USDT_TRC20, r["ts"], end, limit=50, max_pages=1)
        tr = v1_transfer_rows(rows, USDT_TRC20)
        cps = {(x["to"] if x["from"] == addr else x["from"]) for x in tr}
        max_delay = int(self.t["deposit_forward_max_delay_s"]) * 1000
        fwd = [x for x in tr if x["from"] == addr and r["ts"] <= x["ts"] <= r["ts"] + max_delay]
        fwd_total = sum(x["value"] for x in fwd)
        dests = sorted({x["to"] for x in fwd})
        full = fwd_total >= trunc_share(r["value"], str(self.t["deposit_forward_min_share"]))
        few = len(cps) <= int(self.t["deposit_max_counterparties"])
        pattern = bool(fwd) and full and len(dests) == 1 and few
        res: dict[str, Any] = {
            "hub": hub.address,
            "hub_outflow_txid": r["txid"],
            "hub_outflow_utc": ts_utc(r["ts"]),
            "amount": fmt(r["value"]),
            "recipient": addr,
            "forwarded_total_within_max_delay": fmt(fwd_total),
            "forward_txids": [x["txid"] for x in fwd],
            "forward_destinations": dests,
            "forward_delay_s": (fwd[-1]["ts"] - r["ts"]) // 1000 if fwd else None,
            "distinct_counterparties_in_window": len(cps),
            "rule_full": full,
            "rule_single_destination": len(dests) == 1,
            "rule_few_counterparties": few,
            "deposit_pattern": pattern,
            "evidence": [e_list],
            "commingled": True,
            "taint_note": f"hub outflow {fmt(r['value'])} vs stolen arrival {fmt(hub.amount)}: funds commingled, "
                          f"taint share not determined",
        }
        if not pattern:
            res["verdict"] = "no_deposit_pattern"
            return res
        label = self.hot_wallets.get(dests[0])
        acct, e_acct = self.src.tron_account(addr)
        created = acct.get("create_time")
        res["evidence"].append(e_acct)
        res["recipient_activated_utc"] = ts_utc(created) if created else None
        res["recipient_activated_between_deposit_and_forward"] = bool(
            created and r["ts"] <= created <= (fwd[-1]["ts"] if fwd else r["ts"]))
        if label:
            res.update({"verdict": "exchange_exit", "exchange": label["exchange"], "hot_wallet": dests[0],
                        "label_source": label["source"], "label_status": label.get("status")})
        else:
            res.update({"verdict": "deposit_pattern_unlabelled_destination", "hot_wallet": dests[0],
                        "exchange": None})
        return res

    # ================================================================ 5. common funder
    def _funders(self, address: str) -> tuple[dict[str, list[dict[str, Any]]], str]:
        rows, _, eid = self.src.account_txs(address, only_to=True, limit=int(self.t["funder_inbound_page_limit"]))
        trx_in = [r for r in v1_native_rows(rows) if r["type"] == "TransferContract" and r["to"] == address
                  and r["ret"] == "SUCCESS"]
        out: dict[str, list[dict[str, Any]]] = {}
        for i, r in enumerate(trx_in):
            activation = i == 0
            if activation or (r["amount_sun"] or 0) >= int(self.t["funding_min_trx_sun"]):
                out.setdefault(r["owner"], []).append({"txid": r["txid"], "timestamp_utc": ts_utc(r["ts"]),
                                                       "amount_trx": fmt(r["amount_sun"] or 0),
                                                       "activation": activation})
        return out, eid

    def _common_funder(self, start: dict[str, Any]) -> None:
        victim = start["from"]
        victim_funders, e_v = self._funders(victim)
        thief_side = []
        seen = set()
        for h in self.holders:
            if h.chain == "tron" and h.address != victim and h.address not in seen:
                seen.add(h.address)
                thief_side.append(h)
        per: dict[str, dict[str, Any]] = {}
        evid = {victim: e_v}
        for h in thief_side:
            f, eid = self._funders(h.address)
            evid[h.address] = eid
            for funder, txs in f.items():
                per.setdefault(funder, {})[h.address] = {"segment": h.segment, "txs": txs}
        for funder, funded in sorted(per.items()):
            if funder in victim_funders:
                if len(funded) >= 1:
                    self.links.append({
                        "type": "shared_funder_with_victim",
                        "funder": funder,
                        "funded": [{"address": a, "txids": [t["txid"] for t in v["txs"]]} for a, v in funded.items()],
                        "victim_funding_txids": [t["txid"] for t in victim_funders[funder]],
                        "interpretation": "also funded the victim: treated as a service (activation/top-up), "
                                          "not as an operator link",
                        "evidence": [evid[victim]] + [evid[a] for a in funded],
                    })
                continue
            if len(funded) < 2:
                continue
            rows, complete, e_fan = self.src.account_txs(funder, only_from=True,
                                                         limit=int(self.t["funder_fanout_page_limit"]))
            recipients = {r["to"] for r in v1_native_rows(rows) if r["type"] == "TransferContract"}
            segments = {v["segment"] for v in funded.values()}
            k = len(funded)
            score = 1 + (1 if k >= 3 else 0) + (1 if len(segments) > 1 else 0) \
                - (1 if len(recipients) > int(self.t["funder_fanout_service_threshold"]) else 0)
            score = max(1, min(4, score))
            self.links.append({
                "type": "common_trx_funder",
                "statement": "likely same operator (inference from shared TRX funding, not a fact)",
                "funder": funder,
                "funded": [{"address": a, "segment": v["segment"], "txids": [t["txid"] for t in v["txs"]],
                            "amounts_trx": [t["amount_trx"] for t in v["txs"]],
                            "first_funding_utc": v["txs"][0]["timestamp_utc"]} for a, v in funded.items()],
                "funded_count": k,
                "spans_cross_chain_hop": len(segments) > 1,
                "funder_fanout_distinct_trx_recipients": len(recipients),
                "funder_fanout_rows": len(rows),
                "funder_fanout_page_complete": complete,
                "score": score,
                "score_rule": "1 (>=2 funded) +1 (>=3 funded) +1 (funded on both sides of a cross-chain hop) "
                              "-1 (funder fan-out > threshold, looks like a funding service)",
                "confidence": FUNDER_CONFIDENCE_LEVELS[score],
                "evidence": [evid[a] for a in funded] + [e_fan],
            })

    # ================================================================ 6. freeze
    def _freeze_candidates(self) -> list[dict[str, Any]]:
        out = []
        for hub in self.hubs:
            if hub["chain"] != "tron":
                continue
            bal, eid = self.src.usdt_balance_now(hub["address"], USDT_TRC20)
            self.live[f"usdt_balance_now:{hub['address']}"] = {"amount": fmt(bal) if bal is not None else None,
                                                                "evidence": eid,
                                                                "note": "live value at run time; changes constantly"}
            out.append({
                "address": hub["address"],
                "chain": "tron",
                "asset": "USDT-TRC20",
                "reason": "stolen funds arrived and are commingled in a high-volume USDT-TRC20 address; "
                          "USDT-TRC20 can be frozen by the issuer on a law-enforcement request",
                "stolen_arrival": hub["arrived_amount"],
                "uncertainty": "commingled: the share of the current balance that is stolen is not determined; "
                               "the balance changes constantly",
            })
        return out


def semantic_view(out: dict[str, Any]) -> dict[str, Any]:
    """The deterministic part of a reference-run output (what the replay test compares).

    Excludes body hashes (they change when a live run re-records responses whose envelope carries
    a server timestamp), live observations (balances) and timings.
    """
    import json

    from ..core.results import json_default

    view = {"meta": out["meta"], "result": out["result"], "evidence_ids": sorted(out["evidence"])}
    return json.loads(json.dumps(view, default=json_default, ensure_ascii=False))
