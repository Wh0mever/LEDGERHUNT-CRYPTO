"""Minimal cross-process exclusive file lock (Windows: msvcrt, POSIX: fcntl)."""

from __future__ import annotations

import os
import threading
import time
from pathlib import Path

if os.name == "nt":  # pragma: no cover - platform specific
    import msvcrt
else:  # pragma: no cover - platform specific
    import fcntl

_thread_locks: dict[str, threading.Lock] = {}
_thread_locks_guard = threading.Lock()


def _thread_lock(path: Path) -> threading.Lock:
    key = str(path)
    with _thread_locks_guard:
        lock = _thread_locks.get(key)
        if lock is None:
            lock = _thread_locks[key] = threading.Lock()
        return lock


class FileLock:
    """Exclusive lock on ``path`` (created if missing). Use as a context manager."""

    def __init__(self, path: Path | str, timeout: float = 60.0, poll: float = 0.005) -> None:
        self.path = Path(path)
        self.timeout = timeout
        self.poll = poll
        self._fd: int | None = None
        self._tlock = _thread_lock(self.path)

    def __enter__(self) -> "FileLock":
        self._tlock.acquire()
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            fd = os.open(str(self.path), os.O_RDWR | os.O_CREAT, 0o644)
            deadline = time.monotonic() + self.timeout
            while True:
                try:
                    if os.name == "nt":
                        os.lseek(fd, 0, os.SEEK_SET)
                        msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
                    else:
                        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    break
                except OSError:
                    if time.monotonic() > deadline:
                        os.close(fd)
                        raise TimeoutError(f"could not lock {self.path} within {self.timeout}s")
                    time.sleep(self.poll)
            self._fd = fd
            return self
        except BaseException:
            self._tlock.release()
            raise

    def __exit__(self, *exc: object) -> None:
        fd = self._fd
        self._fd = None
        try:
            if fd is not None:
                try:
                    if os.name == "nt":
                        os.lseek(fd, 0, os.SEEK_SET)
                        msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
                    else:
                        fcntl.flock(fd, fcntl.LOCK_UN)
                finally:
                    os.close(fd)
        finally:
            self._tlock.release()
