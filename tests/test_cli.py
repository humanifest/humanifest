from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
import json
from pathlib import Path
import tempfile
import unittest

from humanifest.cli import main
from tests.test_models import opportunity


class CliTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def run_cli(self, *args):
        stdout, stderr = StringIO(), StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            status = main(list(args))
        return status, stdout.getvalue(), stderr.getvalue()

    def write_record(self, name, record):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(record), encoding="utf-8")
        return path

    def seed_portfolio(self):
        project = {
            "id": "sample-project", "name": "Sample", "repository": "https://example.test/repo",
            "homepage": "https://example.test", "license": "MIT", "humanitarian_domain": "Health",
            "maintenance": {}, "contribution": {}, "impact_evidence": [],
            "sources": opportunity()["sources"],
        }
        self.write_record("portfolio/projects/sample.json", project)
        self.write_record("portfolio/opportunities/sample.json", opportunity())

    def test_missing_root_fails_instead_of_reporting_success(self):
        for command in ["validate", "report"]:
            status, out, err = self.run_cli(command, "--root", str(self.root / "missing"))
            self.assertEqual(status, 1)
            self.assertEqual(out, "")
            self.assertIn("required record directory is missing", err)

    def test_valid_portfolio_and_json_score(self):
        self.seed_portfolio()
        for command in ["validate", "report"]:
            status, out, err = self.run_cli(command, "--root", str(self.root))
            self.assertEqual((status, err), (0, ""))
            self.assertTrue(out)
        status, out, err = self.run_cli("score", str(self.root / "portfolio/opportunities/sample.json"))
        self.assertEqual((status, err), (0, ""))
        self.assertEqual(json.loads(out)["score"], 2.7)

    def test_bad_inputs_have_diagnostics_without_tracebacks(self):
        for content in ["{", "[]", '{"id": "a", "id": "b"}', '{"score": NaN}', '{}']:
            path = self.root / "bad.json"
            path.write_text(content)
            for command in ["score", "brief", "handoff"]:
                args = [command, str(path)]
                if command == "handoff":
                    args.extend(["--target", "codex"])
                with self.subTest(content=content, command=command):
                    status, out, err = self.run_cli(*args)
                    self.assertEqual(status, 1)
                    self.assertEqual(out, "")
                    self.assertTrue(err)
                    self.assertNotIn("Traceback", err)
        status, out, err = self.run_cli("brief", str(self.root / "missing.json"))
        self.assertEqual((status, out), (1, ""))
        self.assertIn("missing.json", err)

    def test_portfolio_collects_errors_and_blocks_report(self):
        self.seed_portfolio()
        bad = opportunity()
        bad["project_id"] = "missing-project"
        self.write_record("portfolio/opportunities/duplicate.json", bad)
        (self.root / "portfolio/projects/bad.json").write_text("{")
        for command in ["validate", "report"]:
            status, out, err = self.run_cli(command, "--root", str(self.root))
            self.assertEqual((status, out), (1, ""))
            self.assertIn("bad.json", err)
            self.assertIn("duplicate opportunities id", err)
            self.assertIn("unknown project: missing-project", err)

    def test_duplicate_project_ids_are_rejected(self):
        self.seed_portfolio()
        project = json.loads((self.root / "portfolio/projects/sample.json").read_text())
        self.write_record("portfolio/projects/duplicate.json", project)
        status, _, err = self.run_cli("validate", "--root", str(self.root))
        self.assertEqual(status, 1)
        self.assertIn("duplicate projects id", err)

    def test_invalid_advanced_state_cannot_produce_a_handoff(self):
        record = opportunity()
        record["pipeline_state"] = "BUILDING"
        record["gates"]["maintainer_interest_confirmed"]["passed"] = False
        path = self.write_record("blocked.json", record)
        status, out, err = self.run_cli("handoff", str(path), "--target", "codex")
        self.assertEqual((status, out), (1, ""))
        self.assertIn("requires every hard gate", err)

    def test_uncited_confirmation_cannot_render_score_or_handoff(self):
        record = opportunity()
        del record["gates"]["maintainer_interest_confirmed"]["source_ids"]
        path = self.write_record("uncited.json", record)
        for command in ["score", "brief", "handoff"]:
            args = [command, str(path)]
            if command == "handoff":
                args.extend(["--target", "codex"])
            status, out, err = self.run_cli(*args)
            self.assertEqual((status, out), (1, ""))
            self.assertIn("must cite confirmation evidence", err)

    def test_sources_command_renders_json_and_read_only_review_reminders(self):
        self.seed_portfolio()
        path = self.root / "portfolio/opportunities/sample.json"
        record = json.loads(path.read_text())
        record["sources"][0]["url"] = "file:///tmp/evidence"
        path.write_text(json.dumps(record))
        before = path.read_bytes()
        args = ["sources", "--root", str(self.root), "--as-of", "2026-09-08", "--max-age-days", "30"]
        status, out, err = self.run_cli(*args, "--format", "json", "--needs-review")
        self.assertEqual((status, err), (0, ""))
        review = json.loads(out)
        self.assertEqual(review["total_sources"], 2)
        self.assertEqual(review["sources_needing_review"], 1)
        self.assertEqual(review["sources"][0]["review_reasons"], ["local-file"])
        self.assertEqual(path.read_bytes(), before)
        status, out, err = self.run_cli(*args)
        self.assertEqual((status, err), (0, ""))
        self.assertIn("# Source Review", out)
        self.assertIn("file:///tmp/evidence", out)

    def test_sources_requires_explicit_valid_review_parameters(self):
        for args in [[], ["--as-of", "2026-09-08"],
                     ["--as-of", "2026-02-30", "--max-age-days", "30"],
                     ["--as-of", "20260908", "--max-age-days", "30"],
                     ["--as-of", "2026-09-08", "--max-age-days", "-1"]]:
            with self.subTest(args=args), self.assertRaises(SystemExit) as raised:
                self.run_cli("sources", *args)
            self.assertEqual(raised.exception.code, 2)

    def test_sources_rejects_invalid_portfolio_before_rendering(self):
        status, out, err = self.run_cli("sources", "--root", str(self.root),
                                        "--as-of", "2026-09-08", "--max-age-days", "30")
        self.assertEqual((status, out), (1, ""))
        self.assertIn("required record directory", err)

    def add_opportunity(self, record_id, state, project_id="sample-project"):
        record = opportunity()
        record.update(id=record_id, pipeline_state=state, project_id=project_id)
        self.write_record(f"portfolio/opportunities/{record_id}.json", record)

    def test_work_is_read_only_and_validates_whole_portfolio(self):
        self.seed_portfolio()
        record = opportunity()
        record.update(pipeline_state="MAINTAINER-CHECK", research_next_step="Verify setup hooks.",
                      next_external_status_check="2026-09-15")
        path = self.write_record("portfolio/opportunities/sample.json", record)
        before = path.read_bytes()
        args = ["work", "--root", str(self.root), "--as-of", "2026-09-08"]
        status, out, err = self.run_cli(*args, "--format", "json")
        self.assertEqual((status, err), (0, ""))
        self.assertEqual(json.loads(out)["independent_research"][0]["action"], "Verify setup hooks.")
        self.assertEqual(path.read_bytes(), before)
        status, out, err = self.run_cli(*args)
        self.assertEqual((status, err), (0, ""))
        self.assertIn("Independent research available now", out)
        self.add_opportunity("one", "BUILDING")
        self.add_opportunity("two", "BUILDING")
        status, out, err = self.run_cli(*args)
        self.assertEqual((status, out), (1, ""))
        self.assertIn("2 active implementations", err)

    def test_work_requires_explicit_date_and_rejects_invalid_records(self):
        for args in [[], ["--as-of", "20260908"], ["--as-of", "2026-02-30"]]:
            with self.subTest(args=args), self.assertRaises(SystemExit) as raised:
                self.run_cli("work", *args)
            self.assertEqual(raised.exception.code, 2)
        self.seed_portfolio()
        record = opportunity()
        record["next_external_status_check"] = "tomorrow"
        self.write_record("portfolio/opportunities/sample.json", record)
        status, out, err = self.run_cli("work", "--root", str(self.root), "--as-of", "2026-09-08")
        self.assertEqual((status, out), (1, ""))
        self.assertIn("next_external_status_check", err)

    def test_work_keeps_new_candidates_visible_without_optional_work_fields(self):
        self.seed_portfolio()
        record = opportunity()
        record["pipeline_state"] = "QUEUED"
        record["gates"]["maintainer_interest_confirmed"]["passed"] = False
        path = self.write_record("portfolio/opportunities/sample.json", record)
        before = path.read_bytes()
        args = ["work", "--root", str(self.root), "--as-of", "2026-09-08"]
        status, out, err = self.run_cli(*args)
        self.assertEqual((status, err), (0, ""))
        self.assertIn("Candidates needing a research plan", out)
        self.assertIn(record["title"], out)
        self.assertNotIn("find and verify another bounded opportunity", out)
        status, out, err = self.run_cli(*args, "--format", "json")
        self.assertEqual((status, err), (0, ""))
        plan = json.loads(out)
        self.assertEqual(plan["needs_research_plan"][0]["id"], record["id"])
        self.assertEqual(plan["active_work"], [])
        self.assertFalse(plan["refill_suggested"])
        self.assertEqual(path.read_bytes(), before)

    def set_project_repository(self, repository, project_id="sample-project", **extra):
        project = json.loads((self.root / "portfolio/projects/sample.json").read_text())
        project.update(id=project_id, repository=repository, **extra)
        self.write_record(f"portfolio/projects/{project_id}.json" if project_id != "sample-project"
                          else "portfolio/projects/sample.json", project)

    def test_active_implementation_limit_includes_review_stages(self):
        self.seed_portfolio()
        self.add_opportunity("first", "BUILDING")
        for state in ["BUILDING", "ADVERSARIAL-REVIEW", "HUMAN-REVIEW"]:
            self.add_opportunity("second", state)
            for command in ["validate", "report"]:
                status, out, err = self.run_cli(command, "--root", str(self.root))
                self.assertEqual((status, out), (1, ""))
                self.assertIn("2 active implementations (maximum 1)", err)
                self.assertIn("first, second", err)

    def test_one_implementation_and_two_distinct_organization_prs_are_allowed(self):
        self.seed_portfolio()
        self.set_project_repository("https://github.com/first/repo")
        self.set_project_repository("https://github.com/second/repo", "second-project")
        self.add_opportunity("building", "BUILDING")
        self.add_opportunity("first-pr", "PR-OPEN")
        self.add_opportunity("second-pr", "PR-OPEN", "second-project")
        for state in ["PARKED", "DECLINED", "MERGED", "RELEASED"]:
            self.add_opportunity(state.lower(), state)
        status, out, err = self.run_cli("report", "--root", str(self.root))
        self.assertEqual((status, err), (0, ""))
        self.assertIn("Active implementations: 1/1", out)
        self.assertIn("Open external PRs: 2/2", out)

    def test_organization_limit_spans_repositories_and_ignores_owner_case(self):
        self.seed_portfolio()
        self.set_project_repository("https://github.com/Medic/one.git")
        self.set_project_repository("https://github.com/medic/two/", "second-project")
        self.add_opportunity("first-pr", "PR-OPEN")
        self.add_opportunity("second-pr", "PR-OPEN", "second-project")
        status, _, err = self.run_cli("validate", "--root", str(self.root))
        self.assertEqual(status, 1)
        self.assertIn("organization PR limit exceeded for github.com/medic", err)

    def test_global_pr_limit_across_distinct_organizations(self):
        self.seed_portfolio()
        for index in range(3):
            project_id = f"project-{index}"
            self.set_project_repository(f"https://github.com/org-{index}/repo", project_id)
            self.add_opportunity(f"pr-{index}", "PR-OPEN", project_id)
        status, _, err = self.run_cli("validate", "--root", str(self.root))
        self.assertEqual(status, 1)
        self.assertIn("3 open external PRs (maximum 2)", err)
        self.assertNotIn("organization PR limit exceeded", err)

    def test_unknown_host_requires_explicit_review_organization_for_open_pr(self):
        self.seed_portfolio()
        self.add_opportunity("open-pr", "PR-OPEN")
        status, _, err = self.run_cli("validate", "--root", str(self.root))
        self.assertEqual(status, 1)
        self.assertIn("cannot determine review organization", err)
        self.set_project_repository("https://example.test/repo", review_organization="example.test/team")
        status, _, err = self.run_cli("validate", "--root", str(self.root))
        self.assertEqual((status, err), (0, ""))

    def test_explicit_organization_combines_hosts_and_is_not_blank(self):
        self.seed_portfolio()
        self.set_project_repository("https://example.test/repo", review_organization=" Shared-Team ")
        self.set_project_repository("https://elsewhere.test/repo", "second-project", review_organization="shared-team")
        self.add_opportunity("first-pr", "PR-OPEN")
        self.add_opportunity("second-pr", "PR-OPEN", "second-project")
        status, _, err = self.run_cli("validate", "--root", str(self.root))
        self.assertEqual(status, 1)
        self.assertIn("organization PR limit exceeded for shared-team", err)
        self.set_project_repository("https://example.test/repo", review_organization=" ")
        status, _, err = self.run_cli("validate", "--root", str(self.root))
        self.assertEqual(status, 1)
        self.assertIn("review_organization must be a non-empty string", err)
