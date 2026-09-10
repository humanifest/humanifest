# MetaData Sync native baseline and indicator-type workflow

Accessed September 10, 2026. Revision
`78c8b8c22278dcbb7d2d5678eaafaa80b0fd0cf9`. This follow-up replaces the earlier
schema-adapter limitation for the paths tested here; it does not establish
browser behavior, an actual server update, accepted scope or humanitarian impact.

## Verified behavior

**13 unchanged upstream tests pass:** ten MetadataPayloadBuilder tests, two
metadata synchronization integration tests, and one local-instance mapping test.
These use original project code and its existing synthetic repositories or
Mirage endpoints. No original test assertion was changed.

**Four additional probes pass** using the installed project and original classes:

- The original factory resolves both indicator-type names to `indicatorTypes`.
- The original mapper rewrites a supplied indicator-type reference, retains
  constant numerator/denominator expressions, and leaves input data unchanged.
- A mapping survives save/read through the original MappingD2ApiRepository and
  DataSourceMapping with an in-memory StorageClient boundary. The restored
  mapping is then applied by the original mapper. This is not a real DHIS2
  data-store persistence test.
- The original builder's default inclusion rules include the synthetic source
  indicator type. Applying the mapping changes its ID to the destination ID
  while retaining source `name`, `factor: 100` and `number: false`.

The new fixture is
[`fixtures/mdsync_indicator_workflow.spec.ts`](fixtures/mdsync_indicator_workflow.spec.ts).
Unlike the earlier isolated harness, it imports the original model factory,
mapper, parser, API schemas, builder and mapping repository. Its explicit mocks
are the synthetic metadata/instance repositories and memory storage boundary.
It does not supply a replacement mapping algorithm or schema-only model factory.

## Import-contract implication, with limits

The pinned MetadataSyncUseCase maps its built payload before repository save.
MetadataD2ApiRepository transforms that payload for the target version, then
passes defaults including `identifier: UID`, `importMode: COMMIT`,
`importStrategy: CREATE_AND_UPDATE` and `mergeMode: MERGE` to the API.

DHIS2 2.40 documentation describes matching imported objects by identifier and
updating supplied properties. It also marks MERGE as deprecated with limitations
for certain object types. The documentation is not evidence that this exact
payload was accepted by a server. No destination type with a different factor
was created or overwritten in these tests.

**Inference:** a mapped source type included in the payload could update an
existing destination type, subject to validation and import/version behavior.
The request should clarify reuse versus updating before a picker-only patch.
Do not expand #1255 into changing global import defaults or claim a deployed
calculation error. The next independent check is the original Global Mapping UI
with synthetic instances: confirm the missing option and picker/persistence
behavior before preparing a concise scope inquiry.

## Setup, corrections and reproducibility

The public source archive was 2,467,692 bytes. All **898 source blobs** matched
the pinned Git tree before installation and again after tests. No target clone
was placed in Humanifest. Working directory:

`/tmp/humanifest-mdsync-native/metadata-synchronization-78c8b8c22278dcbb7d2d5678eaafaa80b0fd0cf9`

Official Node **22.22.0** was extracted into the parent directory and verified
against its published SHA-256:
`5ed4db0fcf1eaf84d91ad12462631d73bf4576c1377e192d222e48026a902640`.
The immutable Yarn **4.12.0** install completed in 3m35s, with 1,974 packages and
648.99 MiB reported. Installed versions include TypeScript **4.9.5**, Vitest
**3.2.4** and lockfile-resolved lodash **4.18.1**. The earlier isolated probe used
lodash 4.18.0 and a different transpiler; the native checks use the project set.
No manifest or lockfile change was needed. Existing peer-dependency warnings
were retained, including React, styled-jsx, ESLint and the `d2` peer declaration.

