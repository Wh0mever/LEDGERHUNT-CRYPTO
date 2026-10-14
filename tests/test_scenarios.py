"""Tests of the synthetic scenario generator, raw formats, scorer and committed sets.

No network, no keys. The held-out set is only hashed here (its content is never parsed).
"""

from __future__ import annotations

import copy
import json
from pathlib import Path

import httpx
import pytest

from ledgerhunt.core.evm import keccak256
from ledgerhunt.core.http import RecordingClient
from ledgerhunt.core.ratelimit import RateLimiter
from ledgerhunt.scenarios import formats as F
from ledgerhunt.scenarios import generator as G
from ledgerhunt.scenarios.__main__ import main as scenarios_cli
from ledgerhunt.scenarios.case001_ref import FIXTURE, build_case001
from ledgerhunt.scenarios.schema import ScenarioInput, TraceResult
from ledgerhunt.scenarios.scorer import aggregate, candidate_from_expected, score_scenario, wilson
from ledgerhunt.scenarios.server import ScenarioServer
from ledgerhunt.scenarios.sets import file_hashes, scenarios_root, tree_digest, verify_holdout
from ledgerhunt.scenarios.templates import CATEGORIES
from ledgerhunt.scenarios.validate import validate_scenario
from ledgerhunt.sources import TronGridClient

TEST_SEED = "pytest/scenarios"

# Public chain data of the case-001 theft transaction (98f3ffca...), as returned by
# TronGrid /wallet/gettransactionbyid on 2026-10-14.
THEFT_RAW = {
    "ref_block_bytes": "f5bf", "ref_block_hash": "794feb956ebd111f", "expiration": 1790026356000,
    "contract": [{"parameter": {"value": {
        "owner_address": "TNakrL7VUMLNN4EEpi64HKjj5YqafR5tUx",
        "contract_address": "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t",
        "data": "a9059cbb000000000000000000000041f49e7307ff8215c54450c072bf6d926af59faef5"
                "000000000000000000000000000000000000000000000000000000030953fbc4"},
        "type_url": "type.googleapis.com/protocol.TriggerSmartContract"}, "type": "TriggerSmartContract"}],
    "timestamp": 1789990356000, "fee_limit": 13046000,
}
THEFT_RAW_HEX = (
    "0a02f5bf2208794feb956ebd111f40a0aa8aaf8c345aae01081f12a9010a31747970652e676f6f676c65617069732e636f6d2f70726f"
    "746f636f6c2e54726967676572536d617274436f6e747261637412740a15418a5aa79a2fd854dc565225ef05570c2c7ec8707f121541"
    "a614f803b6fd780986a42c78ec9c7f77e6ded13c2244a9059cbb000000000000000000000041f49e7307ff8215c54450c072bf6d926af5"
    "9faef5000000000000000000000000000000000000000000000000000000030953fbc470a088f59d8c349001f0a19c06"
)
THEFT_TXID = "98f3ffca9d141f2172d28f46905c08e5f32fc6ce8d23f9a37b731fe2a6c1d1bb"


def _item(category: str, variant: str, sid: str = "t-001") -> dict:
    idx = [n for n, _ in CATEGORIES[category]].index(variant)
    return {"scenario_id": sid, "category": category, "variant_index": idx, "variant": variant}


def _build(category: str, variant: str):
    inp, world, expected = G.build("dev", TEST_SEED, _item(category, variant))
    return inp, world, TraceResult.model_validate(expected)


def _limiter() -> RateLimiter:
    return RateLimiter({"api.trongrid.io": 0}, default_rps=0, state_dir=None)


# ---------------------------------------------------------------- formats vs real data


def test_protobuf_reproduces_real_theft_transaction():
    raw = F.encode_raw_data(THEFT_RAW)
    assert raw.hex() == THEFT_RAW_HEX
    assert F.txid_of(raw) == THEFT_TXID


