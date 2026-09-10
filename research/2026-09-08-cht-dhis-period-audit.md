# CHT #11342: reporting-period contract audit

Read-only inspection on 2026-09-08 of committed source at
`35b2bb6dac0844bee3228476591d08d56c5dd10d`. No setup, target tests, implementation,
or outreach was performed. The [issue](https://github.com/medic/cht-core/issues/11342)
remains open, unassigned, with no comments in the live check. Its report of a
local reproduction remains a contributor report, not a Humanifest test result.

## Three distinct decisions

1. **Which target document to read.** The
   [writer](https://github.com/medic/cht-core/blob/35b2bb6dac0844bee3228476591d08d56c5dd10d/shared-libs/rules-engine/src/provider-wireup.js#L285-L315)
   tags the interval end, including in Gregorian mode. The
   [webapp reader](https://github.com/medic/cht-core/blob/35b2bb6dac0844bee3228476591d08d56c5dd10d/webapp/src/ts/services/rules-engine.service.ts#L594-L625)
   agrees. The [exporter](https://github.com/medic/cht-core/blob/35b2bb6dac0844bee3228476591d08d56c5dd10d/api/src/services/export/dhis.js#L38-L98)
   derives its tag from the selected `from` timestamp, without the configured
   reporting start day. This establishes differing expressions, not a completed
   runtime reproduction or an agreed fix.
2. **What the selected period means.** The
   [admin controller](https://github.com/medic/cht-core/blob/35b2bb6dac0844bee3228476591d08d56c5dd10d/admin/src/js/controllers/export-dhis.js#L57-L75)
   creates month labels using `moment().subtract(monthCount, 'months')` and keeps
   the resulting timestamp. It does not normalize to a fixed reporting boundary.
   Inference: replacing only the API lookup with a containing-interval lookup can
   make one displayed month refer to different intervals depending on the day the
   admin page is opened. This must be tested; it is not observed UI behavior.
3. **How the exported period is labelled.** The exporter independently formats
   `period` as Gregorian `YYYYMM`. Matching the writer's target key alone does not
   establish that the payload label matches the intended reporting period. No
   claim about all DHIS2 calendar capabilities follows from this CHT code.

## Existing rules and useful controls

The [settings service](https://github.com/medic/cht-core/blob/35b2bb6dac0844bee3228476591d08d56c5dd10d/webapp/src/ts/services/uhc-settings.service.ts#L15-L26)
prefers `uhc.month_start_date` over the nested visit-count setting. A proposed
export fix needs to respect the existing precedence, not merely read one path.
The [shared interval implementation](https://github.com/medic/cht-core/blob/35b2bb6dac0844bee3228476591d08d56c5dd10d/shared-libs/calendar-interval/src/index.js)
already handles start-day normalization, month boundaries and calendar fallback.
Reimplementing that arithmetic in the exporter risks another mismatch.

Read [calendar fixtures](https://github.com/medic/cht-core/blob/35b2bb6dac0844bee3228476591d08d56c5dd10d/shared-libs/calendar-interval/test/index.js#L621-L665)
cover default start day and both sides of a non-default boundary. For example,
the July 5, 2026/start-day-15 fixture expects a June 29–July 30 interval. These
assertions were read, not run or independently calendar-verified. The existing
[DHIS export fixture](https://github.com/medic/cht-core/blob/35b2bb6dac0844bee3228476591d08d56c5dd10d/api/tests/mocha/services/export/dhis.spec.js#L513-L555)
uses start day 1 and cannot establish non-default behavior.

## Acceptance questions before implementation

Ask the maintainer to choose whether `from` identifies a containing reporting
interval, an interval-end month, or a fixed period selected by the UI; then agree
how the picker and exported label express that choice. Do not silently widen a
lookup fix into a picker/calendar redesign or claim a backend-only change closes
the full issue. No additional inquiry is sent by this audit.

Once scope is confirmed, use distinct nonzero totals in adjacent target documents
so the test distinguishes a wrong-month export from missing data. Cover both sides
of the reporting-day boundary, default-day controls, Gregorian compatibility,
settings precedence, and relevant year/month transitions. Vary the admin clock
while selecting the same displayed period, asserting the agreed meaning of
`from` and the output `period`. The
[admin test file](https://github.com/medic/cht-core/blob/35b2bb6dac0844bee3228476591d08d56c5dd10d/admin/tests/unit/controllers/export-dhis.spec.js)
is a separate test surface from the API test. These are proposed acceptance
checks, not tests added or passed.

The opportunity remains in `MAINTAINER-CHECK`. Its bounded-change gate is now
unconfirmed because the existing proposal does not settle these coupled product
decisions. The source-backed mismatch remains evidence worth discussing.

## Subsequent execution

The [September 9 reproduction](2026-09-09-cht-dhis-period-reproduction.md) now
executes the original export/controller logic with synthetic inputs and the existing
calendar tests. It supersedes the earlier no-execution status for those bounded
surfaces, while leaving the reporting contract and implementation scope unresolved.
