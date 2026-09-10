import unittest

from humanifest.models import (
    BUILDING_STATES,
    cause_report,
    HARD_GATES,
    MAINTAINER_CONFIRMED_STATES,
    failed_gates,
    generate_candidate_brief,
    generate_handoff,
    next_action,
    PIPELINE_STATES,
    portfolio_report,
    score_cause,
    score_opportunity,
    validate_cause,
    validate_opportunity,
)


def opportunity():
    gates = {
        gate: {"passed": True, "rationale": "supported by fixture"}
        for gate in [
            "humanitarian_relevance_supported",
            "repository_active",
            "external_contributions_accepted",
            "contribution_policy_understood",
            "ai_policy_understood",
            "problem_current_and_consequential",
            "behavior_reproducible_or_verifiable",
            "code_and_tests_located",
            "change_bounded",
            "regression_strategy_credible",
            "no_private_data_required",
            "security_and_licensing_risk_acceptable",
            "environment_feasible",
            "maintainer_interest_confirmed",
            "probable_reviewer_identified",
            "benefit_justifies_review_cost",
            "user_can_explain_line_by_line",
        ]
    }
    gates["maintainer_interest_confirmed"]["source_ids"] = ["s1"]
    return {
        "id": "sample",
        "project_id": "sample-project",
        "title": "Sample opportunity",
        "pipeline_state": "SHORTLISTED",
        "problem": "A real problem",
        "humanitarian_relevance": "Relevant",
        "evidence": [{"type": "measured", "claim": "Observed", "source_id": "s1"}],
        "code_surface": "one module",
        "proposed_change": "small patch",
        "tests": "unit test",
        "environment": "local",
        "maintainer": "named reviewer",
        "risks": "low",
        "gates": gates,
        "score_inputs": {
            "humanitarian_benefit": 4,
            "acceptance_probability": 3,
            "technical_confidence": 4,
            "review_burden": 1,
            "deployment_probability": 3,
        },
        "sources": [{"id": "s1", "url": "https://example.test", "accessed": "2026-09-06"}],
    }


def cause():
    return {
        "id": "sample-cause",
        "name": "Sample cause",
        "status": "PROJECT-SEEDING",
        "decision_mode": "global-impact",
        "summary": "A cause area worth investigating",
        "metrics": [{"type": "modeled", "claim": "Large burden", "source_id": "s1"}],
        "software_pathways": [{"type": "inferred", "claim": "Software can help", "source_id": "s1"}],
        "score_inputs": {
            "global_burden": 5,
            "neglectedness": 4,
            "tractability": 3,
            "software_leverage": 4,
            "maintainer_pathway": 2,
            "uncertainty_penalty": 1,
        },
        "sources": [{"id": "s1", "url": "https://example.test", "accessed": "2026-09-10"}],
    }
