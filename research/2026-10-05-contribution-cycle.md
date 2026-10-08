# Humanifest contribution cycle — 2026-10-05

Access date for the linked public sources: 2026-10-05 UTC. This is a research
handoff, not a canonical portfolio update, maintainer acceptance, or donation.
All GitHub reads used the identity-guarded `scripts.bot_github` connection. No
upstream or target-repository write, clone, install, build, test, or post ran.

## Bot inbox and previous contributions

The `all=true` [GitHub notifications](https://github.com/notifications) query
returned the same two already-read threads: [Open Food Facts PR #504](https://github.com/openfoodfacts/openfoodfacts-python/pull/504)
and [Kobo issue #7259](https://github.com/kobotoolbox/kpi/issues/7259). Their
full issue comments, inline PR comments, and the full
[CHT #10155](https://github.com/medic/cht-core/issues/10155) discussion were
read. No new reply to Humanifest or duplicate response was found. Kobo
[PR #7260](https://github.com/kobotoolbox/kpi/pull/7260) is still open at head
`9cb53877c76a0c0ed97c317c988bea7c8b6d35a8`, with the same September 14
changes-requested review. OFF PR #504 is still open at head
`6d18df2fa2e45e65d8ad487e6f867d5a91f3023c`; its latest substantive
comment still asks about live integration tests or V2 parameter mapping. No
read state or discussion was changed. Kobo's author-welcomed same-second test
remains an unimplemented, author-coordination-dependent proposal.

## Contribution lane: OpenFn GitHub sync issue #5197

[OpenFn Lightning issue #5197](https://github.com/OpenFn/lightning/issues/5197)
remains open, unassigned, and without comments. The reporter says that setup
warned a new GitHub action would be committed to `main`, but observed the action
working from a non-main branch. The [adjacent PR #4722](https://github.com/OpenFn/lightning/pull/4722)
merged on October 5 at 08:27 UTC. It changed ancestor branch-conflict
validation, not the disputed copy. The current main revision is
[`58f3f2dc3676b371fc9bbd907d37397f9a4098c7`](https://github.com/OpenFn/lightning/commit/58f3f2dc3676b371fc9bbd907d37397f9a4098c7).

At that revision, the [GitHub sync component](https://github.com/OpenFn/lightning/blob/58f3f2dc3676b371fc9bbd907d37397f9a4098c7/lib/lightning_web/live/project_live/github_sync_component.ex)
labels `.github/workflows/openfn-pull.yml` for the repository's
`default_branch` and `openfn-<project>-deploy.yml` for the selected branch.
The [version-control implementation](https://github.com/OpenFn/lightning/blob/58f3f2dc3676b371fc9bbd907d37397f9a4098c7/lib/lightning/version_control/version_control.ex)
has separate writes: `push_pull_yml_to_default_branch` updates
`heads/#{default_branch}`, while `push_files_to_selected_branch` updates
`heads/#{repo_connection.branch}`. Its verification path also looks for those
files on those respective branches. This is source evidence of intended
two-branch behavior, **not** a live reproduction. The issue may reflect a
different action, a runtime defect, or a misunderstood GitHub view; neither
the issue report nor the source alone resolves that discrepancy.

Specific maintainer-ready request, **not posted**:

> I rechecked #5197 against main after #4722 merged. The setup component lists
> `openfn-pull.yml` on the repository default branch and the project deploy
> workflow on the selected branch. `push_pull_yml_to_default_branch` and
> `push_files_to_selected_branch` appear to implement that split. Could you
> share the repository default branch, selected branch, and links to the commits
> or workflow files from the case where `openfn-pull.yml` landed only on the
> selected branch? That would tell us whether the copy or a write path needs a
> fix. I have not run a live GitHub sync.

The next gate is a reproducible case and maintainer confirmation of the desired
contract, plus full AI/bot policy screening and target-specific posting
authority. Do not make a speculative copy patch. OpenFn's
[PR template](https://github.com/OpenFn/lightning/blob/main/.github/pull_request_template.md)
requires AI-use disclosure, and its [public AI policy](https://www.openfn.org/ai)
states accountability and transparency principles; the full interactive policy
and bot-account eligibility remain unverified.

## New project lead: OpenSRP FHIR Core

[OpenSRP FHIR Core](https://github.com/opensrp/fhircore) is a public,
unarchived, Apache-2.0 Android application for offline-capable health-worker
records and WHO Smart Guidelines. Its [project information](https://github.com/opensrp/fhircore/blob/main/docs/project-information/readme.mdx)
names malaria among care domains. This establishes a plausible route from
reliable patient registration to malaria program records, not a measured
malaria outcome. GitHub reported `pushed_at` 2026-09-03T10:51:33Z; a new
issue was opened September 28. The review cadence for outside work is not
yet established.

[Issue #3855](https://github.com/opensrp/fhircore/issues/3855) is open,
unassigned, and without comments. It has a concrete plan for a no-results
view and Add Person button after typed or QR search. Its acceptance criteria
also cover pagination, loading, questionnaire save/reset behavior, config,
docs, and tests. The scope is larger than a simple UI label. An open
[All Client PR #3853](https://github.com/opensrp/fhircore/pull/3853) touches
`RegisterViewModel.kt` and `RegisterPagingSource.kt`, which #3855 also names.
A title and issue-number search found no open PR claiming #3855, but #3853 is
a material code-overlap risk. It predates the issue and is not proven to
implement the requested behavior.

The [PR template](https://github.com/opensrp/fhircore/blob/main/.github/pull_request_template.md)
asks for an issue link, unit tests, UI strings, changelog, style checks, app
build/run, and review of config/content compatibility. A bounded repository
tree search found no named contribution, AI, bot, or agent policy file; the
public `opensrp/.github` repository lookup returned 404. Neither proves
bot-assisted contribution is accepted. No agreement requirement or qualified
reviewer was identified. Android/Gradle and remote Keycloak/FHIR dependencies
make an unplanned local setup high burden. No private patient data are needed
to assess the issue, but realistic workflow verification may require fixtures.

Next gate: establish external bot/AI contribution rules and reviewer path;
resolve overlap with #3853 and split #3855 into a maintainer-approved small
slice before target setup. Keep it a discovery lead, not a build-ready
opportunity. [Issue #3841](https://github.com/opensrp/fhircore/issues/3841)
is a more operationally consequential sync report but is too vague for a
bounded first task and names a device-specific eCHIS Uganda scenario. The
[DHIS2 Android Capture App](https://github.com/dhis2/dhis2-android-capture-app)
was also screened: active repository, but its complete open-issues page
contained only PRs and no standalone issue, so no new task was inferred from
its issue count.

No lead was promoted to `portfolio/`: the policy and overlap screens remain
open, and no Orca/source-of-truth route is available in this run.
