"""LayerZero Scan API client (https://scan.layerzero-api.com/v1), keyless.

Confirmed live 2026-10-14 with case-001:
- GET /v1/messages/tx/{hash} needs the 0x prefix even for TRON tx ids; without it the API
  answers 404 {"message": "Message not found for tx ...", "code": 4040}. ``messages_by_tx``
  adds the prefix.
- GET /v1/messages/guid/{guid} -> {"data": [ {pathway{srcEid,dstEid,sender,receiver,nonce},
  source{status,tx{...}}, destination{status,tx{...}}, verification, guid, config,
  status{name,message}, created, updated} ]}
A 404 is returned as a Fetched with status 404 (not raised): check ``found``.
"""

from __future__ import annotations

from typing import Any

from .base import BaseSource, Fetched

LAYERZERO_SCAN = "https://scan.layerzero-api.com/v1"


def found(f: Fetched) -> bool:
    return f.status == 200 and bool((f.data or {}).get("data"))


def messages(f: Fetched) -> list[dict[str, Any]]:
    return list((f.data or {}).get("data") or []) if f.status == 200 else []


class LayerZeroScanClient(BaseSource):
    DEFAULT_BASE = LAYERZERO_SCAN
    DEFAULT_PROVIDER = "layerzero_scan"

    def messages_by_tx(self, tx_hash: str) -> Fetched:
        """Messages created by a source-chain transaction (0x added if missing)."""
        h = tx_hash if tx_hash.startswith(("0x", "0X")) else "0x" + tx_hash
        return self._get(f"messages/tx/{h}", endpoint="v1/messages/tx/{hash}", allow_status=(404,))

    def message_by_guid(self, guid: str) -> Fetched:
        return self._get(f"messages/guid/{guid}", endpoint="v1/messages/guid/{hash}", allow_status=(404,))
