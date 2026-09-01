# Task Breakdown (v0.1)

> Atomic, independently reviewable tasks. Order matters: each task's tests
> must be green before the next begins. No task may touch a spec section
> still marked _To be specified_.

- **T-001** Domain types: frozen dataclasses + `Decimal` money
  (plan §3). _Depends on: —_
- **T-002** Port definitions in `riskengine.ports` (plan §2). _Depends: T-001_
- **T-003** Mandate checks M1–M8 as pure functions + `tests/test_mandate.py`.
  _Depends: T-001_
- **T-004** Classifier R1/R2/R3 incl. 80% warning band and sticky R3 halt +
  `tests/test_classification.py`. _Depends: T-003_
- **T-005** Append-only JSONL audit adapter + `tests/test_audit.py`
  (A1–A4, incl. spec git revision in each entry). _Depends: T-001_
- **T-006** Escalation flow with fail-safe no-response behaviour +
  `tests/test_escalation.py` (E1–E4). _Depends: T-004, T-005_
- **T-007** `PaperExecutionAdapter` + ExecutionPort contract test suite.
  _Depends: T-002_
- **T-008** Decision-cycle orchestrator wiring ports together; integration
  test of one full EOD cycle with stub data. _Depends: T-003…T-007_
- **T-009** MarketDataPort manual-ingestion adapter incl. plausibility checks (ADR-0002 accepted).
  _Depends: T-008_
- **T-010** File inbox/outbox notification adapter (ADR-0003 accepted). _Depends: T-006_
- **T-011** Baseline strategy adapter per ADR-0004 behind ProposalPort. _Depends: T-008_

Out of scope for this breakdown: proposal generation (ADR-0004), backtesting,
validation reporting — these follow once spec §§5–6 are fully specified.
