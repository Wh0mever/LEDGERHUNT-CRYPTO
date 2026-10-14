"""RecordingClient: polite, recorded, replayable HTTP for every external source.

Modes
-----
- ``live``   : send requests, store nothing (metrics are still collected).
- ``record`` : send requests and store every final response (default).
- ``replay`` : never touch the network; serve from the store; ``ReplayMiss`` on a miss.
- ``cache``  : serve from the store when the request was recorded before, otherwise
               behave like ``record``. Use for re-runs that must not re-download.

The default mode comes from env ``LEDGERHUNT_HTTP_MODE`` (the CLI sets it to
``replay`` for ``--replay``) and falls back to ``record``.

Store layout (``store_dir``, default ``data/http-store``)::

    <store>/objects/<sha[:2]>/<sha256-of-body>   raw response body bytes
    <store>/index.jsonl                          one JSON row per stored response

Each index row maps a canonical request key (provider, method, URL without
secrets, sorted query params, canonical JSON body) to the body hash, status,
a subset of response headers, latency, attempts, size, timestamp and tag.
Secrets never reach the key, the index, the metrics or the logs: keys are sent
through ``secret_headers`` / ``secret_params`` and everything written is passed
through ``redact``.
"""

from __future__ import annotations

import email.utils
import hashlib
import json
import os
import random
import re
import threading
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import httpx

from . import restricted
from .config import load_env
from .filelock import FileLock
from .paths import default_http_store, ratelimit_state_dir, rel_to_root, repo_root
from .ratelimit import DEFAULT_RPS, RateLimiter
from .log import get_logger
from .redact import contains_registered_secret, redact, redact_bytes, redact_obj

log = get_logger("ledgerhunt.http")

MODES = ("live", "record", "replay", "cache")
RETRY_STATUSES = frozenset({429, 500, 502, 503, 504, 520, 521, 522, 523, 524})
DEFAULT_TIMEOUT = httpx.Timeout(connect=10.0, read=30.0, write=10.0, pool=10.0)
DEFAULT_PENALTY_429: dict[str, float] = {"api.trongrid.io": 5.0}
USER_AGENT = "ledgerhunt/0.2 (stage-2 measurements; read-only)"

_KEEP_HEADERS = {
    "content-type",
    "content-length",
    "content-encoding",
    "date",
    "retry-after",
    "server",
    "cf-cache-status",
    "age",
    "via",
}
_KEEP_HEADER_PREFIXES = ("x-ratelimit", "ratelimit", "x-rate-limit", "x-ratelimit-")

_TRON_B58 = re.compile(r"^T[1-9A-HJ-NP-Za-km-z]{33}$")
_EVM_ADDR = re.compile(r"^0x[0-9a-fA-F]{40}$")
_HASH = re.compile(r"^(0x)?[0-9a-fA-F]{64}$")
_NUM = re.compile(r"^\d+$")


def default_mode() -> str:
    mode = os.environ.get("LEDGERHUNT_HTTP_MODE", "record").strip().lower() or "record"
    if mode not in MODES:
        raise ValueError(f"LEDGERHUNT_HTTP_MODE must be one of {MODES}, got {mode!r}")
    return mode


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


# ---------------------------------------------------------------- errors


class HttpError(Exception):
    """Base class for RecordingClient errors."""


class HttpStatusError(HttpError):
    """Non-2xx final response (raised by ``HttpResult.raise_for_status``)."""

    def __init__(self, result: "HttpResult") -> None:
        self.result = result
        super().__init__(f"HTTP {result.status} from {result.provider} {result.endpoint} ({result.url})")


class RequestFailed(HttpError):
    """No response after all attempts (timeouts / connection errors)."""

    def __init__(self, message: str, *, error_class: str, attempts: int) -> None:
        self.error_class = error_class
        self.attempts = attempts
        super().__init__(message)


class ReplayMiss(HttpError):
    """Replay mode and the request is not in the store."""

    def __init__(self, request_key: str, store_dir: Path) -> None:
        self.request_key = request_key
        self.store_dir = store_dir
        super().__init__(
            "replay miss: request not recorded in store "
            f"{rel_to_root(store_dir)}: {request_key[:300]} "
            "-- run once without --replay (record mode) to capture it"
        )


