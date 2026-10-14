"""Blockscout API v2 client (Ethereum mainnet by default: https://eth.blockscout.com).

Shapes confirmed live 2026-10-14 (keyless) with case-001 tx 0x41bac088...:
- /api/v2/transactions/{hash}: object with hash, block_number, timestamp, from{hash,name,...},
  to{...}, method, status, result, token_transfers[...], decoded_input, fee{...}
- /api/v2/transactions/{hash}/token-transfers and /logs, /api/v2/addresses/{addr}/token-transfers:
  {"items": [...], "next_page_params": {...} | null}; pass next_page_params back as query params.
- Response headers x-ratelimit-limit: 180, x-ratelimit-reset (ms) -> about 3 requests/s keyless.
Optional BLOCKSCOUT_API_KEY is sent as the ``apikey`` query parameter (secret, never recorded).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ..core.config import get_secret
from ..core.http import RecordingClient
from .base import BaseSource, Fetched, Paged, paginate

BLOCKSCOUT_ETH = "https://eth.blockscout.com"
_ENV = object()


class BlockscoutClient(BaseSource):
    DEFAULT_BASE = BLOCKSCOUT_ETH
    DEFAULT_PROVIDER = "blockscout_eth"

    def __init__(
        self,
        http: RecordingClient | None = None,
        *,
        base_url: str | None = None,
        provider: str | None = None,
        store_dir: Path | str | None = None,
        api_key: Any = _ENV,
    ) -> None:
        super().__init__(http, base_url=base_url, provider=provider, store_dir=store_dir)
        key = get_secret("BLOCKSCOUT_API_KEY") if api_key is _ENV else api_key
        if key:
            self._secret_params["apikey"] = key

    @staticmethod
    def _rows(f: Fetched) -> list[Any]:
        return list((f.data or {}).get("items") or [])

    @staticmethod
    def _next(f: Fetched) -> dict[str, Any] | None:
        return (f.data or {}).get("next_page_params") or None

    def _list(self, path: str, endpoint: str, base_params: dict[str, Any] | None, max_pages: int | None) -> Paged:
        def fetch(cursor: dict[str, Any] | None) -> Fetched:
            params = dict(base_params or {})
            if cursor:
                params.update(cursor)
            return self._get(path, params or None, endpoint=endpoint)

        return paginate(fetch, self._next, self._rows, max_pages)

    # -- transactions -----------------------------------------------------
    def transaction(self, tx_hash: str) -> Fetched:
        return self._get(f"api/v2/transactions/{tx_hash}", endpoint="api/v2/transactions/{hash}")

    def transaction_token_transfers(self, tx_hash: str, *, max_pages: int | None = None) -> Paged:
        return self._list(f"api/v2/transactions/{tx_hash}/token-transfers",
                          "api/v2/transactions/{hash}/token-transfers", None, max_pages)

    def transaction_logs(self, tx_hash: str, *, max_pages: int | None = None) -> Paged:
        """Logs with raw topics/data and Blockscout's ``decoded`` (when the ABI is known)."""
        return self._list(f"api/v2/transactions/{tx_hash}/logs", "api/v2/transactions/{hash}/logs", None, max_pages)

    # -- addresses -----------------------------------------------------------
    def address(self, address: str) -> Fetched:
        """Address info incl. name / public_tags / is_contract (explorer labels)."""
        return self._get(f"api/v2/addresses/{address}", endpoint="api/v2/addresses/{address}")

    def address_token_transfers_page(
        self,
        address: str,
        *,
        type: str | None = "ERC-20",
        token: str | None = None,
        filter: str | None = None,
        page_params: dict[str, Any] | None = None,
    ) -> Fetched:
        """One page (50 rows) of /api/v2/addresses/{addr}/token-transfers. filter: 'to' | 'from' | None."""
        params: dict[str, Any] = {k: v for k, v in {"type": type, "token": token, "filter": filter}.items() if v}
        if page_params:
            params.update(page_params)
        return self._get(f"api/v2/addresses/{address}/token-transfers", params or None,
                         endpoint="api/v2/addresses/{address}/token-transfers")

    def address_token_transfers(
        self,
        address: str,
        *,
        type: str | None = "ERC-20",
        token: str | None = None,
        filter: str | None = None,
        max_pages: int | None = None,
    ) -> Paged:
        base = {k: v for k, v in {"type": type, "token": token, "filter": filter}.items() if v}
        return self._list(f"api/v2/addresses/{address}/token-transfers",
                          "api/v2/addresses/{address}/token-transfers", base, max_pages)
