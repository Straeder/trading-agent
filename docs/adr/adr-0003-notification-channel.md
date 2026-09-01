# ADR-0003: File-Based Escalation Inbox/Outbox

- **Status:** Accepted
- **Date:** 2026-09-02
- **Deciders:** Project owner (delegated)

## Context

R3 escalations need a channel to a single human owner. E-mail/chat
integrations add dependencies and secrets that the business case does not
yet justify.

## Decision

v0.1 escalates to `state/escalations/outbox/` (one JSON file per event) and
reads owner responses from `state/escalations/inbox/`
(`APPROVED`/`REJECTED` + note). No response before the next cycle means no
action (E3), with deduplicated re-notification (F-11).

## Consequences

Easier: zero dependencies, fully auditable, trivially testable.
**Accepted residual risk (F-06):** the inbox is not authenticated; anyone
with filesystem access can forge an approval. Acceptable for a single-user
local paper system; a signed-token scheme is required before any real-money
discussion.
