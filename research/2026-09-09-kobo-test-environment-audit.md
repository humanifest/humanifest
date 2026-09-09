# Kobo incremental-sync tests: environment audit

Source-only audit on September 9, 2026 of PR #7260 at
`7968471a4d86ab701f61537499ee080144b2bf3e`. A fresh API read confirms that the
PR remains open at this exact head. No target clone, installation, import, service
startup, test execution or external communication was performed in this audit.

## Contribution requirements

Read the pinned CONTRIBUTING, README, backend style guide, PR template, root
license and OpenRosa license notice. Contributions use a fork and branch from
main, tests, API documentation where relevant, lint and a self-reviewed PR. The
template asks for preview steps and reviewer follow-through. It also asks for a
Support Docs Updates Zulip thread for user-facing documentation changes; this
is a future scope consideration, not permission to send a message now.

The root license is AGPL v3. The OpenRosa notice preserves the inherited KoboCAT
BSD 2-Clause text and states that subsequent modifications/additions use AGPL v3.
No agreement was signed. License identification does not complete all security,
dependency or implementation review.

No explicit AI contribution policy was found in the inspected contribution,
README and PR-template text, nor in policy/agent filenames in the complete pinned
tree. That bounded absence is not acceptance. The existing scoped inquiry remains
pending; AI expectations and permission to add tests to another author's work
remain unresolved. Do not create a replacement PR.

## What the actual tests require

The five new `TestDateModified` tests inherit the real Django `TestBase`. Setup
creates/logs in a synthetic user, assigns permissions, publishes a fixture form
and makes fixture submissions. Tests read Django models and Mongo documents.
They cannot be run faithfully as a standard-library-only unit test.

`kobo.settings.testing` replaces Mongo with `mongomock.MongoClient`, runs Celery
tasks eagerly and substitutes a fake webpack loader. These choices avoid a real
Mongo server, worker and frontend bundle for this test surface. They do not remove
the relational database requirement: root autouse fixtures create an anonymous
user and query `pg_matviews`, creating the user-reports materialized view and
indexes when needed. Although testing settings offer a SQLite default, that is
not a demonstrated route through this PostgreSQL-specific fixture. Do not disable
the fixture or swap databases just to report a passing baseline.

The pinned CI backend matrix uses Ubuntu 24.04, Python 3.12, PostGIS
`postgis/postgis:14-3.4`, and Redis 6.2 on ports 5432/6379. It installs GDAL,
gettext, libproj, PostgreSQL client, ffmpeg and native build tools, then syncs
`dependencies/pip/dev_requirements.txt` and compiles translations. It runs pytest
in parallel and reruns failures sequentially. The relevant new file is in the
OpenRosa shard excluding its API directory. A later HTTP cursor regression also
needs the API paths, not only the existing five tests.

The inherited settings still configure Redis sessions/caches. They enable Sentry
when a DSN is supplied and configure storage/email from environment variables.
Any isolated runner must supply synthetic test configuration and omit production
credentials, DSNs and account settings. A future network boundary must permit
only the disposable test databases; a mock Mongo client is not a general egress
control. The root S3 fixture uses moto only when S3 storage is selected.

## Installation and startup boundaries

Read the exact Python input and compiled requirements, CI entry workflows,
Dockerfile, Docker entrypoint, migration wrapper, local CI wrapper and npm script
definitions. Python requirements pin Django 5.2.14, psycopg 3.3.4, pymongo 4.10.1,
mongomock 4.3.0 and uWSGI 2.0.31, among other dependencies. The compiled lists are
version/commit pins, not a hash-verified wheel lock. Native build requirements
must not be silently removed to make installation succeed.

Five Git dependencies are pinned by commit. Their exact setup manifests were
read: formpack, python-digest, django-digest, ssrf-protect and django-dont-vary-on.
They contain setuptools metadata, package discovery/dependency declarations and
optional test aliases; no custom command class or explicit deployment/network
call was found in those manifests. This does not audit all package code or make
Python source builds non-executable. Their build backends still need an isolated
installation boundary before execution.