class LiveRequestInReplay(ReplayMiss):
    """The process runs with --replay (LEDGERHUNT_HTTP_MODE=replay) but a client or call asked for
    the network (explicit live/record mode, or a cache miss). Never fall back to live silently."""

    def __init__(self, request_key: str, store_dir: Path, mode: str) -> None:
        super().__init__(request_key, store_dir)
        self.args = (
            f"network request refused: process is in replay mode but this request uses mode {mode!r} "
            f"and is not served from {rel_to_root(store_dir)}: {request_key[:300]}",
        )

    def __str__(self) -> str:
        return self.args[0]


class RestrictedBodyMissing(ReplayMiss):
    """Replay: the request is indexed, but its body belongs to a provider whose terms do not allow
    storing it in git (see ``core.restricted``) and the file is absent (e.g. a fresh clone)."""

    def __init__(self, request_key: str, store_dir: Path, provider: str) -> None:
        super().__init__(request_key, store_dir)
        self.provider = provider
        self.args = (
            f"{restricted.absent_message([provider])}: тело ответа отсутствует в {rel_to_root(store_dir)} "
            f"(полный повтор — на машине владельцев): {request_key[:300]}",
        )

    def __str__(self) -> str:
        return self.args[0]


def _process_in_replay() -> bool:
    return os.environ.get("LEDGERHUNT_HTTP_MODE", "").strip().lower() == "replay"


# ---------------------------------------------------------------- data


@dataclass(frozen=True)
class RawRef:
    """Pointer to a stored raw response body."""

    store: str  # store directory, repo-relative POSIX path when inside the repo
    body_sha256: str
    key_sha256: str

    @property
    def object_path(self) -> str:
        return f"{self.store}/objects/{self.body_sha256[:2]}/{self.body_sha256}"

    def to_dict(self) -> dict[str, str]:
        d = asdict(self)
        d["object_path"] = self.object_path
        return d


@dataclass
class HttpResult:
    method: str
    url: str  # redacted URL including query string
    status: int
    headers: dict[str, str]
    body: bytes
    latency_ms: float
    attempts: int
    provider: str
    endpoint: str
    from_replay: bool
    ref: RawRef | None
    timestamp_utc: str
    meta: dict[str, Any] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return 200 <= self.status < 300

    @property
    def text(self) -> str:
        return self.body.decode("utf-8", errors="replace")

    def json(self) -> Any:
        """Parse the body as JSON. Non-integer numbers become Decimal (never float)."""
        return json.loads(self.body, parse_float=Decimal)

    def raise_for_status(self) -> "HttpResult":
        if not self.ok:
            raise HttpStatusError(self)
        return self


# ---------------------------------------------------------------- helpers


def endpoint_template(path: str) -> str:
    """Turn a URL path into a template: addresses -> {address}, hashes -> {hash}, numbers -> {n}."""
    out = []
    for seg in path.strip("/").split("/"):
        if _TRON_B58.match(seg) or _EVM_ADDR.match(seg):
            out.append("{address}")
        elif _HASH.match(seg):
            out.append("{hash}")
        elif _NUM.match(seg):
            out.append("{n}")
        else:
            out.append(seg)
    return redact("/".join(out))


def _param_pairs(params: Mapping[str, Any] | Iterable[tuple[str, Any]] | None) -> list[tuple[str, str]]:
    if not params:
        return []
    items = params.items() if isinstance(params, Mapping) else params
    pairs: list[tuple[str, str]] = []
    for k, v in items:
        if v is None:
            continue
        values = v if isinstance(v, (list, tuple)) else [v]
        for item in values:
            if isinstance(item, bool):
                item = "true" if item else "false"
            pairs.append((str(k), str(item)))
    return pairs


_SECRET_PARAM_NAMES = {"api_key", "api-key", "apikey", "key", "token", "access_token", "auth_token",
                       "auth", "secret", "jwt", "x-api-key"}
_PUBLIC_VALUE = re.compile(r"^(?:0x[0-9a-fA-F]{40}|T[1-9A-HJ-NP-Za-km-z]{33})$")


def _mask_param(name: str, value: str) -> str:
    if name.lower() in _SECRET_PARAM_NAMES and not _PUBLIC_VALUE.match(value):
        return "***"
    return value


def canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)


