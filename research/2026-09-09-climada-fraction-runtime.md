# CLIMADA fraction methods and public COD data verification

Executed September 9, 2026. The current public COD v1.1 file independently
confirms the reported duplicate-fraction counts. The checked impact methods allow
out-of-range fractions through. This does not verify population-weighted impacts,
the 72-country sweep, a full framework installation or downstream decision effects.

## Pinned inputs and reproduction

Source: develop `dea46facc7856ed1c26adc1ee03e954c77d30c1b`.
[Method harness](fixtures/climada_fraction_reproduction.py) verifies SHA-256 hashes
of the four original source/test files before and after execution. It extracts
unchanged function bodies with AST locations; only indentation changes. The
original storage unit test executes as a unittest TestCase. No CLIMADA package
module is imported or installed. Dependencies already available: Python 3.13.7,
NumPy 2.3.4 and SciPy 1.16.2.

```bash
python3 research/fixtures/climada_fraction_reproduction.py /tmp/humanifest-climada-screen
```

Flattened source filenames replace `/` with `__`; retrieve the paths named by
`HASHES` from the pinned revision, without running repository setup. The harness
checks the exact bytes, so a new source revision requires a deliberate review.

The original `Hazard.check_matrices`, `_get_fraction`, `ImpactCalc.__init__`,
`impact_matrix` and `prune_csr_matrix` execute on small probe objects. `get_mdr`
is a disclosed test double returning `[0.25, 0.5]`; exposures are `[100, 200]`.
No impact function, centroid assignment or full geospatial model is evaluated.

## Synthetic results

Original `TestChecks.test_prune_csr_matrix`: **1 passed**. Eight numeric impact
cases passed, plus a separate expected shape-mismatch rejection.

| Fraction case | Apparent fraction before and after normalization | Impact by exposure | Total |
| --- | --- | --- | ---: |
| Duplicate ones | `[2, 1]` | `[50, 100]` | 150 |
| Unique ones | `[1, 1]` | `[25, 100]` | 125 |
| Bounded fractions | `[0.25, 0.75]` | `[6.25, 75]` | 81.25 |
| Fractional duplicates | `[0.5, 0.75]` | `[12.5, 75]` | 87.5 |
| Negative fraction | `[-0.25, 0.75]` | `[-6.25, 75]` | 68.75 |
| Fraction above one | `[1.5, 1]` | `[37.5, 100]` | 137.5 |
| Empty fraction | empty | `[25, 100]` | 125 |
| Explicit zeros | all zeros, then empty | `[25, 100]` | 125 |

Observations use independent sparse copies and assert that the subject's raw
arrays stay unchanged. Duplicate ones already represent two at a repeated cell;
normalization preserves that apparent value. Generic `max` would change the
valid fractional-duplicate result. Empty fraction intentionally means identity;
a proposed clamp-to-zero repair could therefore behave unexpectedly.

## Public dataset provenance and measured results