def test_layerzero_guid_payload_and_topics_match_real_send():
    sender = F.USDT0_OFT_TRON_HEX[2:].rjust(64, "0")
    receiver = F.USDT0_OFT_ETH_ADAPTER[2:].rjust(64, "0")
    guid = F.oft_guid(23381, 30420, sender, 30101, receiver)
    assert guid == "ba20537a6870e4ba2538d40ae16772f198f02d88d24c47d016b53863a7337bf8"
    msg = F.oft_message("0x4079047990917f3150353fbd8a13b05b6286926d", 12901408416)
    assert msg == "00020000000000000000000000004079047990917f3150353fbd8a13b05b6286926d0000000300fbdea0"
    assert F.lz_payload_hash(guid, msg) == "0xa5164bf0284a8fc7e2b08dcbe8a7b8a7d43adb98b06694d284797619cf329f11"
    assert F.topic(F.SIG_OFTSENT) == "85496b760a4b7f8d66384b9df21b381f5d1b1e79f229a47aaf4c232edc2fe59a"
    assert F.topic(F.SIG_PACKETSENT) == "1ab700d4ced0c005b164c0f789fd09fcbb0156d4c2041b8a3bfbcd961cd1567f"
    assert F.topic(F.SIG_TRANSFER) == keccak256("Transfer(address,address,uint256)").hex()


# ---------------------------------------------------------------- generator


def test_plan_counts_and_split_independence():
    dev = G.plan("dev", G.DEV_SEED)
    assert len(dev) == 54 and len({d["scenario_id"] for d in dev}) == 54
    by_cat = {c: sum(1 for d in dev if d["category"] == c) for c in CATEGORIES}
    assert len(by_cat) == 9 and min(by_cat.values()) >= 5
    hold = G.plan("holdout", "another-seed")
    assert len(hold) == 27 and all(d["scenario_id"].startswith("hold-") for d in hold)


def test_generation_is_deterministic_and_replayable(tmp_path):
    item = _item("bridge", "case001_like")
    hashes = []
    for run in ("a", "b"):
        inp, world, expected = G.build("dev", TEST_SEED, item)
        G.write_scenario(tmp_path / run / "t-001", inp, world, expected, tag="pytest")
        hashes.append(tree_digest(file_hashes(tmp_path / run)))
    assert hashes[0] == hashes[1]
    res = validate_scenario(tmp_path / "a" / "t-001")
    assert res["ok"], res["errors"]


def test_server_serves_other_query_shapes(tmp_path):
    _inp, world, _exp = G.build("dev", TEST_SEED, _item("long_chain", "relay"))
    server = ScenarioServer(world)
    http = RecordingClient(mode="live", store_dir=tmp_path / "s", limiter=_limiter(), transport=server.transport(),
                           max_attempts=1, sleep=lambda s: None)
    tg = TronGridClient(http, api_key=None)
    addr = world.addresses()[0]
    full = tg.trc20_transfers(addr, limit=200)
    small = tg.trc20_transfers(addr, limit=1, order_by="block_timestamp,desc")
    assert small.complete and len(small.pages) == len(full.rows)
    assert [r["transaction_id"] for r in small.rows] == [r["transaction_id"] for r in reversed(full.rows)]


def test_input_is_neutral():
    inp, _world, expected = _build("exchange", "fast_forwarder")
    text = json.dumps(inp)
    assert "fast_forwarder" not in text and "exchange" not in json.dumps(inp["start"])
    ScenarioInput.model_validate(inp)
    assert expected.meta["category"] == "exchange"


# ---------------------------------------------------------------- scorer


def test_perfect_answer_scores_100_percent():
    _inp, world, exp = _build("fan_out", "one_percent")
    s = score_scenario(exp, candidate_from_expected(exp), world)
    assert s.passed and s.routes_found == s.routes_expected
    agg = aggregate([s])
    assert agg["fact_recall"] == 1.0 and agg["fact_precision"] == 1.0 and agg["facts_false"] == 0


def test_one_invented_fact_fails_the_scenario():
    _inp, world, exp = _build("direct", "hops_energy_fee")
    cand = candidate_from_expected(exp).model_copy(deep=True)
    fake = cand.transfers[-1].model_copy(update={"txid": "ab" * 32, "event_index": 0})
    cand.transfers.append(fake)
    s = score_scenario(exp, cand, world)
    assert not s.passed and len(s.false_facts) == 1
    assert s.routes_found == s.routes_expected  # all routes found, still fails: one false fact


def test_wrong_amount_and_missing_route():
    _inp, world, exp = _build("fan_out", "split_k")
    cand = candidate_from_expected(exp).model_copy(deep=True)
    cand.transfers[0] = cand.transfers[0].model_copy(update={"amount": "1.000000"})
    s = score_scenario(exp, cand, world)
    assert not s.passed and s.counts["false_matched"] == 1
    cand2 = candidate_from_expected(exp).model_copy(deep=True)
    cand2.routes = cand2.routes[1:]
    s2 = score_scenario(exp, cand2, world)
    assert not s2.passed and s2.missed_routes and not s2.false_facts


