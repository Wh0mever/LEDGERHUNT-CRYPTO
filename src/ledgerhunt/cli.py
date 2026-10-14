"""Command line: ``python -m ledgerhunt <command>``.

Commands
  stage2 <name>|all [--only a,b] [--llm] [--replay] [--http-mode MODE] [-- extra args]
  env              print versions, machine profile and which secrets are present (booleans)
  probe-sources    confirm every source endpoint with a few keyless case-001 requests (recorded)
"""

from __future__ import annotations

import argparse
import json
import os
import sys

from . import __version__
from .core.config import load_env, secrets_presence
from .core.http import MODES
from .core.log import setup_logging
from .core.redact import redact


def _configure_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            if not stream.isatty():
                stream.reconfigure(encoding="utf-8", errors="replace")
            else:
                stream.reconfigure(errors="replace")
        except (AttributeError, ValueError):
            pass


def build_parser() -> argparse.ArgumentParser:
    from .stage2 import REGISTRY

    p = argparse.ArgumentParser(prog="python -m ledgerhunt", description="LEDGERHUNT-CRYPTO Stage 2 harness")
    p.add_argument("--version", action="version", version=f"ledgerhunt {__version__}")
    p.add_argument("--log-level", default=os.environ.get("LEDGERHUNT_LOG_LEVEL", "INFO"))
    sub = p.add_subparsers(dest="command", required=True)

    s2 = sub.add_parser("stage2", help="run Stage 2 measurement areas")
    s2.add_argument("target", choices=[*REGISTRY, "all"], help="area name or 'all'")
    s2.add_argument("--only", action="append", default=None,
                    help="comma-separated area names (with 'all'); 'none' runs nothing (smoke check)")
    s2.add_argument("--llm", action="store_true", help="allow paid Claude API calls (llm_models)")
    s2.add_argument("--replay", action="store_true",
                    help="offline: serve every HTTP request from recorded raw responses; fail on a miss")
    s2.add_argument("--http-mode", choices=MODES, default=None,
                    help="HTTP mode for this run (default: record; --replay forces replay)")

    sub.add_parser("env", help="print environment facts (no secret values)")

    pr = sub.add_parser("probe-sources", help="confirm source endpoints with keyless case-001 probes")
    pr.add_argument("--replay", action="store_true", help="serve probes from recorded responses")
    return p


def cmd_env() -> int:
    from .core.machine import machine_profile
    from .core.results import git_info, package_versions

    out = {
        "ledgerhunt": __version__,
        "python": sys.version.split()[0],
        "packages": package_versions(),
        "git": git_info(),
        "machine": machine_profile(),
        "secrets_present": secrets_presence(),
        "http_mode": os.environ.get("LEDGERHUNT_HTTP_MODE", "record"),
        "anthropic_base_url_used_by_project": "https://api.anthropic.com",
    }
    print(redact(json.dumps(out, ensure_ascii=False, indent=2)))
    return 0


def main(argv: list[str] | None = None) -> int:
    _configure_stdio()
    load_env()
    parser = build_parser()
    args, extra = parser.parse_known_args(argv)
    setup_logging(args.log_level)
    args.extra = extra

    if args.command == "env":
        if extra:
            parser.error(f"unrecognized arguments: {' '.join(extra)}")
        return cmd_env()

    if args.command == "probe-sources":
        if extra:
            parser.error(f"unrecognized arguments: {' '.join(extra)}")
        if args.replay:
            os.environ["LEDGERHUNT_HTTP_MODE"] = "replay"
        from .probe_sources import run as run_probes

        return run_probes(args)

    if args.command == "stage2":
        from .stage2 import parse_names, resolve, run_commands

        mode = "replay" if args.replay else (args.http_mode or os.environ.get("LEDGERHUNT_HTTP_MODE") or "record")
        if args.replay and args.http_mode not in (None, "replay"):
            parser.error("--replay conflicts with --http-mode " + args.http_mode)
        os.environ["LEDGERHUNT_HTTP_MODE"] = mode
        args.http_mode = mode
        if args.llm:
            os.environ["LEDGERHUNT_LLM_ENABLED"] = "1"
        args.only = parse_names(args.only)
        cmds = resolve(args.target, args.only)
        print(f"ledgerhunt {__version__}: stage2 {args.target} | http mode: {mode} | llm: {args.llm} | "
              f"areas: {', '.join(c.name for c in cmds) or '(none)'}", flush=True)
        if not cmds:
            presence = secrets_presence()
            print("secrets present: " + ", ".join(f"{k}={'yes' if v else 'no'}" for k, v in presence.items()))
            print("smoke check OK: package imports, registry resolves, nothing selected to run")
            return 0
        return run_commands(cmds, args)

    parser.error("unknown command")
    return 2
