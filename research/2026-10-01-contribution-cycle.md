# Contribution cycle findings — 2026-10-01

This is a read-only evidence and handoff record. It does not change canonical
portfolio gates or authorize outreach, target code, a PR, or acceptance. Public
GitHub reads used `scripts.bot_github`, which verified `humanifest-bot` on each
successful call. One Kobo metadata call stopped at the identity guard; a single
retry succeeded. No GitHub writes were attempted.

## Existing contribution: Kobo incremental sync

The [Humanifest inquiry on #7259](https://github.com/kobotoolbox/kpi/issues/7259#issuecomment-5593643546)
and [author's response](https://github.com/kobotoolbox/kpi/issues/7259#issuecomment-5600432460)
remain the last substantive discussion. The author welcomed a frozen-time
same-second test and an overlap-cursor note but [deferred documentation](https://github.com/kobotoolbox/kpi/issues/7259#issuecomment-5600507492)
pending Kobo team direction. Do not send another generic follow-up.

[PR #7260](https://github.com/kobotoolbox/kpi/pull/7260) was open and unmerged
on October 1 at head `9cb53877c76a0c0ed97c317c988bea7c8b6d35a8`.
The latest [human review](https://github.com/kobotoolbox/kpi/pull/7260#pullrequestreview-5201137810)
requested OpenAPI generation and API-level tests. The author reported adding
three API tests on September 15. The current diff in
`kpi/tests/api/v2/test_api_submissions.py` confirms tests for field presence,
`$gt`/`$lt` across different days, and legacy fallback; the filter test uses
`freeze_time('2030-01-01 12:00:00')` once. It does not test two updates that
format to the same second or a `$gte` overlap query.

**Bounded test proposal, not target code:** freeze two edits at
`12:00:00.100000` and `12:00:00.900000`; retain the first returned
`_date_modified` as a cursor; show that strict `$gt` does not return the later
edit, while `$gte` plus `_id` deduplication returns its latest content. Assert
the API response and filtering behavior rather than only the formatter output.
Keep the test inside the existing API test module and do not change timestamp
precision. The exact fixture/edit route and assertions need maintainer and
author coordination; no Kobo database or test suite was run here. The Kobo
team's desired feature shape, documentation placement, AI/bot participation,
and specific remote-write authority remain unresolved. The existing
[portfolio record](../portfolio/opportunities/kobo-7259-incremental-sync-verification.json)
must not advance on this note alone.

## New discovery: IFRC GO frontend

The [IFRC GO web app](https://github.com/IFRCGo/go-web-app) is an active,
MIT-licensed disaster-response information frontend. The public
[contribution guide](https://github.com/IFRCGo/go-web-app/blob/develop/CONTRIBUTING.md)
welcomes contributors, and its [PR template](https://github.com/IFRCGo/go-web-app/blob/develop/.github/pull_request_template.md)
asks for issue linkage, changes, CI, and sensitive-data checks. The public
`IFRCGo/.github` repository was not found; that result does not establish that
there is no organization-wide AI or bot policy. No complete policy clearance
or bot eligibility is claimed.

[Issue #2515](https://github.com/IFRCGo/go-web-app/issues/2515) is open and
unassigned. It asks to remove an obsolete DEEP link from the Information
Management page of the Surge Services Catalogue. A search of open PRs
mentioning `DEEP` returned zero; that search cannot exclude an unrelated-titled
PR. On `develop`, the affected card is in
[`app/src/views/SurgeCatalogueInformationManagement/index.tsx`](https://github.com/IFRCGo/go-web-app/blob/develop/app/src/views/SurgeCatalogueInformationManagement/index.tsx)
and its three labels are in the adjacent
[`i18n.json`](https://github.com/IFRCGo/go-web-app/blob/develop/app/src/views/SurgeCatalogueInformationManagement/i18n.json).
The issue's wording says remove the link; whether to remove only the link or
the entire DEEP card and unused strings needs maintainer confirmation. No
target code was cloned, changed, or executed.

This is a better first in-repository candidate than [wiki issue #2532](https://github.com/IFRCGo/go-web-app/issues/2532):
the wiki's edit path has not been established. #2515 still needs the full
repository/organization policy screen, a current link and UI check, translation
and test scope, maintainer interest, probable reviewer, and target-specific
outreach authorization before it can become a build-eligible opportunity.
The [September 30 discovery leads](2026-09-30-project-discovery-leads.md)
remain leads until the required Orca/source-of-truth route is available.
Humanifest already has an IFRC organization project record for
[`pystac-monty`](../portfolio/projects/ifrc-pystac-monty.json) and an unanswered
[bot inquiry on #199](https://github.com/IFRCGo/pystac-monty/issues/199#issuecomment-5594287228).
Its full public discussion was rechecked October 1. Avoid parallel generic
outreach to the same organization; #2515 needs its own narrowly authorized,
maintainer-specific path if advanced.
