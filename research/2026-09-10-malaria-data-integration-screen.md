# Malaria data integration: MetaData Sync research seed

Accessed September 10, 2026. Public source review only; no target clone,
installation, service execution, patient data, outreach or implementation.

Follow-up: [mapping audit and seven isolated original-code checks](2026-09-10-mdsync-mapping-audit.md) refine the source hypothesis and setup limits below. No full app reproduction is claimed.

## Why this software path

WHO's July 2025 national malaria repository guidance describes DHIS2-based
repositories and recommends MetaData Sync for metadata and data exchange across
instances (Annex 5, printed pp. 69–70). It also describes OpenHEXA/DHIS2 hybrid
integration in several countries (Box 4, printed p. 42). This is a specific
software-to-cause pathway, not evidence that a proposed patch will improve health.

The DHIS2 App Hub lists MetaData Sync v2.25.0, compatibility with DHIS2 2.37–2.42,
and funding from the WHO Global Malaria Programme and other health organizations.
The maintainer's March 2025 account explains its use for cross-instance mapping
and metadata packages. These support relevance and a release channel; neither
establishes contribution-specific deployment or measurable time savings.

## Bounded candidate comparison

The public API returned 57 open items without another page: **46 standalone
issues and 11 PRs**. The repository is unarchived, was pushed August 24, 2026,
and has a July 13 release of v2.25.0. Its `development` head is pinned at
`78c8b8c22278dcbb7d2d5678eaafaa80b0fd0cf9` (commit July 29). A later repository
push timestamp does not imply that this branch advanced on that date.

- **#1255, indicator-type mapping:** the July 2026 issue reports that users
  cannot remap differing indicator types through Global Settings. It requests
  the existing mapping pattern for this metadata type. It is unassigned with
  no comments; the inspected timeline contains project events but no linked PR.
  This is the first source-audit candidate, not proof of an unfixed runtime bug.
- **#1261, unmapped organization-unit filter:** describes difficulty finding
  remaining unmapped units in large trees. A possible second candidate, with no
  measured burden or selected implementation scope.
- **#1256, null/zero values:** explicitly calls for work with affected teams to
  distinguish configuration differences from an application defect. Do not
  assume a bug or seek operational instances; defer this candidate.
- **#1259, clearer sync errors:** wider parsing, lookup and guidance changes
  need a curated error set and agreed classification. Defer in favor of the
  narrower metadata-mapping question.

The full open inventory includes existing mapping fixes (#1051 and #1251),
package generation (#1050), and history preservation (#1052). Their titles do
not establish overlap with #1255; inspect their scope before proposing a patch.
No competing contribution has been started.

## Pinned source observation and next action

At the pinned revision, `InstanceMappingPage.tsx` lines 57–67 list seven global
mapping models and omit indicator types. `src/models/dhis/mapping.ts` defines
the corresponding global models. This agrees with the reported missing option;
it does not prove that adding a model is sufficient. The mapping dialog delegates
model construction to `modelFactory`, while `ApplyMappingUseCase` updates the
mapping dictionary. Outgoing metadata-reference transformation remains to trace.

The manifest invokes localization after installation and has a prepare hook.
Vitest loads environment values and `src/tests/setup.ts` with jsdom. Inspect
those hooks, setup and dependencies before any install or execution.

Added the project and #1255 as **OPPORTUNITY-RESEARCH**, with a concrete independent
step: trace indicator-type reference rewriting, compare #1051/#1251, and audit
the test path before a synthetic original-code reproduction. No implementation,
maintainer-acceptance or review date is implied by queueing this research.

## Contribution and environment limits

The repository community profile has no contributing file; the organization
`.github` lookup returned 404. Neither observation establishes permission for
AI/bot contributions or absence of contributor agreements. The PR template asks
for an issue reference, implementation, visual evidence, test guidance and any
companion library changes. The App Hub asks prospective feature contributors to
contact the team. Humanifest scope and reviewer confirmation remain missing.

The README describes Yarn 4.12.0, a DHIS2-backed app, migrations, a scheduler and
unit tests. Its global shell/tool changes and sample remote connections were not
executed. Any local reproduction needs a separate audit of manifests, hooks,
CI, network defaults and test fixtures; use synthetic metadata only. No claim
about environment feasibility or passing upstream tests follows from this read.

## Other paths screened

The DHIS2 core contribution guide requires linked Jira issues and core review.
A 2024 malaria-community reporting-rate complaint concerns version 2.39; its
current resolution was not established. The library accessibility umbrella
#1447 directs contributors to individual component tickets and coordination,
but does not establish an available malaria-specific defect. Keep these as
unselected leads rather than treating old open pages as current work.

## Sources

All accessed September 10, 2026:

- [WHO national malaria repository guidance, July 2025](https://cdn.who.int/media/docs/default-source/malaria/surveillance/guidance-on-establishing-a-national-malaria-data-repository-version-1.0-july-2025.pdf)
- [MetaData Sync App Hub listing](https://apps.dhis2.org/app/fd5f3f76-e306-477e-bcb6-3a28cdc784dd)
- [Maintainer use-case account](https://eyeseetea.com/metadata-sync-dhis2/)
- [Repository metadata](https://api.github.com/repos/EyeSeeTea/metadata-synchronization)
- [Open inventory](https://api.github.com/repos/EyeSeeTea/metadata-synchronization/issues?state=open&per_page=100)
- [Release v2.25.0](https://github.com/EyeSeeTea/metadata-synchronization/releases/tag/v2.25.0)
- [Pinned source](https://github.com/EyeSeeTea/metadata-synchronization/tree/78c8b8c22278dcbb7d2d5678eaafaa80b0fd0cf9)
- [Pinned mapping page](https://github.com/EyeSeeTea/metadata-synchronization/blob/78c8b8c22278dcbb7d2d5678eaafaa80b0fd0cf9/src/presentation/webapp/core/pages/instance-mapping/InstanceMappingPage.tsx)
- [Pinned manifest](https://github.com/EyeSeeTea/metadata-synchronization/blob/78c8b8c22278dcbb7d2d5678eaafaa80b0fd0cf9/package.json)
- [Pinned test configuration](https://github.com/EyeSeeTea/metadata-synchronization/blob/78c8b8c22278dcbb7d2d5678eaafaa80b0fd0cf9/vitest.config.ts)
- [Indicator-type mapping #1255](https://github.com/EyeSeeTea/metadata-synchronization/issues/1255)
- [Organization-unit filter #1261](https://github.com/EyeSeeTea/metadata-synchronization/issues/1261)
- [Null/zero investigation #1256](https://github.com/EyeSeeTea/metadata-synchronization/issues/1256)
- [Sync-error guidance #1259](https://github.com/EyeSeeTea/metadata-synchronization/issues/1259)
- [PR template](https://github.com/EyeSeeTea/metadata-synchronization/blob/78c8b8c22278dcbb7d2d5678eaafaa80b0fd0cf9/.github/pull_request_template.md)
- [DHIS2 core contribution guide](https://developers.dhis2.org/community/contribute/)
- [Historical malaria reporting-rate complaint](https://community.dhis2.org/t/reporting-rate-both-in-reports-and-data-visualizer-is-not-working-for-data-sets-using-category-combinations/58484)
- [DHIS2 UI accessibility umbrella](https://github.com/dhis2/ui/issues/1447)

Public API and selected source snapshots are in
`/tmp/humanifest-malaria-integration-screen`. They are local research inputs,
not a full repository or execution audit.
