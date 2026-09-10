# CHT #11342: executed reporting-period boundaries

Verified September 9, 2026 against CHT commit
`35b2bb6dac0844bee3228476591d08d56c5dd10d` in the previously inspected clean
baseline. The exporter, calendar helper, writer helper, admin controller, relevant
tests and root lockfile were compared byte-for-byte with that commit's Git objects.
No target source was modified, no database or deployment was started, and no
reporting semantics were chosen on the maintainer's behalf.

## What ran

The existing calendar-interval suite passes: **37 tests**, 41 ms reported test
time and approximately 0.25 seconds process wall time. It ran directly through
Mocha with automatic config/package loading disabled, using Node 22.16.0,
`TZ=UTC` and a minimal child environment. The suite emits an existing Moment
warning for its `2018-01-31 23:59:59:999` fixture; it does not fail the suite.
Dependencies come from the already inspected baseline installation: Moment 2.30.1,
Bikram Sambat 1.8.1, Lodash 4.18.1, Mocha 11.7.5, Chai 4.5.0 and Sinon 21.0.1.
No new dependencies were installed.

The [hash-checked reproduction](fixtures/cht-dhis-period-reproduction.cjs) runs
these original code surfaces with explicitly restricted dependency wiring:

- The complete calendar helper computes the containing interval.
- The extracted original `getTargetDocTag` function computes the writer's tag.
- The complete export service queries synthetic target documents, sums their
  values and constructs its output period. Adjacent months contain distinct
  totals, **11** and **29**, so a wrong-month read is distinguishable from no data.
- The original admin controller builds its period list using a controlled Moment
  clock, synthetic Settings/DB responses and an Angular registration stub.

The VM contexts are dependency-wiring harnesses, not security sandboxes. No real
CouchDB, API configuration loader, logger, Angular injector, DOM or browser is
involved. Only the extracted writer helper runs; target aggregation and persistence
are not exercised. This is stronger than comparing copied arithmetic, but is not
an end-to-end export reproduction or a live deployment finding.

## Eight export cases

| Calendar | Selected date | Start day | Containing interval | Writer tag | Exporter tag | Exported / containing-interval total |
| --- | --- | ---: | --- | --- | --- | ---: |
| Gregorian | 2026-07-14 | 15 | 2026-06-15–2026-07-14 | 2026-07 | 2026-07 | 11 / 11 |
| Gregorian | 2026-07-15 | 15 | 2026-07-15–2026-08-14 | 2026-08 | 2026-07 | 11 / 29 |
| Gregorian | 2026-07-15 | 1 | 2026-07-01–2026-07-31 | 2026-07 | 2026-07 | 11 / 11 |
| Gregorian | 2026-12-31 | 15 | 2026-12-15–2027-01-14 | 2027-01 | 2026-12 | 11 / 29 |
| BS | 2026-07-05 | 15 | 2026-06-29–2026-07-30 | 2083-04 | 2083-03 | 11 / 29 |
| BS | 2026-07-30 | 15 | 2026-06-29–2026-07-30 | 2083-04 | 2083-04 | 11 / 11 |
| BS | 2026-07-31 | 15 | 2026-07-31–2026-08-30 | 2083-05 | 2083-04 | 11 / 29 |
| BS | 2026-07-31 | 1 | 2026-07-17–2026-08-16 | 2083-04 | 2083-04 | 11 / 11 |

All eight cases pass their assertions of **current behavior**. Four distinguish
adjacent nonzero totals; default-day and before-boundary controls agree. The
exported `period` remains the selected date's Gregorian `YYYYMM` in every case,
including BS mode. These tests do not approve a replacement date or label contract.
The BS dates use the target's own calendar dependency, not an independently
validated external calendar conversion.

## Picker counterexample and existing coverage

Opening the controller on August 14 versus August 15 produces the same second
label, **July, 2026**, but retains July 14 versus July 15 in its timestamps. With
Gregorian start day 15, those timestamps belong to intervals tagged July versus
August. Both controller assertions pass. A backend containing-interval lookup
would therefore need an agreed picker interpretation before being treated as a
complete fix. This is controller-level behavior, not a rendered UI observation.

The existing admin test fixes January 15, 2000 and checks the six labels, but does
not vary the clock across a reporting boundary. The existing API tests cover BS
mode and an explicit start-day-1 case. Those API tests were inspected but were not
run here; the reproduction does not substitute for their in-memory database suite.
The 431-test admin baseline run recorded earlier included the existing admin test;
no additional real Angular DHIS-specific test was run in this investigation.

The first reproduction attempt completed its export cases but failed in the
harness's fake clock: calling Moment inside `moment.now` recursively invoked the
same hook. Computing the fixed timestamp before installing the hook corrected the
harness. The subsequent complete run passes; no target fix was needed.

## Prepared scope question

Humanifest can offer a bounded, AI-assisted contribution if maintainers want it:
should `from` identify the containing reporting interval, the interval-end month,
or the period displayed by the admin picker? With start day 15, the original
exporter selects July for July 15 while the writer helper tags the containing
interval August. Distinct synthetic totals demonstrate the difference. The picker
also retains July 14 versus July 15 under the same July label on successive visit
dates. Should a fix normalize that selection as well, and what should the exported
`period` represent in BS mode? The smallest coherent implementation depends on
those choices; a backend-only lookup change is not assumed to close #11342.

The September 9 GitHub read found the issue still open, unassigned and without
comments. Its author describes the BS work as an unreleased epic; this check did
not independently establish current release/deployment status.

This text is prepared evidence for coordination, not an inquiry delivery claim or
maintainer confirmation. Recheck the live issue and linked work before sending.
The candidate remains in MAINTAINER-CHECK with scope and reviewer gates unresolved.
No humanitarian outcomes, production data loss, or downstream reporting harm were
measured. Settings precedence and broader calendar/time-zone cases remain future
acceptance work once the intended semantics are confirmed.

## Reproduce

With the previously inspected CHT checkout and locked dependencies available:

```sh
TZ=UTC /path/to/node22 research/fixtures/cht-dhis-period-reproduction.cjs /absolute/path/to/cht-baseline
```

Source locators and policy context remain in the
[original source audit](2026-09-08-cht-dhis-period-audit.md). The fixture embeds the
source/lockfile hashes and refuses other revisions.

## Subsequent coordination check

The [fresh scope check](2026-09-09-cht-dhis-scope-inquiry.md) verified that the
related epic is now complete and the two reproduced export/picker files remain
unchanged on current master. It records the separate locale PR and the exact
prepared inquiry. Automatic approval review rejected posting that inquiry; it
was not delivered and maintainer confirmation remains unresolved.
