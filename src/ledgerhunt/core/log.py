"""Logging with mandatory redaction of secrets."""

from __future__ import annotations

import logging
import sys
import threading
import traceback

from .redact import redact


class RedactingFormatter(logging.Formatter):
    """Formats a record normally, then passes the whole line through ``redact``."""

    def format(self, record: logging.LogRecord) -> str:
        return redact(super().format(record))


class RedactingFilter(logging.Filter):
    """Redacts msg/args in place so any handler (including pytest caplog) sees clean text."""

    def filter(self, record: logging.LogRecord) -> bool:
        try:
            message = record.getMessage()
        except Exception:  # noqa: BLE001 - malformed args; keep original
            return True
        record.msg = redact(message)
        record.args = ()
        return True


_configured = False


def setup_logging(level: str | int = "INFO") -> None:
    """Install a redacting stderr handler on the root logger (idempotent)."""
    global _configured
    root = logging.getLogger()
    if isinstance(level, str):
        level = getattr(logging, level.upper(), logging.INFO)
    root.setLevel(level)
    if not _configured:
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(RedactingFormatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
        handler.addFilter(RedactingFilter())
        root.addHandler(handler)
        for name in ("ledgerhunt", "httpx", "httpcore", "anthropic"):
            logging.getLogger(name).addFilter(RedactingFilter())
        # httpx logs full request URLs at INFO; keep it quiet, our client logs redacted URLs itself.
        logging.getLogger("httpx").setLevel(logging.WARNING)
        logging.getLogger("httpcore").setLevel(logging.WARNING)
        _configured = True


def get_logger(name: str) -> logging.Logger:
    """Logger under the 'ledgerhunt' namespace with the redacting filter attached."""
    logger = logging.getLogger(name if name.startswith("ledgerhunt") else f"ledgerhunt.{name}")
    if not any(isinstance(f, RedactingFilter) for f in logger.filters):
        logger.addFilter(RedactingFilter())
    return logger


_factory_lock = threading.Lock()
_factory_installed = False


def install_redacting_record_factory() -> None:
    """Redact every log record of every logger (incl. httpx, which logs full URLs) at creation.

    Message text and exception text are redacted before any handler sees them, so even
    handlers we do not control (pytest caplog, basicConfig) never receive a secret.
    Idempotent; installed on import of this module.
    """
    global _factory_installed
    with _factory_lock:
        if _factory_installed:
            return
        previous = logging.getLogRecordFactory()

        def factory(*args, **kwargs):
            record = previous(*args, **kwargs)
            try:
                record.msg = redact(record.getMessage())
                record.args = ()
            except Exception:  # noqa: BLE001 - never break logging
                return record
            if record.exc_info and record.exc_info[0] is not None and not record.exc_text:
                text = "".join(traceback.format_exception(*record.exc_info))
                record.exc_text = redact(text.rstrip("\n"))
            return record

        logging.setLogRecordFactory(factory)
        _factory_installed = True


install_redacting_record_factory()
