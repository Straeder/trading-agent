# ADR-0002: EOD Market Data via Manual Ingestion

- **Status:** Accepted
- **Date:** 2026-09-02
- **Deciders:** Project owner (delegated)

## Context

The core needs official Euronext Amsterdam closing prices and AEX membership.
Licensed real-time feeds are out of proportion for a €10,000 paper-trading
business case, and choosing a feed must not block the risk core.

## Decision

v0.1 uses a **manual ingestion adapter**: EOD closes are entered as a CSV/JSON
drop (sourced from public EOD data), with provenance (source, retrieval time)
recorded in the audit log. Every ingest passes plausibility checks (F-13):
a close moving more than 20% day-on-day without a known corporate action is a
data-integrity failure and raises R3 (M8).

## Consequences

Easier: no vendor lock-in, full provenance, the port stays swappable.
Harder: a manual operational step per cycle. An automated feed becomes a new
adapter behind the unchanged MarketDataPort, decided in a future ADR.