def test_commingled_uncertainty_rules():
    _inp, world, exp = _build("merge", "prefunded_hub")
    base = candidate_from_expected(exp)
    outflow = exp.allowed.transfers[0]
    ok = base.model_copy(deep=True)
    ok.transfers.append(outflow.model_copy(update={"taint": "uncertain"}))
    assert score_scenario(exp, ok, world).passed  # continuing with uncertainty is allowed
    bad = base.model_copy(deep=True)
    bad.transfers.append(outflow.model_copy(update={"taint": "traced"}))
    assert not score_scenario(exp, bad, world).passed  # exact attribution after commingling is false
    bad2 = base.model_copy(deep=True)
    bad2.merges[0] = bad2.merges[0].model_copy(update={"attribution": "exact"})
    assert not score_scenario(exp, bad2, world).passed


def test_traps_are_false_facts():
    _inp, world, exp = _build("incomplete_data", "poisoning")
    trap = next(t for t in exp.traps if t.reason == "zero_value_poisoning")
    tx = world.tx(trap.txid)
    ev = tx["events"][0]["args"]
    cand = candidate_from_expected(exp).model_copy(deep=True)
    cand.transfers.append(cand.transfers[0].model_copy(update={
        "txid": trap.txid, "event_index": 0, "from_address": ev["from"], "to_address": ev["to"], "amount": "0.000000"}))
    s = score_scenario(exp, cand, world)
    assert not s.passed and "trap" in s.false_facts[0].detail
    # the same poisoning row reported as context (taint none) is true and neutral
    ctx = candidate_from_expected(exp).model_copy(deep=True)
    ctx.transfers.append(cand.transfers[-1].model_copy(update={"taint": "none"}))
    assert score_scenario(exp, ctx, world).passed


def test_source_outage_is_excluded_from_denominator_and_reported():
    _inp, world, exp = _build("source_failure", "listing_503")
    assert exp.outages and any(t.excluded for t in exp.transfers)
    s = score_scenario(exp, candidate_from_expected(exp), world)
    assert s.passed and s.affected_by_unavailability and s.counts["excluded"] > 0
    _i2, w2, normal = _build("direct", "single")
    s_normal = score_scenario(normal, candidate_from_expected(normal), w2)
    agg = aggregate([s, s_normal])
    assert agg["scenarios_counted"] == 1 and agg["scenarios_with_source_failure"] == 1
    assert agg["source_failure_scenarios_handled"] == 1 and agg["facts_excluded_unavailable"] > 0
    # a candidate that does not report the outage misses the limitation fact but is not false
    silent = candidate_from_expected(exp).model_copy(deep=True)
    silent.limitations = []
    s_silent = score_scenario(exp, silent, world)
    assert s_silent.counts["missed"] >= 1


def test_false_unavailability_and_false_confirmation():
    _inp, world, exp = _build("direct", "single")
    cand = candidate_from_expected(exp).model_copy(deep=True)
    cand.limitations.append(cand.limitations[0] if cand.limitations else
                            __import__("ledgerhunt.scenarios.schema", fromlist=["Limitation"]).Limitation(
                                source_role="tron_index", target=cand.transfers[0].to_address, limitation="unavailable"))
    assert not score_scenario(exp, cand, world).passed  # claims an outage that did not happen
    assert score_scenario(exp, cand, world, trust_candidate_outages=True).passed
    _i, w3, sec = _build("source_failure", "secondary_down")
    c3 = candidate_from_expected(sec).model_copy(deep=True)
    c3.transfers[0] = c3.transfers[0].model_copy(update={"verification": "second_source_confirmed"})
    assert not score_scenario(sec, c3, w3).passed  # confirmation without the second source
    weak = candidate_from_expected(exp).model_copy(deep=True)
    weak.transfers[0] = weak.transfers[0].model_copy(update={"verification": "unverified"})
    s_weak = score_scenario(exp, weak, world)
    assert s_weak.passed and s_weak.counts["weaker"] == 1  # weaker claim: not false, not counted correct


def test_route_continuing_past_commingled_hub_still_matches():
    _inp, world, exp = _build("merge", "prefunded_hub")
    cand = candidate_from_expected(exp).model_copy(deep=True)
    out = exp.allowed.transfers[0]
    r = cand.routes[0]
    cand.routes = [r.model_copy(update={"txids": r.txids + [out.txid],
                                        "terminal": r.terminal.model_copy(update={"address": out.to_address,
                                                                                  "reason": "funds_at_rest"})})]
    cand.transfers.append(out.model_copy(update={"taint": "uncertain"}))
    s = score_scenario(exp, cand, world)
    assert s.routes_found == s.routes_expected and s.passed


