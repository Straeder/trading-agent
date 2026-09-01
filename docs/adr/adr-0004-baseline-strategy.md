# ADR-0004: Transparent Rule-Based Baseline Strategy

- **Status:** Accepted
- **Date:** 2026-09-02
- **Deciders:** Project owner (delegated)

## Context

The business case must demonstrate **governance**, not alpha. An opaque AI
strategy in v0.1 would make the risk engine's behaviour impossible to
attribute: was an outcome the strategy or the guardrails? Research on naive
diversification (1/N) shows equal weighting is a hard-to-beat, fully
explainable baseline.

## Decision

v0.1 proposals come from fixed, published rules:

1. **Universe:** current AEX constituents (M1).
2. **Selection:** the 12 largest constituents by index weight, capped at
   3 per ICB industry to avoid sector concentration.
3. **Weighting:** equal weight, **7.5% target per position** — deliberately
   below the 8% R2 warning band so a fully deployed portfolio is R1 (F-01).
   Deployment ≈ 90%, respecting the 10% cash buffer (M6).
4. **Cadence:** initial build-out, then monthly rebalance; interim trades
   only when a position drifts outside 5.5%–9.5%.
5. **Execution timing:** decisions after close on day T, fills at the close
   of T+1 (no look-ahead; spec §6).

Phase 2 may add AI/LLM-generated proposals behind the same ProposalPort,
treated as **untrusted input**: schema-validated, classified like any other
proposal, and never able to bypass the risk engine.

## Consequences

Easier: every trade is explainable in one sentence; the risk engine is the
star of the demo. Harder: no return ambition beyond the index; that is the
point of v0.1.
