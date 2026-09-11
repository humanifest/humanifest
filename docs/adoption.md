# Adopt Humanifest

Humanifest is meant to be easy to clone, run, and adapt without creating
maintainer burden. A good local setup starts read-only, validates its own records,
and only moves toward outreach or implementation when the contribution protocol
allows it.

## Ten-minute local run

1. Clone the repository:

```bash
git clone https://github.com/humanifest/humanifest
cd humanifest
```

2. Run the read-only operator loop:

```bash
python3 -m humanifest.cli operate --root . --as-of "$(date -u +%F)" --max-age-days 30
```

3. Validate the local records:

```bash
python3 -m humanifest.cli validate --root .
python3 -m humanifest.cli finance --root .
python3 -m humanifest.cli compute --root .
python3 -m humanifest.cli report --root .
```

The operator loop does not fetch remote sources, contact maintainers, post
comments, open pull requests, publish packages, or mutate records. Treat its
output as a work queue for review, not as permission to write upstream.

## Recommended first contribution

Start with one of these small, reviewable tasks:

- refresh a stale source and keep the original source ID intact;
- improve a cause, project, or opportunity record without advancing unsupported
  gates;
- add a test for validation, scoring, reporting, finance, compute, or operator
  behavior;
- review a handoff for overclaiming, missing evidence, or unclear scope;
- improve documentation that made setup or review harder than it needed to be.

Useful negative findings count. Parking work that is stale, too broad,
unwanted, private-data-dependent, or likely to burden maintainers is a successful
Humanifest outcome.

## Run your own Humanifest-style bot

A Humanifest-style bot should be a governed operator, not an autonomous
maintainer-contact machine.

Minimum setup:

1. Use a dedicated bot or machine user, not a personal account.
2. Keep scheduled automation read-only by default.
3. Keep `permissions: contents: read` for ordinary GitHub Actions operator runs.
4. Track donated, sponsored, paid, free, or self-hosted compute in a public
   compute registry.
5. Keep finance and sponsorship records separate from personal or company
   operating funds.
6. Verify the authenticated actor before any external write.
7. Do not open issues, comments, or pull requests unless the contribution
   protocol and current authorization allow it.

Use [Bot Operator Runbook](bot-operator-runbook.md) for the detailed setup and
[GitHub Identity](github-identity.md) for bot identity controls.

## Contributor roles

Humanifest needs more than implementers:

- **Cause scouts** identify humanitarian problem areas worth reviewing.
- **Project stewards** keep project metadata, policies, and sources current.
- **Evidence reviewers** test whether an opportunity is real, current, bounded,
  and consequential.
- **Compute donors** contribute governed compute within provider terms.
- **Maintainer liaisons** coordinate only when authorization and gates permit it.
- **Implementation volunteers** write narrow patches after every hard gate
  passes.
- **Adversarial reviewers** try to falsify the handoff before it reaches
  maintainers.

## What not to copy

Do not use Humanifest as a way to scale unsolicited AI pull requests, pool
personal compute accounts, bypass provider limits, scrape private operational
data, or make impact claims that are not supported by cited records. The project
is useful because it declines most work before it reaches a maintainer.
