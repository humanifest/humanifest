# Bot Operator Runbook

Humanifest is designed so another person can clone the repository, configure a
Humanifest-style bot identity, and run a safe discovery loop that finds worthy
causes and donates compute without creating maintainer burden.

The default operator loop is deliberately read-only. It validates local records,
summarizes cause and opportunity state, checks finance and compute governance,
and reports safe next actions. It does not fetch remote sources, contact
maintainers, post issue comments, open pull requests, publish packages, or change
records.

## First setup

1. Clone the repository.
2. Install Python 3.11 or newer.
3. Run the local checks:

```bash
python3 -m unittest
python3 -m humanifest.cli validate --root .
python3 -m humanifest.cli finance --root .
python3 -m humanifest.cli compute --root .
python3 -m humanifest.cli report --root .
```

4. Read these authority files before changing records:

- `AGENTS.md`
- `GOALS.md`
- `README.md`
- `docs/contribution-protocol.md`
- `docs/cause-discovery.md`
- `docs/finance-governance.md`
- `docs/compute-governance.md`
- `docs/github-identity.md`

## Read-only operator loop

Run the safe loop manually:

```bash
python3 -m humanifest.cli operate --root . --as-of 2026-09-11 --max-age-days 30
```

Use JSON when feeding another scheduler or dashboard:

```bash
python3 -m humanifest.cli operate --root . --as-of 2026-09-11 --max-age-days 30 --format json
```

The command reports:

- top cause pathways to review;
- opportunity state counts;
- source-review needs across cause, project, and opportunity records;
- finance steward status;
- compute-resource registry status;
- whether any opportunity passes every building gate;
- a record-linked work queue and safe next actions.

The work queue is a way to donate bounded review effort. Start with listed
source IDs, then examine active cause pathways and opportunity records. Cause
scores order discovery attention only. The queue excludes parked and completed
records from active cause and opportunity review, while retaining their stale
sources as review reminders. A separate follow-up lane keeps `MAINTAINER-CHECK`,
`PR-OPEN`, `MERGED`, and `RELEASED` opportunities visible for response, review,
release, and outcome checks. It does not assume a prior Humanifest contribution
or a new maintainer reply. Each opportunity shows its failed gate names and
state-specific next action; neither a score nor an empty failed-gate list grants
permission to implement or contact a maintainer. Check the cited source itself,
current upstream state, portfolio capacity, and applicable authorization before
changing a record or acting outside this repository.

## GitHub Actions automation

This repository includes a scheduled read-only workflow:

```text
.github/workflows/operator-loop.yml
```

It runs the operator loop daily and on manual dispatch. It has read-only
permissions and cannot post issues, comments, pull requests, releases, packages,
or repository changes.

Forks can adjust the cron schedule, but should keep `permissions: contents: read`
unless they have separately documented write authorization and bot identity
controls.

## Bot identity

For external writes, use a dedicated bot or machine user such as
`humanifest-bot`, not a personal account. Follow `docs/github-identity.md`.

Before any external write:

1. Verify the exact authenticated actor that will perform the write.
2. Confirm the action is authorized by `docs/contribution-protocol.md`.
3. Confirm the target opportunity's current gates permit the action.
4. Record the evidence URL, access date, actor, timestamp, and outcome.

The operator loop does not grant this authorization. It only tells the operator
what remains safe to inspect or refresh.

## Donated compute

Compute may come from free, donated, sponsored, paid, or self-hosted resources,
but it must comply with `docs/compute-governance.md`.

Allowed uses include source review, evidence synthesis, test design, handoff
drafting, and adversarial review. Extra compute must not be used to pool personal
accounts, evade provider limits, automate maintainer outreach, or scale up
unsolicited pull requests.

## Contribution loop

Use this cadence:

```text
operate
→ refresh stale sources
→ review top cause pathway
→ add or improve cause/project/opportunity records
→ validate
→ ask for maintainer confirmation only when authorized
→ implement only after every hard gate passes
→ adversarial review
→ human review
→ PR only when authorized
→ record accepted, released, or parked outcome
```

Useful negative findings are successful runs. Parking stale, unsupported,
private-data-dependent, or high-burden work protects maintainers and keeps
donated compute honest.
