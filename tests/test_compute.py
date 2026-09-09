import json
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
import tempfile
import unittest

from humanifest.cli import main
from humanifest.compute import compute_report, validate_compute_resources


def resources():
    return {
        "version": 1,
        "resources": [
            {
                "id": "github-copilot-free-individual",
                "provider": "GitHub Copilot",
                "account_scope": "individual",
                "cost_basis": "free-limited",
                "status": "allowed-with-constraints",
                "allowed_tasks": ["source-review", "test-design"],
                "disallowed_tasks": [
                    "limit-evasion",
                    "automated-maintainer-outreach",
                    "ungated-implementation",
                ],
                "limits": "Use only through an eligible individual account.",
                "policy_url": "https://docs.github.com/en/copilot",
                "policy_accessed": "2026-09-09",
                "oversight": "Human review remains required.",
            }
        ],
    }


class ComputeTests(unittest.TestCase):
    def test_valid_resources_report_cost_basis(self):
        record = resources()
        self.assertEqual(validate_compute_resources(record), [])
        report = compute_report(record)
        self.assertIn("Resources: 1", report)
        self.assertIn("- free-limited: 1", report)

    def test_required_disallowed_controls_cannot_be_removed(self):
        record = resources()
        record["resources"][0]["disallowed_tasks"] = ["credential-sharing"]
        issues = validate_compute_resources(record)
        self.assertTrue(any("missing required controls" in issue.message for issue in issues))

    def test_usage_metadata_is_bounded_and_dated(self):
        record = resources()
        resource = record["resources"][0]
        resource["cost_basis"] = "free-forever"
        resource["policy_accessed"] = "2026-02-30"
        issues = validate_compute_resources(record)
        self.assertTrue(any("cost_basis is not allowed" in issue.message for issue in issues))
        self.assertTrue(any("valid YYYY-MM-DD" in issue.message for issue in issues))

    def test_compute_cli_validates_registry(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "portfolio" / "compute-resources.json"
            path.parent.mkdir(parents=True)
            path.write_text(json.dumps(resources()), encoding="utf-8")
            stdout, stderr = StringIO(), StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                self.assertEqual(main(["compute", "--root", str(root)]), 0)
            self.assertIn("Resources: 1", stdout.getvalue())
            self.assertEqual(stderr.getvalue(), "")

            bad = resources()
            bad["resources"][0]["status"] = "unbounded"
            path.write_text(json.dumps(bad), encoding="utf-8")
            stdout, stderr = StringIO(), StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                self.assertEqual(main(["compute", "--root", str(root)]), 1)
            self.assertEqual(stdout.getvalue(), "")
            self.assertIn("status is not allowed", stderr.getvalue())
