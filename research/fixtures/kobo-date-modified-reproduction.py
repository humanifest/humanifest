"""Probe inspected PR expressions without importing Kobo or starting databases.

Pass a directory containing the three pinned source files named as below.
This verifies formatting and fallback behavior, not a live Mongo/API sync.
"""

import ast
import hashlib
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace


def load_source(root, name, expected_hash):
    source = (root / name).read_bytes()
    if hashlib.sha256(source).hexdigest() != expected_hash:
        raise ValueError(f"Unexpected source revision: {name}")
    return ast.parse(source)


def main(root):
    tags = load_source(
        root, "kobo__apps__openrosa__libs__utils__common_tags.py",
        "d634ba35391839f65e3281ae5ab35f7a6f3220353191d7ae8e8598b7323cb625",
    )
    parsed = load_source(
        root, "kobo__apps__openrosa__apps__viewer__models__parsed_instance.py",
        "75bb8cafd491a456bf543868aaf97046801602e67ab9936e907773b1dd60fcd6",
    )
    backend = load_source(
        root, "kpi__deployment_backends__base_backend.py",
        "41b1054fe6ff49cdd7badc33e859aac5fe273aec68167a20a16592b92173cf2a",
    )
    constants = {
        node.targets[0].id: ast.literal_eval(node.value)
        for node in tags.body
        if isinstance(node, ast.Assign)
        and isinstance(node.targets[0], ast.Name)
        and node.targets[0].id in {"MONGO_STRFTIME", "DATE_MODIFIED", "SUBMISSION_TIME"}
    }
    method = next(n for n in ast.walk(parsed)
                  if isinstance(n, ast.FunctionDef) and n.name == "to_dict_for_mongo")
    expressions = [value for n in ast.walk(method) if isinstance(n, ast.Dict)
                   for key, value in zip(n.keys, n.values)
                   if isinstance(key, ast.Name) and key.id == "DATE_MODIFIED"]
    assert len(expressions) == 1
    formatter = compile(ast.Expression(expressions[0]), "pinned-formatter", "eval")

    def wire_time(value):
        # datetime.strftime may lazily import the standard-library time module.
        return eval(formatter, {"__builtins__": {"__import__": __import__}}, {
            **constants, "self": SimpleNamespace(
                instance=SimpleNamespace(date_modified=value)),
        })

    first = datetime(2026, 9, 8, 12, 0, 0, 100000, tzinfo=timezone.utc)
    second = first + timedelta(microseconds=800000)
    later = first + timedelta(seconds=1)
    before, after, later_wire = map(wire_time, (first, second, later))
    assert second > first
    assert before == after
    assert not after > before
    assert later_wire > before

    # Execute only the inspected fallback method with its literal constants.
    fallback = next(n for n in ast.walk(backend)
                    if isinstance(n, ast.FunctionDef) and n.name == "_inject_date_modified")
    namespace = {"__builtins__": {"dict": dict}, **constants}
    exec(compile(ast.Module(body=[fallback], type_ignores=[]), "pinned-fallback", "exec"), namespace)
    inject = namespace["_inject_date_modified"]
    existing = {"_submission_time": before, "_date_modified": later_wire}
    legacy = {"_submission_time": before}
    assert inject(None, existing.copy()) == existing
    assert inject(None, legacy.copy())["_date_modified"] == before
    assert "_date_modified" not in legacy  # Only the supplied copy was changed.
    assert inject(None, {}) == {}
    print(json.dumps({
        "revision": "7968471a4d86ab701f61537499ee080144b2bf3e",
        "scope": "Original formatter expression and fallback; no database/API execution",
        "input_timestamps": [first.isoformat(), second.isoformat()],
        "wire_times": [before, after],
        "strict_greater_than_matches_second": after > before,
        "later_second_control_matches": later_wire > before,
        "fallback_checks": "existing value preserved; legacy creation time injected; missing stays missing",
    }, indent=2))


if __name__ == "__main__":
    main(Path(sys.argv[1]))
