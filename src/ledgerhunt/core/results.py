"""Measurement run records under results/stage-2/<area>/<run_id>/.

Every run directory gets:
- config.json   : date, git commit, Python and package versions, machine profile,
                  secrets present (booleans only), redacted command line, the exact
                  reproduce command, HTTP mode/store and the caller's config
- <raw files>   : whatever the area writes (JSONL/JSON/text), all redacted
- http-metrics.jsonl / http-summary.json : per-request metrics of clients created
                  with ``RunContext.http_client`` (written by ``finish``)
- summary.json / summary.md
and results/stage-2/<area>/latest.json points at the newest finished run.
"""

from __future__ import annotations

import dataclasses
import hashlib
import importlib.metadata as md
import json
import os
import platform
import shlex
import subprocess
import sys
from datetime import date, datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any, Iterable

from .config import secrets_presence
from .machine import machine_profile
from .paths import rel_to_root, repo_root, results_root
from .redact import redact

TRACKED_PACKAGES = (
    "ledgerhunt",
    "httpx",
    "anthropic",
    "pydantic",
    "python-dotenv",
    "base58",
    "pycryptodome",
    "pillow",
    "pytest",
)


# ---------------------------------------------------------------- JSON


def json_default(obj: Any) -> Any:
    """JSON encoder fallback: Decimal -> str (amounts stay exact), Path -> POSIX, datetime -> ISO."""
    if isinstance(obj, Decimal):
        return format(obj, "f")
    if isinstance(obj, Path):
        return obj.as_posix()
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, bytes):
        return obj.hex()
    if isinstance(obj, (set, frozenset)):
        return sorted(obj, key=str)
    if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
        return dataclasses.asdict(obj)
    if hasattr(obj, "to_dict"):
        return obj.to_dict()
    if hasattr(obj, "model_dump"):
        return obj.model_dump(mode="json")
    raise TypeError(f"not JSON serializable: {type(obj).__name__}")


def dumps(obj: Any, *, indent: int | None = 2) -> str:
    """Redacted JSON text (UTF-8, Decimal as string)."""
    return redact(json.dumps(obj, ensure_ascii=False, indent=indent, default=json_default))


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


# ---------------------------------------------------------------- environment facts


def git_info() -> dict[str, Any]:
    def run(*args: str) -> str | None:
        try:
            return subprocess.run(
                ["git", *args], cwd=repo_root(), capture_output=True, text=True, timeout=15, check=True
            ).stdout.strip()
        except (OSError, subprocess.SubprocessError):
            return None

    status = run("status", "--porcelain")
    return {
        "commit": run("rev-parse", "HEAD"),
        "branch": run("rev-parse", "--abbrev-ref", "HEAD"),
        "dirty": bool(status) if status is not None else None,
        "dirty_paths": len(status.splitlines()) if status else 0,
    }


SOURCE_DIGEST_PATHS = ("src/ledgerhunt", "run_stage2.py", "pyproject.toml", "requirements.lock")


def source_digest() -> dict[str, Any]:
    """sha256 over the harness source (relative path + content hash of each file, sorted).

    Ties a result to its code even when the run happened on an uncommitted working tree
    (git.dirty = true): recompute it on a checkout and compare. Line endings are
    normalised to LF (the repository stores text as LF, see .gitattributes).
    """
    root = repo_root()
    h = hashlib.sha256()
    n = 0
    for rel in SOURCE_DIGEST_PATHS:
        p = root / rel
        if p.is_dir():
            files = sorted((f for f in p.rglob("*") if f.is_file() and "__pycache__" not in f.parts),
                           key=lambda f: f.relative_to(root).as_posix())  # same order on every OS
        else:
            files = [p] if p.is_file() else []
        for f in files:
            data = f.read_bytes().replace(b"\r\n", b"\n")
            h.update(f.relative_to(root).as_posix().encode("utf-8") + b"\0" + hashlib.sha256(data).digest())
            n += 1
    return {"sha256": h.hexdigest(), "files": n, "paths": list(SOURCE_DIGEST_PATHS)}


def package_versions(names: Iterable[str] = TRACKED_PACKAGES) -> dict[str, str | None]:
    out: dict[str, str | None] = {}
    for n in names:
        try:
            out[n] = md.version(n)
        except md.PackageNotFoundError:
            out[n] = None
    return out


def _safe_argv(argv: list[str]) -> list[str]:
    """argv with the repo root stripped, 'python -m ledgerhunt' restored and secrets redacted."""
    root = str(repo_root())
    out = []
    for i, a in enumerate(argv):
        if i == 0:
            norm = a.replace("\\", "/")
            if norm.endswith("ledgerhunt/__main__.py") or norm.endswith("/ledgerhunt") or norm == "ledgerhunt":
                out.extend(["python", "-m", "ledgerhunt"])
                continue
            out.append("python")
        a = a.replace(root + os.sep, "").replace(root, ".")
        out.append(redact(a))
    return out


# ---------------------------------------------------------------- run context


