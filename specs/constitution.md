# Project Constitution

Project-wide rules that every specification, plan, and implementation must
obey. Specs may refine these rules; they may never contradict them.

## Principles

1. **Risk-engine-first.** The governed risk engine is the architectural core.
   The execution engine is a replaceable detail operating strictly within the
   risk engine's mandate (ADR-0001). The risk engine acts as a **gatekeeper**:
   no order reaches execution without passing classification.
2. **Spec-driven.** The spec is the source of truth. Behaviour that is not
   specified is not implemented. When behaviour changes, the spec is updated
   first, the code second.
3. **Fail-safe by default.** In any ambiguous, degraded, or unresponsive
   state, the system takes **no action**. Doing nothing is always permitted;
   trading never is by default.
4. **Human sovereignty.** The human owner can halt the system at any time
   (kill switch) and is the only authority that can approve R3 decisions.
5. **Full auditability.** Every decision, classification, escalation, and
   override is logged append-only with the spec version in force at the time.

## Standards

- Language: Python ≥ 3.12, src layout.
- Tests: pytest; every behavioural requirement in a spec has at least one
  automated test before it is considered implemented.
- Lint: ruff; CI must be green on every push.
- Documentation: English, EN-GB spelling (organisation, behaviour, licence),
  enforced via cSpell (`en-GB`).
- Requirements are written in EARS form ("When ⟨trigger⟩, the system shall
  ⟨response⟩") so they are individually testable.

## Guardrails

- No new runtime dependencies without an ADR.
- No trading logic outside the boundaries of `specs/risk-engine-spec.md`.
- No implementation work on a spec section still marked _To be specified_.
- Scope v0.1 is fixed: AEX constituents only, paper trading, €10,000 virtual
  capital, end-of-day cadence, long-only cash equities. Anything else requires
  a new ADR and spec revision.
