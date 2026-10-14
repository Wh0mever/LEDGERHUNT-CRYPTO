"""Repository-relative paths used across the package."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path


@lru_cache(maxsize=1)
def repo_root() -> Path:
    """Return the repository root.

    Order: env LEDGERHUNT_ROOT; the nearest parent of this file that holds
    pyproject.toml; the current working directory.
    """
    env = os.environ.get("LEDGERHUNT_ROOT")
    if env:
        return Path(env).resolve()
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "pyproject.toml").is_file() and (parent / "src" / "ledgerhunt").is_dir():
            return parent
    return Path.cwd().resolve()


def results_root() -> Path:
    """results/stage-2 under the repo root."""
    return repo_root() / "results" / "stage-2"


def default_http_store() -> Path:
    """Default content-addressed store for raw HTTP responses (env LEDGERHUNT_HTTP_STORE overrides)."""
    env = os.environ.get("LEDGERHUNT_HTTP_STORE")
    if env:
        p = Path(env)
        return p if p.is_absolute() else repo_root() / p
    return repo_root() / "data" / "http-store"


def ratelimit_state_dir() -> Path:
    """Directory holding the cross-process rate limiter state (git-ignored .cache/)."""
    env = os.environ.get("LEDGERHUNT_RATELIMIT_DIR")
    if env:
        return Path(env)
    return repo_root() / ".cache" / "ratelimit"


def rel_to_root(path: Path) -> str:
    """Path relative to the repo root in POSIX form when possible, else absolute POSIX."""
    try:
        return Path(path).resolve().relative_to(repo_root()).as_posix()
    except ValueError:
        return Path(path).resolve().as_posix()
