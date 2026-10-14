"""Scorer: compares a candidate trace result with the expected answer of a scenario.

Counting rules (owner decisions, docs/spec/stage-2-decisions.md section 1.5):

1. Fact accuracy is counted per fact, not per report. Every expected fact (transfer, stop
   of a route, exchange deposit, bridge exit, merge, limitation) is matched by key.
2. A scenario passes only if every expected route is found and the candidate states no
   false fact.
3. Source unavailability is excluded from the denominator but counted and reported
   separately: expected facts marked ``excluded`` (behind a designed outage or index gap)
   are not in the fact denominators, and scenarios with a designed source failure are not
   in the pass-rate denominator; both are reported on their own lines.

Fact outcomes:
- ``correct``  : expected fact found with every compared attribute equal;
- ``weaker``   : found, true, but less specific (taint ``uncertain`` where the answer is
                 ``traced``, ``unverified`` where it is confirmed, a subset of sweeps or
                 merge inflows) - not correct, not false;
- ``missed``   : expected fact absent;
- ``false``    : a stated fact that contradicts the answer or the world: wrong amount or
                 parties, a transfer that does not exist, a failed/zero-value/poisoning
                 transfer presented as a flow, exact attribution after commingling,
                 "confirmed" where the second source was down, an exchange or bridge that
                 is not one, a source failure that did not happen, a wrong stop reason;
- ``neutral``  : a true fact that is not required (allowed: beyond the depth limit, after
                 commingling, sweeps, context transfers with taint ``none``).

Route matching: an expected route (TXID sequence + terminal address) is found when a
candidate route has the same TXIDs and terminal, or starts with the expected TXIDs and
continues further (continuing past a stop is judged by the facts it states, not by the
route itself).

Metrics: fact recall = correct / counted expected facts; fact precision = (correct +
weaker) / (correct + weaker + false); scenario pass rate = passed / scenarios without a
designed source failure, with a 95% Wilson interval.
"""

from __future__ import annotations

import math
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any, Iterable

from .schema import EVIDENCE_BOUNDARY_REASONS, TraceResult
from .world import World

TAINT_RANK = {"none": 0, "uncertain": 1, "traced": 2}
VERIF_RANK = {"unverified": 0, "second_source_confirmed": 1}
LIMITATION_REASONS = frozenset({"source_unavailable", "incomplete_listing", "data_gap"})


def _norm_addr(a: str | None) -> str | None:
    if a is None:
        return None
    return a.lower() if a.lower().startswith("0x") else a


def _norm_tx(t: str | None) -> str | None:
    if t is None:
        return None
    t = t.lower()
    return t[2:] if t.startswith("0x") and len(t) == 66 else t


def _norm_tx_chain(t: str, chain: str) -> str:
    t = t.lower()
    if chain == "tron":
        return t[2:] if t.startswith("0x") else t
    return t if t.startswith("0x") else "0x" + t


def _amount_eq(a: str | None, b: str | None) -> bool:
    if a is None or b is None:
        return a is b
    return Decimal(a) == Decimal(b)


@dataclass
class FactOutcome:
    key: str
    kind: str
    outcome: str  # correct | weaker | missed | false | neutral | excluded | excluded_found
    detail: str = ""


@dataclass
class ScenarioScore:
    scenario_id: str
    category: str | None
    passed: bool
    affected_by_unavailability: bool
    routes_expected: int
    routes_found: int
    counts: Counter = field(default_factory=Counter)
    by_kind: dict[str, Counter] = field(default_factory=lambda: defaultdict(Counter))
    false_facts: list[FactOutcome] = field(default_factory=list)
    missed_routes: list[str] = field(default_factory=list)
    outcomes: list[FactOutcome] = field(default_factory=list)

    @property
    def counted(self) -> int:
        return self.counts["correct"] + self.counts["weaker"] + self.counts["missed"] + self.counts["false_matched"]

    def to_dict(self, *, details: bool = True) -> dict[str, Any]:
        d = {
            "scenario_id": self.scenario_id,
            "category": self.category,
            "passed": self.passed,
            "affected_by_unavailability": self.affected_by_unavailability,
            "routes_expected": self.routes_expected,
            "routes_found": self.routes_found,
            "facts": {
                "expected_counted": self.counted,
                "correct": self.counts["correct"],
                "weaker": self.counts["weaker"],
                "missed": self.counts["missed"],
                "false": self.counts["false_matched"] + self.counts["false_extra"],
                "neutral": self.counts["neutral"],
                "excluded_unavailable": self.counts["excluded"],
                "excluded_found": self.counts["excluded_found"],
            },
        }
        if details:
            d["false_facts"] = [f.__dict__ for f in self.false_facts]
            d["missed_routes"] = self.missed_routes
            d["by_kind"] = {k: dict(v) for k, v in sorted(self.by_kind.items())}
        return d


