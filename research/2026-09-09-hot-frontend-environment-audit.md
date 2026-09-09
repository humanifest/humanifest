# HOT frontend: test environment boundaries

Read-only source audit and disposable setup attempt on September 9, 2026.
Tasking Manager is pinned to `2b917a14ea7b0b76935c4e2d6985ab25764cd1c9`.
This extends the [download investigation](2026-09-08-hot-download-audit.md).
No implementation is approved by this audit, and frontend failure handling would
not restore archived extracts or resolve #7227 by itself.

## Inspected contribution and environment requirements

The pinned `AGENTS.md` and its required development setup, contributing,
contributing-guidelines, submit/review-PR, database-schema and dataflow documents
were read. Tests of existing behavior are explicitly welcome. Fork-based PRs,
current develop ancestry, scoped changes, frontend formatting and honest AI
assistance disclosure are required. Good-first-issue work is reserved for humans;
the previously inspected #7227 metadata contains only the `repo:tm` label.
Recheck labels before implementing. The linked full AI guide's human-review and
PR-description requirements remain applicable; no human review is claimed.

Some setup text is historical: it mentions Node 12+, older Flask/Python setup,
and deleting migration versions, while current agent instructions protect applied
migrations. Those backend/migration instructions are irrelevant to this frontend
baseline and were not executed. Source and current CI guide this bounded attempt:

| Location | Runtime/tooling stated |
| --- | --- |
| Frontend manifest | Volta Node 18.19.1 |
| PR frontend CI | Node 22.12.0; installs Yarn globally; lint, tests and build |
| Frontend Dockerfile | Node 22.13.0; debug and nginx stages expose 3000 |
| Local attempt | Existing Node 22.16.0 and Yarn Classic 1.22.22 |

This is not an exact CI/container reproduction. The inspected standalone setup
allows frontend and backend development independently. No OSM OAuth app, write-map
permission, staging API, PostgreSQL service or backend token is needed for mocked
component tests; none was requested or used.

## Executable boundaries

- `frontend/package.json` defines `test` as lint followed by CRACO/jsdom. It does
  not invoke `start`, `build`, environment preparation or static-asset generation.
- Both `start` and `build` invoke `build-sandbox-id`, which runs a nested plain
  `npm install` and `npm run all`. The locked editor's `all` command cleans/builds
  assets and rewrites locales. Its build-data script fetches preset data and
  interim icons from external hosts. Its optional server listens on port 8080.
- Main frontend `build` ends with a Sentry command that can inject and upload
  sourcemaps. The build workflow also loads environment variables/secrets and has
  a separate deployment stage. The PR workflow runs a build after tests and
  invokes reusable image-building configuration. These were inspected, not run.
- The Docker entrypoint unconditionally runs Yarn before its command; the image
  build also downloads an environment-substitution binary and runs `yarn build`.
  Neither Docker entrypoint nor image build is used for this test-only attempt.
- The root test setup starts MSW via `server.listen()` without an explicit
  unhandled-request rejection option. Test configuration still contains live
  default OSM/ohsome URLs. A mocked test environment alone is insufficient evidence
  that accidental live requests are impossible.
- `testWithIntl` imports the Redux store; the store starts browser-local
  persistence and subscribes to state changes. In jsdom this uses the test's
  storage. No real browser profile or account is loaded.

## Locked Git dependencies and install policy

The frontend lockfile resolves:

- `@osm-sandbox/sandbox-id` to
  `osm-sandbox/sandbox-iD@9e51118ca32676c17ed5fc5d20faccc078ebc2eb`.
- `react-placeholder` to
  `hotosm/react-placeholder@ef6301c4a017b91513c2c4b091d291d82d8b5916`.

The exact manifests were read. Neither has a `prepare` hook. The latter has a
`prepublishOnly` build; the former has explicit build/deploy commands and requires
Node >=20. An initial read of react-placeholder's default-branch manifest was
replaced by review of the exact locked revision; the moving branch is not the
installation authority.

The installed Yarn 1.22.22 implementation was inspected. Its lifecycle dispatcher
returns without execution when `ignoreScripts` is set. Its Git fetcher specially
installs/packs dependencies with a `prepare` script using a separate configuration,
so the absence of `prepare` in both locked Git manifests matters; do not assume
one flag covers an arbitrary future Git dependency. Tarball dependencies are still
subject to the disabled lifecycle-script policy.

A disposable sparse frontend checkout was created at
`/private/tmp/humanifest-hot-baseline`, detached at the pinned commit, with Git
credentials/hooks disabled during retrieval. The attempted install uses a minimal
child environment, no inherited credentials, no default Yarn rc files, empty npm
user/global configs, and a dedicated cache at
`/private/tmp/humanifest-hot-yarn-cache`:

