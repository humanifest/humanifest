"""Read-only operator loop for governed Humanifest runs."""

from __future__ import annotations

from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any

from .compute import load_compute_resources, validate_compute_resources
from .finance import load_funding_ledger, validate_funding_ledger
from .models import INACTIVE_STATES, PIPELINE_STATES, load_causes, load_portfolio, next_action, score_cause, score_opportunity
from .review import source_review

FOLLOW_UP_STATES = {"MAINTAINER-CHECK", "PR-OPEN", "MERGED", "RELEASED"}


def operator_snapshot(root: Path, *, as_of: date, max_age_days: int) -> tuple[dict[str, Any], list[Any]]:
    """Return a read-only snapshot plus validation issues.

    This function does not fetch remote sources, mutate records, contact
    maintainers, or inspect target repositories. It is safe for scheduled runs.
    """
    root = root.resolve()
    issues: list[Any] = []
    causes, cause_issues = load_causes(root)
    projects, opportunities, portfolio_issues = load_portfolio(root)
    issues.extend(cause_issues)
    issues.extend(portfolio_issues)

    try:
        funding = load_funding_ledger(root)
        issues.extend(validate_funding_ledger(funding))
    except (OSError, ValueError) as error:
        funding = None
        issues.append(_ad_hoc_issue("portfolio/funding-ledger.json", str(error)))

    try:
        compute = load_compute_resources(root)
        issues.extend(validate_compute_resources(compute))
    except (OSError, ValueError) as error:
        compute = None
        issues.append(_ad_hoc_issue("portfolio/compute-resources.json", str(error)))

    if issues:
        return {}, issues

    review = source_review(projects, opportunities, as_of=as_of, max_age_days=max_age_days,
                           needs_review_only=True, causes=causes)
    cause_scores = sorted(
        [(cause["id"], score_cause(cause)["score"], cause["status"]) for cause in causes
         if cause["status"] != "PARKED"],
        key=lambda item: (-item[1], item[0]),
    )
    opportunity_states = Counter(item["pipeline_state"] for item in opportunities)
    eligible = [item["id"] for item in opportunities if score_opportunity(item)["eligible_for_building"]]
    ready_for_maintainer_check = [
        item["id"] for item in opportunities
        if item["pipeline_state"] in {"SHORTLISTED", "MAINTAINER-CHECK"}
    ]
    source_reviews = [
        {key: entry[key] for key in ("record_type", "record_id", "source_id", "review_reasons")}
        for entry in review["sources"]
    ]
    stale_causes = {entry["record_id"] for entry in source_reviews if entry["record_type"] == "cause"}
    cause_reviews = [
        {"id": cause_id, "status": status, "score": score,
         "sources_need_review": cause_id in stale_causes}
        for cause_id, score, status in cause_scores
    ]
    active_opportunities = sorted(
        opportunities, key=lambda item: (PIPELINE_STATES.index(item["pipeline_state"]), item["id"])
    )
    opportunity_reviews = [
        {"id": item["id"], "project_id": item["project_id"], "state": item["pipeline_state"],
         "failed_gates": [gate["gate"] for gate in score_opportunity(item)["failed_gates"]],
         "next_action": next_action(item)}
        for item in active_opportunities
        if item["pipeline_state"] not in INACTIVE_STATES
        and item["pipeline_state"] not in FOLLOW_UP_STATES
    ]
    follow_up_reviews = [
        {"id": item["id"], "project_id": item["project_id"], "state": item["pipeline_state"],
         "failed_gates": [gate["gate"] for gate in score_opportunity(item)["failed_gates"]],
         "next_action": next_action(item)}
        for item in active_opportunities if item["pipeline_state"] in FOLLOW_UP_STATES
    ]

    actions = []
    if review["sources_needing_review"]:
        actions.append(f"Refresh {review['sources_needing_review']} stale, future-dated, or local-only sources.")
    if cause_scores:
        actions.append(f"Review the top cause pathway: {cause_scores[0][0]}.")
    if ready_for_maintainer_check:
        actions.append(f"Check maintainer responses for {len(ready_for_maintainer_check)} shortlisted or maintainer-check opportunities.")
    if not eligible:
        actions.append("Do not implement yet; no opportunity currently passes every building gate.")
    actions.append("Do not perform external writes without explicit authorization and verified Humanifest identity.")

    return {
        "as_of": as_of.isoformat(),
        "max_age_days": max_age_days,
        "causes": len(causes),
        "projects": len(projects),
        "opportunities": len(opportunities),
        "top_causes": [
            {"id": cause_id, "score": score, "status": status}
            for cause_id, score, status in cause_scores[:5]
        ],
        "opportunity_states": dict(sorted(opportunity_states.items())),
        "sources_needing_review": review["sources_needing_review"],
        "eligible_for_building": sorted(eligible),
        "ready_for_maintainer_check": sorted(ready_for_maintainer_check),
        "finance_steward": funding["fiscal_steward"]["name"] if funding else None,
        "compute_resources": len(compute["resources"]) if compute else 0,
        "work_queue": {
            "source_reviews": source_reviews,
            "cause_reviews": cause_reviews,
            "opportunity_reviews": opportunity_reviews,
            "follow_up_reviews": follow_up_reviews,
        },
        "safe_next_actions": actions,
        "scope": "Read-only work suggestions from supplied records; scores rank discovery attention only. No remote sources fetched, records changed, maintainers contacted, or external writes performed. Gates, portfolio capacity, current upstream status, and authorization require separate review.",
    }, []


