"""Step 1: re-fetch raw responses for every identifier of the case-001 fixture.

Every request goes through RecordingClient into the fixture store (tests/fixtures/case-001/raw/
http-store), so the fact check and the reference run can be replayed offline. ``inventory``
lists each request (what, provider, endpoint, status, body sha256, empty answer or not).
Failures are recorded, never fatal: one unavailable source must not stop the others.
"""

from __future__ import annotations

import re
import time
from dataclasses import dataclass, field
from typing import Any, Callable

from ..core.config import has_secret
from ..core.evm import TRANSFER_TOPIC, USDT_ERC20
from ..core.http import ReplayMiss, RecordingClient
from ..core.redact import redact
from ..core.tron import USDT_TRC20, is_valid_address
from ..sources import (
    BlockscoutClient,
    EthRpcClient,
    Fetched,
    LayerZeroScanClient,
    NearIntentsClient,
    Paged,
    TronGridClient,
    TronNodeClient,
)
from ..sources.case001_etherscan import EtherscanNameTag
from ..sources.case001_tronscan import TronScanTagLookup
from .chain import parse_ts
from .fetch import RECEIPT_NULL_RETRY_S

_TRON_ADDR = re.compile(r"\bT[1-9A-HJ-NP-Za-km-z]{33}\b")
_EVM_ADDR = re.compile(r"\b0x[0-9a-fA-F]{40}\b")
_TXID = re.compile(r"\b[0-9a-f]{64}\b")

DAY_MS = 86_400_000


@dataclass
class Inventory:
    """What the fixture names: TRON txids/addresses, Ethereum txs/addresses, bridge identifiers."""

    tron_txids: list[str] = field(default_factory=list)
    tron_addresses: list[str] = field(default_factory=list)
    eth_txs: list[str] = field(default_factory=list)
    eth_addresses: list[str] = field(default_factory=list)
    lz_guids: list[str] = field(default_factory=list)
    lz_src_txs: list[str] = field(default_factory=list)
    oneclick_deposits: list[str] = field(default_factory=list)
    tronscan_tag_lookups: list[str] = field(default_factory=list)


def _add(lst: list[str], value: str) -> None:
    if value and value not in lst:
        lst.append(value)


def build_inventory(fx: dict[str, Any]) -> Inventory:
    inv = Inventory()
    _add(inv.tron_addresses, fx["victim"]["address"])
    for t in fx["transactions"]:
        if t["chain"] == "tron":
            _add(inv.tron_txids, t["txid"])
            for a in (t.get("from"), t.get("to")):
                if a and is_valid_address(a):
                    _add(inv.tron_addresses, a)
        else:
            _add(inv.eth_txs, t["txid"])
            for a in (t.get("from"), t.get("to")):
                if a and a.startswith("0x"):
                    _add(inv.eth_addresses, a)
        lz = t.get("layerzero")
        if lz:
            _add(inv.lz_guids, lz["guid"])
            _add(inv.lz_src_txs, t["txid"])
        ni = t.get("near_intents")
        if ni:
            _add(inv.oneclick_deposits, t["from"])
            _add(inv.tron_txids, ni["destination_tx"])
            _add(inv.tron_addresses, ni["recipient_tron"])
        rg = t.get("rango")
        if rg:
            _add(inv.eth_addresses, rg["affiliate"])
            _add(inv.eth_addresses, rg["forwarded_to"])
    for a in fx["addresses"]:
        if a["chain"] == "tron":
            _add(inv.tron_addresses, a["address"])
        else:
            _add(inv.eth_addresses, a["address"])
        if "TronScan" in (a.get("role") or "") or "TronScan" in (a.get("confidence") or ""):
            _add(inv.tronscan_tag_lookups, a["address"])
    for link in fx["links"]:
        text = _json_text(link)
        for txid in _TXID.findall(text):
            _add(inv.tron_txids, txid)
        for a in _TRON_ADDR.findall(text):
            if is_valid_address(a):
                _add(inv.tron_addresses, a)
        for a in _EVM_ADDR.findall(text):
            _add(inv.eth_addresses, a)
    return inv


def _json_text(obj: Any) -> str:
    import json

    return json.dumps(obj, ensure_ascii=False)


