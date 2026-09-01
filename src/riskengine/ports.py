"""Ports (interfaces) defined by the risk-engine core (plan §2, ADR-0001).

Adapters depend on these Protocols; the core never depends on adapters
(dependency inversion). Any adapter must pass the corresponding contract
test suite before it may be wired into the decision cycle.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Mapping, Protocol, runtime_checkable

from riskengine.domain import (
    AuditEvent,
    EscalationEvent,
    Fill,
    Order,
    OwnerResponse,
    Portfolio,
    Position,
    Proposal,
)


@runtime_checkable
class ExecutionPort(Protocol):
    """The replaceable execution detail. v0.1: paper trading only."""

    def submit(self, order: Order) -> Fill: ...

    def positions(self) -> tuple[Position, ...]: ...

    def cash(self) -> Decimal: ...


@runtime_checkable
class MarketDataPort(Protocol):
    """End-of-day market data for AEX constituents (M1)."""

    def eod_prices(self, on: date) -> Mapping[str, Decimal]: ...

    def aex_constituents(self, on: date) -> frozenset[str]: ...


@runtime_checkable
class ProposalPort(Protocol):
    """Source of trade proposals. v0.1 ships a stub returning none."""

    def proposals(self, on: date, portfolio: Portfolio) -> tuple[Proposal, ...]: ...


@runtime_checkable
class NotificationPort(Protocol):
    """R3 escalation channel to the owner (E1–E3).

    Returns ``None`` when no response has been received; the caller must
    then take no action (fail-safe, E3).
    """

    def escalate(self, event: EscalationEvent) -> OwnerResponse | None: ...


@runtime_checkable
class AuditLogPort(Protocol):
    """Append-only audit log (A1–A4). Entries are never edited or deleted."""

    def append(self, event: AuditEvent) -> None: ...


@runtime_checkable
class Clock(Protocol):
    """Time source; a fixed clock is injected in tests."""

    def today(self) -> date: ...
