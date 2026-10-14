"""Extra read-only clients for the bridges/Ethereum benchmark (stage2 area 'bridges').

All go through RecordingClient (rate limits, recording, replay). Keys are sent only as secret
query parameters and never enter the request key, the index, metrics or results.

- EtherscanV2Client: https://api.etherscan.io/v2/api?chainid=1&module=...&action=... (ETHERSCAN_API_KEY,
  sent as ``apikey``). Without a key Etherscan answers with an error body; that is recorded as such.
- BlockscoutEtherscanApi: Blockscout's Etherscan-compatible RPC API on the same host as API v2
  (``/api?module=logs&action=getLogs``, ``module=block&action=getblocknobytime``).
- RangoStatusClient: https://api.rango.exchange/basic/status?requestId=&txId= (RANGO_API_KEY as ``apiKey``).
  Rango documents that every call needs an API key obtained through a Discord ticket.
- Usdt0DeploymentsClient: https://docs.usdt0.to/api/deployments (official USDT0 deployment list, JSON).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ..core.config import get_secret
from ..core.http import RecordingClient
from .base import BaseSource, Fetched

ETHERSCAN_V2 = "https://api.etherscan.io/v2"
BLOCKSCOUT_ETH = "https://eth.blockscout.com"
RANGO_API = "https://api.rango.exchange"
USDT0_DOCS = "https://docs.usdt0.to"
_ENV = object()


def _hex(n: int | str) -> str:
    return hex(n) if isinstance(n, int) else n


class EtherscanV2Client(BaseSource):
    """Etherscan API v2 (multichain). ``has_key`` tells whether ETHERSCAN_API_KEY was configured."""

    DEFAULT_BASE = ETHERSCAN_V2
    DEFAULT_PROVIDER = "etherscan_v2"

    def __init__(self, http: RecordingClient | None = None, *, chain_id: int = 1, api_key: Any = _ENV,
                 base_url: str | None = None, provider: str | None = None,
                 store_dir: Path | str | None = None) -> None:
        super().__init__(http, base_url=base_url, provider=provider, store_dir=store_dir)
        key = get_secret("ETHERSCAN_API_KEY") if api_key is _ENV else api_key
        self.has_key = bool(key)
        if key:
            self._secret_params["apikey"] = key
        self.chain_id = chain_id

    def query(self, module: str, action: str, **params: Any) -> Fetched:
        """GET /v2/api with chainid/module/action; any HTTP status is returned (body says NOTOK on errors)."""
        p = {"chainid": self.chain_id, "module": module, "action": action}
        p.update({k: v for k, v in params.items() if v is not None})
        return self._get("api", p, endpoint=f"v2/api?module={module}&action={action}",
                         allow_status=(400, 401, 403, 404, 429))

    def tx_receipt(self, tx_hash: str) -> Fetched:
        return self.query("proxy", "eth_getTransactionReceipt", txhash=tx_hash)

    def get_logs(self, *, from_block: int, to_block: int, address: str, topic0: str,
                 topic1: str | None = None) -> Fetched:
        extra = {"topic1": topic1, "topic0_1_opr": "and"} if topic1 else {}
        return self.query("logs", "getLogs", fromBlock=from_block, toBlock=to_block, address=address,
                          topic0=topic0, **extra)


class BlockscoutEtherscanApi(BaseSource):
    """Blockscout's Etherscan-compatible API (same host and rate bucket as Blockscout API v2)."""

    DEFAULT_BASE = BLOCKSCOUT_ETH
    DEFAULT_PROVIDER = "blockscout_eth"

    def __init__(self, http: RecordingClient | None = None, *, api_key: Any = _ENV, base_url: str | None = None,
                 provider: str | None = None, store_dir: Path | str | None = None) -> None:
        super().__init__(http, base_url=base_url, provider=provider, store_dir=store_dir)
        key = get_secret("BLOCKSCOUT_API_KEY") if api_key is _ENV else api_key
        if key:
            self._secret_params["apikey"] = key

    def get_logs(self, *, from_block: int, to_block: int, address: str, topic0: str,
                 topic1: str | None = None) -> Fetched:
        p: dict[str, Any] = {"module": "logs", "action": "getLogs", "fromBlock": from_block, "toBlock": to_block,
                             "address": address, "topic0": topic0}
        if topic1:
            p.update({"topic1": topic1, "topic0_1_opr": "and"})
        return self._get("api", p, endpoint="api?module=logs&action=getLogs", allow_status=(400, 404, 429))

    def block_by_time(self, timestamp: int, closest: str = "before") -> Fetched:
        p = {"module": "block", "action": "getblocknobytime", "timestamp": timestamp, "closest": closest}
        return self._get("api", p, endpoint="api?module=block&action=getblocknobytime", allow_status=(400, 404))


class BlockscoutTokens(BaseSource):
    """Blockscout API v2 token metadata (name, type, reputation) — used to explain token-transfer gaps."""

    DEFAULT_BASE = BLOCKSCOUT_ETH
    DEFAULT_PROVIDER = "blockscout_eth"

    def token(self, address: str) -> Fetched:
        return self._get(f"api/v2/tokens/{address}", endpoint="api/v2/tokens/{address}", allow_status=(404,))


class RangoStatusClient(BaseSource):
    """Rango Basic API transaction status. Needs RANGO_API_KEY (Rango issues keys via Discord)."""

    DEFAULT_BASE = RANGO_API
    DEFAULT_PROVIDER = "rango_api"

    def __init__(self, http: RecordingClient | None = None, *, api_key: Any = _ENV, base_url: str | None = None,
                 provider: str | None = None, store_dir: Path | str | None = None) -> None:
        super().__init__(http, base_url=base_url, provider=provider, store_dir=store_dir)
        key = get_secret("RANGO_API_KEY") if api_key is _ENV else api_key
        self.has_key = bool(key)
        if key:
            self._secret_params["apiKey"] = key

    def status(self, request_id: str, tx_id: str) -> Fetched:
        return self._get("basic/status", {"requestId": request_id, "txId": tx_id}, endpoint="basic/status",
                         allow_status=(400, 401, 403, 404, 429))


class Usdt0DeploymentsClient(BaseSource):
    DEFAULT_BASE = USDT0_DOCS
    DEFAULT_PROVIDER = "usdt0_docs"

    def deployments(self) -> Fetched:
        return self._get("api/deployments", endpoint="api/deployments")


def find_usdt0_contract(deployments: Any, address: str) -> list[dict[str, Any]]:
    """Every (section, chain, contract) entry in the USDT0 deployments JSON whose address equals ``address``."""
    hits: list[dict[str, Any]] = []
    target = address.lower()

    def walk(node: Any, path: list[str]) -> None:
        if isinstance(node, dict):
            if isinstance(node.get("contracts"), list):
                for c in node["contracts"]:
                    if isinstance(c, dict) and str(c.get("address", "")).lower() == target:
                        hits.append({"section": "/".join(path), "chain": node.get("name"),
                                     "lz_eid": node.get("lzEid"), "contract": c.get("name"),
                                     "address": c.get("address")})
            for k, v in node.items():
                if k != "contracts":
                    walk(v, path + [str(k)])
        elif isinstance(node, list):
            for item in node:
                walk(item, path)

    walk(deployments, [])
    return hits
