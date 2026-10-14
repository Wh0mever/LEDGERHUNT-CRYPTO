"""Helpers for the Stage 2 TRON source benchmark (area ``tron_sources``).

- ``TronJsonRpcClient``: the java-tron ``/jsonrpc`` endpoint (eth_getLogs, eth_blockNumber, ...)
  of any TRON operator, with an optional TronGrid key sent only as a secret header.
- ``BenchSource``: one TRON operator as seen by the benchmark (node API, JSON-RPC and, for
  TronGrid, the v1 index), built from the shared RecordingClient. Keys and paid URLs are read
  through ``ledgerhunt.core.config`` and never stored; results record only presence booleans.
- Small pure decoders: JSON-RPC USDT Transfer logs, java-tron receipt logs, v1 TRC20 rows and
  v1 events into one comparable shape ``{txid, from, to, value, ...}``.
- ``raw_request``: one request through a source client's settings that returns the full
  ``HttpResult`` (status, kept headers, body) instead of raising on non-2xx; the load phases need
  the 429 headers and bodies.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ..core.config import get_secret, has_secret, require_secret
from ..core.evm import TRANSFER_TOPIC, strip0x
from ..core.http import HttpResult, RecordingClient
from ..core.tron import USDT_TRC20, USDT_TRC20_HEX, address_to_word, hex_to_b58, word_to_b58
from .base import Fetched
from .eth_rpc import EthRpcClient, JsonRpcError
from .tron_node import PUBLICNODE_TRON, TronNodeClient
from .trongrid import TRONGRID_BASE, TronGridClient

USDT_LOG_ADDRESS = USDT_TRC20_HEX[2:].lower()  # receipt/JSON-RPC log address form (no 41 prefix)
USDT_JSONRPC_ADDRESS = "0x" + USDT_LOG_ADDRESS
TRANSFER_TOPIC_BARE = strip0x(TRANSFER_TOPIC).lower()


class TronJsonRpcClient(EthRpcClient):
    """java-tron JSON-RPC (``<base>/jsonrpc``). Same call surface as EthRpcClient."""

    def __init__(
        self,
        http: RecordingClient | None = None,
        *,
        url: str,
        provider: str,
        api_key: str | None = None,
        api_key_header: str = "TRON-PRO-API-KEY",
        rate_key: str | None = None,
        store_dir: Path | str | None = None,
    ) -> None:
        super().__init__(http, url=url, provider=provider, store_dir=store_dir)
        if api_key:
            self._secret_headers[api_key_header] = api_key
        self._rate_key = rate_key

    def usdt_transfer_logs(self, *, from_block: int, to_block: int, sender: str | None = None,
                           receiver: str | None = None) -> Fetched:
        """eth_getLogs for USDT Transfer with an optional indexed sender / receiver filter."""
        topics: list[Any] = [TRANSFER_TOPIC, "0x" + address_to_word(sender) if sender else None]
        if receiver:
            topics.append("0x" + address_to_word(receiver))
        return self.get_logs(from_block=from_block, to_block=to_block, address=USDT_JSONRPC_ADDRESS,
                             topics=topics)


@dataclass
class BenchSource:
    """One TRON operator in the benchmark."""

    name: str                 # trongrid_key | trongrid_keyless | publicnode | paid_rpc | paid_rpc_2
    operator: str             # human label: TronGrid / PublicNode / paid provider (env var)
    node: TronNodeClient
    jsonrpc: TronJsonRpcClient | None
    v1: TronGridClient | None = None
    keyed: bool = False
    paid: bool = False
    notes: list[str] = field(default_factory=list)

    @property
    def rate_key(self) -> str | None:
        return self.node._rate_key  # noqa: SLF001 - bench needs the limiter bucket

    def set_rate_key(self, key: str) -> None:
        """Route this source's requests through another limiter bucket (load phases)."""
        self.node._rate_key = key  # noqa: SLF001
        if self.jsonrpc is not None:
            self.jsonrpc._rate_key = key  # noqa: SLF001
        if self.v1 is not None and self.v1 is not self.node:
            self.v1._rate_key = key  # noqa: SLF001


