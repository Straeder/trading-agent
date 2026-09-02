"""Mandate checks M1–M8 as pure functions (spec §1; plan §4; task T-003).

Every check is side-effect free and returns a ``CheckResult`` carrying the
metric and limit values, so the T-004 classifier can compute warning bands
and the audit log (A2) can record exact numbers. Checks evaluate the
**joint** projected post-trade portfolio of a whole cycle (F-10).

Staleness, cross-source and plausibility checks (the rest of M8) live at
the ingest adapter (ADR-0002); here M8 verifies completeness of prices.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Mapping

from riskengine.domain import (
    HaltState,
    Portfolio,
    Proposal,
    Side,
    portfolio_value,
)

ZERO = Decimal("0")


@dataclass(frozen=True)
class MandateLimits:
    """Owner-ratified limits (spec §1 defaults)."""

    max_position_pct: Decimal = Decimal("0.10")  # M4
    max_order_pct: Decimal = Decimal("0.05")  # M5
    min_cash_buffer_pct: Decimal = Decimal("0.10")  # M6


@dataclass(frozen=True)
class CheckResult:
    """Outcome of a single mandate check."""

    rule: str
    passed: bool
    metric: Decimal
    limit: Decimal
    message: str


@dataclass(frozen=True)
class ProjectedState:
    """Joint post-trade projection of a full cycle at reference prices.

    ``raw_cash`` and ``raw_quantities`` may be negative — projections must
    be able to *show* a would-be breach so checks can report it.
    """

    value: Decimal
    raw_cash: Decimal
    raw_quantities: tuple[tuple[str, int], ...]


def project(
    portfolio: Portfolio,
    proposals: tuple[Proposal, ...],
    prices: Mapping[str, Decimal],
) -> ProjectedState:
    """Apply all proposals jointly at reference prices (F-10).

    Raises ``KeyError`` on any missing price (M8 semantics: never zero).
    """
    cash = portfolio.cash
    quantities: dict[str, int] = {
        p.instrument.isin: p.quantity for p in portfolio.positions
    }
    for proposal in proposals:
        isin = proposal.instrument.isin
        if proposal.side is Side.BUY:
            cash -= proposal.notional
            quantities[isin] = quantities.get(isin, 0) + proposal.quantity
        else:
            cash += proposal.notional
            quantities[isin] = quantities.get(isin, 0) - proposal.quantity
    value = cash
    for isin, qty in quantities.items():
        if qty > 0:
            value += prices[isin] * qty
    return ProjectedState(
        value=value,
        raw_cash=cash,
        raw_quantities=tuple(sorted(quantities.items())),
    )


def check_mandate(
    portfolio: Portfolio,
    proposals: tuple[Proposal, ...],
    prices: Mapping[str, Decimal],
    constituents: frozenset[str],
    halt: HaltState,
    limits: MandateLimits = MandateLimits(),
) -> tuple[CheckResult, ...]:
    """Run M1–M8 over the joint cycle. Returns one result per rule."""
    results: list[CheckResult] = []

    # M7 — halt dominates everything.
    results.append(
        CheckResult(
            rule="M7",
            passed=not halt.active,
            metric=Decimal(1 if halt.active else 0),
            limit=ZERO,
            message="halt active" if halt.active else "no halt",
        )
    )

    # M8 (completeness part) — every held or proposed instrument priced.
    needed = {p.instrument.isin for p in portfolio.positions} | {
        p.instrument.isin for p in proposals
    }
    missing = sorted(needed - set(prices))
    results.append(
        CheckResult(
            rule="M8",
            passed=not missing,
            metric=Decimal(len(missing)),
            limit=ZERO,
            message=f"missing prices: {missing}" if missing else "prices complete",
        )
    )
    if missing:
        return tuple(results)  # cannot evaluate further without prices (M8)

    projected = project(portfolio, proposals, prices)
    projected_cash = projected.raw_cash
    projected_qty = dict(projected.raw_quantities)
    current_value = portfolio_value(portfolio, prices)

    # M1 — buys only in current constituents.
    non_constituent_buys = sorted(
        {
            p.instrument.isin
            for p in proposals
            if p.side is Side.BUY and p.instrument.isin not in constituents
        }
    )
    results.append(
        CheckResult(
            rule="M1",
            passed=not non_constituent_buys,
            metric=Decimal(len(non_constituent_buys)),
            limit=ZERO,
            message=(
                f"non-constituent buys: {non_constituent_buys}"
                if non_constituent_buys
                else "all buys are constituents"
            ),
        )
    )

    # M2 — long-only: no projected negative quantity (joint oversell check).
    oversold = sorted(isin for isin, qty in projected_qty.items() if qty < 0)
    results.append(
        CheckResult(
            rule="M2",
            passed=not oversold,
            metric=Decimal(len(oversold)),
            limit=ZERO,
            message=f"oversell: {oversold}" if oversold else "long-only respected",
        )
    )

    # M3 — no leverage: projected cash never negative.
    results.append(
        CheckResult(
            rule="M3",
            passed=projected_cash >= ZERO,
            metric=projected_cash,
            limit=ZERO,
            message=f"projected cash {projected_cash}",
        )
    )

    # M4 — every projected position within max share of projected value.
    worst_pct = ZERO
    worst_isin = "-"
    if projected.value > ZERO:
        for isin, qty in projected.raw_quantities:
            if qty <= 0:
                continue
            pct = (prices[isin] * qty) / projected.value
            if pct > worst_pct:
                worst_pct, worst_isin = pct, isin
    results.append(
        CheckResult(
            rule="M4",
            passed=worst_pct <= limits.max_position_pct,
            metric=worst_pct,
            limit=limits.max_position_pct,
            message=f"largest projected position {worst_isin} at {worst_pct:.4f}",
        )
    )

    # M5 — single order size vs current portfolio value.
    biggest_order = max((p.notional for p in proposals), default=ZERO)
    order_pct = biggest_order / current_value if current_value > ZERO else ZERO
    results.append(
        CheckResult(
            rule="M5",
            passed=order_pct <= limits.max_order_pct,
            metric=order_pct,
            limit=limits.max_order_pct,
            message=f"largest order {order_pct:.4f} of portfolio",
        )
    )

    # M6 — projected cash buffer vs projected value.
    buffer_pct = (
        projected_cash / projected.value if projected.value > ZERO else ZERO
    )
    results.append(
        CheckResult(
            rule="M6",
            passed=buffer_pct >= limits.min_cash_buffer_pct,
            metric=buffer_pct,
            limit=limits.min_cash_buffer_pct,
            message=f"projected cash buffer {buffer_pct:.4f}",
        )
    )

    return tuple(results)


def all_passed(results: tuple[CheckResult, ...]) -> bool:
    """True when every mandate check passed."""
    return all(r.passed for r in results)
