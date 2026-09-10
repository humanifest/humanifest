# Air-quality data discovery: OpenAQ

Follow-up: the [coverage reproduction audit](2026-09-10-openaq-coverage-reproduction.md) records subsequent original-model and SQL execution. Statements below about tests or installation not yet run describe this initial screen.

Accessed September 10, 2026. This screen moves from a high-burden cause to a
specific data-access hypothesis. It does not estimate lives saved by software.

## Cause and operational pathway

WHO's June 21, 2026 [technical brief](https://www.who.int/publications/i/item/B09563)
reports about **6.6 million annual deaths** attributable to air pollution, with
close to 84% from noncommunicable diseases. This is a modeled global burden
estimate, not OpenAQ's impact. Older WHO material uses 6.7 million; do not combine
those figures or interpret their difference as an intervention effect.

OpenAQ describes its [platform](https://openaq.org/about/initiatives/openaq-data-platform/)
as a way to collect, standardize and share air-quality measurements, including
coverage in lower-income countries. Its [community case study](https://openaq.org/about/use-cases/data-for-communities/)
reports that Clean Air One Atmosphere uses the platform to preserve and share
measurements in Ghana and Malawi. That provides a named operational pathway;
it remains project-reported evidence, without independent attribution of a
health outcome to this software or to a proposed contribution.

**Falsifiable hypothesis:** a location's partially missing sensor reporting
metadata can make its entire sensor-list response fail, obstructing access to
otherwise available measurements. An isolated response-model/route reproduction
should distinguish this failure from valid coverage and entirely absent coverage.
A future fix would need agreement on whether to enforce ingestion/database
requirements, change API response handling, or both. Do not substitute guessed
coverage values or broaden field nullability without an agreed contract.

## Bounded inventory and exclusions

GitHub REST open-issue inventories were read in full (each fit one 100-item page),
including PRs. No target repository was cloned and no operational API queried.

| Repository | Current inventory | Decision |
| --- | --- | --- |
| `openaq-python` | 2 issues, 1 PR; main `430d724e28355b73f5bb0e7149371cfdaf16de9b`; September 3 push; v1.1.0 July 2 | Defer. #105/#106 concern a future Python 3.11 baseline; the current manifest still supports 3.10. No reported user data-access defect is available in this queue. |
| `openaq-explorer` | 6 issues, 2 PRs; September 3 push | Preserve existing work: #60 has PR #72; #61/#76/#46 are assigned. #115 has a maintainer explanation about unavailable CO2 data and intentionally limited map filters, so it is not established as a missing-data bug. #79 remains an unverified navigation report. |
| `openaq-api` | 10 issues, 6 PRs; main `87c060c28f5b484e0e9953d247082f5e678935c9`; May 22 push | Research #404. It is unassigned and its inspected timeline has no linked PR. Several other reports already have PRs: #395/#398, #388/#406, #390/#394 and ARM64 #264/#400. Error-response work also has PR #396. |

These counts are snapshots, not a guarantee that no duplicate or competing work
exists. The GitHub web view showed fewer API PRs than the live REST inventory;
the recorded count uses the REST response. The SDK's privileged issue template
is not a general ban on external contribution: its actual contributing guide
welcomes contributions and requires PRs to link an existing issue.

## Selected API #404: source observation

The [issue](https://github.com/openaq/openaq-api/issues/404), opened June 19, 2026,
reports HTTP 500 for a location's sensor list. A [diagnostic comment](https://github.com/openaq/openaq-api/issues/404#issuecomment-4783126755)
attributes it to missing logging/averaging values and lists five null-field
validation errors. The commenter proposes requiring those values in the database;
that proposal is not maintainer acceptance of Humanifest work or an agreed fix.

At the pinned revision:

- `openaq_api/v3/models/responses.py` defines non-null `Coverage` fields
  `expected_count`, `expected_interval`, `observed_count`, `observed_interval`,
  `percent_complete` and `percent_coverage`. `Sensor.coverage` itself is nullable.
- `openaq_api/v3/routers/sensors.py` declares `SensorsResponse` on
  `/v3/locations/{locations_id}/sensors`. `fetch_sensors` constructs coverage
  using `calculate_coverage` with the sensor's logging/averaging periods when a
  latest value exists. This is consistent with the report, but the database
  function and a runtime failure have not yet been reproduced.
- Existing `tests/test_sensors.py` uses the full application and database pool.
  Its mixed v2/v3 smoke list does not directly cover the reported location-sensor
  endpoint with incomplete coverage. `tests/README.md` switches environment
  files; do not use a real environment or existing credentials for reproduction.
- `pyproject.toml` targets Python >=3.11, Pydantic >=2.11,<3 and FastAPI
  >=0.115.11,<0.116, with database/cache/cloud dependencies. The inspected test
  workflow uses a requirements path and working-directory layout that need
  reconciliation with the current tree. No installation or target tests ran.

Eight source/setup files were saved outside Humanifest and verified against
Git blob IDs in the pinned tree. Receipts and source browsing copies are in
`/tmp/humanifest-openaq-screen/`. Production source remains untouched.

## Contribution and next action

The API's pinned [contributing guide](https://github.com/openaq/openaq-api/blob/87c060c28f5b484e0e9953d247082f5e678935c9/CONTRIBUTING.md)
welcomes fork-based contributions and favors focused patches. GitHub identifies
MIT licensing for the API and Apache-2.0 for the SDK/Explorer. No applicable
AI/bot acceptance or complete contribution/dependency audit is established.
The public web issue-creation control appeared restricted; do not infer a
posting entitlement or attempt to work around it. No outreach was sent.

Queue one research opportunity for #404: inspect the remaining test/setup and
coverage-function sources, then reproduce the original response contract with
synthetic missing/null/valid metadata and a database boundary. Determine whether
a database-backed test is necessary before proposing a regression strategy.
Keep database constraints and API handling as unresolved scope alternatives.
No deployment access, private sensor records, credentials or live error probes
are needed for this next step.

## Source inventory

All accessed September 10, 2026:

- [SDK repository](https://api.github.com/repos/openaq/openaq-python), [open items](https://api.github.com/repos/openaq/openaq-python/issues?state=open&per_page=100), [pinned manifest](https://github.com/openaq/openaq-python/blob/430d724e28355b73f5bb0e7149371cfdaf16de9b/pyproject.toml)
- [Explorer repository](https://api.github.com/repos/openaq/openaq-explorer), [open items](https://api.github.com/repos/openaq/openaq-explorer/issues?state=open&per_page=100), [#115 explanation](https://github.com/openaq/openaq-explorer/issues/115#issuecomment-3651793146)
- [API repository](https://api.github.com/repos/openaq/openaq-api), [open items](https://api.github.com/repos/openaq/openaq-api/issues?state=open&per_page=100), [#404 timeline](https://api.github.com/repos/openaq/openaq-api/issues/404/timeline)
- [Pinned response models](https://github.com/openaq/openaq-api/blob/87c060c28f5b484e0e9953d247082f5e678935c9/openaq_api/v3/models/responses.py), [sensor routes](https://github.com/openaq/openaq-api/blob/87c060c28f5b484e0e9953d247082f5e678935c9/openaq_api/v3/routers/sensors.py), [sensor tests](https://github.com/openaq/openaq-api/blob/87c060c28f5b484e0e9953d247082f5e678935c9/tests/test_sensors.py)
- [Pinned API manifest](https://github.com/openaq/openaq-api/blob/87c060c28f5b484e0e9953d247082f5e678935c9/pyproject.toml), [test workflow](https://github.com/openaq/openaq-api/blob/87c060c28f5b484e0e9953d247082f5e678935c9/.github/workflows/test.yml)
