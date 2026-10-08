"""Offline source-review queues derived from validated portfolio records."""

from datetime import date
from typing import Any
from urllib.parse import urlsplit


def source_review(
    projects: list[dict[str, Any]],
    opportunities: list[dict[str, Any]],
    *,
    as_of: date,
    max_age_days: int,
    needs_review_only: bool = False,
    causes: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Keep each source's record context even when URLs appear in multiple records."""
    if isinstance(max_age_days, bool) or not isinstance(max_age_days, int) or max_age_days < 0:
        raise ValueError("max_age_days must be a non-negative integer")
    entries = []
    for kind, records in [("cause", causes or []), ("project", projects), ("opportunity", opportunities)]:
        for record in records:
            for source in record["sources"]:
                age = (as_of - date.fromisoformat(source["accessed"])).days
                reasons = []
                if age < 0:
                    reasons.append("future-date")
                elif age > max_age_days:
                    reasons.append("older-than-window")
                if urlsplit(source["url"]).scheme == "file":
                    reasons.append("local-file")
                entries.append({
                    "record_type": kind,
                    "record_id": record["id"],
                    "source_id": source["id"],
                    "url": source["url"],
                    "accessed": source["accessed"],
                    "age_days": age,
                    "review_reasons": reasons,
                })
    entries.sort(key=lambda entry: (
        not bool(entry["review_reasons"]), entry["accessed"],
        entry["record_type"], entry["record_id"], entry["source_id"],
    ))
    needs_review = sum(bool(entry["review_reasons"]) for entry in entries)
    return {
        "as_of": as_of.isoformat(),
        "max_age_days": max_age_days,
        "scope": "Supplied source dates only; no sources fetched, claims verified, or gates changed.",
        "total_sources": len(entries),
        "sources_needing_review": needs_review,
        "needs_review_only": needs_review_only,
        "sources": [entry for entry in entries if entry["review_reasons"] or not needs_review_only],
    }


def render_source_review(review: dict[str, Any]) -> str:
    rows = [
        "# Source Review", "",
        f"As of: {review['as_of']}",
        f"Review window: {review['max_age_days']} days (inclusive)",
        f"Sources: {review['total_sources']}; needing review: {review['sources_needing_review']}",
        "", review["scope"],
        "Source age is a review reminder, not a measure of truth. Local files may be inaccessible to another reviewer; future dates need checking against the selected as-of date.",
        "",
    ]
    if not review["sources"]:
        rows.append("No sources match this review filter.")
    for entry in review["sources"]:
        status = ", ".join(entry["review_reasons"]) or "within-window"
        rows.extend([
            f"- {entry['record_type']} {entry['record_id']} / {entry['source_id']}: {status}",
            f"  Accessed: {entry['accessed']}; age: {entry['age_days']} days",
            f"  Source: {entry['url']}",
        ])
    return "\n".join(rows)
