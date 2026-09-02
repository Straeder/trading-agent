# Red-Team Review v0.1

Adversarial review of `constitution.md`, `risk-engine-spec.md` (v0.1),
`plan.md` and ADR-0001..0004. Severity: H(igh) / M(edium) / L(ow).
Every finding is either **resolved in spec v0.2** or **accepted** with
rationale.

| ID | Sev | Finding | Resolution |
| --- | --- | --- | --- |
| F-01 | H | Limit interaction deadlock: 10% cap + 80% warning band means any position at target 10% is permanently R2; equal-weight full deployment was impossible without living in the warning band. | ADR-0004: target weight 7.5%, 12 names, ≈90% deployed — all metrics R1 at rest. |
| F-02 | H | "Stale or inconsistent data" (M8) was undefined, so the fail-safe could never fire deterministically. | Spec v0.2 M8: data older than the last Euronext trading day, missing constituents, or failed plausibility checks ⇒ R3. |
| F-03 | M | No timezone convention; "end of day" is ambiguous around DST. | Spec v0.2: market times CET/CEST (Euronext close), all log timestamps UTC. |
| F-04 | H | Halt persistence unspecified: a restart could silently clear an R3 halt. | Spec v0.2 M7: HaltState persisted; on any state/audit mismatch the system boots halted. |
| F-05 | H | Plain JSONL audit log is silently editable — violates the spirit of A3. | Spec v0.2 A3: hash chain; each entry stores SHA-256 of the previous entry. |
| F-06 | M | File-based owner approval is unauthenticated and forgeable. | **Accepted** for single-user local paper trading (ADR-0003); blocking issue for anything beyond. |
| F-07 | M | Corporate actions (splits, dividends, tickers changes) corrupt position values undetected. | Spec v0.2 M9: any corporate action on a held instrument ⇒ R3, manual adjustment, logged. |
| F-08 | M | Instrument leaving the AEX: M1 as written could force a fire sale. | Spec v0.2 M1: buying restricted to constituents; existing holdings become legacy (hold or sell only), flagged in reporting. |
| F-09 | H | Sell-side under-specified: shorting via oversell was not structurally blocked at classification. | Spec v0.2 M2: SELL quantity must not exceed held quantity; violation ⇒ R3. Domain types already enforce positive positions. |
| F-10 | H | Per-proposal classification ignores same-cycle aggregation: five individually valid orders can jointly breach cash/exposure limits. | Spec v0.2 §2: proposals are classified jointly against the projected post-trade portfolio of the whole cycle. |
| F-11 | L | E3 re-notification every cycle spams the owner and buries new escalations. | Spec v0.2 E3: re-notify with the same event ID; new events always distinct. |
| F-12 | M | "Drawdown from peak" undefined (peak of what, since when?). | Spec v0.2 §2: peak of total EOD portfolio value since inception. |
| F-13 | M | A single bad tick (fat-finger close) can trigger or mask limits. | ADR-0002: ±20% day-on-day plausibility check without corporate action ⇒ R3 data integrity. |
| F-14 | M | Future AI proposals could be steered by adversarial content (prompt injection via news). | ADR-0004: phase-2 proposals are untrusted input — schema-validated, fully classified, cannot bypass the engine. Out of scope v0.1. |
| F-15 | L | Currency implicit; a non-EUR listing would corrupt arithmetic. | Spec v0.2 M1: EUR-denominated ordinary shares only. |

**Conclusion:** no finding invalidates the risk-engine-first architecture;
F-01, F-04, F-05, F-09 and F-10 were material spec defects and are fixed in
spec v0.2 before any further implementation (spec first, code second).

## Live findings from cycle 1 (2026-09-02)

| ID | Sev | Finding | Resolution |
| --- | --- | --- | --- |
| F-16 | M | M5 order cap (5% = €500) sits below the 7.5% ADR-0004 target weight, blocking a one-day build-out. | Two-phase build-out: ≤5% orders in cycle 1, top-up to 7.5% in a later cycle. Letter- and spirit-compliant; no spec change. |
| F-17 | M | Whole-share minimum tickets make ASML (€1,435.40), Adyen (€1,006.80) and ASMI (€786.00) uninvestable at €10,000 capital under M4/M5 — the index's largest name is excluded by the mandate itself. | Replaced by next-ranked UMG and NN; consequence (tracking error vs AEX) reported to owner. Owner options: accept, raise virtual capital, or specify fractional shares in a spec revision. |
| F-18 | L | Ad-hoc web sources serve cached pages with mixed dates; a first fetch presented day-old intraday data as current. | Caught by the M8 cross-check (index close verified across two sources). Reinforces ADR-0002 provenance + plausibility requirements. |