def _host(url: str) -> str:
    return url.split("://", 1)[-1].split("/", 1)[0].lower()


def trongrid_source(http: RecordingClient, *, keyed: bool) -> BenchSource | None:
    """TronGrid with the key from .env (keyed=True; None when the key is absent) or forced keyless."""
    if keyed and not has_secret("TRONGRID_API_KEY"):
        return None
    tg = TronGridClient(http) if keyed else TronGridClient(http, api_key=None)
    key = get_secret("TRONGRID_API_KEY") if keyed else None
    rpc = TronJsonRpcClient(http, url=f"{TRONGRID_BASE}/jsonrpc", provider="trongrid_jsonrpc", api_key=key,
                            rate_key=tg._rate_key)  # noqa: SLF001 - same bucket as the rest of TronGrid
    return BenchSource(name="trongrid_key" if keyed else "trongrid_keyless", operator="TronGrid",
                       node=tg, jsonrpc=rpc, v1=tg, keyed=keyed)


def publicnode_source(http: RecordingClient) -> BenchSource:
    node = TronNodeClient(http)  # base https://tron-rpc.publicnode.com, provider tron_publicnode
    rpc = TronJsonRpcClient(http, url=f"{PUBLICNODE_TRON}/jsonrpc", provider="tron_publicnode_jsonrpc",
                            rate_key=_host(PUBLICNODE_TRON))
    return BenchSource(name="publicnode", operator="PublicNode (Allnodes)", node=node, jsonrpc=rpc)


def paid_source(http: RecordingClient, env_name: str = "TRON_RPC_URL", *, jsonrpc_suffix: str = "/jsonrpc",
                rps: float | None = None) -> BenchSource | None:
    """Paid TRON provider from a secret URL (the whole URL is a secret). None when not configured."""
    if not has_secret(env_name):
        return None
    suffix = env_name.lower().replace("tron_rpc_url", "")  # '' or '_2'
    provider = f"tron_rpc_paid{suffix}"
    node = TronNodeClient.from_env(env_name, http, provider=provider)
    base = require_secret(env_name).rstrip("/")
    rate_key = f"paid-tron{suffix}"
    node._rate_key = rate_key  # noqa: SLF001 - keep the secret host out of limiter file names
    if rps is not None:
        http.set_rate(rate_key, rps)
    rpc = TronJsonRpcClient(http, url=base + jsonrpc_suffix, provider=f"{provider}_jsonrpc", rate_key=rate_key)
    return BenchSource(name=f"paid_rpc{suffix}", operator=f"платный провайдер ({env_name})", node=node,
                       jsonrpc=rpc, paid=True)


# ---------------------------------------------------------------- raw requests


def raw_request(client: Any, method: str, path_or_url: str, *, params: dict[str, Any] | None = None,
                json: Any = None, endpoint: str | None = None, mode: str | None = None) -> HttpResult:
    """One request with a source client's base URL, secret headers, provider and limiter bucket.

    Returns the HttpResult for any status (no exception on 4xx/5xx). ``path_or_url`` is a path
    under the client's base URL, or '' for the base URL itself (JSON-RPC).
    """
    url = client.base_url if not path_or_url else client._url(path_or_url)  # noqa: SLF001
    return client.http.request(
        method,
        url,
        params=params,
        json=json,
        secret_headers=client._secret_headers or None,  # noqa: SLF001
        secret_params=client._secret_params or None,  # noqa: SLF001
        provider=client.provider,
        endpoint=endpoint,
        store_dir=client.store_dir,
        rate_key=client._rate_key,  # noqa: SLF001
        mode=mode,
    )


# ---------------------------------------------------------------- block headers


def block_header(node: TronNodeClient, num: int | None = None, *, solidity: bool = False) -> dict[str, Any] | None:
    """Header of block ``num`` (latest when None) via /wallet[solidity]/getblock detail=false.

    Returns {num, ts_ms, id, ref} or None when the node answers ``{}`` (unknown / outside history).
    """
    payload: dict[str, Any] = {"detail": False}
    if num is not None:
        payload["id_or_num"] = str(int(num))
    f = node.call(f"{'walletsolidity' if solidity else 'wallet'}/getblock", payload)
    return parse_header(f)


