"""TronScan account lookup used ONCE by the case-001 fact check (development verification only).

Status: TronScan, pending written consent for commercial use of the API. The response is kept
only as a raw recording (separate store directory, easy to delete); its tag is NOT copied into
any label store. The request runs in ``cache`` mode: when a recording already exists nothing is
sent again, so re-running the harness never repeats the lookup. In replay mode it is served
from the recording only.

Endpoint: GET https://apilist.tronscanapi.com/api/accountv2?address=<T...> (account detail;
tag-like fields are reported as found, e.g. addressTag / publicTag / redTag / greyTag / blueTag).
TRONSCAN_API_KEY, if configured, is sent only as the TRON-PRO-API-KEY header (secret).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ..core.config import get_secret
from ..core.http import RecordingClient
from .base import BaseSource, Fetched

TRONSCAN_BASE = "https://apilist.tronscanapi.com"
TAG_FIELD_HINTS = ("tag", "label", "name")


class TronScanTagLookup(BaseSource):
    DEFAULT_BASE = TRONSCAN_BASE
    DEFAULT_PROVIDER = "tronscan_pending_consent"

    def __init__(self, http: RecordingClient | None = None, *, store_dir: Path | str | None = None,
                 api_key: Any = ...) -> None:
        super().__init__(http, store_dir=store_dir)
        key = get_secret("TRONSCAN_API_KEY") if api_key is ... else api_key
        if key:
            self._secret_headers["TRON-PRO-API-KEY"] = key

    def account(self, address: str) -> Fetched:
        """One account-detail request; never repeated once recorded (cache mode unless replaying)."""
        mode = "replay" if self.http.mode == "replay" else "cache"
        res = self.http.request(
            "GET",
            self._url("api/accountv2"),
            params={"address": address},
            secret_headers=self._secret_headers or None,
            provider=self.provider,
            endpoint="api/accountv2",
            store_dir=self.store_dir,
            mode=mode,
        )
        return Fetched.from_result(res)


def tag_fields(data: Any) -> dict[str, Any]:
    """Top-level fields whose name looks like a tag/label (values kept as returned)."""
    if not isinstance(data, dict):
        return {}
    return {k: v for k, v in data.items() if any(h in k.lower() for h in TAG_FIELD_HINTS) and v not in (None, "", [])}
