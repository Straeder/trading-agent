"""T-002: port definitions — minimal fakes satisfy each Protocol."""

from datetime import date
from decimal import Decimal
from typing import Mapping

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
from riskengine.ports import (
    AuditLogPort,
    Clock,
    ExecutionPort,
    MarketDataPort,
    NotificationPort,
    ProposalPort,
)


class FakeExecution:
    def submit(self, order: Order) -> Fill:
        return Fill(order, Decimal("1"), date(2026, 9, 1))

    def positions(self) -> tuple[Position, ...]:
        return ()

    def cash(self) -> Decimal:
        return Decimal("10000")


class FakeMarketData:
    def eod_prices(self, on: date) -> Mapping[str, Decimal]:
        return {}

    def aex_constituents(self, on: date) -> frozenset[str]:
        return frozenset()


class FakeProposals:
    def proposals(self, on: date, portfolio: Portfolio) -> tuple[Proposal, ...]:
        return ()


class FakeNotifier:
    def escalate(self, event: EscalationEvent) -> OwnerResponse | None:
        return None


class FakeAuditLog:
    def append(self, event: AuditEvent) -> None:
        return None


class FakeClock:
    def today(self) -> date:
        return date(2026, 9, 1)


def test_fakes_satisfy_port_protocols() -> None:
    assert isinstance(FakeExecution(), ExecutionPort)
    assert isinstance(FakeMarketData(), MarketDataPort)
    assert isinstance(FakeProposals(), ProposalPort)
    assert isinstance(FakeNotifier(), NotificationPort)
    assert isinstance(FakeAuditLog(), AuditLogPort)
    assert isinstance(FakeClock(), Clock)


def test_incomplete_adapter_fails_protocol_check() -> None:
    class NotAnExecutionAdapter:
        def submit(self, order: Order) -> Fill:  # missing positions() and cash()
            raise NotImplementedError

    assert not isinstance(NotAnExecutionAdapter(), ExecutionPort)
