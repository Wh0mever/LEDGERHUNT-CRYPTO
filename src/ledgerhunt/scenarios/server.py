"""ScenarioServer: answers HTTP requests from a synthetic World in the real sources' raw formats.

Two uses:
1. The generator records each scenario's ``http-store`` by calling the real foundation
   clients (TronGridClient, TronNodeClient, LayerZeroScanClient) through a RecordingClient
   whose transport is this server. The store therefore contains exactly the requests and
   bodies the clients produce, and replays with ``RecordingClient(mode="replay")``.
2. A tracer can run against the server directly (``ScenarioServer(world).transport()``),
   with any query parameters, page sizes or providers, without the recorded store.

Served: TronGrid v1 (``/v1/accounts/{a}/transactions/trc20``, ``/v1/accounts/{a}/transactions``,
``/v1/transactions/{txid}/events``, ``/v1/contracts/{a}/events``) on api.trongrid.io;
java-tron ``/wallet*`` and ``/walletsolidity*`` (gettransactionbyid, gettransactioninfobyid,
triggerconstantcontract balanceOf) on any host; LayerZero Scan ``/v1/messages/tx|guid``
on scan.layerzero-api.com. Anything else answers 501 with a synthetic text body.

Assumptions (not sampled live): TronGrid default ``limit`` 20 and default order
``block_timestamp,desc``; an empty event list for transactions missing from the index.

Designed source failures come from ``world.outages`` rules::

    {"role": "trongrid_v1"|"trongrid_node"|"secondary_node"|"layerzero_scan",
     "endpoint": "trc20"|"account_transactions"|"events"|"contract_events"|"gettransactionbyid"|
                 "gettransactioninfobyid"|"triggerconstantcontract"|"messages_tx"|"messages_guid"|"*",
     "target": "<address|txid|*>", "page": <int>|null, "status": 503, "mode": "http"|"timeout"}

``page`` (1-based) fails that page and makes later pages unreachable. ``mode: timeout``
raises ``httpx.ReadTimeout`` (only meaningful against the live transport: a recorded store
cannot hold a response that never arrived).
"""

from __future__ import annotations

import email.utils
import hashlib
import json
from typing import Any, Callable
from urllib.parse import urlsplit

import base58
import httpx

from ..core.tron import USDT_TRC20, b58_to_hex, hex_to_b58, to_b58
from . import formats as F
from .world import World

TRONGRID_HOST = "api.trongrid.io"
LZ_HOST = "scan.layerzero-api.com"
MAX_LIMIT = 200
DEFAULT_LIMIT = 20  # assumption: TronGrid documented default
SERVER_HEADER = "ledgerhunt-synthetic"
FP_MAGIC = b"LHFP"