def render_operator_snapshot(snapshot: dict[str, Any]) -> str:
    rows = [
        "# Humanifest Operator Loop",
        "",
        f"As of: {snapshot['as_of']}",
        f"Source review window: {snapshot['max_age_days']} days",
        f"Causes: {snapshot['causes']}",
        f"Projects: {snapshot['projects']}",
        f"Opportunities: {snapshot['opportunities']}",
        f"Finance steward: {snapshot['finance_steward']}",
        f"Compute resources: {snapshot['compute_resources']}",
        f"Sources needing review: {snapshot['sources_needing_review']}",
        f"Build-eligible opportunities: {len(snapshot['eligible_for_building'])}",
        "",
        "## Top Causes",
    ]
    if snapshot["top_causes"]:
        rows.extend(f"- {item['id']}: score={item['score']}; status={item['status']}" for item in snapshot["top_causes"])
    else:
        rows.append("- none")
    queue = snapshot["work_queue"]
    rows.extend(["", "## Source Reviews"])
    if queue["source_reviews"]:
        rows.extend(
            f"- {item['record_type']} {item['record_id']} / {item['source_id']}: {', '.join(item['review_reasons'])}"
            for item in queue["source_reviews"]
        )
    else:
        rows.append("- none")
    rows.extend(["", "## Cause Reviews"])
    if queue["cause_reviews"]:
        rows.extend(
            f"- {item['id']}: score={item['score']}; status={item['status']}; sources need review={item['sources_need_review']}"
            for item in queue["cause_reviews"]
        )
    else:
        rows.append("- none")
    rows.extend(["", "## Opportunity Reviews"])
    if queue["opportunity_reviews"]:
        for item in queue["opportunity_reviews"]:
            rows.append(f"- {item['id']} ({item['project_id']}): {item['state']}; failed gates: {', '.join(item['failed_gates']) or 'none'}")
            rows.append(f"  Next: {item['next_action']}")
    else:
        rows.append("- none")
    rows.extend(["", "## Follow-up Reviews"])
    if queue["follow_up_reviews"]:
        for item in queue["follow_up_reviews"]:
            rows.append(f"- {item['id']} ({item['project_id']}): {item['state']}; failed gates: {', '.join(item['failed_gates']) or 'none'}")
            rows.append(f"  Next: {item['next_action']}")
    else:
        rows.append("- none")
    rows.extend(["", "## Opportunity States"])
    if snapshot["opportunity_states"]:
        rows.extend(f"- {state}: {count}" for state, count in snapshot["opportunity_states"].items())
    else:
        rows.append("- none")
    rows.extend(["", "## Safe Next Actions"])
    rows.extend(f"- {action}" for action in snapshot["safe_next_actions"])
    rows.extend(["", f"Scope: {snapshot['scope']}"])
    return "\n".join(rows)


def _ad_hoc_issue(record: str, message: str):
    class Issue:
        def __init__(self, record: str, message: str):
            self.record = record
            self.message = message

    return Issue(record, message)
