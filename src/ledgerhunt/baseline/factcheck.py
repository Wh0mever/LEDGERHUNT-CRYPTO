"""Step 2: compare every checkable fact of the case-001 fixture with the re-fetched raw data.

Verdicts: ``confirmed`` / ``mismatch`` (claim and observed raw values both shown) /
``not_verifiable`` (why). Values from the fixture are never adjusted. Each fact lists the raw
responses it was checked against (``evidence`` = "<kind>:<id>" keys of the step-1 inventory,
which maps them to body sha256 values) and whether an independent second source agreed.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from ..core.evm import USDT_ERC20
from ..core.tron import USDT_TRC20, format_amount
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
from .refetch import RawBundle
from .sigcheck import check_tron_signatures

CONFIRMED, MISMATCH, NOT_VERIFIABLE = "confirmed", "mismatch", "not_verifiable"
PN_EMPTY = "PublicNode TRON (independent java-tron node): {} - no data for this tx (node is not archival)"


def _usdt(raw: int) -> str:
    return format_amount(raw, 6)


def _norm_amount(text: str) -> Decimal | None:
    try:
        return Decimal(str(text).replace(",", "").strip())
    except Exception:  # noqa: BLE001
        return None


class FactChecker:
    def __init__(self, fx: dict[str, Any], b: RawBundle) -> None:
        self.fx = fx
        self.b = b
        self.facts: list[dict[str, Any]] = []
        self.observations: list[dict[str, Any]] = []

    # ---------------------------------------------------------------- helpers
    def fact(self, group: str, subject: str, field: str, claim: Any, observed: Any, verdict: str, *,
             evidence: list[str] | None = None, note: str | None = None, second_source: str | None = None) -> None:
        self.facts.append({
            "n": len(self.facts) + 1, "group": group, "subject": subject, "field": field,
            "claim": claim, "observed": observed, "verdict": verdict,
            "second_source": second_source, "note": note, "evidence": evidence or [],
        })

    def eq(self, group: str, subject: str, field: str, claim: Any, observed: Any, **kw: Any) -> bool:
        ok = observed is not None and claim == observed
        verdict = CONFIRMED if ok else (MISMATCH if observed is not None else NOT_VERIFIABLE)
        if observed is None and "note" not in kw:
            kw["note"] = "no raw value available"
        self.fact(group, subject, field, claim, observed, verdict, **kw)
        return ok

    def _tx(self, txid: str) -> dict[str, Any]:
        return self.b.tron_tx.get(txid) or {}

    def _pn_note(self, txid: str) -> str:
        pn = self._tx(txid).get("pn_info")
        if pn == {}:
            return PN_EMPTY
        if pn:
            return "PublicNode TRON returned data"
        return "PublicNode TRON: request failed"

    # ---------------------------------------------------------------- run
    def run(self) -> list[dict[str, Any]]:
        steps = {t["step"]: t for t in self.fx["transactions"]}
        for t in self.fx["transactions"]:
            if t["chain"] == "tron":
                self._tron_step(t, steps)
            else:
                self._eth_step(t)
        self._theft_block()
        self._mechanism()
        self._addresses()
        self._links()
        self._ground_truth_arithmetic(steps)
        return self.facts

    # ---------------------------------------------------------------- TRON transactions
    def _tron_step(self, t: dict[str, Any], steps: dict[int, dict[str, Any]]) -> None:
        txid = t["txid"]
        subj = f"step {t['step']} {txid[:10]}"
        rec = self._tx(txid)
        tx, info, events = rec.get("tx") or {}, rec.get("info") or {}, rec.get("events") or {}
        ev = [f"tron_tx:{txid}", f"tron_info:{txid}", f"tron_events:{txid}", f"tron_info_publicnode:{txid}"]
        second = self._pn_note(txid)
        if not tx or not info:
            for f in ("from", "to", "amount", "timestamp_utc", "status"):
                self.fact("transactions", subj, f, t.get(f), None, NOT_VERIFIABLE, evidence=ev,
                          note="TronGrid returned no data for this txid", second_source=second)
            return
        c = tron_contract(tx)
        ts = ts_utc(info.get("blockTimeStamp"))
        block = info.get("blockNumber")
        ok_status = c.get("ret") == "SUCCESS" and (info.get("receipt") or {}).get("result", "SUCCESS") == "SUCCESS"
        if t.get("asset") == "USDT-TRC20" and t.get("kind") != "approve":
            transfers = [x for x in tron_token_transfers(info) if x["token"] == USDT_TRC20]
            match = next((x for x in transfers if x["from"] == t["from"] and x["to"] == t["to"]), None)
            obs = match or (transfers[0] if transfers else None)
            v1 = [e for e in (events.get("data") or []) if e.get("event_name") == "Transfer"
                  and e.get("contract_address") == USDT_TRC20]
            v1_ok = any(str((e.get("result") or {}).get("value")) == str(obs["value"]) for e in v1) if obs else False
            src_note = "TronGrid node receipt log; TronGrid v1 events " + ("agree" if v1_ok else "DISAGREE/absent")
            self.eq("transactions", subj, "from", t["from"], obs["from"] if obs else None, evidence=ev,
                    second_source=second, note=src_note)
            self.eq("transactions", subj, "to", t["to"], obs["to"] if obs else None, evidence=ev, second_source=second)
            self.eq("transactions", subj, "amount", t["amount"], _usdt(obs["value"]) if obs else None, evidence=ev,
                    second_source=second)
            self.eq("transactions", subj, "asset", "USDT-TRC20", "USDT-TRC20" if obs else None, evidence=ev,
                    note=f"token contract {USDT_TRC20}")
        elif t.get("kind") == "approve":
            call = c.get("call") or {}
            approvals = [lg["decoded"] for lg in tron_logs(info) if lg["decoded"] and lg["decoded"]["event"] == "Approval"]
            a = approvals[0] if approvals else None
            self.eq("transactions", subj, "from (owner)", t["from"], a["owner"] if a else c.get("owner"), evidence=ev)
            self.eq("transactions", subj, "to (spender)", t["to"], a["spender"] if a else call.get("to"), evidence=ev)
            self.eq("transactions", subj, "amount (allowance)", t["amount"],
                    _usdt(a["value"]) if a else (_usdt(call["value"]) if "value" in call else None), evidence=ev)
            self.eq("transactions", subj, "kind", "approve", call.get("method"), evidence=ev,
                    note="calldata selector 095ea7b3 = approve(address,uint256); Approval event "
                         + ("present" if a else "absent"))
        elif t.get("asset") == "ENERGY":
            self.eq("transactions", subj, "kind", "energy_delegation (DelegateResourceContract)",
                    f"energy_delegation ({c.get('type')})" if c.get("type") == "DelegateResourceContract" else c.get("type"),
                    evidence=ev)
            self.eq("transactions", subj, "from", t["from"], c.get("owner"), evidence=ev)
            self.eq("transactions", subj, "to", t["to"], c.get("to"), evidence=ev)
            claimed_trx = t["amount"].split(" ")[0]
            obs_trx = fmt(c.get("balance_sun") or 0) if c.get("balance_sun") is not None else None
            self.eq("transactions", subj, "amount (TRX staked behind the delegated energy)",
                    _norm_amount(claimed_trx), _norm_amount(obs_trx) if obs_trx else None, evidence=ev,
                    note=f"resource={c.get('resource')}")
        elif t.get("asset") == "TRX":
            self.eq("transactions", subj, "kind", "TRX transfer (TransferContract)",
                    "TRX transfer (TransferContract)" if c.get("type") == "TransferContract" else c.get("type"),
                    evidence=ev)
            self.eq("transactions", subj, "from", t["from"], c.get("owner"), evidence=ev)
            self.eq("transactions", subj, "to", t["to"], c.get("to"), evidence=ev)
            self.eq("transactions", subj, "amount (TRX)", _norm_amount(t["amount"].split(" ")[0]),
                    _norm_amount(fmt(c["amount_sun"])) if c.get("amount_sun") is not None else None, evidence=ev)
        self.eq("transactions", subj, "timestamp_utc", t["timestamp_utc"], ts, evidence=ev,
                note="block timestamp from gettransactioninfobyid")
        if t.get("block") is not None:
            self.eq("transactions", subj, "block", t["block"], block, evidence=ev)
        self.fact("transactions", subj, "status", t.get("status"), f"contractRet={c.get('ret')}",
                  CONFIRMED if ok_status else MISMATCH, evidence=ev,
                  note="'fact' = the transaction exists and succeeded on chain" if ok_status else None)
        self._tron_kind(t, c, info, subj, ev, steps)

    def _tron_kind(self, t: dict[str, Any], c: dict[str, Any], info: dict[str, Any], subj: str, ev: list[str],
                   steps: dict[int, dict[str, Any]]) -> None:
        kind = t.get("kind")
        logs = tron_logs(info)
        names = sorted({lg["decoded"]["event"] for lg in logs if lg["decoded"]})
        if kind in ("THEFT", "theft_fee_energy_rental"):
            tx = self._tx(t["txid"]).get("tx") or {}
            sig = check_tron_signatures(tx)
            self.eq("transactions", subj, "signed by (recovered from signature)", [t["from"]], sig["signers"],
                    evidence=ev, note=f"signatures={sig['signature_count']}, Permission_id="
                                      f"{c.get('permission_id') if c.get('permission_id') is not None else 'absent (0 = owner)'}"
                                      f", txID==sha256(raw_data): {sig['txid_matches_raw_data']}")
        elif kind == "bridge_out_USDT0_LayerZero":
            self.eq("transactions", subj, "kind (bridge event present)", "OFTSent", "OFTSent" if "OFTSent" in names else
                    ",".join(names) or None, evidence=ev, note="raw TRON log topic0 = keccak(OFTSent(bytes32,uint32,"
                                                               "address,uint256,uint256))")
            self._layerzero(t, logs, subj)
        elif kind == "fee_1pct":
            parent = steps.get(8)
            if parent:
                p = int(Decimal(parent["amount"]).scaleb(6))
                self.eq("transactions", subj, "exactly 1% of 13035.640112 (truncated to 6 decimals)", t["amount"],
                        _usdt(p // 100), evidence=ev, note=f"1% of {parent['amount']} = {Decimal(p) / 100 / 10**6}")
        elif kind == "hop_99pct":
            parent = steps.get(8)
            cut = steps.get(10)
            if parent and cut:
                p = int(Decimal(parent["amount"]).scaleb(6))
                c1 = int(Decimal(cut["amount"]).scaleb(6))
                self.eq("transactions", subj, "hop = parent - 1% cut", t["amount"], _usdt(p - c1), evidence=ev,
                        note=f"share of parent = {(Decimal(int(Decimal(t['amount']).scaleb(6))) / p * 100):.8f}%")
        elif kind == "bridge_in_NEAR_Intents":
            st = (self.b.oneclick.get(steps[16]["from"]) or {}).get("data") or {}
            dst = [x.get("hash") for x in ((st.get("swapDetails") or {}).get("destinationChainTxHashes") or [])]
            self.eq("transactions", subj, "listed by NEAR Intents 1Click as destination tx", True,
                    t["txid"] in dst if st else None, evidence=ev + [f"oneclick_status:{steps[16]['from']}"],
                    second_source="NEAR Intents 1Click status API (independent of TronGrid)")
            ao = (st.get("swapDetails") or {}).get("amountOut")
            if ao:
                self.fact("transactions", subj, "note: 1Click amountOut vs on-chain transfer",
                          "1Click amountOut 12878.410167; on-chain 12878.454902",
                          f"1Click amountOut {_usdt(int(ao))}; on-chain {t['amount']}",
                          CONFIRMED if _usdt(int(ao)) == "12878.410167" else MISMATCH,
                          evidence=[f"oneclick_status:{steps[16]['from']}"],
                          note=f"difference on-chain - amountOut = {_usdt(int(Decimal(t['amount']).scaleb(6)) - int(ao))}")
        elif kind == "exchange_sweep":
            hot = t["to"]
            ts_lookup = (self.b.tronscan.get(hot) or {})
            self._tronscan_fact(hot, ts_lookup, subj)

    def _layerzero(self, t: dict[str, Any], logs: list[dict[str, Any]], subj: str) -> None:
        lz = t["layerzero"]
        oft = next((lg for lg in logs if lg["decoded"] and lg["decoded"]["event"] == "OFTSent"), None)
        msgs = ((self.b.lz.get(f"tx:{t['txid']}") or {}).get("data")) or []
        msg = msgs[0] if msgs else {}
        by_guid = ((self.b.lz.get(f"guid:{lz['guid']}") or {}).get("data")) or []
        ev = [f"tron_info:{t['txid']}", f"lz_by_tx:{t['txid']}", f"lz_by_guid:{lz['guid']}"]
        d = oft["decoded"] if oft else {}
        lzs = "LayerZero Scan (independent indexer)"
        self.eq("layerzero", subj, "guid", lz["guid"], d.get("guid"), evidence=ev,
                second_source=f"{lzs}: {'agrees' if msg.get('guid') == lz['guid'] else 'differs/absent'}")
        self.eq("layerzero", subj, "srcEid", lz["srcEid"], (msg.get("pathway") or {}).get("srcEid"), evidence=ev,
                note="from LayerZero Scan pathway")
        self.eq("layerzero", subj, "dstEid", lz["dstEid"], d.get("dstEid"), evidence=ev,
                second_source=f"{lzs}: dstEid {(msg.get('pathway') or {}).get('dstEid')}")
        self.eq("layerzero", subj, "dst_chain", lz["dst_chain"], ((msg.get("pathway") or {}).get("receiver") or {})
                .get("chain"), evidence=ev)
        tx = self._tx(t["txid"]).get("tx") or {}
        call = tron_contract(tx).get("call") or {}
        to_word = call.get("to_bytes32") or ""
        bridge_in = next((x for x in self.fx["transactions"] if x.get("kind") == "bridge_in_USDT0"), None)
        eth = self.b.eth_tx.get(bridge_in["txid"]) if bridge_in else None
        recv = None
        if eth:
            recv = next((lg["decoded"] for lg in evm_logs_from_blockscout(eth.get("logs") or [])
                         if lg["decoded"] and lg["decoded"]["event"] == "OFTReceived"), None)
        self.eq("layerzero", subj, "sendTo", lz["sendTo"].lower(), ("0x" + to_word[-40:]).lower() if to_word else None,
                evidence=ev + [f"tron_tx:{t['txid']}"], note="decoded from OFT send() calldata (SendParam.to)",
                second_source="Ethereum OFTReceived.toAddress: " + (recv["toAddress"] if recv else "n/a"))
        self.eq("layerzero", subj, "amountReceivedLD", lz["amountReceivedLD"],
                _usdt(d["amountReceivedLD"]) if d else None, evidence=ev,
                second_source="Ethereum OFTReceived.amountReceivedLD: "
                              + (_usdt(recv["amountReceivedLD"]) if recv else "n/a"))
        self.eq("layerzero", subj, "status", lz["status"], (msg.get("status") or {}).get("name"), evidence=ev,
                note=f"by guid: {(by_guid[0].get('status') or {}).get('name') if by_guid else 'n/a'}")
        dst_tx = ((msg.get("destination") or {}).get("tx") or {}).get("txHash")
        self.eq("layerzero", subj, "destination tx (fixture step 14)", bridge_in["txid"] if bridge_in else None,
                dst_tx, evidence=ev)

    # ---------------------------------------------------------------- Ethereum transactions
    def _eth_step(self, t: dict[str, Any]) -> None:
        h = t["txid"]
        subj = f"step {t['step']} {h[:12]}"
        rec = self.b.eth_tx.get(h) or {}
        btx = rec.get("tx") or {}
        ev = [f"eth_tx:{h}", f"eth_token_transfers:{h}", f"eth_logs:{h}", f"eth_receipt:{h}"]
        rows = rec.get("token_transfers") or []
        tr = [{"from": r["from"]["hash"], "to": r["to"]["hash"], "value": int(r["total"]["value"]),
               "token": (r.get("token") or {}).get("address_hash")} for r in rows if (r.get("total") or {}).get("value")]
        match = next((x for x in tr if same_evm(x["from"], t["from"]) and same_evm(x["to"], t["to"])), None)
        rcpt = rec.get("receipt") or {}
        rlogs = evm_logs_from_receipt(rcpt) if rcpt else []
        r_tr = evm_token_transfers(rlogs)
        r_match = next((x for x in r_tr if same_evm(x["from"], t["from"]) and same_evm(x["to"], t["to"])), None)
        second = ("public Ethereum RPC receipt: " + ("agrees" if r_match and match and r_match["value"] == match["value"]
                                                    else "differs") if rcpt else
                  "public Ethereum RPC receipt: null/no data")
        self.eq("transactions", subj, "from", t["from"].lower(), match["from"].lower() if match else None, evidence=ev,
                second_source=second)
        self.eq("transactions", subj, "to", t["to"].lower(), match["to"].lower() if match else None, evidence=ev)
        self.eq("transactions", subj, "amount", t["amount"], _usdt(match["value"]) if match else None, evidence=ev,
                second_source=second)
        self.eq("transactions", subj, "asset", "USDT-ERC20",
                "USDT-ERC20" if match and same_evm(match["token"], USDT_ERC20) else None, evidence=ev)
        ts = ts_utc(parse_ts(btx["timestamp"])) if btx.get("timestamp") else None
        self.eq("transactions", subj, "timestamp_utc", t["timestamp_utc"], ts, evidence=ev)
        if t.get("block") is not None:
            self.eq("transactions", subj, "block", t["block"], btx.get("block_number"), evidence=ev,
                    second_source=f"receipt blockNumber {int(rcpt['blockNumber'], 16) if rcpt.get('blockNumber') else 'n/a'}")
        self.fact("transactions", subj, "status", t.get("status"), f"blockscout status={btx.get('status')}",
                  CONFIRMED if btx.get("status") == "ok" else NOT_VERIFIABLE if not btx else MISMATCH, evidence=ev)
        if t.get("rango"):
            self._rango(t, rec, subj, ev)
        if t.get("near_intents"):
            self._near(t, subj)

    def _rango(self, t: dict[str, Any], rec: dict[str, Any], subj: str, ev: list[str]) -> None:
        rg = t["rango"]
        logs = evm_logs_from_blockscout(rec.get("logs") or [])
        ri = next((lg for lg in logs if lg["decoded"] and lg["decoded"]["event"] == "RangoBridgeInitiated"), None)
        fi = next((lg["decoded"] for lg in logs if lg["decoded"] and lg["decoded"]["event"] == "FeeInfo"), None)
        d = ri["decoded"] if ri else {}
        diamond = ri["emitter"] if ri else None
        trs = evm_token_transfers(logs)
        fwd = next((x for x in trs if same_evm(x["from"], diamond) and d and x["value"] == d["bridgeAmount"]), None)
        aff = next((x for x in trs if same_evm(x["from"], diamond) and fi and same_evm(x["to"], fi["affiliatorAddress"])),
                   None)
        g = "rango"
        self.eq(g, subj, "dAppName", rg["dAppName"], d.get("dAppName"), evidence=ev)
        self.eq(g, subj, "dAppTag", rg["dAppTag"], d.get("dAppTag"), evidence=ev)
        self.eq(g, subj, "bridgeId", rg["bridgeId"], d.get("bridgeId"), evidence=ev)
        self.eq(g, subj, "destinationChainId", rg["destinationChainId"], d.get("destinationChainId"), evidence=ev)
        self.eq(g, subj, "destinationChainId_ascii", rg["destinationChainId_ascii"],
                ascii_of_uint(d["destinationChainId"]) if d else None, evidence=ev)
        self.eq(g, subj, "receiver_bytes_ascii", rg["receiver_bytes_ascii"],
                ascii_of_address_bytes(d["_raw_address_hex"]["receiver"]) if d else None, evidence=ev,
                note="20 'address' bytes of RangoBridgeInitiated.receiver read as ASCII: only the first 20 characters "
                     "of the TRON address fit")
        self.eq(g, subj, "affiliate", rg["affiliate"].lower(), fi["affiliatorAddress"].lower() if fi else None,
                evidence=ev)
        self.eq(g, subj, "affiliateFee", rg["affiliateFee"], _usdt(fi["affiliateFee"]) if fi else None, evidence=ev,
                second_source="USDT Transfer Diamond->affiliate: " + (_usdt(aff["value"]) if aff else "n/a"))
        self.eq(g, subj, "forwarded_to", rg["forwarded_to"].lower(), fwd["to"].lower() if fwd else None, evidence=ev)
        self.eq(g, subj, "forwarded_amount", rg["forwarded_amount"], _usdt(fwd["value"]) if fwd else None,
                evidence=ev)
        rcpt = rec.get("receipt") or {}
        r2 = next((lg["decoded"] for lg in evm_logs_from_receipt(rcpt) if lg["decoded"]
                   and lg["decoded"]["event"] == "RangoBridgeInitiated"), None) if rcpt else None
        self.eq(g, subj, "second source: RangoBridgeInitiated in public RPC receipt (bridgeAmount)",
                rg["forwarded_amount"], _usdt(r2["bridgeAmount"]) if r2 else None, evidence=ev,
                note=None if rcpt else "public RPC returned result=null for this receipt (also after one retry)")

    def _near(self, t: dict[str, Any], subj: str) -> None:
        ni = t["near_intents"]
        rec = self.b.oneclick.get(t["from"]) or {}
        st = rec.get("data") or {}
        sd = st.get("swapDetails") or {}
        qr = (st.get("quoteResponse") or {}).get("quoteRequest") or {}
        ev = [f"oneclick_status:{t['from']}"]
        g = "near_intents"
        self.eq(g, subj, "status", ni["status"], st.get("status"), evidence=ev)
        self.eq(g, subj, "recipient_tron", ni["recipient_tron"], qr.get("recipient"), evidence=ev)
        self.eq(g, subj, "refundTo", ni["refundTo"].lower(), (qr.get("refundTo") or "").lower() or None, evidence=ev)
        self.eq(g, subj, "intentHash", [ni["intentHash"]], sd.get("intentHashes"), evidence=ev)
        self.eq(g, subj, "near_tx", ni["near_tx"], sd.get("nearTxHashes"), evidence=ev)
        self.eq(g, subj, "destination_tx", [ni["destination_tx"]],
                [x.get("hash") for x in sd.get("destinationChainTxHashes") or []] or None, evidence=ev)
        self.eq(g, subj, "deposit address (quote.depositAddress)", t["from"].lower(),
                ((st.get("quoteResponse") or {}).get("quote") or {}).get("depositAddress", "").lower() or None,
                evidence=ev)
        origin = [x.get("hash") for x in sd.get("originChainTxHashes") or []]
        if st and t["txid"] not in origin:
            self.observations.append({
                "subject": subj, "what": "1Click originChainTxHashes",
                "observed": origin, "fixture_step_txid": t["txid"],
                "note": "1Click lists the tx that paid INTO the deposit address (the Rango tx) as the origin tx; "
                        "fixture step 16 is the sweep OUT of the deposit address to 0x2CfF. Both transactions are "
                        "real and the fixture does not claim otherwise: an observation, not a mismatch.",
                "evidence": ev + [f"eth_tx:{t['txid']}"]})

    # ---------------------------------------------------------------- theft block / mechanism
    def _theft_block(self) -> None:
        th = self.fx["theft"]
        info = self._tx(th["txid"]).get("info") or {}
        ev = [f"tron_info:{th['txid']}"]
        rec = info.get("receipt") or {}
        self.eq("theft", "theft", "block", th["block"], info.get("blockNumber"), evidence=ev)
        self.eq("theft", "theft", "energy used (note: 130,285 energy)", 130285, rec.get("energy_usage_total"),
                evidence=ev)
        self.eq("theft", "theft", "TRX burned (note: 0.345 TRX)", "0.345000", fmt(int(info.get("fee") or 0)),
                evidence=ev, note=f"fee={info.get('fee')} sun, net_fee={rec.get('net_fee')}, "
                                  f"energy_fee={rec.get('energy_fee', 0)}: the 0.345 TRX is the bandwidth fee; "
                                  f"energy came from the delegation (step 3)")
        trc = (self.b.trc20.get("victim:all") or {}).get("rows") or []
        transfers = v1_transfer_rows(trc, USDT_TRC20)
        theft_ms = parse_ts(th["timestamp_utc"])
        inc = [r for r in transfers if r["to"] == self.fx["victim"]["address"] and r["ts"] <= theft_ms]
        last = inc[-1] if inc else None
        self.eq("theft", "theft", "seconds_after_incoming_payment", th["seconds_after_incoming_payment"],
                (theft_ms - last["ts"]) // 1000 if last else None, evidence=["trc20:victim:all"],
                note=f"incoming {last['txid'][:10]} {_usdt(last['value'])} USDT" if last else None)
        # balance of the victim just before the incoming payment (step 2 note: '109.79 USDT')
        victim = self.fx["victim"]["address"]
        complete = (self.b.trc20.get("victim:all") or {}).get("complete")
        pay = next((r for r in transfers if r["txid"] == next(t["txid"] for t in self.fx["transactions"]
                                                               if t["step"] == 1)), None)
        if pay and complete:
            bal = sum(r["value"] if r["to"] == victim else -r["value"] for r in transfers
                      if (r["ts"], r["txid"]) < (pay["ts"], pay["txid"]) and r["ts"] < pay["ts"])
            self.fact("theft", "victim", "USDT balance before the large payment (step 2 note: 109.79)", "109.79",
                      _usdt(bal), CONFIRMED if Decimal(_usdt(bal)).quantize(Decimal("0.01")) == Decimal("109.79")
                      else MISMATCH, evidence=["trc20:victim:all"],
                      note="sum of all USDT transfers of the victim before 2026-09-21 11:31:54 (complete history)")

    def _mechanism(self) -> None:
        th = self.fx["theft"]
        victim = self.fx["victim"]["address"]
        tx = self._tx(th["txid"]).get("tx") or {}
        c = tron_contract(tx)
        sig = check_tron_signatures(tx)
        ev = [f"tron_tx:{th['txid']}", f"tron_account:{victim}", "account_txs:victim:outgoing-history"]
        g = "mechanism"
        self.eq(g, "theft", "single signature", 1, sig["signature_count"], evidence=ev)
        pid = c.get("permission_id")
        self.fact(g, "theft", "no Permission_id (owner permission)", "absent",
                  "absent" if pid is None else f"Permission_id={pid}",
                  CONFIRMED if pid is None else MISMATCH, evidence=ev,
                  note="raw_data.contract[0] has no Permission_id -> permission 0 (owner)" if pid is None else None)
        self.eq(g, "theft", "signer = victim owner key (recovered from signature)", [victim], sig["signers"],
                evidence=ev, note=f"txID==sha256(raw_data): {sig['txid_matches_raw_data']}")
        acct = (self.b.tron_account.get(victim) or {})
        for src_name, data in (("TronGrid", acct.get("tg")), ("PublicNode", acct.get("pn"))):
            if not data:
                self.fact(g, "victim", f"permissions ({src_name})", "owner/active = itself, threshold 1", None,
                          NOT_VERIFIABLE, evidence=ev, note="no account data")
                continue
            own = data.get("owner_permission") or {}
            act = data.get("active_permission") or []
            obs = {"owner_threshold": own.get("threshold"),
                   "owner_keys": [k.get("address") for k in own.get("keys") or []],
                   "active": [(p.get("threshold"), [k.get("address") for k in p.get("keys") or []]) for p in act]}
            ok = obs["owner_threshold"] == 1 and obs["owner_keys"] == [victim] and all(
                th_ == 1 and ks == [victim] for th_, ks in obs["active"])
            self.fact(g, "victim", f"owner/active key = itself, threshold 1 ({src_name}, current state)",
                      "owner/active = itself, threshold 1", obs, CONFIRMED if ok else MISMATCH, evidence=ev,
                      second_source="PublicNode getaccount (independent node)" if src_name == "PublicNode" else None)
        hist = self.b.account_txs.get("victim:outgoing-history") or {}
        rows = v1_native_rows(hist.get("rows") or [])
        upd = [r["txid"] for r in rows if r["type"] == "AccountPermissionUpdateContract"]
        self.fact(g, "victim", "permissions never changed (no AccountPermissionUpdateContract)", "never changed",
                  f"{len(upd)} permission updates in {len(rows)} outgoing txs (history complete: {hist.get('complete')})",
                  CONFIRMED if not upd and hist.get("complete") else (MISMATCH if upd else NOT_VERIFIABLE), evidence=ev)

    # ---------------------------------------------------------------- addresses
    def _bal_fact(self, addr: str, claim: str, subj: str) -> None:
        bal = self.b.usdt_balance.get(addr) or {}
        tg, pn = bal.get("tg"), bal.get("pn")
        obs = f"TronGrid {_usdt(tg) if tg is not None else 'n/a'}; PublicNode {_usdt(pn) if pn is not None else 'n/a'}"
        claim_d = _norm_amount(claim.replace("~", "").split(" ")[0])
        approx = claim.startswith("~")
        verdict = NOT_VERIFIABLE
        note = "live value read at the time of the re-fetch"
        if tg is not None and claim_d is not None:
            diff = abs(Decimal(_usdt(tg)) - claim_d)
            if diff == 0 or (approx and diff < Decimal("0.01")):
                verdict = CONFIRMED
            else:
                note = ("live value differs from the fixture; the fixture gives no time for this balance, so a "
                        "later change cannot be told apart from an error")
        self.fact("addresses", subj, "USDT balance now", claim, obs, verdict,
                  evidence=[f"usdt_balance_tg:{addr}", f"usdt_balance_pn:{addr}"], note=note,
                  second_source="PublicNode balanceOf " + ("agrees" if tg == pn and tg is not None else "differs/n/a"))

    def _addresses(self) -> None:
        steps = {t["step"]: t for t in self.fx["transactions"]}
        for a in self.fx["addresses"]:
            addr = a["address"]
            subj = f"{addr[:10]} ({a['role'][:40]})"
            conf = a.get("confidence", "")
            acct = (self.b.tron_account.get(addr) or {}).get("tg") if a["chain"] == "tron" else None
            if "balance_usdt" in a and a["chain"] == "tron":
                claim = a["balance_usdt"]
                win = next((v for v in self.b.trc20.values() if v["address"] == addr and v.get("min_ms")
                            and v.get("max_ms") is None), None) if "window" in claim else None
                if win and win.get("complete"):
                    tr = v1_transfer_rows(win["rows"], USDT_TRC20)
                    net = sum(r["value"] if r["to"] == addr else -r["value"] for r in tr)
                    claim_d = _norm_amount(claim.replace("~", "").split(" ")[0])
                    ok = claim_d is not None and abs(Decimal(_usdt(net)) - claim_d) < Decimal("0.01")
                    self.fact("addresses", subj, "USDT net inflow since the window start", claim,
                              f"net of {len(tr)} USDT transfers since {ts_utc(win['min_ms'])} = {_usdt(net)}",
                              CONFIRMED if ok else MISMATCH, evidence=[f"trc20:{k}" for k, v in self.b.trc20.items()
                                                                       if v is win])
                elif "window" in claim or " at " in claim:
                    bal = self.b.usdt_balance.get(addr) or {}
                    self.fact("addresses", subj, "USDT balance", claim,
                              f"now: TronGrid {_usdt(bal['tg']) if bal.get('tg') is not None else 'n/a'}",
                              NOT_VERIFIABLE, evidence=[f"usdt_balance_tg:{addr}"],
                              note="the claim is tied to a past moment/window; only the current value can be read")
                else:
                    self._bal_fact(addr, claim, subj)
            if a.get("balance_trx") and acct:
                same_bal = Decimal(fmt(int(acct.get("balance") or 0))) == Decimal(a["balance_trx"])
                self.fact("addresses", subj, "TRX balance", a["balance_trx"], fmt(int(acct.get("balance") or 0)),
                          CONFIRMED if same_bal else NOT_VERIFIABLE, evidence=[f"tron_account:{addr}"],
                          note="live value; the fixture gives no time for it"
                          + ("" if same_bal else " and the current value differs"))
            role = a["role"]
            if role.startswith("victim"):
                self._bal_fact(addr, "0.023623", subj)
            if "fresh, activated" in role:
                rows = v1_native_rows((self.b.account_txs.get("thief1:earliest-inbound") or {}).get("rows") or [])
                act = next((r for r in rows if r["type"] == "TransferContract" and r["to"] == addr), None)
                created = ts_utc(acct.get("create_time")) if acct else None
                self.eq("addresses", subj, "activated 11:35:27 (activation transfer)", "2026-09-21 11:35:27",
                        ts_utc(act["ts"]) if act else None,
                        evidence=["account_txs:thief1:earliest-inbound", f"tron_account:{addr}"],
                        note=(f"activation tx {act['txid'][:12]} from {act['owner']} ({fmt(act['amount_sun'])} TRX); "
                              f"getaccount create_time = {created}: java-tron stamps create_time with the previous "
                              f"block time (3 s earlier)") if act else None)
                prior = [r for r in rows if r["ts"] < parse_ts("2026-09-21 11:32:39")]
                self.fact("addresses", subj, "fresh (no activity before the theft)", "fresh",
                          f"{len(prior)} inbound native txs before the theft; create_time {created}",
                          CONFIRMED if not prior and created and created > "2026-09-21 11:32:39" else MISMATCH,
                          evidence=["account_txs:thief1:earliest-inbound", f"tron_account:{addr}"])
            if "USDT0 OFT contract" in role:
                c = self.b.tron_contract.get(addr) or {}
                self.eq("addresses", subj, "contract name", "UsdtOFT", c.get("name"), evidence=[f"tron_contract:{addr}"])
            if a["chain"] == "ethereum":
                info = self.b.eth_address.get(addr) or {}
                if "explorer tag" in conf:
                    self._etherscan_fact(addr, subj, role)
                    name = info.get("name")
                    tags = [x.get("display_name") or x.get("label") for x in info.get("public_tags") or []]
                    expected = {"USDT0 OFT adapter (Ethereum)": "UsdtOFT", "Rango Diamond (aggregator)": "RangoDiamond",
                                "NEAR Intents vault": None}.get(role)
                    if expected:
                        self.eq("addresses", subj, "Blockscout contract name", expected, name,
                                evidence=[f"eth_address:{addr}"], note=f"public tags: {tags or 'none'}")
                    else:
                        self.fact("addresses", subj, "explorer tag", role, {"name": name, "public_tags": tags},
                                  NOT_VERIFIABLE if not name and not tags else CONFIRMED, evidence=[f"eth_address:{addr}"],
                                  note="Blockscout shows no name or public tag for this address; the tag probably comes "
                                       "from another explorer (Etherscan), which needs an API key")
                if "transit EOA" in role:
                    tr = self.b.eth_address_transfers.get(addr) or {}
                    rows = blockscout_transfer_rows(tr.get("rows") or [])
                    usdt = [r for r in rows if same_evm(r["token"], USDT_ERC20)]
                    if usdt:
                        first, last = ts_utc(usdt[0]["ts"]), ts_utc(usdt[-1]["ts"])
                        early = [r for r in usdt if ts_utc(r["ts"]) < "2026-08-01"]
                        net = sum(r["value"] if same_evm(r["to"], addr) else -r["value"] for r in usdt)
                        self.fact("addresses", subj, "EOA reused Aug-Oct 2026", "reused Aug-Oct 2026",
                                  f"is_contract={info.get('is_contract')}; USDT transfers {len(usdt)} from {first} to {last}; "
                                  f"{len(early)} of them before August 2026 (first: {usdt[0]['from']} -> {usdt[0]['to']} "
                                  f"{_usdt(usdt[0]['value'])}, tx {usdt[0]['txid']})",
                                  CONFIRMED if not info.get("is_contract") and first.startswith("2026-08")
                                  and last.startswith("2026-10") else MISMATCH, evidence=[f"eth_address_transfers:{addr}"])
                        self.fact("addresses", subj, "USDT balance ~0", "~0",
                                  f"net of all USDT transfers = {_usdt(net)} (listing complete: {tr.get('complete')})",
                                  CONFIRMED if tr.get("complete") and abs(net) < 10**6 else NOT_VERIFIABLE,
                                  evidence=[f"eth_address_transfers:{addr}"])
                if "affiliate" in role:
                    self._affiliate_fact(addr, subj, steps)
                if "one-time deposit address" in role:
                    st = self.b.oneclick.get(addr) or {}
                    self.eq("addresses", subj, "1Click status API knows it as a deposit address", "SUCCESS",
                            (st.get("data") or {}).get("status"), evidence=[f"oneclick_status:{addr}"])
            if "payout wallet" in role:
                d = self.b.tron_tx.get(steps[17]["txid"]) or {}
                pays = [x for x in tron_token_transfers(d.get("info") or {}) if x["to"] == steps[17]["to"]]
                self.eq("addresses", subj, "sender of the 1Click destination tx", addr, pays[0]["from"] if pays else None,
                        evidence=[f"tron_info:{steps[17]['txid']}", f"oneclick_status:{steps[16]['from']}"],
                        note="that it is 'the NEAR Intents payout wallet' is an inference from this single swap")
            if "WhiteBIT deposit address" in role:
                self._deposit_fact(addr, subj)
            if "TronScan tag" in role:
                self._tronscan_fact(addr, self.b.tronscan.get(addr) or {}, subj)
            if not conf.startswith("fact"):
                self.fact("addresses", subj, "role (interpretation)", f"{role} [{conf}]", None, NOT_VERIFIABLE,
                          note="a role/intent label, not an on-chain fact; on-chain facts behind it are checked "
                               "in the other rows")

    def _etherscan_fact(self, addr: str, subj: str, role: str) -> None:
        rec = self.b.etherscan_tags.get(addr) or {}
        data = rec.get("data")
        ev = [f"etherscan_nametag:{addr}"]
        if rec.get("status") is None:
            self.fact("addresses", subj, "Etherscan name tag", role, None, NOT_VERIFIABLE, evidence=ev,
                      note=rec.get("note") or "lookup not performed")
            return
        res = data.get("result") if isinstance(data, dict) else None
        if isinstance(data, dict) and str(data.get("status")) == "1" and isinstance(res, list) and res:
            tag = {k: res[0].get(k) for k in ("nametag", "labels") if res[0].get(k)}
            words = [w.lower() for w in role.replace("(", " ").replace(")", " ").split() if len(w) > 3]
            hit = any(w in str(tag).lower() for w in words)
            self.fact("addresses", subj, "Etherscan name tag", role, tag, CONFIRMED if hit else MISMATCH, evidence=ev,
                      second_source="Etherscan (independent of Blockscout)")
        else:
            msg = (data.get("result") or data.get("message")) if isinstance(data, dict) else None
            self.fact("addresses", subj, "Etherscan name tag", role, f"HTTP {rec.get('status')}: {str(msg)[:120]}",
                      NOT_VERIFIABLE, evidence=ev,
                      note="Etherscan did not return a tag with the available key (name tags are an API Pro feature)")

    def _affiliate_fact(self, addr: str, subj: str, steps: dict[int, dict[str, Any]]) -> None:
        rango_step = next(t for t in self.fx["transactions"] if t.get("rango"))
        rec = self.b.eth_tx.get(rango_step["txid"]) or {}
        logs = evm_logs_from_blockscout(rec.get("logs") or [])
        fi = next((lg["decoded"] for lg in logs if lg["decoded"] and lg["decoded"]["event"] == "FeeInfo"), None)
        ri = next((lg["decoded"] for lg in logs if lg["decoded"] and lg["decoded"]["event"] == "RangoBridgeInitiated"),
                  None)
        if not fi:
            self.fact("addresses", subj, "affiliate of MoonGate, 0.15% fee", "0.15%", None, NOT_VERIFIABLE)
            return
        inp = int(Decimal(rango_step["amount"]).scaleb(6))
        share = Decimal(fi["affiliateFee"]) / Decimal(inp) * 100
        self.fact("addresses", subj, "Rango affiliate of dApp 'MoonGate' with a 0.15% fee", "MoonGate, 0.15%",
                  f"FeeInfo.affiliator={fi['affiliatorAddress']}, dAppTag={fi['dAppTag']}, "
                  f"dAppName={ri['dAppName'] if ri else 'n/a'}, fee={_usdt(fi['affiliateFee'])} = {share:.6f}% of "
                  f"{rango_step['amount']}",
                  CONFIRMED if same_evm(fi["affiliatorAddress"], addr) and abs(share - Decimal("0.15")) < Decimal("0.0001")
                  and ri and ri["dAppName"] == "MoonGate" else MISMATCH, evidence=[f"eth_logs:{rango_step['txid']}"])

    def _deposit_fact(self, addr: str, subj: str) -> None:
        win = next((v for k, v in self.b.trc20.items() if k.startswith(f"deposit:{addr}")), None)
        if not win:
            self.fact("addresses", subj, "deposit pattern", "WhiteBIT deposit address", None, NOT_VERIFIABLE)
            return
        tr = v1_transfer_rows(win["rows"], USDT_TRC20)
        ins = [r for r in tr if r["to"] == addr]
        outs = [r for r in tr if r["from"] == addr]
        if ins and outs:
            delay = (outs[0]["ts"] - ins[0]["ts"]) // 1000
            obs = (f"received {_usdt(ins[0]['value'])} at {ts_utc(ins[0]['ts'])}, forwarded {_usdt(outs[0]['value'])} "
                   f"to {outs[0]['to']} after {delay} s")
            full = outs[0]["value"] >= ins[0]["value"] * 99 // 100
            hot = outs[0]["to"] == "TWBPGLwQw2EbqYLLw1DJnTDt2ZQ9yJW1JJ"
            self.fact("addresses", subj, "deposit pattern: full and quick forward to the WhiteBIT-tagged wallet",
                      "WhiteBIT deposit address", obs, CONFIRMED if full and hot and delay <= 3600 else MISMATCH,
                      evidence=[f"trc20:deposit:{addr}:6h"],
                      note="attribution to WhiteBIT rests on the hot-wallet label (TronScan, pending written consent)")
        else:
            self.fact("addresses", subj, "deposit pattern", "WhiteBIT deposit address", "no forward found",
                      MISMATCH, evidence=[f"trc20:deposit:{addr}:6h"])

    def _tronscan_fact(self, addr: str, rec: dict[str, Any], subj: str) -> None:
        from ..sources.case001_tronscan import tag_fields

        data = rec.get("data")
        tags = tag_fields(data) if isinstance(data, dict) else {}
        text = str(tags)
        if rec.get("status") is None:
            verdict, obs = NOT_VERIFIABLE, "TronScan lookup not performed"
        elif rec.get("status") != 200:
            verdict, obs = NOT_VERIFIABLE, (f"HTTP {rec.get('status')}" + (" (TronScan API requires an API key; "
                                                                           "keyless lookup refused)"
                                                                           if rec.get("status") == 401 else ""))
        else:
            verdict = CONFIRMED if "whitebit" in text.lower() else NOT_VERIFIABLE
            obs = tags or "no tag-like fields in the response"
        self.fact("addresses", subj, "TronScan tag 'WhiteBIT'", "WhiteBIT", obs, verdict,
                  evidence=[f"tronscan_account:{addr}"],
                  note="TronScan, pending written consent, not stored in any label store; one lookup, development "
                       "verification only")

    # ---------------------------------------------------------------- links
    def _links(self) -> None:
        link = self.fx["links"][0]
        funder = link["funder"]
        for f in link["funded"]:
            for txid in f["txids"]:
                self._trx_transfer_fact(txid, funder, f["addr"], "links", f"funder->{f['addr'][:10]}")
            for txid in f.get("returns_trx_to_funder") or []:
                self._trx_transfer_fact(txid, f["addr"], funder, "links", f"return {f['addr'][:10]}->funder")
            if f.get("note"):
                acct = (self.b.tron_account.get(funder) or {}).get("tg") or {}
                rows = v1_native_rows((self.b.account_txs.get(f"funded:{f['addr']}:earliest-inbound") or {}).get("rows")
                                      or [])
                trx_in = [r for r in rows if r["type"] == "TransferContract"]
                first = trx_in[0] if trx_in else None
                self.eq("links", f"{f['addr'][:10]}", "activation (note)", "activated by funder at 2026-08-06 17:47:57",
                        f"activated by {'funder' if first and first['owner'] == funder else (first or {}).get('owner')}"
                        f" at {ts_utc(first['ts'])}" if first else None,
                        evidence=[f"account_txs:funded:{f['addr']}:earliest-inbound"])
                self.eq("links", f"{funder[:10]}", "funder created (note: 17:22:48)", "2026-08-06 17:22:48",
                        ts_utc(acct.get("create_time"))
                        if acct else None, evidence=[f"tron_account:{funder}"])
        up = link.get("funder_upstream") or {}
        for s in up.get("txids") or []:
            txid = s.split(" ")[0]
            amount = s.split("(")[1].split(" TRX")[0]
            frm = s.split("from ")[1].split(",")[0].split(")")[0].strip()
            self._trx_transfer_fact(txid, frm, funder, "links", f"upstream {frm[:10]}->funder", amount=amount)
        for frm_addr, by in (("TMGtBUqWevfE2y1XpvzTsHEkLpSDi4bW51", "TSm7vUxW9DvKiwwDRcaR36X8vBjKc99Sxe"),):
            rows = v1_native_rows((self.b.account_txs.get(f"upstream:{frm_addr}:earliest-inbound") or {}).get("rows") or [])
            senders = sorted({r["owner"] for r in rows if r["type"] == "TransferContract"
                              and (r["amount_sun"] or 0) >= 1_000_000})
            self.fact("links", f"{frm_addr[:10]} upstream", f"funded by {by[:10]}", by, senders if rows else None,
                      (CONFIRMED if by in senders else MISMATCH) if rows else NOT_VERIFIABLE,
                      evidence=[f"account_txs:upstream:{frm_addr}:earliest-inbound"],
                      note="senders of >= 1 TRX among its earliest 50 inbound transactions" if rows else "no data")
        tsm = "TSm7vUxW9DvKiwwDRcaR36X8vBjKc99Sxe"
        acct = (self.b.tron_account.get(tsm) or {}).get("tg") or {}
        self.fact("links", "TSm7vU", "active since 2024-11 (unlabelled service)", "since 2024-11",
                  f"create_time {ts_utc(acct.get('create_time'))}" if acct else None,
                  CONFIRMED if acct and (ts_utc(acct.get("create_time")) or "").startswith("2024-11") else
                  (MISMATCH if acct else NOT_VERIFIABLE), evidence=[f"tron_account:{tsm}"],
                  note="'high-volume' and 'likely a service' are interpretations, not checked")
        reuse = self.fx["links"][1] if len(self.fx["links"]) > 1 else None
        if reuse:
            for flow in reuse["flows"]:
                path = flow["path"]
                for txid in flow["txids"]:
                    self._reuse_tx_fact(txid, path)
                hop = path[-2]
                win = self.b.trc20.get(f"reuse_flow:{hop}") or {}
                tr = v1_transfer_rows(win.get("rows") or [], USDT_TRC20)
                outs = [r for r in tr if r["from"] == hop]
                ins = [r for r in tr if r["to"] == hop]
                to_bw = [r for r in outs if r["to"] == path[-1]]
                to_fee = [r for r in outs if r["to"] == "TRUJEtAFzBWReAUu5L83wFRvxWtrVw3sAz"]
                if ins and to_bw and to_fee:
                    a_in = ins[0]["value"]
                    ok = is_exact_cut(to_fee[0]["value"], a_in, "0.01") and to_bw[0]["value"] == a_in - to_fee[0]["value"]
                    mode = "floor" if to_fee[0]["value"] == trunc_share(a_in, "0.01") else "half-up"
                    obs = (f"{hop[:10]} received {_usdt(a_in)}, sent {_usdt(to_bw[0]['value'])} to {path[-1][:10]} and "
                           f"{_usdt(to_fee[0]['value'])} to TRUJEt ({ts_utc(to_bw[0]['ts'])}); 1% of the input at "
                           f"6 decimals, rounding: {mode}")
                    self.fact("links", f"reused route via {hop[:10]}", "99% to TUrQNN + exactly 1% to TRUJEt",
                              "99%/1% split", obs, CONFIRMED if ok else MISMATCH, evidence=[f"trc20:reuse_flow:{hop}"])
                else:
                    self.fact("links", f"reused route via {hop[:10]}", "99% to TUrQNN + exactly 1% to TRUJEt",
                              "99%/1% split", f"in={len(ins)}, to TUrQNN={len(to_bw)}, to TRUJEt={len(to_fee)}",
                              NOT_VERIFIABLE if not tr else MISMATCH, evidence=[f"trc20:reuse_flow:{hop}"])
            transit = next(t["to"] for t in self.fx["transactions"] if t.get("kind") == "bridge_in_USDT0")
            tr = self.b.eth_address_transfers.get(transit) or {}
            rows = [r for r in blockscout_transfer_rows(tr.get("rows") or []) if same_evm(r["token"], USDT_ERC20)
                    and same_evm(r["to"], transit)]
            for item in reuse.get("ethereum_0x4079_other_inbound_bridges") or []:
                day, amount = item.split(" ")
                hit = [r for r in rows if ts_utc(r["ts"]).startswith(day) and _usdt(r["value"]) == amount]
                self.fact("links", "0x4079 other inbound bridges", f"{day} {amount}", item,
                          f"{ts_utc(hit[0]['ts'])} {_usdt(hit[0]['value'])} from {hit[0]['from'][:10]} tx {hit[0]['txid'][:12]}"
                          if hit else "not found in Blockscout transfers",
                          CONFIRMED if hit else (MISMATCH if tr.get("complete") else NOT_VERIFIABLE),
                          evidence=[f"eth_address_transfers:{transit}"])

    def _trx_transfer_fact(self, txid: str, frm: str, to: str, group: str, subj: str, amount: str | None = None) -> None:
        rec = self._tx(txid)
        tx, info = rec.get("tx") or {}, rec.get("info") or {}
        ev = [f"tron_tx:{txid}", f"tron_info:{txid}"]
        if not tx:
            self.fact(group, subj, f"TRX transfer {txid[:10]}", f"{frm[:10]}->{to[:10]}", None, NOT_VERIFIABLE,
                      evidence=ev, note="no data")
            return
        c = tron_contract(tx)
        obs = f"{c.get('type')} {c.get('owner')}->{c.get('to')} {fmt(c['amount_sun']) if c.get('amount_sun') is not None else ''} TRX at {ts_utc(info.get('blockTimeStamp'))}"
        ok = c.get("type") == "TransferContract" and c.get("owner") == frm and c.get("to") == to and c.get("ret") == "SUCCESS"
        if amount is not None and c.get("amount_sun") is not None:
            ok = ok and Decimal(fmt(c["amount_sun"])) == Decimal(amount)
        self.fact(group, subj, f"TRX transfer {txid[:10]}",
                  f"{frm}->{to}" + (f" {amount} TRX" if amount else ""), obs, CONFIRMED if ok else MISMATCH,
                  evidence=ev, second_source=self._pn_note(txid))

    def _reuse_tx_fact(self, txid: str, path: list[str]) -> None:
        rec = self._tx(txid)
        info = rec.get("info") or {}
        trs = [x for x in tron_token_transfers(info) if x["token"] == USDT_TRC20]
        ev = [f"tron_info:{txid}"]
        if not trs:
            self.fact("links", f"reused route tx {txid[:10]}", "USDT transfer on the path", "path " + "->".join(
                p[:6] for p in path), "no USDT transfer in receipt" if info else None,
                MISMATCH if info else NOT_VERIFIABLE, evidence=ev)
            return
        x = trs[0]
        on_path = x["to"] in path or x["from"] in path
        self.fact("links", f"reused route tx {txid[:10]}", "USDT transfer on the path",
                  "path " + "->".join(p[:6] for p in path),
                  f"{x['from'][:10]}->{x['to'][:10]} {_usdt(x['value'])} at {ts_utc(info.get('blockTimeStamp'))}",
                  CONFIRMED if on_path else MISMATCH, evidence=ev)

    # ---------------------------------------------------------------- arithmetic
    def _ground_truth_arithmetic(self, steps: dict[int, dict[str, Any]]) -> None:
        gt = self.fx["ground_truth"]
        theft = int(Decimal(self.fx["theft"]["amount"]).scaleb(6))
        arrived = int(Decimal(steps[17]["amount"]).scaleb(6))
        self.eq("ground_truth", "arithmetic", "total_fees_lost_before_hub = 13041.400772 - 12878.454902",
                Decimal(gt["total_fees_lost_before_hub"]), Decimal(_usdt(theft - arrived)),
                note="fixture amounts; both endpoints are confirmed on chain in the transaction rows")
        lz = steps[12]["layerzero"]
        fee_usdt0 = int(Decimal(steps[12]["amount"]).scaleb(6)) - int(Decimal(lz["amountReceivedLD"]).scaleb(6))
        near_fee = int(Decimal(steps[16]["amount"]).scaleb(6)) - arrived
        parts = {
            "energy fee TYGdh7->TDii6v (step 7)": int(Decimal(steps[7]["amount"]).scaleb(6)),
            "left on TYGdh7 (13041.400772 - 5.486343 - 13035.640112)": theft - int(Decimal(steps[7]["amount"]).scaleb(6))
            - int(Decimal(steps[8]["amount"]).scaleb(6)),
            "1% to TRUJEt (step 10)": int(Decimal(steps[10]["amount"]).scaleb(6)),
            "left on TUrQNN (12905.283711 - 12905.28)": int(Decimal(steps[9]["amount"]).scaleb(6))
            - int(Decimal(steps[12]["amount"]).scaleb(6)),
            "USDT0 fee (12905.28 - 12901.408416)": fee_usdt0,
            "0x4079 added own balance (12901.408416 - 12901.411)": int(Decimal(lz["amountReceivedLD"]).scaleb(6))
            - int(Decimal(steps[15]["amount"]).scaleb(6)),
            "Rango affiliate fee": int(Decimal(steps[15]["rango"]["affiliateFee"]).scaleb(6)),
            "NEAR Intents (12882.058884 - 12878.454902)": near_fee,
        }
        total = sum(parts.values())
        self.fact("ground_truth", "arithmetic", "fee components reconcile to total_fees_lost_before_hub",
                  gt["total_fees_lost_before_hub"], {k: _usdt(v) for k, v in parts.items()} | {"sum": _usdt(total)},
                  CONFIRMED if total == theft - arrived else MISMATCH)
        # every hop reconciles with its neighbours (data_caveat)
        checks = [
            ("step 15 = affiliateFee + forwarded_amount", steps[15]["amount"],
             _usdt(int(Decimal(steps[15]["rango"]["affiliateFee"]).scaleb(6))
                   + int(Decimal(steps[15]["rango"]["forwarded_amount"]).scaleb(6)))),
            ("step 16 amount = Rango forwarded_amount", steps[16]["amount"], steps[15]["rango"]["forwarded_amount"]),
            ("step 14 amount = USDT0 amountReceivedLD", steps[14]["amount"], lz["amountReceivedLD"]),
            ("step 8 + step 7 + residual = theft", self.fx["theft"]["amount"],
             _usdt(int(Decimal(steps[7]["amount"]).scaleb(6)) + int(Decimal(steps[8]["amount"]).scaleb(6))
                   + int(Decimal("0.274317").scaleb(6)))),
        ]
        for name, a, b in checks:
            self.fact("ground_truth", "arithmetic", name, a, b, CONFIRMED if Decimal(a) == Decimal(b) else MISMATCH)


def summarize(facts: list[dict[str, Any]]) -> dict[str, Any]:
    by: dict[str, dict[str, int]] = {}
    for f in facts:
        g = by.setdefault(f["group"], {CONFIRMED: 0, MISMATCH: 0, NOT_VERIFIABLE: 0})
        g[f["verdict"]] += 1
    total = {v: sum(g[v] for g in by.values()) for v in (CONFIRMED, MISMATCH, NOT_VERIFIABLE)}
    return {"total": total, "facts": len(facts), "by_group": by,
            "mismatches": [{k: f[k] for k in ("n", "group", "subject", "field", "claim", "observed", "note", "evidence")}
                           for f in facts if f["verdict"] == MISMATCH]}
