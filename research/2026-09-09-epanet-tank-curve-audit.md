# EPANET tank-volume curve verification intake

Initial intake accessed September 9, 2026. This historical snapshot predates
target execution. See [the subsequent native reproduction](2026-09-09-epanet-native-reproduction.md)
for the completed build and measured behavior; current portfolio records include it.

## Public-benefit pathway and current need

[EPA describes EPANET](https://www.epa.gov/water-research/epanet) as a tool for
modeling water-distribution hydraulics and water quality, including infrastructure
planning, operational analysis and emergency preparation. OWA-EPANET is the
community-maintained engine branch; its README explicitly distinguishes it from
an official EPA release. This establishes a relevant water-infrastructure use
case, not a measured water-safety or resource-saving outcome from this work.

[OWA issue #883](https://github.com/OpenWaterAnalytics/EPANET/issues/883), reported
by LRossman, says decreasing volume values can be assigned to a tank curve,
leading to nonsensical volume/area calculations. It remains open, unassigned and
without comments. Dev is `83e25bbe2b0b460803e71df03bc989afe9557ea3`; repository is
unarchived, pushed August 27, 2026. No matching fix appears in the complete list
of four open PRs. These facts do not confirm that a Humanifest patch is wanted.

The issue's claim of a floating-point exception is not yet independently
reproduced. A negative square-root input can produce a nonfinite value without
terminating a process; runtime behavior and returned errors must be measured,
not inferred from the title or one expression.

## Source paths and controls needed

- `src/input1.c:inittanks` interpolates initial/min/max volumes and derives nominal
  tank diameter from the end-to-end curve slope using a square root.
- `EN_setnodevalue(..., EN_VOLCURVE, ...)` checks curve index, tank type and whether
  tank levels lie in the curve's X range. The inspected branch then assigns the
  curve, interpolates volumes and derives area from the endpoint slope without
  checking increasing Y values there.
- `EN_settankdata` similarly checks level ranges and computes area from the curve's
  endpoints. It is a second public assignment route, not covered by inspecting
  only `EN_VOLCURVE`.
- `EN_setcurve` and `EN_setcurvevalue` check increasing X values but do not check Y
  ordering. `EN_setcurvetype` only checks that the supplied type is in range.
  Changing an already assigned curve could therefore be a separate mutation path.
- Generic curves also serve pumps and other purposes. Do not impose increasing Y
  globally: a valid decreasing pump curve is an essential compatibility control.
- A curve whose endpoints increase can still dip at an interior point. A simple
  positive endpoint-slope check would not establish monotonic volume throughout.

The complete file-loading validation path still needs tracing before claiming
that all malformed curves are accepted. Existing `test_curve.cpp` checks curve
comments, values and identifiers; `test_node.cpp` includes a cylindrical-tank
volume preservation regression. Those files were read but not executed.

Next, finish the remaining parser/validation and build audit, then build the pinned
unmodified library outside Humanifest and run tiny synthetic networks through its
public API and file loader. Cover valid increasing volume, decreasing volume,
interior dips with positive endpoint slope, unchanged cylindrical tanks and a valid
decreasing pump curve. Compare file loading, API assignment and post-assignment
edits, plus US/metric-unit controls where they affect the path. Check return codes,
finite area/diameter, and volume-versus-level behavior; keep invalid-data outcomes
separate from a claimed physical simulation or operational impact. Do not select
new error codes, tolerance policy or mutation semantics before maintainer agreement.

## Build and contribution audit

Read README, BUILDING, MIT license, Contributor Covenant, root/run/output/tests
CMake files, macOS/Linux CI and relevant C/C++ sources. README asks contributors
to discuss an issue before choosing a path, fork and branch from dev, and submit a
PR for review. No explicit bot/AI rule or CLA requirement was established in the
inspected files; organization-wide policy and Humanifest eligibility remain to
verify. No agreement has been signed and no reviewer has committed to this scope.

The native build uses CMake and a C compiler. Tests require Boost unit_test_framework,
system, thread and filesystem. **BUILD_TESTS defaults to OFF**; inspected macOS and
Linux CI configure without enabling it, then build/upload artifacts. A green build
there does not prove the test suite ran. The documented test route enables
BUILD_TESTS and runs CTest. Windows CI, Conan and optional coverage tooling were
not executed or fully audited.

The output-library CMake step copies a generated export header back into
`src/outfile/include`; preserve and account for that build output when checking
source integrity. No build/install command has run. Host Clang is present; CMake
was not found on PATH and Boost was absent at the checked Homebrew include/library
paths. This is a setup task, not proof that the environment is impossible. Prefer
an isolated reviewed tool/dependency setup, with no global installation or target
setup execution before its audit. No services, ports, operational secrets or
real utility network data are needed for the proposed synthetic reproduction.

## Other leads excluded or deferred

- [Leakage #922](https://github.com/OpenWaterAnalytics/EPANET/issues/922) already has
  the maintainer's revised fix and another user's successful single/multiple-pipe
  checks. Current dev sets `LeakageChanged` when relevant API values change,
  reinitializes leakage in `runhyd`, and clears the flag. Do not duplicate that fix
  simply because the issue remains open.
- [Water-age #913](https://github.com/OpenWaterAnalytics/EPANET/issues/913) includes
  screenshots and a ChatGPT-generated explanation about stagnant-flow thresholds.
  No actual input file or independent mechanism reproduction was established in
  this screen. It remains a possible research lead, not verified hydraulic/quality
  causation or a more urgent task than the bounded invalid-input investigation.
- #885 has PR #886; Lua support has PR #932. The unclear title of PR #930 was
  resolved by reading its files: website and editor configuration, not tank curves.
- Search presented locale issue #875 as open, but it was absent from the complete
  current open-issue list. Its exact resolution was not investigated; do not queue
  it from the search snippet alone.

A read-only check of CHT #10155 and Open Food Facts PR #504 found no maintainer
reply after the Humanifest notes. No repeated nudge was sent; their existing review
dates and states remain unchanged.

## Sources

Accessed September 9, 2026:

- [Current #883](https://github.com/OpenWaterAnalytics/EPANET/issues/883)
- [Pinned README](https://github.com/OpenWaterAnalytics/EPANET/blob/83e25bbe2b0b460803e71df03bc989afe9557ea3/README.md)
- [Pinned file initialization](https://github.com/OpenWaterAnalytics/EPANET/blob/83e25bbe2b0b460803e71df03bc989afe9557ea3/src/input1.c)
- [Pinned public API](https://github.com/OpenWaterAnalytics/EPANET/blob/83e25bbe2b0b460803e71df03bc989afe9557ea3/src/epanet.c)
- [Pinned curve tests](https://github.com/OpenWaterAnalytics/EPANET/blob/83e25bbe2b0b460803e71df03bc989afe9557ea3/tests/test_curve.cpp)
- [Pinned node tests](https://github.com/OpenWaterAnalytics/EPANET/blob/83e25bbe2b0b460803e71df03bc989afe9557ea3/tests/test_node.cpp)
- [Pinned build instructions](https://github.com/OpenWaterAnalytics/EPANET/blob/83e25bbe2b0b460803e71df03bc989afe9557ea3/BUILDING.md)
- [Pinned CMake test configuration](https://github.com/OpenWaterAnalytics/EPANET/blob/83e25bbe2b0b460803e71df03bc989afe9557ea3/tests/CMakeLists.txt)
