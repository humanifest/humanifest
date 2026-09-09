# Humanifest

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
python3 -m humanifest.cli report --root .
python3 -m humanifest.cli work --root . --as-of 2026-09-08
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
prints JSON for use by other tools. `validate`, `report`, `work`, and `sources` require both portfolio
record directories and check unique record IDs, opportunity-to-project links, and
the implementation and PR capacity limits above. Single-record commands cannot
check portfolio capacity; validate the full portfolio before starting work.

Reports show capacity, blockers, and state-specific next actions in state/ID order.
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

`work` shows recorded independent research alongside active work and review
reminders, so waiting for a reply need not stall other useful contributions.
Use optional opportunity fields `research_next_step` for a concrete permitted
research step and `next_external_status_check` for a planned review date in
`YYYY-MM-DD` form. Remove a research step when completed. These fields do not
approve implementation, pass gates, or schedule an automation.

The required `--as-of` date separates reviews due on or before that day from
later reviews. Missing review dates are shown separately, not treated as a
reason to poll on every run. Relevant new feedback can be handled sooner.
Parked and declined records are excluded; explicit post-merge follow-up dates
remain visible. Items are ordered by ID, not ranked by impact. Early-stage
candidates without a next step or review date remain visible under
**Candidates needing a research plan**.
Assess those existing leads and record a bounded research step or a reason to wait
or stop. They are not implementation-ready work. The view suggests finding another
bounded opportunity only when no active work, independent research or such
unplanned candidate remains. Candidates with a review date stay in the review
sections until an independent step is recorded. Add `--format json` for structured
output; `needs_research_plan` contains the unplanned candidates.
The command validates the whole portfolio and performs no network requests or
record changes.

## Repository Map


- `humanifest/`: deterministic Python core.
- `schemas/`: public JSON schema documents.
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

## Donations

Donations support Humanifest's coordination work: evidence review, maintainer
communication, reproducible environments, adversarial review, and small,
maintainer-approved contributions to humanitarian and public-interest open
source. Sponsorship is not a purchase of influence, priority, outreach, ranking,
or a guaranteed upstream contribution.

Use [GitHub Sponsors](https://github.com/sponsors/humanifest) or this
repository's Sponsor button. Funding configuration lives in
[.github/FUNDING.yml](.github/FUNDING.yml).

## License

Humanifest is licensed under the [MIT License](LICENSE). See
[docs/licensing.md](docs/licensing.md) for licensing notes and contribution
expectations.

## Non-Goals

Humanifest is not a dashboard, hosted service, autonomous GitHub bot, issue spammer, database server, LLM framework, or impact-ranking oracle.