class _Scorer:
    def __init__(self, expected: TraceResult, candidate: TraceResult, world: World | None,
                 trust_candidate_outages: bool) -> None:
        self.e = expected
        self.c = candidate
        self.w = world
        self.trust = trust_candidate_outages
        self.out: list[FactOutcome] = []
        self.excluded_targets: set[str] = set()
        traps: dict[tuple[str | None, int | None], str] = {}
        trap_txids: dict[str | None, str] = {}
        for t in expected.traps:
            traps[(_norm_tx(t.txid), t.event_index)] = t.reason
            trap_txids.setdefault(_norm_tx(t.txid), t.reason)
        self.traps = traps
        self.trap_txids = trap_txids
        if trust_candidate_outages:
            self.excluded_targets = {lim.target for lim in candidate.limitations}

    # -- helpers --------------------------------------------------------
    def add(self, key: str, kind: str, outcome: str, detail: str = "") -> None:
        self.out.append(FactOutcome(key, kind, outcome, detail))

    def trap_reason(self, txid: str, event_index: int | None) -> str | None:
        t = _norm_tx(txid)
        return self.traps.get((t, event_index)) or self.traps.get((t, None))

    def world_transfer(self, txid: str, event_index: int | None) -> dict[str, Any] | None:
        if self.w is None:
            return None
        for tr in self.w.transfers():
            if tr["txid"] == _norm_tx(txid) and (event_index is None or tr["event_index"] == event_index):
                return tr
        return None

    def excluded_by_trust(self, fact_targets: Iterable[str]) -> bool:
        return self.trust and any(t in self.excluded_targets for t in fact_targets)

    # -- transfers -----------------------------------------------------------------
    @staticmethod
    def tkey(f) -> str:
        base = f"transfer:{f.chain}:{_norm_tx_chain(f.txid, f.chain)}"
        if f.event_index is None:  # unknown index (reference case): one key per (txid, from, to)
            return f"{base}:*:{_norm_addr(f.from_address)}>{_norm_addr(f.to_address)}"
        return f"{base}:{f.event_index}"

    @staticmethod
    def wkey(f) -> str:
        return (f"transfer:{f.chain}:{_norm_tx_chain(f.txid, f.chain)}:*:"
                f"{_norm_addr(f.from_address)}>{_norm_addr(f.to_address)}")

    def compare_transfer(self, e, c) -> tuple[str, str]:
        if _norm_addr(e.from_address) != _norm_addr(c.from_address) or _norm_addr(e.to_address) != _norm_addr(c.to_address):
            return "false", "wrong parties"
        if not _amount_eq(e.amount, c.amount) or e.asset != c.asset:
            return "false", "wrong amount or asset"
        if TAINT_RANK[c.taint] > TAINT_RANK[e.taint]:
            return "false", f"overclaimed taint {c.taint} (answer: {e.taint})"
        if VERIF_RANK[c.verification] > VERIF_RANK[e.verification]:
            return "false", "claims second-source confirmation that was not available"
        if TAINT_RANK[c.taint] < TAINT_RANK[e.taint] or VERIF_RANK[c.verification] < VERIF_RANK[e.verification]:
            return "weaker", "true but less specific"
        return "correct", ""

    def score_transfers(self) -> None:
        exp = {self.tkey(f): f for f in self.e.transfers}
        wild = {self.tkey(f): f for f in self.e.transfers if f.event_index is None}
        allowed = {self.tkey(f): f for f in (self.e.allowed.transfers if self.e.allowed else [])}
        seen: set[str] = set()
        for c in self.c.transfers:
            k = self.tkey(c)
            e = exp.get(k) or wild.get(self.wkey(c))
            if e is not None:
                ek = self.tkey(e)
                if ek in seen:
                    continue
                seen.add(ek)
                outcome, detail = self.compare_transfer(e, c)
                if e.excluded or self.excluded_by_trust([e.from_address, e.txid]):
                    self.add(ek, "transfer", "excluded_found" if outcome != "false" else "false_extra", detail)
                else:
                    self.add(ek, "transfer", outcome if outcome != "false" else "false_matched", detail)
                continue
            if k in allowed:
                outcome, detail = self.compare_transfer(allowed[k], c)
                self.add(k, "transfer", "neutral" if outcome != "false" else "false_extra", detail)
                continue
            trap = self.trap_reason(c.txid, c.event_index)
            if c.taint == "none":
                if trap in ("failed_transaction",):
                    self.add(k, "transfer", "false_extra", "failed transaction presented as a transfer")
                elif self.w is None or self._true_in_world(c):
                    self.add(k, "transfer", "neutral", "context transfer")
                else:
                    self.add(k, "transfer", "false_extra", "transfer not found on chain")
                continue
            if trap:
                self.add(k, "transfer", "false_extra", f"flow claim on a trap ({trap})")
            else:
                self.add(k, "transfer", "false_extra", "flow claim not supported by the answer")
        for k, e in exp.items():
            if k in seen:
                continue
            if e.excluded or self.excluded_by_trust([e.from_address, e.txid]):
                self.add(k, "transfer", "excluded")
            else:
                self.add(k, "transfer", "missed")

    def _true_in_world(self, c) -> bool:
        tr = self.world_transfer(c.txid, c.event_index)
        return bool(tr) and tr["from"] == c.from_address and tr["to"] == c.to_address and \
            Decimal(tr["value"]) / Decimal(10**6) == Decimal(c.amount)

    # -- routes and stops ------------------------------------------------------------------
    def score_routes(self) -> tuple[int, int, list[str]]:
        cand = [(tuple(_norm_tx_chain(t, r.terminal.chain) for t in r.txids), r) for r in self.c.routes]
        exp_routes = [r for r in self.e.routes if not r.excluded]
        found = 0
        missed: list[str] = []
        stop_expected: dict[str, tuple[str, Any]] = {}
        for r in exp_routes:
            txs = tuple(_norm_tx_chain(t, r.terminal.chain) for t in r.txids)
            skey = f"stop:{r.terminal.chain}:{_norm_addr(r.terminal.address)}:{txs[-1]}"
            stop_expected.setdefault(skey, (r.terminal.reason, r))
            hit = False
            for ctx, cr in cand:
                if ctx == txs and _norm_addr(cr.terminal.address) == _norm_addr(r.terminal.address):
                    hit = True
                    break
                if len(ctx) > len(txs) and ctx[:len(txs)] == txs:
                    hit = True
                    break
            if hit:
                found += 1
            else:
                missed.append(r.route_id or ",".join(txs))
        # stop facts
        cand_stops: dict[str, Any] = {}
        for ctx, cr in cand:
            skey = f"stop:{cr.terminal.chain}:{_norm_addr(cr.terminal.address)}:{ctx[-1]}"
            cand_stops.setdefault(skey, cr)
        for skey, (reason, r) in stop_expected.items():
            cr = cand_stops.get(skey)
            if self.excluded_by_trust([r.terminal.address]) and r.terminal.reason not in LIMITATION_REASONS:
                self.add(skey, "stop", "excluded")
                continue
            if cr is None:
                self.add(skey, "stop", "missed")
            elif cr.terminal.reason == reason:
                self.add(skey, "stop", "correct")
            else:
                self.add(skey, "stop", "false_matched", f"stop reason {cr.terminal.reason} (answer: {reason})")
        for skey, cr in cand_stops.items():
            if skey in stop_expected:
                continue
            verdict = self.judge_extra_stop(cr)
            self.add(skey, "stop", "neutral" if verdict is None else "false_extra", verdict or "")
        # invalid txids inside extra routes
        world_tx = {t["txid"] for t in self.w.txs} if self.w else None
        for ctx, cr in cand:
            for t in ctx:
                trap = self.trap_txids.get(_norm_tx(t))
                if trap in ("failed_transaction", "zero_value_poisoning", "approval_not_transfer", "lookalike_dust",
                            "pre_theft_inflow", "pre_theft_history"):
                    self.add(f"route_txid:{t}", "route", "false_extra", f"route uses a trap transaction ({trap})")
                elif world_tx is not None and cr.terminal.chain == "tron" and t not in world_tx:
                    self.add(f"route_txid:{t}", "route", "false_extra", "route uses a transaction that does not exist")
        return len(exp_routes), found, missed

    def judge_extra_stop(self, cr) -> str | None:
        """None if the stated stop is consistent with the answer/world, else why it is false."""
        reason, addr = cr.terminal.reason, cr.terminal.address
        exp_ex = {d.deposit_address for d in self.e.exchange_deposits}
        exp_ex |= {d.deposit_address for d in (self.e.allowed.exchange_deposits if self.e.allowed else [])}
        labels = {lab["address"]: lab for lab in (self.w.labels if self.w else [])}
        if reason == "exchange_deposit":
            return None if addr in exp_ex else "address is not an exchange deposit"
        if reason == "exchange_hot_wallet":
            return None if labels.get(addr, {}).get("type") == "exchange_hot_wallet" or self.w is None else \
                "address is not a known exchange hot wallet"
        if reason == "known_service":
            return None if addr in labels or self.w is None else "address is not a known service"
        if reason in ("bridge_exit_supported", "bridge_exit_unsupported", "bridge_destination_unconfirmed"):
            bridge_addrs = {lab["address"] for lab in labels.values() if lab.get("type") == "bridge_contract"}
            if self.w is not None:
                for tx in self.w.txs:
                    for ev in tx["events"]:
                        if ev["name"] == "OFTSent":
                            bridge_addrs.add(ev["contract"])
            return None if addr in bridge_addrs or self.w is None else "address is not a bridge"
        if reason in LIMITATION_REASONS:
            targets = {lim.target for lim in self.e.limitations}
            return None if addr in targets or self.trust else "no source failure at this address"
        if reason == "commingled":
            merges = {m.address for m in self.e.merges} | {m.address for m in (self.e.allowed.merges if self.e.allowed else [])}
            return None if addr in merges else "no commingling at this address"
        if reason == "funds_at_rest":
            if self.w is None:
                return None
            return None if self.w.balance(addr) > 0 else "address holds no funds"
        return None  # max_depth

    # -- exchange deposits, bridges, merges, limitations --------------------------------------
    def score_keyed(self, kind: str, exp_items, allowed_items, cand_items, keyf, comparef) -> None:
        exp = {keyf(x): x for x in exp_items}
        allowed = {keyf(x): x for x in allowed_items}
        seen = set()
        for c in cand_items:
            k = keyf(c)
            if k in exp:
                seen.add(k)
                e = exp[k]
                outcome, detail = comparef(e, c)
                if getattr(e, "excluded", None):
                    self.add(k, kind, "excluded_found" if outcome != "false" else "false_extra", detail)
                else:
                    self.add(k, kind, outcome if outcome != "false" else "false_matched", detail)
            elif k in allowed:
                outcome, detail = comparef(allowed[k], c)
                self.add(k, kind, "neutral" if outcome != "false" else "false_extra", detail)
            elif kind == "limitation" and self.trust:
                self.add(k, kind, "neutral", "candidate-reported source failure (trusted)")
            else:
                self.add(k, kind, "false_extra", f"{kind} not supported by the answer")
        for k, e in exp.items():
            if k not in seen:
                self.add(k, kind, "excluded" if getattr(e, "excluded", None) else "missed")

    def compare_exchange(self, e, c) -> tuple[str, str]:
        if e.exchange.lower() != c.exchange.lower() or _norm_addr(e.hot_wallet) != _norm_addr(c.hot_wallet):
            return "false", "wrong exchange or hot wallet"
        es = {_norm_tx(t) for t in e.sweep_txids}
        cs = {_norm_tx(t) for t in c.sweep_txids}
        extra = cs - es
        if extra and self.w is not None:
            for t in extra:
                tr = self.world_transfer(t, None)
                if not tr or tr["from"] != e.deposit_address or tr["to"] != e.hot_wallet:
                    return "false", "sweep txid is not a sweep to the hot wallet"
        if es <= cs:
            return "correct", ""
        return ("weaker", "some sweeps missing") if cs else ("weaker", "no sweep evidence")

    def compare_bridge(self, e, c) -> tuple[str, str]:
        if e.protocol != c.protocol or e.supported != c.supported or e.dst_eid != c.dst_eid:
            return "false", "wrong protocol, destination or support flag"
        for f in ("amount_sent", "amount_received"):
            ev, cv = getattr(e, f), getattr(c, f)
            if cv is not None and ev is not None and not _amount_eq(ev, cv):
                return "false", f"wrong {f}"
            if cv is not None and ev is None:
                return "false", f"{f} not observable"
        for f in ("recipient", "guid", "dst_txid"):
            ev, cv = getattr(e, f), getattr(c, f)
            if cv is None:
                continue
            if ev is None:
                truth = self._bridge_truth(e.txid, f)
                if truth is None or (_norm_addr(truth) != _norm_addr(cv)):
                    return "false", f"{f} not supported by the evidence"
                continue
            if _norm_addr(ev) != _norm_addr(cv):
                return "false", f"wrong {f}"
        missing = [f for f in ("recipient", "amount_received", "dst_txid") if getattr(e, f) is not None and getattr(c, f) is None]
        return ("weaker", "missing " + ", ".join(missing)) if missing else ("correct", "")

    def _bridge_truth(self, txid: str, f: str) -> str | None:
        if self.w is None:
            return None
        m = self.w.lz_by_tx(txid)
        if not m:
            return None
        return {"recipient": m.get("recipient"), "guid": "0x" + m["guid"], "dst_txid": m.get("dst_txid")}.get(f)

    def compare_merge(self, e, c) -> tuple[str, str]:
        if c.attribution == "exact":
            return "false", "exact attribution claimed for commingled funds"
        es = {_norm_tx(t) for t in e.traced_inflow_txids}
        cs = {_norm_tx(t) for t in c.traced_inflow_txids}
        if cs - es:
            return "false", "traced inflow not supported by the answer"
        return ("correct", "") if cs == es else ("weaker", "some traced inflows missing")

    @staticmethod
    def compare_limitation(e, c) -> tuple[str, str]:
        return ("correct", "") if e.limitation == c.limitation else ("false", f"limitation {c.limitation} (answer: {e.limitation})")

    def run(self) -> tuple[int, int, list[str]]:
        self.score_transfers()
        routes = self.score_routes()
        allowed = self.e.allowed
        self.score_keyed("exchange_deposit", self.e.exchange_deposits, allowed.exchange_deposits if allowed else [],
                         self.c.exchange_deposits, lambda x: f"exchange_deposit:{x.chain}:{_norm_addr(x.deposit_address)}",
                         self.compare_exchange)
        self.score_keyed("bridge_exit", self.e.bridge_exits, allowed.bridge_exits if allowed else [], self.c.bridge_exits,
                         lambda x: f"bridge_exit:{x.chain}:{_norm_tx_chain(x.txid, x.chain)}", self.compare_bridge)
        self.score_keyed("merge", self.e.merges, allowed.merges if allowed else [], self.c.merges,
                         lambda x: f"merge:{x.chain}:{_norm_addr(x.address)}", self.compare_merge)
        self.score_keyed("limitation", self.e.limitations, [], self.c.limitations,
                         lambda x: f"limitation:{x.source_role}:{_norm_addr(x.target)}", self.compare_limitation)
        return routes


