"""Configuration and secrets.

Secrets live only in the git-ignored ``.env`` at the repo root (or in real
environment variables, which take precedence: ``.env`` never overrides them).
Every secret value that is loaded is registered with the redactor.

Never print, log or store a secret value. Use ``has_secret`` / ``secrets_presence``
when a result needs to say whether a key was available.
"""

from __future__ import annotations

import os
import re
import threading
from pathlib import Path

from dotenv import dotenv_values

from .paths import repo_root
from .log import get_logger
from .redact import register_secret

log = get_logger(__name__)

ANTHROPIC_API_BASE_URL = "https://api.anthropic.com"

# Known secret variables (documented in .env.example). Whole values are secret.
SECRET_NAMES: tuple[str, ...] = (
    "ANTHROPIC_API_KEY",
    "TRONGRID_API_KEY",
    "TRON_RPC_URL",
    "TRON_RPC_URL_2",
    "TRONSCAN_API_KEY",
    "ETH_RPC_URL",
    "ETHERSCAN_API_KEY",
    "BLOCKSCOUT_API_KEY",
    "NEAR_INTENTS_JWT",
)

# Any other variable whose name looks like this is also treated as a secret.
_SECRET_NAME_RE = re.compile(r"(KEY|TOKEN|SECRET|PASSWORD|PASS|JWT|DSN|_RPC_URL|_RPC_URL_\d+)$", re.IGNORECASE)

_lock = threading.Lock()
_loaded = False
_dotenv: dict[str, str] = {}  # values from .env, kept private (NOT copied into os.environ)


def is_secret_name(name: str) -> bool:
    return name in SECRET_NAMES or bool(_SECRET_NAME_RE.search(name))


def env_file_path() -> Path:
    return repo_root() / ".env"


def load_env(force: bool = False) -> None:
    """Load ``.env`` once and register every secret value with the redactor.

    Real environment variables take precedence (``.env`` never overrides them).
    Secret values from ``.env`` stay in this module and are NOT exported to
    ``os.environ``, so child processes and SDKs that read the environment on their
    own (e.g. anthropic.Anthropic() with the host's ANTHROPIC_BASE_URL) never see
    them. Only non-secret ``LEDGERHUNT_*`` settings are exported.
    """
    global _loaded
    with _lock:
        if _loaded and not force:
            return
        path = env_file_path()
        _dotenv.clear()
        if path.is_file():
            for name, value in dotenv_values(path).items():
                if value is not None:
                    _dotenv[name] = value
        for name, value in _dotenv.items():
            if name.startswith("LEDGERHUNT_") and not is_secret_name(name) and name not in os.environ:
                os.environ[name] = value
        # Register every secret-looking value, whether it came from .env or the real environment.
        for name in set(_dotenv) | set(SECRET_NAMES):
            if is_secret_name(name):
                register_secret(_lookup(name))
        # Defensive: also mask long secret-looking values present in the host environment.
        for name, value in os.environ.items():
            if is_secret_name(name):
                register_secret(value, min_len=12)
        _loaded = True


def _lookup(name: str) -> str | None:
    if name in os.environ:  # real environment wins, even when set to an empty string
        return os.environ[name]
    return _dotenv.get(name)


def get_secret(name: str) -> str | None:
    """Return the secret value or None. The value must never be printed, logged or stored."""
    load_env()
    value = _lookup(name)
    if value is None:
        return None
    value = value.strip()
    if not value:
        return None
    register_secret(value)
    return value


def has_secret(name: str) -> bool:
    """True when the secret is set and non-empty."""
    return get_secret(name) is not None


def get_setting(name: str, default: str | None = None) -> str | None:
    """Non-secret setting (e.g. LEDGERHUNT_LOG_LEVEL). Do not use for keys."""
    load_env()
    value = _lookup(name)
    return value if value not in (None, "") else default


def secrets_presence(names: tuple[str, ...] | list[str] | None = None) -> dict[str, bool]:
    """Map of secret name -> present (bool). Safe to write into results."""
    load_env()
    names = tuple(names) if names is not None else SECRET_NAMES
    extra = sorted(n for n in _dotenv if is_secret_name(n) and n not in names)
    return {n: has_secret(n) for n in (*names, *extra)}


class MissingSecretError(RuntimeError):
    """Raised when a required secret is not configured."""


def require_secret(name: str) -> str:
    value = get_secret(name)
    if value is None:
        raise MissingSecretError(
            f"Secret {name} is not set. Add it to the git-ignored .env at the repo root "
            f"(see .env.example) or to the process environment."
        )
    return value


def make_anthropic_client(**kwargs):
    """Return ``anthropic.Anthropic`` bound to the official API endpoint.

    ``ANTHROPIC_BASE_URL`` from the host environment is ignored on purpose:
    base_url is always https://api.anthropic.com. The key comes from
    ANTHROPIC_API_KEY (.env or environment); passing it explicitly also stops
    the SDK from picking up ANTHROPIC_AUTH_TOKEN. Raises MissingSecretError
    if the key is absent. Extra kwargs (timeout, max_retries, ...) go to the SDK.
    """
    import anthropic

    api_key = require_secret("ANTHROPIC_API_KEY")
    kwargs.pop("base_url", None)
    kwargs.pop("api_key", None)
    kwargs.pop("auth_token", None)
    if os.environ.get("ANTHROPIC_CUSTOM_HEADERS"):
        log.warning("ANTHROPIC_CUSTOM_HEADERS is set in the environment; the SDK will merge those headers")
    return anthropic.Anthropic(api_key=api_key, base_url=ANTHROPIC_API_BASE_URL, **kwargs)
