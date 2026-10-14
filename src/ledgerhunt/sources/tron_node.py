"""java-tron HTTP API client (/wallet and /walletsolidity) at a configurable base URL.

Default base: https://tron-rpc.publicnode.com (keyless). Confirmed 2026-10-14: it serves
/wallet/* and /walletsolidity/*, but it is NOT an archive: case-001 transactions
(blocks ~86.44M, 2026-09-21) come back as ``{}``; blocks from 7 days earlier were served.
java-tron answers ``{}`` (HTTP 200) when a transaction/block is unknown — check with
``is_empty``. A paid provider URL (may embed a key) comes from ``TronNodeClient.from_env``.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ..core.config import require_secret
from ..core.http import RecordingClient
from ..core.tron import USDT_TRC20, address_to_word
from .base import BaseSource, Fetched

PUBLICNODE_TRON = "https://tron-rpc.publicnode.com"


def is_empty(fetched: Fetched) -> bool:
    """True when java-tron returned an empty object (unknown tx/block, or outside node history)."""
    return isinstance(fetched.data, dict) and not fetched.data


class TronNodeClient(BaseSource):
    DEFAULT_BASE = PUBLICNODE_TRON
    DEFAULT_PROVIDER = "tron_publicnode"

    def __init__(
        self,
        http: RecordingClient | None = None,
        *,
        base_url: str | None = None,
        provider: str | None = None,
        store_dir: Path | str | None = None,
        api_key: str | None = None,
        api_key_header: str = "TRON-PRO-API-KEY",
    ) -> None:
        super().__init__(http, base_url=base_url, provider=provider, store_dir=store_dir)
        if api_key:
            self._secret_headers[api_key_header] = api_key

    @classmethod
    def from_env(
        cls,
        name: str = "TRON_RPC_URL",
        http: RecordingClient | None = None,
        *,
        provider: str = "tron_rpc_paid",
        store_dir: Path | str | None = None,
    ) -> "TronNodeClient":
        """Client for a provider URL kept in a secret env var (the whole URL is treated as secret).

        Raises MissingSecretError when the variable is not set. The URL may include a path
        prefix (e.g. .../<key>) — '/wallet/...' is appended to it.
        """
        return cls(http, base_url=require_secret(name), provider=provider, store_dir=store_dir)

    # -- generic -------------------------------------------------------
    def call(self, path: str, payload: dict[str, Any] | None = None, *, endpoint: str | None = None) -> Fetched:
        """POST any java-tron HTTP API path, e.g. call('wallet/getnowblock', {})."""
        return self._post(path, payload or {}, endpoint=endpoint or path.strip("/"))

    @staticmethod
    def _p(solidity: bool) -> str:
        return "walletsolidity" if solidity else "wallet"

    # -- blocks --------------------------------------------------------
    def get_now_block(self, *, solidity: bool = False) -> Fetched:
        """Latest block (~0.5 MB with all transactions)."""
        return self.call(f"{self._p(solidity)}/getnowblock")

    def get_block_by_num(self, num: int, *, solidity: bool = False) -> Fetched:
        return self.call(f"{self._p(solidity)}/getblockbynum", {"num": int(num)})

    # -- transactions --------------------------------------------------
    def get_transaction_by_id(self, txid: str, *, solidity: bool = False, visible: bool = True) -> Fetched:
        """Signed transaction (raw_data, signature, ret). visible=True -> base58 addresses."""
        return self.call(f"{self._p(solidity)}/gettransactionbyid", {"value": txid, "visible": visible})

    def get_transaction_info_by_id(self, txid: str, *, solidity: bool = True) -> Fetched:
        """Receipt: fee, blockNumber, blockTimeStamp, receipt{energy_usage...,result}, log[] (hex addresses)."""
        return self.call(f"{self._p(solidity)}/gettransactioninfobyid", {"value": txid})

    def get_transaction_info_by_block_num(self, num: int, *, solidity: bool = True) -> Fetched:
        """All receipts of one block (list)."""
        return self.call(f"{self._p(solidity)}/gettransactioninfobyblocknum", {"num": int(num)})

    # -- accounts / contracts -----------------------------------------
    def get_account(self, address: str, *, solidity: bool = False, visible: bool = True) -> Fetched:
        """Account state: balance (sun), create_time, owner_permission/active_permission, frozenV2, ..."""
        return self.call(f"{self._p(solidity)}/getaccount", {"address": address, "visible": visible})

    def trigger_constant_contract(
        self,
        owner_address: str,
        contract_address: str,
        function_selector: str,
        parameter: str = "",
        *,
        visible: bool = True,
    ) -> Fetched:
        """Read-only contract call. ``parameter`` is ABI-encoded hex without 0x.

        Result: data['constant_result'][0] (hex), data['result']['result'] (bool).
        """
        payload = {
            "owner_address": owner_address,
            "contract_address": contract_address,
            "function_selector": function_selector,
            "parameter": parameter,
            "visible": visible,
        }
        return self.call("wallet/triggerconstantcontract", payload)

    def trc20_balance_of(self, holder: str, contract: str = USDT_TRC20) -> tuple[int | None, Fetched]:
        """balanceOf(holder) as a raw integer (None if the call returned no result)."""
        f = self.trigger_constant_contract(holder, contract, "balanceOf(address)", address_to_word(holder))
        results = (f.data or {}).get("constant_result") or []
        value = int(results[0], 16) if results and results[0] else None
        return value, f
