"""Scenario sets on disk: regeneration, manifests with sha256 hashes, held-out protection.

tests/scenarios/
    schema/                         JSON Schemas of input.json and result files
    dev/                            development set (seed DEV_SEED) + case-001 reference
        manifest.json               counts, categories, sha256 of every file
        <dev-NNN>/ ...              one directory per scenario
        case-001/                   reference scenario pointing to tests/fixtures/case-001
    holdout/                        held-out set (different seed) - NOT for development
        README.md                   rules (Russian)
        manifest.json               counts and sha256 of every file; no id->category map
        seed.txt                    holdout seed
                                    (only README.md and manifest.json are in git; the scenarios and
                                    seed.txt are kept by the owners, see holdout/README.md)
        <hold-NNN>/ ...

The held-out set is created once (``create_holdout``) and never rewritten by a normal run:
``verify_holdout`` only re-hashes the files and, when the seed is available, regenerates
the set into a temporary directory and compares hashes. Reports about the held-out set
contain counts and hashes only.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import secrets
import shutil
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any

from ..core.paths import repo_root
from . import generator as G
from .case001_ref import write_case001
from .schema import json_schemas

MANIFEST_SCHEMA = "ledgerhunt.scenario-manifest/1"
COUNTING_RULES = [
    "Fact accuracy is counted per fact (transfer, route stop, exchange deposit, bridge exit, merge, limitation).",
    "A scenario passes only if all expected routes are found and there is no false fact.",
    "Source unavailability is excluded from the denominator but counted and reported separately: facts behind a "
    "designed outage or index gap leave the fact denominators; scenarios with a designed source failure leave the "
    "pass-rate denominator and are reported on their own line.",
    "case-001 is a development reference and is never part of the held-out set.",
]
_SCENARIO_DIR = re.compile(r"^(dev|hold)-\d{3}$")
HOLDOUT_ABSENT_MESSAGE = "отложенный набор у владельцев, проверка по манифесту пропущена"


def scenarios_root() -> Path:
    return repo_root() / "tests" / "scenarios"


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def file_hashes(split_dir: Path) -> dict[str, str]:
    out = {}
    for p in sorted(split_dir.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(split_dir).as_posix()
        if rel in ("manifest.json",) or rel.endswith(".lock"):
            continue
        out[rel] = sha256_file(p)
    return out


def tree_digest(hashes: dict[str, str]) -> str:
    return hashlib.sha256("".join(f"{k} {v}\n" for k, v in sorted(hashes.items())).encode()).hexdigest()


def _write_json(p: Path, obj: Any) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")


def write_schemas(root: Path) -> None:
    for name, schema in json_schemas().items():
        _write_json(root / "schema" / name, schema)


def _sync_dir(src: Path, dst: Path) -> None:
    """Replace generated scenario directories in ``dst`` with those from ``src`` (only dev-/hold- dirs)."""
    dst.mkdir(parents=True, exist_ok=True)
    for d in dst.iterdir():
        if d.is_dir() and _SCENARIO_DIR.match(d.name) and not (src / d.name).exists():
            shutil.rmtree(d)
    for d in sorted(src.iterdir()):
        if not d.is_dir():
            continue
        target = dst / d.name
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(d, target)


def build_manifest(split: str, split_dir: Path, rows: list[dict[str, Any]], *, seed: str) -> dict[str, Any]:
    hashes = file_hashes(split_dir)
    cats = Counter(r["category"] for r in rows)
    m: dict[str, Any] = {
        "schema": MANIFEST_SCHEMA,
        "split": split,
        "generator": G.GENERATOR_VERSION,
        "request_profile": G.REQUEST_PROFILE,
        "synthetic_scenarios": len(rows),
        "by_category": dict(sorted(cats.items())),
        "counting_rules": COUNTING_RULES,
        "files_count": len(hashes),
        "bytes_total": sum((split_dir / k).stat().st_size for k in hashes),
        "tree_sha256": tree_digest(hashes),
        "files": hashes,
    }
    if split == "dev":
        m["seed"] = seed
        m["scenarios"] = [{"scenario_id": r["scenario_id"], "category": r["category"], "variant": r["variant"]}
                          for r in rows]
        m["reference_scenarios"] = ["case-001"]
    else:
        m["seed_sha256"] = G.seed_digest(seed)
        m["notice"] = "Held-out set: not for development or tuning. See README.md."
    return m


def regenerate_dev(root: Path | None = None) -> dict[str, Any]:
    root = root or scenarios_root()
    dev_dir = root / "dev"
    old = _load_manifest(dev_dir)
    with tempfile.TemporaryDirectory(prefix="lh-dev-") as tmp:
        rows = G.generate_split("dev", G.DEV_SEED, Path(tmp))
        _sync_dir(Path(tmp), dev_dir)
    write_case001(dev_dir / "case-001")
    write_schemas(root)
    manifest = build_manifest("dev", dev_dir, rows, seed=G.DEV_SEED)
    _write_json(dev_dir / "manifest.json", manifest)
    return {"rows": rows, "manifest": manifest,
            "changed_vs_previous": None if old is None else old.get("tree_sha256") != manifest["tree_sha256"]}


def _load_manifest(split_dir: Path) -> dict[str, Any] | None:
    p = split_dir / "manifest.json"
    if not p.is_file():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def holdout_seed(root: Path | None = None, *, holdout_dir: Path | None = None) -> str | None:
    env = os.environ.get("LEDGERHUNT_HOLDOUT_SEED")
    if env:
        return env.strip()
    p = (holdout_dir or (root or scenarios_root()) / "holdout") / "seed.txt"
    return p.read_text(encoding="utf-8").strip() if p.is_file() else None


def create_holdout(root: Path | None = None, *, seed: str | None = None, force: bool = False) -> dict[str, Any]:
    """Create the held-out set once. Refuses to overwrite an existing set unless ``force``."""
    root = root or scenarios_root()
    hdir = root / "holdout"
    if (hdir / "manifest.json").exists() and not force:
        raise FileExistsError("held-out set already exists; it is never rewritten by a normal run")
    seed = seed or f"ledgerhunt/scenarios/holdout/{secrets.token_hex(16)}"
    with tempfile.TemporaryDirectory(prefix="lh-hold-") as tmp:
        rows = G.generate_split("holdout", seed, Path(tmp))
        _sync_dir(Path(tmp), hdir)
    (hdir / "seed.txt").write_text(seed + "\n", encoding="utf-8", newline="\n")
    manifest = build_manifest("holdout", hdir, rows, seed=seed)
    _write_json(hdir / "manifest.json", manifest)
    return {"scenarios": len(rows), "by_category": manifest["by_category"], "tree_sha256": manifest["tree_sha256"]}


def verify_holdout(root: Path | None = None, *, regenerate: bool = True,
                   content_dir: Path | None = None) -> dict[str, Any]:
    """Hash check of the held-out set (no parsing of its content) and, if the seed is known,
    a regeneration into a temporary directory compared hash-by-hash. Returns counts only.

    The committed ``holdout/manifest.json`` is the reference. ``content_dir`` checks a copy kept
    elsewhere (e.g. the owners' archive unpacked to a temporary directory) against it. When none of
    the listed files is present (the content is kept by the owners, only README.md and
    manifest.json are in git), the check is skipped: ``content == "absent"``, not a failure.
    """
    root = root or scenarios_root()
    hdir = root / "holdout"
    manifest = _load_manifest(hdir)
    if manifest is None:
        return {"present": False}
    cdir = Path(content_dir) if content_dir is not None else hdir
    current = file_hashes(cdir) if cdir.is_dir() else {}
    current.pop("seed.txt", None)
    current.pop("README.md", None)
    listed = dict(manifest["files"])
    listed.pop("seed.txt", None)
    listed.pop("README.md", None)
    if not any(k in current for k in listed):
        return {
            "present": False,
            "content": "absent",
            "message": HOLDOUT_ABSENT_MESSAGE,
            "manifest_synthetic_scenarios": manifest["synthetic_scenarios"],
            "files_listed": len(listed),
            "tree_sha256": manifest["tree_sha256"],
        }
    out: dict[str, Any] = {
        "present": True,
        "synthetic_scenarios": manifest["synthetic_scenarios"],
        "by_category": manifest["by_category"],
        "files_listed": len(listed),
        "files_matching": sum(1 for k, v in listed.items() if current.get(k) == v),
        "files_missing": sum(1 for k in listed if k not in current),
        "files_unlisted": sum(1 for k in current if k not in listed),
        "tree_sha256": manifest["tree_sha256"],
    }
    out["integrity_ok"] = out["files_matching"] == out["files_listed"] and not out["files_unlisted"]
    seed = holdout_seed(root, holdout_dir=cdir)
    if not regenerate or seed is None:
        out["regeneration"] = "skipped: seed not available" if seed is None else "skipped"
        return out
    if G.seed_digest(seed) != manifest.get("seed_sha256"):
        out["regeneration"] = "skipped: seed does not match manifest"
        return out
    with tempfile.TemporaryDirectory(prefix="lh-hold-check-") as tmp:
        G.generate_split("holdout", seed, Path(tmp))
        regen = file_hashes(Path(tmp))
    same = sum(1 for k, v in listed.items() if regen.get(k) == v)
    out["regeneration"] = "identical" if same == len(listed) and len(regen) == len(listed) else "differs"
    out["regenerated_files_matching"] = same
    return out