@dataclass
class RawBundle:
    """Parsed raw data by identifier (what the fact check reads), plus the request inventory."""

    tron_tx: dict[str, dict[str, Any]] = field(default_factory=dict)
    tron_account: dict[str, dict[str, Any]] = field(default_factory=dict)
    tron_contract: dict[str, Any] = field(default_factory=dict)
    usdt_balance: dict[str, dict[str, Any]] = field(default_factory=dict)
    trc20: dict[str, dict[str, Any]] = field(default_factory=dict)
    account_txs: dict[str, dict[str, Any]] = field(default_factory=dict)
    eth_tx: dict[str, dict[str, Any]] = field(default_factory=dict)
    eth_address: dict[str, Any] = field(default_factory=dict)
    eth_address_transfers: dict[str, dict[str, Any]] = field(default_factory=dict)
    lz: dict[str, Any] = field(default_factory=dict)
    oneclick: dict[str, Any] = field(default_factory=dict)
    tronscan: dict[str, Any] = field(default_factory=dict)
    etherscan_tags: dict[str, Any] = field(default_factory=dict)
    probes: dict[str, Any] = field(default_factory=dict)
    requests: list[dict[str, Any]] = field(default_factory=list)
    replay_misses: int = 0
    keys_present: dict[str, bool] = field(default_factory=dict)

    def ref(self, kind: str, ident: str) -> list[str]:
        """Body sha256 values recorded for (kind, ident)."""
        return [r["body_sha256"] for r in self.requests if r["kind"] == kind and r["id"] == ident and r["body_sha256"]]


