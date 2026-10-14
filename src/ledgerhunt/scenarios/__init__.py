"""Synthetic TRON test scenarios with exactly known answers (Stage 2, item 4.6).

Modules:
- ``generator``  deterministic generator of the dev and held-out sets (recorded through the real clients)
- ``templates``  9 categories x 6 variants
- ``builder``    builds a synthetic world and its expected answer from the same construction
- ``server``     ScenarioServer: serves a world in the raw formats of TronGrid, java-tron and LayerZero Scan
- ``formats``    raw response builders checked against real recorded responses
- ``schema``     expected/candidate result schema (pydantic) and scenario input schema
- ``scorer``     per-fact scoring and set metrics (owner decisions, section 1.5)
- ``validate``   structural validation, replay check, format parity with real responses
- ``sets``       manifests with sha256 hashes, held-out protection
- ``case001_ref`` case-001 as a development reference scenario
"""

from .schema import ScenarioInput, TraceResult
from .scorer import aggregate, candidate_from_expected, score_scenario

__all__ = ["ScenarioInput", "TraceResult", "aggregate", "candidate_from_expected", "score_scenario"]
