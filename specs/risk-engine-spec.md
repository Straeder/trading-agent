# Risk Engine Specification

> **Status:** v0.2 — red-team findings F-01..F-15 incorporated
> (see `docs/redteam/redteam-v0.1.md`). Values marked **[DEFAULT]** are
> owner-overridable; spec first, code second.

**Scope (v0.1 system):** AEX constituents only · paper trading, €10,000
virtual capital · end-of-day cadence · long-only, EUR-denominated cash
equities. Market times are CET/CEST (Euronext); all logged timestamps are
UTC (F-03).

---

## 1. Mandate

- M1. The system shall **buy** only EUR-denominated ordinary shares of
  current AEX constituents (F-15). A held instrument that leaves the index
  becomes **legacy**: hold or sell only, flagged in reporting (F-08).
- M2. The system shall be long-only; shorts and derivatives are prohibited.
  A SELL exceeding the held quantity shall be classified R3 (F-09).
- M3. No leverage: projected cash after all approved orders of a cycle shall
  never be negative.
- M4. **[DEFAULT]** A single position shall not exceed **10%** of portfolio
  value at classification time.
- M5. **[DEFAULT]** A single order shall not exceed **5%** of portfolio value.
- M6. **[DEFAULT]** Projected cash after the cycle's orders shall be at least
  **10%** of portfolio value.
- M7. The owner may halt all activity at any time; a halt takes precedence
  over every rule. HaltState is persisted; on restart, if persisted state
  and the audit log disagree, the system boots **halted** (F-04).
- M8. Data integrity: prices older than the last completed Euronext trading
  day, missing prices for any held or proposed instrument, missing
  constituent data, or a failed plausibility check (±20% day-on-day move
  without a known corporate action, F-13) shall raise R3 and block all
  market action. Prices are valid only when confirmed by at least 2 of 3
  independent sources; unexplained divergence between sources shall raise
  R3 (ADR-0005).
- M9. Any corporate action affecting a held instrument shall raise R3;
  position adjustments are made only after owner approval and are logged
  (F-07).

## 2. Risk Classification (R1 / R2 / R3)

- Classification is computed fresh each cycle over the **joint** set of
  proposals: metrics are evaluated against the projected post-trade
  portfolio of the entire cycle, not per proposal in isolation (F-10).
- **R1 — within mandate.** No limit breached, no metric in the warning band:
  execute autonomously (paper) and log.
- **R2 — approaching a limit.** **[DEFAULT]** Any metric at ≥ **80%** of its
  limit. The engine shall reduce the proposal set until all metrics are
  below the band, or escalate; never execute unchanged.
- **R3 — breach or hazard.** Any limit breach; **[DEFAULT]** daily loss of
  total portfolio value ≥ **2%**; **[DEFAULT]** drawdown ≥ **10%** from the
  peak of total EOD portfolio value since inception (F-12); any M7/M8/M9
  event. No market action; escalate.
- An R3 halt is sticky until explicitly cleared by the owner (E4).

## 3. Escalation Protocol

- E1. Every R3 event shall be notified with: a stable event ID, trigger,
  metric and limit values, and the proposed action.
- E2. Market action after R3 requires an explicit, logged owner approval
  referencing the event ID.
- E3. No response before the next cycle ⇒ no action; re-notification reuses
  the same event ID so repeats are deduplicated (F-11).
- E4. De-escalation only by explicit, logged owner decision.

## 4. Audit Log

- A1. Log every ingest (with provenance), proposal, classification,
  decision, escalation, owner response, halt change and config change.
- A2. Each entry records: UTC timestamp, event type, inputs (metric and
  limit values), outcome, and the git revision of the spec in force.
- A3. Append-only JSON Lines with a **hash chain**: every entry contains the
  SHA-256 of the previous entry; verification failure ⇒ boot halted (F-05).
- A4. The log alone suffices to reconstruct every decision.

## 5. Paper-Trading Validation

- V1. **[DEFAULT]** Minimum **3 months** of EOD paper trading.
- V2. Success criteria are governance metrics, not returns: 100% of
  decisions logged and hash-chain verified; zero mandate breaches; every
  R3 escalated and resolved per §3; zero unexplained state changes.
- V3. Any mandate breach or audit-chain failure aborts validation; restart
  requires a spec revision and owner sign-off.
- V4. An EOD summary report is delivered to the owner each cycle (C8).
- V5. Objective hierarchy (owner direction, 2026-09-02): profit is the
  long-term goal; risk constraints always dominate the return objective,
  never the reverse. Performance is reported against the AEX Gross Return
  index net of costs (B3). Outperformance is NOT a v0.1 success
  criterion; making it one requires a specified edge hypothesis and its
  own falsifiable test in a future spec revision.

## 6. Backtest Methodology

- B1. EOD closes only; AEX membership history free of survivorship bias.
- B2. No look-ahead: signals from close T, fills at close T+1 — identical to
  live paper timing (ADR-0004).
- B3. **[DEFAULT]** Costs: **0.15%** per trade plus **0.10%** spread proxy,
  applied to every simulated fill.
- B4. Backtests report governance metrics (breaches, R2/R3 frequency,
  escalations) alongside performance, against the same spec revision.
