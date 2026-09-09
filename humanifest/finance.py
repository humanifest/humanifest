"""Finance governance ledger validation and reporting."""

from __future__ import annotations

from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any

from .models import ValidationIssue, load_json


ALLOWED_TRANSACTION_CATEGORIES = {
    "sponsorship-income",
    "fiscal-admin",
    "engineering",
    "evidence-review",
    "maintainer-coordination",
    "environment",
    "adversarial-review",
    "documentation",
    "governance",
    "reimbursement",
    "reserve",
}

ALLOWED_TRANSACTION_CONFLICT_STATUSES = {"none-known", "disclosed", "requires-review"}
ALLOWED_CONFLICT_STATUSES = {"disclosed", "requires-review", "resolved"}

REQUIRED_STEWARD_PHRASE = "Humanifest is currently fiscally administered by Avaelus LLC/Inc."


def load_funding_ledger(root: Path) -> dict[str, Any]:
    return load_json(root / "portfolio" / "funding-ledger.json")


def validate_funding_ledger(record: dict[str, Any], label: str = "portfolio/funding-ledger.json") -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    required = ["version", "currency", "fiscal_steward", "privacy", "transactions", "conflicts", "reports"]
    for field in required:
        if field not in record:
            issues.append(ValidationIssue(label, f"missing required field: {field}"))
    if issues:
        return issues

    if record["version"] != 1:
        issues.append(ValidationIssue(label, "version must be 1"))
    if record["currency"] != "USD":
        issues.append(ValidationIssue(label, "currency must be USD"))
    _validate_steward(record["fiscal_steward"], label, issues)
    _validate_privacy(record["privacy"], label, issues)
    _validate_collection(record["transactions"], "transactions", label, issues, _validate_transaction)
    _validate_collection(record["conflicts"], "conflicts", label, issues, _validate_conflict)
    _validate_collection(record["reports"], "reports", label, issues, _validate_report)
    return issues


def finance_report(record: dict[str, Any]) -> str:
    transactions = record.get("transactions", [])
    conflicts = record.get("conflicts", [])
    total = sum(item.get("amount", 0) for item in transactions if isinstance(item.get("amount"), (int, float)))
    categories = Counter(item.get("category") for item in transactions)
    needs_review = [item for item in conflicts if item.get("status") == "requires-review"]
    rows = [
        "# Finance Governance",
        "",
        f"Fiscal steward: {record.get('fiscal_steward', {}).get('name', 'unknown')}",
        f"Relationship: {record.get('fiscal_steward', {}).get('relationship', 'unknown')}",
        f"Currency: {record.get('currency', 'unknown')}",
        f"Transactions: {len(transactions)}",
        f"Net recorded amount: {total:.2f}",
        f"Conflicts requiring review: {len(needs_review)}",
        "",
        "Category counts:",
    ]
    rows.extend(f"- {category}: {count}" for category, count in sorted(categories.items()) if category)
    if not categories:
        rows.append("- none")
    return "\n".join(rows)


def _validate_steward(value: Any, label: str, issues: list[ValidationIssue]) -> None:
    if not isinstance(value, dict):
        issues.append(ValidationIssue(label, "fiscal_steward must be an object"))
        return
    for field in ["name", "relationship", "started", "status", "notes"]:
        if not _nonempty_string(value.get(field)):
            issues.append(ValidationIssue(label, f"fiscal_steward.{field} must be a non-empty string"))
    if value.get("relationship") != REQUIRED_STEWARD_PHRASE:
        issues.append(ValidationIssue(label, "fiscal_steward.relationship must state the Avaelus fiscal administration relationship"))
    if value.get("status") not in {"temporary", "active", "retired"}:
        issues.append(ValidationIssue(label, "fiscal_steward.status must be temporary, active, or retired"))
    _validate_date(value.get("started"), label, "fiscal_steward.started", issues)


def _validate_privacy(value: Any, label: str, issues: list[ValidationIssue]) -> None:
    if not isinstance(value, dict):
        issues.append(ValidationIssue(label, "privacy must be an object"))
        return
    if value.get("public_ledger_excludes_private_donor_data") is not True:
        issues.append(ValidationIssue(label, "privacy.public_ledger_excludes_private_donor_data must be true"))
    if not _nonempty_string(value.get("notes")):
        issues.append(ValidationIssue(label, "privacy.notes must be a non-empty string"))


def _validate_collection(value: Any, field: str, label: str, issues: list[ValidationIssue], validator) -> None:
    if not isinstance(value, list):
        issues.append(ValidationIssue(label, f"{field} must be an array"))
        return
    seen = set()
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            issues.append(ValidationIssue(label, f"{field}[{index}] must be an object"))
            continue
        item_id = item.get("id") or item.get("period")
        if item_id in seen:
            issues.append(ValidationIssue(label, f"duplicate {field} id: {item_id}"))
        seen.add(item_id)
        validator(item, f"{field}[{index}]", label, issues)


def _validate_transaction(item: dict[str, Any], path: str, label: str, issues: list[ValidationIssue]) -> None:
    for field in ["id", "description"]:
        if not _nonempty_string(item.get(field)):
            issues.append(ValidationIssue(label, f"{path}.{field} must be a non-empty string"))
    _validate_date(item.get("date"), label, f"{path}.date", issues)
    if item.get("category") not in ALLOWED_TRANSACTION_CATEGORIES:
        issues.append(ValidationIssue(label, f"{path}.category is not allowed"))
    if not isinstance(item.get("amount"), (int, float)) or isinstance(item.get("amount"), bool):
        issues.append(ValidationIssue(label, f"{path}.amount must be a number"))
    if item.get("conflict_status") not in ALLOWED_TRANSACTION_CONFLICT_STATUSES:
        issues.append(ValidationIssue(label, f"{path}.conflict_status is not allowed"))


def _validate_conflict(item: dict[str, Any], path: str, label: str, issues: list[ValidationIssue]) -> None:
    for field in ["id", "description", "resolution"]:
        if not _nonempty_string(item.get(field)):
            issues.append(ValidationIssue(label, f"{path}.{field} must be a non-empty string"))
    _validate_date(item.get("date"), label, f"{path}.date", issues)
    if item.get("status") not in ALLOWED_CONFLICT_STATUSES:
        issues.append(ValidationIssue(label, f"{path}.status is not allowed"))


def _validate_report(item: dict[str, Any], path: str, label: str, issues: list[ValidationIssue]) -> None:
    if not _nonempty_string(item.get("period")):
        issues.append(ValidationIssue(label, f"{path}.period must be a non-empty string"))
    if not _nonempty_string(item.get("summary")):
        issues.append(ValidationIssue(label, f"{path}.summary must be a non-empty string"))
    _validate_date(item.get("published"), label, f"{path}.published", issues)


def _validate_date(value: Any, label: str, field: str, issues: list[ValidationIssue]) -> None:
    if not isinstance(value, str):
        issues.append(ValidationIssue(label, f"{field} must be a YYYY-MM-DD date"))
        return
    try:
        parsed = date.fromisoformat(value)
    except ValueError:
        issues.append(ValidationIssue(label, f"{field} must be a valid YYYY-MM-DD date"))
        return
    if parsed.isoformat() != value:
        issues.append(ValidationIssue(label, f"{field} must be a valid YYYY-MM-DD date"))


def _nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())
