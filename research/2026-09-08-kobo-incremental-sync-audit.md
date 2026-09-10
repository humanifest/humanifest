# Kobo incremental-sync PR: timestamp precision and verification gaps

Accessed 2026-09-08. The existing [PR #7260](https://github.com/kobotoolbox/kpi/pull/7260)
is owned by another contributor. This audit supports that work; no replacement
patch or formal PR review was prepared. The head inspected is
`7968471a4d86ab701f61537499ee080144b2bf3e` in `RuneO/kpi`.
All seven changed files and the full 100-line new test file were read at that
revision. The PR was open when pinned; its last update was 2026-07-28.

## Actionable boundary case

The PR serializes `Instance.date_modified` with the existing
[`MONGO_STRFTIME`](https://github.com/RuneO/kpi/blob/7968471a4d86ab701f61537499ee080144b2bf3e/kobo/apps/openrosa/libs/utils/common_tags.py#L42),
which has second precision. The
[new formatter expression](https://github.com/RuneO/kpi/blob/7968471a4d86ab701f61537499ee080144b2bf3e/kobo/apps/openrosa/apps/viewer/models/parsed_instance.py#L313)
therefore maps both `12:00:00.100000` and `12:00:00.900000` to `12:00:00`.
The [new tests](https://github.com/RuneO/kpi/blob/7968471a4d86ab701f61537499ee080144b2bf3e/kobo/apps/openrosa/apps/viewer/tests/test_date_modified.py)
assert that the database datetime advances and that Mongo matches its formatted
value; they do not assert that the formatted value advances or test an API query.

The [query path](https://github.com/RuneO/kpi/blob/7968471a4d86ab701f61537499ee080144b2bf3e/kpi/deployment_backends/openrosa_backend.py#L1521)
passes filters to Mongo before injecting response properties. Mongo's
[`$gt` operator](https://www.mongodb.com/docs/manual/reference/operator/query/gt/)
excludes equal values. Consequently, a consumer that records the first returned
timestamp and then uses strict `$gt` can miss a second edit within that same
second. This is a contract risk inferred from verified formatting and the query
semantics, not an observed production incident or completed database test.

The PR's query example uses `$gt`; it does not specify a complete sync protocol.
Do not claim every consumer loses updates. A fixed historical cutoff still finds
later timestamps; the risk concerns advancing a cursor to a returned timestamp.
More fractional digits alone also cannot guarantee lossless sync across delayed
Mongo writes or equal timestamps. The desired cursor/overlap contract needs an
explicit decision rather than changing the shared timestamp format blindly.

## Reproducible evidence

[The standalone probe](fixtures/kobo-date-modified-reproduction.py) checks source
hashes, reads the format constant, evaluates the original formatter expression,
and exercises the original read-time fallback method. It does not import Kobo,
install dependencies, or connect to a database. Retrieve these files from the
pinned head above, replacing path separators with `__` in local filenames:

- `kobo/apps/openrosa/libs/utils/common_tags.py`
- `kobo/apps/openrosa/apps/viewer/models/parsed_instance.py`
- `kpi/deployment_backends/base_backend.py`

Run:

```sh
python3 research/fixtures/kobo-date-modified-reproduction.py /absolute/path/source-directory
```

Observed on 2026-09-08: two supplied timestamps 800 milliseconds apart collide;
a timestamp one second later advances; an existing modified value is preserved;
a legacy response receives its creation time; a response lacking both fields
still lacks a modified time. All probe assertions passed. These are isolated
expression/method checks, not Django, PostgreSQL, MongoDB or HTTP integration tests.

## Coverage matrix

| Path | Evidence in the new tests | Remaining verification |
| --- | --- | --- |
| Serialization | Both date fields compared with formatted model values | Same-second collision and API filtering |
| Edit | Calls `instance.save()` then synchronous Mongo update | Actual XML edit/API route and delayed visibility |
| Single validation | Calls existing status helper, compares timestamps | Frozen-time boundary and creation-time invariance |
| Bulk validation | Exercises batch helper, checks shared values | Multi-record query boundaries and failure consistency |
| Attachments | Calls bulk refresh on an instance | Actual attachment-only edit/deletion; unchanged submission data |
| Legacy documents | Fallback added to response code; no new test there | Unfiltered fallback versus filtered retrieval before backfill |
| Exports | Metadata ignored; existing expected-document test adjusted | Explicit export/cache behavior across update paths |

Legacy fallback is an acknowledged PR limitation, not a newly discovered bug:
response injection occurs after Mongo filtering and cannot make absent stored
fields match the query. The author also identifies the missing `DataResponse`
schema entry and inability to regenerate API artifacts locally. Do not duplicate
these as novel review findings.

The returned commit check list contained only a successful Greptile review; the
retrieved issue comments likewise contained that bot's summary. Its confidence
score is not test execution evidence. Other check mechanisms were not exhaustively
audited, so full CI readiness remains unverified.

## Smallest useful next contribution

Coordinate with the existing author on one focused addition: a frozen-time API
regression case that updates a record twice within one second and queries from
the first returned timestamp, paired with documented cursor/overlap semantics.
Test the chosen contract against multiple equal-time records and delayed Mongo
visibility before promising lossless incremental sync. Preserve creation-time
and export behavior; keep backfill and schema generation separate unless requested.

No target code was changed and no full target test suite was run. No human
review or measured compute savings are claimed. The author's workload report supports relevance
but does not establish actual savings. Full environment inspection, policy and
maintainer confirmation remain required before implementation. Continue other
independent work while this bounded support proposal awaits coordination.

## Coordination delivered

Under the user's standing direction to handle GitHub communication through the
Humanifest identity, a [bounded scope question](https://github.com/kobotoolbox/kpi/issues/7259#issuecomment-5593643546)
was posted by `humanifest-bot` at 2026-09-09T00:02:57Z (September 8 local
time). It links this reproduction, states the limited execution scope and AI
involvement, and asks whether a test/documentation addition is welcome within
the existing PR. The issue remained open and the PR head unchanged immediately
before posting; no duplicate bot message was present. GitHub confirmed the
returned author and exact body. This is coordination, not a formal PR review,
permission to modify the other author's work, or maintainer approval.

The opportunity is now `MAINTAINER-CHECK`. Its planned external-status check
remains September 15 absent a reply or actionable event. Continue bounded queue
replenishment across other organizations in the meantime.
