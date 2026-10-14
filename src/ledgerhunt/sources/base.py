"""Shared pieces of the read-only source clients."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Mapping

from ..core.http import HttpResult, RawRef, RecordingClient


class SourceError(Exception):
    """A source answered, but not with usable data (HTTP error, success=false, JSON-RPC error)."""

    def __init__(self, message: str, fetched: "Fetched | None" = None) -> None:
        self.fetched = fetched
        super().__init__(message)


@dataclass
class Fetched:
    """Parsed JSON of one response plus where its raw body is stored."""

    data: Any  # parsed JSON (non-integer numbers are Decimal)
    ref: RawRef | None  # None only in live mode (nothing stored)
    status: int
    latency_ms: float
    attempts: int
    from_replay: bool
    url: str  # redacted

    @classmethod
    def from_result(cls, res: HttpResult, data: Any = None) -> "Fetched":
        if data is None:
            try:
                data = res.json()
            except ValueError:
                data = None
        return cls(data, res.ref, res.status, res.latency_ms, res.attempts, res.from_replay, res.url)

    def ref_dict(self) -> dict[str, Any] | None:
        return self.ref.to_dict() if self.ref else None


@dataclass
class Paged:
    """All rows of a paginated listing plus every page fetched."""

    rows: list[Any] = field(default_factory=list)
    pages: list[Fetched] = field(default_factory=list)
    complete: bool = False  # True when the source reported no further page

    @property
    def refs(self) -> list[RawRef]:
        return [p.ref for p in self.pages if p.ref is not None]


class BaseSource:
    """Common GET/POST plumbing over a RecordingClient."""

    DEFAULT_BASE: str = ""
    DEFAULT_PROVIDER: str = ""

    def __init__(
        self,
        http: RecordingClient | None = None,
        *,
        base_url: str | None = None,
        provider: str | None = None,
        store_dir: Path | str | None = None,
    ) -> None:
        self.http = http or RecordingClient()
        self.base_url = (base_url or self.DEFAULT_BASE).rstrip("/")
        self.provider = provider or self.DEFAULT_PROVIDER
        self.store_dir = store_dir
        self._secret_headers: dict[str, str] = {}
        self._secret_params: dict[str, str] = {}
        self._rate_key: str | None = None

    def _url(self, path: str) -> str:
        return f"{self.base_url}/{path.lstrip('/')}"

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: Mapping[str, Any] | None = None,
        json: Any = None,
        endpoint: str | None = None,
        allow_status: tuple[int, ...] = (),
    ) -> Fetched:
        res = self.http.request(
            method,
            self._url(path),
            params=params,
            json=json,
            secret_headers=self._secret_headers or None,
            secret_params=self._secret_params or None,
            provider=self.provider,
            endpoint=endpoint,
            store_dir=self.store_dir,
            rate_key=self._rate_key,
        )
        fetched = Fetched.from_result(res)
        if not res.ok and res.status not in allow_status:
            raise SourceError(f"{self.provider} {endpoint or path}: HTTP {res.status}: {res.text[:300]}", fetched)
        return fetched

    def _get(self, path: str, params: Mapping[str, Any] | None = None, **kw: Any) -> Fetched:
        return self._request("GET", path, params=params, **kw)

    def _post(self, path: str, json: Any, **kw: Any) -> Fetched:
        return self._request("POST", path, json=json, **kw)


def paginate(fetch_page: Callable[[Any], Fetched], next_cursor: Callable[[Fetched], Any],
             rows_of: Callable[[Fetched], list[Any]], max_pages: int | None) -> Paged:
    """Generic cursor pagination: ``fetch_page(cursor)`` until ``next_cursor`` is falsy or max_pages."""
    out = Paged()
    cursor = None
    while True:
        page = fetch_page(cursor)
        out.pages.append(page)
        out.rows.extend(rows_of(page))
        cursor = next_cursor(page)
        if not cursor:
            out.complete = True
            return out
        if max_pages is not None and len(out.pages) >= max_pages:
            out.complete = False
            return out
