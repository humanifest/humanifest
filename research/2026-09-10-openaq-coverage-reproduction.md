# OpenAQ #404: original coverage calculation and response validation

Executed September 10, 2026. API revision
`87c060c28f5b484e0e9953d247082f5e678935c9`; database revision
`0e49c258186372f4af6c5679a4e1ab47157f0158`.

The original database calculation produces the five null fields identified in
[#404's diagnostic comment](https://github.com/openaq/openaq-api/issues/404#issuecomment-4783126755)
when both reporting periods are explicitly null. Those outputs fail validation
in the original API response model. Eight additional model/HTTP scenarios show
that a wholly absent coverage object is allowed, whereas an incomplete object
can make a whole mixed sensor response fail. This reproduces the contract-level
mechanism with synthetic inputs; no operational API was queried.

## Observed boundaries

The [response probe](fixtures/openaq_coverage_response_probe.py) imports the
unchanged `SensorsResponse`, its nested models and original date helper. It
checks model validation and serves each synthetic payload through a minimal
FastAPI route with that original response model. This route is a test boundary,
**not OpenAQ's original router, middleware or application startup**.

| Synthetic response | Model errors | In-process HTTP status |
| --- | ---: | ---: |
| Valid coverage | 0 | 200 |
| Coverage field omitted | 0 | 200 |
| Entire coverage object null | 0 | 200 |
| Valid zero observed measurements | 0 | 200 |
| Five coverage fields null | 5 | 500 |
| One valid sensor plus one with those null fields | 5, on second sensor | 500 |
| Empty coverage object | 6 missing fields | 500 |
| Valid camel-case coverage keys | 0 | 200 |

The mixed case did not return the valid sensor as a partial successful response.
All eight scenarios met their asserted expectations. Payloads and original
source files remained unchanged. Zero observations remain distinct from
missing reporting metadata; the tests do not replace missing data with zero.

The [SQL probe](fixtures/openaq_coverage_sql_probe.py) extracts the two complete
`calculate_coverage` definitions verbatim from the pinned database utility file.
It executes them in PostgreSQL **14.18**, using a newly initialized temporary
cluster in single-user mode. Seven returned coverage objects are then passed
through the original API response model; two additional cases capture SQL errors.

| Calculation input | Original result | Original response-model errors |
| --- | --- | ---: |
| Period arguments omitted | Defaults used; one expected observation, 100% coverage | 0 |
| Explicit 3,600-second periods | Same as omitted arguments | 0 |
| Both periods null | Five fields null; observed count retained | 5 |
| Averaging period null | Observed/expected intervals and percent coverage null | 3 |
| Logging period null | Expected count/interval and percent complete null | 3 |
| Zero observations with valid periods | Zero observed coverage | 0 |
| Timestamp overload over one hour | Same as explicit one-hour periods | 0 |
| Zero averaging period | Division-by-zero SQLSTATE `22012` | Not reached |
| Zero logging period | Division-by-zero SQLSTATE `22012` | Not reached |

Explicit nulls do not invoke the SQL parameter defaults. The both-null fields
match the issue diagnosis: `expected_count`, `expected_interval`,
`observed_interval`, `percent_complete` and `percent_coverage`. The zero-period
cases are local boundary checks, not evidence of another deployed incident or
justification to expand the patch's scope without agreement.

## Scope implications and disconfirming evidence

The original API sensor route calls the calculation when a latest value exists
and passes stored averaging/logging periods. This is consistent with the
reported mechanism. Neither the route's real SQL joins nor production database
constraints were exercised here.

The database README says table SQL should describe current desired structure,
but the inspected `openaqdb/tables/sensors.sql` does not define the two period
columns. Historical `import_sensors.sql` defines nullable period columns and
source-specific fallback values. These files do **not** prove today's deployed
schema or ingestion invariants. Confirm the current migration/ingestion source
before recommending a constraint. Do not silently treat historical import
fallbacks as desired present behavior.

The evidence supports a focused scope discussion: prevent incomplete metadata
at ingestion, handle unavailable coverage in API output, or an agreed combination.
A blanket nullable-field change or guessed interval would hide a contract
decision. Maintainer confirmation, AI/bot eligibility and benefit relative to
review cost remain unresolved. No production change or outreach was made.

## Environment and reproduction

The existing API manifest, pinned requirements and Poetry lock were inspected,
along with all three GitHub workflows, Dockerfile, settings loader and README.
The application has database/cache/cloud dependencies; deployments consume AWS
secrets and run CDK. The README's local Redis instructions expose ports and suggest
an OS setting change. None of those deployment, service or OS changes was used.
The model helper depends only on date parsing in addition to the model packages.

A new Python **3.13.7** virtual environment under
`/tmp/humanifest-openaq-screen/venv` contains 17 wheel packages selected from the
upstream lock. Installation used `--no-deps --only-binary=:all: --require-hashes`,
with hashes from that lock, no source builds, no bytecode compilation, no personal
pip configuration and an explicit environment without inherited credentials.
No project build/install/deployment command ran. Important versions:

- Pydantic 2.11.1 / pydantic-core 2.33.0;
- FastAPI 0.115.12 / Starlette 0.46.1 / HTTPX 0.28.1;
- pyhumps 3.8.0 / python-dateutil 2.9.0.post0;
- remaining locked dependencies: annotated-types, anyio, certifi, h11, httpcore,
  idna, six, sniffio, typing-extensions and typing-inspection.

Run both fixtures with the selected lockfile environment. `--source` points to
an external copy of the API files; `--database-source` points to the external
database source. The fixtures verify their original-source hashes before use.

```sh
python research/fixtures/openaq_coverage_response_probe.py \
  --source /path/to/external/api-source --require-network-denial
python research/fixtures/openaq_coverage_sql_probe.py \
  --source /path/to/external/api-source \
  --database-source /path/to/external/db-source \
  --postgres-bin /path/to/postgresql/bin --work-area /path/to/temporary/work
```

Both observed runs used macOS `sandbox-exec` with
`(version 1) (allow default) (deny network*)`. The response probe independently
verified denial with a socket-bind control. Its TestClient stayed in-process.
The SQL probe used `postgres --single -j` and created its own fresh cluster;
TCP and Unix socket settings were empty and host/local authentication was set
to reject connections. No listening service or existing database was used.
The single-user process exited normally. PostgreSQL's [single-user documentation](https://www.postgresql.org/docs/14/app-postgres.html)
explains this execution mode; it does not reproduce normal concurrent-server
behavior. No database platform or cloud account was configured.

All 15 fetched API source/setup files and five database source files match their
pinned Git blob hashes after testing. The two fixture model files are also checked
before and after their runs. The [checked-in result receipt](fixtures/openaq-coverage-results.json) preserves
the scenario outputs, runtime versions and source revisions without local paths.
Temporary receipts include `probe-install.log`,
`response-probe-results.json`, `sql-probe-results.json`, and the SQL probe's
`initdb.log`, exact `probe.sql` and `postgres.log` under its reported work area.

Not run: upstream full test suite, original route/application integration,
PostGIS schema setup, ingestion or migration tests, concurrent server behavior,
production API calls or deployed-benefit measurement. The next independent task
is original-router verification with a synthetic database boundary and locating
the current period-column/migration contract.

## Sources

All accessed September 10, 2026:

- [API model source](https://github.com/openaq/openaq-api/blob/87c060c28f5b484e0e9953d247082f5e678935c9/openaq_api/v3/models/responses.py)
- [Original sensor route](https://github.com/openaq/openaq-api/blob/87c060c28f5b484e0e9953d247082f5e678935c9/openaq_api/v3/routers/sensors.py)
- [API lockfile](https://github.com/openaq/openaq-api/blob/87c060c28f5b484e0e9953d247082f5e678935c9/poetry.lock)
- [Database coverage functions](https://github.com/openaq/openaq-db/blob/0e49c258186372f4af6c5679a4e1ab47157f0158/openaqdb/idempotent/util_functions.sql)
- [Database table source](https://github.com/openaq/openaq-db/blob/0e49c258186372f4af6c5679a4e1ab47157f0158/openaqdb/tables/sensors.sql)
- [Historical import source](https://github.com/openaq/openaq-db/blob/0e49c258186372f4af6c5679a4e1ab47157f0158/openaqdb/import_sensors.sql)
- [Database README](https://github.com/openaq/openaq-db/blob/0e49c258186372f4af6c5679a4e1ab47157f0158/README.md)
