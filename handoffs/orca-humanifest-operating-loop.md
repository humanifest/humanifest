# Humanifest Operating Loop Handoff

Objective: continue the governed Humanifest loop that finds worthy humanitarian
and public-interest open-source work, verifies evidence, checks compute and
funding capacity, and advances only maintainer-approved low-burden contributions.

Read first:

- `AGENTS.md`
- `GOALS.md`
- `README.md`
- `docs/contribution-protocol.md`
- `docs/compute-governance.md`
- `docs/finance-governance.md`
- `docs/model-routing.md`
- `portfolio/status.md`
- `portfolio/compute-resources.json`
- `portfolio/funding-ledger.json`

Current state as of 2026-09-10:

- No active implementation is recorded.
- No external PR is recorded.
- No funding entries are recorded.
- GitHub Copilot is recorded as potential sponsored compute but remains
  `unverified`; do not use or recommend it as available capacity until account,
  license, disclosure, target-project policy, and allocation checks pass.
- CHT opportunities at `MAINTAINER-CHECK` still require maintainer confirmation
  before environment or implementation work.
- Parked opportunities remain parked until their stopping reasons are resolved
  with evidence.

Allowed next independent jobs:

- Run `python3 -m humanifest.cli sources --root . --as-of 2026-09-10 --max-age-days 30 --needs-review` and refresh stale source records using read-only browsing.
- Verify whether `humanifest-bot` still has the exact identity and permissions
  required by the contribution protocol before any authorized CHT follow-up.
- Inspect one candidate issue read-only and update its record only if evidence
  supports a narrower blocker or useful negative finding.
- Extend finance or compute governance only from recorded, auditable facts.

Do not contact maintainers, post comments, open pull requests, publish packages,
or make other external writes without explicit authorization and verified
Humanifest identity. Do not execute third-party setup code before setup and
security inspection.

Before handing off or proposing work, run:

```bash
python3 -m unittest
python3 -m humanifest.cli validate --root .
python3 -m humanifest.cli finance --root .
python3 -m humanifest.cli compute --root .
python3 -m humanifest.cli report --root .
```
