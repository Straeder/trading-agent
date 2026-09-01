# Technical Plan (v0.1)

> Derived from `constitution.md` and `risk-engine-spec.md`. The plan states
> **how**; the spec states **what**. Where the two disagree, the spec wins.

## 1. Architecture: ports and adapters (hexagonal)

Standard pattern for "core domain + replaceable details". The risk engine is
the domain core; everything else reaches it only through ports (interfaces)
defined **by the core**.

```
                    ┌──────────────────────────────┐
 MarketDataPort ──► │                              │ ──► ExecutionPort
 ProposalPort   ──► │   riskengine (domain core)   │ ──► NotificationPort
 Clock          ──► │  mandate · R1/R2/R3 · halt   │ ──► AuditLogPort
                    └──────────────────────────────┘
```

- `src/riskengine/` owns all domain logic **and all port definitions**
  (dependency inversion: adapters depend on the core, never the reverse).
- `src/execution/` contains only adapters implementing `ExecutionPort`.
  v0.1 ships a single `PaperExecutionAdapter`.
- The decision cycle is a pure, deterministic pipeline:
  `state + EOD data + proposals → classifications → decisions → effects`.
  All side effects (execute, notify, log) happen at the edges via ports, which
  keeps every mandate rule unit-testable without I/O.

## 2. Ports (contracts)

| Port | Core methods (indicative) | v0.1 adapter |
| --- | --- | --- |
| ExecutionPort | `submit(order) -> Fill`, `positions()`, `cash()` | Paper simulator, EOD fills |
| MarketDataPort | `eod_prices(date)`, `aex_constituents(date)` | **Deferred → ADR-0002** |
| ProposalPort | `proposals(date, portfolio)` | Stub returning none (v0.1 starts empty) |
| NotificationPort | `escalate(event) -> OwnerResponse \| None` | File/console inbox |
| AuditLogPort | `append(event)` | JSON Lines file, append-only |
| Clock | `today()` | System clock; fixed clock in tests |

Contract tests: one reusable test suite per port that **any** adapter must
pass, so execution stays a swappable detail (ADR-0001).

## 3. Data model

Standard library `dataclasses` (frozen) — no new runtime dependencies without
an ADR. All monetary amounts use `decimal.Decimal`, never floats.

`Instrument`, `Position`, `Portfolio`, `Proposal`, `Order`, `Fill`,
`Classification {R1, R2, R3}`, `Decision`, `AuditEvent`, `HaltState`.

State persistence: single JSON file for portfolio state; the audit log is the
authoritative history (spec A4).

## 4. Requirement → test mapping

Every spec ID gets at least one test before its code is written
(constitution: tests per behavioural requirement).

- M1–M8 → `tests/test_mandate.py`
- R1/R2/R3 incl. 80% band and halt stickiness → `tests/test_classification.py`
- E1–E4 fail-safe behaviour → `tests/test_escalation.py`
- A1–A4 append-only log → `tests/test_audit.py`
- ExecutionPort contract → `tests/contracts/test_execution_port.py`

## 5. Deferred decisions (each requires an ADR before implementation)

- **ADR-0002:** EOD market data source for AEX constituents.
- **ADR-0003:** notification channel for R3 escalation.
- **ADR-0004:** proposal generation (the AI component) — explicitly out of
  scope until the risk core passes all mandate tests.
