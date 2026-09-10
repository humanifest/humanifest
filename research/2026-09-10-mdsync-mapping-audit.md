# MetaData Sync #1255: mapping path and isolated behavior

Accessed September 10, 2026. Target revision
`78c8b8c22278dcbb7d2d5678eaafaa80b0fd0cf9` (`development`). All 33 downloaded
source files match their Git blob IDs in the pinned, non-truncated source tree.
No target source was modified, full repository cloned, app installed, server
contacted or upstream message posted.

## Result and consequence for the proposed scope

The missing indicator-type option is supported by the pinned global-mapping
list. The underlying metadata machinery is more general: `modelFactory`
registers `IndicatorTypeModel`, and that model identifies the `indicatorTypes`
collection. `MetadataSyncUseCase.mapPayload` invokes `MappingMapper` when mapping
is enabled, before `postPayload` passes the result to the metadata repository.

Seven isolated checks execute the **entire unchanged MappingMapper class** and
its original metadata helpers. A supplied indicator-type mapping rewrites an
indicator's reference. With an included source type object, it also changes that
object's ID while retaining its source fields, including `factor` and `number`.
`IndicatorModel` lists indicator types among its inclusion rules, so this payload
shape deserves further investigation; it is not a contrived unrelated field.

This is a payload observation, **not a demonstrated destination overwrite**.
The server import mode, target validation, dependency selection and user-intended
meaning of remapping remain untested. A picker-only patch must not be presumed
complete: agree whether mapped types should be reused, excluded or updated, and
verify actual outgoing payload construction and server semantics first.

## Reproduction and boundaries

The reusable harness is
[`fixtures/mdsync_indicator_mapping_probe.cjs`](fixtures/mdsync_indicator_mapping_probe.cjs).
It requires already retrieved files and makes no downloads. Run:

```sh
node research/fixtures/mdsync_indicator_mapping_probe.cjs \
  /tmp/humanifest-malaria-integration-screen \
  /private/tmp/humanifest-cht-baseline/node_modules/typescript/lib/typescript.js
```

Observed environment: Node 22.16.0, TypeScript 5.8.3 transpilation, lodash 4.18.0,
and the published DHIS2 2.40 schemas from `@eyeseetea/d2-api` 1.21.0. This is not
the project's exact Node 22.22.0 / TypeScript 4.9.5 toolchain or a type check.
The two package archives (260,322 and 315,751 bytes respectively) were verified
against their npm SHA-512 integrity values before extraction; no package install
or lifecycle command was run. The target and d2-api declare GPL-3.0; lodash
includes its MIT license. No third-party source is redistributed in this commit.

The probe substitutes **schema-only API and model-factory adapters**. It loads
the actual published schemas, and runs original metadata name-resolution helpers
and mapper methods. It does not instantiate the full API or app model classes.
Unexpected imports, expression parsing, category-combo conversion and UID
validation throw if reached. The VM receives no network or filesystem API.
Inputs are synthetic metadata objects with no patient records or credentials.
This is neither an end-to-end app test nor an unchanged upstream test-suite run.

Assertions cover:

1. No mapping preserves the source reference.
2. Supplied mapping rewrites the indicator-type reference.
3. Disabled mapping preserves the reference.
4. An unrelated mapping leaves it unchanged.
5. Mapper lookup also applies a supplied mapping with `global: false`.
6. An included type receives the mapped ID and retains source fields.
7. Existing category-option reference mapping remains functional.

Every case checks that the input payload is unchanged. The harness verifies
SHA-256 values for both original source modules, the schema and lodash before
and after execution. The raw receipt is
`/tmp/humanifest-malaria-integration-screen/mapper-results.json`.
Expressions, browser selection, saved/reloaded mappings, full sync-rule execution,
server imports and operational outcomes are outside these assertions.

## Existing contributions checked