def test_wilson_interval():
    lo, hi = wilson(50, 50)
    assert 0.92 < lo < 0.93 and hi == 1.0


# ---------------------------------------------------------------- committed sets


def _manifest(split: str) -> dict:
    p = scenarios_root() / split / "manifest.json"
    if not p.is_file():
        pytest.skip(f"{split} set not generated")
    return json.loads(p.read_text(encoding="utf-8"))


def test_committed_dev_set_matches_manifest():
    m = _manifest("dev")
    assert m["synthetic_scenarios"] >= 50 and min(m["by_category"].values()) >= 5 and len(m["by_category"]) >= 9
    current = file_hashes(scenarios_root() / "dev")
    assert current == m["files"]
    assert "case-001/expected.json" in m["files"]


def test_holdout_integrity_by_hash_only():
    m = _manifest("holdout")
    assert m["synthetic_scenarios"] >= 20 and "scenarios" not in m and "seed" not in m
    assert not any("case-001" in k for k in m["files"])
    res = verify_holdout(regenerate=False)
    if res.get("content") == "absent":  # git has only README.md and manifest.json; the set is with the owners
        pytest.skip(res["message"])
    assert res["integrity_ok"], {k: v for k, v in res.items() if k != "tree_sha256"}


def test_holdout_absent_content_is_skipped_not_failed(tmp_path):
    """A clone without the held-out content: the check is skipped with a message; a partial copy fails."""
    root = tmp_path / "scenarios"
    hdir = root / "holdout"
    (hdir / "hold-001").mkdir(parents=True)
    (hdir / "hold-001" / "expected.json").write_text("{}", encoding="utf-8")
    (hdir / "hold-002").mkdir()
    (hdir / "hold-002" / "expected.json").write_text("[]", encoding="utf-8")
    (hdir / "seed.txt").write_text("unit-seed\n", encoding="utf-8")
    files = file_hashes(hdir)
    manifest = {"synthetic_scenarios": 2, "by_category": {"direct": 2}, "files": files,
                "tree_sha256": tree_digest(files), "seed_sha256": G.seed_digest("unit-seed")}
    (hdir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    copy_dir = tmp_path / "owners-copy"
    copy_dir.mkdir()
    for rel in files:
        (copy_dir / rel).parent.mkdir(parents=True, exist_ok=True)
        (copy_dir / rel).write_bytes((hdir / rel).read_bytes())
    ok = verify_holdout(root, regenerate=False)
    assert ok["present"] and ok["integrity_ok"]
    for rel in files:  # the content leaves the repository, the manifest stays
        (hdir / rel).unlink()
    absent = verify_holdout(root, regenerate=False)
    assert absent["present"] is False and absent["content"] == "absent"
    assert absent["message"] == "отложенный набор у владельцев, проверка по манифесту пропущена"
    assert absent["manifest_synthetic_scenarios"] == 2
    copy = verify_holdout(root, regenerate=False, content_dir=copy_dir)  # the owners' copy, checked elsewhere
    assert copy["present"] and copy["integrity_ok"] and copy["files_matching"] == copy["files_listed"] == 2
    (copy_dir / "hold-002" / "expected.json").unlink()
    partial = verify_holdout(root, regenerate=False, content_dir=copy_dir)
    assert partial["present"] and not partial["integrity_ok"] and partial["files_missing"] == 1


def test_holdout_scoring_requires_owner_flag(tmp_path):
    _manifest("holdout")
    assert scenarios_cli(["score", "--split", "holdout", "--candidates", str(tmp_path)]) == 2


def test_case001_reference_points_to_fixture():
    inp, expected = build_case001()
    ScenarioInput.model_validate(inp)
    exp = TraceResult.model_validate(expected)
    assert inp["reference"]["fixture"] == FIXTURE and inp["reference"]["counts_toward_metrics"] is False
    assert exp.routes[0].txids[0] == "98f3ffca9d141f2172d28f46905c08e5f32fc6ce8d23f9a37b731fe2a6c1d1bb"
    assert exp.routes[0].terminal.address == "TYHeH2HQn7pM5fe6aYwGabz9x4yizJbwp6"
    s = score_scenario(exp, candidate_from_expected(exp))
    assert s.passed
