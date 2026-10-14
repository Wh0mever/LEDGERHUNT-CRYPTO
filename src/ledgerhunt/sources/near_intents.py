"""NEAR Intents 1Click API client (https://1click.chaindefuser.com), status endpoint.

Confirmed live 2026-10-14 keyless with case-001 deposit address 0xdA39...22C0:
GET /v0/status?depositAddress=... -> {status, updatedAt, correlationId, swapDetails{
amountIn, amountOut, intentHashes[], nearTxHashes[], originChainTxHashes[{hash}],
destinationChainTxHashes[{hash}], refundFee, withdrawFee, ...}, quoteResponse{quoteRequest{
originAsset, destinationAsset, recipient, refundTo, referral, appFees...}, quote{depositAddress,...}}}.
Rate-limit headers seen: x-ratelimit-limit-unauth: 1200 (per 60 s window).
Optional NEAR_INTENTS_JWT is sent as ``Authorization: Bearer`` (secret, never recorded).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ..core.config import get_secret
from ..core.http import RecordingClient
from .base import BaseSource, Fetched

ONECLICK_BASE = "https://1click.chaindefuser.com"
_ENV = object()


class NearIntentsClient(BaseSource):
    DEFAULT_BASE = ONECLICK_BASE
    DEFAULT_PROVIDER = "near_intents_1click"

    def __init__(
        self,
        http: RecordingClient | None = None,
        *,
        base_url: str | None = None,
        provider: str | None = None,
        store_dir: Path | str | None = None,
        jwt: Any = _ENV,
    ) -> None:
        super().__init__(http, base_url=base_url, provider=provider, store_dir=store_dir)
        token = get_secret("NEAR_INTENTS_JWT") if jwt is _ENV else jwt
        if token:
            self._secret_headers["Authorization"] = f"Bearer {token}"

    def status(self, deposit_address: str, deposit_memo: str | None = None) -> Fetched:
        """Swap status for a 1Click deposit address (404 returned, not raised)."""
        params = {"depositAddress": deposit_address}
        if deposit_memo:
            params["depositMemo"] = deposit_memo
        return self._get("v0/status", params, endpoint="v0/status", allow_status=(404,))