def score_scenario(expected: TraceResult, candidate: TraceResult, world: World | None = None, *,
                   trust_candidate_outages: bool = False) -> ScenarioScore:
    """Score one candidate against one expected answer (and the world, when available)."""
    if candidate.scenario_id != expected.scenario_id:
        raise ValueError(f"candidate is for {candidate.scenario_id}, answer is for {expected.scenario_id}")
    s = _Scorer(expected, candidate, world, trust_candidate_outages)
    n_routes, found, missed = s.run()
    counts: Counter = Counter()
    by_kind: dict[str, Counter] = defaultdict(Counter)
    false_facts = []
    for o in s.out:
        counts[o.outcome] += 1
        by_kind[o.kind][o.outcome] += 1
        if o.outcome in ("false_matched", "false_extra"):
            false_facts.append(o)
    meta = getattr(expected, "meta", None) or {}
    affected = bool(expected.outages)
    passed = found == n_routes and not false_facts
    return ScenarioScore(
        scenario_id=expected.scenario_id, category=meta.get("category"), passed=passed,
        affected_by_unavailability=affected, routes_expected=n_routes, routes_found=found, counts=counts,
        by_kind=by_kind, false_facts=false_facts, missed_routes=missed, outcomes=s.out,
    )


def wilson(k: int, n: int, z: float = 1.959964) -> tuple[float | None, float | None]:
    if n == 0:
        return None, None
    p = k / n
    den = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / den
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return round(max(0.0, centre - half), 4), round(min(1.0, centre + half), 4)


