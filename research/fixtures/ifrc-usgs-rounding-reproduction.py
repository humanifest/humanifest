"""Exercise inspected USGS aggregation and caller arithmetic without target imports.

Usage: python3 research/fixtures/ifrc-usgs-rounding-reproduction.py /path/usgs.py
The comparison preserves the existing midpoint formula; it is not a loss model.
"""

import ast
import hashlib
import json
import sys
import typing
from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace


def main(path):
    source = path.read_bytes()
    assert hashlib.sha256(source).hexdigest() == (
        "e30b4bf9ecfe2eef9ccfe9c9da86af5e1dc0e660d5b6867f5b2df188e628a680"
    ), "Expected pystac-monty revision 7dd2d48cd599c3e0b894f1676b5de88c19028c46"
    tree = ast.parse(source)
    function = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)
                    and n.name == "_calculate_value_from_bins")
    namespace = {"typing": typing, "AlertBin": SimpleNamespace}
    exec(compile(ast.Module(body=[function], type_ignores=[]), "pinned-helper", "exec"), namespace)
    aggregate = namespace["_calculate_value_from_bins"]
    scale = next(ast.literal_eval(n.value) for n in ast.walk(tree)
                 if isinstance(n, ast.Assign) and any(
                     isinstance(t, ast.Name) and t.id == "PAGER_ALERT_ECONOMIC_UNIT_SCALE"
                     for t in n.targets))
    expressions = [n for n in ast.walk(tree) if isinstance(n, ast.BinOp)
                   and isinstance(n.op, ast.Mult)
                   and isinstance(n.right, ast.Attribute)
                   and n.right.attr == "PAGER_ALERT_ECONOMIC_UNIT_SCALE"]
    assert len(expressions) == 1
    expression = compile(ast.Expression(expressions[0]), "pinned-economic-caller", "eval")
    transformer = SimpleNamespace(
        PAGER_ALERT_ECONOMIC_UNIT_SCALE=scale,
        _calculate_value_from_bins=lambda bins: aggregate(None, bins),
    )
    results = []
    cases = {
        "submillion": [(0, 1, 1)],
        "fractional_millions": [(1, 10, 1)],
        "exact_integer_control": [(0, 2, 1)],
        "empty_control": [],
    }
    # Original public payload retrieved during the September 8 source audit.
    # This is one input to the existing midpoint formula, not ground-truth loss.
    payload = Path(__file__).with_name("usgs-us6000t7zp-alerts.json").read_bytes()
    assert hashlib.sha256(payload).hexdigest() == (
        "4058bea104960004b80cde32d21e3465d5bde9104fcd097eb5fe92d475177b68"
    ), "Expected archived USGS payload"
    cases["archived_public_payload"] = [
        (item["min"], item["max"], item["probability"])
        for item in json.loads(payload)["economic"]["bins"]
    ]
    for name, values in cases.items():
        bins = [SimpleNamespace(min=lo, max=hi, probability=p) for lo, hi, p in values]
        actual = eval(expression, {}, {
            "self": transformer,
            "alert_data": SimpleNamespace(economic=SimpleNamespace(bins=bins)),
        })
        unrounded = sum(((Decimal(str(lo)) + Decimal(str(hi))) / 2 * Decimal(str(p))
                         for lo, hi, p in values), Decimal(0))
        comparison = int(unrounded * scale)
        if name in {"submillion", "fractional_millions"}:
            assert comparison - actual == 500_000
        elif name == "archived_public_payload":
            assert actual == 1_768_846_000_000
            assert comparison == 1_768_846_489_394
        else:
            assert actual == comparison
        results.append({"case": name, "current_usd": actual,
                        "same_formula_scaled_before_rounding_usd": comparison})
    print(json.dumps({
        "revision": "7dd2d48cd599c3e0b894f1676b5de88c19028c46",
        "scope": "Original helper and economic caller; synthetic bins plus one archived public payload, not ground-truth losses",
        "cases": results,
    }, indent=2))


if __name__ == "__main__":
    main(Path(sys.argv[1]))
