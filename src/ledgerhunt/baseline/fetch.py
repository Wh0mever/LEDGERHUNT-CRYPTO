"""Source access for the reference run: one RecordingClient, the source clients, a per-run memo
(the same request is never sent twice in one run), evidence references and per-step metrics.

Every raw response goes through ``RecordingClient`` (rate limits, retries, recording, replay).
``Evidence`` keeps, for each request the tracer relied on, the provider, endpoint, request
identity and the sha256 of the stored raw body, so every fact in the output points at bytes.
"""

from __future__ import annotations

import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any, Callable, Iterator

from ..core.http import RecordingClient
from .chain import parse_ts
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


RECEIPT_NULL_RETRY_S = 2.0


@dataclass
class StepMetrics:
    name: str
    wall_ms: float = 0.0
    requests: int = 0
    replayed: int = 0
    by_provider: dict[str, dict[str, float]] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "step": self.name,
            "wall_ms": round(self.wall_ms, 1),
            "requests": self.requests,
            "replayed": self.replayed,
            "by_provider": {k: {kk: round(vv, 1) if isinstance(vv, float) else vv for kk, vv in v.items()}
                            for k, v in sorted(self.by_provider.items())},
        }


class CaseSources:
    """Clients + memo + evidence + step metrics for one reference run."""

    def __init__(self, http: RecordingClient, *, trongrid_api_key: Any = ...) -> None:
        self.http = http
        self.tg = TronGridClient(http) if trongrid_api_key is ... else TronGridClient(http, api_key=trongrid_api_key)
        self.tron_node = TronNodeClient(http)  # PublicNode, keyless (second TRON source; not archival)
        self.bs = BlockscoutClient(http)
        self.eth = EthRpcClient(http)
        self.lz = LayerZeroScanClient(http)
        self.ni = NearIntentsClient(http)
        self._memo: dict[tuple, Any] = {}
        self.evidence: dict[str, dict[str, Any]] = {}
        self.steps: list[StepMetrics] = []
        self._current: StepMetrics | None = None

    # -- steps -------------------------------------------------------------
    @contextmanager
    def step(self, name: str) -> Iterator[StepMetrics]:
        sm = StepMetrics(name)
        start_idx = len(self.http.metrics)
        prev, self._current = self._current, sm
        t0 = time.perf_counter()
        try:
            yield sm
        finally:
            sm.wall_ms = (time.perf_counter() - t0) * 1000
            for row in self.http.metrics[start_idx:]:
                sm.requests += 1
                sm.replayed += 1 if row.get("from_replay") else 0
                p = sm.by_provider.setdefault(row["provider"], {"requests": 0, "latency_ms": 0.0,
                                                                "total_ms": 0.0, "rate_wait_ms": 0.0,
                                                                "retries": 0, "errors": 0})
                p["requests"] += 1
                p["latency_ms"] += float(row.get("latency_ms") or 0.0)
                p["total_ms"] += float(row.get("total_ms") or 0.0)
                p["rate_wait_ms"] += float(row.get("rate_wait_ms") or 0.0)
                p["retries"] += max(0, int(row.get("attempts") or 1) - 1)
                p["errors"] += 1 if row.get("error_class") else 0
            self.steps.append(sm)
            self._current = prev

    # -- memo + evidence ------------------------------------------------------
    def _remember(self, key: tuple, eid: str, provider: str, endpoint: str, request: str,
                  fn: Callable[[], Fetched | Paged]) -> Fetched | Paged:
        if key in self._memo:
            return self._memo[key]
        res = fn()
        self._memo[key] = res
        pages = res.pages if isinstance(res, Paged) else [res]
        self.evidence[eid] = {
            "provider": provider,
            "endpoint": endpoint,
            "request": request,
            "status": [p.status for p in pages],
            "pages": len(pages),
            "complete": res.complete if isinstance(res, Paged) else True,
            "body_sha256": [p.ref.body_sha256 if p.ref else None for p in pages],
            "store": pages[0].ref.store if pages and pages[0].ref else None,
        }
        return res

    # -- TRON -----------------------------------------------------------------
    def tron_tx(self, txid: str) -> tuple[dict, str]:
        eid = f"trongrid:gettransactionbyid:{txid}"
        f = self._remember(("tx", txid), eid, "trongrid", "wallet/gettransactionbyid", txid,
                           lambda: self.tg.get_transaction_by_id(txid))
        return (f.data or {}), eid

    def tron_info(self, txid: str) -> tuple[dict, str]:
        eid = f"trongrid:gettransactioninfobyid:{txid}"
        f = self._remember(("info", txid), eid, "trongrid", "walletsolidity/gettransactioninfobyid", txid,
                           lambda: self.tg.get_transaction_info_by_id(txid))
        return (f.data or {}), eid

    def tron_account(self, address: str) -> tuple[dict, str]:
        eid = f"trongrid:getaccount:{address}"
        f = self._remember(("acct", address), eid, "trongrid", "wallet/getaccount", address,
                           lambda: self.tg.get_account(address))
        return (f.data or {}), eid

    def trc20_window(self, address: str, token: str, min_ms: int, max_ms: int, *, limit: int,
                     max_pages: int) -> tuple[list[dict], bool, str]:
        eid = f"trongrid:trc20:{address}:{min_ms}-{max_ms}"
        p = self._remember(("trc20", address, token, min_ms, max_ms, limit, max_pages), eid, "trongrid",
                           "v1/accounts/{address}/transactions/trc20", f"{address} [{min_ms},{max_ms}] limit={limit}",
                           lambda: self.tg.trc20_transfers(address, contract_address=token, min_timestamp=min_ms,
                                                           max_timestamp=max_ms, limit=limit, max_pages=max_pages))
        return p.rows, p.complete, eid

    def account_txs(self, address: str, *, only_to: bool | None = None, only_from: bool | None = None,
                    min_ms: int | None = None, max_ms: int | None = None, limit: int = 50,
                    max_pages: int = 1) -> tuple[list[dict], bool, str]:
        tag = "to" if only_to else "from" if only_from else "all"
        eid = f"trongrid:transactions:{address}:{tag}:{min_ms}-{max_ms}:limit={limit}:pages={max_pages}"
        p = self._remember(("acctx", address, only_to, only_from, min_ms, max_ms, limit, max_pages), eid, "trongrid",
                           "v1/accounts/{address}/transactions", f"{address} {tag} [{min_ms},{max_ms}] limit={limit}",
                           lambda: self.tg.account_transactions(address, only_to=only_to, only_from=only_from,
                                                                min_timestamp=min_ms, max_timestamp=max_ms,
                                                                limit=limit, max_pages=max_pages))
        return p.rows, p.complete, eid

    def usdt_balance_now(self, address: str, token: str) -> tuple[int | None, str]:
        eid = f"trongrid:balanceOf:{address}"
        holder: dict[str, Any] = {}

        def call() -> Fetched:
            value, f = self.tg.trc20_balance_of(address, token)
            holder["value"] = value
            return f

        f = self._remember(("bal", address, token), eid, "trongrid", "wallet/triggerconstantcontract",
                           f"balanceOf({address})", call)
        results = (f.data or {}).get("constant_result") or []
        return (int(results[0], 16) if results and results[0] else None), eid

    # -- Ethereum ---------------------------------------------------------------
    def eth_tx(self, tx_hash: str) -> tuple[dict, str]:
        eid = f"blockscout:transaction:{tx_hash}"
        f = self._remember(("btx", tx_hash), eid, "blockscout_eth", "api/v2/transactions/{hash}", tx_hash,
                           lambda: self.bs.transaction(tx_hash))
        return (f.data or {}), eid

    def eth_logs(self, tx_hash: str) -> tuple[list[dict], str]:
        eid = f"blockscout:logs:{tx_hash}"
        p = self._remember(("blogs", tx_hash), eid, "blockscout_eth", "api/v2/transactions/{hash}/logs", tx_hash,
                           lambda: self.bs.transaction_logs(tx_hash, max_pages=5))
        return p.rows, eid

    def eth_receipt(self, tx_hash: str) -> tuple[dict, str]:
        """Receipt from the keyless public RPC. It is a load-balanced pool: a known tx can come back as
        ``result: null``; then one retry after RECEIPT_NULL_RETRY_S (live only). ``{}`` = no data."""
        eid = f"eth_publicnode:receipt:{tx_hash}"
        nulls = {"n": 0}

        def fetch() -> Fetched:
            f = self.eth.get_transaction_receipt(tx_hash)
            if f.data is None and not f.from_replay:
                nulls["n"] += 1
                time.sleep(RECEIPT_NULL_RETRY_S)
                f = self.eth.get_transaction_receipt(tx_hash)
                if f.data is None:
                    nulls["n"] += 1
            return f

        f = self._remember(("rcpt", tx_hash), eid, "eth_publicnode", "jsonrpc/eth_getTransactionReceipt", tx_hash,
                           fetch)
        if nulls["n"]:
            self.evidence[eid]["null_results_live"] = nulls["n"]
        if f.data is None:
            self.evidence[eid]["result_null"] = True
        return (f.data or {}), eid

    def eth_address_transfers(self, address: str, token: str, *, max_pages: int,
                              stop_before_ms: int | None = None) -> tuple[list[dict], bool, str]:
        """Blockscout address token transfers (newest first); pages until older than ``stop_before_ms``."""
        eid = f"blockscout:address_token_transfers:{address}:{token}"

        def fetch() -> Paged:
            out = Paged()
            cursor = None
            while True:
                page = self.bs.address_token_transfers_page(address, token=token, type="ERC-20", page_params=cursor)
                out.pages.append(page)
                items = list((page.data or {}).get("items") or [])
                out.rows.extend(items)
                cursor = (page.data or {}).get("next_page_params") or None
                oldest = items[-1]["timestamp"] if items else None
                if not cursor or (stop_before_ms is not None and oldest and parse_ts(oldest) < stop_before_ms):
                    out.complete = True
                    return out
                if len(out.pages) >= max_pages:
                    out.complete = False
                    return out

        p = self._remember(("btt", address, token, max_pages, stop_before_ms), eid, "blockscout_eth",
                           "api/v2/addresses/{address}/token-transfers", f"{address} token={token}", fetch)
        return p.rows, p.complete, eid

    # -- bridge APIs ---------------------------------------------------------------
    def lz_by_tx(self, tx_hash: str) -> tuple[Fetched, str]:
        eid = f"layerzero_scan:messages_by_tx:{tx_hash}"
        f = self._remember(("lz", tx_hash), eid, "layerzero_scan", "v1/messages/tx/{hash}", tx_hash,
                           lambda: self.lz.messages_by_tx(tx_hash))
        return f, eid

    def oneclick_status(self, deposit_address: str) -> tuple[Fetched, str]:
        eid = f"near_intents_1click:status:{deposit_address}"
        f = self._remember(("1click", deposit_address), eid, "near_intents_1click", "v0/status", deposit_address,
                           lambda: self.ni.status(deposit_address))
        return f, eid

    # -- output -------------------------------------------------------------------
    def timings(self) -> dict[str, Any]:
        by_provider: dict[str, dict[str, float]] = {}
        for sm in self.steps:
            for prov, v in sm.by_provider.items():
                agg = by_provider.setdefault(prov, {k: 0 for k in v})
                for k, val in v.items():
                    agg[k] += val
        return {
            "http_mode": self.http.mode,
            "steps": [s.to_dict() for s in self.steps],
            "total_requests": sum(s.requests for s in self.steps),
            "total_wall_ms": round(sum(s.wall_ms for s in self.steps), 1),
            "by_provider": {k: {kk: round(vv, 1) if isinstance(vv, float) else vv for kk, vv in v.items()}
                            for k, v in sorted(by_provider.items())},
        }
