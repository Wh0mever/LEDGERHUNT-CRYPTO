"""Etherscan API V2 address name-tag lookup, used by the case-001 fact check for "explorer tag" claims.

GET https://api.etherscan.io/v2/api?chainid=1&module=nametag&action=getaddresstag&address=<0x...>
The key (ETHERSCAN_API_KEY) is sent only as the secret ``apikey`` query parameter (never recorded).
Etherscan documents this endpoint as API Pro; a free key gets an error answer, which is recorded
as such. Requests run in ``cache`` mode (never repeated once recorded) unless replaying.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ..core.config import get_secret
from ..core.http import RecordingClient
from .base import BaseSource, Fetched

ETHERSCAN_V2 = "https://api.etherscan.io"


class EtherscanNameTag(BaseSource):
    DEFAULT_BASE = ETHERSCAN_V2
    DEFAULT_PROVIDER = "etherscan"

    def __init__(self, http: RecordingClient | None = None, *, store_dir: Path | str | None = None,
                 api_key: Any = ...) -> None:
        super().__init__(http, store_dir=store_dir)
        key = get_secret("ETHERSCAN_API_KEY") if api_key is ... else api_key
        self.has_key = bool(key)
        if key:
            self._secret_params["apikey"] = key

    def address_tag(self, address: str) -> Fetched:
        mode = "replay" if self.http.mode == "replay" else "cache"
        res = self.http.request(
            "GET",
            self._url("v2/api"),
            params={"chainid": 1, "module": "nametag", "action": "getaddresstag", "address": address},
            secret_params=self._secret_params or None,
            provider=self.provider,
            endpoint="v2/api?module=nametag&action=getaddresstag",
            store_dir=self.store_dir,
            mode=mode,
        )
        return Fetched.from_result(res)
