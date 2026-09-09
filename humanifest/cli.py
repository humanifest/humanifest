"""Command line interface for Humanifest."""

from __future__ import annotations

import argparse
from datetime import date
import json
from pathlib import Path
import sys

from .models import (
    generate_candidate_brief,
    generate_handoff,
    load_json,
    load_portfolio,
    portfolio_report,
    score_opportunity,
    validate_opportunity,
)
from .review import render_source_review, source_review
from .work import render_work_plan, work_plan


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="humanifest", description="Validate and score humanitarian OSS contribution opportunities.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser("validate")
    validate_parser.add_argument("--root", default=".", help="Repository root")

    score_parser = subparsers.add_parser("score")
    score_parser.add_argument("path", help="Opportunity JSON path")

    brief_parser = subparsers.add_parser("brief")
    brief_parser.add_argument("path", help="Opportunity JSON path")

    handoff_parser = subparsers.add_parser("handoff")
    handoff_parser.add_argument("path", help="Opportunity JSON path")
    handoff_parser.add_argument("--target", choices=["codex", "spark", "cursor-red-team"], required=True)

    report_parser = subparsers.add_parser("report")
    report_parser.add_argument("--root", default=".", help="Repository root")

    work_parser = subparsers.add_parser("work", help="List independent work and scheduled reviews without polling upstream")
    work_parser.add_argument("--root", default=".", help="Repository root")
    work_parser.add_argument("--as-of", required=True, type=_date, help="Review date in YYYY-MM-DD form")
    work_parser.add_argument("--format", choices=["markdown", "json"], default="markdown")

    sources_parser = subparsers.add_parser("sources", help="List source access dates and offline review reminders")
    sources_parser.add_argument("--root", default=".", help="Repository root")
    sources_parser.add_argument("--as-of", required=True, type=_date, help="Review date in YYYY-MM-DD form")
    sources_parser.add_argument("--max-age-days", required=True, type=_nonnegative_int, help="Inclusive source-age review window")
    sources_parser.add_argument("--needs-review", action="store_true", help="Only show older sources, future dates, and local files")
    sources_parser.add_argument("--format", choices=["markdown", "json"], default="markdown")

    args = parser.parse_args(argv)

    try:
        if args.command in {"validate", "report", "sources", "work"}:
            projects, opportunities, issues = load_portfolio(Path(args.root))
            if _print_issues(issues):
                return 1
            if args.command == "work":
                plan = work_plan(opportunities, as_of=args.as_of)
                print(json.dumps(plan, indent=2) if args.format == "json" else render_work_plan(plan))
            elif args.command == "sources":
                review = source_review(projects, opportunities, as_of=args.as_of,
                                       max_age_days=args.max_age_days, needs_review_only=args.needs_review)
                print(json.dumps(review, indent=2) if args.format == "json" else render_source_review(review))
            else:
                print("validation ok" if args.command == "validate" else portfolio_report(projects, opportunities))
        else:
            record = load_json(Path(args.path))
            if _print_issues(validate_opportunity(record, args.path)):
                return 1
            if args.command == "score":
                print(json.dumps(score_opportunity(record), indent=2, allow_nan=False))
            elif args.command == "brief":
                print(generate_candidate_brief(record))
            else:
                print(generate_handoff(record, args.target))
    except (OSError, ValueError) as error:
        print(f"humanifest: {error}", file=sys.stderr)
        return 1
    return 0


def _print_issues(issues) -> bool:
    for issue in issues:
        print(f"{issue.record}: {issue.message}", file=sys.stderr)
    return bool(issues)


def _date(value: str) -> date:
    try:
        parsed = date.fromisoformat(value)
        if parsed.isoformat() != value:
            raise ValueError
        return parsed
    except ValueError:
        raise argparse.ArgumentTypeError("must be a valid YYYY-MM-DD date") from None


def _nonnegative_int(value: str) -> int:
    try:
        parsed = int(value)
        if parsed < 0:
            raise ValueError
        return parsed
    except ValueError:
        raise argparse.ArgumentTypeError("must be a non-negative integer") from None


if __name__ == "__main__":
    raise SystemExit(main())
