"""Core domain types for the risk engine (spec: risk-engine-spec.md; plan §3).

All monetary amounts are ``decimal.Decimal`` — never floats. All types are
immutable (frozen dataclasses) so the decision pipeline stays pure and every
mandate rule is unit-testable without I/O.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Mapping


class Side(Enum):
    """Order direction. The mandate is long-only (M2): SELL only closes."""

    BUY = "BUY"
    SELL = "SELL"


class RiskClass(Enum):
    """Risk classification per spec §2."""

    R1 = "R1"
    R2 = "R2"
    R3 = "R3"


class DecisionAction(Enum):
    """What the engine decided to do with a proposal (spec §2)."""

    EXECUTE = "EXECUTE"
    REDUCE = "REDUCE"
    ESCALATE = "ESCALATE"
    NO_ACTION = "NO_ACTION"


class OwnerDecision(Enum):
    """Owner response to an R3 escalation (spec E2)."""

    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


def _require_decimal(name: str, value: object) -> None:
    if not isinstance(value, Decimal):
        raise TypeError(f"{name} must be Decimal, got {type(value).__name__}")


def _require_positive_decimal(name: str, value: Decimal) -> None:
    _require_decimal(name, value)
    if value <= 0:
        raise ValueError(f"{name} must be positive, got {value}")


@dataclass(frozen=True)
class Instrument:
    """An ordinary share identified by ISIN (mandate M1)."""

    isin: str
    symbol: str

    def __post_init__(self) -> None:
        if not self.isin or not self.symbol:
            raise ValueError("isin and symbol must be non-empty")


@dataclass(frozen=True)
class Position:
    """A held position. Long-only (M2): quantity is strictly positive."""

    instrument: Instrument
    quantity: int

    def __post_init__(self) -> None:
        if self.quantity <= 0:
            raise ValueError("position quantity must be positive (long-only)")


@dataclass(frozen=True)
class Portfolio:
    """Virtual portfolio state: cash plus held positions."""

    cash: Decimal
    positions: tuple[Position, ...] = ()

    def __post_init__(self) -> None:
        _require_decimal("cash", self.cash)
        if self.cash < 0:
            raise ValueError("cash cannot be negative (no leverage, M3)")
        isins = [p.instrument.isin for p in self.positions]
        if len(isins) != len(set(isins)):
            raise ValueError("duplicate position for the same instrument")

    def position_for(self, isin: str) -> Position | None:
        for position in self.positions:
            if position.instrument.isin == isin:
                return position
        return None


@dataclass(frozen=True)
class Proposal:
    """A trade proposal awaiting classification."""

    instrument: Instrument
    side: Side
    quantity: int
    reference_price: Decimal
    proposed_on: date

    def __post_init__(self) -> None:
        if self.quantity <= 0:
            raise ValueError("proposal quantity must be positive")
        _require_positive_decimal("reference_price", self.reference_price)

    @property
    def notional(self) -> Decimal:
        return self.reference_price * self.quantity


@dataclass(frozen=True)
class Order:
    """An approved instruction handed to an ExecutionPort adapter."""

    instrument: Instrument
    side: Side
    quantity: int

    def __post_init__(self) -> None:
        if self.quantity <= 0:
            raise ValueError("order quantity must be positive")


@dataclass(frozen=True)
class Fill:
    """The result of an executed order."""

    order: Order
    price: Decimal
    filled_on: date

    def __post_init__(self) -> None:
        _require_positive_decimal("price", self.price)


@dataclass(frozen=True)
class Classification:
    """Outcome of classifying a proposal or portfolio state (spec §2)."""

    risk_class: RiskClass
    reasons: tuple[str, ...] = ()


@dataclass(frozen=True)
class Decision:
    """A classified proposal plus the action the engine took (spec §2, A1)."""

    proposal: Proposal
    classification: Classification
    action: DecisionAction


@dataclass(frozen=True)
class EscalationEvent:
    """R3 notification to the owner (spec E1): trigger, metrics, limits."""

    trigger: str
    metrics: tuple[tuple[str, str], ...]
    proposed_action: str
    raised_at: datetime


@dataclass(frozen=True)
class OwnerResponse:
    """The owner's logged answer to an escalation (spec E2, E4)."""

    decision: OwnerDecision
    responded_at: datetime
    note: str = ""


@dataclass(frozen=True)
class HaltState:
    """Kill-switch / sticky R3 halt (M7, spec §2). Cleared only by owner."""

    active: bool
    reason: str = ""


@dataclass(frozen=True)
class AuditEvent:
    """One append-only audit entry (spec A1–A2)."""

    occurred_at: datetime
    event_type: str
    details: tuple[tuple[str, str], ...]
    spec_revision: str


def position_value(position: Position, price: Decimal) -> Decimal:
    """Market value of a single position at the given price."""
    _require_positive_decimal("price", price)
    return price * position.quantity


def portfolio_value(portfolio: Portfolio, prices: Mapping[str, Decimal]) -> Decimal:
    """Total portfolio value: cash plus every position at EOD prices.

    Raises ``KeyError`` when a price is missing — callers must treat that as
    a data-integrity failure (mandate M8), never as zero.
    """
    total = portfolio.cash
    for position in portfolio.positions:
        total += position_value(position, prices[position.instrument.isin])
    return total
