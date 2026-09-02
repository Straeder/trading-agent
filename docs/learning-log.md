# Learning Log

What building and operating this system has taught us, one entry per
lesson, each traceable to evidence. New entries are appended per cycle
(V4). This file — not any single session's memory — is the system's
institutional memory; a lesson that is not written down does not exist.

- **L-01 (F-01, F-16):** limits interact. Individually sensible defaults
  (10% cap, 80% band, 5% order cap, 7.5% target) formed an unworkable
  system. Test the *set* of rules jointly, never each rule alone.
- **L-02 (F-18):** data provenance is the weakest layer. A cached page
  presented day-old intraday data as current; only a cross-source check
  caught it. Hence the 2-of-3 source rule in M8.
- **L-03 (F-17):** capital granularity is a real constraint. At €10,000,
  whole-share tickets exclude the index's largest name. Mandates must be
  evaluated against ticket sizes, not just percentages.
- **L-04 (Alpha Arena evidence):** in live LLM-trading experiments the
  losers died of overtrading, fees and leverage — not of bad predictions.
  Discipline is the transferable edge; cadence and cost modelling are
  risk controls, not accounting details.
- **L-05 (owner dialogue):** owner decisions need a defined domain:
  risk appetite, limits and capital are owner-level; market timing is
  excluded for everyone. Sovereignty is a role, not deference.
- **L-06 (cycle 1):** the escalation path was never exercised because the
  build-out was engineered to be R1. A validation criterion should force
  at least one deliberate R3 drill before real money (add to V-checks).
- **L-07 (repo migration):** invisible files *are* the history. Moving a
  repository via a graphical file manager silently drops `.git`,
  `.github` and `.gitignore`; always migrate with `unzip`/`cp -a` in a
  terminal, and verify with `git log` plus the audit-chain check.
