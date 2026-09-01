# ADR-0001: Risk-Engine-First Architecture

- **Status:** Accepted
- **Date:** 2026-09-01
- **Deciders:** Project owner

## Context

This project is a personal, AI-assisted equity trading system built as a
business case for the organisation. The dominant risk in such systems is not
poor trade selection but ungoverned behaviour: positions taken outside an
agreed mandate, silent failures, and decisions that cannot be reconstructed
afterwards.

Two architectural orientations were considered:

1. **Trading-first** — build the strategy and execution pipeline, then bolt on
   risk checks.
2. **Risk-engine-first** — build a governed risk engine as the core of the
   system, and treat the trading/execution engine as a replaceable detail that
   operates strictly within the risk engine's mandate.

The project also commits to spec-driven development: the specification in
`specs/` is authoritative, and code follows the spec, never the reverse.

## Decision

We will build the system risk-engine-first.

- The risk engine (`src/riskengine/`) is the architectural core. It owns the
  mandate, the R1/R2/R3 risk classification, the escalation protocol to the
  human owner, and the audit log.
- The execution engine (`src/execution/`) is a replaceable detail. It is
  developed interface-first: the risk engine defines the contract, and any
  execution implementation (paper trading now, potentially a broker adapter
  later) must satisfy that contract.
- No trading logic is implemented before the relevant sections of
  `specs/risk-engine-spec.md` are written and agreed.
- Automated tests and linting are mandatory and enforced in CI from the first
  commit.

## Consequences

- **Easier:** governance, auditability, and the business case itself — the
  organisation can evaluate the control framework independently of any trading
  strategy. Swapping or discarding the execution engine does not threaten the
  core.
- **Harder:** initial velocity. Visible "trading" functionality arrives later,
  because the mandate, classification, and escalation behaviour must be
  specified and tested first.
- **Accepted trade-off:** slower start in exchange for a system whose every
  decision is classified, escalatable, and reconstructable from the audit log.
