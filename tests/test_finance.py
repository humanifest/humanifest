import json
from pathlib import Path
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO

from humanifest.finance import finance_report, validate_funding_ledger
from humanifest.cli import main


def ledger():
    return {
        "version": 1,
        "currency": "USD",
        "fiscal_steward": {
            "name": "Avaelus LLC/Inc.",
            "relationship": "Humanifest is currently fiscally administered by Avaelus LLC/Inc.",
            "started": "2026-09-09",
            "status": "temporary",
            "notes": "Temporary fiscal administration while Humanifest lacks a dedicated entity.",
        },
        "privacy": {
            "public_ledger_excludes_private_donor_data": True,
            "notes": "Public records omit donor private data.",
        },
        "transactions": [],
        "conflicts": [],
        "reports": [],
    }


class FinanceTests(unittest.TestCase):
    def test_valid_empty_ledger_records_fiscal_steward(self):
        record = ledger()
        self.assertEqual(validate_funding_ledger(record), [])
        report = finance_report(record)
        self.assertIn("Fiscal steward: Avaelus LLC/Inc.", report)
        self.assertIn("Transactions: 0", report)

    def test_fiscal_relationship_must_be_plainly_documented(self):
        record = ledger()
        record["fiscal_steward"]["relationship"] = "Avaelus helps"
        issues = validate_funding_ledger(record)
        self.assertTrue(any("Avaelus fiscal administration" in issue.message for issue in issues))

    def test_public_ledger_must_exclude_private_donor_data(self):
        record = ledger()
        record["privacy"]["public_ledger_excludes_private_donor_data"] = False
        issues = validate_funding_ledger(record)
        self.assertTrue(any("must be true" in issue.message for issue in issues))

    def test_transaction_categories_and_conflicts_are_bounded(self):
        record = ledger()
        record["transactions"].append({
            "id": "first-sponsor",
            "date": "2026-09-09",
            "category": "priority-access",
            "amount": 100,
            "description": "Invalid paid priority.",
            "conflict_status": "none-known",
        })
        record["conflicts"].append({
            "id": "needs-review",
            "date": "2026-09-09",
            "status": "requires-review",
            "description": "Avaelus client relationship may affect project selection.",
            "resolution": "Pending independent review.",
        })
        issues = validate_funding_ledger(record)
        self.assertTrue(any("category is not allowed" in issue.message for issue in issues))
        self.assertIn("Conflicts requiring review: 1", finance_report(record))

    def test_finance_cli_validates_ledger(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "portfolio" / "funding-ledger.json"
            path.parent.mkdir(parents=True)
            path.write_text(json.dumps(ledger()), encoding="utf-8")
            stdout, stderr = StringIO(), StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                self.assertEqual(main(["finance", "--root", str(root)]), 0)
            self.assertIn("Fiscal steward: Avaelus LLC/Inc.", stdout.getvalue())
            self.assertEqual(stderr.getvalue(), "")

            bad = ledger()
            bad["currency"] = "EUR"
            path.write_text(json.dumps(bad), encoding="utf-8")
            stdout, stderr = StringIO(), StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                self.assertEqual(main(["finance", "--root", str(root)]), 1)
            self.assertEqual(stdout.getvalue(), "")
            self.assertIn("currency must be USD", stderr.getvalue())