def canonical_request_key(
    method: str,
    url: str,
    params: Mapping[str, Any] | Iterable[tuple[str, Any]] | None = None,
    json_body: Any = None,
    provider: str = "",
) -> str:
    """Canonical, secret-free request key: ``provider METHOD url?sorted-params`` + newline + canonical JSON."""
    parts = urlsplit(url)
    pairs = parse_qsl(parts.query, keep_blank_values=True) + _param_pairs(params)
    pairs.sort()
    base = urlunsplit((parts.scheme.lower(), parts.netloc.lower(), parts.path or "/", "", ""))
    key = f"{provider} {method.upper()} {base}"
    if pairs:
        key += "?" + urlencode(pairs)
    if json_body is not None:
        key += "\n" + canonical_json(json_body)
    return redact(key)


def _keep_headers(headers: httpx.Headers | Mapping[str, str]) -> dict[str, str]:
    out: dict[str, str] = {}
    for name, value in headers.items():
        n = name.lower()
        if n in _KEEP_HEADERS or n.startswith(_KEEP_HEADER_PREFIXES):
            out[n] = redact(value)
    return out


def _retry_after_seconds(value: str | None) -> float | None:
    if not value:
        return None
    value = value.strip()
    try:
        return max(0.0, float(value))
    except ValueError:
        pass
    try:
        dt = email.utils.parsedate_to_datetime(value)
    except (TypeError, ValueError):
        return None
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return max(0.0, (dt - datetime.now(timezone.utc)).total_seconds())


def _error_class_for_exception(exc: Exception) -> str:
    if isinstance(exc, httpx.TimeoutException):
        return "timeout"
    if isinstance(exc, httpx.ConnectError):
        return "connect_error"
    if isinstance(exc, httpx.TransportError):
        return "transport_error"
    return type(exc).__name__


# ---------------------------------------------------------------- store


class ResponseStore:
    """Content-addressed body store plus a JSONL index (append-only, cross-process safe)."""

    def __init__(self, root: Path | str) -> None:
        self.root = Path(root)
        if not self.root.is_absolute():
            self.root = repo_root() / self.root
        self.index_path = self.root / "index.jsonl"
        self._lock_path = self.root / ".index.lock"
        self._replay_index: dict[str, dict[str, Any]] | None = None
        self._replay_mtime: float | None = None
        self._mem_lock = threading.Lock()

    @property
    def rel(self) -> str:
        return rel_to_root(self.root)

    def object_path(self, sha: str) -> Path:
        return self.root / "objects" / sha[:2] / sha

    def put_body(self, body: bytes) -> str:
        sha = hashlib.sha256(body).hexdigest()
        path = self.object_path(sha)
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            tmp = path.with_name(f"{sha}.{os.getpid()}.{threading.get_ident()}.tmp")
            tmp.write_bytes(body)
            try:
                os.replace(tmp, path)
            except OSError:
                if not path.exists():
                    raise
                tmp.unlink(missing_ok=True)
        return sha

    def get_body(self, sha: str) -> bytes:
        return self.object_path(sha).read_bytes()

    def append_index(self, row: dict[str, Any]) -> None:
        line = redact(canonical_json(row)) + "\n"
        self.root.mkdir(parents=True, exist_ok=True)
        with FileLock(self._lock_path):
            with open(self.index_path, "a", encoding="utf-8", newline="\n") as fh:
                fh.write(line)
        with self._mem_lock:
            if self._replay_index is not None:
                if row.get("body_sha256"):
                    self._replay_index[row["key_sha256"]] = row
                try:
                    self._replay_mtime = self.index_path.stat().st_mtime
                except OSError:
                    self._replay_mtime = None

    def _load_index(self) -> dict[str, dict[str, Any]]:
        with self._mem_lock:
            try:
                mtime = self.index_path.stat().st_mtime
            except FileNotFoundError:
                mtime = None
            if self._replay_index is not None and mtime == self._replay_mtime:
                return self._replay_index
            index: dict[str, dict[str, Any]] = {}
            if mtime is not None:
                with open(self.index_path, encoding="utf-8") as fh:
                    for line in fh:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            row = json.loads(line)
                        except ValueError:
                            continue
                        if row.get("body_sha256"):
                            index[row["key_sha256"]] = row  # latest row wins
            self._replay_index = index
            self._replay_mtime = mtime
            return index

    def lookup(self, key_sha256: str) -> dict[str, Any] | None:
        return self._load_index().get(key_sha256)

    def rows(self) -> list[dict[str, Any]]:
        """All index rows (including failures), in file order."""
        if not self.index_path.exists():
            return []
        out = []
        with open(self.index_path, encoding="utf-8") as fh:
            for line in fh:
                if line.strip():
                    out.append(json.loads(line))
        return out


