# Humanifest contribution cycle — 2026-10-07

Public source access date: 2026-10-07 UTC. This is an evidence-linked research
handoff, not a donation, upstream acceptance, or canonical portfolio update.
GitHub reads used `python3 -m scripts.bot_github api` on the identity-guarded bot
connection. No target repository was cloned or changed; no test, build, post,
or notification read-state mutation ran.

## Bot inbox and previous donations

The `all=true` [GitHub notifications](https://github.com/notifications) query
returned the same two already-read threads, [Open Food Facts PR #504](https://github.com/openfoodfacts/openfoodfacts-python/pull/504)
and [Kobo issue #7259](https://github.com/kobotoolbox/kpi/issues/7259), and no
unread threads. Their full discussions, OFF inline review comments, Kobo
[PR #7260](https://github.com/kobotoolbox/kpi/pull/7260) comments and inline
comments, and the full [CHT #10155](https://github.com/medic/cht-core/issues/10155)
discussion were checked for new requests and duplicate replies. No relevant
reply or change since the October 5 cycle was found. Kobo PR #7260 remains open
at head `9cb53877c76a0c0ed97c317c988bea7c8b6d35a8`; the September 14
changes-requested review remains the latest review. No response was posted.

## Contribution lane: precise Kobo same-second test seam

The [Kobo #7259 author response](https://github.com/kobotoolbox/kpi/issues/7259)
confirms that `_date_modified` has one-second granularity and is a change
indicator, not an exactly-once cursor. Consumers should use `$gte` or an overlap
window and deduplicate `_id`. The author welcomed a frozen-time same-second
test and short note on the author's
[`add-submission-date-modified` branch](https://github.com/kobotoolbox/kpi/pull/7260),
while deferring broader docs to the Kobo team.

The current PR head's
[`kpi/tests/api/v2/test_api_submissions.py`](https://github.com/kobotoolbox/kpi/blob/9cb53877c76a0c0ed97c317c988bea7c8b6d35a8/kpi/tests/api/v2/test_api_submissions.py)
already has `test_list_submissions_filter_by_date_modified` near line 1620.
It checks `$gt` and `$lt` across different days with `freeze_time`, and it
updates an existing `Instance` plus its Mongo projection synchronously. The
smallest author-coordinated test would extend this case with two *meaningful*
updates to the same submission within one second: assert that a strict `$gt`
cursor at the first observed timestamp misses the second state, while an
overlapping `$gte` fetch includes the `_id` for consumer deduplication. A
short note should state that this is consumer behavior, not a guarantee that
all intermediate states can be recovered. The exact mutation and response
assertions still need a target-worktree inspection. No target code or test was
written or run here. A small upstream PR requires author coordination, current
hard-gate review, bot identity verification, and specific external-write
authority; this issue's encouragement alone is not authority to open one.

## Discovery lane: OpenAQ documentation

The initial malaria-specific search did not yield a bounded eligible patch.
[OpenMalaria](https://github.com/OpenMalaria-Org/openmalaria) is active, but its
remaining standalone open issues are old XSD sampler and wiki design work
([#427](https://github.com/OpenMalaria-Org/openmalaria/issues/427),
[#416](https://github.com/OpenMalaria-Org/openmalaria/issues/416)); neither
has a small agreed acceptance path. [malariaAtlas](https://github.com/malaria-atlas-project/malariaAtlas)
has only stale standalone issues and unresolved license metadata. Both are
parked. The search then followed the existing air-pollution-data cause pathway.

**New candidate:** [`openaq/docs.openaq.org`](https://github.com/openaq/docs.openaq.org)
is a public, unarchived documentation repository, pushed September 29, 2026,
at [main `740fb4a`](https://github.com/openaq/docs.openaq.org/commit/740fb4a0b59aeeb2d5ff4c87d77781c64caf12b7).
Clearer air-quality API documentation could reduce mistakes by public-data
consumers; no downstream health benefit is established. Its open, unassigned,
uncommented [issue #4](https://github.com/openaq/docs.openaq.org/issues/4)
asks for better `datetime_min` documentation for Latest endpoints. The issue
was last updated May 5, 2025, but the current
[Latest guide](https://github.com/openaq/docs.openaq.org/blob/740fb4a0b59aeeb2d5ff4c87d77781c64caf12b7/src/content/docs/resources/latest.mdx)
still omits `datetime_min`. Its existing warning explains that Latest is
measurement-time based and is not a complete incremental polling feed. The
[location Latest API reference](https://docs.openaq.org/api/operations/location_latest_get_v3_locations__locations_id__latest_get)
labels the parameter only "Minimum datetime." A bounded GitHub search found
no `datetime_min` use in this docs repository, and no open PR in the repo.

The [OpenAQ API router at `87c060c`](https://github.com/openaq/openaq-api/blob/87c060c28f5b484e0e9953d247082f5e678935c9/openaq_api/v3/routers/latest.py)
implements `datetime_last > :datetime_min` for both location and parameter
Latest endpoints. Explicit timezone offsets are used directly; a date or
datetime without a timezone is interpreted in the location timezone. The
[API unit tests](https://github.com/openaq/openaq-api/blob/87c060c28f5b484e0e9953d247082f5e678935c9/tests/unit/test_v3_queries.py)
cover the date, timezone-less, and explicit-offset query forms. This is source
behavior, not a live API test. The candidate edit is a short Latest-guide
section covering the strict comparison, timezone interpretation, a small
request example, and the existing incomplete-polling caution, with links to
the API reference. Do not author the target patch until the gates below pass.

**Policy and review:** the organization's
[contribution guide](https://github.com/openaq/.github/blob/main/CONTRIBUTING.md)
welcomes outside documentation PRs and requires its
[LLM policy](https://github.com/openaq/.github/blob/main/LLM_POLICY.md): disclose
LLM use, understand the contribution, and expect wholly LLM-written work to
be unlikely to be accepted. The docs repository's
[NOTICE](https://github.com/openaq/docs.openaq.org/blob/740fb4a0b59aeeb2d5ff4c87d77781c64caf12b7/NOTICE)
separately labels code Apache-2.0 and documentation content CC BY-NC-SA 4.0;
it prohibits using docs content as model training data without prior written
permission, and separately prohibits using it as the primary or substantial
source for an AI-powered tool. Applicability
to the proposed assistance needs a conservative project-specific check; no
legal or maintainer approval is inferred. The repo has no open PRs, and prior
documentation PRs [#8](https://github.com/openaq/docs.openaq.org/pull/8)
and [#6](https://github.com/openaq/docs.openaq.org/pull/6) merged, showing a
review path, but not a commitment to review this issue. Exact next gate:
confirm AI-assisted documentation work is permitted under the NOTICE and org
policy; then secure a narrow maintainer scope/reviewer for #4 and specific bot
posting/PR authority before an upstream write. Target build entry points and
side effects must be inspected before any local build.

Other air-quality leads were rejected for this cycle:
[AirGradient map #439](https://github.com/airgradienthq/airgradient-map/issues/439)
is assigned, while [#441](https://github.com/airgradienthq/airgradient-map/issues/441)
needs a fresh Android reproduction;
[`openaq-fetch`](https://github.com/openaq/openaq-fetch) labels itself
maintenance-only; and [ingestor #24](https://github.com/openaq/openaq-ingestor/issues/24)
already reports its main outage fixed, with distinct new issues suggested for
the remaining symptoms. None is promoted as a fresh patch.

No lead was promoted to `portfolio/`: the project-specific policy and
maintainer screens remain open, and an Orca/source-of-truth route was not
available in this run. No upstream contribution was implemented, tested,
accepted, posted, or activated.
