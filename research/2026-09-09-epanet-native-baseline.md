# EPANET unchanged native test baseline

September 9, 2026. Completes the dependency/test work left pending in the
[native water-storage curve reproduction](2026-09-09-epanet-native-reproduction.md).
No upstream code changes or message were made in this step.

## Verified results

The pinned source remains `83e25bbe2b0b460803e71df03bc989afe9557ea3`.
All six registered CTest programs pass; the additional compiled string-helper
program also passes when run separately.

| Original executable | Verified result |
| --- | --- |
| `test_net_builder` | 4 Boost cases pass |
| `test_toolkit` | 64 Boost cases pass |
| `test_reent` | Both threaded EPANET runs print status 0 |
| `test_errormanager` | 3 Boost cases pass |
| `test_filemanager` | 3 Boost cases pass |
| `test_output` | 12 Boost cases pass |
| `test_cstrhelper` | 2 Boost cases / 6 assertions pass; not registered in CTest |

That is **88 Boost cases across six binaries, plus the threaded executable**.
`test_reent` always returns zero from `main`, even if its model runs fail; its
two actual status messages were therefore inspected instead of trusting the
process exit alone. CTest reports six of six passed in 5.95 seconds. The separate
string-helper result closes a coverage omission in the runner configuration;
no target CMake file was changed. Sources commented out in the upstream CMake
list, such as `test_pump.cpp`, were not independently added to the build.

The 34 water-storage curve reproduction cases also pass against the test-enabled
library. That binary has the same SHA256 as the earlier build:
`3b6ca9970af751fe3374070230c354804c76e1d7ad9fd71ca55d2fcd7c81fc2f`.
**All 144 tracked target files remain byte-identical to their pre-build hashes.**
The suite writes ignored temporary reports/networks alongside its public test
fixtures; no tracked fixture was changed. The previously documented generated
output export header remains an expected ignored build output.

These are regression-baseline and synthetic reproduction results. They do not
establish a fixed bug, accepted contribution, production deployment or measured
benefit to a water utility. The original suite exercises its own bundled example
simulations; the separate 34-case fixture still stops at hydraulic initialization.

## Isolated Boost build audit

The [official Boost 1.85.0 archive](https://archives.boost.io/release/1.85.0/source/boost_1_85_0.tar.bz2)
contains 124,015,250 compressed bytes, 85,080 entries and 757,529,043 unpacked
file bytes. Its SHA256 matches the [official metadata](https://archives.boost.io/release/1.85.0/source/boost_1_85_0.tar.bz2.json):
`7009fe1faa1697476bdc7027703a2badb84e849b7b0baad5086b087b971f8617`.
Archive paths were checked and Python's data extraction filter used. No setup
was run before inspection of the bootstrap/build path and selected libraries.

Read the Boost Software License 1.0, bootstrap script, relevant engine build
logic, selected test/system/thread/filesystem build definitions and transitive
atomic/chrono definitions. The selected path compiles local sources; it needs
no downloads during execution, services, listening ports, credentials or root
privileges. ICU/Python integrations and unrelated optional libraries are unused.

Built with Apple Clang 21.0.0 for arm64, C++11, Release, shared libraries and
four workers. Bootstrap and B2 ran with only a system PATH and task-specific
temporary-directory environment, without inherited credentials. B2 site/user
configuration loading was disabled. Everything is under
`/private/tmp/humanifest-epanet-native`; nothing was installed globally.

The first test configuration found the four directly requested libraries and
atomic, but reported missing chrono. The original test build succeeded; before
running tests, chrono's build definition was inspected and that component staged
as well. Final configuration finds **unit_test_framework, system, thread,
filesystem, chrono and atomic**. Old-minimum-CMake and CMP0167 development
warnings remain; they are not test failures. Compiler build logs contain no
warnings/errors from EPANET sources.

## Reproduction commands

After verifying and extracting the archive, from its root:

```bash
sh bootstrap.sh --with-toolset=clang \
  --with-libraries=test,system,thread,filesystem --without-icu \
  --prefix=/path/to/temporary/boost-install
./b2 --ignore-site-config --user-config= -j4 \
  --with-test --with-system --with-thread --with-filesystem --with-chrono \
  toolset=clang variant=release link=shared runtime-link=shared \
  threading=multi architecture=arm address-model=64 cxxstd=11 \
  --layout=system --stagedir=/path/to/temporary/boost-stage stage
```

Then configure and test the pinned EPANET source:

```bash
cmake -S /path/to/EPANET -B /path/to/build-tests \
  -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTS=ON -DBUILD_COVERAGE=OFF \
  -DBOOST_ROOT=/path/to/boost_1_85_0 \
  -DBOOST_LIBRARYDIR=/path/to/temporary/boost-stage/lib \
  -DBoost_NO_SYSTEM_PATHS=ON -DBoost_NO_BOOST_CMAKE=ON
cmake --build /path/to/build-tests --parallel 4
ctest --test-dir /path/to/build-tests -V --parallel 1 --timeout 120
/path/to/build-tests/bin/test_cstrhelper --report_level=detailed
```

Serial CTest avoids collisions in shared upstream output filenames. Use the
platform's compiler/architecture settings elsewhere. The recorded macOS runner
used the previously verified CMake 3.31.6 binary and no elevated runtime rights.

Local evidence:

- `epanet-ctest.log`: SHA256
  `baf00450ae7591b8e4d33a512fb6b8f1f13120d80930da52708509f831bd05a3`.
- `epanet-cstrhelper.log`: SHA256
  `04545131bcab9aa442b57501d589d8b758d24d25b29f2c7e1f173ce369c7d35e`.
- `tank-curve-results-tests-build.json`: all 34 reproduction cases against the
  test-enabled library. All logs/results are in `/tmp/humanifest-epanet-native`.

## Duplicate and maintainer checks

GitHub issue searches for `EN_VOLCURVE`, `tank diameter metric`, and
`volume curve units` returned 4, 1 and 3 results respectively, with
`incomplete_results=false`. Full related discussions were read:

- [#464](https://github.com/OpenWaterAnalytics/EPANET/issues/464) concerns parameter
  update semantics and switching between cylindrical geometry and volume curves.
- [#597](https://github.com/OpenWaterAnalytics/EPANET/issues/597) concerns an older
  zero-maximum-volume division; the maintainer states it was addressed in #580.
- [#720](https://github.com/OpenWaterAnalytics/EPANET/issues/720) concerns converting
  the network when changing unit systems.
- [#903](https://github.com/OpenWaterAnalytics/EPANET/pull/903) concerns assigning
  curve types for `EN_setflowunits`, preserving pressure units and adjusted tests.

These differ from assigning a valid water-storage curve while keeping LPS units
fixed, which produced the nominal-diameter ratio of 0.3048 in our reproduction.
This bounded search found no matching report; it does not prove novelty or
consequence. Next verify file round-trips and simulated behavior before proposing
separate work: the discrepancy may affect presentation without changing modeled
volumes or flows. Keep it separate from #883's invalid-curve validation scope.

[#883](https://github.com/OpenWaterAnalytics/EPANET/issues/883) still had no comments.
CHT #10155 still had no response after Humanifest's inquiry. No repeat nudge was
sent. A #883 evidence/scope inquiry still needs preparation under the current
contribution and compute review rules; bot eligibility and maintainer acceptance
remain unconfirmed. This baseline does not advance the opportunity beyond research.

Sources accessed September 9, 2026: linked official Boost release/metadata and
GitHub discussions, plus the pinned target CMake/test sources described above.