def _ratio(a: int, b: int) -> float | None:
    return round(a / b, 4) if b else None


def aggregate(scores: list[ScenarioScore]) -> dict[str, Any]:
    """Set-level metrics with source failures reported separately."""
    counted = [s for s in scores if not s.affected_by_unavailability]
    affected = [s for s in scores if s.affected_by_unavailability]
    tot: Counter = Counter()
    for s in scores:
        tot.update(s.counts)
    correct, weaker = tot["correct"], tot["weaker"]
    false_n = tot["false_matched"] + tot["false_extra"]
    expected_counted = correct + weaker + tot["missed"] + tot["false_matched"]
    passed = sum(1 for s in counted if s.passed)
    lo, hi = wilson(passed, len(counted))
    by_cat: dict[str, dict[str, Any]] = {}
    for s in scores:
        c = by_cat.setdefault(s.category or "unknown", {"scenarios": 0, "counted": 0, "passed": 0,
                                                        "with_source_failure": 0, "source_failure_handled": 0})
        c["scenarios"] += 1
        if s.affected_by_unavailability:
            c["with_source_failure"] += 1
            c["source_failure_handled"] += int(s.passed)
        else:
            c["counted"] += 1
            c["passed"] += int(s.passed)
    return {
        "scenarios_total": len(scores),
        "scenarios_counted": len(counted),
        "scenarios_passed": passed,
        "pass_rate": _ratio(passed, len(counted)),
        "pass_rate_wilson95": [lo, hi],
        "scenarios_with_source_failure": len(affected),
        "source_failure_scenarios_handled": sum(1 for s in affected if s.passed),
        "routes_expected": sum(s.routes_expected for s in scores),
        "routes_found": sum(s.routes_found for s in scores),
        "facts_expected_counted": expected_counted,
        "facts_correct": correct,
        "facts_weaker": weaker,
        "facts_missed": tot["missed"],
        "facts_false": false_n,
        "facts_neutral": tot["neutral"],
        "facts_excluded_unavailable": tot["excluded"] + tot["excluded_found"],
        "fact_recall": _ratio(correct, expected_counted),
        "fact_precision": _ratio(correct + weaker, correct + weaker + false_n),
        "by_category": dict(sorted(by_cat.items())),
    }


def candidate_from_expected(expected: TraceResult) -> TraceResult:
    """The perfect candidate: every counted expected fact, nothing else (used for self-checks)."""
    d = expected.dump()
    d["result_type"] = "candidate"
    for k in ("allowed", "traps", "outages", "evidence_boundaries", "notes", "meta"):
        d.pop(k, None)
    for section in ("transfers", "routes", "exchange_deposits", "bridge_exits", "merges", "limitations"):
        d[section] = [dict(x, excluded=None) for x in d[section] if not x.get("excluded")]
    return TraceResult.model_validate(d)


__all__ = ["ScenarioScore", "aggregate", "candidate_from_expected", "score_scenario", "wilson",
           "EVIDENCE_BOUNDARY_REASONS"]
