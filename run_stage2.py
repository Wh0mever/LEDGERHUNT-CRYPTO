#!/usr/bin/env python3
"""Stage 2: the single command.

    python run_stage2.py [--only a,b] [--llm] [--replay] [--reinstall] [extra args...]

1. creates .venv next to this file if it is missing (needs Python >= 3.12);
2. installs the package in editable mode with dev extras, pinned by requirements.lock
   (skipped when pyproject.toml and requirements.lock did not change since the last install);
3. runs ``python -m ledgerhunt stage2 all`` inside .venv, passing the flags through.

--only none   runs nothing (smoke check of install + registry).
--llm         allows the paid Claude benchmark (llm_models).
--replay      offline: every HTTP request is served from recorded raw responses; a miss fails.
Works the same from PowerShell, cmd and Git Bash. Standard library only.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VENV = ROOT / ".venv"
STAMP = VENV / ".ledgerhunt-install.sha256"
MIN_PY = (3, 12)


def venv_python() -> Path:
    if os.name == "nt":
        return VENV / "Scripts" / "python.exe"
    return VENV / "bin" / "python"


def ensure_venv() -> Path:
    py = venv_python()
    if py.exists():
        return py
    if sys.version_info < MIN_PY:
        sys.exit(f"Python >= {MIN_PY[0]}.{MIN_PY[1]} is required to create .venv (found {sys.version.split()[0]})")
    print(f"[run_stage2] creating virtual environment in {VENV.name}/", flush=True)
    subprocess.run([sys.executable, "-m", "venv", str(VENV)], check=True)
    if not py.exists():
        sys.exit(f"venv creation failed: {py} not found")
    return py


def install_digest() -> str:
    h = hashlib.sha256()
    for name in ("pyproject.toml", "requirements.lock"):
        p = ROOT / name
        h.update(name.encode())
        h.update(p.read_bytes() if p.exists() else b"")
    return h.hexdigest()


def ensure_installed(py: Path, force: bool) -> None:
    digest = install_digest()
    if not force and STAMP.exists() and STAMP.read_text(encoding="utf-8").strip() == digest:
        return
    cmd = [str(py), "-m", "pip", "install", "--disable-pip-version-check", "-e", ".[dev]"]
    lock = ROOT / "requirements.lock"
    if lock.exists():
        cmd[4:4] = ["-c", str(lock)]
    print("[run_stage2] installing ledgerhunt (editable, dev extras, pinned by requirements.lock)", flush=True)
    subprocess.run(cmd, cwd=ROOT, check=True)
    STAMP.write_text(digest + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="LEDGERHUNT-CRYPTO Stage 2 single command")
    p.add_argument("--only", action="append", default=None, help="comma-separated areas; 'none' = smoke check")
    p.add_argument("--llm", action="store_true", help="allow paid Claude API calls")
    p.add_argument("--replay", action="store_true", help="offline replay of recorded HTTP responses")
    p.add_argument("--reinstall", action="store_true", help="force pip install even if nothing changed")
    p.add_argument("--no-install", action="store_true", help="skip venv creation/installation checks")
    args, rest = p.parse_known_args(argv)

    py = venv_python() if args.no_install else ensure_venv()
    if args.no_install and not py.exists():
        sys.exit(f"--no-install: {py} not found; run once without --no-install to create .venv")
    if not args.no_install:
        ensure_installed(py, args.reinstall)

    cmd = [str(py), "-m", "ledgerhunt", "stage2", "all"]
    if args.only:
        cmd += ["--only", ",".join(args.only)]
    if args.llm:
        cmd.append("--llm")
    if args.replay:
        cmd.append("--replay")
    cmd += rest
    env = os.environ.copy()
    env.setdefault("PYTHONIOENCODING", "utf-8")
    env.pop("PYTHONHOME", None)
    return subprocess.call(cmd, cwd=ROOT, env=env)


if __name__ == "__main__":
    sys.exit(main())
