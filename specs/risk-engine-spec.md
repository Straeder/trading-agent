# Risk Engine Specification

> **Status:** Draft placeholder — v0.1 scope only.
> This specification is the single source of truth. Code follows the spec; the
> spec is never retrofitted to match code (spec-driven development).

**Scope (v0.1):** AEX constituents only · paper trading with €10,000 virtual
capital · end-of-day decision cadence.

---

## 1. Mandate

_To be specified._

Defines what the risk engine is authorised to decide autonomously, what it must
refuse outright, and what it must escalate to the human owner. The trading and
execution engine is a replaceable detail operating strictly within this
mandate.

## 2. Risk Classification (R1 / R2 / R3)

_To be specified._

- **R1 —** definition, thresholds, permitted autonomous behaviour.
- **R2 —** definition, thresholds, constraints and required checks.
- **R3 —** definition, thresholds, mandatory escalation to the human owner.

Classification criteria, boundary conditions, and reclassification rules will
be specified here before any implementation begins.

## 3. Escalation Protocol

_To be specified._

Covers: escalation triggers per risk class, notification channel and format,
required human response, default behaviour when no response is received
(fail-safe: no action), and de-escalation conditions.

## 4. Audit Log

_To be specified._

Covers: events that must be logged (every decision, classification, escalation
and override), log schema, immutability and retention requirements, and how the
log supports post-hoc review by the organisation.

## 5. Paper-Trading Validation

_To be specified._

Covers: validation criteria for the €10,000 virtual portfolio, minimum
observation period, success and abort criteria, and the conditions under which
v0.1 may be considered validated.

## 6. Backtest Methodology

_To be specified._

Covers: data sources and coverage for AEX constituents, look-ahead and
survivorship-bias safeguards, end-of-day simulation assumptions, cost and
slippage model, and reporting of results against the risk mandate.
