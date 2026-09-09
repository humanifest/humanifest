"""Compute resource governance validation and reporting."""

from __future__ import annotations

from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any

from .models import ValidationIssue, load_json


ALLOWED_ACCOUNT_SCOPES = {"individual", "organization", "fiscal-steward", "self-hosted", "sponsored", "other"}
ALLOWED_COST_BASES = {"free-limited", "paid", "paid-or-sponsored", "donated", "self-hosted", "unknown"}
ALLOWED_STATUSES = {"allowed", "allowed-with-constraints", "requires-review", "disabled"}
REQUIRED_DISALLOWED_TASKS = {"limit-evasion", "automated-maintainer-outreach", "ungated-implementation"}


def load_compute_resources(root: Path) -> dict[str, Any]:
    return load_json(root / "portfolio" / "compute-resources.json")


def validate_compute_resources(record: dict[str, Any], label: str = "portfolio/compute-resources.json") -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    if record.get("version") != 1:
        issues.append(ValidationIssue(label, "version must be 1"))
    resources = record.get("resources")
    if not isinstance(resources, list):
        issues.append(ValidationIssue(label, "resources must be an array"))
        return issues
    seen = set()
    for index, resource in enumerate(resources):
        path = f"resources[{index}]"
        if not isinstance(resource, dict):
            issues.append(ValidationIssue(label, f"{path} must be an object"))
            continue
        resource_id = resource.get("id")
        if resource_id in seen:
            issues.append(ValidationIssue(label, f"duplicate resource id: {resource_id}"))
        seen.add(resource_id)
        _validate_resource(resource, path, label, issues)
    return issues


def compute_report(record: dict[str, Any]) -> str:
    resources = record.get("resources", [])
    statuses = Counter(item.get("status") for item in resources)
    cost_bases = Counter(item.get("cost_basis") for item in resources)
    rows = [
        "# Compute Governance",
        "",
        f"Resources: {len(resources)}",
        "Statuses:",
    ]
    rows.extend(f"- {status}: {count}" for status, count in sorted(statuses.items()) if status)
    if not statuses:
        rows.append("- none")
    rows.append("")
    rows.append("Cost bases:")
    rows.extend(f"- {basis}: {count}" for basis, count in sorted(cost_bases.items()) if basis)
    if not cost_bases:
        rows.append("- none")
    return "\n".join(rows)


def _validate_resource(resource: dict[str, Any], path: str, label: str, issues: list[ValidationIssue]) -> None:
    for field in ["id", "provider", "limits", "policy_url", "policy_accessed", "oversight"]:
        if not _nonempty_string(resource.get(field)):
            issues.append(ValidationIssue(label, f"{path}.{field} must be a non-empty string"))
    if resource.get("account_scope") not in ALLOWED_ACCOUNT_SCOPES:
        issues.append(ValidationIssue(label, f"{path}.account_scope is not allowed"))
    if resource.get("cost_basis") not in ALLOWED_COST_BASES:
        issues.append(ValidationIssue(label, f"{path}.cost_basis is not allowed"))
    if resource.get("status") not in ALLOWED_STATUSES:
        issues.append(ValidationIssue(label, f"{path}.status is not allowed"))
    for field in ["allowed_tasks", "disallowed_tasks"]:
        values = resource.get(field)
        if not isinstance(values, list) or not values:
            issues.append(ValidationIssue(label, f"{path}.{field} must be a non-empty array"))
            continue
        if len(values) != len(set(values)):
            issues.append(ValidationIssue(label, f"{path}.{field} must not contain duplicates"))
        if not all(_nonempty_string(value) for value in values):
            issues.append(ValidationIssue(label, f"{path}.{field} values must be non-empty strings"))
    disallowed = set(resource.get("disallowed_tasks", [])) if isinstance(resource.get("disallowed_tasks"), list) else set()
    missing = sorted(REQUIRED_DISALLOWED_TASKS - disallowed)
    if missing:
        issues.append(ValidationIssue(label, f"{path}.disallowed_tasks missing required controls: {', '.join(missing)}"))
    _validate_date(resource.get("policy_accessed"), label, f"{path}.policy_accessed", issues)


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