The production Docker build runs npm lifecycle scripts, a frontend build, Python
dependency installation, system-package installation and static/translation setup;
it also pipes a remote Node setup script into bash. Its entrypoint synchronizes
dependencies, waits for databases, runs migration-repair scripts and migrations,
creates a superuser, may rebuild assets, synchronizes an nginx volume with deletion
enabled, then starts an application server on port 8000. The migration wrapper
can drop/recreate a materialized view and migrates both database aliases. None of
these production startup actions is needed merely to collect the five tests.

The recommended `ci_locally.sh` installs Playwright system dependencies, performs
npm CI/build/tests, then backend tests. For a bounded backend baseline, select
pytest directly inside an inspected disposable environment instead of invoking
that whole wrapper. Frontend preinstall runs `hint`; postinstall applies patches
and generates/copies fonts/icons. No frontend install or script was executed.

## Local availability and next decision

The host has a PostgreSQL 14 installation but no PostGIS extension control file
in its extension directory, no GDAL library in `/opt/homebrew/lib`, and no Redis
server on the inspected PATH. These are bounded host checks, not an exhaustive
search of all possible runtimes. The local Docker socket exists. The first read
was sandbox-denied; an approved read of that exact local socket returned
“Cannot connect to the Docker daemon.” No container was started or installed.

The next actual target test requires an available isolated Linux runner with the
CI dependencies. Do not repeatedly retry the unavailable engine or install a
different database silently. Once a runner exists, inspect its setup and execute
the unchanged five-test file against synthetic data; retain failures before
adding the agreed API boundary case. No environment-feasibility or reproduction
gate advances from this audit. Continue other queue work meanwhile.

## Sources

All accessed September 9, 2026, pinned to the PR head above:

- [PR #7260](https://github.com/kobotoolbox/kpi/pull/7260)
- [Contribution guide](https://github.com/RuneO/kpi/blob/7968471a4d86ab701f61537499ee080144b2bf3e/CONTRIBUTING.md)
- [PR template](https://github.com/RuneO/kpi/blob/7968471a4d86ab701f61537499ee080144b2bf3e/.github/PULL_REQUEST_TEMPLATE.md)
- [Root license](https://github.com/RuneO/kpi/blob/7968471a4d86ab701f61537499ee080144b2bf3e/LICENSE)
- [OpenRosa license notice](https://github.com/RuneO/kpi/blob/7968471a4d86ab701f61537499ee080144b2bf3e/kobo/apps/openrosa/LICENSE)
- [CI test setup](https://github.com/RuneO/kpi/blob/7968471a4d86ab701f61537499ee080144b2bf3e/.github/workflows/pytest.yml)
- [Test settings](https://github.com/RuneO/kpi/blob/7968471a4d86ab701f61537499ee080144b2bf3e/kobo/settings/testing.py)
- [Autouse fixtures](https://github.com/RuneO/kpi/blob/7968471a4d86ab701f61537499ee080144b2bf3e/conftest.py)
- [Dependencies](https://github.com/RuneO/kpi/blob/7968471a4d86ab701f61537499ee080144b2bf3e/dependencies/pip/dev_requirements.txt)
- [Dockerfile](https://github.com/RuneO/kpi/blob/7968471a4d86ab701f61537499ee080144b2bf3e/Dockerfile)
- [Entrypoint](https://github.com/RuneO/kpi/blob/7968471a4d86ab701f61537499ee080144b2bf3e/docker/entrypoint.sh)
- [Local CI wrapper](https://github.com/RuneO/kpi/blob/7968471a4d86ab701f61537499ee080144b2bf3e/scripts/ci_locally.sh)

Exact Git dependency manifests: [formpack](https://github.com/kobotoolbox/formpack/blob/3bf65b74fe876a514cff839fb10c24470dd63de2/setup.py),
[python-digest](https://github.com/dimagi/python-digest/blob/9c77ff12e7d7fedf792b25fddd7f443e1d02206f/setup.py),
[django-digest](https://github.com/kobotoolbox/django-digest/blob/a417e901c55d7c0aee89e2aab719975f45dbec4e/setup.py),
[ssrf-protect](https://github.com/kobotoolbox/ssrf-protect/blob/9b97d3f0fd8f737a38dd7a6b64efeffc03ab3cdd/setup.py),
[django-dont-vary-on](https://github.com/trevoriancox/django-dont-vary-on/blob/01a804122b7ddcdc22f50b40993f91c27b03bef6/setup.py).
