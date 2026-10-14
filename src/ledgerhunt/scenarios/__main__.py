"""Command line for the scenario sets.

  python -m ledgerhunt.scenarios generate                 regenerate the development set (+ case-001, schemas)
  python -m ledgerhunt.scenarios create-holdout [--seed S] [--out DIR]
                                                          owners only: create a held-out set once
  python -m ledgerhunt.scenarios verify-holdout [--dir D] hash check against tests/scenarios/holdout/manifest.json
                                                          (+ regeneration check when the seed is known); D = a copy
                                                          kept elsewhere (unpacked owners' archive)
  python -m ledgerhunt.scenarios validate [--split dev]   structural validation (holdout: counts only)
  python -m ledgerhunt.scenarios score --split dev --candidates DIR [--out FILE]
         [--trust-candidate-outages] [--owner-final-evaluation]
         DIR holds <scenario_id>.json candidate results (schema ledgerhunt.scenario-result/1).
         Scoring the held-out split requires --owner-final-evaluation.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .schema import TraceResult
from .scorer import aggregate, score_scenario
from .sets import create_holdout, regenerate_dev, scenarios_root, verify_holdout
from .validate import validate_scenario
from .world import World


def _scenario_dirs(split_dir: Path) -> list[Path]:
    return sorted(d for d in split_dir.iterdir() if d.is_dir() and (d / "expected.json").is_file())


def cmd_score(args: argparse.Namespace) -> int:
    if args.split == "holdout" and not args.owner_final_evaluation:
        print("refused: the held-out split is scored only in the owners' final evaluation "
              "(--owner-final-evaluation)", file=sys.stderr)
        return 2
    split_dir = scenarios_root() / args.split
    cand_dir = Path(args.candidates)
    scores = []
    for d in _scenario_dirs(split_dir):
        exp = TraceResult.model_validate(json.loads((d / "expected.json").read_text(encoding="utf-8")))
        if (exp.meta or {}).get("counts_toward_metrics") is False:
            continue  # case-001 reference
        world = World.load(d / "world.json") if (d / "world.json").is_file() else None
        cf = cand_dir / f"{d.name}.json"
        if cf.is_file():
            cand = TraceResult.model_validate(json.loads(cf.read_text(encoding="utf-8")))
        else:
            cand = TraceResult(scenario_id=d.name)
        scores.append(score_scenario(exp, cand, world, trust_candidate_outages=args.trust_candidate_outages))
    report = {"split": args.split, "aggregate": aggregate(scores),
              "scenarios": [s.to_dict(details=args.split == "dev") for s in scores]}
    text = json.dumps(report, ensure_ascii=False, indent=1)
    if args.out:
        Path(args.out).write_text(text + "\n", encoding="utf-8")
    print(json.dumps(report["aggregate"], ensure_ascii=False, indent=1))
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="python -m ledgerhunt.scenarios")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("generate")
    ch = sub.add_parser("create-holdout")
    ch.add_argument("--seed", default=None)
    ch.add_argument("--out", default=None, help="scenarios root to write <root>/holdout into (default tests/scenarios)")
    vh = sub.add_parser("verify-holdout")
    vh.add_argument("--dir", default=None, help="held-out copy to check (default tests/scenarios/holdout)")
    va = sub.add_parser("validate")
    va.add_argument("--split", choices=["dev", "holdout"], default="dev")
    sc = sub.add_parser("score")
    sc.add_argument("--split", choices=["dev", "holdout"], default="dev")
    sc.add_argument("--candidates", required=True)
    sc.add_argument("--out", default=None)
    sc.add_argument("--trust-candidate-outages", action="store_true")
    sc.add_argument("--owner-final-evaluation", action="store_true")
    args = p.parse_args(argv)

    if args.cmd == "generate":
        res = regenerate_dev()
        print(json.dumps({"dev_scenarios": len(res["rows"]), "tree_sha256": res["manifest"]["tree_sha256"],
                          "changed_vs_previous": res["changed_vs_previous"]}, indent=1))
        return 0
    if args.cmd == "create-holdout":
        root = Path(args.out) if args.out else None
        print(json.dumps(create_holdout(root, seed=args.seed), indent=1))
        return 0
    if args.cmd == "verify-holdout":
        res = verify_holdout(content_dir=Path(args.dir) if args.dir else None)
        print(json.dumps(res, ensure_ascii=False, indent=1))
        if res.get("content") == "absent":
            print(res["message"], file=sys.stderr)
            return 0 if args.dir is None else 1  # an explicitly given copy must contain the set
        return 0 if res.get("integrity_ok", False) and res.get("regeneration") != "differs" else 1
    if args.cmd == "validate":
        dirs = _scenario_dirs(scenarios_root() / args.split)
        results = [validate_scenario(d) for d in dirs]
        bad = [r for r in results if not r["ok"]]
        if args.split == "dev":
            for r in bad:
                print(r["scenario_id"], r["errors"][:5])
        print(json.dumps({"split": args.split, "scenarios": len(results), "ok": len(results) - len(bad),
                          "failed": len(bad)}, indent=1))
        return 0 if not bad else 1
    if args.cmd == "score":
        return cmd_score(args)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
