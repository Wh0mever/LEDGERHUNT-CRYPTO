"""Ethereum JSON-RPC client (works for any EVM JSON-RPC, incl. TRON's /jsonrpc).

Default URL: https://ethereum-rpc.publicnode.com (keyless; confirmed live 2026-10-14:
eth_getTransactionReceipt / eth_getTransactionByHash for case-001 tx 0x8ea2bdef... and
eth_getBlockByNumber(26025709)). A paid URL (may embed a key) comes from ``EthRpcClient.from_env``.
Request ids are always 1 so identical calls map to one recorded response (replay).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ..core.config import require_secret
from ..core.http import RecordingClient
from .base import BaseSource, Fetched, SourceError

PUBLICNODE_ETH = "https://ethereum-rpc.publicnode.com"


class JsonRpcError(SourceError):
    def __init__(self, method: str, error: Any, fetched: Fetched) -> None:
        self.method = method
        self.error = error
        super().__init__(f"JSON-RPC {method} error: {str(error)[:300]}", fetched)


class EthRpcClient(BaseSource):
    DEFAULT_PROVIDER = "eth_publicnode"

    def __init__(
        self,
        http: RecordingClient | None = None,
        *,
        url: str | None = None,
        provider: str | None = None,
        store_dir: Path | str | None = None,
    ) -> None:
        super().__init__(http, base_url=url or PUBLICNODE_ETH, provider=provider, store_dir=store_dir)

    @classmethod
    def from_env(cls, name: str = "ETH_RPC_URL", http: RecordingClient | None = None, *,
                 provider: str = "eth_rpc_paid", store_dir: Path | str | None = None) -> "EthRpcClient":
        """Client for an RPC URL kept in a secret env var. Raises MissingSecretError if unset."""
        return cls(http, url=require_secret(name), provider=provider, store_dir=store_dir)

    def call(self, method: str, params: list[Any] | None = None) -> Fetched:
        """POST one JSON-RPC call. Returns Fetched whose ``data`` is the ``result`` member.

        Raises JsonRpcError when the response has an ``error`` member.
        """
        payload = {"jsonrpc": "2.0", "id": 1, "method": method, "params": params or []}
        res = self.http.request(
            "POST",
            self.base_url,
            json=payload,
            secret_headers=self._secret_headers or None,
            provider=self.provider,
            endpoint=f"jsonrpc/{method}",
            store_dir=self.store_dir,
            rate_key=self._rate_key,
        )
        fetched = Fetched.from_result(res)
        if not res.ok:
            raise SourceError(f"{self.provider} {method}: HTTP {res.status}: {res.text[:300]}", fetched)
        envelope = fetched.data if isinstance(fetched.data, dict) else {}
        if envelope.get("error") is not None:
            raise JsonRpcError(method, envelope["error"], fetched)
        fetched.data = envelope.get("result")
        return fetched

    # -- convenience -----------------------------------------------------
    def block_number(self) -> tuple[int, Fetched]:
        f = self.call("eth_blockNumber")
        return int(f.data, 16), f

    def get_transaction_by_hash(self, tx_hash: str) -> Fetched:
        return self.call("eth_getTransactionByHash", [tx_hash])

    def get_transaction_receipt(self, tx_hash: str) -> Fetched:
        """Receipt with status, blockNumber, logs[{address, topics, data, logIndex, ...}]."""
        return self.call("eth_getTransactionReceipt", [tx_hash])

    def get_block_by_number(self, number: int | str, full_transactions: bool = False) -> Fetched:
        tag = hex(number) if isinstance(number, int) else number
        return self.call("eth_getBlockByNumber", [tag, full_transactions])

    def get_logs(self, *, from_block: int | str, to_block: int | str, address: str | list[str] | None = None,
                 topics: list[Any] | None = None) -> Fetched:
        flt: dict[str, Any] = {
            "fromBlock": hex(from_block) if isinstance(from_block, int) else from_block,
            "toBlock": hex(to_block) if isinstance(to_block, int) else to_block,
        }
        if address is not None:
            flt["address"] = address
        if topics is not None:
            flt["topics"] = topics
        return self.call("eth_getLogs", [flt])