class ModelTests(unittest.TestCase):
    def test_cause_records_score_discovery_attention(self):
        record = cause()
        self.assertEqual(validate_cause(record, "sample"), [])
        score = score_cause(record)
        self.assertTrue(score["eligible_for_project_seeding"])
        self.assertEqual(score["decision_mode"], "global-impact")
        self.assertEqual(score["raw_score"], 3.7)
        self.assertIn("sample-cause", cause_report([record]))

    def test_cause_records_validate_sources_and_scores(self):
        record = cause()
        record["metrics"][0]["source_id"] = "missing"
        self.assertTrue(validate_cause(record, "sample"))
        record = cause()
        record["score_inputs"]["global_burden"] = 6
        self.assertTrue(validate_cause(record, "sample"))

    def test_passing_maintainer_gate_requires_traceable_evidence(self):
        for references in [None, [], ["missing"], ["s1", "s1"], [None], [["s1"]], "s1", [" "]]:
            with self.subTest(references=references):
                record = opportunity()
                gate = record["gates"]["maintainer_interest_confirmed"]
                if references is None:
                    del gate["source_ids"]
                else:
                    gate["source_ids"] = references
                self.assertTrue(validate_opportunity(record, "sample"))
                self.assertFalse(score_opportunity(record)["eligible_for_building"])
                self.assertIn("maintainer_interest_confirmed", [item["gate"] for item in failed_gates(record)])

    def test_optional_gate_evidence_must_resolve_even_for_failed_gates(self):
        record = opportunity()
        gate = record["gates"]["repository_active"]
        gate["source_ids"] = ["s1"]
        self.assertEqual(validate_opportunity(record, "sample"), [])
        gate["source_ids"] = ["unknown"]
        for passed in [True, False]:
            gate["passed"] = passed
            self.assertTrue(validate_opportunity(record, "sample"))
            self.assertFalse(score_opportunity(record)["eligible_for_building"])

    def test_unconfirmed_gate_does_not_need_fabricated_evidence(self):
        record = opportunity()
        record["gates"]["maintainer_interest_confirmed"] = {"passed": False, "rationale": "Not yet asked"}
        self.assertEqual(validate_opportunity(record, "sample"), [])

    def test_gate_evidence_is_preserved_in_briefs_and_handoffs(self):
        record = opportunity()
        for text in [generate_candidate_brief(record), generate_handoff(record, "codex")]:
            self.assertIn("Gate evidence: maintainer_interest_confirmed cites s1", text)
            self.assertIn("https://example.test", text)

    def test_missing_rationale_cannot_produce_eligible_score(self):
        record = opportunity()
        del record["gates"]["repository_active"]["rationale"]
        self.assertFalse(score_opportunity(record)["eligible_for_building"])

    def test_inactive_work_cannot_be_build_eligible_even_when_gates_pass(self):
        for state in ["PARKED", "DECLINED", "MERGED", "RELEASED"]:
            record = opportunity()
            record["pipeline_state"] = state
            score = score_opportunity(record)
            self.assertFalse(score["eligible_for_building"])
            self.assertEqual(score["score"], 0)
            self.assertEqual(score["raw_score"], 2.7)
            self.assertIn("Implementation blocked", generate_handoff(record, "codex"))

    def test_every_state_has_a_next_action_and_stopped_work_stays_stopped(self):
        for state in PIPELINE_STATES:
            record = opportunity()
            record["pipeline_state"] = state
            self.assertTrue(next_action(record))
        self.assertIn("Keep declined", next_action(dict(opportunity(), pipeline_state="DECLINED")))
        self.assertIn("Keep parked", next_action(dict(opportunity(), pipeline_state="PARKED")))

    def test_brief_and_handoff_preserve_source_urls_dates_and_context(self):
        record = opportunity()
        for text in [generate_candidate_brief(record), generate_handoff(record, "codex")]:
            self.assertIn("https://example.test", text)
            self.assertIn("accessed 2026-09-06", text)
            self.assertIn("Next action:", text)
        text = generate_handoff(record, "codex")
        self.assertIn("Environment: local", text)
        self.assertIn("Maintainer context: named reviewer", text)
        self.assertIn("Risks: low", text)
        self.assertIn("validate the full Humanifest portfolio", text)

    def test_report_is_deterministic_and_does_not_rank_by_raw_score(self):
        first = dict(opportunity(), id="a")
        second = dict(opportunity(), id="b")
        second["score_inputs"] = dict(second["score_inputs"], humanitarian_benefit=5)
        report = portfolio_report([], [second, first])
        self.assertEqual(report, portfolio_report([], [first, second]))
        self.assertLess(report.index("- a:"), report.index("- b:"))

    def test_evidence_must_reference_a_unique_source(self):
        record = opportunity()
        record["evidence"][0]["source_id"] = "unknown"
        self.assertTrue(any("unknown source" in issue.message for issue in validate_opportunity(record, "sample")))
        record = opportunity()
        record["sources"].append(dict(record["sources"][0]))
        self.assertTrue(any("duplicate source id" in issue.message for issue in validate_opportunity(record, "sample")))

    def test_source_dates_and_urls_are_validated(self):
        for field, values in {"accessed": ["2026-02-30", "20260906", "", None],
                              "url": ["relative/path", "https://", "https://[", "https://bad host", None]}.items():
            for value in values:
                record = opportunity()
                record["sources"][0][field] = value
                self.assertTrue(validate_opportunity(record, "sample"), (field, value))
        record = opportunity()
        record["sources"][0]["url"] = "file:///private/tmp/inspected-repo"
        self.assertEqual(validate_opportunity(record, "sample"), [])

    def test_malformed_nested_data_returns_issues(self):
        for field, values in {"evidence": [None, [None], [{"type": []}]],
                              "sources": [None, [None], [{"id": []}]],
                              "title": [None, "", []], "pipeline_state": [None, [], {}]}.items():
            for value in values:
                record = opportunity()
                record[field] = value
                self.assertTrue(validate_opportunity(record, "sample"), (field, value))

    def test_advanced_states_require_maintainer_confirmation(self):
        for state in MAINTAINER_CONFIRMED_STATES:
            with self.subTest(state=state):
                record = opportunity()
                record["pipeline_state"] = state
                record["gates"]["maintainer_interest_confirmed"]["passed"] = False
                self.assertTrue(validate_opportunity(record, "sample"))

    def test_building_and_later_require_every_gate(self):
        for state in BUILDING_STATES:
            for gate in HARD_GATES:
                with self.subTest(state=state, gate=gate):
                    record = opportunity()
                    record["pipeline_state"] = state
                    record["gates"][gate]["passed"] = False
                    self.assertTrue(validate_opportunity(record, "sample"))

    def test_early_and_stopped_states_can_retain_failed_gates(self):
        for state in ["MAINTAINER-CHECK", "PARKED", "DECLINED"]:
            record = opportunity()
            record["pipeline_state"] = state
            record["gates"]["maintainer_interest_confirmed"]["passed"] = False
            self.assertEqual(validate_opportunity(record, "sample"), [])

    def test_invalid_gate_shapes_fail_closed(self):
        for value in [None, [], True, "yes"]:
            record = opportunity()
            record["gates"] = value
            self.assertTrue(validate_opportunity(record, "sample"))
            self.assertEqual(len(failed_gates(record)), len(HARD_GATES))
        record = opportunity()
        record["gates"][HARD_GATES[0]] = None
        self.assertTrue(validate_opportunity(record, "sample"))
        self.assertEqual(len(failed_gates(record)), 1)

    def test_gate_values_require_boolean_and_explanation(self):
        for value in [1, "true", None]:
            record = opportunity()
            record["gates"][HARD_GATES[0]]["passed"] = value
            self.assertTrue(validate_opportunity(record, "sample"))
        for value in ["", "  ", None]:
            record = opportunity()
            record["gates"][HARD_GATES[0]]["rationale"] = value
            self.assertTrue(validate_opportunity(record, "sample"))

    def test_invalid_scores_are_rejected(self):
        for value in [True, float("nan"), float("inf"), -1, 6, "3"]:
            record = opportunity()
            record["score_inputs"]["humanitarian_benefit"] = value
            self.assertTrue(validate_opportunity(record, "sample"))

    def test_handoff_exposes_blockers_for_every_target(self):
        record = opportunity()
        record["gates"]["maintainer_interest_confirmed"] = {"passed": False, "rationale": "not yet asked"}
        for target in ["codex", "spark", "cursor-red-team"]:
            text = generate_handoff(record, target)
            self.assertIn("Implementation blocked. Do not implement", text)
            self.assertIn("maintainer_interest_confirmed: not yet asked", text)

    def test_validation_accepts_complete_opportunity(self):
        self.assertEqual(validate_opportunity(opportunity(), "sample"), [])

    def test_score_is_zero_when_hard_gate_fails(self):
        record = opportunity()
        record["gates"]["maintainer_interest_confirmed"] = {"passed": False, "rationale": "not yet asked"}
        result = score_opportunity(record)
        self.assertEqual(result["score"], 0.0)
        self.assertFalse(result["eligible_for_building"])
        self.assertEqual(failed_gates(record)[0]["gate"], "maintainer_interest_confirmed")

    def test_score_rewards_benefit_confidence_and_penalizes_review_burden(self):
        result = score_opportunity(opportunity())
        self.assertEqual(result["raw_score"], 2.7)
        self.assertEqual(result["score"], 2.7)

    def test_handoff_generation_is_bounded(self):
        text = generate_handoff(opportunity(), "cursor-red-team")
        self.assertIn("Do not implement", text)
        self.assertIn("no external writes", text)


if __name__ == "__main__":
    unittest.main()
