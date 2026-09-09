# CLIMADA wildfire fraction: research intake

Accessed September 9, 2026. Public issue and pinned-source inspection only.
No clone, dependency installation, target import, hazard-data download or upstream
message occurred. The reported numerical results below are not independently
reproduced.

## Current need and public-benefit pathway

[CLIMADA #1312](https://github.com/CLIMADA-project/climada_python/issues/1312)
reports duplicate sparse entries in wildfire fraction data, including the v1.1
release intended to address an earlier intensity-data issue. The reporter says
fractions greater than one propagate into impact estimates. The issue is open,
unassigned and has no comments in the current API response. No matching PR was
identified in the complete returned list of 17 open PRs. This is not confirmation
of an accepted Humanifest scope or proof of no private work.

The ETH-hosted project site describes climate-risk assessment and adaptation
option appraisal. The potential contribution is model/data correctness for those
analyses. This does not establish improved adaptation decisions, avoided losses,
beneficiaries or realized humanitarian benefit. The report's country-sweep
percentages and comparisons with a published study remain self-reported.

## Pinned source and a necessary distinction

Repository is unarchived, pushed September 7. Default main is
`5cb73da1a5daee3bf46486d42bff8a511adb1a67`; contributions target **develop**,
inspected at `dea46facc7856ed1c26adc1ee03e954c77d30c1b`.

- `Hazard.check_matrices` calls `prune_csr_matrix` on both intensity and fraction,
  then checks their shapes when fraction has nonzero entries.
- `prune_csr_matrix` checks structure, eliminates zeros and sums duplicate
  entries. Its documentation explicitly says apparent matrix values are preserved.
  SciPy documents addition of duplicates as the operation's intended behavior.
- `ImpactCalc.__init__` calls `hazard.check_matrices`. `impact_matrix` obtains
  mean damage ratios and fraction, then multiplies fraction, ratios and exposure
  values. `_get_fraction` returns nonempty fraction data without a range check;
  an empty fraction represents multiplication by one.
- Merged PR #893 expressly limited its change to consistent sparse storage, not
  repair of unintentionally summed source values. The new report should not be
  framed as proof that the canonicalizer itself introduces new mathematical values.

A plausible validation or data-generation defect is different from an error in
sparse summation. Do not substitute `max`, clip all fraction values, or repair a
published dataset before establishing the intended data semantics and provenance.

## Existing tests and bounded next work

Read the existing checker, hazard-base and impact-calculation test files.
`test_prune_csr_matrix` checks sparse canonicalization. Hazard tests exercise
fraction shape and empty-fraction behavior; impact tests exercise multiplication.
Some fixtures deliberately contain values above one or below zero (e.g. fraction
2 in the hazard fixture and -1 in the impact-matrix fixture). These values do not
prove such fractions are physically valid, but an unconditional range restriction
would affect existing assumptions and needs explicit review.

Next, finish the CI/configuration and dependency audit and execute hash-checked
original canonicalization/fraction/impact methods with tiny synthetic sparse
inputs, without importing the full package. Include duplicate ones, unique bounded
fractions, fractional duplicates, negative/out-of-range values, empty-fraction
identity and shape mismatch controls. Compare the apparent matrix *before* and
*after* canonicalization using independent copies so an observation does not
silently mutate the test subject. Separately check propagation into impact with
known exposure values and a clearly disclosed damage-ratio test double.

This can establish a small method-level reproduction and an appropriate scope
question. It cannot verify the live wildfire data version, national percentages,
full hazard loading, geospatial assignment or policy consequences. Obtain
maintainer agreement before choosing data regeneration, validation, warnings or
an implementation contract. No full-framework feasibility gate passes yet.

## Setup and contribution constraints

Read CONTRIBUTING, README, pyproject, PR template, CODEOWNERS and the relevant
source/test files. Metadata and source headers declare GPLv3; the LICENSE file was
retrieved, but a full dependency/license audit has not been completed.

Contributions may use a fork and must target develop, with tests, Pylint,
documentation/changelog and attribution updates. The guide references additional
developer/reviewer guidance still to inspect. No explicit bot/AI policy was
established in the inspected files; absence is not acceptance. CODEOWNERS names
emanuel-schmid, chahank and peanutfun globally; this identifies potential reviewers,
not a commitment or an invitation to tag all three.

The manifest requires Python >=3.10,<3.14 and a broad native/geospatial dependency
set, including GDAL, Fiona, rasterio, cartopy and NetCDF. The package initializer
calls `setup_climada_data()` on import, creating configured system/demo directories
and copying bundled files (home-directory defaults). No full package import should
precede explicit data-path and configuration review. The tree also contains
Conda requirements, CI/release workflows, pre-commit configuration and a docs
Dockerfile; their setup paths have not yet been audited. No release or data-upload
operation is part of this research.

## Other leads not promoted

- #1268 (duplicated FAST cyclone tracks) is assigned, and its fix #1269 is verified
  merged May 15. A recent commenter already supplies a regression check. Do not
  duplicate that work merely because the issue remains open.
- #1319's pandas compatibility report already has PR #1320; #1314's CI request has
  PR #1318; World Bank URL issues have PR #1292.
- #1321 contains several remote-data problems and already detailed reporter
  verification. The NOAA replacement involves authentication; no blind URL patch
  or credential workflow is justified by the report.
- #1316's rasterio coordinate-resolution difference needs a version/geometry
  contract investigation. It has no discussion or independently verified impact
  in this screen; it was not added ahead of the fraction investigation.

## Sources

Accessed September 9, 2026:

- [CLIMADA purpose and maintenance](https://climada.ethz.ch/)
- [Issue #1312](https://github.com/CLIMADA-project/climada_python/issues/1312)
- [Pinned contribution guide](https://github.com/CLIMADA-project/climada_python/blob/dea46facc7856ed1c26adc1ee03e954c77d30c1b/CONTRIBUTING.md)
- [Pinned hazard checks](https://github.com/CLIMADA-project/climada_python/blob/dea46facc7856ed1c26adc1ee03e954c77d30c1b/climada/hazard/base.py#L214)
- [Pinned sparse canonicalizer](https://github.com/CLIMADA-project/climada_python/blob/dea46facc7856ed1c26adc1ee03e954c77d30c1b/climada/util/checker.py#L199)
- [Pinned impact multiplication](https://github.com/CLIMADA-project/climada_python/blob/dea46facc7856ed1c26adc1ee03e954c77d30c1b/climada/engine/impact_calc.py#L464)
- [Pinned hazard tests](https://github.com/CLIMADA-project/climada_python/blob/dea46facc7856ed1c26adc1ee03e954c77d30c1b/climada/hazard/test/test_base.py#L92)
- [Pinned impact tests](https://github.com/CLIMADA-project/climada_python/blob/dea46facc7856ed1c26adc1ee03e954c77d30c1b/climada/engine/test/test_impact_calc.py#L971)
- [SciPy duplicate addition](https://docs.scipy.org/doc/scipy/reference/generated/scipy.sparse.csr_matrix.sum_duplicates.html)
- [Prior sparse-storage fix #893](https://github.com/CLIMADA-project/climada_python/pull/893)
- [Merged FAST fix #1269](https://github.com/CLIMADA-project/climada_python/pull/1269)
