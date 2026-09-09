"""Validate public schemas, audited records, and negative gate fixtures.

Run from the checkout with: python -m scripts.check_schemas
Requires the development dependencies in requirements-checks.txt.
"""

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

from humanifest.models import BUILDING_STATES, HARD_GATES, MAINTAINER_CONFIRMED_STATES
from tests.test_models import opportunity


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    record_count = 0
    for kind, collection in [("project", "projects"), ("opportunity", "opportunities")]:
        schema = json.loads((root / "schemas" / f"{kind}.schema.json").read_text())
        Draft202012Validator.check_schema(schema)
        validator = Draft202012Validator(schema, format_checker=FormatChecker())
        directory = root / "portfolio" / collection
        if not directory.is_dir():
            raise AssertionError(f"Required record directory is missing: {directory}")
        for path in sorted(directory.glob("*.json")):
            errors = list(validator.iter_errors(json.loads(path.read_text())))
            if errors:
                raise AssertionError(f"{path}: {errors[0].message}")
            record_count += 1
        if kind == "opportunity":
            check_opportunity_rules(validator)
    print(f"Both public schemas and {record_count} audited records pass; invalid gate and source fixtures are rejected.")


def check_opportunity_rules(validator: Draft202012Validator) -> None:
    validator.validate(opportunity())
    for field, values in {
        "next_external_status_check": [None, True, 20260908, "", "20260908", "2026-W37-2", "2026-02-30"],
        "research_next_step": [None, True, [], "", " \n"],
    }.items():
        for value in values:
            record = opportunity()
            record[field] = value
            reject(validator, record, f"{field}={value!r}")
    record = opportunity()
    record.update(next_external_status_check="2028-02-29", research_next_step="Verify a source.")
    validator.validate(record)
    for state in BUILDING_STATES:
        for gate in HARD_GATES:
            record = opportunity()
            record["pipeline_state"] = state
            validator.validate(record)
            record["gates"][gate]["passed"] = False
            reject(validator, record, f"{state} with failed {gate}")
    for state in MAINTAINER_CONFIRMED_STATES:
        record = opportunity()
        record["pipeline_state"] = state
        record["gates"]["maintainer_interest_confirmed"]["passed"] = False
        reject(validator, record, f"{state} without confirmation")
    for state in ["PARKED", "DECLINED", "MAINTAINER-CHECK"]:
        record = opportunity()
        record["pipeline_state"] = state
        record["gates"]["maintainer_interest_confirmed"]["passed"] = False
        validator.validate(record)
    for field, value in [("passed", 1), ("passed", "true"), ("rationale", " ")]:
        record = opportunity()
        record["gates"][HARD_GATES[0]][field] = value
        reject(validator, record, f"gate {field}={value!r}")
    for value in [True, -1, 6, "3"]:
        record = opportunity()
        record["score_inputs"]["humanitarian_benefit"] = value
        reject(validator, record, f"score={value!r}")
    for field, value in [("accessed", "2026-02-30"), ("url", "relative/path")]:
        record = opportunity()
        record["sources"][0][field] = value
        reject(validator, record, f"source {field}={value!r}")
    for references in [None, [], ["s1", "s1"], [" "], [1], "s1"]:
        record = opportunity()
        gate = record["gates"]["maintainer_interest_confirmed"]
        if references is None:
            del gate["source_ids"]
        else:
            gate["source_ids"] = references
        reject(validator, record, f"confirmation source_ids={references!r}")
    record = opportunity()
    record["gates"]["maintainer_interest_confirmed"]["passed"] = False
    del record["gates"]["maintainer_interest_confirmed"]["source_ids"]
    validator.validate(record)


def reject(validator: Draft202012Validator, record: dict, label: str) -> None:
    if validator.is_valid(record):
        raise AssertionError(f"Public schema accepted invalid fixture: {label}")


if __name__ == "__main__":
    main()
