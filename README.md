# Humanifest

[![Sponsor Humanifest](https://img.shields.io/badge/Sponsor-Humanifest-2ea44f?logo=githubsponsors&logoColor=white)](https://github.com/sponsors/humanifest)

Humanifest converts donated AI-assisted engineering capacity into verified, maintainer-approved, low-burden contributions to humanitarian and public-interest open-source software.

It is deliberately a thin coordination layer. Its job is to help decide what not to do, then prepare a small number of excellent upstream contributions only after evidence and maintainer interest support the work.

## Open-Source Mission

Humanifest is intended to become an open protocol and toolkit for directing
donated engineering and AI-assisted review time toward work that humanitarian
maintainers actually want. The project values restraint as much as output:
refreshing evidence, parking a weak opportunity, or reducing reviewer burden can
be as useful as writing code.

Public participation should strengthen this standard. Contributors can help by
auditing project records, refreshing stale sources, improving gates and schemas,
reviewing proposed handoffs, hardening the CLI, and documenting repeatable
workflows. Upstream outreach, issue comments, pull requests, and other external
writes remain controlled by the contribution protocol and require explicit
authorization.

## Current Status

This repository contains the first deterministic MVP:

- Cause-area records for metric-guided discovery before project selection.
- JSON records for projects and opportunities.
- Hard gates that prevent premature implementation.
- Transparent scoring from supplied evidence.
- Candidate brief, handoff, and portfolio report generation.
- Offline source-review lists with explicit review dates and age windows.
- Unit tests for validation, gates, scoring, and handoff generation.

Current records contain no opportunity ready for implementation. Run `report` for
each candidate's blockers and next permitted action; upstream status must be
rechecked before outreach or implementation.

## Principles

- One active implementation at a time.
- At most one open pull request per external organization.
- At most two open external pull requests across the portfolio.
- No nontrivial implementation before current maintainer interest is confirmed.
- No external writes without explicit user authorization.
- Standing authorization can cover routine contribution follow-ups; use the verified Humanifest identity and consult [the protocol](docs/contribution-protocol.md#communication-authorization).
- No private patient, survivor, volunteer, employee, or operational data.
- Every contribution must be minimal, issue-linked, reproducible, tested, and explainable line by line.

## Use

Python 3.11 or newer is required. The commands below run directly from this
checkout without installing dependencies.

```bash
python3 -m humanifest.cli validate --root .
python3 -m humanifest.cli operate --root . --as-of 2026-09-11 --max-age-days 30
python3 -m humanifest.cli causes --root .
python3 -m humanifest.cli report --root .
python3 -m humanifest.cli score portfolio/opportunities/cht-dhis2-bs-month-export.json
python3 -m humanifest.cli brief portfolio/opportunities/cht-dhis2-bs-month-export.json
python3 -m humanifest.cli handoff portfolio/opportunities/cht-dhis2-bs-month-export.json --target codex
python3 -m humanifest.cli sources --root . --as-of 2026-09-08 --max-age-days 30 --needs-review
```

For an installed `humanifest` command, create a virtual environment and install
the local app:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install .
.venv/bin/humanifest report --root .
```

The installed package contains the Python app. Records, schemas, and research stay
in the checkout; pass `--root /path/to/humanifest` when running portfolio commands
from elsewhere. Installation does not publish a package.

Every command validates its input before producing output. Invalid records return
exit code `1` with diagnostics on stderr; argument errors return `2`. `score`
prints JSON for use by other tools. `validate`, `report`, and `sources` require both portfolio
record directories and check unique record IDs, opportunity-to-project links, and
the implementation and PR capacity limits above. Single-record score and brief commands cannot
check portfolio capacity; validate the full portfolio before starting work. CLI
handoffs additionally require the exact record in a valid current portfolio.

Reports show capacity, blockers, and state-specific next actions in state/ID order.
Reports and CLI handoffs consume a checked-in, immutable Metamap v0.5 projection.
It is derived from current records and policy; it cannot authorize outreach,
implementation, state transitions, or impact claims. Stale or missing projections
fail closed. After changing records or bound controls, regenerate before reporting:

```bash
npm ci --ignore-scripts --prefix tools/metamap
python3 -m scripts.compile_correspondence
```

Node 22.12+ is needed for this development-time compilation and mutation tests;
normal reports use Python and the generated artifact without Node or network.
See [correspondence boundaries and exclusions](docs/portfolio-correspondence.md).
To refresh the saved status after validating records:

```bash
python3 -m humanifest.cli report --root . > /tmp/humanifest-status.md && cp /tmp/humanifest-status.md portfolio/status.md
```

Sources need unique IDs, absolute HTTP(S) or local `file://` URLs, and real access
dates in `YYYY-MM-DD` form. Evidence must reference a source in the same record.
These checks validate record consistency; they do not fetch sources or establish
that a claim is true. Reports and handoffs never advance opportunity states.

Gates can cite their supporting evidence with `source_ids`. A passing maintainer
confirmation gate requires at least one valid citation to the record's own sources;
see the [contribution protocol](docs/contribution-protocol.md) for the format and
review requirements. Briefs and handoffs preserve these gate-to-source links.

`sources` collects source references for manual rechecking. Both `--as-of` and
`--max-age-days` are required so repeated reviews are deterministic and no age
policy is assumed. The window includes its last day: at 30 days, a 30-day-old
source is within the window, while a 31-day-old source gets a review reminder.
The command also flags future access dates and local file references that another
reviewer may not be able to access. It performs no network requests or reads of
referenced local files and changes no records or gates.

Omit `--needs-review` to show every source, or add `--format json` for structured
output. Shared URLs stay separate when cited by different records, preserving
their individual source IDs and access dates. Review reminders return exit code
`0`; invalid records return `1` and invalid review arguments return `2`.

## Operator Loop

To clone Humanifest and run a safe bot-style discovery process, start with the
read-only operator loop:

```bash
python3 -m humanifest.cli operate --root . --as-of 2026-09-11 --max-age-days 30
```

The loop validates the portfolio, finance ledger, compute registry, and cause
records; identifies stale sources and top cause pathways; and reports safe next
actions. It does not contact maintainers, post comments, open pull requests,
fetch remote sources, publish packages, or mutate records.

See [Bot Operator Runbook](docs/bot-operator-runbook.md) for clone setup,
scheduled automation, bot identity, donated compute, and the contribution loop.
See [Adopt Humanifest](docs/adoption.md) for the short path to running your own
Humanifest-style bot.

## Repository Map

- `humanifest/`: deterministic Python core.
- `schemas/`: public JSON schema documents.
- `portfolio/causes/`: metric-guided cause-area discovery records.
- `portfolio/projects/`: audited project records.
- `portfolio/opportunities/`: issue-level opportunity records.
- `portfolio/contributions/`: future contribution records.
- `docs/`: protocol, methodology, research, and governance.
- `handoffs/`: bounded prompts for Codex, Spark, Cursor, and reviewers.
- `tests/`: offline unit tests.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) before opening work. The best first
contributions are small and evidence-preserving:

- refresh a stale source review;
- improve an opportunity record without advancing unsupported gates;
- add tests for validation, scoring, or report behavior;
- clarify documentation where the workflow is hard to follow;
- adversarially review a handoff or proposed implementation.

Do not contact external maintainers, post issue comments, open upstream pull
requests, or submit AI-generated reviews on behalf of Humanifest unless the
current protocol and authorization explicitly allow it.

If you want to help spread the project, use [Outreach](docs/outreach.md) for
maintainer-safe language and [Adopt Humanifest](docs/adoption.md) for the
clone-and-run path.

## Donations

Donations support Humanifest's coordination work: evidence review, maintainer
communication, reproducible environments, adversarial review, and small,
maintainer-approved contributions to humanitarian and public-interest open
source. Sponsorship is not a purchase of influence, priority, outreach, ranking,
or a guaranteed upstream contribution.

Humanifest is currently fiscally administered by Avaelus LLC/Inc. Humanifest
funds should be tracked separately from Avaelus operating funds, with conflicts
and aggregate public finance records handled under
[finance governance](docs/finance-governance.md).

Use [GitHub Sponsors](https://github.com/sponsors/humanifest) or this
repository's Sponsor button. Funding configuration lives in
[.github/FUNDING.yml](.github/FUNDING.yml).

## Compute Resources

Humanifest can use donated, free, sponsored, paid, or self-hosted compute when
the provider's terms and Humanifest's gates allow it. Extra compute should reduce
review burden and improve verification; it must not increase unsolicited
maintainer contact, bypass provider limits, pool personal accounts, or substitute
model output for cited evidence.

Compute-resource policy lives in [docs/compute-governance.md](docs/compute-governance.md)
and the public registry lives in
[portfolio/compute-resources.json](portfolio/compute-resources.json). Validate it
with:

```bash
python3 -m humanifest.cli compute --root .
```

## License

Humanifest is licensed under the [MIT License](LICENSE). See
[docs/licensing.md](docs/licensing.md) for licensing notes and contribution
expectations.

## Non-Goals

Humanifest is not a dashboard, hosted service, autonomous GitHub bot, issue spammer, database server, LLM framework, or impact-ranking oracle.
