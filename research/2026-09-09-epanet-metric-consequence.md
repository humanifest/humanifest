# Metric water-storage diameter: bounded consequence check

September 9, 2026. Follows the [native baseline](2026-09-09-epanet-native-baseline.md).
**No meaningful hydraulic difference was observed in the tested networks.**
The valid-curve metric discrepancy is therefore not promoted as a consequential
simulation bug or a separate contribution opportunity.

The original, unchanged library at dev `83e25bbe2b0b460803e71df03bc989afe9557ea3`
was exercised through file loading, `EN_VOLCURVE` assignment and `EN_settankdata`.
Each route was run before and after saving/reloading an input file, separately
in GPM and LPS units: **12 four-hour native hydraulic simulations**. All API
calls returned zero and all measured values were finite.

The two synthetic networks contain a reservoir, junction, water-storage tank,
two pipes and changing hourly demands. Storage volume increases linearly from
0 to 1000 over depth 0 to 10. Each route within a unit system starts with the
same data. GPM and LPS examples are not physically equivalent networks.

| Measure | GPM example | LPS example |
| --- | --- | --- |
| Steps per run | 18 | 17 |
| Water-depth range | 5 to 10 | 5 to 5.485909692801769 |
| Reference nominal diameter | 11.283791670955125 | 11.283791670955125 |
| EN_VOLCURVE nominal diameter | 11.283791670955127 | 3.4392997013071227 |
| EN_VOLCURVE saved diameter | 11.2838 | 3.4393 |
| Diameter after reload | 11.283791670955125 | 11.283791670955125 |

Stored volume, current water depth, flow into storage and junction pressure were
compared at matching timestamps. GPM differences were zero. The largest LPS
absolute differences were 2.84e-14 in depth, 1.82e-12 in volume, 8.53e-14 in flow
and 5.33e-14 in pressure. They occur for both API assignment routes relative to
file loading and after round-trips, consistent with floating-point rounding.
Assertions use relative tolerance 1e-9 and absolute tolerance 1e-7. Each run
must exhibit changing water depth and reach 14,400 seconds; a static or empty
simulation would fail the fixture.

Source tracing explains why this result is plausible: `tankvolume` and
`tankgrade` interpolate the assigned volume curve, while the input writer emits
the diameter calculated from nominal area. File initialization recomputes the
nominal area/diameter from the curve. This supports the bounded finding; it is
not proof of equivalence for all networks, water-quality/mixing calculations or
other uses of nominal diameter.

## Reproduce

The [fixture](fixtures/epanet_metric_roundtrip_probe.py) imports the prior
public-API wrapper, verifies the pinned clean source, calls the original shared
library and uses temporary synthetic files. It downloads nothing and changes
no target source. All **144 tracked target files remain unchanged**.

```bash
python3 research/fixtures/epanet_metric_roundtrip_probe.py \
  --source /path/to/EPANET \
  --library /path/to/build-tests/lib/libepanet2.dylib \
  --output /path/to/results.json
```

Library SHA256 remains
`3b6ca9970af751fe3374070230c354804c76e1d7ad9fd71ca55d2fcd7c81fc2f`.
Local full time series and saved storage rows are recorded at
`/tmp/humanifest-epanet-native/metric-roundtrip-results.json`.

## Decision

Close this bounded metric-consequence investigation with a negative finding.
Do not claim improved water supply, detected operational failure or a newly
justified patch. Keep the original invalid-curve #883 inquiry narrow: its
34-case reproduction and 88-case unchanged baseline remain distinct evidence.
The [prepared inquiry](2026-09-09-epanet-scope-inquiry.md) is unsent and awaits the
human review required by current compute governance. No maintainer response
or acceptance is implied. Remove the completed independent-research step from
the opportunity so cause-led discovery can refill the queue while review waits.

Sources inspected September 9, 2026:

- [Pinned hydraulic volume/grade functions](https://github.com/OpenWaterAnalytics/EPANET/blob/83e25bbe2b0b460803e71df03bc989afe9557ea3/src/hydraul.c)
- [Pinned input writer](https://github.com/OpenWaterAnalytics/EPANET/blob/83e25bbe2b0b460803e71df03bc989afe9557ea3/src/inpfile.c)
- [Pinned input initialization](https://github.com/OpenWaterAnalytics/EPANET/blob/83e25bbe2b0b460803e71df03bc989afe9557ea3/src/input1.c)
