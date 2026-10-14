"""Test isolation: no network, no real keys, temp stores and results."""

from __future__ import annotations

import pytest

from ledgerhunt.core import redact as redact_mod


@pytest.fixture(autouse=True)
def _isolate(monkeypatch, tmp_path):
    # Keep shared limiter state and the HTTP store out of the repo during tests.
    monkeypatch.setenv("LEDGERHUNT_RATELIMIT_DIR", str(tmp_path / "ratelimit"))
    monkeypatch.setenv("LEDGERHUNT_HTTP_STORE", str(tmp_path / "http-store"))
    monkeypatch.setenv("LEDGERHUNT_HTTP_MODE", "record")
    yield
    redact_mod.clear_registered_secrets()
