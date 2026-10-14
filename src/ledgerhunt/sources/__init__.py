"""Thin, typed, read-only source clients built on RecordingClient.

Every method returns ``Fetched`` (parsed JSON + RawRef to the stored raw body) or
``Paged`` (rows + every page's Fetched). Pass one shared RecordingClient per run.
"""

from .base import BaseSource, Fetched, Paged, SourceError
from .blockscout import BlockscoutClient
from .eth_rpc import EthRpcClient, JsonRpcError
from .layerzero_scan import LayerZeroScanClient
from .near_intents import NearIntentsClient
from .tron_node import TronNodeClient, is_empty
from .trongrid import TronGridClient

__all__ = [
    "BaseSource",
    "BlockscoutClient",
    "EthRpcClient",
    "Fetched",
    "JsonRpcError",
    "LayerZeroScanClient",
    "NearIntentsClient",
    "Paged",
    "SourceError",
    "TronGridClient",
    "TronNodeClient",
    "is_empty",
]
