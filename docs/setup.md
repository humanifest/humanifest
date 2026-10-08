# Humanifest setup

This guide covers a local checkout and the repository's read-only automation.
It does not create accounts, install a GitHub credential, contact maintainers,
or grant permission to write upstream.

## Local development

Humanifest requires Python 3.11 or newer. The application itself has no runtime
dependencies, but the full checks use the pinned tools in
`requirements-checks.txt` and Node 22 for the Metamap compiler.

```bash
git clone https://github.com/humanifest/humanifest.git
cd humanifest
python3 --version
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -e .
.venv/bin/python -m pip install -r requirements-checks.txt
```

The editable install is optional; commands can also be run as
`python3 -m humanifest.cli` from the checkout. Do not put credentials or `.env`
files in this repository.

## Verify the checkout

Run the deterministic, offline checks from the repository root:

```bash
.venv/bin/python -m unittest
.venv/bin/python -m humanifest.cli validate --root .
.venv/bin/python -m humanifest.cli finance --root .
.venv/bin/python -m humanifest.cli compute --root .
.venv/bin/python -m humanifest.cli operate --root . --as-of "$(date -u +%F)" --max-age-days 30
.venv/bin/python -m humanifest.cli report --root .
```

For the full CI-equivalent check, install Node 22.12 or newer, then run:

```bash
npm ci --ignore-scripts --no-audit --no-fund --prefix tools/metamap
.venv/bin/python -m scripts.compile_correspondence --check
.venv/bin/python -m scripts.check_schemas
.venv/bin/python -m scripts.check_install
```

`npm ci` is limited to the checked-in Metamap compiler and lifecycle scripts are
disabled. The project does not require a target-project clone or target-project
dependency installation for its own checks.

## Automation

Yes: a fresh fork or deployment should normally enable the repository's existing
read-only jobs:

- `checks.yml` runs on pushes to `main` and pull requests.
- `operator-loop.yml` runs daily and on manual dispatch.

Both workflows use `contents: read`, disable checkout credential persistence, and
do not post comments, open issues or pull requests, publish packages, or mutate
records. Keep that permission boundary unless a separately reviewed workflow
and authorization are added. Scheduled automation is a reporting convenience,
not an authorization or maintainer-contact queue.

## Optional Humanifest bot

A bot is not required to bootstrap or run the read-only jobs. If a deployment
will perform external writes, create a dedicated Humanifest bot or machine user
under the provider's account rules; do not use a personal account. A human must
create the account and accept responsibility for its actions.

Before any write, the operator must have explicit authorization, applicable
protocol gates, an exact credential check proving the approved identity, and a
record of the evidence URL, access date, actor, timestamp, and outcome.

Store credentials only in the local authentication tool's secure store. Use
`python3 -m scripts.bot_github ...` for GitHub commands so the selected bot
credential is verified before the command runs. See
[`docs/github-identity.md`](github-identity.md) and the
[contribution protocol](contribution-protocol.md) for the required controls.

Do not add a write-capable token to GitHub Actions or create a write workflow as
part of setup. Bot identity, repository access, scopes, and any write workflow
require a separate security review and explicit authorization.