- [PR #1051](https://github.com/EyeSeeTea/metadata-synchronization/pull/1051),
  head `28ac4deecdc49bc0518ac816e9c8f3a2d7ce86fa`, remains open. Its source
  changes pass the selected model into the mapping dialog to address category
  option listings. It overlaps the picker surface but adds no indicator-type
  option. The PR's test claims were not independently run here; disclosed AI
  assistance in an existing PR does not establish Humanifest bot eligibility.
- [PR #1251](https://github.com/EyeSeeTea/metadata-synchronization/pull/1251),
  head `7cd5140c51345ac9bbdb4d2e178bcffb20a52cc2`, remains open. It changes
  destination category-option-combo candidates and related fallback logic, with
  a new unit test. It does not add indicator-type mapping. Neither PR was copied,
  modified or superseded by a competing patch.

This is a bounded comparison of these two PRs, not an exhaustive duplicate search.

## Setup audit and remaining work

The repository's `.yarnrc.yml` specifies `enableScripts: false`, hardened mode,
checksum failures and a seven-day package age gate. This qualifies the earlier
manifest-only concern: installation hooks exist, but this Yarn configuration
already disables scripts. Preserve that setting. The `prepare`/`postinstall`
commands, Husky pre-push formatting/localization/tests and post-merge install
hook were read and not executed.

Vitest uses jsdom, loads environment values and runs `src/tests/setup.ts`, which
replaces fetch with an XHR polyfill for Mirage/Pretender interception. A mocked
transport does not itself prove that all network paths are blocked. The pinned
workflow delegates to a shared workflow on mutable `master`; that retrieved
workflow delegates testing and build jobs again. The transitive workflow audit
and full application dependency/fixture audit are incomplete. No secret or
operational configuration was retrieved.

The next independent research step is a full isolated test-path audit, followed
by original app/model and mapping-persistence checks using synthetic metadata.
Trace whether the native builder includes mapped indicator types and inspect the
import contract before proposing overwrite/reuse behavior. Keep #1255 at
**OPPORTUNITY-RESEARCH**; maintainer scope, bot eligibility, review acceptance and
real benefit remain unconfirmed. Other pending inquiries do not block this work.

## Sources

All accessed September 10, 2026:

- [Pinned source tree](https://github.com/EyeSeeTea/metadata-synchronization/tree/78c8b8c22278dcbb7d2d5678eaafaa80b0fd0cf9)
- [MappingMapper](https://github.com/EyeSeeTea/metadata-synchronization/blob/78c8b8c22278dcbb7d2d5678eaafaa80b0fd0cf9/src/domain/mapping/helpers/MappingMapper.ts)
- [Metadata utilities](https://github.com/EyeSeeTea/metadata-synchronization/blob/78c8b8c22278dcbb7d2d5678eaafaa80b0fd0cf9/src/domain/metadata/utils.ts)
- [MetadataSyncUseCase](https://github.com/EyeSeeTea/metadata-synchronization/blob/78c8b8c22278dcbb7d2d5678eaafaa80b0fd0cf9/src/domain/metadata/usecases/MetadataSyncUseCase.ts)
- [Model factory](https://github.com/EyeSeeTea/metadata-synchronization/blob/78c8b8c22278dcbb7d2d5678eaafaa80b0fd0cf9/src/models/dhis/factory.ts)
- [Metadata models and inclusion rules](https://github.com/EyeSeeTea/metadata-synchronization/blob/78c8b8c22278dcbb7d2d5678eaafaa80b0fd0cf9/src/models/dhis/metadata.ts)
- [Yarn settings](https://github.com/EyeSeeTea/metadata-synchronization/blob/78c8b8c22278dcbb7d2d5678eaafaa80b0fd0cf9/.yarnrc.yml)
- [Test setup](https://github.com/EyeSeeTea/metadata-synchronization/blob/78c8b8c22278dcbb7d2d5678eaafaa80b0fd0cf9/src/tests/setup.ts)
- [Shared workflow, unpinned retrieval](https://github.com/EyeSeeTea/github-workflows/blob/master/.github/workflows/master.yml)
- [d2-api 1.21.0 package metadata](https://registry.npmjs.org/@eyeseetea%2fd2-api/1.21.0)
- [lodash 4.18.0 package metadata](https://registry.npmjs.org/lodash/4.18.0)
