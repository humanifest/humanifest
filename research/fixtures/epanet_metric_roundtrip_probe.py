"""Compare valid EPANET water-storage curves across API/file routes and reloads.

Uses the pinned original native library and the earlier public-API harness.
No downloads, target modifications or operational-system access.
"""
import argparse
import ctypes as c
import hashlib
import json
import math
from pathlib import Path
import tempfile

from epanet_tank_curve_probe import API, PIN, source_hashes, with_project


def network(units, assigned):
    diameter, length = (4, 1000) if units == 'GPM' else (100, 300)
    return f'''[TITLE]
Synthetic water-storage model for fixed-unit route comparisons
[JUNCTIONS]
J 90 2 P
[RESERVOIRS]
R 110
[TANKS]
T 100 5 0 10 5 0 {'V' if assigned else ''}
[PIPES]
P1 R J {length} {diameter} 100 0 Open
P2 J T {length} {diameter} 100 0 Open
[PATTERNS]
P 1 2 0.5 1.5
[CURVES]
V 0 0
V 3 300
V 6 600
V 10 1000
[OPTIONS]
UNITS {units}
HEADLOSS H-W
[TIMES]
DURATION 4:00
HYDRAULIC TIMESTEP 0:15
PATTERN TIMESTEP 1:00
[END]
'''


def value(api, ph, kind, index, prop):
    result = c.c_double()
    code = api.call(f'EN_get{kind}value', ph, index, api.enums[prop], c.byref(result))
    assert code == 0 and math.isfinite(result.value), (kind, prop, code, result.value)
    return result.value


def simulate(api, ph):
    tank, junction = api.index(ph, 'node', 'T'), api.index(ph, 'node', 'J')
    pipe = api.index(ph, 'link', 'P2')
    assert api.call('EN_openH', ph) == 0
    rows = []
    try:
        assert api.call('EN_initH', ph, 0) == 0
        while True:
            now, step = c.c_long(), c.c_long()
            assert api.call('EN_runH', ph, c.byref(now)) == 0
            rows.append({'seconds': now.value,
                         'level': value(api, ph, 'node', tank, 'EN_HEAD') - value(api, ph, 'node', tank, 'EN_ELEVATION'),
                         'volume': value(api, ph, 'node', tank, 'EN_TANKVOLUME'),
                         'flow_to_storage': value(api, ph, 'link', pipe, 'EN_FLOW'),
                         'junction_pressure': value(api, ph, 'node', junction, 'EN_PRESSURE')})
            assert api.call('EN_nextH', ph, c.byref(step)) == 0
            if step.value == 0:
                break
            assert len(rows) < 1000
    finally:
        assert api.call('EN_closeH', ph) == 0
    assert rows[0]['seconds'] == 0 and rows[-1]['seconds'] == 14400
    assert len(rows) >= 17
    assert max(r['level'] for r in rows) - min(r['level'] for r in rows) > 0.01
    return rows


def compare(left, right):
    assert len(left) == len(right)
    assert [r['seconds'] for r in left] == [r['seconds'] for r in right]
    differences = {}
    for prop in ['level', 'volume', 'flow_to_storage', 'junction_pressure']:
        differences[prop] = max(abs(a[prop] - b[prop]) for a, b in zip(left, right))
        assert all(math.isclose(a[prop], b[prop], rel_tol=1e-9, abs_tol=1e-7) for a, b in zip(left, right)), (prop, differences[prop])
    return differences


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--library', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    before = source_hashes(args.source)
    api = API(args.library, args.source)
    signatures = {'EN_getlinkindex': [c.c_void_p, c.c_char_p, c.POINTER(c.c_int)],
                  'EN_getlinkvalue': [c.c_void_p, c.c_int, c.c_int, c.POINTER(c.c_double)],
                  'EN_runH': [c.c_void_p, c.POINTER(c.c_long)],
                  'EN_nextH': [c.c_void_p, c.POINTER(c.c_long)],
                  'EN_saveinpfile': [c.c_void_p, c.c_char_p]}
    for name, signature in signatures.items():
        f = getattr(api.lib, name)
        f.argtypes, f.restype = signature, c.c_int
    results = []
    with tempfile.TemporaryDirectory(prefix='humanifest-water-storage-') as tmp:
        directory = Path(tmp)
        for units in ['GPM', 'LPS']:
            for route in ['file', 'volume_assignment', 'tankdata_assignment']:
                name = f'{units}-{route}'
                saved = directory / f'{name}-saved.inp'
                def body(ph):
                    tank = api.index(ph, 'node', 'T')
                    if route == 'volume_assignment':
                        curve = api.index(ph, 'curve', 'V')
                        assert api.call('EN_setnodevalue', ph, tank, api.enums['EN_VOLCURVE'], curve) == 0
                    elif route == 'tankdata_assignment':
                        assert api.call('EN_settankdata', ph, tank, 100, 5, 0, 10, 5, 0, b'V') == 0
                    initial = api.snapshot(ph, tank)
                    assert api.call('EN_saveinpfile', ph, str(saved).encode()) == 0
                    return {'initial': initial, 'series': simulate(api, ph)}
                original = with_project(api, directory, name, network(units, route == 'file'), body)
                def reopened(ph):
                    return {'initial': api.snapshot(ph, api.index(ph, 'node', 'T')), 'series': simulate(api, ph)}
                restored = with_project(api, directory, name + '-reloaded', saved.read_text(), reopened)
                storage_section = saved.read_text().split('[TANKS]')[1].split('[')[0]
                storage_line = next(line for line in storage_section.splitlines() if line.split() and line.split()[0] == 'T')
                results.append({'units': units, 'route': route, 'original': original, 'reloaded': restored,
                                'saved_storage_row': storage_line.strip(),
                                'roundtrip_max_absolute_differences': compare(original['series'], restored['series'])})
    comparisons = []
    for units in ['GPM', 'LPS']:
        selected = [r for r in results if r['units'] == units]
        reference = selected[0]
        for row in selected[1:]:
            comparisons.append({'units': units, 'route': row['route'],
                                'max_absolute_differences_from_file': compare(reference['original']['series'], row['original']['series'])})
        for row in selected:
            ratio = row['original']['initial']['EN_TANKDIAM'] / reference['original']['initial']['EN_TANKDIAM']
            assert math.isclose(ratio, 0.3048 if units == 'LPS' and row['route'] == 'volume_assignment' else 1, rel_tol=1e-10)
            assert math.isclose(row['reloaded']['initial']['EN_TANKDIAM'], reference['original']['initial']['EN_TANKDIAM'], rel_tol=1e-10)
    assert source_hashes(args.source) == before
    output = {'revision': PIN, 'library_sha256': hashlib.sha256(args.library.read_bytes()).hexdigest(),
              'unchanged_tracked_files': len(before), 'simulation_runs': 12,
              'duration_seconds_per_run': 14400, 'results': results, 'comparisons': comparisons,
              'limits': 'Two synthetic networks, hydraulic results only. No claim of equivalence for all inputs, quality/mixing, every use of nominal diameter or real utility operations. Unit systems are separate numeric examples, not equivalent physical networks.'}
    args.output.write_text(json.dumps(output, indent=2, allow_nan=False) + '\n')
    print('12 four-hour native simulations pass; save/reload and route comparisons agree within stated tolerance.')
    print(json.dumps(comparisons))


if __name__ == '__main__':
    main()