class Refetcher:
    """Runs step 1 with one RecordingClient whose store is the fixture store."""

    def __init__(self, http: RecordingClient, *, tronscan_store: str | None = None, log: Callable[[str], None] = print):
        self.http = http
        self.tg = TronGridClient(http)
        self.pn = TronNodeClient(http)
        self.paid = TronNodeClient.from_env("TRON_RPC_URL", http) if has_secret("TRON_RPC_URL") else None
        self.bs = BlockscoutClient(http)
        self.eth = EthRpcClient(http)
        self.lz = LayerZeroScanClient(http)
        self.ni = NearIntentsClient(http)
        self.ts = TronScanTagLookup(http, store_dir=tronscan_store)
        self.es = EtherscanNameTag(http)
        self.log = log
        self.b = RawBundle(keys_present={"TRONGRID_API_KEY": self.tg.has_key,
                                         "TRON_RPC_URL": self.paid is not None,
                                         "BLOCKSCOUT_API_KEY": has_secret("BLOCKSCOUT_API_KEY"),
                                         "NEAR_INTENTS_JWT": has_secret("NEAR_INTENTS_JWT"),
                                         "TRONSCAN_API_KEY": has_secret("TRONSCAN_API_KEY"),
                                         "ETHERSCAN_API_KEY": self.es.has_key})

    # -- recording helper ------------------------------------------------------
    def _get(self, kind: str, ident: str, provider: str, endpoint: str,
             fn: Callable[[], Fetched | Paged]) -> Fetched | Paged | None:
        try:
            res = fn()
        except ReplayMiss as exc:
            self.b.replay_misses += 1
            self.b.requests.append({"kind": kind, "id": ident, "provider": provider, "endpoint": endpoint,
                                    "status": None, "body_sha256": None, "error": f"ReplayMiss: {redact(exc)[:200]}"})
            return None
        except Exception as exc:  # noqa: BLE001 - recorded, step continues
            f = getattr(exc, "fetched", None)
            self.b.requests.append({"kind": kind, "id": ident, "provider": provider, "endpoint": endpoint,
                                    "status": f.status if f else None,
                                    "body_sha256": f.ref.body_sha256 if f and f.ref else None,
                                    "error": f"{type(exc).__name__}: {redact(exc)[:300]}"})
            self.log(f"    ! {kind} {ident}: {type(exc).__name__}")
            return f
        pages = res.pages if isinstance(res, Paged) else [res]
        for i, p in enumerate(pages):
            data = p.data
            empty = data in ({}, None, []) or (isinstance(data, dict) and "data" in data and data["data"] == [])
            self.b.requests.append({"kind": kind, "id": ident, "page": i, "provider": provider, "endpoint": endpoint,
                                    "status": p.status, "body_sha256": p.ref.body_sha256 if p.ref else None,
                                    "latency_ms": p.latency_ms, "from_replay": p.from_replay, "empty": empty,
                                    "error": None})
        return res

    # -- plan ---------------------------------------------------------------------
    def run(self, fx: dict[str, Any], inv: Inventory) -> RawBundle:
        b = self.b
        self.log(f"  TRON transactions: {len(inv.tron_txids)} (TronGrid x3 + PublicNode)")
        for txid in inv.tron_txids:
            rec: dict[str, Any] = {}
            f = self._get("tron_tx", txid, "trongrid", "wallet/gettransactionbyid",
                          lambda: self.tg.get_transaction_by_id(txid))
            rec["tx"] = f.data if f else None
            f = self._get("tron_info", txid, "trongrid", "walletsolidity/gettransactioninfobyid",
                          lambda: self.tg.get_transaction_info_by_id(txid))
            rec["info"] = f.data if f else None
            f = self._get("tron_events", txid, "trongrid", "v1/transactions/{hash}/events",
                          lambda: self.tg.transaction_events(txid))
            rec["events"] = f.data if f else None
            f = self._get("tron_info_publicnode", txid, "tron_publicnode", "walletsolidity/gettransactioninfobyid",
                          lambda: self.pn.get_transaction_info_by_id(txid))
            rec["pn_info"] = f.data if f else None
            if self.paid is not None:
                f = self._get("tron_info_paid", txid, "tron_rpc_paid", "walletsolidity/gettransactioninfobyid",
                              lambda: self.paid.get_transaction_info_by_id(txid))
                rec["paid_info"] = f.data if f else None
            b.tron_tx[txid] = rec

        self.log(f"  TRON accounts: {len(inv.tron_addresses)} (TronGrid + PublicNode getaccount)")
        for a in inv.tron_addresses:
            f1 = self._get("tron_account", a, "trongrid", "wallet/getaccount", lambda: self.tg.get_account(a))
            f2 = self._get("tron_account_publicnode", a, "tron_publicnode", "wallet/getaccount",
                           lambda: self.pn.get_account(a))
            b.tron_account[a] = {"tg": f1.data if f1 else None, "pn": f2.data if f2 else None}

        # contract metadata of TRON contracts named in the fixture roles
        for a in [x["address"] for x in fx["addresses"] if x["chain"] == "tron" and "contract" in x["role"].lower()]:
            f = self._get("tron_contract", a, "trongrid", "wallet/getcontract",
                          lambda: self.tg.call("wallet/getcontract", {"value": a, "visible": True}))
            b.tron_contract[a] = f.data if f else None

        # USDT balances now (addresses with a balance claim), two sources
        bal_addrs = [x["address"] for x in fx["addresses"] if x["chain"] == "tron" and "balance_usdt" in x]
        bal_addrs = [fx["victim"]["address"]] + [a for a in bal_addrs if a != fx["victim"]["address"]]
        self.log(f"  USDT balanceOf now: {len(bal_addrs)} addresses x 2 sources")
        for a in bal_addrs:
            out: dict[str, Any] = {}
            for name, client, prov in (("tg", self.tg, "trongrid"), ("pn", self.pn, "tron_publicnode")):
                f = self._get(f"usdt_balance_{name}", a, prov, "wallet/triggerconstantcontract",
                              lambda: client.trc20_balance_of(a)[1])
                res = (f.data or {}).get("constant_result") if f else None
                out[name] = int(res[0], 16) if res and res[0] else None
            b.usdt_balance[a] = out

        self._trc20_windows(fx)
        self._account_windows(fx)
        self._ethereum(fx, inv)
        self._bridges(inv)
        self._tronscan(inv)
        return b

    def _trc20(self, key: str, address: str, min_ms: int | None, max_ms: int | None, *, limit: int = 200,
               max_pages: int = 5) -> None:
        p = self._get("trc20", key, "trongrid", "v1/accounts/{address}/transactions/trc20",
                      lambda: self.tg.trc20_transfers(address, contract_address=USDT_TRC20, min_timestamp=min_ms,
                                                      max_timestamp=max_ms, limit=limit, max_pages=max_pages))
        self.b.trc20[key] = {"address": address, "min_ms": min_ms, "max_ms": max_ms,
                             "rows": p.rows if isinstance(p, Paged) else [],
                             "complete": p.complete if isinstance(p, Paged) else False}

    def _trc20_windows(self, fx: dict[str, Any]) -> None:
        tx = {t["step"]: t for t in fx["transactions"]}
        hub_in = parse_ts(tx[17]["timestamp_utc"])
        self.log("  TRC20 transfer windows (TronGrid v1)")
        self._trc20("victim:all", fx["victim"]["address"], None, None)
        self._trc20("thief1:all", tx[6]["to"], None, None)
        self._trc20("hop2:all", tx[8]["to"], None, None)
        self._trc20("bridge_wallet:2026-08-26..2026-09-22", tx[9]["to"], parse_ts("2026-08-26 00:00:00"),
                    parse_ts("2026-09-22 00:00:00"))
        self._trc20("fee1pct:since-2026-09-21", tx[10]["to"], parse_ts("2026-09-21 00:00:00"), None, max_pages=3)
        self._trc20("hub:24h-after-arrival", tx[17]["to"], hub_in, hub_in + DAY_MS)
        for step in (18, 22):
            t = tx[step]
            ms = parse_ts(t["timestamp_utc"])
            self._trc20(f"deposit:{t['to']}:6h", t["to"], ms, ms + 6 * 3600 * 1000, limit=50, max_pages=1)
        for flow in fx["links"][1]["flows"] if len(fx["links"]) > 1 else []:
            for a in flow["path"][:-1]:
                self._trc20(f"reuse_flow:{a}", a, parse_ts("2026-08-25 00:00:00"), parse_ts("2026-09-02 00:00:00"),
                            limit=50, max_pages=1)

    def _acctx(self, key: str, address: str, **kw: Any) -> None:
        p = self._get("account_txs", key, "trongrid", "v1/accounts/{address}/transactions",
                      lambda: self.tg.account_transactions(address, **kw))
        self.b.account_txs[key] = {"address": address, "params": kw,
                                   "rows": p.rows if isinstance(p, Paged) else [],
                                   "complete": p.complete if isinstance(p, Paged) else False}

    def _account_windows(self, fx: dict[str, Any]) -> None:
        tx = {t["step"]: t for t in fx["transactions"]}
        theft_ms = parse_ts(fx["theft"]["timestamp_utc"])
        victim = fx["victim"]["address"]
        funder = fx["links"][0]["funder"]
        self.log("  native transaction windows (TronGrid v1)")
        self._acctx("victim:theft+-120s", victim, min_timestamp=theft_ms - 120_000, max_timestamp=theft_ms + 120_000,
                    limit=50, max_pages=1)
        self._acctx("victim:outgoing-history", victim, only_from=True, limit=200, max_pages=5)
        self._acctx("victim:earliest-inbound", victim, only_to=True, limit=50, max_pages=1)
        self._acctx("thief1:earliest-inbound", tx[6]["to"], only_to=True, limit=50, max_pages=1)
        self._acctx("funder:earliest-inbound", funder, only_to=True, limit=50, max_pages=1)
        self._acctx("funder:earliest-outgoing", funder, only_from=True, limit=200, max_pages=1)
        for f in fx["links"][0]["funded"]:
            self._acctx(f"funded:{f['addr']}:earliest-inbound", f["addr"], only_to=True, limit=50, max_pages=1)
        up = [a for a in _TRON_ADDR.findall(_json_text(fx["links"][0].get("funder_upstream") or {}))]
        for a in dict.fromkeys(up):
            self._acctx(f"upstream:{a}:earliest-inbound", a, only_to=True, limit=50, max_pages=1)

    def _ethereum(self, fx: dict[str, Any], inv: Inventory) -> None:
        self.log(f"  Ethereum: {len(inv.eth_txs)} txs (Blockscout x3 + public RPC receipt), "
                 f"{len(inv.eth_addresses)} addresses")
        for h in inv.eth_txs:
            rec: dict[str, Any] = {}
            f = self._get("eth_tx", h, "blockscout_eth", "api/v2/transactions/{hash}", lambda: self.bs.transaction(h))
            rec["tx"] = f.data if f else None
            p = self._get("eth_token_transfers", h, "blockscout_eth", "api/v2/transactions/{hash}/token-transfers",
                          lambda: self.bs.transaction_token_transfers(h, max_pages=3))
            rec["token_transfers"] = p.rows if isinstance(p, Paged) else []
            p = self._get("eth_logs", h, "blockscout_eth", "api/v2/transactions/{hash}/logs",
                          lambda: self.bs.transaction_logs(h, max_pages=3))
            rec["logs"] = p.rows if isinstance(p, Paged) else []
            f = self._get("eth_receipt", h, "eth_publicnode", "jsonrpc/eth_getTransactionReceipt",
                          lambda: self.eth.get_transaction_receipt(h))
            nulls = 0
            if f is not None and f.data is None and not f.from_replay:
                # the keyless public RPC is a load-balanced pool: a known tx can come back as result=null
                nulls = 1
                time.sleep(RECEIPT_NULL_RETRY_S)
                f = self._get("eth_receipt_retry", h, "eth_publicnode", "jsonrpc/eth_getTransactionReceipt",
                              lambda: self.eth.get_transaction_receipt(h))
                nulls += 1 if f is not None and f.data is None else 0
            rec["receipt"] = f.data if f else None
            rec["receipt_status"] = f.status if f else None
            rec["receipt_null_results_live"] = nulls
            self.b.eth_tx[h] = rec
        for a in inv.eth_addresses:
            f = self._get("eth_address", a, "blockscout_eth", "api/v2/addresses/{address}", lambda: self.bs.address(a))
            self.b.eth_address[a] = f.data if f else None
        # explorer-tag claims: Etherscan name tag (needs ETHERSCAN_API_KEY; documented as an API Pro endpoint)
        tagged = [x["address"] for x in fx["addresses"] if x["chain"] == "ethereum"
                  and "explorer tag" in (x.get("confidence") or "")]
        for a in tagged:
            if not self.es.has_key:
                self.b.etherscan_tags[a] = {"status": None, "data": None, "note": "not measured: no ETHERSCAN_API_KEY"}
                continue
            f = self._get("etherscan_nametag", a, "etherscan", "v2/api?module=nametag&action=getaddresstag",
                          lambda: self.es.address_tag(a))
            self.b.etherscan_tags[a] = {"status": f.status if f else None, "data": f.data if f else None}
        transit = next(t["to"] for t in fx["transactions"] if t.get("kind") == "bridge_in_USDT0")
        deposit = next(t["from"] for t in fx["transactions"] if t.get("near_intents"))
        for a in (transit, deposit):
            p = self._get("eth_address_transfers", a, "blockscout_eth", "api/v2/addresses/{address}/token-transfers",
                          lambda: self.bs.address_token_transfers(a, type="ERC-20", max_pages=5))
            self.b.eth_address_transfers[a] = {"rows": p.rows if isinstance(p, Paged) else [],
                                               "complete": p.complete if isinstance(p, Paged) else False}
        # one probe: does the keyless public RPC serve eth_getLogs for a 3-week-old block range?
        bridge_in = next(t for t in fx["transactions"] if t.get("kind") == "bridge_in_USDT0")
        blk = int(bridge_in["block"])
        topic_from = "0x" + transit[2:].lower().rjust(64, "0")
        f = self._get("probe_eth_getLogs", f"{blk}-{blk + 1800}", "eth_publicnode", "jsonrpc/eth_getLogs",
                      lambda: self.eth.get_logs(from_block=blk, to_block=blk + 1800, address=USDT_ERC20,
                                                topics=[TRANSFER_TOPIC, topic_from]))
        last = self.b.requests[-1]
        self.b.probes["eth_getLogs_publicnode"] = {"range": [blk, blk + 1800], "status": last.get("status"),
                                                   "error": last.get("error"),
                                                   "logs": len(f.data) if f and isinstance(f.data, list) else None}

    def _bridges(self, inv: Inventory) -> None:
        self.log("  bridge APIs: LayerZero Scan, NEAR Intents 1Click")
        for h in inv.lz_src_txs:
            f = self._get("lz_by_tx", h, "layerzero_scan", "v1/messages/tx/{hash}", lambda: self.lz.messages_by_tx(h))
            self.b.lz[f"tx:{h}"] = f.data if f else None
        for g in inv.lz_guids:
            f = self._get("lz_by_guid", g, "layerzero_scan", "v1/messages/guid/{hash}",
                          lambda: self.lz.message_by_guid(g))
            self.b.lz[f"guid:{g}"] = f.data if f else None
        for d in inv.oneclick_deposits:
            f = self._get("oneclick_status", d, "near_intents_1click", "v0/status", lambda: self.ni.status(d))
            self.b.oneclick[d] = {"status": f.status if f else None, "data": f.data if f else None}

    def _tronscan(self, inv: Inventory) -> None:
        for a in inv.tronscan_tag_lookups[:1]:  # exactly one lookup, development verification only
            self.log(f"  TronScan account lookup (once, pending written consent): {a}")
            f = self._get("tronscan_account", a, "tronscan_pending_consent", "api/accountv2",
                          lambda: self.ts.account(a))
            self.b.tronscan[a] = {"status": f.status if f else None, "data": f.data if f else None,
                                  "from_cache_or_replay": f.from_replay if f else None}
