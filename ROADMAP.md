# Roadmap

## Phase 0: Thin Protocol MVP

- Define hard gates, scoring, records, and handoffs.
- Audit two candidate projects.
- Produce one maintainer inquiry draft.
- Keep unconfirmed opportunities out of implementation: retain viable candidates
  in `MAINTAINER-CHECK`, and use `PARKED` when stopping conditions apply.

## Phase 1: Maintainer-Confirmed Pilot

- The CHT #10155 inquiry is sent as `humanifest-bot`; await maintainer response.
- If maintainers confirm, prepare an isolated environment manifest.
- Reproduce the issue with synthetic data.
- Implement the smallest safe fix.
- Run adversarial review before any PR.
- While the pilot waits, resolve independent research questions and add a small
  number of verified opportunities from other organizations. Maintain useful
  next actions; a pending response does not stall the portfolio.

## Phase 2: Selective Automation

- Add read-only GitHub metadata ingestion only after manual records prove useful.
- Keep outreach within standing user authorization and verify the posting identity.
- Track post-merge retention and maintainer satisfaction before adding scale.

## Explicitly Deferred

- Hosted dashboard.
- Autonomous GitHub App.
- Database server.
- LLM agent framework.
- Indiscriminate bulk discovery. Bounded, evidence-backed queue replenishment is
  active work whenever the current implementation path is waiting.
