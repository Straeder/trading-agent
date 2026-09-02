"""T-003: mandate checks M1–M8 (spec §1). One test per rule, plus the
joint-aggregation scenario from red-team finding F-10."""

from datetime import date
from decimal import Decimal

from riskengine.domain import HaltState, Instrument, Portfolio, Position, Proposal, Side
from riskengine.mandate import all_passed, check_mandate

D = Decimal
TODAY = date(2026, 9, 2)
ASML = Instrument("NL0010273215", "ASML")
KPN = Instrument("NL0000009082", "KPN")
SHELL = Instrument("GB00BP6MXD84", "SHELL")
FOREIGN = Instrument("US0378331005", "AAPL")

CONSTITUENTS = frozenset({ASML.isin, KPN.isin, SHELL.isin})
NO_HALT = HaltState(active=False)
PRICES = {ASML.isin: D("100"), KPN.isin: D("4"), SHELL.isin: D("40")}


def buy(instr: Instrument, qty: int, px: str) -> Proposal:
    return Proposal(instr, Side.BUY, qty, D(px), TODAY)


def sell(instr: Instrument, qty: int, px: str) -> Proposal:
    return Proposal(instr, Side.SELL, qty, D(px), TODAY)


def result(results, rule):
    return next(r for r in results if r.rule == rule)


def test_compliant_cycle_passes_everything() -> None:
    pf = Portfolio(cash=D("10000"))
    proposals = (buy(SHELL, 12, "40"), buy(KPN, 100, "4"))
    results = check_mandate(pf, proposals, PRICES, CONSTITUENTS, NO_HALT)
    assert all_passed(results)


def test_m1_rejects_non_constituent_buy_but_allows_legacy_sell() -> None:
    pf = Portfolio(cash=D("1000"), positions=(Position(FOREIGN, 5),))
    prices = {**PRICES, FOREIGN.isin: D("10")}
    bad_buy = check_mandate(
        pf, (buy(FOREIGN, 1, "10"),), prices, CONSTITUENTS, NO_HALT
    )
    assert not result(bad_buy, "M1").passed
    legacy_sell = check_mandate(
        pf, (sell(FOREIGN, 5, "10"),), prices, CONSTITUENTS, NO_HALT
    )
    assert result(legacy_sell, "M1").passed  # F-08: hold or sell only


def test_m2_blocks_joint_oversell() -> None:
    pf = Portfolio(cash=D("1000"), positions=(Position(KPN, 10),))
    # Two sells of 6 each: individually below holdings, jointly oversold.
    results = check_mandate(
        pf, (sell(KPN, 6, "4"), sell(KPN, 6, "4")), PRICES, CONSTITUENTS, NO_HALT
    )
    assert not result(results, "M2").passed


def test_m3_blocks_joint_negative_cash_f10() -> None:
    pf = Portfolio(cash=D("1000"))
    # Each order (400) is fine alone; the pair overdraws the cash jointly.
    results = check_mandate(
        pf,
        (buy(KPN, 100, "4"), buy(KPN, 100, "4"), buy(KPN, 100, "4")),
        PRICES,
        CONSTITUENTS,
        NO_HALT,
    )
    assert not result(results, "M3").passed


def test_m4_caps_projected_position_share() -> None:
    pf = Portfolio(cash=D("10000"))
    results = check_mandate(
        pf, (buy(ASML, 15, "100"),), PRICES, CONSTITUENTS, NO_HALT
    )
    m4 = result(results, "M4")
    assert not m4.passed and m4.metric > m4.limit


def test_m5_caps_single_order_size() -> None:
    pf = Portfolio(cash=D("10000"))
    results = check_mandate(
        pf, (buy(ASML, 6, "100"),), PRICES, CONSTITUENTS, NO_HALT
    )
    assert not result(results, "M5").passed  # 600 > 5% of 10,000


def test_m6_requires_projected_cash_buffer() -> None:
    pf = Portfolio(cash=D("1000"))
    # Spend 920 via many small compliant orders: buffer 80/1000 = 8% < 10%.
    proposals = tuple(buy(KPN, 10, "4") for _ in range(23))
    results = check_mandate(pf, proposals, PRICES, CONSTITUENTS, NO_HALT)
    assert not result(results, "M6").passed


def test_m7_halt_dominates() -> None:
    pf = Portfolio(cash=D("10000"))
    results = check_mandate(
        pf, (buy(KPN, 10, "4"),), PRICES, CONSTITUENTS, HaltState(True, "drill")
    )
    assert not result(results, "M7").passed


def test_m8_missing_price_blocks_and_short_circuits() -> None:
    pf = Portfolio(cash=D("1000"), positions=(Position(ASML, 1),))
    results = check_mandate(pf, (), {}, CONSTITUENTS, NO_HALT)
    m8 = result(results, "M8")
    assert not m8.passed
    assert {r.rule for r in results} == {"M7", "M8"}  # no further evaluation


def test_results_carry_metric_and_limit_for_classifier() -> None:
    pf = Portfolio(cash=D("10000"))
    results = check_mandate(
        pf, (buy(SHELL, 12, "40"),), PRICES, CONSTITUENTS, NO_HALT
    )
    m4 = result(results, "M4")
    assert m4.limit == D("0.10") and D("0") < m4.metric < m4.limit
