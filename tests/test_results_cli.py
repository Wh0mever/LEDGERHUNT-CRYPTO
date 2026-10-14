import json
import os
from decimal import Decimal
from pathlib import Path

import pytest

from ledgerhunt import cli
from ledgerhunt.core import config
from ledgerhunt.core.redact import register_secret
from ledgerhunt.core.results import start_run
from ledgerhunt.stage2 import REGISTRY, resolve

FAKE = "fake-results-secret-9a8b7c6d5e4f"


def test_start_run_writes_config_and_latest(tmp_path):
    register_secret(FAKE)
    run = start_run("unit-area", config={"token_note": FAKE, "n": 1}, argv=["prog", f"--x={FAKE}"], root=tmp_path)
    cfg = json.loads((run.dir / "config.json").read_text(encoding="utf-8"))
    for key in ("date_utc", "git", "source", "packages", "machine", "secrets_present", "command", "reproduce", "python"):
        assert key in cfg
    assert len(cfg["source"]["sha256"]) == 64 and cfg["source"]["files"] > 10
    assert all(isinstance(v, bool) for v in cfg["secrets_present"].values())
    run.write_jsonl("raw.jsonl", [{"amount": Decimal("13041.400772")}])
    run.append_jsonl("raw.jsonl", {"amount": Decimal("0.000001")})
    run.finish({"ok": True, "secret": FAKE}, "# итог\n" + FAKE)
    text = "".join(p.read_text(encoding="utf-8") for p in run.dir.iterdir() if p.is_file())
    assert FAKE not in text
    rows = [json.loads(line) for line in (run.dir / "raw.jsonl").read_text(encoding="utf-8").splitlines()]
    assert rows == [{"amount": "13041.400772"}, {"amount": "0.000001"}]  # Decimal -> string, never float
    latest = json.loads((tmp_path / "unit-area" / "latest.json").read_text(encoding="utf-8"))
    assert latest["run_id"] == run.run_id and latest["status"] == "ok"
    assert (run.dir / "summary.md").exists()


def test_secondary_live_client_does_not_relabel_run_mode(tmp_path, monkeypatch):
    monkeypatch.setenv("LEDGERHUNT_HTTP_MODE", "record")
    run = start_run("unit-area", root=tmp_path, argv=["prog"])
    run.http_client(store_dir=tmp_path / "store")
    run.http_client(mode="live", store_dir=tmp_path / "store", max_attempts=1)  # e.g. a live-only load phase
    run.finish({"ok": True})
    cfg = json.loads((run.dir / "config.json").read_text(encoding="utf-8"))
    assert cfg["http"]["mode"] == "record"
    assert cfg["http"]["client_modes"] == ["record", "live"]
    latest = json.loads((tmp_path / "unit-area" / "latest.json").read_text(encoding="utf-8"))
    assert latest["http_mode"] == "record"


def test_registry_has_six_areas_and_resolve():
    assert set(REGISTRY) == {"case001", "bridges", "llm_models", "scenarios", "tron_sources", "projection"}
    assert resolve("all", ["none"]) == []
    assert [c.name for c in resolve("all", ["case001", "bridges"])] == ["case001", "bridges"]
    with pytest.raises(SystemExit):
        resolve("all", ["nope"])


def _stub_registry(monkeypatch, calls, behaviour=None):
    """Replace every registered area with an in-memory stub module.

    The real areas write into results/stage-2 of the working tree; a unit test must not
    (an earlier version of this test ran them and left replay-miss runs behind).
    """
    import sys
    import types

    from ledgerhunt import stage2
    from ledgerhunt.core.http import ReplayMiss

    behaviour = behaviour or {}
    stubs = {}
    for name, cmd in stage2.REGISTRY.items():
        mod = types.ModuleType(f"_ledgerhunt_test_stub_{name}")

        def run(args, _name=name):
            calls.append((_name, args.http_mode, os.environ.get("LEDGERHUNT_HTTP_MODE")))
            if behaviour.get(_name) == "miss":
                raise ReplayMiss("stub GET https://example.invalid/x", Path("."))
            return 0

        mod.run = run
        monkeypatch.setitem(sys.modules, mod.__name__, mod)
        stubs[name] = stage2.Stage2Command(name, mod.__name__, cmd.title, cmd.requires_llm)
    monkeypatch.setattr(stage2, "REGISTRY", stubs)


def test_cli_stage2_all_replay_dispatch(monkeypatch, capsys):
    calls = []
    _stub_registry(monkeypatch, calls)
    code = cli.main(["stage2", "all", "--replay"])
    out = capsys.readouterr().out
    assert code == 0
    ran = [c[0] for c in calls]
    assert "llm_models" not in ran and len(ran) == 5  # paid area skipped without --llm
    assert "--llm" in out
    assert all(mode == "replay" and env == "replay" for _, mode, env in calls)
    assert os.environ["LEDGERHUNT_HTTP_MODE"] == "replay"


def test_cli_stage2_replay_miss_exit_code(monkeypatch, capsys):
    calls = []
    _stub_registry(monkeypatch, calls, behaviour={"bridges": "miss"})
    code = cli.main(["stage2", "all", "--replay"])
    out = capsys.readouterr().out
    assert code == 3  # a replay miss is reported, never silently served live
    assert "replay" in out and "bridges" in out
    assert len(calls) == 5  # the other areas still ran


def test_cli_only_none_smoke(capsys):
    assert cli.main(["stage2", "all", "--only", "none"]) == 0
    assert "smoke check OK" in capsys.readouterr().out


def test_make_anthropic_client_ignores_base_url_env(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_BASE_URL", "http://127.0.0.1:9/should-not-be-used")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-fake-unit-test-key")
    client = config.make_anthropic_client()
    assert str(client.base_url).rstrip("/") == "https://api.anthropic.com"
    monkeypatch.setenv("ANTHROPIC_API_KEY", "")
    with pytest.raises(config.MissingSecretError):
        config.make_anthropic_client()