```sh
yarn --no-default-rc install --frozen-lockfile --ignore-scripts \
  --non-interactive --network-concurrency 4 \
  --cache-folder /private/tmp/humanifest-hot-yarn-cache
```

Do not remove the frozen-lockfile constraint or enable all lifecycle hooks to make
an install pass. A missing built dependency should be traced to its specific
inspected build step. Neither `npm install` inside sandbox-iD nor any target build,
Sentry upload, deployment, account action or environment-preparation script is
part of this attempt.

## Installation outcome

The single install attempt reached the wrapper's 1,200-second limit during
package fetching. Yarn logged a network retry, then the wrapper terminated the
command with `subprocess.TimeoutExpired`; no completed dependency installation or
`node_modules` directory was available. The cache is retained for a later bounded
retry. The log does not identify the failing package or establish whether the
cause was a registry, Git host or local network condition. No lockfile constraint
was relaxed and no lifecycle scripts were enabled.

No HOT target tests, component reproduction, lint or build ran. The completed
contribution-policy audit supports that gate only; environment feasibility remains
unconfirmed. Next time, use one bounded diagnostic retry with the retained cache
and more informative fetch logging. If downloading still fails, record the exact
endpoint/error and move to independent queue work rather than repeatedly spending
compute on the same stalled install.

## Proposed first target test

After a successful locked install and inspection of the installed test entrypoint,
run the existing
`src/components/projectDetail/tests/downloadButtons.test.js` through CRACO/jsdom,
with `CI=true`, `--watchAll=false`, `--runInBand` and explicit `--runTestsByPath`.
Supply synthetic `.invalid` API/extractor endpoints, omit credentials and reject
real socket/DNS operations in the test process. Do not run `start` or `build`.

The existing test exercises the AOI link, not `DownloadOsmData`; passing it would
establish only a focused component-test baseline. A subsequent original-component
reproduction should cover unsuccessful HEAD results, null browser handles,
rejected requests and metadata failures, after verifying those imports and
preserving the target's policy boundaries.

A local Node preload guard was exercised against TCP connect, TLS connect, DNS
lookup and server listen. All four attempts threw before making a connection.
This guard is an accidental-network-use check, not an OS security boundary or
proof that arbitrary native code cannot bypass it. No target test result is
claimed until the actual runner completes.

## Sources

All Tasking Manager paths below refer to the pinned commit above:

- [Agent instructions](https://github.com/hotosm/tasking-manager/blob/2b917a14ea7b0b76935c4e2d6985ab25764cd1c9/AGENTS.md)
- [Development setup](https://github.com/hotosm/tasking-manager/blob/2b917a14ea7b0b76935c4e2d6985ab25764cd1c9/docs/developers/development-setup.md)
- [Contribution guidance](https://github.com/hotosm/tasking-manager/blob/2b917a14ea7b0b76935c4e2d6985ab25764cd1c9/docs/developers/contributing-guidelines.md)
- [Frontend manifest](https://github.com/hotosm/tasking-manager/blob/2b917a14ea7b0b76935c4e2d6985ab25764cd1c9/frontend/package.json)
- [Lockfile](https://github.com/hotosm/tasking-manager/blob/2b917a14ea7b0b76935c4e2d6985ab25764cd1c9/frontend/yarn.lock)
- [PR test workflow](https://github.com/hotosm/tasking-manager/blob/2b917a14ea7b0b76935c4e2d6985ab25764cd1c9/.github/workflows/pr_test_frontend.yml)
- [Frontend Dockerfile](https://github.com/hotosm/tasking-manager/blob/2b917a14ea7b0b76935c4e2d6985ab25764cd1c9/scripts/docker/Dockerfile.frontend)
- [CRACO configuration](https://github.com/hotosm/tasking-manager/blob/2b917a14ea7b0b76935c4e2d6985ab25764cd1c9/frontend/craco.config.js)
- [Test setup](https://github.com/hotosm/tasking-manager/blob/2b917a14ea7b0b76935c4e2d6985ab25764cd1c9/frontend/src/setupTests.js)
- [Locked sandbox-iD manifest](https://github.com/osm-sandbox/sandbox-iD/blob/9e51118ca32676c17ed5fc5d20faccc078ebc2eb/package.json)
- [Editor data builder](https://github.com/osm-sandbox/sandbox-iD/blob/9e51118ca32676c17ed5fc5d20faccc078ebc2eb/scripts/build_data.js)
- [Locked placeholder manifest](https://github.com/hotosm/react-placeholder/blob/ef6301c4a017b91513c2c4b091d291d82d8b5916/package.json)
