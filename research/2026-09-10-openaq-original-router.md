# OpenAQ #404: original sensor routes and period-column definitions

Executed September 10, 2026. API revision
`87c060c28f5b484e0e9953d247082f5e678935c9`; database revision
`0e49c258186372f4af6c5679a4e1ab47157f0158`.

The original location-sensor and single-sensor routes both fail response
validation when supplied the incomplete coverage objects produced by the
[previous SQL probe](2026-09-10-openaq-coverage-reproduction.md).
The current checked-in database initialization includes a separate metadata
script that adds both reporting-period columns as nullable integers. Their
location is now established; deployed constraints and ingestion behavior are not.

## Original-route observations

The [reusable probe](fixtures/openaq_sensor_router_probe.py) imports the unchanged
sensor router, query models/builder and response models. It extracts and executes
`DB.fetchPage` without changing its AST, body, defaults or annotations. A fixture
replaces `DB.fetch` with synthetic rows and captures the query and parameters.
This preserves original pagination/result wrapping without importing connection
settings, authentication or cache dependencies. The enclosing FastAPI application
is minimal; OpenAQ's full application startup and middleware do not run.

| Synthetic rows | Location route | Single-sensor route |
| --- | --- | --- |
| Valid coverage | 200 | 200 |
| Zero observations, valid periods | 200; zero preserved | 200; zero preserved |
| Coverage omitted | 200 | 200 |
| Coverage wholly null | 200 | 200 |
| Both periods null | 500; five invalid fields | 500; five invalid fields |
| Averaging period null | 500; three invalid fields | 500; three invalid fields |
| Logging period null | 500; three invalid fields | 500; three invalid fields |
| One valid and one incomplete sensor | 500; errors on second sensor | 500; errors on second sensor |
| Empty coverage object | 500; six missing fields | 500; six missing fields |
| No rows | 200; empty results | 404; Sensor not found |

Four additional path controls (zero and non-integer IDs on each route) returned
422 without calling the database boundary. All **24 scenarios** met assertions.
The mixed case on the single-sensor route is a response-contract stress control;
it does not claim a real ID-filtered SQL query can return two distinct sensors.

Each error case first required an actual `ResponseValidationError` with the
expected field names and result index, then separately checked HTTP 500 with
exception propagation disabled. An unrelated fixture exception cannot satisfy
that check. Each successful database call checked the original generated SQL's
location/sensor predicate, public-visibility predicates, coverage function and
integer ID parameter. The captured SQL was **not executed**; filtering and join
correctness are not established by checking its text. Empty-result and metadata
counts exercise the original response wrapping. Synthetic rows remained unchanged.

The [result receipt](fixtures/openaq-router-results.json) records individual
outcomes. The run used the prior lockfile-selected Python 3.13.7 environment,
macOS OS network denial and an independent denied socket-bind control. No new
packages, service, cloud setup or operational data request was needed. All
**22 fetched API files and 21 fetched database files** matched their pinned Git
blob hashes after execution.

```sh
# Use the audited lockfile environment and a network-denial sandbox.
python research/fixtures/openaq_sensor_router_probe.py \
  --source /path/to/external/api-source \
  --coverage-results research/fixtures/openaq-coverage-results.json \
  --require-network-denial
```

## Database contract located

The prior audit inspected `tables/sensors.sql` and historical import SQL but had
not yet found the current column-addition script. `init.sql` includes
`tables/metadata.sql`. That file adds `data_averaging_period_seconds int` and
`data_logging_period_seconds int` with no `NOT NULL`, default or check clause in
those definitions. Its comments define averaging as the duration represented by
each measurement, and logging as the expected measurement frequency.

`metadata_transfer.sql` updates averaging/logging fields only where corresponding
metadata exists, including a source-specific hourly averaging conversion. This is
a transfer script, not proof of the current ingestion path or an invariant that
all sensors obtain periods. The inspected schema-comparison documentation derives
migration statements by comparing databases; it is not a record of migrations
actually applied to production. Neither that comparison nor the database's
migration tests were executed. Those tests expect populated datasets and do not
provide a synthetic incomplete-period regression.

These findings remove the need to guess where the columns are defined. They do
not justify changing missing periods to zero or guessed hourly values. Maintainers
still need to choose whether unavailable coverage should be represented in API
output, prevented upstream, or handled through an agreed combination.

## Remaining work

Check the current ingestion ownership and complete contributor/AI-policy review,
then prepare a short scope inquiry grounded in the reproduction and nullable
column definitions. Original routing is now tested at the synthetic database
boundary; repeating pure-model tests is not the next step. Full SQL joins,
PostGIS/application integration, deployed prevalence, affected-user benefit and
maintainer acceptance remain unverified. No production patch or outreach was made.

## Sources

All accessed September 10, 2026:

- [Original sensor router](https://github.com/openaq/openaq-api/blob/87c060c28f5b484e0e9953d247082f5e678935c9/openaq_api/v3/routers/sensors.py)
- [Original query models and builder](https://github.com/openaq/openaq-api/blob/87c060c28f5b484e0e9953d247082f5e678935c9/openaq_api/v3/models/queries.py)
- [Original DB result wrapping](https://github.com/openaq/openaq-api/blob/87c060c28f5b484e0e9953d247082f5e678935c9/openaq_api/db.py)
- [Database initialization](https://github.com/openaq/openaq-db/blob/0e49c258186372f4af6c5679a4e1ab47157f0158/openaqdb/init.sql)
- [Period-column definitions and comments](https://github.com/openaq/openaq-db/blob/0e49c258186372f4af6c5679a4e1ab47157f0158/openaqdb/tables/metadata.sql)
- [Metadata transfer](https://github.com/openaq/openaq-db/blob/0e49c258186372f4af6c5679a4e1ab47157f0158/openaqdb/metadata_transfer.sql)
- [Schema comparison documentation](https://github.com/openaq/openaq-db/blob/0e49c258186372f4af6c5679a4e1ab47157f0158/migra/README.md)
- [Existing migration tests](https://github.com/openaq/openaq-db/blob/0e49c258186372f4af6c5679a4e1ab47157f0158/tests/test_database_migration.py)