class RunContext:
    """One measurement run. Create with ``start_run``; finish with ``finish``."""

    def __init__(self, area: str, run_dir: Path, run_id: str, started: datetime, config: dict[str, Any]) -> None:
        self.area = area
        self.dir = run_dir
        self.run_id = run_id
        self.started = started
        self.config = config
        self._clients: list[Any] = []
        self.finished = False

    # -- paths / writers --------------------------------------------------
    @property
    def rel_dir(self) -> str:
        return rel_to_root(self.dir)

    def path(self, name: str) -> Path:
        p = self.dir / name
        p.parent.mkdir(parents=True, exist_ok=True)
        return p

    def write_json(self, name: str, obj: Any) -> Path:
        p = self.path(name)
        p.write_text(dumps(obj) + "\n", encoding="utf-8", newline="\n")
        return p

    def write_jsonl(self, name: str, rows: Iterable[Any]) -> Path:
        p = self.path(name)
        with open(p, "w", encoding="utf-8", newline="\n") as fh:
            for row in rows:
                fh.write(dumps(row, indent=None) + "\n")
        return p

    def append_jsonl(self, name: str, row: Any) -> Path:
        p = self.path(name)
        with open(p, "a", encoding="utf-8", newline="\n") as fh:
            fh.write(dumps(row, indent=None) + "\n")
        return p

    def write_text(self, name: str, text: str) -> Path:
        p = self.path(name)
        p.write_text(redact(text), encoding="utf-8", newline="\n")
        return p

    # -- HTTP -----------------------------------------------------------------
    def http_client(self, **kwargs: Any):
        """A RecordingClient tagged '<area>/<run_id>'; its metrics are dumped by ``finish``."""
        from .http import RecordingClient

        kwargs.setdefault("tag", f"{self.area}/{self.run_id}")
        client = RecordingClient(**kwargs)
        self._clients.append(client)
        # http.mode stays the run's mode (set by start_run); a secondary client created with an
        # explicit mode (e.g. the live-only load phase) must not relabel a record/replay run.
        http_cfg = self.config.setdefault("http", {})
        http_cfg.setdefault("mode", client.mode)
        http_cfg.setdefault("store", client.store.rel)
        for key, value in (("client_modes", client.mode), ("stores", client.store.rel)):
            values = http_cfg.setdefault(key, [])
            if value not in values:
                values.append(value)
        self._write_config()
        return client

    def track_client(self, client: Any) -> Any:
        """Register an externally created RecordingClient so ``finish`` dumps its metrics."""
        self._clients.append(client)
        return client

    # -- lifecycle ------------------------------------------------------------
    def _write_config(self) -> None:
        self.write_json("config.json", self.config)

    def write_summary(self, summary: dict[str, Any], markdown: str | None = None) -> None:
        self.write_json("summary.json", summary)
        if markdown is not None:
            self.write_text("summary.md", markdown)

    def finish(self, summary: dict[str, Any] | None = None, markdown: str | None = None,
               status: str = "ok") -> Path:
        """Dump HTTP metrics, write summary.json/.md, stamp config.json and update latest.json."""
        metrics_rows = []
        http_summary = []
        for client in self._clients:
            metrics_rows.extend(client.metrics)
            http_summary.extend(client.metrics_summary())
        if self._clients:
            self.write_jsonl("http-metrics.jsonl", metrics_rows)
            self.write_json("http-summary.json", http_summary)
        finished = utc_now()
        self.config["finished_utc"] = finished.strftime("%Y-%m-%dT%H:%M:%SZ")
        self.config["status"] = status
        self.config["duration_s"] = round((finished - self.started).total_seconds(), 3)
        self._write_config()
        if summary is not None or markdown is not None:
            self.write_summary(summary or {}, markdown)
        latest = {
            "area": self.area,
            "run_id": self.run_id,
            "path": self.rel_dir,
            "finished_utc": self.config["finished_utc"],
            "status": status,
            "http_mode": (self.config.get("http") or {}).get("mode"),
        }
        (self.dir.parent / "latest.json").write_text(dumps(latest) + "\n", encoding="utf-8", newline="\n")
        self.finished = True
        return self.dir


def start_run(
    area: str,
    *,
    config: dict[str, Any] | None = None,
    argv: list[str] | None = None,
    reproduce: str | None = None,
    root: Path | None = None,
) -> RunContext:
    """Create results/stage-2/<area>/<YYYYMMDDTHHMMSSZ>/ and write config.json.

    ``config`` is the area's own configuration (redacted before writing).
    ``reproduce`` is the exact command that repeats the run; defaults to
    ``python run_stage2.py --only <area>`` (+ ``--replay`` when in replay mode).
    """
    if not area or any(c in area for c in r'\/:*?"<>|'):
        raise ValueError(f"bad area name: {area!r}")
    started = utc_now()
    base = (root or results_root()) / area
    run_id = started.strftime("%Y%m%dT%H%M%SZ")
    run_dir = base / run_id
    n = 1
    while True:
        try:
            run_dir.mkdir(parents=True, exist_ok=False)
            break
        except FileExistsError:
            n += 1
            run_dir = base / f"{run_id}-{n}"
    run_id = run_dir.name
    mode = os.environ.get("LEDGERHUNT_HTTP_MODE", "record")
    if reproduce is None:
        reproduce = f"python run_stage2.py --only {area}" + (" --replay" if mode == "replay" else "")
    argv = list(sys.argv if argv is None else argv)
    cfg: dict[str, Any] = {
        "area": area,
        "run_id": run_id,
        "started_utc": started.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "date_utc": started.strftime("%Y-%m-%d"),
        "git": git_info(),
        "source": source_digest(),
        "python": {"version": platform.python_version(), "implementation": platform.python_implementation()},
        "packages": package_versions(),
        "machine": machine_profile(),
        "secrets_present": secrets_presence(),
        "command": " ".join(shlex.quote(a) for a in _safe_argv(argv)),
        "reproduce": reproduce,
        "http": {"mode": mode},
        "config": config or {},
    }
    ctx = RunContext(area, run_dir, run_id, started, cfg)
    ctx._write_config()
    return ctx


def latest_run_dir(area: str, root: Path | None = None) -> Path | None:
    """Directory of the newest finished run of ``area`` (from latest.json), or None."""
    p = (root or results_root()) / area / "latest.json"
    if not p.is_file():
        return None
    data = json.loads(p.read_text(encoding="utf-8"))
    return repo_root() / data["path"]