**Correction to earlier setup wording:** `enableScripts: false` disables
third-party dependency postinstall scripts, **not workspace postinstall scripts**.
Yarn still ran the already inspected project localization command. It reported
missing `msgmerge`, but returned success; a successful install therefore does
not establish full localization/build readiness. Only tracked `i18n/en.pot`
changed. That output was preserved separately, then the file restored from the
verified archive before tests. Future installations should use
`yarn install --immutable --mode=skip-build` and run only separately audited
build steps. The previous claim that Yarn disabled all install scripts was too
broad and has been corrected in the linked audit and PR description.

Corepack, Yarn cache/global directories and temporary files were confined to the
new temporary work area. The installer used an explicit environment without
inherited credentials; an alternate local Yarn config filename retained the
repository settings without loading personal Yarn configuration. No global Node,
Yarn, gettext or shell configuration was changed.

Tests used the exact project Vitest configuration and one worker, inside macOS
`sandbox-exec` with `(deny network*)`. A separate local-listener control returned
`EPERM`, verifying the network denial. The profile cannot be nested inside the
existing tool sandbox, so its permitted execution was verified before testing.
No automatic approval rejection occurred. Test environment values included
`NODE_ENV=test`, `CI=1`, `BROWSER=none` and synthetic `VITE_DHIS2_BASE_URL`.

The selected baseline command after setup was:

```sh
node node_modules/vitest/vitest.mjs run \
  src/domain/metadata/builders/__tests__/MetadataPayloadBuilder.spec.tsx \
  src/data/metadata/__tests__/integration/sync-metadata.spec.ts \
  src/data/metadata/__tests__/integration/local-instance-mapped.spec.ts \
  --maxWorkers=1 --minWorkers=1 --no-file-parallelism
```

For the additional checks, copy the fixture to
`humanifest-probes/indicator-workflow.spec.ts` in that external checkout and run
that path with the same runner/configuration/isolation. The extra file is not a
production patch. Logs and JSON receipts are under `/tmp/humanifest-mdsync-native`:
`install.log`, `baseline-results.json`, `workflow-results.json` and their logs.

Not run: whole application test suite, full TypeScript check, localization/build
verification, browser flow, real storage/API import, or production deployment.
The native baseline covers these selected tests only.

## Sources

All accessed September 10, 2026:

- [Pinned source](https://github.com/EyeSeeTea/metadata-synchronization/tree/78c8b8c22278dcbb7d2d5678eaafaa80b0fd0cf9)
- [Original metadata integration tests](https://github.com/EyeSeeTea/metadata-synchronization/blob/78c8b8c22278dcbb7d2d5678eaafaa80b0fd0cf9/src/data/metadata/__tests__/integration/sync-metadata.spec.ts)
- [Original payload-builder tests](https://github.com/EyeSeeTea/metadata-synchronization/blob/78c8b8c22278dcbb7d2d5678eaafaa80b0fd0cf9/src/domain/metadata/builders/__tests__/MetadataPayloadBuilder.spec.tsx)
- [Original mapping repository](https://github.com/EyeSeeTea/metadata-synchronization/blob/78c8b8c22278dcbb7d2d5678eaafaa80b0fd0cf9/src/data/mapping/MappingD2ApiRepository.ts)
- [Original metadata importer](https://github.com/EyeSeeTea/metadata-synchronization/blob/78c8b8c22278dcbb7d2d5678eaafaa80b0fd0cf9/src/data/metadata/MetadataD2ApiRepository.ts)
- [DHIS2 2.40 metadata import contract](https://docs.dhis2.org/en/develop/using-the-api/dhis-core-version-240/metadata.html)
- [Yarn enableScripts semantics](https://yarnpkg.com/configuration/yarnrc#enableScripts)
- [Yarn install build-mode options](https://yarnpkg.com/cli/install)
- [Official Node checksums](https://nodejs.org/dist/v22.22.0/SHASUMS256.txt)
- [Shared test workflow inspected](https://github.com/EyeSeeTea/github-workflows/blob/master/.github/workflows/app-test.yml)
- [Shared build workflow inspected](https://github.com/EyeSeeTea/github-workflows/blob/master/.github/workflows/bundlemon-build-size.yml)
