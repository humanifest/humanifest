"""Data loading, validation, gates, scoring, and report generation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
import json
from typing import Any
from urllib.parse import urlsplit


PIPELINE_STATES = [
    "QUEUED",
    "PROJECT-AUDIT",
    "OPPORTUNITY-RESEARCH",
    "SHORTLISTED",
    "MAINTAINER-CHECK",
    "ENVIRONMENT-READY",
    "REPRODUCED",
    "BUILDING",
    "ADVERSARIAL-REVIEW",
    "HUMAN-REVIEW",
    "PR-OPEN",
    "MERGED",
    "RELEASED",
    "PARKED",
    "DECLINED",
]

EVIDENCE_TYPES = {"measured", "modeled", "self_reported", "inferred"}
MAINTAINER_CONFIRMED_STATES = PIPELINE_STATES[5:13]
BUILDING_STATES = PIPELINE_STATES[7:13]
ACTIVE_IMPLEMENTATION_STATES = ["BUILDING", "ADVERSARIAL-REVIEW", "HUMAN-REVIEW"]
INACTIVE_STATES = ["PARKED", "DECLINED", "MERGED", "RELEASED"]

HARD_GATES = [
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

SCORE_WEIGHTS = {
    "humanitarian_benefit": 0.30,
    "acceptance_probability": 0.20,
    "technical_confidence": 0.20,
    "review_burden": -0.20,
    "deployment_probability": 0.10,
}

REQUIRED_PROJECT_FIELDS = [
    "id",
    "name",
    "repository",
    "homepage",
    "license",
    "humanitarian_domain",
    "impact_evidence",
    "maintenance",
    "contribution",
    "sources",
]

REQUIRED_OPPORTUNITY_FIELDS = [
    "id",
    "project_id",
    "title",
    "pipeline_state",
    "problem",
    "humanitarian_relevance",
    "evidence",
    "code_surface",
    "proposed_change",
    "tests",
    "environment",
    "maintainer",
    "risks",
    "gates",
    "score_inputs",
    "sources",
]


@dataclass(frozen=True)
class ValidationIssue:
    record: str
    message: str


def load_json(path: Path) -> dict[str, Any]:
    def unique_object(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate JSON key: {key}")
            result[key] = value
        return result

    def reject_constant(value):
        raise ValueError(f"invalid JSON constant: {value}")

    with path.open(encoding="utf-8") as handle:
        data = json.load(handle, object_pairs_hook=unique_object, parse_constant=reject_constant)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def iter_records(directory: Path) -> list[tuple[Path, dict[str, Any]]]:
    records: list[tuple[Path, dict[str, Any]]] = []
    if not directory.exists():
        return records
    for path in sorted(directory.glob("*.json")):
        records.append((path, load_json(path)))
    return records


def validate_project(record: dict[str, Any], record_name: str) -> list[ValidationIssue]:
    issues = _require_fields(record, REQUIRED_PROJECT_FIELDS, record_name)
    issues.extend(_validate_text_fields(record, REQUIRED_PROJECT_FIELDS[:6], record_name))
    for field in ["maintenance", "contribution"]:
        if not isinstance(record.get(field), dict):
            issues.append(ValidationIssue(record_name, f"{field} must be an object"))
    if "review_organization" in record:
        issues.extend(_validate_text_fields(record, ["review_organization"], record_name))
    issues.extend(_validate_sources(record, record_name))
    issues.extend(_validate_evidence_list(record.get("impact_evidence", []), record_name, "impact_evidence", _source_ids(record)))
    return issues


def validate_opportunity(record: dict[str, Any], record_name: str) -> list[ValidationIssue]:
    issues = _require_fields(record, REQUIRED_OPPORTUNITY_FIELDS, record_name)
    issues.extend(_validate_text_fields(record, [field for field in REQUIRED_OPPORTUNITY_FIELDS
                                               if field not in {"evidence", "gates", "score_inputs", "sources"}], record_name))
    state = record.get("pipeline_state")
    if state not in PIPELINE_STATES:
        issues.append(ValidationIssue(record_name, f"pipeline_state must be one of {', '.join(PIPELINE_STATES)}"))
    gates = record.get("gates", {})
    if not isinstance(gates, dict):
        issues.append(ValidationIssue(record_name, "gates must be an object"))
    else:
        for gate in HARD_GATES:
            item = gates.get(gate)
            if not isinstance(item, dict) or "passed" not in item or "rationale" not in item:
                issues.append(ValidationIssue(record_name, f"gate {gate} must include passed and rationale"))
                continue
            if not isinstance(item["passed"], bool):
                issues.append(ValidationIssue(record_name, f"gate {gate}.passed must be a boolean"))
            if not isinstance(item["rationale"], str) or not item["rationale"].strip():
                issues.append(ValidationIssue(record_name, f"gate {gate}.rationale must be a non-empty string"))
            issues.extend(ValidationIssue(record_name, message) for message in
                          _gate_reference_errors(gate, item, _source_ids(record)))
    failures = failed_gates(record)
    if state in MAINTAINER_CONFIRMED_STATES and any(
        item["gate"] == "maintainer_interest_confirmed" for item in failures
    ):
        issues.append(ValidationIssue(record_name, f"{state} requires maintainer_interest_confirmed to pass"))
    if state in BUILDING_STATES and failures:
        issues.append(ValidationIssue(record_name, f"{state} requires every hard gate to pass"))
    score_inputs = record.get("score_inputs", {})
    if not isinstance(score_inputs, dict):
        issues.append(ValidationIssue(record_name, "score_inputs must be an object"))
    else:
        for key in SCORE_WEIGHTS:
            value = score_inputs.get(key)
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not 0 <= value <= 5:
                issues.append(ValidationIssue(record_name, f"score_inputs.{key} must be a number from 0 to 5"))
    issues.extend(_validate_sources(record, record_name))
    issues.extend(_validate_evidence_list(record.get("evidence", []), record_name, "evidence", _source_ids(record)))
    return issues


def failed_gates(record: dict[str, Any]) -> list[dict[str, str]]:
    failures = []
    gates = record.get("gates")
    if not isinstance(gates, dict):
        gates = {}
    for gate in HARD_GATES:
        item = gates.get(gate)
        if not isinstance(item, dict):
            item = {}
        if item.get("passed") is not True:
            failures.append({"gate": gate, "rationale": str(item.get("rationale", "missing rationale"))})
        else:
            errors = _gate_reference_errors(gate, item, _source_ids(record))
            if not isinstance(item.get("rationale"), str) or not item["rationale"].strip():
                errors.append(f"gate {gate}.rationale must be a non-empty string")
            if errors:
                failures.append({"gate": gate, "rationale": "; ".join(errors)})
    return failures


def score_opportunity(record: dict[str, Any], weights: dict[str, float] | None = None) -> dict[str, Any]:
    weights = weights or SCORE_WEIGHTS
    inputs = record["score_inputs"]
    weighted_total = 0.0
    details = {}
    for key, weight in weights.items():
        contribution = float(inputs[key]) * weight
        details[key] = {"value": inputs[key], "weight": weight, "contribution": round(contribution, 3)}
        weighted_total += contribution

    failures = failed_gates(record)
    eligible = not failures and record.get("pipeline_state") not in INACTIVE_STATES
    return {
        "eligible_for_building": eligible,
        "eligibility_scope": "Record gates and state only; portfolio capacity and user authorization must be checked separately.",
        "score": round(max(0.0, weighted_total), 3) if eligible else 0.0,
        "raw_score": round(weighted_total, 3),
        "failed_gates": failures,
        "details": details,
    }


def generate_candidate_brief(record: dict[str, Any]) -> str:
    score = score_opportunity(record)
    evidence_lines = [
        f"- {item['type']}: {item['claim']} ({item['source_id']})"
        for item in record.get("evidence", [])
    ]
    failed = score["failed_gates"]
    gate_lines = ["- none"] if not failed else [f"- {item['gate']}: {item['rationale']}" for item in failed]
    return "\n".join(
        [
            f"# {record['title']}",
            "",
            f"Project: {record['project_id']}",
            f"Pipeline state: {record['pipeline_state']}",
            f"Score: {score['score']} (raw {score['raw_score']})",
            f"Next action: {next_action(record)}",
            score["eligibility_scope"],
            "",
            "## Problem",
            record["problem"],
            "",
            "## Evidence",
            *evidence_lines,
            "",
            "## Proposed smallest safe change",
            record["proposed_change"],
            "",
            "## Failed gates",
            *gate_lines,
            "",
            "## Sources",
            *_gate_evidence_lines(record),
            *_source_lines(record),
        ]
    )


def generate_handoff(record: dict[str, Any], target: str) -> str:
    if target not in {"codex", "spark", "cursor-red-team"}:
        raise ValueError("target must be codex, spark, or cursor-red-team")
    base = [
        f"Objective: evaluate and prepare the opportunity `{record['id']}` for {record['project_id']}.",
        f"Title: {record['title']}",
        f"Scope: {record['code_surface']}",
        f"Problem: {record['problem']}",
        f"Proposed bounded change: {record['proposed_change']}",
        f"Acceptance criteria: {record['tests']}",
        f"Environment: {record['environment']}",
        f"Maintainer context: {record['maintainer']}",
        f"Risks: {record['risks']}",
        f"Next action: {next_action(record)}",
        "Before implementation: validate the full Humanifest portfolio and check its capacity limits; inspect target setup code before executing it.",
        "Publication: follow the target's contribution policy; push an authorized, tested change on a dedicated branch in the verified Humanifest bot's fork and open a PR against the intended upstream base. Verify PR author, head, and base; do not request upstream Write access as a prerequisite or merge without separate authorization.",
        "Constraints: no external writes or maintainer contact outside explicit user authorization. Consult docs/contribution-protocol.md for standing authorization and verify the Humanifest posting identity; never use the user's personal account. No private data; stop if evidence contradicts the gate rationale.",
        "Return format: findings, changed files if any, commands run, remaining blockers, and confidence.",
    ]
    failures = failed_gates(record)
    base.insert(2, f"Pipeline state: {record['pipeline_state']}.")
    if failures or record["pipeline_state"] in INACTIVE_STATES:
        base.append("Implementation blocked. Do not implement; respect the current state. Inspect listed blockers read-only; maintainer coordination is permitted only within explicit user authorization and through the verified Humanifest identity.")
    else:
        base.append("All hard gates pass. Implementation still requires an approved scope and inspected environment.")
    base.extend(f"Blocker: {item['gate']}: {item['rationale']}" for item in failures)
    base.extend(_gate_evidence_lines(record))
    base.extend(["Sources (supplied evidence; not independently refreshed):", *_source_lines(record)])
    if target == "spark":
        base.insert(0, "Use a fast Codex model only for bounded inspection or mechanical verification.")
    elif target == "cursor-red-team":
        base.insert(0, "Act as an independent adversarial reviewer. Do not implement the fix.")
        base.append("Focus on hidden scope, security, environment risk, test gaps, and maintainer burden.")
    else:
        base.insert(0, "Use full-reasoning Codex for synthesis, integration, and final go/no-go.")
    return "\n".join(base)


def portfolio_report(projects: list[dict[str, Any]], opportunities: list[dict[str, Any]]) -> str:
    rows = ["# Portfolio Status", ""]
    rows.append(f"Projects: {len(projects)}")
    rows.append(f"Opportunities: {len(opportunities)}")
    active = sum(item["pipeline_state"] in ACTIVE_IMPLEMENTATION_STATES for item in opportunities)
    prs = sum(item["pipeline_state"] == "PR-OPEN" for item in opportunities)
    rows.extend([f"Active implementations: {active}/1", f"Open external PRs: {prs}/2 (at most 1 per organization)"])
    rows.extend(["", "Status reflects supplied records; source access dates are not a live upstream check.",
                 "Scores do not authorize implementation or external writes. Candidates are listed by state and ID, not ranked by raw score."])
    rows.append("")
    for opportunity in sorted(opportunities, key=lambda item: (PIPELINE_STATES.index(item["pipeline_state"]), item["id"])):
        score = score_opportunity(opportunity)
        rows.append(f"- {opportunity['id']}: {opportunity['pipeline_state']}; score={score['score']}; failed_gates={len(score['failed_gates'])}")
        rows.append(f"  Next: {next_action(opportunity)}")
        for failure in score["failed_gates"]:
            rows.append(f"  - {failure['gate']}: {failure['rationale']}")
    return "\n".join(rows)


def next_action(record: dict[str, Any]) -> str:
    """Suggest a bounded action without advancing records or granting permission."""
    state = record["pipeline_state"]
    actions = {
        "QUEUED": "Audit humanitarian relevance and contribution policies using read-only sources.",
        "PROJECT-AUDIT": "Complete the project audit and record evidence before shortlisting an issue.",
        "OPPORTUNITY-RESEARCH": "Verify the issue is current and bound its code surface and regression strategy.",
        "SHORTLISTED": "Prepare a maintainer inquiry; check standing authorization and verify the Humanifest posting identity before sending.",
        "MAINTAINER-CHECK": "Coordinate within standing authorization using the verified Humanifest identity; record current maintainer confirmation.",
        "ENVIRONMENT-READY": "Reproduce with synthetic data in the inspected environment; record results.",
        "REPRODUCED": "Check all hard gates and portfolio capacity before starting the approved bounded implementation.",
        "BUILDING": "Complete the bounded change and regression tests, then prepare adversarial review.",
        "ADVERSARIAL-REVIEW": "Review correctness, scope, security, tests, and maintainer burden before human review.",
        "HUMAN-REVIEW": "Review the change line by line and check PR capacity, standing authorization, and the Humanifest posting identity before opening a PR.",
        "PR-OPEN": "Review upstream feedback; respond and update within standing authorization using the verified Humanifest identity.",
        "MERGED": "Verify release and deployment evidence without assuming that merge proves humanitarian impact.",
        "RELEASED": "Record observed retention and outcomes with sources; do not infer impact from release alone.",
        "PARKED": "Keep parked until the stopping reason is resolved and evidence supports reconsideration.",
        "DECLINED": "Keep declined; do not resume work without a new decision supported by evidence.",
    }
    return actions[state]


def _source_lines(record: dict[str, Any]) -> list[str]:
    return [f"- {source['id']}: {source['url']} (accessed {source['accessed']})" for source in record["sources"]]


def _gate_evidence_lines(record: dict[str, Any]) -> list[str]:
    gates = record.get("gates")
    if not isinstance(gates, dict):
        return []
    lines = []
    for gate in HARD_GATES:
        item = gates.get(gate)
        if (isinstance(item, dict) and item.get("source_ids")
                and not _gate_reference_errors(gate, item, _source_ids(record))):
            lines.append(f"- Gate evidence: {gate} cites {', '.join(item['source_ids'])}")
    return lines


def _require_fields(record: dict[str, Any], fields: list[str], record_name: str) -> list[ValidationIssue]:
    return [ValidationIssue(record_name, f"missing required field: {field}") for field in fields if field not in record]


def _validate_text_fields(record: dict[str, Any], fields: list[str], record_name: str) -> list[ValidationIssue]:
    return [ValidationIssue(record_name, f"{field} must be a non-empty string")
            for field in fields if not isinstance(record.get(field), str) or not record[field].strip()]


def _source_ids(record: dict[str, Any]) -> set[str]:
    sources = record.get("sources")
    if not isinstance(sources, list):
        return set()
    return {source["id"] for source in sources if isinstance(source, dict) and isinstance(source.get("id"), str)}


def _gate_reference_errors(gate: str, item: dict[str, Any], source_ids: set[str]) -> list[str]:
    if "source_ids" not in item:
        if gate == "maintainer_interest_confirmed" and item.get("passed") is True:
            return [f"gate {gate} must cite confirmation evidence in source_ids before passing"]
        return []
    references = item["source_ids"]
    if not isinstance(references, list) or not references:
        return [f"gate {gate}.source_ids must be a non-empty list"]
    errors = []
    seen = set()
    for index, reference in enumerate(references):
        if not isinstance(reference, str) or not reference.strip():
            errors.append(f"gate {gate}.source_ids[{index}] must be a non-empty string")
            continue
        if reference in seen:
            errors.append(f"gate {gate}.source_ids contains duplicate source: {reference}")
        seen.add(reference)
        if reference not in source_ids:
            errors.append(f"gate {gate}.source_ids references unknown source: {reference}")
    return errors


def _validate_sources(record: dict[str, Any], record_name: str) -> list[ValidationIssue]:
    issues = []
    sources = record.get("sources", [])
    if not isinstance(sources, list) or not sources:
        return [ValidationIssue(record_name, "sources must be a non-empty list")]
    seen = set()
    for index, source in enumerate(sources):
        if not isinstance(source, dict):
            issues.append(ValidationIssue(record_name, f"sources[{index}] must be an object"))
            continue
        issues.extend(_validate_text_fields(source, ["id", "url", "accessed"], f"{record_name}: sources[{index}]"))
        source_id = source.get("id")
        if isinstance(source_id, str):
            if source_id in seen:
                issues.append(ValidationIssue(record_name, f"duplicate source id: {source_id}"))
            seen.add(source_id)
        try:
            accessed = source.get("accessed")
            if not isinstance(accessed, str) or date.fromisoformat(accessed).isoformat() != accessed:
                raise ValueError
        except ValueError:
            issues.append(ValidationIssue(record_name, f"sources[{index}].accessed must be a valid YYYY-MM-DD date"))
        try:
            url = source.get("url")
            parsed = urlsplit(url) if isinstance(url, str) else None
            web_url = parsed is not None and parsed.scheme in {"https", "http"} and bool(parsed.hostname)
            local_url = parsed is not None and parsed.scheme == "file" and parsed.netloc in {"", "localhost"} and parsed.path.startswith("/")
            if not (web_url or local_url) or any(c.isspace() for c in url):
                raise ValueError
        except ValueError:
            issues.append(ValidationIssue(record_name, f"sources[{index}].url must be an absolute HTTP(S) or local file URL"))
    return issues


def _validate_evidence_list(items: Any, record_name: str, field: str, source_ids: set[str]) -> list[ValidationIssue]:
    issues = []
    if not isinstance(items, list):
        return [ValidationIssue(record_name, f"{field} must be a list")]
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            issues.append(ValidationIssue(record_name, f"{field}[{index}] must be an object"))
            continue
        evidence_type = item.get("type")
        if not isinstance(evidence_type, str) or evidence_type not in EVIDENCE_TYPES:
            issues.append(ValidationIssue(record_name, f"{field}[{index}].type must be measured, modeled, self_reported, or inferred"))
        issues.extend(_validate_text_fields(item, ["claim", "source_id"], f"{record_name}: {field}[{index}]"))
        source_id = item.get("source_id")
        if isinstance(source_id, str) and source_id not in source_ids:
            issues.append(ValidationIssue(record_name, f"{field}[{index}].source_id references unknown source: {source_id}"))
    return issues


def load_portfolio(root: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[ValidationIssue]]:
    """Collect diagnostics across the portfolio before any report is rendered."""
    issues = []
    collections = []
    for kind, validator in [("projects", validate_project), ("opportunities", validate_opportunity)]:
        directory = root / "portfolio" / kind
        records = []
        seen = set()
        if not directory.is_dir():
            issues.append(ValidationIssue(str(directory), "required record directory is missing"))
        else:
            for path in sorted(directory.glob("*.json")):
                try:
                    record = load_json(path)
                except (OSError, ValueError) as error:
                    issues.append(ValidationIssue(str(path), str(error)))
                    continue
                issues.extend(validator(record, str(path)))
                record_id = record.get("id")
                if isinstance(record_id, str):
                    if record_id in seen:
                        issues.append(ValidationIssue(str(path), f"duplicate {kind} id: {record_id}"))
                    seen.add(record_id)
                records.append((path, record))
        collections.append(records)
    projects, opportunities = collections
    project_ids = {record["id"] for _, record in projects if isinstance(record.get("id"), str)}
    for path, record in opportunities:
        project_id = record.get("project_id")
        if isinstance(project_id, str) and project_id not in project_ids:
            issues.append(ValidationIssue(str(path), f"project_id references unknown project: {project_id}"))
    # Capacity checks require valid IDs and states. Preserve structural errors first.
    if not issues:
        issues.extend(_validate_capacity(projects, opportunities))
    return [record for _, record in projects], [record for _, record in opportunities], issues


def _review_organization(project: dict[str, Any]) -> str | None:
    explicit = project.get("review_organization")
    if explicit:
        return explicit.strip().casefold()
    try:
        repository = urlsplit(project["repository"])
        parts = repository.path.strip("/").split("/")
        if (repository.scheme in {"http", "https"} and repository.hostname == "github.com"
                and not repository.username and not repository.password
                and not repository.query and not repository.fragment
                and len(parts) == 2 and all(parts)
                and not any(char.isspace() for char in project["repository"])):
            return f"github.com/{parts[0].casefold()}"
    except ValueError:
        pass
    return None


def _validate_capacity(
    projects: list[tuple[Path, dict[str, Any]]],
    opportunities: list[tuple[Path, dict[str, Any]]],
) -> list[ValidationIssue]:
    issues = []
    active = [(path, record) for path, record in opportunities if record["pipeline_state"] in ACTIVE_IMPLEMENTATION_STATES]
    open_prs = [(path, record) for path, record in opportunities if record["pipeline_state"] == "PR-OPEN"]
    for records, limit, label in [(active, 1, "active implementations"), (open_prs, 2, "open external PRs")]:
        if len(records) > limit:
            ids = ", ".join(record["id"] for _, record in records)
            for path, _ in records:
                issues.append(ValidationIssue(str(path), f"portfolio limit exceeded: {len(records)} {label} (maximum {limit}): {ids}"))
    by_id = {record["id"]: record for _, record in projects}
    by_organization: dict[str, list[tuple[Path, dict[str, Any]]]] = {}
    for path, record in open_prs:
        project = by_id[record["project_id"]]
        organization = _review_organization(project)
        if organization is None:
            issues.append(ValidationIssue(str(path), f"cannot determine review organization for {project['id']}; set the project's review_organization"))
        else:
            by_organization.setdefault(organization, []).append((path, record))
    for organization, records in sorted(by_organization.items()):
        if len(records) > 1:
            ids = ", ".join(record["id"] for _, record in records)
            for path, _ in records:
                issues.append(ValidationIssue(str(path), f"organization PR limit exceeded for {organization} (maximum 1): {ids}"))
    return issues
