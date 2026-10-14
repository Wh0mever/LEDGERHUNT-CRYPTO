"""Deterministic reference (baseline) for case-001: no AI, raw source data only.

Modules
- registry : known tokens, bridge contracts/APIs, event ABIs, exchange hot-wallet labels, thresholds
- chain    : parsing of raw TRON / Ethereum responses (integers, never floats)
- sigcheck : signer recovery for TRON transactions (secp256k1, pure Python)
- fetch    : source access with memo, evidence references and per-step metrics
- tracer   : the reference algorithm, starting from one TXID
- refetch  : step 1, raw re-fetch of every fixture identifier
- factcheck: step 2, fact-by-fact comparison of the fixture with raw data
- compare  : step 4, reference run vs ground_truth
- report   : Russian Markdown (MANIFEST.md, run report)
"""

from .tracer import ReferenceTracer

__all__ = ["ReferenceTracer"]
