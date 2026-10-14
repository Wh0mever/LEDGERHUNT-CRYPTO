"""Builder: creates a synthetic world and, from the same construction, its expected answer.

Templates (``templates.py``) move "lots" of stolen funds with ``hop``/``split``/``merge_hop``
and close every lot with ``end``. A lot's history (``Path.edges``) is exactly one expected
route. ``finalize`` then applies depth limits and designed source failures:

- a route longer than ``max_depth`` ends at depth ``max_depth`` with reason ``max_depth``;
  the deeper edges become *allowed* (true but not required);
- a route that needs the listing of an address whose listing is unavailable, a page of it
  that fails, or a transfer hidden from the index, ends at that address with reason
  ``source_unavailable`` / ``incomplete_listing`` / ``data_gap``; everything behind that
  boundary is kept in the answer with ``excluded`` set, so it leaves the denominator but is
  still counted and reported.

No tracer logic is involved: the answer is what the template built.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable

from ..core.tron import USDT_TRC20, b58_to_bytes, b58_to_evm_hex, format_amount, hex_to_b58
from . import formats as F
from .rng import DetRng
from .schema import EVIDENCE_BOUNDARY_REASONS
from .world import World

BLOCK_REF = 86439360  # real block of the case-001 theft
TS_REF_S = 1789990359  # its timestamp (2026-09-21 11:32:39 UTC)
DAY_MS = 86_400_000
NEEDS_LISTING = frozenset({"funds_at_rest", "exchange_deposit", "commingled"})
SUPPORTED_BRIDGES = [{"protocol": "usdt0_oft", "dst_eids": [30101]}]
EID_CHAINS = {30101: "ethereum", 30110: "arbitrum", 30102: "bsc"}  # informative; only 30101 is confirmed (case-001)
OFT_CONTRACT = hex_to_b58(F.USDT0_OFT_TRON_HEX)
LZ_ENDPOINT = hex_to_b58(F.LZ_ENDPOINT_TRON_HEX)
LZ_SENDLIB = hex_to_b58(F.LZ_SENDLIB_TRON_HEX)
OFT_OPTIONS = "000301001101000000000000000000000000000186a0"  # as in the live packet


def block_of(ts_ms: int) -> int:
    return BLOCK_REF + (ts_ms // 1000 - TS_REF_S) // 3


def amt(raw: int) -> str:
    return format_amount(raw)


@dataclass(frozen=True)
class Path:
    """One lot of traced funds: the edges it travelled and who holds it now."""

    edges: tuple[tuple[str, int], ...]
    holder: str
    amount: int

    def extend(self, edge: tuple[str, int], holder: str, amount: int) -> "Path":
        return Path(self.edges + (edge,), holder, amount)


@dataclass
class _Terminal:
    path: Path
    reason: str
    kind: str


@dataclass
class _Exchange:
    exchange: str
    hot_wallet: str
    pending: int = 0
    sweep_txids: list[str] = field(default_factory=list)
    sweep_edges: list[tuple[str, int]] = field(default_factory=list)


class Builder:
    def __init__(self, rng: DetRng, scenario_id: str, *, start_ms: int, max_depth: int = 20) -> None:
        self.rng = rng
        self.sid = scenario_id
        self.now_ms = start_ms - start_ms % 3000
        self.max_depth = max_depth
        self.txs: list[dict[str, Any]] = []
        self.opening: dict[str, int] = {}
        self.openable: set[str] = set()
        self.bal: dict[str, int] = {}
        self.labels: list[dict[str, Any]] = []
        self.lz: dict[str, dict[str, Any]] = {}
        self.outages: list[dict[str, Any]] = []
        self.hidden: set[str] = set()
        self.edge_info: dict[tuple[str, int], dict[str, Any]] = {}
        self.terminals: list[_Terminal] = []
        self.exchanges: dict[str, _Exchange] = {}
        self.bridges: dict[str, dict[str, Any]] = {}
        self.merges: dict[str, dict[str, list[str]]] = {}
        self.uncertain_edges: list[tuple[str, int]] = []
        self.uncertain_exchanges: set[str] = set()
        self.traps: list[dict[str, Any]] = []
        self.start_txid: str | None = None
        self.victim: str | None = None
        self.notes: list[str] = []
        self._addrs: set[str] = set()

    # ------------------------------------------------------------------ basics
    def tick(self, lo_s: int = 3, hi_s: int = 600) -> None:
        self.now_ms += 3000 * self.rng.randint(max(1, lo_s // 3), max(1, hi_s // 3))

    def addr(self) -> str:
        while True:
            a = hex_to_b58("41" + self.rng.hex(20))
            if a not in self._addrs:
                self._addrs.add(a)
                return a

    def evm_addr(self) -> str:
        return "0x" + self.rng.hex(20)

    def source(self) -> str:
        """An outside account whose earlier history is not part of the world (opening balance allowed)."""
        a = self.addr()
        self.openable.add(a)
        return a

    def lookalike(self, target: str) -> str:
        """Address sharing the first 5 and last 2 base58 characters with ``target`` (poisoning lookalike)."""
        tb = b58_to_bytes(target)
        cand = target
        for _ in range(100_000):
            cand = hex_to_b58((tb[:4] + self.rng.bytes(17)).hex())
            if cand != target and cand[:5] == target[:5] and cand[-2:] == target[-2:]:
                break
        self._addrs.add(cand)
        self.openable.add(cand)
        return cand

    def label(self, address: str, entity: str, typ: str, **extra: Any) -> str:
        self.labels.append({"address": address, "entity": entity, "type": typ, "source": "synthetic_registry", **extra})
        return address

    def trap(self, txid: str, reason: str, event_index: int | None = None) -> None:
        self.traps.append({"txid": txid, "event_index": event_index, "reason": reason})

    # ------------------------------------------------------------------ balances
    def _move(self, frm: str, to: str, value: int) -> None:
        have = self.bal.get(frm, 0)
        if have < value:
            if frm not in self.openable:
                raise AssertionError(f"{self.sid}: {frm} would go negative ({have} < {value})")
            self.opening[frm] = self.opening.get(frm, 0) + (value - have)
            have = value
        self.bal[frm] = have - value
        self.bal[to] = self.bal.get(to, 0) + value

    # ------------------------------------------------------------------ transactions
    def _receipt(self, *, fresh_recipient: bool, burn: bool | None = None) -> tuple[dict[str, Any], int]:
        energy = 130285 if fresh_recipient else 64285
        penalty = energy - 29650
        if burn is None:
            burn = self.rng.chance(1, 2)
        if burn:
            rec = {"energy_fee": energy * 100, "energy_usage_total": energy, "net_fee": 345000, "result": "SUCCESS",
                   "energy_penalty_total": penalty}
            return rec, energy * 100 + 345000
        rec = {"energy_usage": energy, "energy_usage_total": energy, "net_fee": 345000, "result": "SUCCESS",
               "energy_penalty_total": penalty}
        return rec, 345000

    def _tx(self, owner: str, ctype: str, *, contract: str | None = None, data: str = "", call_value: int = 0,
            to: str | None = None, amount: int = 0, status: str = "SUCCESS", events: list[dict[str, Any]] | None = None,
            fee_limit: int | None = None, receipt: dict[str, Any] | None = None, fee: int = 0,
            contract_result: list[str] | None = None, internal: list[dict[str, Any]] | None = None,
            res_message: str | None = None) -> dict[str, Any]:
        ts = self.now_ms
        block = block_of(ts)
        created = ts - 3000 + self.rng.randint(0, 2000)
        ref_block = block - self.rng.randint(8, 30)
        tx: dict[str, Any] = {
            "block": block, "ts_ms": ts, "created_ms": created, "owner": owner, "ctype": ctype,
            "ref_block_bytes": f"{ref_block & 0xFFFF:04x}", "ref_block_hash": self.rng.hex(8),
            "expiration": created + 60_000, "status": status, "events": events or [], "fee": fee,
        }
        if ctype == "TriggerSmartContract":
            tx.update({"contract": contract, "data": data, "fee_limit": fee_limit or 30_000_000})
            if call_value:
                tx["call_value"] = call_value
            tx["receipt"] = receipt or {}
            tx["contract_result"] = contract_result or [""]
        else:
            tx.update({"to": to, "amount": amount, "net_usage": 267})
        if internal:
            tx["internal_transactions"] = internal
        if res_message:
            tx["res_message"] = res_message
        raw = F.raw_data_dict(tx, visible=True)
        raw_bytes = F.encode_raw_data(raw)
        tx["raw_data_hex"] = raw_bytes.hex()
        tx["txid"] = F.txid_of(raw_bytes)
        tx["signature"] = self.rng.hex(65)  # synthetic, not a valid signature
        for i, ev in enumerate(tx["events"]):
            ev["index"] = i
        self.txs.append(tx)
        return tx

    def _transfer_event(self, frm: str, to: str, value: int) -> dict[str, Any]:
        return {"contract": USDT_TRC20, "name": "Transfer", "args": {"from": frm, "to": to, "value": value}}

    def usdt_transfer(self, frm: str, to: str, value: int, *, owner: str | None = None, status: str = "SUCCESS",
                      tick: bool = True) -> tuple[str, int]:
        """USDT transfer (transfer() by the holder, or transferFrom() by a spender). Returns the edge key."""
        if tick:
            self.tick()
        owner = owner or frm
        if owner == frm:
            data = F.SELECTOR_TRANSFER + F.addr_word(to) + F.word(value)
        else:
            data = F.SELECTOR_TRANSFER_FROM + F.addr_word(frm) + F.addr_word(to) + F.word(value)
        if status != "SUCCESS":
            limit = self.rng.randint(5, 15) * 1_000_000
            if status == "OUT_OF_ENERGY":
                rec = {"energy_fee": limit, "energy_usage_total": limit // 100, "net_fee": 345000, "result": "OUT_OF_ENERGY"}
                msg = "Not enough energy for 'SSTORE' operation executing (synthetic message)"
            else:
                rec = {"energy_usage_total": 29650, "net_fee": 345000, "result": "REVERT"}
                msg = "REVERT opcode executed (synthetic message)"
            tx = self._tx(owner, "TriggerSmartContract", contract=USDT_TRC20, data=data, status=status, fee_limit=limit,
                          receipt=rec, fee=rec.get("energy_fee", 0) + 345000, res_message=msg.encode().hex())
            return tx["txid"], -1
        fresh = self.bal.get(to, 0) == 0
        rec, fee = self._receipt(fresh_recipient=fresh)
        self._move(frm, to, value)
        tx = self._tx(owner, "TriggerSmartContract", contract=USDT_TRC20, data=data, receipt=rec, fee=fee,
                      contract_result=[F.word(0)], events=[self._transfer_event(frm, to, value)])
        key = (tx["txid"], 0)
        self.edge_info[key] = {"from": frm, "to": to, "value": value, "ts_ms": tx["ts_ms"]}
        return key

    def approve(self, owner: str, spender: str, value: int) -> str:
        self.tick(3, 120)
        rec, fee = self._receipt(fresh_recipient=False)
        rec = dict(rec, energy_usage_total=23000, energy_penalty_total=0)
        tx = self._tx(owner, "TriggerSmartContract", contract=USDT_TRC20,
                      data=F.SELECTOR_APPROVE + F.addr_word(spender) + F.word(value), receipt=rec, fee=fee,
                      contract_result=[F.word(1)],
                      events=[{"contract": USDT_TRC20, "name": "Approval",
                               "args": {"owner": owner, "spender": spender, "value": value}}])
        self.trap(tx["txid"], "approval_not_transfer", 0)
        return tx["txid"]

    def trx(self, frm: str, to: str, sun: int) -> str:
        self.tick(3, 300)
        return self._tx(frm, "TransferContract", to=to, amount=sun)["txid"]

    def multi_transfer(self, frm: str, contract: str, parts: list[tuple[str, int]], *, owner: str | None = None,
                       tick: bool = True) -> list[tuple[str, int]]:
        """One transaction through ``contract`` emitting one USDT Transfer per part (event_index 0..n-1)."""
        if tick:
            self.tick()
        n = len(parts)
        data = (F.SELECTOR_BATCH + F.word(0x40) + F.word(0x40 + 32 * (n + 1)) + F.word(n)
                + "".join(F.addr_word(t) for t, _ in parts) + F.word(n) + "".join(F.word(v) for _, v in parts))
        events = []
        for to, v in parts:
            self._move(frm, to, v)
            events.append(self._transfer_event(frm, to, v))
        rec, fee = self._receipt(fresh_recipient=True)
        rec = dict(rec, energy_usage_total=rec["energy_usage_total"] * n)
        tx = self._tx(owner or frm, "TriggerSmartContract", contract=contract, data=data, receipt=rec, fee=fee,
                      contract_result=[F.word(1)], events=events)
        keys = []
        for i, (to, v) in enumerate(parts):
            key = (tx["txid"], i)
            self.edge_info[key] = {"from": frm, "to": to, "value": v, "ts_ms": tx["ts_ms"]}
            keys.append(key)
        return keys

    # ------------------------------------------------------------------ flows
    def fund_victim(self, victim: str, payments: list[int]) -> None:
        payer = self.source()
        for v in payments:
            txid, _ = self.usdt_transfer(payer, victim, v)
            self.trap(txid, "pre_theft_inflow", 0)
            self.tick(60, 7200)

    def theft(self, *, payments: list[int] | None = None, amount: int | None = None, via_spender: bool = False) -> Path:
        """Victim gets 1-2 payments, then the theft transfer. Returns the stolen lot held by the thief."""
        victim = self.addr()
        thief = self.addr()
        self.victim = victim
        payments = payments or [self.rng.amount(500_000_000, 150_000_000_000)]
        self.fund_victim(victim, payments)
        amount = amount or sum(payments)
        owner = None
        if via_spender:  # approval phishing: an earlier approve to a malicious spender, then transferFrom
            spender = self.addr()
            self.approve(victim, spender, 2**256 - 1)
            owner = spender
        self.tick(30, 900)
        key = self.usdt_transfer(victim, thief, amount, owner=owner, tick=False)
        self.start_txid = key[0]
        return Path((key,), thief, amount)

    def hop(self, path: Path, to: str | None = None, value: int | None = None, *, owner: str | None = None) -> Path:
        to = to or self.addr()
        value = path.amount if value is None else value
        key = self.usdt_transfer(path.holder, to, value, owner=owner)
        return path.extend(key, to, value)

    def chain(self, path: Path, hops: int) -> Path:
        for _ in range(hops):
            path = self.hop(path)
        return path

    def split(self, path: Path, parts: list[tuple[str | None, int]]) -> list[Path]:
        if sum(v for _, v in parts) != path.amount:
            raise AssertionError(f"{self.sid}: split parts do not add up")
        return [self.hop(path, to, v) for to, v in parts]

    def batch_split(self, path: Path, parts: list[tuple[str | None, int]]) -> list[Path]:
        contract = self.addr()
        parts2 = [(to or self.addr(), v) for to, v in parts]
        total = sum(v for _, v in parts2)
        if total != path.amount:
            raise AssertionError(f"{self.sid}: batch parts do not add up")
        self.approve(path.holder, contract, total)
        keys = self.multi_transfer(path.holder, contract, parts2)
        return [path.extend(k, to, v) for k, (to, v) in zip(keys, parts2)]

    def merge_hop(self, paths: list[Path], to: str | None = None) -> list[Path]:
        holders = {p.holder for p in paths}
        if len(holders) != 1:
            raise AssertionError(f"{self.sid}: merge_hop needs one holder")
        to = to or self.addr()
        total = sum(p.amount for p in paths)
        key = self.usdt_transfer(paths[0].holder, to, total)
        return [p.extend(key, to, p.amount) for p in paths]

    def fee(self, path: Path, collector: str, value: int) -> Path:
        """Side branch paid out of the lot (energy rental, 1% cut). Returns the remaining lot."""
        key = self.usdt_transfer(path.holder, collector, value)
        lab = next((l for l in self.labels if l["address"] == collector), None)
        reason = "known_service" if lab else "funds_at_rest"
        self.end(path.extend(key, collector, value), reason, kind="side_branch")
        return Path(path.edges, path.holder, path.amount - value)

    def end(self, path: Path, reason: str, *, kind: str = "main") -> None:
        self.terminals.append(_Terminal(path, reason, kind))

    # ------------------------------------------------------------------ exchanges
    def exchange(self, name: str) -> str:
        """Labelled hot wallet of a synthetic exchange (with a few other users' sweeps as background)."""
        hot = self.label(self.addr(), name, "exchange_hot_wallet")
        return hot

    def background_sweeps(self, hot: str, n: int) -> None:
        for _ in range(n):
            other = self.source()
            self.usdt_transfer(other, hot, self.rng.amount(50_000_000, 40_000_000_000), owner=other)
            self.trap(self.txs[-1]["txid"], "exchange_internal", 0)

    def deposit(self, path: Path, name: str, hot: str, deposit: str | None = None) -> str:
        deposit = deposit or self.addr()
        ex = self.exchanges.setdefault(deposit, _Exchange(name, hot))
        p = self.hop(path, deposit)
        ex.pending += p.amount
        self.end(p, "exchange_deposit")
        return deposit

    def sweep(self, deposit: str, *, delay: tuple[int, int] = (60, 1800)) -> str:
        ex = self.exchanges[deposit]
        self.tick(*delay)
        key = self.usdt_transfer(deposit, ex.hot_wallet, ex.pending, tick=False)
        ex.sweep_txids.append(key[0])
        ex.sweep_edges.append(key)
        ex.pending = 0
        return key[0]

    # ------------------------------------------------------------------ commingling
    def foreign_in(self, hub: str, value: int, *, reason: str = "foreign_inflow") -> str:
        src = self.source()
        key = self.usdt_transfer(src, hub, value, owner=src)
        self.merges.setdefault(hub, {"traced": [], "foreign": []})["foreign"].append(key[0])
        self.trap(key[0], reason, 0)
        return key[0]

    def commingle(self, path: Path, hub: str) -> Path:
        p = self.hop(path, hub)
        self.merges.setdefault(hub, {"traced": [], "foreign": []})["traced"].append(p.edges[-1][0])
        self.end(p, "commingled")
        return p

    def uncertain_out(self, hub: str, to: str | None, value: int) -> tuple[str, int]:
        to = to or self.addr()
        key = self.usdt_transfer(hub, to, value)
        self.uncertain_edges.append(key)
        return key

    # ------------------------------------------------------------------ bridges
    def oft_send(self, path: Path, dst_eid: int, *, recipient: str | None = None, indexed: bool = True,
                 approve: bool = True) -> Path:
        """USDT0-like OFT send from the lot holder (Transfer + fee events + PacketSent + OFTSent)."""
        sender = path.holder
        sent = path.amount
        received = sent - sent * 3 // 10_000  # 0.03 %, as observed on the case-001 send
        recipient = (recipient or self.evm_addr()).lower()
        if approve:
            self.approve(sender, OFT_CONTRACT, sent)
        self.tick(3, 120)
        nonce = self.rng.randint(20_000, 60_000)
        receiver_oapp = F.USDT0_OFT_ETH_ADAPTER if dst_eid == 30101 else self.evm_addr()
        sender_word = F.USDT0_OFT_TRON_HEX[2:].rjust(64, "0")
        receiver_word = receiver_oapp[2:].rjust(64, "0")
        guid = F.oft_guid(nonce, F.TRON_EID, sender_word, dst_eid, receiver_word)
        message = F.oft_message(recipient, received)
        exec_fee = self.rng.randint(4_000_000, 6_000_000)
        dvn_fees = [self.rng.randint(300_000, 400_000), self.rng.randint(300_000, 400_000)]
        native_fee = exec_fee + sum(dvn_fees)
        data = (F.SELECTOR_OFT_SEND + F.word(0x80) + F.word(native_fee) + F.word(0) + F.addr_word(sender)
                + F.word(dst_eid) + F.addr_word(recipient) + F.word(sent) + F.word(received)
                + F.word(0xE0) + F.word(0x100) + F.word(0x120) + F.word(0) + F.word(0) + F.word(0))
        events = [
            self._transfer_event(sender, OFT_CONTRACT, sent),
            {"contract": LZ_SENDLIB, "name": "ExecutorFeePaid", "args": {"executor": F.LZ_EXECUTOR, "fee": exec_fee}},
            {"contract": LZ_SENDLIB, "name": "DVNFeePaid",
             "args": {"requiredDVNs": list(F.LZ_DVNS), "optionalDVNs": [], "fees": dvn_fees}},
            {"contract": LZ_ENDPOINT, "name": "PacketSent",
             "args": {"encodedPayload": F.packet_encoded(nonce, F.TRON_EID, sender_word, dst_eid, receiver_word, guid,
                                                         message),
                      "options": OFT_OPTIONS, "sendLibrary": "0x" + F.LZ_SENDLIB_TRON_HEX[2:]}},
            {"contract": OFT_CONTRACT, "name": "OFTSent",
             "args": {"guid": guid, "dstEid": dst_eid, "fromAddress": sender, "amountSentLD": sent,
                      "amountReceivedLD": received}},
        ]
        energy = self.rng.randint(200_000, 240_000)
        rec = {"energy_fee": energy * 100, "energy_usage_total": energy, "net_fee": 736000, "result": "SUCCESS",
               "energy_penalty_total": self.rng.randint(60_000, 75_000)}
        internal = [
            {"hash": self.rng.hex(32), "caller_address": F.USDT0_OFT_TRON_HEX, "transferTo_address": "41" + USDT_TRC20_HEX40,
             "callValueInfo": [{}], "note": "63616c6c"},
            {"hash": self.rng.hex(32), "caller_address": F.USDT0_OFT_TRON_HEX, "transferTo_address": F.LZ_ENDPOINT_TRON_HEX,
             "callValueInfo": [{"callValue": native_fee}], "note": "63616c6c"},
        ]
        result = guid + F.word(nonce) + F.word(native_fee) + F.word(0) + F.word(sent) + F.word(received)
        self._move(sender, OFT_CONTRACT, sent)
        tx = self._tx(sender, "TriggerSmartContract", contract=OFT_CONTRACT, data=data, call_value=native_fee,
                      events=events, fee_limit=150_000_000, receipt=rec, fee=rec["energy_fee"] + 736000,
                      contract_result=[result], internal=internal)
        key = (tx["txid"], 0)
        self.edge_info[key] = {"from": sender, "to": OFT_CONTRACT, "value": sent, "ts_ms": tx["ts_ms"]}
        src_ts = tx["ts_ms"] // 1000
        msg = {
            "src_txid": tx["txid"], "guid": guid, "nonce": nonce, "dst_eid": dst_eid,
            "dst_chain": EID_CHAINS.get(dst_eid, f"eid-{dst_eid}"), "dst_oapp": receiver_oapp, "recipient": recipient,
            "indexed": indexed, "status": "DELIVERED", "src_block": tx["block"], "src_block_hash": "0x" + self.rng.hex(32),
            "src_ts": src_ts, "src_from": b58_to_evm_hex(sender), "message": message,
            "dst_txid": "0x" + self.rng.hex(32), "dst_block": 26_000_000 + self.rng.randint(0, 900_000),
            "dst_block_hash": "0x" + self.rng.hex(32), "dst_ts": src_ts + self.rng.randint(90, 400),
            "created": _iso(src_ts + 17), "updated": _iso(src_ts + 420),
            "amount_sent": sent, "amount_received": received,
        }
        msg.update({
            "verify_txids": ["0x" + self.rng.hex(32), "0x" + self.rng.hex(32)], "verify_block": msg["dst_block"] - 2,
            "verify_block_hash": "0x" + self.rng.hex(32), "verify_ts": msg["dst_ts"] - 24,
            "sealer_txid": "0x" + self.rng.hex(32), "sealer_block": msg["dst_block"] - 1,
            "sealer_block_hash": "0x" + self.rng.hex(32), "sealer_ts": msg["dst_ts"] - 12,
        })
        self.lz[tx["txid"]] = msg
        self.bridges[tx["txid"]] = {"protocol": "usdt0_oft", "dst_eid": dst_eid, "sender": sender}
        p = path.extend(key, OFT_CONTRACT, sent)
        self.end(p, "bridge")  # resolved in finalize (supported / unsupported / unconfirmed)
        return p

    def unknown_bridge(self, path: Path, name: str) -> Path:
        contract = self.label(self.addr(), name, "bridge_contract", protocol=f"unknown_bridge:{_slug(name)}")
        p = self.hop(path, contract)
        self.bridges[p.edges[-1][0]] = {"protocol": f"unknown_bridge:{_slug(name)}", "dst_eid": None,
                                        "sender": path.holder}
        self.end(p, "bridge")
        return p

    # ------------------------------------------------------------------ noise / traps
    def poison(self, holder: str, imitate: str, *, zero: bool = True) -> str:
        """Zero-value transferFrom(holder -> lookalike of ``imitate``) signed by a poisoner."""
        look = self.lookalike(imitate)
        poisoner = self.source()
        txid, _ = self.usdt_transfer(holder, look, 0, owner=poisoner)
        self.trap(txid, "zero_value_poisoning", 0)
        return look

    def dust_to(self, target: str, imitate: str) -> str:
        look = self.lookalike(imitate)
        txid, _ = self.usdt_transfer(look, target, self.rng.randint(1, 10_000), owner=look)
        self.trap(txid, "lookalike_dust", 0)
        return look

    def spam(self, holder: str, rows: int, *, per_tx: int = 50) -> None:
        """Zero-value poisoning spam through a multicall contract: ``rows`` listing rows for ``holder``."""
        contract = self.addr()
        looks = [self.lookalike(holder) for _ in range(5)]
        poisoner = self.source()
        done = 0
        while done < rows:
            n = min(per_tx, rows - done)
            parts = [(looks[(done + i) % len(looks)], 0) for i in range(n)]
            keys = self.multi_transfer(holder, contract, parts, owner=poisoner)
            for k in keys:
                self.trap(k[0], "zero_value_poisoning", k[1])
            done += n

    def failed(self, holder: str, to: str, value: int, status: str = "OUT_OF_ENERGY") -> str:
        txid, _ = self.usdt_transfer(holder, to, value, status=status)
        self.trap(txid, "failed_transaction")
        return txid

    # ------------------------------------------------------------------ outages
    def outage(self, role: str, endpoint: str, target: str, *, status: int = 503, page: int | None = None) -> None:
        self.outages.append({"role": role, "endpoint": endpoint, "target": target, "page": page, "status": status,
                             "mode": "http"})

    def hide(self, edge: tuple[str, int]) -> None:
        self.hidden.add(edge[0])

    # ------------------------------------------------------------------ finalize
    def _listing_down(self, addr: str) -> bool:
        return any(o["role"] == "trongrid_v1" and o["endpoint"] in ("trc20", "*") and o["target"] == addr
                   and o.get("page") is None for o in self.outages)

    def _listing_page_down(self, addr: str) -> int | None:
        pages = [o["page"] for o in self.outages if o["role"] == "trongrid_v1" and o["endpoint"] in ("trc20", "*")
                 and o["target"] == addr and o.get("page") is not None]
        return min(pages) if pages else None

    def _secondary_down(self, txid: str) -> bool:
        return any(o["role"] == "secondary_node" and o["endpoint"] in ("gettransactioninfobyid", "*")
                   and o["target"] in ("*", txid) for o in self.outages)

    def _lz_down(self, txid: str) -> bool:
        return any(o["role"] == "layerzero_scan" and o["target"] in ("*", txid) for o in self.outages)

    def _cut(self, world: World, term: _Terminal) -> tuple[int | None, str | None]:
        edges = term.path.edges
        for i, key in enumerate(edges):
            info = self.edge_info[key]
            frm = info["from"]
            if i >= self.max_depth:
                return i, "max_depth"
            if key[0] in self.hidden:
                return i, "data_gap"
            if i >= 1:
                if self._listing_down(frm):
                    return i, "source_unavailable"
                pg = self._listing_page_down(frm)
                if pg is not None and (world.page_of(frm, key[0]) or 0) >= pg:
                    return i, "incomplete_listing"
        if term.reason in NEEDS_LISTING:
            holder = term.path.holder
            if self._listing_down(holder):
                return len(edges), "source_unavailable"
            if self._listing_page_down(holder) is not None:
                return len(edges), "incomplete_listing"
        return None, None

    def finalize(self) -> tuple[World, dict[str, Any]]:
        for dep, ex in self.exchanges.items():
            if ex.pending:
                self.sweep(dep)
        last = max(t["ts_ms"] for t in self.txs)
        snapshot = last - last % 1000 + 7 * DAY_MS
        world = World(scenario_id=self.sid, snapshot_ms=snapshot, snapshot_block=block_of(snapshot), txs=self.txs,
                      opening=self.opening, hidden=self.hidden, outages=self.outages, lz=self.lz, labels=self.labels,
                      snapshot_ref={"ref_block_bytes": f"{(block_of(snapshot) - 19) & 0xFFFF:04x}",
                                    "ref_block_hash": self.rng.hex(8)})
        # edge status: expected > allowed > excluded
        rank = {"expected": 3, "allowed": 2, "source_unavailable": 1, "source_data_gap": 1}
        edge_status: dict[tuple[str, int], str] = {}
        edge_role: dict[tuple[str, int], str] = {}

        def mark(key: tuple[str, int], status: str, role: str) -> None:
            if rank[status] > rank.get(edge_status.get(key, ""), 0):
                edge_status[key] = status
                edge_role[key] = role

        routes: dict[tuple[tuple[str, ...], str], dict[str, Any]] = {}
        term_status: list[tuple[_Terminal, str, str | None]] = []  # (terminal, final status, final reason)
        for term in self.terminals:
            cut, why = self._cut(world, term)
            edges = term.path.edges
            role = "side_branch" if term.kind == "side_branch" else "main"
            reason = self._bridge_reason(term) if term.reason == "bridge" else term.reason
            if cut is None:
                for k in edges:
                    mark(k, "expected", role)
                routes.setdefault((tuple(k[0] for k in edges), term.path.holder),
                                  {"kind": term.kind, "txids": [k[0] for k in edges],
                                   "terminal": {"chain": "tron", "address": term.path.holder, "reason": reason}})
                term_status.append((term, "expected", reason))
                continue
            for k in edges[:cut]:
                mark(k, "expected", role)
            rest = "allowed" if why == "max_depth" else ("source_data_gap" if why == "data_gap" else "source_unavailable")
            for k in edges[cut:]:
                mark(k, rest, "beyond_depth" if why == "max_depth" else role)
            holder = self.edge_info[edges[cut - 1]]["to"] if cut >= 1 else self.victim
            if cut == len(edges):
                holder = term.path.holder
            routes.setdefault((tuple(k[0] for k in edges[:cut]), holder),
                              {"kind": term.kind, "txids": [k[0] for k in edges[:cut]],
                               "terminal": {"chain": "tron", "address": holder, "reason": why}})
            term_status.append((term, rest, reason))

        for key in self.uncertain_edges:
            if key not in edge_status:
                edge_status[key] = "allowed_uncertain"
                edge_role[key] = "commingled_outflow"
        for ex in self.exchanges.values():
            for key in ex.sweep_edges:
                if key not in edge_status:
                    edge_status[key] = "allowed"
                    edge_role[key] = "sweep"

        def transfer(key: tuple[str, int], *, taint: str = "traced", excluded: str | None = None) -> dict[str, Any]:
            info = self.edge_info[key]
            return {"chain": "tron", "txid": key[0], "event_index": key[1], "from": info["from"], "to": info["to"],
                    "amount": amt(info["value"]), "asset": "USDT-TRC20", "taint": taint,
                    "verification": "unverified" if self._secondary_down(key[0]) else "second_source_confirmed",
                    "role": edge_role.get(key), "excluded": excluded}

        order = {t["txid"]: i for i, t in enumerate(world.txs)}
        keys_sorted = sorted(edge_status, key=lambda k: (order[k[0]], k[1]))
        transfers, allowed_transfers = [], []
        for k in keys_sorted:
            st = edge_status[k]
            if st == "expected":
                transfers.append(transfer(k))
            elif st in ("source_unavailable", "source_data_gap"):
                transfers.append(transfer(k, excluded=st))
            elif st == "allowed":
                allowed_transfers.append(transfer(k))
            elif st == "allowed_uncertain":
                allowed_transfers.append(transfer(k, taint="uncertain"))

        # facts attached to terminals: exchange deposits, bridge exits, merges
        def fact_status(addr_or_tx: str, pred) -> str | None:
            sts = [st for term, st, _r in term_status if pred(term)]
            if not sts:
                return None
            best = max(sts, key=lambda s: rank.get(s, 0))
            return best

        exchange_deposits, allowed_ex = [], []
        for dep, ex in self.exchanges.items():
            st = fact_status(dep, lambda t, d=dep: t.reason == "exchange_deposit" and t.path.holder == d)
            fact = {"chain": "tron", "deposit_address": dep, "exchange": ex.exchange, "hot_wallet": ex.hot_wallet,
                    "sweep_txids": list(ex.sweep_txids), "excluded": None}
            if dep in self.uncertain_exchanges or st == "allowed":
                allowed_ex.append(fact)
            elif st == "expected":
                exchange_deposits.append(fact)
            elif st is not None:
                exchange_deposits.append(dict(fact, excluded=st))

        bridge_exits, allowed_br = [], []
        for txid, br in self.bridges.items():
            st = fact_status(txid, lambda t, x=txid: t.reason == "bridge" and t.path.edges[-1][0] == x)
            fact = self._bridge_fact(txid, br)
            if st == "expected":
                bridge_exits.append(fact)
            elif st == "allowed":
                allowed_br.append(fact)
            elif st is not None:
                bridge_exits.append(dict(fact, excluded=st))

        merges, allowed_m = [], []
        for hub, m in self.merges.items():
            if not m["traced"]:
                continue  # foreign funds only (a trap, not a merge)
            sts = [(term.path.edges[-1][0], st) for term, st, _r in term_status
                   if term.reason == "commingled" and term.path.holder == hub]
            exp_in = sorted({tx for tx, st in sts if st == "expected"})
            fact = {"chain": "tron", "address": hub, "attribution": "uncertain", "traced_inflow_txids": exp_in,
                    "foreign_inflow_txids": list(m["foreign"]), "excluded": None}
            if exp_in:
                merges.append(fact)
            elif any(st == "allowed" for _tx, st in sts):
                allowed_m.append(dict(fact, traced_inflow_txids=sorted({tx for tx, _ in sts})))
            elif sts:
                merges.append(dict(fact, traced_inflow_txids=sorted({tx for tx, _ in sts}), excluded=sts[0][1]))

        # routes
        route_list = []
        for i, r in enumerate(sorted(routes.values(), key=lambda r: (len(r["txids"]), [order[t] for t in r["txids"]],
                                                                     r["terminal"]["address"])), 1):
            route_list.append({"route_id": f"r{i:02d}", "kind": r["kind"], "txids": r["txids"],
                               "terminal": r["terminal"], "excluded": None})
        boundaries = [{"route_id": r["route_id"], "address": r["terminal"]["address"], "reason": r["terminal"]["reason"],
                       "after_txid": r["txids"][-1]} for r in route_list
                      if r["terminal"]["reason"] in EVIDENCE_BOUNDARY_REASONS]

        limitations = self._limitations(route_list, transfers, bridge_exits)
        expected = {
            "schema": "ledgerhunt.scenario-result/1",
            "scenario_id": self.sid,
            "result_type": "expected",
            "transfers": transfers,
            "routes": route_list,
            "exchange_deposits": exchange_deposits,
            "bridge_exits": bridge_exits,
            "merges": merges,
            "limitations": limitations,
            "allowed": {"transfers": allowed_transfers, "exchange_deposits": allowed_ex, "bridge_exits": allowed_br,
                        "merges": allowed_m},
            "traps": _dedupe_traps(self.traps),
            "outages": list(self.outages) + ([{"role": "trongrid_v1", "endpoint": "index_gap", "target": t,
                                               "page": None, "status": 200, "mode": "hidden"}
                                              for t in sorted(self.hidden)]),
            "evidence_boundaries": boundaries,
            "notes": list(self.notes),
        }
        return world, expected

    def _bridge_reason(self, term: _Terminal) -> str:
        txid = term.path.edges[-1][0]
        br = self.bridges[txid]
        if br["protocol"] != "usdt0_oft" or br["dst_eid"] not in SUPPORTED_BRIDGES[0]["dst_eids"]:
            return "bridge_exit_unsupported"
        msg = self.lz.get(txid)
        if msg is None or not msg["indexed"] or self._lz_down(txid):
            return "bridge_destination_unconfirmed"
        return "bridge_exit_supported"

    def _bridge_fact(self, txid: str, br: dict[str, Any]) -> dict[str, Any]:
        info = self.edge_info[(txid, 0)]
        msg = self.lz.get(txid)
        fact: dict[str, Any] = {"chain": "tron", "txid": txid, "protocol": br["protocol"], "dst_eid": br["dst_eid"],
                                "dst_chain": EID_CHAINS.get(br["dst_eid"]) if br["dst_eid"] else None,
                                "supported": br["protocol"] == "usdt0_oft" and br["dst_eid"] in SUPPORTED_BRIDGES[0]["dst_eids"],
                                "sender": br["sender"], "recipient": None, "amount_sent": amt(info["value"]),
                                "amount_received": None, "guid": None, "dst_txid": None, "excluded": None}
        if msg is not None:
            fact.update({"recipient": msg["recipient"], "amount_received": amt(msg["amount_received"]),
                         "guid": "0x" + msg["guid"]})
            if msg["indexed"] and not self._lz_down(txid):
                fact["dst_txid"] = msg["dst_txid"]
        return fact

    def _limitations(self, routes: list[dict[str, Any]], transfers: list[dict[str, Any]],
                     bridge_exits: list[dict[str, Any]]) -> list[dict[str, Any]]:
        visited = {r["terminal"]["address"] for r in routes}
        visited |= {t["from"] for t in transfers if not t["excluded"]}
        out: dict[tuple[str, str], dict[str, Any]] = {}

        def add(role: str, target: str, kind: str) -> None:
            out.setdefault((role, target), {"source_role": role, "target": target, "limitation": kind, "excluded": None})

        for o in self.outages:
            if o["role"] == "trongrid_v1" and o["endpoint"] in ("trc20", "*") and o["target"] in visited:
                add("tron_index", o["target"], "unavailable" if o.get("page") is None else "incomplete_listing")
            elif o["role"] == "trongrid_v1" and o["endpoint"] == "events":
                add("tron_events", o["target"], "unavailable")
            elif o["role"] == "secondary_node":
                add("tron_receipts_secondary", o["target"], "unavailable")
            elif o["role"] == "layerzero_scan" and (o["target"] == "*" or o["target"] in {b["txid"] for b in bridge_exits}):
                add("bridge_api", o["target"], "unavailable")
        for r in routes:
            if r["terminal"]["reason"] == "data_gap":
                add("tron_index", r["terminal"]["address"], "data_gap")
        return [out[k] for k in sorted(out)]


USDT_TRC20_HEX40 = "a614f803b6fd780986a42c78ec9c7f77e6ded13c"


def _iso(ts_s: int) -> str:
    from datetime import datetime, timezone

    return datetime.fromtimestamp(ts_s, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")


def _slug(name: str) -> str:
    return "".join(c.lower() if c.isalnum() else "_" for c in name).strip("_")


def _dedupe_traps(traps: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    seen, out = set(), []
    for t in traps:
        k = (t["txid"], t["event_index"], t["reason"])
        if k not in seen:
            seen.add(k)
            out.append(t)
    return out
