"""Stage 2 command registry.

Each area lives in its own module ``ledgerhunt.stage2.<name>`` exposing
``run(args: argparse.Namespace) -> int`` (0 = success). Modules are imported lazily,
so a broken module never blocks the others. ``all`` runs them in REGISTRY order.
To add an area: create the module and add one ``Stage2Command`` line below.
"""

from __future__ import annotations

import argparse
import importlib
import traceback
from dataclasses import dataclass

from ..core.http import ReplayMiss
from ..core.redact import redact
from ..core.restricted import absent_reason


@dataclass(frozen=True)
class Stage2Command:
    name: str
    module: str
    title: str
    requires_llm: bool = False  # paid Claude calls: skipped unless --llm
    # HTTP stores whose restricted-provider bodies (core.restricted, kept out of git) the area
    # replays; in a fresh clone they are absent and --replay skips the area with a clear message
    restricted_stores: tuple[str, ...] = ()


# Insertion order is the run order of "stage2 all".
REGISTRY: dict[str, Stage2Command] = {
    c.name: c
    for c in (
        Stage2Command("tron_sources", "ledgerhunt.stage2.tron_sources", "4.1 Источники данных TRON"),
        Stage2Command("bridges", "ledgerhunt.stage2.bridges", "4.2 Мосты и Ethereum",
                      restricted_stores=("data/http-store",)),
        Stage2Command("case001", "ledgerhunt.stage2.case001", "4.5 Эталонный прогон case-001",
                      restricted_stores=("tests/fixtures/case-001/raw/http-store",
                                         "tests/fixtures/case-001/raw/tronscan-pending-consent")),
        Stage2Command("scenarios", "ledgerhunt.stage2.scenarios", "4.6 Тестовые сценарии"),
        Stage2Command("llm_models", "ledgerhunt.stage2.llm_models", "4.4 Модели Claude", requires_llm=True),
        Stage2Command("projection", "ledgerhunt.stage2.projection", "4.3 Расчёт по замерам"),
    )
}


def parse_names(values: list[str] | None) -> list[str] | None:
    """'--only a,b --only c' -> ['a','b','c']; None when --only was not given."""
    if values is None:
        return None
    names: list[str] = []
    for v in values:
        names.extend(n.strip() for n in v.split(",") if n.strip())
    return names


def resolve(target: str, only: list[str] | None) -> list[Stage2Command]:
    """Commands to run for ``stage2 <target> [--only ...]``. 'none' selects nothing."""
    if only is not None:
        if target != "all":
            raise SystemExit("use either 'stage2 <name>' or 'stage2 all --only <names>', not both")
        names = only
    else:
        names = list(REGISTRY) if target == "all" else [target]
    names = [n for n in names if n != "none"]
    unknown = [n for n in names if n not in REGISTRY]
    if unknown:
        raise SystemExit(f"unknown stage2 command(s): {', '.join(unknown)}; known: {', '.join(REGISTRY)}")
    return [REGISTRY[n] for n in names]


def run_commands(cmds: list[Stage2Command], args: argparse.Namespace) -> int:
    """Run each command; return the worst exit code (ReplayMiss -> 3, crash -> 1)."""
    worst = 0
    for cmd in cmds:
        print(f"== stage2 {cmd.name}: {cmd.title}", flush=True)
        if cmd.requires_llm and not getattr(args, "llm", False):
            print(f"[{cmd.name}] пропущено: платные вызовы Claude запускаются только с флагом --llm", flush=True)
            continue
        if cmd.restricted_stores and getattr(args, "http_mode", None) == "replay":
            reason = absent_reason(cmd.restricted_stores)
            if reason:  # fresh clone: bodies kept out of git by the provider's terms
                print(f"[{cmd.name}] пропущено: {reason}", flush=True)
                print(f"== stage2 {cmd.name}: exit 0 (пропущено)", flush=True)
                continue
        try:
            module = importlib.import_module(cmd.module)
            code = int(module.run(args) or 0)
        except ReplayMiss as exc:
            print(f"[{cmd.name}] ОШИБКА replay: {redact(exc)}", flush=True)
            code = 3
        except SystemExit as exc:
            code = exc.code if isinstance(exc.code, int) else 1
        except Exception:  # noqa: BLE001 - one area must not stop the others
            print(f"[{cmd.name}] ОШИБКА:\n{redact(traceback.format_exc())}", flush=True)
            code = 1
        print(f"== stage2 {cmd.name}: exit {code}", flush=True)
        worst = max(worst, code)
    return worst
