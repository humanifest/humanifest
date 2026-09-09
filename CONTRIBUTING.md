# Contributing

Humanifest protects maintainers from speculative AI-generated contribution noise. Contributions here should model that standard.

## Contribution lanes

Useful work is not limited to code. Good first contributions include:

- refreshing source access dates and flagging stale evidence;
- improving project or opportunity records while preserving provenance;
- tightening schemas, validators, reports, and tests;
- documenting confusing workflow steps;
- adversarially reviewing a candidate handoff or proposed implementation;
- preparing bounded implementation work only after every hard gate passes.

## Before opening nontrivial work

1. Open or identify an issue.
2. Confirm the maintainer wants the work.
3. Keep the change narrow and explainable.
4. Include tests or a clear reason tests do not apply.
5. Disclose AI assistance and retain human responsibility.

Do not submit mass formatting, dependency churn, broad rewrites, automated issue reports, or unsolicited AI-generated PR reviews.

Do not contact external maintainers, post issue comments, open upstream pull
requests, or make other external writes on behalf of Humanifest unless the
current protocol and authorization explicitly allow it. When communication is
authorized, use the verified Humanifest identity required by
[the contribution protocol](docs/contribution-protocol.md#communication-authorization).

Do not advance an opportunity record beyond the evidence it actually supports.
A useful negative finding, parked opportunity, or failed gate is a valid
contribution when it prevents low-quality work from reaching a maintainer.

Use a fork and a dedicated branch to submit a pull request against the intended
upstream base. Humanifest agents publish through `humanifest-bot`'s fork and
verify the PR identity and destination; upstream Write access is unnecessary.
Follow the [fork and PR workflow](docs/contribution-protocol.md#fork-and-pull-request-workflow)
for authorization, checks, attribution, and review expectations.

Humanifest is licensed under the MIT License. Contributors should use DCO signoff
unless the project later adopts a CLA; see [Licensing](docs/licensing.md).

## Donations and sponsorship

Sponsorship supports Humanifest coordination work, not donor direction over the
portfolio. Donations do not guarantee project selection, priority, maintainer
outreach, pull requests, merge outcomes, or favorable scoring. Conflicts of
interest should be disclosed in any contribution that affects project selection,
opportunity scoring, or public claims of impact.

## Development checks

The core suite and record checks run without third-party dependencies:

```bash
python3 -m unittest
python3 -m humanifest.cli validate --root .
python3 -m humanifest.cli report --root .
```

For the full CI checks, use a virtual environment and install the development
tools, then validate schemas and the installed package:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-checks.txt
.venv/bin/python -m scripts.check_schemas
.venv/bin/python -m scripts.check_install
```

The installation check builds a wheel with the installed build backend, creates a
temporary virtual environment, and runs every CLI command outside the checkout.
It uses no package index during build or installation and removes its temporary
environment afterward. Build artifacts in the checkout are ignored by Git.

CI runs these checks on Python 3.11 and 3.14 for pushes to `main` and pull requests.
It also compares `portfolio/status.md` with current report output. Refresh that
generated file using the README command whenever records or report formatting
change. CI has read-only repository permissions and does not contact maintainers,
publish packages, or change records.
