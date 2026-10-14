"""Closed synthetic world of one scenario: every transaction, label, outage and bridge message.

``world.json`` is the generator's ground truth. A tracer under test must not read it: it
gets ``input.json`` and the recorded raw responses only. The scorer uses the world to
check whether an unexpected candidate fact is at least true on chain.

Amount-like integers (raw USDT units, sun) are written as decimal strings in world.json.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

from ..core.tron import USDT_TRC20

AMOUNT_KEYS = frozenset({"value", "amount", "call_value", "fee", "fees", "amountSentLD", "amountReceivedLD",
                         "energy_fee", "net_fee", "callValue", "amount_sent", "amount_received"})
WORLD_SCHEMA = "ledgerhunt.scenario-world/1"


def _amounts_to_str(obj: Any, key: str | None = None) -> Any:
    if isinstance(obj, dict):
        return {k: _amounts_to_str(v, k) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_amounts_to_str(v, key) for v in obj]
    if key in AMOUNT_KEYS and isinstance(obj, int) and not isinstance(obj, bool):
        return str(obj)
    return obj


def _amounts_to_int(obj: Any, key: str | None = None) -> Any:
    if isinstance(obj, dict):
        return {k: _amounts_to_int(v, k) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_amounts_to_int(v, key) for v in obj]
    if key in AMOUNT_KEYS and isinstance(obj, str) and obj.isdigit():
        return int(obj)
    return obj


class World:
    """In-memory world with the derived views the scenario server needs."""

    def __init__(self, *, scenario_id: str, snapshot_ms: int, snapshot_block: int, txs: list[dict[str, Any]],
                 opening: dict[str, int] | None = None, hidden: Iterable[str] = (), outages: list[dict] | None = None,
                 lz: dict[str, dict] | None = None, labels: list[dict] | None = None,
                 snapshot_ref: dict[str, Any] | None = None) -> None:
        self.scenario_id = scenario_id
        self.snapshot_ms = snapshot_ms
        self.snapshot_block = snapshot_block
        self.snapshot_ref = snapshot_ref or {}
        self.txs = sorted(txs, key=lambda t: (t["block"], t["ts_ms"], t["txid"]))
        self.opening = dict(opening or {})
        self.hidden = set(hidden)
        self.outages = list(outages or [])
        self.lz = dict(lz or {})
        self.labels = list(labels or [])
        self._by_id = {t["txid"]: t for t in self.txs}
        self._guid = {m["guid"]: m for m in self.lz.values()}

    # -- serialization ----------------------------------------------------
    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": WORLD_SCHEMA,
            "scenario_id": self.scenario_id,
            "snapshot_ms": self.snapshot_ms,
            "snapshot_block": self.snapshot_block,
            "snapshot_ref": self.snapshot_ref,
            "labels": self.labels,
            "opening_balances_raw": {k: str(v) for k, v in sorted(self.opening.items())},
            "hidden_from_index": sorted(self.hidden),
            "outages": self.outages,
            "layerzero_messages": [_amounts_to_str(self.lz[k]) for k in sorted(self.lz)],
            "transactions": [_amounts_to_str(t) for t in self.txs],
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "World":
        return cls(
            scenario_id=d["scenario_id"],
            snapshot_ms=d["snapshot_ms"],
            snapshot_block=d["snapshot_block"],
            snapshot_ref=d.get("snapshot_ref") or {},
            txs=[_amounts_to_int(t) for t in d["transactions"]],
            opening={k: int(v) for k, v in d.get("opening_balances_raw", {}).items()},
            hidden=d.get("hidden_from_index", []),
            outages=d.get("outages", []),
            lz={m["src_txid"]: _amounts_to_int(m) for m in d.get("layerzero_messages", [])},
            labels=d.get("labels", []),
        )

    @classmethod
    def load(cls, path: Path | str) -> "World":
        return cls.from_dict(json.loads(Path(path).read_text(encoding="utf-8")))

    # -- lookups ------------------------------------------------------------
    def tx(self, txid: str) -> dict[str, Any] | None:
        return self._by_id.get(txid.lower().removeprefix("0x"))

    def lz_by_tx(self, txid: str) -> dict[str, Any] | None:
        return self.lz.get(txid.lower().removeprefix("0x"))

    def lz_by_guid(self, guid: str) -> dict[str, Any] | None:
        return self._guid.get(guid.lower().removeprefix("0x"))

    def label(self, address: str) -> dict[str, Any] | None:
        for lab in self.labels:
            if lab["address"] == address:
                return lab
        return None

    @staticmethod
    def usdt_events(tx: dict[str, Any]) -> list[dict[str, Any]]:
        if tx["status"] != "SUCCESS":
            return []
        return [e for e in tx["events"] if e["contract"] == USDT_TRC20 and e["name"] in ("Transfer", "Approval")]

    def addresses(self) -> list[str]:
        """Every account that appears in the world (signers, TRX recipients, USDT parties), USDT contract excluded."""
        seen: set[str] = set()
        for t in self.txs:
            seen.add(t["owner"])
            if t.get("to"):
                seen.add(t["to"])
            for e in t["events"]:
                if e["contract"] == USDT_TRC20 and e["name"] == "Transfer":
                    seen.update((e["args"]["from"], e["args"]["to"]))
                elif e["contract"] == USDT_TRC20 and e["name"] == "Approval":
                    seen.update((e["args"]["owner"], e["args"]["spender"]))
        seen.discard(USDT_TRC20)
        return sorted(seen)

    def transfers(self, *, include_hidden: bool = True) -> list[dict[str, Any]]:
        """All successful USDT Transfer events: {txid, event_index, from, to, value, ts_ms, block, hidden}."""
        out = []
        for t in self.txs:
            hid = t["txid"] in self.hidden
            if hid and not include_hidden:
                continue
            for e in self.usdt_events(t):
                if e["name"] == "Transfer":
                    out.append({"txid": t["txid"], "event_index": e["index"], "from": e["args"]["from"],
                                "to": e["args"]["to"], "value": int(e["args"]["value"]), "ts_ms": t["ts_ms"],
                                "block": t["block"], "hidden": hid})
        return out

    # -- TronGrid v1 index views ------------------------------------------------
    def trc20_rows(self, address: str) -> list[tuple[dict[str, Any], dict[str, Any]]]:
        """(tx, event) pairs listed by /v1/accounts/{address}/transactions/trc20, ascending."""
        rows = []
        for t in self.txs:
            if t["txid"] in self.hidden:
                continue
            for e in self.usdt_events(t):
                a = e["args"]
                parties = (a["from"], a["to"]) if e["name"] == "Transfer" else (a["owner"], a["spender"])
                if address in parties:
                    rows.append((t, e))
        rows.sort(key=lambda p: (p[0]["ts_ms"], p[0]["txid"], p[1]["index"]))
        return rows

    def account_txs(self, address: str) -> list[dict[str, Any]]:
        """Transactions listed by /v1/accounts/{address}/transactions (assumption: signer or TRX recipient)."""
        rows = [t for t in self.txs if t["txid"] not in self.hidden
                and (t["owner"] == address or (t["ctype"] == "TransferContract" and t.get("to") == address))]
        rows.sort(key=lambda t: (t["ts_ms"], t["txid"]))
        return rows

    def events(self, txid: str) -> list[dict[str, Any]]:
        t = self.tx(txid)
        if t is None or t["txid"] in self.hidden or t["status"] != "SUCCESS":
            return []
        return sorted(t["events"], key=lambda e: -e["index"])

    def balance(self, address: str) -> int:
        bal = self.opening.get(address, 0)
        for tr in self.transfers(include_hidden=True):
            if tr["to"] == address:
                bal += tr["value"]
            if tr["from"] == address:
                bal -= tr["value"]
        return bal

    def page_of(self, address: str, txid: str, *, limit: int = 200) -> int | None:
        """1-based page (ascending order, given limit) of the first listing row with ``txid``."""
        for i, (t, _e) in enumerate(self.trc20_rows(address)):
            if t["txid"] == txid:
                return i // limit + 1
        return None
