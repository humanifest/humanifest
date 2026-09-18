"""Catch drift between the public schema contract and the offline validator."""

import json
from pathlib import Path
import unittest

from humanifest.models import (
    COMPUTE_RESOURCE_TYPES, COMPUTE_STATUSES, FUNDING_ENTRY_STATUSES,
    FUNDING_ENTRY_TYPES,
    BUILDING_STATES, HARD_GATES, MAINTAINER_CONFIRMED_STATES, PIPELINE_STATES,
    REQUIRED_OPPORTUNITY_FIELDS, REQUIRED_PROJECT_FIELDS, SCORE_WEIGHTS,
)


class SchemaContractTests(unittest.TestCase):
    def test_required_fields_and_pipeline_match_runtime(self):
        root = Path(__file__).resolve().parents[1] / "schemas"
        for kind, fields in [("project", REQUIRED_PROJECT_FIELDS), ("opportunity", REQUIRED_OPPORTUNITY_FIELDS)]:
            schema = json.loads((root / f"{kind}.schema.json").read_text())
            self.assertEqual(set(schema["required"]), set(fields))
            self.assertTrue(set(fields).issubset(schema["properties"]))
        self.assertEqual(schema["properties"]["pipeline_state"]["enum"], PIPELINE_STATES)
        self.assertEqual(schema["properties"]["gates"]["required"], HARD_GATES)
        self.assertEqual(set(schema["properties"]["score_inputs"]["required"]), set(SCORE_WEIGHTS))
        for condition, states, gates in zip(
            schema["allOf"], [MAINTAINER_CONFIRMED_STATES, BUILDING_STATES],
            [["maintainer_interest_confirmed"], HARD_GATES], strict=True,
        ):
            self.assertEqual(condition["if"]["properties"]["pipeline_state"]["enum"], states)
            required = condition["then"]["properties"]["gates"]["properties"]
            self.assertEqual(set(required), set(gates))
            for gate in gates:
                self.assertIs(required[gate]["properties"]["passed"]["const"], True)

    def test_governance_schemas_match_runtime_enums(self):
        root = Path(__file__).resolve().parents[1] / "schemas"
        compute = json.loads((root / "compute-resources.schema.json").read_text())
        funding = json.loads((root / "funding-ledger.schema.json").read_text())
        resource = compute["$defs"]["resource"]["properties"]
        self.assertEqual(set(resource["resource_type"]["enum"]), COMPUTE_RESOURCE_TYPES)
        self.assertEqual(set(resource["status"]["enum"]), COMPUTE_STATUSES)
        entry = funding["$defs"]["entry"]["properties"]
        self.assertEqual(set(entry["type"]["enum"]), FUNDING_ENTRY_TYPES)
        self.assertEqual(set(entry["status"]["enum"]), FUNDING_ENTRY_STATUSES)
