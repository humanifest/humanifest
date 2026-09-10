"""Catch drift between the public schema contract and the offline validator."""

import json
from pathlib import Path
import unittest

from humanifest.models import (
    BUILDING_STATES, CAUSE_SCORE_WEIGHTS, CAUSE_STATUSES, HARD_GATES,
    MAINTAINER_CONFIRMED_STATES, PIPELINE_STATES, REQUIRED_CAUSE_FIELDS,
    REQUIRED_OPPORTUNITY_FIELDS, REQUIRED_PROJECT_FIELDS, SCORE_WEIGHTS,
)


class SchemaContractTests(unittest.TestCase):
    def test_required_fields_and_pipeline_match_runtime(self):
        root = Path(__file__).resolve().parents[1] / "schemas"
        for kind, fields in [
            ("cause", REQUIRED_CAUSE_FIELDS),
            ("project", REQUIRED_PROJECT_FIELDS),
            ("opportunity", REQUIRED_OPPORTUNITY_FIELDS),
        ]:
            schema = json.loads((root / f"{kind}.schema.json").read_text())
            self.assertEqual(set(schema["required"]), set(fields))
            self.assertTrue(set(fields).issubset(schema["properties"]))
        cause_schema = json.loads((root / "cause.schema.json").read_text())
        opportunity_schema = json.loads((root / "opportunity.schema.json").read_text())
        self.assertEqual(cause_schema["properties"]["status"]["enum"], CAUSE_STATUSES)
        self.assertEqual(set(cause_schema["properties"]["score_inputs"]["required"]), set(CAUSE_SCORE_WEIGHTS))
        self.assertEqual(opportunity_schema["properties"]["pipeline_state"]["enum"], PIPELINE_STATES)
        self.assertEqual(opportunity_schema["properties"]["gates"]["required"], HARD_GATES)
        self.assertEqual(set(opportunity_schema["properties"]["score_inputs"]["required"]), set(SCORE_WEIGHTS))
        for condition, states, gates in zip(
            opportunity_schema["allOf"], [MAINTAINER_CONFIRMED_STATES, BUILDING_STATES],
            [["maintainer_interest_confirmed"], HARD_GATES], strict=True,
        ):
            self.assertEqual(condition["if"]["properties"]["pipeline_state"]["enum"], states)
            required = condition["then"]["properties"]["gates"]["properties"]
            self.assertEqual(set(required), set(gates))
            for gate in gates:
                self.assertIs(required[gate]["properties"]["passed"]["const"], True)