class ScenarioServer:
    def __init__(self, world: World) -> None:
        self.world = world
        self.requests = 0
        self._date = email.utils.formatdate(world.snapshot_ms / 1000, usegmt=True)

    # -- public ----------------------------------------------------------------
    def transport(self) -> httpx.MockTransport:
        return httpx.MockTransport(self)

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.requests += 1
        host = (request.url.host or "").lower()
        path = request.url.path.strip("/")
        try:
            if host == LZ_HOST:
                return self._layerzero(request, path)
            if host == TRONGRID_HOST and path.startswith("v1/"):
                return self._v1(request, path)
            if path.startswith(("wallet/", "walletsolidity/")):
                role = "trongrid_node" if host == TRONGRID_HOST else "secondary_node"
                return self._node(request, path, role)
        except _Fail as f:
            return f.response
        return self._error(501, "unsupported endpoint", "text")

    # -- helpers -----------------------------------------------------------------
    def _headers(self, kind: str) -> dict[str, str]:
        ctype = {"tg": "application/json;charset=utf-8", "node": "application/json", "lz": "application/json; charset=utf-8",
                 "text": "text/plain; charset=utf-8"}[kind]
        return {"content-type": ctype, "server": SERVER_HEADER, "date": self._date}

    def _ok(self, body: bytes, kind: str, status: int = 200) -> httpx.Response:
        return httpx.Response(status, content=body, headers=self._headers(kind))

    def _error(self, status: int, what: str, kind: str = "text") -> httpx.Response:
        return httpx.Response(status, content=F.synthetic_error(status, what), headers=self._headers("text"))

    def _check_outage(self, request: httpx.Request, role: str, endpoint: str, target: str | None,
                      page: int | None = None) -> None:
        for rule in self.world.outages:
            if rule["role"] != role or rule.get("endpoint", "*") not in ("*", endpoint):
                continue
            if rule.get("target", "*") not in ("*", target):
                continue
            rpage = rule.get("page")
            if rpage is not None and (page is None or page < rpage):
                continue
            if rule.get("mode") == "timeout":
                raise httpx.ReadTimeout("synthetic timeout (ledgerhunt scenario generator)", request=request)
            status = int(rule.get("status", 503))
            what = "rate limit" if status == 429 else "outage"
            raise _Fail(self._error(status, what))

    def _fingerprint(self, endpoint: str, target: str, offset: int) -> str:
        digest = hashlib.sha256(f"{self.world.scenario_id}|{endpoint}|{target}|{offset}".encode()).digest()
        return base58.b58encode(FP_MAGIC + offset.to_bytes(4, "big") + digest + digest[::-1]).decode()

    def _decode_fp(self, endpoint: str, target: str, fp: str | None) -> int:
        if not fp:
            return 0
        try:
            raw = base58.b58decode(fp)
        except ValueError:
            raise _Fail(self._error(400, "invalid fingerprint")) from None
        if not raw.startswith(FP_MAGIC) or len(raw) < 8:
            raise _Fail(self._error(400, "invalid fingerprint"))
        offset = int.from_bytes(raw[4:8], "big")
        if self._fingerprint(endpoint, target, offset) != fp:
            raise _Fail(self._error(400, "fingerprint does not match the query"))
        return offset

    @staticmethod
    def _limit(params: httpx.QueryParams) -> int:
        try:
            n = int(params.get("limit", DEFAULT_LIMIT))
        except ValueError:
            n = DEFAULT_LIMIT
        return max(1, min(MAX_LIMIT, n))

    def _paged(self, request: httpx.Request, *, rows: list[Any], ts_of: Callable[[Any], int], endpoint: str,
               target: str, url_path: str, role: str = "trongrid_v1") -> httpx.Response:
        p = request.url.params
        order = p.get("order_by", "block_timestamp,desc")
        rows = list(rows)
        if order.endswith(",desc"):
            rows.reverse()
        lo, hi = p.get("min_timestamp"), p.get("max_timestamp")
        if lo is not None:
            rows = [r for r in rows if ts_of(r) >= int(lo)]
        if hi is not None:
            rows = [r for r in rows if ts_of(r) <= int(hi)]
        limit = self._limit(p)
        offset = self._decode_fp(endpoint, target, p.get("fingerprint"))
        page = offset // limit + 1
        self._check_outage(request, role, endpoint, target, page)
        chunk = rows[offset:offset + limit]
        fp = next_url = None
        if offset + limit < len(rows):
            fp = self._fingerprint(endpoint, target, offset + limit)
            query = "&".join(f"{k}={v}" for k, v in sorted((k, v) for k, v in p.multi_items() if k != "fingerprint"))
            next_url = f"https://{TRONGRID_HOST}/{url_path}?{query}&fingerprint={fp}"
        return self._ok(F.v1_page(chunk, self.world.snapshot_ms, fingerprint=fp, next_url=next_url), "tg")

    # -- TronGrid v1 -------------------------------------------------------------------
    def _v1(self, request: httpx.Request, path: str) -> httpx.Response:
        parts = path.split("/")
        p = request.url.params
        w = self.world
        if len(parts) == 5 and parts[1] == "accounts" and parts[3:] == ["transactions", "trc20"]:
            addr = parts[2]
            contract = p.get("contract_address")
            pairs = w.trc20_rows(addr) if contract in (None, USDT_TRC20) else []
            if p.get("only_to") == "true":
                pairs = [(t, e) for t, e in pairs if F.v1_trc20_row(t, e)["to"] == addr]
            if p.get("only_from") == "true":
                pairs = [(t, e) for t, e in pairs if F.v1_trc20_row(t, e)["from"] == addr]
            rows = [F.v1_trc20_row(t, e) for t, e in pairs]
            return self._paged(request, rows=rows, ts_of=lambda r: r["block_timestamp"], endpoint="trc20",
                               target=addr, url_path=path)
        if len(parts) == 4 and parts[1] == "accounts" and parts[3] == "transactions":
            addr = parts[2]
            txs = w.account_txs(addr)
            if p.get("only_to") == "true":
                txs = [t for t in txs if t.get("to") == addr]
            if p.get("only_from") == "true":
                txs = [t for t in txs if t["owner"] == addr]
            rows = [F.v1_account_tx_row(t) for t in txs]
            return self._paged(request, rows=rows, ts_of=lambda r: r["block_timestamp"],
                               endpoint="account_transactions", target=addr, url_path=path)
        if len(parts) == 4 and parts[1] == "transactions" and parts[3] == "events":
            txid = parts[2].lower()
            self._check_outage(request, "trongrid_v1", "events", txid)
            t = w.tx(txid)
            rows = [F.v1_event_row(t, e) for e in w.events(txid)] if t else []
            return self._ok(F.v1_page(rows, w.snapshot_ms), "tg")
        if len(parts) == 4 and parts[1] == "contracts" and parts[3] == "events":
            contract = parts[2]
            rows = []
            for t in w.txs:
                if t["txid"] in w.hidden:
                    continue
                for e in sorted(w.events(t["txid"]), key=lambda e: e["index"]):
                    if e["contract"] != contract:
                        continue
                    if p.get("event_name") and e["name"] != p.get("event_name"):
                        continue
                    if p.get("block_number") and t["block"] != int(p.get("block_number")):
                        continue
                    rows.append(F.v1_event_row(t, e))
            lo, hi = p.get("min_block_timestamp"), p.get("max_block_timestamp")
            if lo is not None:
                rows = [r for r in rows if r["block_timestamp"] >= int(lo)]
            if hi is not None:
                rows = [r for r in rows if r["block_timestamp"] <= int(hi)]
            return self._paged(request, rows=rows, ts_of=lambda r: r["block_timestamp"], endpoint="contract_events",
                               target=contract, url_path=path)
        return self._error(501, "unsupported TronGrid v1 endpoint")

    # -- java-tron node ------------------------------------------------------------------
    def _node(self, request: httpx.Request, path: str, role: str) -> httpx.Response:
        try:
            payload = json.loads(request.content or b"{}")
        except ValueError:
            return self._error(400, "invalid JSON body")
        method = path.split("/", 1)[1]
        w = self.world
        if method in ("gettransactionbyid", "gettransactioninfobyid"):
            txid = str(payload.get("value", "")).lower()
            self._check_outage(request, role, method, txid)
            t = w.tx(txid)
            if t is None:
                return self._ok(F.node_empty(), "node")
            if method == "gettransactionbyid":
                return self._ok(F.node_transaction(t, visible=bool(payload.get("visible"))), "node")
            return self._ok(F.node_transaction_info(t), "node")
        if method == "triggerconstantcontract":
            owner = payload.get("owner_address", "")
            self._check_outage(request, role, method, owner if owner.startswith("T") else None)
            contract = payload.get("contract_address", "")
            if (to_b58(contract) if contract else "") != USDT_TRC20 or payload.get("function_selector") != "balanceOf(address)":
                return self._error(501, "only USDT balanceOf(address) is served")
            holder = hex_to_b58("41" + str(payload.get("parameter", ""))[-40:])
            owner_b58 = to_b58(owner) if owner else holder
            ref = w.snapshot_ref
            return self._ok(F.trigger_balance_of(owner_b58, max(0, w.balance(holder)),
                                                 ref_block_bytes=ref.get("ref_block_bytes", "0000"),
                                                 ref_block_hash=ref.get("ref_block_hash", "00" * 8),
                                                 expiration=w.snapshot_ms + 60_000, created_ms=w.snapshot_ms), "node")
        return self._error(501, f"unsupported node method {method}")

    # -- LayerZero Scan ----------------------------------------------------------------------
    def _layerzero(self, request: httpx.Request, path: str) -> httpx.Response:
        parts = path.split("/")
        if len(parts) == 4 and parts[:2] == ["v1", "messages"] and parts[2] in ("tx", "guid"):
            key = parts[3]
            endpoint = "messages_tx" if parts[2] == "tx" else "messages_guid"
            if parts[2] == "tx":
                msg = self.world.lz_by_tx(key) if key.lower().startswith("0x") else None
            else:
                msg = self.world.lz_by_guid(key)
            # an outage keyed by the source txid also blocks the guid lookup of the same message
            self._check_outage(request, "layerzero_scan", endpoint,
                               msg["src_txid"] if msg else key.lower().removeprefix("0x"))
            if msg is None or msg.get("indexed") is False:
                return self._ok(F.lz_not_found(key), "lz", status=404)
            return self._ok(F.lz_found(msg), "lz")
        return self._error(501, "unsupported LayerZero Scan endpoint")


class _Fail(Exception):
    def __init__(self, response: httpx.Response) -> None:
        self.response = response
        super().__init__(response.status_code)



