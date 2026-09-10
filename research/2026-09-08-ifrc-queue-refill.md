# IFRC queue replenishment: USGS economic-unit rounding

This initial screening is followed by [runtime verification](2026-09-08-ifrc-runtime-verification.md)
and the completed [contribution review and archived-input check](2026-09-08-ifrc-contribution-review.md).
Those later results supersede this note's unverified setup/policy status. Current
acceptance and impact gates remain in the opportunity record.

Accessed 2026-09-08 local time. Added one independent research opportunity in
IFRC's `pystac-monty`, pinned to `7dd2d48cd599c3e0b894f1676b5de88c19028c46`.
The queue item concerns an arithmetic follow-on to a merged correction, not a
replacement for that contribution or the broader uncertainty-model work.

## Why this cause and this scope

IFRC's [World Disasters Report 2026, Annex 2](https://wdr26.org/en/reports/wdr26/annex2)
explicitly uses Montandon data for disaster-trend analysis. The
[library](https://github.com/IFRCGo/pystac-monty/blob/7dd2d48cd599c3e0b894f1676b5de88c19028c46/README.md)
transforms disaster-source data into Montandon STAC records. That establishes
an operational pathway for data quality; it does not establish the reach or
benefit of this particular proposed change.

The [USGS unit issue #199](https://github.com/IFRCGo/pystac-monty/issues/199)
is still open, but its linked [PR #204](https://github.com/IFRCGo/pystac-monty/pull/204)
merged on 2026-08-31. Current source already uses `people`, `usd`, and the
million-dollar conversion. Do not queue that original correction as undone.

The collaborator's [scope guidance](https://github.com/IFRCGo/pystac-monty/issues/199#issuecomment-5291242904)
separates the unit correction from the unsettled histogram/uncertainty model.
This historical guidance does not confirm a new Humanifest contribution.

## Source finding and reproduction

In the [current USGS source](https://github.com/IFRCGo/pystac-monty/blob/7dd2d48cd599c3e0b894f1676b5de88c19028c46/pystac_monty/sources/usgs.py#L685),
the economic caller multiplies `_calculate_value_from_bins(...)` by 1,000,000.
That helper first computes the probability-weighted midpoint sum and converts
it to `int`. Fractional millions are discarded before conversion to dollars.

The [hash-checked probe](fixtures/ifrc-usgs-rounding-reproduction.py) evaluates
the original helper and economic caller expression with synthetic finite bins.
It compares their result with an independent Decimal calculation that preserves
the same midpoint formula but scales before integer conversion. It is not a new
loss model or a claim that midpoint aggregation is scientifically appropriate.

Retrieve the pinned `usgs.py` above, then run:

```sh
python3 research/fixtures/ifrc-usgs-rounding-reproduction.py /absolute/path/usgs.py
```

| Synthetic case | Current result (USD) | Same formula, scale before rounding (USD) |
| --- | ---: | ---: |
| Bin 0–1 million, probability 1 | 0 | 500,000 |
| Bin 1–10 million, probability 1 | 5,000,000 | 5,500,000 |
| Exact-integer control | 1,000,000 | 1,000,000 |
| Empty-bin control | 0 | 0 |

All four assertions passed. No target imports, setup, full transformer tests,
production queries, or measured impact were involved. These are deterministic
arithmetic observations, not observed loss estimates for an actual earthquake.

The [USGS payload cited in #199](https://earthquake.usgs.gov/product/losspager/us6000t7zp/us/1783916550513/json/alerts.json)
was retrieved. Its economic bin boundaries include 0–1, 1–10, 10–100 and 100–1000,
consistent with the issue's million-dollar interpretation and USGS's published
[PAGER thresholds](https://earthquake.usgs.gov/data/pager/background.php).
The repository's [Venezuela fixture](https://github.com/IFRCGo/pystac-monty/blob/7dd2d48cd599c3e0b894f1676b5de88c19028c46/tests/data/usgs/venezuela_alerts.json)
instead uses boundaries such as 0–1,000,000. It is a repository fixture, not
verified original USGS data. The inspected
[alert regression test](https://github.com/IFRCGo/pystac-monty/blob/7dd2d48cd599c3e0b894f1676b5de88c19028c46/tests/extensions/test_usgs.py#L319)
checks item count, roles, country codes and identifiers without asserting the
economic magnitude. A useful next check should address both arithmetic and
source-faithful units in fixtures.

## Next work and limits

Inspect test setup, hooks, CI, submodules and schema-fetch behavior before running
the target suite. Then prepare a focused regression case through the economic
item output, preserving fatality rounding and existing empty/error behavior.
Confirm with maintainers that unit-conversion precision is separable from the
paused representation work before implementation. No new outreach was sent.

README welcomes issues and PRs; the manifest requires Python 3.11+ and declares
Apache-2.0. The license notice was read, but complete terms and contribution/AI
policy review remain open. README offers recorded HTTP cassettes; an offline
test environment has not been verified. No implementation gates were waived.

## Other candidates screened

- [HDX Python Utilities](https://github.com/OCHA-DAP/hdx-python-utilities): public
  issue-only search returned zero open issues. No invented task was added.
- [IFRC GO production crash #2542](https://github.com/IFRCGo/go-web-app/issues/2542):
  assigned to two existing maintainers; not taken over.
- [Monty #165](https://github.com/IFRCGo/pystac-monty/issues/165): item-link media-type
  consistency spans code, tests, upstream fixtures and submodule alignment.
  Recorded as a lower-priority lead; no demonstrated consumer failure inspected.
- [GO data-integrity task #2491](https://github.com/IFRCGo/go-web-app/issues/2491):
  no body or acceptance criteria returned. Do not treat its title as a spec.

The new project/opportunity records control readiness. Research can continue now;
the planned September 15 status check does not install a monitor or pause work.

## Subsequent runtime verification

The [runtime note](2026-09-08-ifrc-runtime-verification.md) now records a clean,
pinned temporary environment, three real-transformer reproduction cases and
all eight existing USGS tests passing with networking blocked. It supersedes
the earlier setup/reproduction unknowns for this focused path. Maintainer scope,
policy and human review gates remain unresolved; no target fix has been made.
