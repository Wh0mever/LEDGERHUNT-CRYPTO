"""case-001: the deterministic reference run replayed from recorded raw responses, without network.

The raw responses live in tests/fixtures/case-001/raw/http-store (recorded by
``python -m ledgerhunt stage2 case001``). The expected output is
tests/fixtures/case-001/raw/expected/reference-run.json (``--update-expected`` rewrites it).

The LayerZero Scan and 1Click bodies are kept out of git by the providers' terms
(ledgerhunt.core.restricted). In a fresh clone they are absent and these tests are skipped
with that reason; where the bodies exist (the recording machine) everything runs. A partly
missing set is not skipped: it fails.
"""

from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path

import httpx
import pytest

from ledgerhunt.baseline.fetch import CaseSources
from ledgerhunt.baseline.tracer import ReferenceTracer, semantic_view
from ledgerhunt.core.http import RecordingClient
from ledgerhunt.core.restricted import absent_message, store_status

FIXTURE = Path(__file__).parent / "fixtures" / "case-001"
RAW = FIXTURE / "raw"
STORE = RAW / "http-store"
EXPECTED = RAW / "expected" / "reference-run.json"
THEFT_TXID = "98f3ffca9d141f2172d28f46905c08e5f32fc6ce8d23f9a37b731fe2a6c1d1bb"


class _NoNetwork(httpx.BaseTransport):
    def handle_request(self, request: httpx.Request) -> httpx.Response:
        raise AssertionError(f"network access attempted in a replay test: {request.method} {request.url.host}")


@pytest.fixture(scope="module")
def replayed():
    if not (STORE / "index.jsonl").is_file():
        pytest.skip("raw fixture store not recorded yet")
    restricted = store_status(STORE)
    if restricted.all_absent:  # fresh clone: bodies not in git by the providers' terms
        pytest.skip(f"{absent_message(restricted.providers)}: тела ответов отсутствуют в {restricted.store} "
                    f"(0 из {restricted.listed}); полный повтор case-001 — на машине владельцев")
    http = RecordingClient(mode="replay", store_dir=STORE, shared_limiter=False, transport=_NoNetwork())
    src = CaseSources(http, trongrid_api_key=None)
    out = ReferenceTracer(src).run(THEFT_TXID)
    return out, http


@pytest.fixture(scope="module")
def fixture_json():
    return json.loads((FIXTURE / "case-001-ground-truth.json").read_text(encoding="utf-8"))


def test_replay_uses_only_recorded_responses(replayed):
    _, http = replayed
    assert http.metrics, "the reference run made no requests"
    assert all(m["from_replay"] for m in http.metrics)
    assert all(m["error_class"] != "replay_miss" for m in http.metrics)


def test_replay_matches_stored_expected_output(replayed):
    out, _ = replayed
    expected = json.loads(EXPECTED.read_text(encoding="utf-8"))
    got = semantic_view(out)
    assert got["meta"] == expected["meta"]
    for key in expected["result"]:
        assert got["result"].get(key) == expected["result"][key], f"result.{key} differs from the expected output"
    assert got["evidence_ids"] == expected["evidence_ids"]
    assert got == expected


def test_reference_run_reproduces_ground_truth_core(replayed, fixture_json):
    out, _ = replayed
    r = out["result"]
    gt = fixture_json["ground_truth"]
    expected_route = [s.split()[-1] for s in gt["expected_route"]]
    assert [x["address"] for x in r["route"]] == expected_route
    assert Decimal(r["value_accounting"]["total_lost_before_hub"]) == Decimal(gt["total_fees_lost_before_hub"])
    assert r["value_accounting"]["components_reconcile"] is True
    assert r["mechanism"]["signed_by_victim_owner_key"] is True
    assert r["mechanism"]["permissions_unchanged"] is True
    assert [f["address"] for f in r["freeze_candidates"]] == ["TYHeH2HQn7pM5fe6aYwGabz9x4yizJbwp6"]
    exits = {(e["recipient"], e["exchange"]) for e in r["exchange_exits"]}
    assert exits == {("TNJSC23oMcb5ws9tppANFTGtEDcKQgQBYQ", "WhiteBIT"), ("TCiwRNyeUK7JwkEgF5W3AExFpZ2ErRZG4C", "WhiteBIT")}
    protocols = [c["protocol"] for c in r["cross_chain"]]
    assert protocols == ["USDT0 (LayerZero OFT)", "Rango (aggregator)", "NEAR Intents 1Click"]
    oft, rango, near = r["cross_chain"]
    assert oft["dstEid"] == 30101 and oft["recipient"] == "0x4079047990917F3150353FBd8A13b05b6286926d"
    assert rango["destinationChainId"] == 1414680398 and rango["destinationChainId_ascii"] == "TRON"
    assert near["recipient"].startswith(rango["receiver_ascii"])
    link = next(x for x in r["links"] if x["type"] == "common_trx_funder")
    assert link["funder"] == "TVNMa2ZrUWE9sdBawJoQ8aN6LPFjv9ZppZ"
    assert link["confidence"] in ("low", "medium", "medium-high", "high")
    assert "not a fact" in link["statement"]


def test_amounts_are_decimal_strings(replayed):
    out, _ = replayed

    def walk(obj, path="result"):
        if isinstance(obj, float):
            raise AssertionError(f"float found at {path}")
        if isinstance(obj, dict):
            for k, v in obj.items():
                walk(v, f"{path}.{k}")
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                walk(v, f"{path}[{i}]")

    walk(out["result"])


def test_evidence_points_at_stored_bodies(replayed):
    out, _ = replayed
    assert out["evidence"]
    for eid, ev in out["evidence"].items():
        for sha in ev["body_sha256"]:
            assert sha, f"{eid}: no stored body"
            assert (STORE / "objects" / sha[:2] / sha).is_file(), f"{eid}: body {sha} missing from the fixture store"
