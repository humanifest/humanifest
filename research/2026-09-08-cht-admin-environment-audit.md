# CHT #10155: admin test environment audit

This is the earlier read-only audit. The subsequent
[runtime verification](2026-09-08-cht-admin-runtime-verification.md) completes the
focused local baseline setup and controller reproduction under the user's
standing direction to continue independent verification. Its measured results
supersede this note's unverified execution status; maintainer confirmation and
rendered-modal/video work remain outstanding.

Read-only inspection on 2026-09-08. The opportunity remains in
`MAINTAINER-CHECK`; no reply to the Humanifest inquiry was present when checked.
No CHT setup, build, test, container, or application was executed in this audit.

## Revision and method

Inspected committed files from the existing external checkout at
`35b2bb6dac0844bee3228476591d08d56c5dd10d` using Git's object reader, not the
uncommitted preparation patch. The nine modified files in that checkout remain
untouched. Upstream `master` now resolves to
`372677567640d1d3e77e6e46f168fe69a8a9e218`. GitHub's
[comparison](https://github.com/medic/cht-core/compare/35b2bb6dac0844bee3228476591d08d56c5dd10d...372677567640d1d3e77e6e46f168fe69a8a9e218)
reports one additional commit changing infodoc source and integration tests;
none of the directly inspected setup files changed. Recheck before execution.

## Findings that change the setup plan

All linked sources below were inspected on 2026-09-08 at the pinned revision.

| Observed requirement | Evidence | Consequence |
| --- | --- | --- |
| Node >=22.15.0 and npm >=10.9.0; root workspaces are `shared-libs/*`. | [Root manifest](https://github.com/medic/cht-core/blob/35b2bb6dac0844bee3228476591d08d56c5dd10d/package.json) | Root installation does not install the separate admin package. Minimum declared versions are not proof that an arbitrary newer runtime works. |
| Root hooks invoke patch-package and Husky. A workspace postinstall removes its own dist directory and builds with TypeScript. | [Datasource manifest](https://github.com/medic/cht-core/blob/35b2bb6dac0844bee3228476591d08d56c5dd10d/shared-libs/cht-datasource/package.json), [patches](https://github.com/medic/cht-core/tree/35b2bb6dac0844bee3228476591d08d56c5dd10d/patches), [commit hook](https://github.com/medic/cht-core/blob/35b2bb6dac0844bee3228476591d08d56c5dd10d/.husky/pre-commit) | The previous list of two root hooks understated project-controlled execution. Both dependency patches and the branch-protection hook were read. |
| Admin has its own manifest and lockfile; Karma loads modules from both dependency directories. | [Admin manifest](https://github.com/medic/cht-core/blob/35b2bb6dac0844bee3228476591d08d56c5dd10d/admin/package.json), [admin lockfile](https://github.com/medic/cht-core/blob/35b2bb6dac0844bee3228476591d08d56c5dd10d/admin/package-lock.json), [Karma config](https://github.com/medic/cht-core/blob/35b2bb6dac0844bee3228476591d08d56c5dd10d/admin/tests/karma-unit.conf.js) | Installing only root dependencies is insufficient. |
| Karma consumes `api/build/static/admin/js/main.js` and `templates.js`. | Karma config above; [browser bundler](https://github.com/medic/cht-core/blob/35b2bb6dac0844bee3228476591d08d56c5dd10d/scripts/build/browserify-admin.sh), [template builder](https://github.com/medic/cht-core/blob/35b2bb6dac0844bee3228476591d08d56c5dd10d/scripts/build/build-angularjs-template-cache.js) | Generate both bundles before running tests, and rebuild after relevant source/template changes. A stale bundle could test old code. |
| `unit-admin` launches Chrome in single-run mode; its launcher specifies remote debugging port 9222. Karma's server port and bind address are not explicitly set in this project config. | [Runner](https://github.com/medic/cht-core/blob/35b2bb6dac0844bee3228476591d08d56c5dd10d/scripts/ci/run-karma.js), Karma config above | A Chrome executable and verified internal-only listeners are needed. Empty services/ports lists were misleading. |
| The broad build path installs webapp and admin dependencies and builds more than the admin bundles. CI runs a full compile/integration pipeline. | [Build preparation](https://github.com/medic/cht-core/blob/35b2bb6dac0844bee3228476591d08d56c5dd10d/scripts/build/build-prepare.sh), [module installer](https://github.com/medic/cht-core/blob/35b2bb6dac0844bee3228476591d08d56c5dd10d/scripts/build/index.js), [CI](https://github.com/medic/cht-core/blob/35b2bb6dac0844bee3228476591d08d56c5dd10d/.github/workflows/build.yml) | Do not treat full CI as a minimal local unit-test recipe or import its publishing credentials. A narrower admin sequence remains a hypothesis to validate. |

The tracked tree has no `.devcontainer` configuration at this revision. The
previous runner recommendation therefore did not identify an actual inspected
environment. CPU, memory and disk numbers in the old plan were estimates, not
measurements.

## Execution remains unverified

The [root lockfile](https://github.com/medic/cht-core/blob/35b2bb6dac0844bee3228476591d08d56c5dd10d/package-lock.json)
marks multiple dependencies with install scripts, including browser-driver and
native packages. The root manifest also names a Git-hosted dependency. These flags
identify further inspection work; they do not prove what each installer executes.
The admin lockfile marks a core-js install script. Dependency hook contents and
all potential download destinations were not audited here.

No application secret reference was found in the inspected unit-test launcher or
Karma configuration. That bounded finding does not certify the entire dependency
graph. No runner image, Dockerfiles/Compose runtime, mounts, privileges, or live UI
environment has been approved by this audit. The synthetic-data video requested
in prior review needs a separate runtime plan.

After maintainer confirmation, inspect a disposable runner and remaining setup
code, install the locked root and admin dependencies, generate the two admin
bundles, and run `npm run unit-admin` on untouched upstream before testing any
patch. Record actual runtime versions, commands, output, elapsed time, and
resource use. If the minimal sequence fails, investigate the missing dependency
instead of silently invoking the entire build pipeline. Do not claim reproduction
or a passing regression test from this source inspection.

The updated environment plan captures these prerequisites. The current
opportunity's `environment_feasible` gate is now false until feasibility is
demonstrated; maintainer confirmation and reproduction remain false as well.
