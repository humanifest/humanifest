# Queue screening: September 9, 2026

Read-only screening avoids redoing already-owned work or spending setup compute
where the required contribution pathway cannot be used. No screened repository
was cloned and no target code or setup script was executed.

| Candidate | Evidence and decision |
| --- | --- |
| [OCHA HDX Python API](https://github.com/OCHA-DAP/hdx-python-api/issues) | Current API returned zero open issues/PRs. No concrete unmet need identified; do not invent an issue to fill capacity. |
| [HXL core-schema validation #364](https://github.com/HXLStandard/libhxl-python/issues/364) | Open report has no comments and last update January 2024. Current priority/maintainer demand is unverified; not promoted. The numeric-attribute issue #355 is already assigned. |
| [OCHA country annotation #90](https://github.com/OCHA-DAP/hdx-python-country/issues/90) | Recent report concerns a type annotation. No demonstrated operational consequence justifies prioritizing it over current correctness investigations. |
| [Field-TM centroid download #2730](https://github.com/hotosm/field-tm/issues/2730) | Maintainer described low priority; a later contributor already traced both repositories without a reproduction. Avoid duplicating that static trace. |
| [Field-TM synchronization #3099](https://github.com/hotosm/field-tm/issues/3099) | Maintainer explains that current Field-TM delegates data collection/sync to ODK or QField. The reporter's loss/duplication claims were not verified. No Field-TM sync patch is justified. |
| [Field-TM reference geometry #3120](https://github.com/hotosm/field-tm/issues/3120) | Potentially useful mapping context, supported by current ODK feature documentation. However, pinned contribution rules reject automated bot/AI accounts; incompatible with Humanifest's required identity, so not active queue work. |
| [Open Food Facts request configuration #507](https://github.com/openfoodfacts/openfoodfacts-python/issues/507) | Two contributors describe already-prepared implementations. Avoid competing work. |
| [Open Food Facts text search #496 / PR #504](https://github.com/openfoodfacts/openfoodfacts-python/pull/504) | Added a support-existing-contribution research item after finding a specific mismatch between the proposed endpoint and official search semantics. Subsequent [runtime verification](2026-09-09-openfoodfacts-runtime-verification.md) passed 38 SDK tests and four original-server-filter cases; accepted scope and live behavior remain unverified. |

Field-TM was inspected at `68feb4d05306dd4b58110721d027fba0d1f0acf0`. Its
[contribution guide](https://github.com/hotosm/field-tm/blob/68feb4d05306dd4b58110721d027fba0d1f0acf0/CONTRIBUTING.md)
explicitly rejects automated bot/AI accounts. The
[shared HOT guide](https://docs.hotosm.org/become-a-contributor/#how-contributions-are-handled)
states the same restriction. This corrected the earlier Tasking Manager audit:
human-led AI assistance is permitted, but that is not bot-account acceptance.
The existing HOT opportunity is now PARKED, and its install retry is superseded.
Do not sign an agreement, claim human authorship or use the personal account to
bypass that policy. Existing findings and delivered inquiry provenance remain.

Other initial screens were not promoted: the guessed WFP-VAM food-price scraper
repository returned 404, which establishes neither project inactivity nor absence
of another repository; the first page of current OpenRefine issues was dominated
by assigned work or platform-specific build tasks. Neither is an exhaustive audit.

## Subsequent current-state screen

The search index still presented OWID ETL #6572 and #6165 as open. Direct GitHub
API reads on September 9 showed both closed (August 14 and August 20 respectively).
Do not create duplicate fixes from those stale results. #6165's closing discussion
says it can be reconsidered if it causes problems; an earlier proposed fix is not
proof that further contribution is currently wanted.

XLSForm pyxform #821 is now an independent research item. The
[nested-repeat audit](2026-09-09-pyxform-nested-repeat-audit.md) records a current
public request for an effort investigation, source/test boundaries, setup
requirements and the explicit limit on claimed impact. The contribution is not
approved or implemented. ODK maintenance groups it with getodk review capacity.

Other XLSForm reports were not added at this stage: #856 describes an edge-case
required binding that clients ignore and has no discussion; #844 reports an
instance-expression label mismatch but has no discussion or independent
reproduction. Neither was established as more consequential than #821's requested
investigation. #829 already has open PR #830. This screen is not an exhaustive
ranking of all humanitarian work.

Sources accessed September 9: [OWID #6572](https://github.com/owid/etl/issues/6572),
[OWID #6165](https://github.com/owid/etl/issues/6165),
[XLSForm #856](https://github.com/XLSForm/pyxform/issues/856),
[XLSForm #844](https://github.com/XLSForm/pyxform/issues/844),
[XLSForm open PRs](https://github.com/XLSForm/pyxform/pulls).
