# Risk Engine Specification

> **Status:** Draft v0.1 — populated with industry-standard defaults.
> Values marked **[DEFAULT]** are conventional starting points for a small,
> long-only, single-owner portfolio; the owner may override any of them by
> editing this spec (spec first, code second).

**Scope (v0.1):** AEX constituents only · paper trading with €10,000 virtual
capital · end-of-day decision cadence · long-only cash equities.

---

## 1. Mandate

The risk engine is the sole gatekeeper between trade proposals and execution.

- M1. The system shall trade only ordinary shares of current AEX constituents.
- M2. The system shall be long-only; short positions and derivatives are
  prohibited.
- M3. The system shall use no leverage; total invested capital shall never
  exceed available virtual cash.
- M4. **[DEFAULT]** A single position shall not exceed **10%** of portfolio
  value at the time of order creation.
- M5. **[DEFAULT]** A single order shall not exceed **5%** of portfolio value.
- M6. **[DEFAULT]** The portfolio shall hold a cash buffer of at least **10%**
  of portfolio value after any proposed order.
- M7. The owner may halt all activity at any time (kill switch); a halt takes
  precedence over every other rule.
- M8. When any input required for classification is missing, stale, or
  inconsistent, the system shall take no action and raise an R3 event.

## 2. Risk Classification (R1 / R2 / R3)

Every trade proposal and every end-of-day portfolio state shall be classified
before any action is taken.

- **R1 — within mandate.** The proposal breaches no limit and no metric is in
  the warning band. The system shall execute autonomously (paper) and log the
  decision.
- **R2 — approaching a limit.** **[DEFAULT]** Any metric at or above **80%**
  of its limit (e.g. position at ≥ 8% of portfolio value, daily loss at
  ≥ 1.6%). The system shall either (a) reduce the proposal so all metrics
  return below the warning band, or (b) escalate; it shall never execute the
  original proposal unchanged.
- **R3 — breach or hazard.** Any of: a limit would be breached; **[DEFAULT]**
  daily portfolio loss ≥ **2%**; **[DEFAULT]** drawdown from peak ≥ **10%**;
  data integrity failure (M8); kill switch active. The system shall take no
  market action and shall escalate to the owner.

Reclassification: classifications are computed fresh each decision cycle;
no class is sticky except an R3 halt, which persists until the owner clears it.

## 3. Escalation Protocol

- E1. When a proposal or state is classified R3, the system shall notify the
  owner with: trigger, metric values, limit values, and the proposed action.
- E2. The system shall proceed only after explicit owner approval recorded in
  the audit log.
- E3. When no owner response is received before the next decision cycle, the
  system shall take no action (fail-safe) and repeat the notification.
- E4. De-escalation: an R3 halt is cleared only by an explicit owner decision,
  which shall itself be logged.

## 4. Audit Log

- A1. The system shall log every proposal, classification, decision,
  escalation, owner response, and configuration change.
- A2. Each entry shall record: UTC timestamp, event type, inputs (metric and
  limit values), outcome, and the git revision of the spec in force.
- A3. The log shall be append-only (JSON Lines); entries are never edited or
  deleted.
- A4. The log shall be sufficient to reconstruct every decision without access
  to any other system state.

## 5. Paper-Trading Validation

_To be specified in detail._ **[DEFAULT]** outline: minimum **3 months** of
end-of-day paper trading; success requires zero unlogged decisions, zero
mandate breaches, and every R3 correctly escalated. Any mandate breach aborts
validation.

## 6. Backtest Methodology

_To be specified in detail._ Constraints already fixed by this spec:
end-of-day data only, AEX constituents with survivorship-bias-free membership
history, no look-ahead, and transaction costs modelled conservatively.
