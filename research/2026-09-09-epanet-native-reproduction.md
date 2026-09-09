# EPANET water-storage curve behavior in the original native library

September 9, 2026. This follows the [source intake](2026-09-09-epanet-tank-curve-audit.md).
The subject is water-storage geometry in a drinking-water distribution model.
All networks here are synthetic local files. No real utility system, operational
data, military system, security assessment or deployed service is involved.

## Result

**34 current-behavior cases pass against the compiled, unmodified C library.**
Passing means the assertions accurately reproduce existing behavior, including
incorrect behavior; it does not mean EPANET has been repaired. No upstream code
was changed, maintainer inquiry sent or implementation scope accepted.

At dev `83e25bbe2b0b460803e71df03bc989afe9557ea3`, increasing depth values
`[0, 3, 6, 10]` were paired with three sets of volume values:

| Shape | Volume values | Volume returned at requested depths 3 → 6 |
| --- | --- | --- |
| Increasing control | `[0, 30, 60, 100]` | 30 → 60 |
| Decreasing | `[100, 70, 40, 0]` | 70 → 40 |
| Interior dip, positive endpoint slope | `[0, 60, 30, 100]` | 60 → 30 |

Every combination was exercised through file loading, `EN_VOLCURVE` assignment,
`EN_settankdata` assignment, bulk editing an assigned curve and point-by-point
editing an assigned curve, in both GPM and LPS modes: 30 cases. Four additional
controls cover unchanged cylindrical-tank volumes and a valid four-point
decreasing pump curve, in both modes. These use identical numeric inputs in
each unit system, not equivalent physical networks.

All file-open and mutation calls returned zero. Hydraulic opening and
initialization also returned zero for all cases. Raising the requested initial
depth from 3 to 6 returned the volumes in the table through `EN_INITVOLUME`.
Metric results agree within floating-point rounding. These are direct API
queries after setting initial depth, **not a simulated filling time series**.

For decreasing curves, file loading and either direct assignment route return
`NaN` from the public diameter getter with error code zero. The process did not
crash. Bulk/point edits retain a finite old nominal diameter while subsequent
depth changes use the newly invalid curve. Interior dips retain finite diameter
on every route. Checking endpoint slope or diameter alone would miss those cases.

## Separate metric discrepancy

The increasing control exposed a separate inconsistency. In LPS mode, file
loading and `EN_settankdata` return diameter `3.5682482323055424`, whereas
`EN_VOLCURVE` assignment returns `1.0876020612067294`, a ratio of **0.3048**.
The same difference occurs for the positive-endpoint interior-dip curve. GPM
routes agree. The harness asserts this observed discrepancy explicitly.

Source inspection finds that `EN_settankdata` converts the endpoint-derived area
using `Ucf[ELEV]` twice, while the `EN_VOLCURVE` branch assigns the raw slope.
This supports a unit-conversion explanation, but no separate duplicate search,
accepted correction or downstream hydraulic consequence is established yet.
Do not silently fold an additional fix into #883.

## Build, integrity and reproduction

- Target: pinned OWA-EPANET dev revision above, cloned outside Humanifest under
  `/private/tmp/humanifest-epanet-native/source`.
- CMake 3.31.6 universal macOS wheel: 47,224,338 bytes, SHA256
  `da9d4fd9abd571fd016ddb27da0428b10277010b23bb21e3678f8b9e96e1686e`,
  verified against [PyPI release metadata](https://pypi.org/pypi/cmake/3.31.6/json).
  Inspected metadata/entry points; unpacked locally and invoked the bundled native
  binary without installing Python hooks or changing global tools.
- Apple Clang 21.0.0 on macOS arm64; CMake Release build with `BUILD_TESTS=OFF`
  and `BUILD_COVERAGE=OFF`. Original library, output library and CLI all build.
  Configuration emits old-minimum-CMake compatibility notices; build log has
  no compiler warnings/errors. No Conan, Windows scripts or coverage commands run.
- Python 3.13.7 standard-library `ctypes` calls the real shared library. Argument
  signatures and enum values come from the inspected pinned public headers.
  No copied EPANET functions, test doubles, patched source or replacement math.
- Shared library SHA256:
  `3b6ca9970af751fe3374070230c354804c76e1d7ad9fd71ca55d2fcd7c81fc2f`.
- All **144 tracked source files** are byte-identical to their pre-build hashes
  and remain unchanged after probes. The expected ignored generated file
  `src/outfile/include/epanet_output_export.h` is the only reported source-tree
  build output. Network inputs/reports are temporary and cleaned by the fixture.

After acquiring the pinned source and reviewed CMake binary, run the documented
native build route, then the [reproduction fixture](fixtures/epanet_tank_curve_probe.py):

```bash
cmake -S /path/to/EPANET -B /path/to/build -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTS=OFF -DBUILD_COVERAGE=OFF
cmake --build /path/to/build --parallel 4
python3 research/fixtures/epanet_tank_curve_probe.py \
  --source /path/to/EPANET \
  --library /path/to/build/lib/libepanet2.dylib \
  --output /path/to/results.json
```

Use the platform's shared-library filename where different. The harness enforces
the exact source revision and clean tracked files, records library/source hashes,
and downloads or installs nothing. Local raw results are retained at
`/tmp/humanifest-epanet-native/tank-curve-results.json`; the fixture reproduces
the table and detailed before/after values. No full Boost test-suite claim is made.

## Completed audit and remaining work

The remaining parser and `validate.c` paths were read: tank checks cover level
bounds and curve checks cover data presence/increasing X. Pump validation has its
own decreasing-head requirement. The measured file/API cases establish acceptance
for these specific malformed inputs, not every malformed curve or input file.

All four CI definitions, Conan recipe, CMake files and Windows build/test guide
were inspected. CI builds leave tests disabled; the separate native test suite
requires Boost unit-test, system, thread and filesystem components. No global
Boost installation or unchanged-suite baseline has occurred. Coverage helpers
are optional and not invoked. No target services, ports or secrets are required.
An organization `.github` contents query returned 404; no explicit bot policy
was established. Absence of a retrieved policy does not establish acceptance.

Next: set up reviewed isolated Boost dependencies and run unchanged tests, check
whether the metric discrepancy is already tracked, and prepare a short #883
evidence/scope inquiry with accurate AI/bot disclosure. Maintainer confirmation
is still required before implementing a patch. Error codes, strictness/tolerance,
curve-type sharing and rollback semantics remain decisions to agree.

The hydraulic solver was opened/initialized but **never advanced with `EN_runH`**.
No extended-period simulation, physical water-safety assessment, operational
deployment or realized humanitarian benefit is measured. The public-benefit
pathway remains the documented drinking-water modeling use case.

Sources accessed September 9, 2026:

- [EPA: drinking-water distribution modeling](https://www.epa.gov/water-research/epanet)
- [Reported water-storage curve issue #883](https://github.com/OpenWaterAnalytics/EPANET/issues/883)
- [Pinned public API implementation](https://github.com/OpenWaterAnalytics/EPANET/blob/83e25bbe2b0b460803e71df03bc989afe9557ea3/src/epanet.c)
- [Pinned validation](https://github.com/OpenWaterAnalytics/EPANET/blob/83e25bbe2b0b460803e71df03bc989afe9557ea3/src/validate.c)
- [Pinned build/test guide](https://github.com/OpenWaterAnalytics/EPANET/blob/83e25bbe2b0b460803e71df03bc989afe9557ea3/BUILDING.md)