def parse_header(f: Fetched) -> dict[str, Any] | None:
    data = f.data if isinstance(f.data, dict) else {}
    raw = ((data.get("block_header") or {}).get("raw_data") or {})
    if not raw:
        return None
    return {"num": int(raw.get("number", 0)), "ts_ms": int(raw.get("timestamp", 0)), "id": data.get("blockID"),
            "ref": f.ref_dict(), "latency_ms": f.latency_ms}


# ---------------------------------------------------------------- decoders


def _word_addr(word: str) -> str:
    return word_to_b58(strip0x(word)[-64:].rjust(64, "0"))


def transfer_from_jsonrpc_log(log: dict[str, Any]) -> dict[str, Any] | None:
    """USDT Transfer from an eth_getLogs entry (TRON JSON-RPC). None for other logs."""
    topics = [strip0x(t).lower() for t in (log.get("topics") or [])]
    if len(topics) < 3 or topics[0] != TRANSFER_TOPIC_BARE:
        return None
    if strip0x(str(log.get("address", ""))).lower()[-40:] != USDT_LOG_ADDRESS:
        return None
    data = strip0x(log.get("data") or "") or "0"
    ts = log.get("blockTimestamp")
    return {
        "txid": strip0x(log.get("transactionHash", "")).lower(),
        "from": _word_addr(topics[1]),
        "to": _word_addr(topics[2]),
        "value": int(data, 16),
        "block": int(log["blockNumber"], 16) if log.get("blockNumber") else None,
        "log_index_block": int(log["logIndex"], 16) if log.get("logIndex") else None,
        "tx_index": int(log["transactionIndex"], 16) if log.get("transactionIndex") else None,
        "ts_s": int(ts, 16) if isinstance(ts, str) and ts.startswith("0x") else None,
    }


def transfers_from_receipt(info: dict[str, Any]) -> list[dict[str, Any]]:
    """USDT Transfer logs of a java-tron receipt with their ordinal in ``log[]`` (0-based)."""
    out = []
    for i, log in enumerate(info.get("log") or []):
        topics = [strip0x(t).lower() for t in (log.get("topics") or [])]
        if len(topics) < 3 or topics[0] != TRANSFER_TOPIC_BARE:
            continue
        if strip0x(str(log.get("address", ""))).lower()[-40:] != USDT_LOG_ADDRESS:
            continue
        out.append({"ordinal": i, "from": _word_addr(topics[1]), "to": _word_addr(topics[2]),
                    "value": int(strip0x(log.get("data") or "") or "0", 16)})
    return out


def transfer_from_v1_row(row: dict[str, Any]) -> dict[str, Any]:
    """One /v1/accounts/{addr}/transactions/trc20 row in the comparable shape."""
    return {
        "txid": str(row.get("transaction_id", "")).lower(),
        "from": row.get("from"),
        "to": row.get("to"),
        "value": int(row.get("value") or 0),
        "type": row.get("type"),
        "ts_ms": int(row.get("block_timestamp") or 0),
        "token": (row.get("token_info") or {}).get("address"),
    }


def transfers_from_v1_events(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """USDT Transfer events of /v1/transactions/{txid}/events with their event_index."""
    out = []
    for ev in rows:
        if ev.get("event_name") != "Transfer" or ev.get("contract_address") != USDT_TRC20:
            continue
        res = ev.get("result") or {}
        try:
            frm = hex_to_b58(res.get("from") or res.get("0"))
            to = hex_to_b58(res.get("to") or res.get("1"))
        except (ValueError, TypeError):
            continue
        out.append({"event_index": ev.get("event_index"), "from": frm, "to": to,
                    "value": int(res.get("value") or res.get("2") or 0),
                    "block": ev.get("block_number"), "ts_ms": ev.get("block_timestamp")})
    return out


def is_result_limit_error(exc: Exception) -> bool:
    """java-tron eth_getLogs refuses ranges with more than 10 000 matching logs (-32005)."""
    return isinstance(exc, JsonRpcError) and "more than" in str(exc.error).lower()