# ---------------------------------------------------------------- client


class RecordingClient:
    """Rate-limited, retrying, recording HTTP client shared by all sources.

    Thread-safe. One instance per run is recommended so metrics aggregate.
    """

    def __init__(
        self,
        *,
        mode: str | None = None,
        store_dir: Path | str | None = None,
        rate_limits: dict[str, float] | None = None,
        default_rps: float = DEFAULT_RPS,
        burst: int = 1,
        shared_limiter: bool = True,
        limiter: RateLimiter | None = None,
        timeout: httpx.Timeout | float = DEFAULT_TIMEOUT,
        max_attempts: int = 5,
        backoff_base: float = 1.0,
        backoff_cap: float = 30.0,
        penalty_429: dict[str, float] | None = None,
        tag: str | None = None,
        transport: httpx.BaseTransport | None = None,
        user_agent: str = USER_AGENT,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        load_env()  # registers secrets with the redactor before anything is logged or stored
        self.mode = (mode or default_mode()).lower()
        if self.mode not in MODES:
            raise ValueError(f"mode must be one of {MODES}")
        self.store = ResponseStore(store_dir or default_http_store())
        self._stores: dict[str, ResponseStore] = {str(self.store.root): self.store}
        self.limiter = limiter or RateLimiter(
            rate_limits,
            default_rps=default_rps,
            burst=burst,
            state_dir=ratelimit_state_dir() if shared_limiter else None,
            sleep=sleep,
        )
        self.max_attempts = max(1, max_attempts)
        self.backoff_base = backoff_base
        self.backoff_cap = backoff_cap
        self.penalty_429 = dict(DEFAULT_PENALTY_429)
        if penalty_429:
            self.penalty_429.update(penalty_429)
        self.tag = tag
        self.sleep = sleep
        self.metrics: list[dict[str, Any]] = []
        self._metrics_lock = threading.Lock()
        self._client: httpx.Client | None = None
        self._client_lock = threading.Lock()
        self._timeout = timeout
        self._transport = transport
        self._user_agent = user_agent

    # -- lifecycle --------------------------------------------------
    def _http(self) -> httpx.Client:
        with self._client_lock:
            if self._client is None:
                self._client = httpx.Client(
                    timeout=self._timeout,
                    transport=self._transport,
                    headers={"User-Agent": self._user_agent, "Accept": "application/json"},
                    follow_redirects=True,
                )
            return self._client

    def close(self) -> None:
        if self._client is not None:
            self._client.close()
            self._client = None

    def __enter__(self) -> "RecordingClient":
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    # -- configuration -------------------------------------------------
    def set_rate(self, host: str, rps: float) -> None:
        """Override requests-per-second for a host (0 = unlimited)."""
        self.limiter.set_rate(host, rps)

    def _store_for(self, store_dir: Path | str | None) -> ResponseStore:
        if store_dir is None:
            return self.store
        root = Path(store_dir)
        if not root.is_absolute():
            root = repo_root() / root
        st = self._stores.get(str(root))
        if st is None:
            st = self._stores[str(root)] = ResponseStore(root)
        return st

    # -- public API ----------------------------------------------------
    def get(self, url: str, **kw: Any) -> HttpResult:
        return self.request("GET", url, **kw)

    def post(self, url: str, **kw: Any) -> HttpResult:
        return self.request("POST", url, **kw)

    def request(
        self,
        method: str,
        url: str,
        *,
        params: Mapping[str, Any] | Iterable[tuple[str, Any]] | None = None,
        json: Any = None,
        headers: Mapping[str, str] | None = None,
        secret_headers: Mapping[str, str] | None = None,
        secret_params: Mapping[str, str] | None = None,
        provider: str | None = None,
        endpoint: str | None = None,
        store_dir: Path | str | None = None,
        mode: str | None = None,
        rate_key: str | None = None,
    ) -> HttpResult:
        """Send (or replay) one request and return the final ``HttpResult`` (any status).

        ``secret_headers`` / ``secret_params`` are sent on the wire only; they never enter
        the request key, the index, metrics or logs. ``rate_key`` selects the limiter
        bucket (default: the URL host; e.g. 'api.trongrid.io#key' for keyed TronGrid).
        Raises ``ReplayMiss`` (replay mode, not recorded) or ``RequestFailed`` (no response
        after all attempts). Non-2xx responses are returned, not raised: call
        ``.raise_for_status()``.
        """
        method = method.upper()
        mode = (mode or self.mode).lower()
        parts = urlsplit(url)
        host = (parts.hostname or "").lower()
        provider = provider or host
        endpoint = endpoint or endpoint_template(parts.path)
        rate_key = (rate_key or host).lower()
        store = self._store_for(store_dir)
        key = canonical_request_key(method, url, params, json, provider)
        key_sha = hashlib.sha256(key.encode("utf-8")).hexdigest()
        safe_url = redact(self._display_url(url, params))
        started = time.perf_counter()

        if mode in ("replay", "cache"):
            row = store.lookup(key_sha)
            if row is not None and restricted.is_restricted(row.get("provider")) \
                    and not store.object_path(row["body_sha256"]).is_file():
                # restricted provider body kept out of git (core.restricted): explain instead of a traceback
                if mode == "replay":
                    self._add_metric_raw(provider, endpoint, method, None, 0.0, 0.0, 0.0, 0, 0,
                                         "restricted_body_absent", mode, False, [], rate_key)
                    raise RestrictedBodyMissing(key, store.root, row.get("provider") or provider)
                row = None  # cache mode: treat as not recorded
            if row is not None:
                body = store.get_body(row["body_sha256"])
                result = HttpResult(
                    method=method,
                    url=safe_url,
                    status=int(row["status"]),
                    headers=dict(row.get("headers") or {}),
                    body=body,
                    latency_ms=float(row.get("latency_ms") or 0.0),
                    attempts=int(row.get("attempts") or 1),
                    provider=provider,
                    endpoint=endpoint,
                    from_replay=True,
                    ref=RawRef(store.rel, row["body_sha256"], key_sha),
                    timestamp_utc=row.get("ts_utc", ""),
                    meta={"recorded_tag": row.get("tag")},
                )
                self._add_metric(result, mode=mode, total_ms=(time.perf_counter() - started) * 1000,
                                 rate_wait_ms=0.0, error_class=None if result.ok else f"http_{result.status}",
                                 attempt_statuses=[result.status], rate_key=rate_key)
                return result
            if mode == "replay":
                self._add_metric_raw(provider, endpoint, method, None, 0.0, 0.0, 0.0, 0, 0,
                                     "replay_miss", mode, False, [], rate_key)
                raise ReplayMiss(key, store.root)

        if self._transport is None and _process_in_replay():
            # Safety net: --replay must never reach the real network, even when a client was
            # created with an explicit live/record/cache mode. Injected transports (tests, the
            # synthetic scenario server) are in-process and stay allowed.
            self._add_metric_raw(provider, endpoint, method, None, 0.0, 0.0, 0.0, 0, 0,
                                 "live_request_in_replay", mode, False, [], rate_key)
            raise LiveRequestInReplay(key, store.root, mode)

        return self._send_live(
            method, url, host, rate_key, params, json, headers, secret_headers, secret_params,
            provider, endpoint, store, key, key_sha, safe_url, mode, started,
        )

    # -- internals -----------------------------------------------------
    @staticmethod
    def _display_url(url: str, params: Any) -> str:
        pairs = _param_pairs(params)
        if not pairs:
            return url
        sep = "&" if urlsplit(url).query else "?"
        return url + sep + urlencode(pairs)

    def _backoff(self, attempt: int) -> float:
        base = min(self.backoff_cap, self.backoff_base * (2 ** (attempt - 1)))
        return base * (0.5 + random.random() / 2)

    def _send_live(
        self, method, url, host, rate_key, params, json_body, headers, secret_headers, secret_params,
        provider, endpoint, store, key, key_sha, safe_url, mode, started,
    ) -> HttpResult:
        wire_params = _param_pairs(params) + _param_pairs(secret_params)
        wire_headers = dict(headers or {})
        wire_headers.update(secret_headers or {})
        attempt = 0
        rate_wait = 0.0
        statuses: list[int | None] = []
        last_exc: Exception | None = None
        resp: httpx.Response | None = None
        latency_ms = 0.0
        while True:
            attempt += 1
            rate_wait += self.limiter.acquire(rate_key)
            t0 = time.perf_counter()
            try:
                resp = self._http().request(
                    method,
                    url,
                    params=wire_params or None,
                    json=json_body,
                    headers=wire_headers or None,
                )
                body = resp.content
                latency_ms = (time.perf_counter() - t0) * 1000
                last_exc = None
            except httpx.HTTPError as exc:  # transport level: timeout / connect / protocol
                latency_ms = (time.perf_counter() - t0) * 1000
                last_exc = exc
                resp = None
                statuses.append(None)
                err = _error_class_for_exception(exc)
                log.warning("%s %s -> %s (attempt %d/%d)", method, safe_url, err, attempt, self.max_attempts)
                if attempt < self.max_attempts:
                    self.sleep(self._backoff(attempt))
                    continue
                break
            statuses.append(resp.status_code)
            if resp.status_code in RETRY_STATUSES and attempt < self.max_attempts:
                delay = _retry_after_seconds(resp.headers.get("retry-after"))
                if resp.status_code == 429:
                    delay = max(delay or 0.0, self.penalty_429.get(host, 0.0), self._backoff(attempt))
                    log.warning("%s %s -> 429, backing off %.1fs (attempt %d/%d)",
                                method, safe_url, delay, attempt, self.max_attempts)
                    self.limiter.penalize(rate_key, delay)  # shared: other processes wait too
                else:
                    delay = delay if delay is not None else self._backoff(attempt)
                    log.warning("%s %s -> %d, retry in %.1fs (attempt %d/%d)",
                                method, safe_url, resp.status_code, delay, attempt, self.max_attempts)
                    self.sleep(delay)
                continue
            break

        total_ms = (time.perf_counter() - started) * 1000
        ts = utc_now_iso()
        if resp is None:
            err = _error_class_for_exception(last_exc) if last_exc else "unknown"
            self._add_metric_raw(provider, endpoint, method, None, latency_ms, total_ms, rate_wait * 1000,
                                 attempt, 0, err, mode, False, statuses, rate_key)
            if mode in ("record", "cache"):
                store.append_index(self._index_row(ts, provider, endpoint, method, url, params, json_body,
                                                   key, key_sha, None, {}, None, 0, latency_ms, attempt,
                                                   err, statuses, False))
            raise RequestFailed(
                f"{method} {safe_url}: no response after {attempt} attempts ({err}: {redact(last_exc)})",
                error_class=err,
                attempts=attempt,
            )

        body = resp.content
        body_redacted = False
        if contains_registered_secret(body):
            body = redact_bytes(body)
            body_redacted = True
        kept = _keep_headers(resp.headers)
        ref: RawRef | None = None
        error_class = None if 200 <= resp.status_code < 300 else f"http_{resp.status_code}"
        if mode in ("record", "cache"):
            sha = store.put_body(body)
            ref = RawRef(store.rel, sha, key_sha)
            store.append_index(self._index_row(ts, provider, endpoint, method, url, params, json_body,
                                               key, key_sha, resp.status_code, kept, sha, len(body),
                                               latency_ms, attempt, error_class, statuses, body_redacted))
        result = HttpResult(
            method=method,
            url=safe_url,
            status=resp.status_code,
            headers=kept,
            body=body,
            latency_ms=round(latency_ms, 3),
            attempts=attempt,
            provider=provider,
            endpoint=endpoint,
            from_replay=False,
            ref=ref,
            timestamp_utc=ts,
            meta={"total_ms": round(total_ms, 3), "rate_wait_ms": round(rate_wait * 1000, 3),
                  "attempt_statuses": statuses, "body_redacted": body_redacted},
        )
        self._add_metric(result, mode=mode, total_ms=total_ms, rate_wait_ms=rate_wait * 1000,
                         error_class=error_class, attempt_statuses=statuses, rate_key=rate_key)
        log.debug("%s %s -> %d in %.0f ms (%d attempts)", method, safe_url, resp.status_code, latency_ms, attempt)
        return result

    def _index_row(self, ts, provider, endpoint, method, url, params, json_body, key, key_sha, status,
                   headers, body_sha, size, latency_ms, attempts, error_class, statuses, body_redacted):
        parts = urlsplit(url)
        return {
            "ts_utc": ts,
            "provider": provider,
            "endpoint": endpoint,
            "method": method,
            "url": redact(urlunsplit((parts.scheme, parts.netloc, parts.path, parts.query, ""))),
            "params": [[k, _mask_param(k, v)] for k, v in sorted(_param_pairs(params))],
            "json_body": redact_obj(json_body) if json_body is not None else None,
            "request_key": key,
            "key_sha256": key_sha,
            "status": status,
            "headers": headers,
            "body_sha256": body_sha,
            "size": size,
            "latency_ms": round(latency_ms, 3),
            "attempts": attempts,
            "attempt_statuses": statuses,
            "error_class": error_class,
            "body_redacted": body_redacted,
            "tag": self.tag,
        }

    def _add_metric(self, result: HttpResult, *, mode: str, total_ms: float, rate_wait_ms: float,
                    error_class: str | None, attempt_statuses: list, rate_key: str) -> None:
        self._add_metric_raw(result.provider, result.endpoint, result.method, result.status, result.latency_ms,
                             total_ms, rate_wait_ms, result.attempts, len(result.body), error_class, mode,
                             result.from_replay, attempt_statuses, rate_key)

    def _add_metric_raw(self, provider, endpoint, method, status, latency_ms, total_ms, rate_wait_ms,
                        attempts, nbytes, error_class, mode, from_replay, attempt_statuses, rate_key) -> None:
        row = {
            "ts_utc": utc_now_iso(),
            "provider": redact(provider),
            "endpoint": redact(endpoint),
            "rate_key": redact(rate_key),
            "method": method,
            "status": status,
            "latency_ms": round(latency_ms, 3),
            "total_ms": round(total_ms, 3),
            "rate_wait_ms": round(rate_wait_ms, 3),
            "attempts": attempts,
            "attempt_statuses": attempt_statuses,
            "bytes": nbytes,
            "error_class": error_class,
            "mode": mode,
            "from_replay": from_replay,
            "tag": self.tag,
        }
        with self._metrics_lock:
            self.metrics.append(row)

    # -- metrics output ------------------------------------------------
    def dump_metrics(self, path: Path | str) -> Path:
        """Write all metrics rows as JSONL (redacted) and return the path."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with self._metrics_lock:
            rows = list(self.metrics)
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            for row in rows:
                fh.write(redact(canonical_json(row)) + "\n")
        return path

    def metrics_summary(self) -> list[dict[str, Any]]:
        """Aggregate metrics per (provider, endpoint): count, errors, attempts, p50/p95/max latency, bytes."""
        with self._metrics_lock:
            rows = list(self.metrics)
        groups: dict[tuple[str, str], list[dict[str, Any]]] = {}
        for r in rows:
            groups.setdefault((r["provider"], r["endpoint"]), []).append(r)
        out = []
        for (provider, endpoint), rs in sorted(groups.items()):
            lat = sorted(r["latency_ms"] for r in rs if r["status"] is not None)
            out.append({
                "provider": provider,
                "endpoint": endpoint,
                "requests": len(rs),
                "ok": sum(1 for r in rs if r["error_class"] is None),
                "errors": sum(1 for r in rs if r["error_class"] is not None),
                "error_classes": sorted({r["error_class"] for r in rs if r["error_class"]}),
                "retries": sum(max(0, (r["attempts"] or 1) - 1) for r in rs),
                "http_429_seen": sum(1 for r in rs for s in (r["attempt_statuses"] or []) if s == 429),
                "replayed": sum(1 for r in rs if r["from_replay"]),
                "latency_ms_p50": _percentile(lat, 50),
                "latency_ms_p95": _percentile(lat, 95),
                "latency_ms_max": lat[-1] if lat else None,
                "bytes_total": sum(r["bytes"] or 0 for r in rs),
            })
        return out


def _percentile(sorted_values: list[float], pct: float) -> float | None:
    if not sorted_values:
        return None
    if len(sorted_values) == 1:
        return round(sorted_values[0], 3)
    k = (len(sorted_values) - 1) * pct / 100.0
    lo = int(k)
    hi = min(lo + 1, len(sorted_values) - 1)
    return round(sorted_values[lo] + (sorted_values[hi] - sorted_values[lo]) * (k - lo), 3)
