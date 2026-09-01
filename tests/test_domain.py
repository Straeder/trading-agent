"""T-001: domain types — immutability, Decimal money, long-only invariants."""

import dataclasses
from datetime import date
from decimal import Decimal

import pytest

from riskengine.domain import (
    Fill,
    Instrument,
    Order,
    Portfolio,
    Position,
    Proposal,
    Side,
    portfolio_value,
    position_value,
)

ASML = Instrument(isin="NL0010273215", symbol="ASML")
KPN = Instrument(isin="NL0000009082", symbol="KPN")


def test_types_are_immutable() -> None:
    portfolio = Portfolio(cash=Decimal("10000"))
    with pytest.raises(dataclasses.FrozenInstanceError):
        portfolio.cash = Decimal("0")  # type: ignore[misc]


def test_cash_must_be_decimal_not_float() -> None:
    with pytest.raises(TypeError, match="Decimal"):
        Portfolio(cash=10000.0)  # type: ignore[arg-type]


def test_cash_cannot_be_negative() -> None:
    with pytest.raises(ValueError, match="negative"):
        Portfolio(cash=Decimal("-1"))


def test_position_quantity_must_be_positive_long_only() -> None:
    with pytest.raises(ValueError, match="long-only"):
        Position(instrument=ASML, quantity=-5)
    with pytest.raises(ValueError, match="long-only"):
        Position(instrument=ASML, quantity=0)


def test_duplicate_positions_rejected() -> None:
    with pytest.raises(ValueError, match="duplicate"):
        Portfolio(
            cash=Decimal("0"),
            positions=(
                Position(ASML, 1),
                Position(ASML, 2),
            ),
        )


def test_proposal_and_order_validate_inputs() -> None:
    with pytest.raises(ValueError):
        Proposal(ASML, Side.BUY, 0, Decimal("600"), date(2026, 9, 1))
    with pytest.raises(ValueError):
        Proposal(ASML, Side.BUY, 1, Decimal("0"), date(2026, 9, 1))
    with pytest.raises(ValueError):
        Order(ASML, Side.SELL, -1)
    with pytest.raises(ValueError):
        Fill(Order(ASML, Side.BUY, 1), Decimal("-600"), date(2026, 9, 1))


def test_proposal_notional_is_exact_decimal() -> None:
    proposal = Proposal(ASML, Side.BUY, 3, Decimal("600.10"), date(2026, 9, 1))
    assert proposal.notional == Decimal("1800.30")


def test_portfolio_value_sums_cash_and_positions_exactly() -> None:
    portfolio = Portfolio(
        cash=Decimal("1000.10"),
        positions=(Position(ASML, 2), Position(KPN, 100)),
    )
    prices = {"NL0010273215": Decimal("600.20"), "NL0000009082": Decimal("3.55")}
    assert position_value(portfolio.positions[0], prices["NL0010273215"]) == Decimal(
        "1200.40"
    )
    assert portfolio_value(portfolio, prices) == Decimal("2555.50")


def test_missing_price_raises_key_error_per_m8() -> None:
    portfolio = Portfolio(cash=Decimal("0"), positions=(Position(ASML, 1),))
    with pytest.raises(KeyError):
        portfolio_value(portfolio, {})


def test_position_lookup() -> None:
    portfolio = Portfolio(cash=Decimal("0"), positions=(Position(ASML, 2),))
    assert portfolio.position_for("NL0010273215") == Position(ASML, 2)
    assert portfolio.position_for("NL0000009082") is None
