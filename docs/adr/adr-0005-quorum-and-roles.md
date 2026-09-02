# ADR-0005: Quorum and Functional Agent Roles

- **Status:** Accepted (data layer) / Deferred to phase 2 (proposal layer)
- **Date:** 2026-09-02
- **Deciders:** Project owner (concept), assistant (elaboration)

## Context

The owner proposed a three-agent quorum before any transaction, with the
agents forbidden from sharing sources. Redundancy-with-independence is a
proven safety pattern (triple modular redundancy), but N-version research
(Knight & Leveson) shows independently built judges fail more correlatedly
than assumed — and LLM agents share training data, so persona diversity is
largely cosmetic.

## Decision

1. **Adopted — data quorum (spec M8 revision):** EOD prices are valid only
   when confirmed by at least 2 of 3 independent sources; disagreement
   beyond rounding ⇒ R3 data-integrity event. This formalises the manual
   cross-check that caught F-18.
2. **Rejected — quorum on mandate checks:** M1–M9 are deterministic and
   testable; voting adds no information and creates a path for a 2-1
   majority to bless a limit breach. Rules stay absolute.
3. **Deferred to phase 2 — functional roles in the proposal layer:** not
   personas but mandates with opposed incentives: a Proposer (must propose,
   with verifiable grounding), a Challenger (may not propose; must seek
   grounds for rejection), and a Compliance role (verifies spec citations
   only). No consensus ⇒ no action (constitution: fail-safe). All three
   remain subordinate to the deterministic risk engine and the owner's R3
   authority.

## Consequences

Easier: source failures become detectable by construction; phase-2
proposals get structured dissent instead of diversity theatre.
Harder: a third data source must be identified per ADR-0002; the proposal
layer gains latency and cost. Residual risk, accepted and documented:
roles on a shared model are not independent judges.
