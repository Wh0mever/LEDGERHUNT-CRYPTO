"""TronGrid client: v1 indexed REST API plus the java-tron node API on api.trongrid.io.

Shapes confirmed live 2026-10-14 (keyless) with case-001 identifiers:
- v1 list endpoints return {"data": [...], "success": true, "meta": {"at", "page_size",
  "fingerprint"?, "links": {"next"}?}}; the next page repeats the same query plus
  ``fingerprint=<meta.fingerprint>``; no fingerprint means the last page.
- TRC20 rows: transaction_id, token_info{symbol,address,decimals,name}, block_timestamp (ms),
  from, to, type ("Transfer"/"Approval"), value (raw integer string).
- Keyless TronGrid returned HTTP 429 on the second request about 1 s after the first;
  the client backs off (5 s penalty, shared across processes) and retries.

The key (TRONGRID_API_KEY) is sent only as the TRON-PRO-API-KEY header. The provider label
stays "trongrid" with or without a key so recordings replay without keys; metrics carry the
limiter bucket ('api.trongrid.io' or 'api.trongrid.io#key').
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ..core.config import get_secret
from ..core.http import RecordingClient
from ..core.ratelimit import TRONGRID_RPS_WITH_KEY
from ..core.tron import USDT_TRC20
from .base import Fetched, Paged, SourceError, paginate
from .tron_node import TronNodeClient

TRONGRID_BASE = "https://api.trongrid.io"
_ENV = object()


def _clean(params: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in params.items() if v is not None}


class TronGridClient(TronNodeClient):
    DEFAULT_BASE = TRONGRID_BASE
    DEFAULT_PROVIDER = "trongrid"

    def __init__(
        self,
        http: RecordingClient | None = None,
        *,
        api_key: Any = _ENV,
        base_url: str | None = None,
        provider: str | None = None,
        store_dir: Path | str | None = None,
        keyed_rps: float = TRONGRID_RPS_WITH_KEY,
    ) -> None:
        """api_key: default reads TRONGRID_API_KEY from config; pass None to force keyless."""
        key = get_secret("TRONGRID_API_KEY") if api_key is _ENV else api_key
        super().__init__(http, base_url=base_url, provider=provider, store_dir=store_dir, api_key=key or None)
        self.has_key = bool(key)
        host = self.base_url.split("://", 1)[-1].split("/", 1)[0].lower()
        if self.has_key:
            self._rate_key = f"{host}#key"
            self.http.set_rate(self._rate_key, keyed_rps)
        else:
            self._rate_key = host

    # -- helpers --------------------------------------------------------
    @staticmethod
    def _check(f: Fetched) -> Fetched:
        if isinstance(f.data, dict) and f.data.get("success") is False:
            raise SourceError(f"trongrid success=false: {str(f.data.get('error'))[:300]}", f)
        return f

    @staticmethod
    def _rows(f: Fetched) -> list[Any]:
        return list((f.data or {}).get("data") or [])

    @staticmethod
    def _next(f: Fetched) -> str | None:
        return ((f.data or {}).get("meta") or {}).get("fingerprint")

    # -- TRC20 transfers -------------------------------------------------
    def trc20_transfers_page(
        self,
        address: str,
        *,
        contract_address: str | None = USDT_TRC20,
        only_confirmed: bool | None = None,
        only_to: bool | None = None,
        only_from: bool | None = None,
        min_timestamp: int | None = None,
        max_timestamp: int | None = None,
        order_by: str | None = "block_timestamp,asc",
        limit: int = 200,
        fingerprint: str | None = None,
    ) -> Fetched:
        """GET /v1/accounts/{address}/transactions/trc20 (timestamps in ms, limit <= 200)."""
        params = _clean({
            "contract_address": contract_address,
            "only_confirmed": only_confirmed,
            "only_to": only_to,
            "only_from": only_from,
            "min_timestamp": min_timestamp,
            "max_timestamp": max_timestamp,
            "order_by": order_by,
            "limit": limit,
            "fingerprint": fingerprint,
        })
        return self._check(self._get(f"v1/accounts/{address}/transactions/trc20", params,
                                     endpoint="v1/accounts/{address}/transactions/trc20"))

    def trc20_transfers(self, address: str, *, max_pages: int | None = None, **kw: Any) -> Paged:
        """All pages of ``trc20_transfers_page`` (same keyword arguments)."""
        kw.pop("fingerprint", None)
        return paginate(lambda fp: self.trc20_transfers_page(address, fingerprint=fp, **kw),
                        self._next, self._rows, max_pages)

    # -- account transactions --------------------------------------------
    def account_transactions_page(
        self,
        address: str,
        *,
        only_confirmed: bool | None = None,
        only_to: bool | None = None,
        only_from: bool | None = None,
        min_timestamp: int | None = None,
        max_timestamp: int | None = None,
        order_by: str | None = "block_timestamp,asc",
        limit: int = 200,
        fingerprint: str | None = None,
        search_internal: bool | None = None,
    ) -> Fetched:
        """GET /v1/accounts/{address}/transactions (native txs incl. TRX transfers, delegations, contract calls)."""
        params = _clean({
            "only_confirmed": only_confirmed,
            "only_to": only_to,
            "only_from": only_from,
            "min_timestamp": min_timestamp,
            "max_timestamp": max_timestamp,
            "order_by": order_by,
            "limit": limit,
            "fingerprint": fingerprint,
            "search_internal": search_internal,
        })
        return self._check(self._get(f"v1/accounts/{address}/transactions", params,
                                     endpoint="v1/accounts/{address}/transactions"))

    def account_transactions(self, address: str, *, max_pages: int | None = None, **kw: Any) -> Paged:
        kw.pop("fingerprint", None)
        return paginate(lambda fp: self.account_transactions_page(address, fingerprint=fp, **kw),
                        self._next, self._rows, max_pages)

    # -- events -------------------------------------------------------------
    def transaction_events(self, txid: str, *, only_confirmed: bool | None = None) -> Fetched:
        """GET /v1/transactions/{txid}/events (decoded events with event_index, result{from,to,value})."""
        params = _clean({"only_confirmed": only_confirmed})
        return self._check(self._get(f"v1/transactions/{txid}/events", params or None,
                                     endpoint="v1/transactions/{hash}/events"))

    def contract_events_page(
        self,
        contract_address: str,
        *,
        event_name: str | None = None,
        block_number: int | None = None,
        min_block_timestamp: int | None = None,
        max_block_timestamp: int | None = None,
        order_by: str | None = None,
        only_confirmed: bool | None = None,
        limit: int = 200,
        fingerprint: str | None = None,
    ) -> Fetched:
        """GET /v1/contracts/{address}/events."""
        params = _clean({
            "event_name": event_name,
            "block_number": block_number,
            "min_block_timestamp": min_block_timestamp,
            "max_block_timestamp": max_block_timestamp,
            "order_by": order_by,
            "only_confirmed": only_confirmed,
            "limit": limit,
            "fingerprint": fingerprint,
        })
        return self._check(self._get(f"v1/contracts/{contract_address}/events", params,
                                     endpoint="v1/contracts/{address}/events"))

    def contract_events(self, contract_address: str, *, max_pages: int | None = None, **kw: Any) -> Paged:
        kw.pop("fingerprint", None)
        return paginate(lambda fp: self.contract_events_page(contract_address, fingerprint=fp, **kw),
                        self._next, self._rows, max_pages)
