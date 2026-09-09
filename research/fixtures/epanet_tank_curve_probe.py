"""Measure pinned, unmodified EPANET tank curves through its real public C API.

Build the audited target separately; this runner downloads/installs nothing and
does not model EPANET behavior in Python. Requires a native shared library built
from PIN. Synthetic networks and reports stay in a temporary directory.
"""

import argparse
import ctypes as c
import hashlib
import json
import math
from pathlib import Path
import platform
import re
import subprocess
import tempfile


PIN = "83e25bbe2b0b460803e71df03bc989afe9557ea3"
X = [0.0, 3.0, 6.0, 10.0]
SHAPES = {
    "increasing": [0.0, 30.0, 60.0, 100.0],
    "decreasing": [100.0, 70.0, 40.0, 0.0],
    "interior_dip": [0.0, 60.0, 30.0, 100.0],
}
ROUTES = ["file", "volume_assignment", "tankdata_assignment", "bulk_edit", "point_edit"]


def source_hashes(root):
    def git(*args):
        return subprocess.check_output(["git", "-C", str(root), *args])
    assert git("rev-parse", "HEAD").decode().strip() == PIN
    git("diff", "--exit-code", "HEAD", "--")
    paths = git("ls-files", "-z").decode().rstrip("\0").split("\0")
    return {p: hashlib.sha256((root / p).read_bytes()).hexdigest() for p in paths}


def clean_number(value):
    if math.isnan(value):
        return "NaN"
    if math.isinf(value):
        return "Infinity" if value > 0 else "-Infinity"
    return value


class API:
    def __init__(self, library, source):
        self.lib = c.CDLL(str(library.resolve()))
        text = (source / "include/epanet2_enums.h").read_text()
        self.enums = {k: int(v) for k, v in re.findall(r"\b(EN_\w+)\s*=\s*(\d+)", text)}
        p, i, d, s = c.c_void_p, c.c_int, c.c_double, c.c_char_p
        signatures = {
            "EN_createproject": [c.POINTER(p)], "EN_deleteproject": [p],
            "EN_open": [p, s, s, s], "EN_close": [p],
            "EN_getnodeindex": [p, s, c.POINTER(i)],
            "EN_getcurveindex": [p, s, c.POINTER(i)],
            "EN_getnodevalue": [p, i, i, c.POINTER(d)],
            "EN_setnodevalue": [p, i, i, d],
            "EN_settankdata": [p, i, d, d, d, d, d, d, s],
            "EN_setcurve": [p, i, c.POINTER(d), c.POINTER(d), i],
            "EN_setcurvevalue": [p, i, i, d, d],
            "EN_getcurvetype": [p, i, c.POINTER(i)],
            "EN_openH": [p], "EN_initH": [p, i], "EN_closeH": [p],
        }
        for name, args in signatures.items():
            f = getattr(self.lib, name)
            f.argtypes, f.restype = args, i

    def call(self, name, *args):
        return getattr(self.lib, name)(*args)

    def index(self, ph, kind, name):
        result = c.c_int()
        code = self.call(f"EN_get{kind}index", ph, name.encode(), c.byref(result))
        assert code == 0, (kind, name, code)
        return result.value

    def snapshot(self, ph, tank):
        result = {}
        for name in ["EN_TANKDIAM", "EN_TANKLEVEL", "EN_INITVOLUME", "EN_MINVOLUME", "EN_MAXVOLUME", "EN_VOLCURVE"]:
            value = c.c_double()
            code = self.call("EN_getnodevalue", ph, tank, self.enums[name], c.byref(value))
            assert code == 0, (name, code)
            result[name] = clean_number(value.value)
        return result


def tank_network(units, shape, assigned=True):
    curve = "V" if assigned else ""
    values = "\n".join(f"V {x} {y}" for x, y in zip(X, SHAPES[shape]))
    return f"""[TITLE]
Synthetic tank validation probe; not a utility network
[JUNCTIONS]
J 90 1
[RESERVOIRS]
R 120
[TANKS]
T 100 5 0 10 5 0 {curve}
[PIPES]
P1 R J 100 100 100 0 Open
P2 J T 100 100 100 0 Open
[CURVES]
{values}
[OPTIONS]
UNITS {units}
HEADLOSS H-W
[TIMES]
DURATION 0
[END]
"""


def with_project(api, directory, name, network, body):
    inp, report = directory / f"{name}.inp", directory / f"{name}.rpt"
    inp.write_text(network)
    ph = c.c_void_p()
    assert api.call("EN_createproject", c.byref(ph)) == 0
    try:
        opened = api.call("EN_open", ph, str(inp).encode(), str(report).encode(), b"")
        assert opened == 0, (name, "EN_open", opened, report.read_text())
        return {"case": name, "open_code": opened, **body(ph)}
    finally:
        api.call("EN_close", ph)
        api.call("EN_deleteproject", ph)


def hydraulic_initialization(api, ph):
    opened = api.call("EN_openH", ph)
    initialized = None
    if opened == 0:
        try:
            initialized = api.call("EN_initH", ph, 0)
        finally:
            api.call("EN_closeH", ph)
    return {"open_hydraulics_code": opened, "initialize_hydraulics_code": initialized}


