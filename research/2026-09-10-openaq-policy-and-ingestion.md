# OpenAQ #404: contribution eligibility and ingestion ownership

Read-only audit, September 10, 2026. No ingestion code, cloud handler, database
migration or operational data request was run.

## Contribution policy

The organization-wide [contribution guide](https://github.com/openaq/.github/blob/683b47c9bb265c3855b06d004352bc0fdaf64fc4/CONTRIBUTING.md)
requires both organization and repository rules, including its
[LLM policy](https://github.com/openaq/.github/blob/683b47c9bb265c3855b06d004352bc0fdaf64fc4/LLM_POLICY.md).
That policy requires disclosure of LLM use and contributor understanding of
submitted code. Wholly LLM-written contributions are unlikely to be accepted,
with possible case-by-case review. This is neither blanket permission nor an
absolute exclusion. Humanifest has no accepted scope or independent human code
review, so acceptance probability remains unestablished. Do not present automated
verification as human review or assume a disclosure alone makes a patch welcome.

The [organization code of conduct](https://github.com/openaq/.github/blob/683b47c9bb265c3855b06d004352bc0fdaf64fc4/CODE_OF_CONDUCT.md)
applies across its contribution spaces. The API's pinned contribution guide
welcomes fork-based PRs, focused changes and explanatory commit messages. The
[API license](https://github.com/openaq/openaq-api/blob/87c060c28f5b484e0e9953d247082f5e678935c9/LICENSE.md)
is MIT, including notice preservation. This confirms the API's declared license;
it does not complete a dependency audit or establish licensing for every related
repository. No agreement was signed.

The organization policy should have been checked during the initial screen,
before target installation and repeated reproduction. The generic API guide and
community-profile endpoint did not establish the absence of an LLM rule. The
contribution protocol now explicitly requires direct organization-policy discovery
before substantial target testing. Existing reproduction remains valid technical
evidence, but is not evidence of likely contribution acceptance.

## Ingestion paths

The API README identifies `openaq-ingestor` as the loader between fetched data
and `openaq-db`. The public ingestor is unarchived and was pushed September 8,
2026. This audit pins its main tree to
`106d71ae215a3fa3ed9e405f75f217b05f7a1b5b`.

The [ingestor README](https://github.com/openaq/openaq-ingestor/blob/106d71ae215a3fa3ed9e405f75f217b05f7a1b5b/README.md)
describes two paths whose period handling differs:

- In [lcsV2.py](https://github.com/openaq/openaq-ingestor/blob/106d71ae215a3fa3ed9e405f75f217b05f7a1b5b/ingest/lcsV2.py), the sensor parser sets both logging and averaging intervals when it encounters `interval_seconds`. The staging writer includes both interval fields. Its node-loading path executes `etl_process_nodes.sql`.
- That [node ETL SQL](https://github.com/openaq/openaq-ingestor/blob/106d71ae215a3fa3ed9e405f75f217b05f7a1b5b/ingest/etl_process_nodes.sql) inserts the intervals into both sensor columns and replaces both columns from incoming values on conflict. The shown insertion predicates require measurand and sensor-system IDs, not non-null periods. This is static source evidence, not a reproduction of missing-field CSV encoding or an actual null overwrite.
- The realtime [fetch ingestion SQL](https://github.com/openaq/openaq-ingestor/blob/106d71ae215a3fa3ed9e405f75f217b05f7a1b5b/ingest/fetch_ingest_full.sql) constructs averaging metadata but its new-sensor insert lists system ID, measurand ID and metadata, omitting both dedicated period columns. The [fetch runner](https://github.com/openaq/openaq-ingestor/blob/106d71ae215a3fa3ed9e405f75f217b05f7a1b5b/ingest/fetch.py) loads this SQL. Deployed triggers or later processing were not inspected or executed.

The checked-in [database initialization path](2026-09-10-openaq-original-router.md)
adds the dedicated columns as nullable integers without defaults in their
definitions. A proposal to require them therefore needs an ingestion/backfill
plan, including the realtime insert that omits them. Merely making the API fields
nullable would also decide public response semantics without agreement.

Nine fetched ingestor files and four organization-policy files were verified
against their pinned Git blob hashes. The API license was likewise verified.
No third-party setup command ran in this audit. Ingestor deployment configuration,
complete data contracts, staging behavior, triggers and live database invariants
remain outside its coverage.

## Current issue and disposition

The refreshed [issue](https://github.com/openaq/openaq-api/issues/404) is open,
unassigned and unlocked. Its sole diagnostic comment still proposes required
period columns and asks another maintainer for input. The inspected timeline has
no linked PR. There is no Humanifest contribution acceptance.

A [short inquiry](2026-09-10-openaq-scope-inquiry.md) is prepared for human review.
It discloses automated authorship, asks whether this contribution mode is welcome,
and requests the API-versus-ingestion scope decision. The opportunity moves to
`MAINTAINER-CHECK`, retaining failed implementation gates. It has no invented
reply date because nothing was posted. Independent discovery should continue;
further tests here should be driven by new evidence or an agreed scope.

All source links and public GitHub issue/organization inventories were accessed
September 10, 2026. The organization inventory returned 53 public repositories
on a page with a 100-item limit.