[Public metadata query](https://climada.ethz.ch/data-api/v2/dataset/?data_type=wildfire&country_iso3alpha=COD&status=&limit=100)
returned one active dataset, UUID `b08e7a2b-3ec9-4792-8dc1-daf999a1b899`, version
`v1.1`, created May 7 and activated May 8, 2026, declared CLIMADA v6.1.0.
Its metadata licenses the data under **CC BY 4.0** and attributes the wildfire
hazard to CLIMADA Petals using NASA FIRMS MODIS/VIIRS data. It discloses regular-grid
remapping, a 120-versus-150-arcsecond calibration difference, possible metropolitan
overestimation and lack of tropical impact validation. Those caveats are not
independently resolved by this check. Attribution: CLIMADA data API / ETH Zurich,
wildfire dataset credited in its description to Samuel Lüthi; underlying NASA FIRMS.

[Original unmodified artifact](https://data.iac.ethz.ch/climada/b08e7a2b-3ec9-4792-8dc1-daf999a1b899/wildfire_COD_150arcsec_historical_2001_2020.hdf5):

- Filename: `wildfire_COD_150arcsec_historical_2001_2020.hdf5`.
- Downloaded bytes: **31,323,560**, exactly matching metadata.
- Publisher MD5, verified: `86337f8a6060f7a497d6bc7990047a68`.
- Independently computed SHA-256: `e62c41b250786ff36bdf6400d7e84cc38cc650a3ceab67c4c00ce3a53f6aeb8f`.
- Both sparse matrix shapes: **20 × 109,268**.

[Data harness](fixtures/climada_wildfire_data_check.py) opens the original file
read-only, loads only CSR `data`, `indices`, `indptr` and shape metadata, and
checks duplicate indices independently row by row. It then runs the original
canonicalizer on copies and verifies original arrays and dataset hashes remain
unchanged. No dense national matrix or CLIMADA API client is loaded.

| Field | Raw entries | Extra duplicate entries | Duplicated cells | Canonical entries |
| --- | ---: | ---: | ---: | ---: |
| fraction | 1,296,686 | 104,708 | 99,939 | 1,191,978 |
| intensity | 1,191,978 | 0 | 0 | 1,191,978 |

All raw fractions equal one. Canonical fraction value/count pairs are
**1: 1,092,039; 2: 97,236; 3: 637; 4: 2,066**. All 99,939 fraction cells above
one overlap positive intensity. The fraction sum is **1,296,686** both before
and after normalization. Its ratio to binary support is **1.0878439031592866**.
This arithmetic comparison is not a population-weighted or full impact-model
estimate, and binary replacement is not an approved data repair. The raw
intensity range is 300.5–506.5; its sum is unchanged by normalization.

## Environment audit and limits

Read the pinned CI workflow, Conda manifest, pre-commit hooks, docs Dockerfile,
configuration module/file, API client, hazard HDF5 loader and linked Git/testing/
coding guides before the relevant execution. CI uses Linux Python 3.11–3.13,
micromamba, a development install and unit tests, then a reusable Petals workflow.
The full native/geospatial environment and downstream workflow were not executed.
The docs Dockerfile runs apt and a Miniconda installer; it was not built. Hooks
pin pre-commit checks, isort and Black; they were inspected, not installed.

The package initializer creates/copies configured system/demo data; the API
client opens/creates a SQLite download cache at module scope. Neither is imported.
The public metadata request and artifact download use explicit URLs instead.
No services, ports, credentials, private data or release/upload operations are
needed for these probes.

For HDF5, a temporary venv with access to existing system site packages installs
only the binary h5py 3.14.0 wheel, with `--no-index --no-deps` after a separate
verified download. This is not a frozen full-framework environment. PyPI metadata
requires Python >=3.9 and NumPy >=1.19.3 and declares BSD-3-Clause. The inspected
wheel has no `.pth`, entry-point or lifecycle-script paths. The arm64 CPython 3.13
wheel SHA-256 is `ef9603a501a04fcd0ba28dd8f0995303d26a77a980a1f9474b3417543d4c6174`;
runtime h5py is 3.14.0 and bundled HDF5 is 1.14.6. No source build or global install.

```bash
/tmp/humanifest-climada-hdf5-venv/bin/python research/fixtures/climada_wildfire_data_check.py \
  /tmp/humanifest-climada-screen \
  /tmp/humanifest-climada-screen/wildfire_COD_150arcsec_historical_2001_2020.hdf5
```

Children use a minimal environment, a 60-second timeout, one BLAS thread and
Python socket/DNS/subprocess blocking. HDF5 plugin loading is disabled; selected
fields must be local hard links, nonvirtual numeric arrays with bounded size.
These are Python-level controls, not OS isolation or a native-code security audit.
The first HDF5 run failed because h5py's import asks the standard library for
processor information using `uname`; the harness now primes that standard-library
cache before enabling the process block and importing third-party libraries. The
completed run passes; no upstream source was changed to accommodate the harness.

No production fix is selected. Maintainer agreement on fraction semantics, data
regeneration versus diagnostics, bot eligibility and review scope remains needed.
A full-framework baseline, population-weighted calculations and useful deployment
outcomes remain unverified. Source/dataset versions are different by declaration:
the method probe uses develop; the API data declares v6.1.0.