def tank_case(api, directory, units, shape, route):
    editing = route in {"bulk_edit", "point_edit"}
    assigned = route not in {"volume_assignment", "tankdata_assignment"}
    network = tank_network(units, "increasing" if editing else shape, assigned)
    def body(ph):
        tank, curve = api.index(ph, "node", "T"), api.index(ph, "curve", "V")
        before = api.snapshot(ph, tank)
        codes = []
        if route == "volume_assignment":
            codes.append(api.call("EN_setnodevalue", ph, tank, api.enums["EN_VOLCURVE"], curve))
        elif route == "tankdata_assignment":
            codes.append(api.call("EN_settankdata", ph, tank, 100, 5, 0, 10, 5, 0, b"V"))
        elif route == "bulk_edit":
            codes.append(api.call("EN_setcurve", ph, curve, (c.c_double * 4)(*X),
                                  (c.c_double * 4)(*SHAPES[shape]), 4))
        elif route == "point_edit":
            for point, (x, y) in enumerate(zip(X, SHAPES[shape]), 1):
                codes.append(api.call("EN_setcurvevalue", ph, curve, point, x, y))
        assert all(code == 0 for code in codes), (route, shape, codes)
        after = api.snapshot(ph, tank)
        levels = []
        for level in [3.0, 6.0]:
            code = api.call("EN_setnodevalue", ph, tank, api.enums["EN_TANKLEVEL"], level)
            assert code == 0, (route, shape, level, code)
            levels.append({"requested_level": level, "setter_code": code, **api.snapshot(ph, tank)})
        for actual, expected in zip(levels, SHAPES[shape][1:3]):
            assert math.isclose(actual["EN_INITVOLUME"], expected, rel_tol=1e-10, abs_tol=1e-10)
        diameter = after["EN_TANKDIAM"]
        # These assertions describe current behavior, not an accepted fixed contract.
        if shape == "decreasing" and not editing:
            assert diameter == "NaN", (route, units, diameter)
        else:
            assert isinstance(diameter, float) and diameter > 0
        hydraulics = hydraulic_initialization(api, ph)
        assert hydraulics == {"open_hydraulics_code": 0, "initialize_hydraulics_code": 0}
        return {"units": units, "shape": shape, "route": route,
                "mutation_codes": codes, "before": before, "after": after,
                "level_probes": levels, **hydraulics}
    return with_project(api, directory, f"{units}-{shape}-{route}", network, body)


def cylinder_case(api, directory, units):
    def body(ph):
        tank = api.index(ph, "node", "T")
        before = api.snapshot(ph, tank)
        code = api.call("EN_settankdata", ph, tank, 100, 5, 0, 10, 5, 0, b"")
        assert code == 0
        after = api.snapshot(ph, tank)
        for prop in ["EN_TANKDIAM", "EN_INITVOLUME", "EN_MINVOLUME", "EN_MAXVOLUME"]:
            assert math.isclose(before[prop], after[prop], rel_tol=1e-10, abs_tol=1e-10)
        assert after["EN_MINVOLUME"] < after["EN_INITVOLUME"] < after["EN_MAXVOLUME"]
        return {"units": units, "before": before, "after": after, **hydraulic_initialization(api, ph)}
    return with_project(api, directory, f"{units}-cylinder", tank_network(units, "increasing", False), body)


def pump_case(api, directory, units):
    network = f"""[JUNCTIONS]
J 90 1
[RESERVOIRS]
R 100
[PUMPS]
P R J HEAD C
[CURVES]
C 0 100
C 10 90
C 20 60
C 30 0
[OPTIONS]
UNITS {units}
HEADLOSS H-W
[TIMES]
DURATION 0
[END]
"""
    def body(ph):
        curve = api.index(ph, "curve", "C")
        result = hydraulic_initialization(api, ph)
        assert result == {"open_hydraulics_code": 0, "initialize_hydraulics_code": 0}
        kind = c.c_int()
        assert api.call("EN_getcurvetype", ph, curve, c.byref(kind)) == 0
        assert kind.value == api.enums["EN_PUMP_CURVE"]
        return {"units": units, "curve_type": kind.value, **result}
    return with_project(api, directory, f"{units}-decreasing-pump", network, body)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--library", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    before = source_hashes(args.source)
    api = API(args.library, args.source)
    results = []
    with tempfile.TemporaryDirectory(prefix="humanifest-epanet-probe-") as temp:
        directory = Path(temp)
        for units in ["GPM", "LPS"]:
            for shape in SHAPES:
                for route in ROUTES:
                    results.append(tank_case(api, directory, units, shape, route))
            results.append(cylinder_case(api, directory, units))
            results.append(pump_case(api, directory, units))
    by_case = {row["case"]: row for row in results}
    for shape in ["increasing", "interior_dip"]:
        file_diameter = by_case[f"LPS-{shape}-file"]["after"]["EN_TANKDIAM"]
        assigned_diameter = by_case[f"LPS-{shape}-volume_assignment"]["after"]["EN_TANKDIAM"]
        tankdata_diameter = by_case[f"LPS-{shape}-tankdata_assignment"]["after"]["EN_TANKDIAM"]
        # Record the observed unit discrepancy; this is not desired behavior.
        assert math.isclose(assigned_diameter / file_diameter, 0.3048, rel_tol=1e-10)
        assert math.isclose(tankdata_diameter, file_diameter, rel_tol=1e-10)
    assert source_hashes(args.source) == before
    output = {"revision": PIN, "platform": platform.platform(),
              "python": platform.python_version(),
              "library_sha256": hashlib.sha256(args.library.read_bytes()).hexdigest(),
              "tracked_source_files_unchanged": len(before),
              "cases_passed": len(results), "results": results,
              "limits": "Public API, parser and hydraulic initialization only; no EN_runH/time-series simulation, Boost test suite, operational data or impact estimate. GPM/LPS cases use the same numeric inputs in their respective units, not equivalent physical networks."}
    args.output.write_text(json.dumps(output, indent=2, allow_nan=False) + "\n")
    print(f"{len(results)} native-library cases passed; {len(before)} tracked source files unchanged.")


if __name__ == "__main__":
    main()
