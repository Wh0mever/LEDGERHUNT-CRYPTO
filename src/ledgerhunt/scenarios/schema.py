"""Schema of scenario inputs and trace results (expected answers and candidate results).

One model, ``TraceResult``, is used for both the expected answer (``expected.json``) and a
tracer's candidate result. A candidate fills only the fact sections; ``allowed``, ``traps``
and ``outages`` exist only in expected answers.

Fact sections and how each fact is keyed (the scorer compares facts by key):

- ``transfers``         key ``transfer:<chain>:<txid>:<event_index>`` (``*`` when the index is unknown,
                        reference case only). Compared: from, to, amount, asset, taint, verification.
- ``routes``            a route is a TXID sequence from the theft plus its terminal (address, reason).
                        Each route yields one stop fact ``stop:<chain>:<terminal address>:<last txid>``.
- ``exchange_deposits`` key ``exchange_deposit:<chain>:<deposit address>``.
- ``bridge_exits``      key ``bridge_exit:<chain>:<txid>``.
- ``merges``            key ``merge:<chain>:<address>`` (commingled funds).
- ``limitations``       key ``limitation:<source_role>:<target>`` (source unavailable, incomplete listing,
                        data gap).

Amounts are decimal strings with exactly 6 fractional digits (USDT), never floats.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

RESULT_SCHEMA = "ledgerhunt.scenario-result/1"
INPUT_SCHEMA = "ledgerhunt.scenario-input/1"

Chain = Literal["tron", "ethereum"]
Taint = Literal["traced", "uncertain", "none"]
Verification = Literal["second_source_confirmed", "unverified"]
ExcludedReason = Literal["source_unavailable", "source_data_gap"]
StopReason = Literal[
    "funds_at_rest",
    "exchange_deposit",
    "exchange_hot_wallet",
    "known_service",
    "bridge_exit_supported",
    "bridge_exit_unsupported",
    "bridge_destination_unconfirmed",
    "commingled",
    "max_depth",
    "source_unavailable",
    "incomplete_listing",
    "data_gap",
]
EVIDENCE_BOUNDARY_REASONS = frozenset({
    "bridge_exit_unsupported", "bridge_destination_unconfirmed", "max_depth", "source_unavailable",
    "incomplete_listing", "data_gap",
})
SourceRole = Literal["tron_index", "tron_events", "tron_receipts_secondary", "bridge_api"]
LimitationKind = Literal["unavailable", "incomplete_listing", "data_gap"]
TrapReason = Literal[
    "pre_theft_inflow", "pre_theft_history", "zero_value_poisoning", "lookalike_dust", "failed_transaction",
    "approval_not_transfer", "foreign_inflow", "foreign_outflow", "exchange_internal", "unrelated",
]

AMOUNT_PATTERN = r"^\d+\.\d{6}$"


class _Model(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class TransferFact(_Model):
    chain: Chain = "tron"
    txid: str
    event_index: int | None = None
    from_address: str = Field(alias="from")
    to_address: str = Field(alias="to")
    amount: str = Field(pattern=AMOUNT_PATTERN)
    asset: str = "USDT-TRC20"
    taint: Taint = "traced"
    verification: Verification = "second_source_confirmed"
    role: str | None = None  # informative: main, side_branch, sweep, commingled_outflow, beyond_depth...
    excluded: ExcludedReason | None = None

    @field_validator("txid")
    @classmethod
    def _txid(cls, v: str) -> str:
        return v.lower()


class Terminal(_Model):
    chain: Chain = "tron"
    address: str
    reason: StopReason


class Route(_Model):
    route_id: str | None = None
    kind: Literal["main", "side_branch"] | None = None
    txids: list[str]
    terminal: Terminal
    excluded: ExcludedReason | None = None

    @field_validator("txids")
    @classmethod
    def _txids(cls, v: list[str]) -> list[str]:
        if not v:
            raise ValueError("a route needs at least one txid")
        return [t.lower() for t in v]


class ExchangeDeposit(_Model):
    chain: Chain = "tron"
    deposit_address: str
    exchange: str
    hot_wallet: str
    sweep_txids: list[str]
    excluded: ExcludedReason | None = None


class BridgeExit(_Model):
    chain: Chain = "tron"
    txid: str
    protocol: str  # usdt0_oft | unknown_bridge:<label> | rango | near_intents_1click
    dst_eid: int | None = None
    dst_chain: str | None = None  # informative
    supported: bool
    sender: str | None = None
    recipient: str | None = None
    amount_sent: str | None = Field(default=None, pattern=AMOUNT_PATTERN)
    amount_received: str | None = Field(default=None, pattern=AMOUNT_PATTERN)
    guid: str | None = None
    dst_txid: str | None = None
    excluded: ExcludedReason | None = None


class Merge(_Model):
    chain: Chain = "tron"
    address: str
    attribution: Literal["uncertain", "exact"] = "uncertain"
    traced_inflow_txids: list[str]
    foreign_inflow_txids: list[str] = Field(default_factory=list)  # informative, not scored
    excluded: ExcludedReason | None = None


class Limitation(_Model):
    source_role: SourceRole
    target: str  # address, txid or "*" (whole provider)
    limitation: LimitationKind
    excluded: ExcludedReason | None = None


class Trap(_Model):
    txid: str
    event_index: int | None = None
    reason: TrapReason


class Allowed(_Model):
    """True facts a candidate may report without being required to (beyond depth, after commingling, sweeps)."""

    transfers: list[TransferFact] = Field(default_factory=list)
    exchange_deposits: list[ExchangeDeposit] = Field(default_factory=list)
    bridge_exits: list[BridgeExit] = Field(default_factory=list)
    merges: list[Merge] = Field(default_factory=list)


class TraceResult(_Model):
    schema_id: str = Field(default=RESULT_SCHEMA, alias="schema")
    scenario_id: str
    result_type: Literal["expected", "candidate"] = "candidate"
    transfers: list[TransferFact] = Field(default_factory=list)
    routes: list[Route] = Field(default_factory=list)
    exchange_deposits: list[ExchangeDeposit] = Field(default_factory=list)
    bridge_exits: list[BridgeExit] = Field(default_factory=list)
    merges: list[Merge] = Field(default_factory=list)
    limitations: list[Limitation] = Field(default_factory=list)
    # expected-only sections
    allowed: Allowed | None = None
    traps: list[Trap] = Field(default_factory=list)
    outages: list[dict[str, Any]] = Field(default_factory=list)
    evidence_boundaries: list[dict[str, Any]] = Field(default_factory=list)  # derived view of route terminals
    notes: list[str] = Field(default_factory=list)
    meta: dict[str, Any] | None = None  # expected only: category, variant, title, description

    def dump(self) -> dict[str, Any]:
        return self.model_dump(mode="json", by_alias=True, exclude_none=False)


class ScenarioInput(_Model):
    """What a tracer gets: the start, parameters, context (labels, supported bridges) and the store."""

    schema_id: str = Field(default=INPUT_SCHEMA, alias="schema")
    scenario_id: str  # opaque: category and variant are kept in expected.json only
    split: Literal["dev", "holdout"]
    synthetic: bool = True
    start: dict[str, Any]
    params: dict[str, Any]
    context: dict[str, Any]
    store: str | None  # http-store directory relative to the scenario directory (None: shared store)
    request_profile: str
    providers: dict[str, str]
    reference: dict[str, Any] | None = None


def load_result(path: Path | str) -> TraceResult:
    return TraceResult.model_validate(json.loads(Path(path).read_text(encoding="utf-8")))


def json_schemas() -> dict[str, dict[str, Any]]:
    """JSON Schema documents for publication next to the scenario sets."""
    return {
        "trace-result.schema.json": TraceResult.model_json_schema(by_alias=True),
        "scenario-input.schema.json": ScenarioInput.model_json_schema(by_alias=True),
    }
