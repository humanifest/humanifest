from copy import deepcopy
from datetime import date
import unittest

from humanifest.models import validate_opportunity
from humanifest.work import render_work_plan, work_plan
from tests.test_models import opportunity


class WorkTests(unittest.TestCase):
    def plan(self, *records):
        return work_plan(list(records), as_of=date(2026, 9, 8))

    def test_waiting_review_does_not_hide_independent_research_or_mutate_record(self):
        record = opportunity()
        record.update(pipeline_state="MAINTAINER-CHECK", next_external_status_check="2026-09-15",
                      research_next_step="Inspect remaining setup hooks before installing dependencies.")
        record["gates"]["maintainer_interest_confirmed"]["passed"] = False
        before = deepcopy(record)
        plan = self.plan(record)
        self.assertEqual(plan["independent_research"][0]["action"], record["research_next_step"])
        self.assertEqual(plan["waiting"][0]["review_on"], "2026-09-15")
        self.assertEqual(plan["due_reviews"], [])
        self.assertFalse(plan["refill_suggested"])
        self.assertEqual(record, before)

    def test_due_boundary_missing_dates_and_refill(self):
        records = []
        for identifier, day in [("later", "2026-09-09"), ("today", "2026-09-08"),
                                ("earlier", "2026-09-07"), ("unknown", None)]:
            record = opportunity()
            record.update(id=identifier, pipeline_state="PR-OPEN")
            if day:
                record["next_external_status_check"] = day
            records.append(record)
        plan = self.plan(*records)
        self.assertEqual([item["id"] for item in plan["due_reviews"]], ["earlier", "today"])
        self.assertEqual([item["id"] for item in plan["unscheduled_reviews"]], ["unknown"])
        self.assertTrue(plan["refill_suggested"])
        output = render_work_plan(plan)
        self.assertIn("find and verify another bounded opportunity", output)
        self.assertIn("missing dates do not mean poll on every run", output)

    def test_parked_work_is_excluded_but_explicit_post_merge_followup_remains(self):
        for state in ["PARKED", "DECLINED", "MERGED", "RELEASED"]:
            with self.subTest(state=state):
                record = opportunity()
                record.update(pipeline_state=state, next_external_status_check="2026-09-08",
                              research_next_step="An old research step")
                plan = self.plan(record)
                self.assertEqual(plan["independent_research"], [])
                self.assertEqual(len(plan["due_reviews"]), int(state in {"MERGED", "RELEASED"}))

    def test_active_work_prevents_empty_queue_hint(self):
        for state in ["ENVIRONMENT-READY", "REPRODUCED", "BUILDING", "ADVERSARIAL-REVIEW", "HUMAN-REVIEW"]:
            with self.subTest(state=state):
                record = opportunity()
                record["pipeline_state"] = state
                plan = self.plan(record)
                self.assertEqual(len(plan["active_work"]), 1)
                self.assertFalse(plan["refill_suggested"])
        self.assertTrue(self.plan()["refill_suggested"])

    def test_unplanned_candidates_remain_visible_before_queue_refill(self):
        for state in ["QUEUED", "PROJECT-AUDIT", "OPPORTUNITY-RESEARCH", "SHORTLISTED"]:
            with self.subTest(state=state):
                record = opportunity()
                record["pipeline_state"] = state
                record["gates"]["maintainer_interest_confirmed"]["passed"] = False
                before = deepcopy(record)
                plan = self.plan(record)
                self.assertEqual([item["id"] for item in plan["needs_research_plan"]], [record["id"]])
                self.assertEqual(plan["active_work"], [])
                self.assertEqual(plan["independent_research"], [])
                self.assertFalse(plan["refill_suggested"])
                self.assertIn(record["title"], render_work_plan(plan))
                self.assertIn("Candidates needing a research plan", render_work_plan(plan))
                self.assertEqual(record, before)

    def test_waiting_or_planned_research_is_not_an_unplanned_candidate(self):
        record = opportunity()
        record["pipeline_state"] = "OPPORTUNITY-RESEARCH"
        record["next_external_status_check"] = "2026-09-15"
        plan = self.plan(record)
        self.assertEqual(plan["needs_research_plan"], [])
        self.assertTrue(plan["refill_suggested"])
        record.pop("next_external_status_check")
        record["research_next_step"] = "Inspect the reported behavior."
        plan = self.plan(record)
        self.assertEqual(plan["needs_research_plan"], [])
        self.assertEqual(len(plan["independent_research"]), 1)

    def test_optional_work_fields_require_canonical_dates_and_nonblank_text(self):
        for field, values in {
            "next_external_status_check": [None, True, 20260908, "", "20260908", "2026-W37-2", "2026-02-30"],
            "research_next_step": [None, True, [], "", " \n"],
        }.items():
            for value in values:
                with self.subTest(field=field, value=value):
                    record = opportunity()
                    record[field] = value
                    self.assertTrue(any(field in issue.message for issue in validate_opportunity(record, "fixture")))
        record = opportunity()
        record.update(next_external_status_check="2028-02-29", research_next_step="Verify a source.")
        self.assertEqual(validate_opportunity(record, "fixture"), [])
