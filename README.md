# AEX Risk-Engine-First Trading System (SDD Scaffold)

A personal, AI-assisted equity trading system built as a business case for the
organisation. This repository is currently a **scaffold**: it contains the
specification skeleton, architectural decisions, and quality tooling — and
deliberately **no trading logic yet**.

## Architectural philosophy

**Risk-engine-first.** The governed risk engine is the core of the system. It
owns the mandate, the R1/R2/R3 risk classification, escalation to the human
owner, and the audit log. The trading/execution engine is a replaceable detail
beneath it, developed interface-first: the risk engine defines the contract,
and any execution implementation must satisfy it. See
[ADR-0001](docs/adr/adr-0001-risk-engine-first.md).

**Spec-driven development (SDD).** The specification in
[`specs/risk-engine-spec.md`](specs/risk-engine-spec.md) is the single source
of truth. Code follows the spec, never the other way around. Behaviour that is
not specified is not implemented.

**Quality first.** Automated tests (pytest) and linting (ruff) are mandatory
and run in CI on every push.

## Scope (v0.1)

- AEX constituents only
- Paper trading with €10,000 virtual capital
- End-of-day decision cadence
- R1/R2/R3 risk classes with escalation to the human owner
- Full audit log of every decision

## Repository structure

```
specs/                  Authoritative specifications (SDD source of truth)
  constitution.md       Project-wide principles, standards and guardrails
  risk-engine-spec.md   Risk engine spec: mandate, R1/R2/R3, escalation,
                        audit log, paper-trading validation, backtesting
docs/adr/               Architecture Decision Records
  adr-template.md       Template for new ADRs
  adr-0001-*.md         The risk-engine-first decision
src/riskengine/         The governed risk engine (architectural core)
src/execution/          Execution engine (replaceable detail, interface-first)
tests/                  Automated tests (pytest)
.github/workflows/      CI: ruff lint + pytest on every push
```

## Getting started

```bash
pip install -e ".[dev]"
ruff check .
pytest
```

## Style

All documentation in this repository is written in **English, using EN-GB
spelling** (organisation, behaviour, licence). This aligns the project with
standard SDD tooling and keeps terminology consistent across specs, ADRs and
code comments. The convention is enforced with cSpell configured for `en-GB`
(see [`cspell.json`](cspell.json)).
