# Capability Map (v0.1)

What the system must be able to do, independent of how. Each capability maps
to spec sections and plan ports.

| ID | Capability | Spec | Port(s) |
| --- | --- | --- | --- |
| C1 | Ingest end-of-day prices and AEX membership | M1, M8 | MarketDataPort |
| C2 | Maintain virtual portfolio state (EUR only) | M3–M6 | ExecutionPort |
| C3 | Generate trade proposals from transparent rules | ADR-0004 | ProposalPort |
| C4 | Classify every proposal and state as R1/R2/R3 | §2 | core |
| C5 | Decide, reduce, or escalate; fail-safe on silence | §3 | NotificationPort |
| C6 | Execute approved orders as paper fills | §1 | ExecutionPort |
| C7 | Record everything append-only and tamper-evident | §4 | AuditLogPort |
| C8 | Report an EOD summary to the owner | §5 | NotificationPort |
| C9 | Honour a halt (kill switch) above all else | M7 | core |

**Out of scope v0.1:** intraday trading, derivatives, short selling, leverage,
real money, non-AEX markets, tax treatment, and AI/LLM proposal generation
(phase 2 behind the same ProposalPort — see ADR-0004).
