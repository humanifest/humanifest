"""Command line interface for Humanifest."""

from __future__ import annotations

import argparse
from datetime import date
import json
from pathlib import Path
import sys

from .compute import compute_report, load_compute_resources, validate_compute_resources
from .finance import finance_report, load_funding_ledger, validate_funding_ledger
from .models import (
    cause_report,
    generate_candidate_brief,
    generate_handoff,
    load_causes,
    load_json,
    load_portfolio,
    portfolio_report,
    score_cause,
    score_opportunity,
    validate_cause,
    validate_opportunity,
)
from .review import render_source_review, source_review
from .correspondence import load_projection
from .workflow import HANDOFF_ROUTES


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="humanifest", description="Validate and score humanitarian OSS contribution opportunities.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser("validate")
    validate_parser.add_argument("--root", default=".", help="Repository root")

    causes_parser = subparsers.add_parser("causes", help="Validate and summarize cause-area discovery records")
    causes_parser.add_argument("--root", default=".", help="Repository root")
    causes_parser.add_argument("--format", choices=["markdown", "json"], default="markdown")

    cause_score_parser = subparsers.add_parser("cause-score")
    cause_score_parser.add_argument("path", help="Cause-area JSON path")

    score_parser = subparsers.add_parser("score")
    score_parser.add_argument("path", help="Opportunity JSON path")

    brief_parser = subparsers.add_parser("brief")
    brief_parser.add_argument("path", help="Opportunity JSON path")

    handoff_parser = subparsers.add_parser("handoff")
    handoff_parser.add_argument("path", help="Opportunity JSON path")
    handoff_parser.add_argument("--root", help="Authoritative portfolio root; inferred from portfolio/opportunities otherwise")
    handoff_parser.add_argument("--target", choices=list(HANDOFF_ROUTES), required=True)

    report_parser = subparsers.add_parser("report")
    report_parser.add_argument("--root", default=".", help="Repository root")

    finance_parser = subparsers.add_parser("finance", help="Validate and summarize the public funding ledger")
    finance_parser.add_argument("--root", default=".", help="Repository root")

    compute_parser = subparsers.add_parser("compute", help="Validate and summarize the public compute-resource registry")
    compute_parser.add_argument("--root", default=".", help="Repository root")

    sources_parser = subparsers.add_parser("sources", help="List source access dates and offline review reminders")
    sources_parser.add_argument("--root", default=".", help="Repository root")
    sources_parser.add_argument("--as-of", required=True, type=_date, help="Review date in YYYY-MM-DD form")
    sources_parser.add_argument("--max-age-days", required=True, type=_nonnegative_int, help="Inclusive source-age review window")
    sources_parser.add_argument("--needs-review", action="store_true", help="Only show older sources, future dates, and local files")
    sources_parser.add_argument("--format", choices=["markdown", "json"], default="markdown")

    args = parser.parse_args(argv)

    try:
        if args.command == "compute":
            resources = load_compute_resources(Path(args.root))
            if _print_issues(validate_compute_resources(resources)):
                return 1
            print(compute_report(resources))
        elif args.command == "finance":
            ledger = load_funding_ledger(Path(args.root))
            if _print_issues(validate_funding_ledger(ledger)):
                return 1
            print(finance_report(ledger))
        elif args.command == "causes":
            causes, issues = load_causes(Path(args.root))
            if _print_issues(issues):
                return 1
            if args.format == "json":
                print(json.dumps([{**cause, "discovery_score": score_cause(cause)} for cause in causes],
                                 indent=2, allow_nan=False))
            else:
                print(cause_report(causes))
        elif args.command == "cause-score":
            record = load_json(Path(args.path))
            if _print_issues(validate_cause(record, args.path)):
                return 1
            print(json.dumps(score_cause(record), indent=2, allow_nan=False))
        elif args.command in {"validate", "report", "sources"}:
            projects, opportunities, issues = load_portfolio(Path(args.root))
            if _print_issues(issues):
                return 1
            if args.command == "sources":
                review = source_review(projects, opportunities, as_of=args.as_of,
                                       max_age_days=args.max_age_days, needs_review_only=args.needs_review)
                print(json.dumps(review, indent=2) if args.format == "json" else render_source_review(review))
            elif args.command == "validate":
                print("validation ok")
            else:
                causes, cause_issues = load_causes(Path(args.root), require_directory=False)
                if _print_issues(cause_issues):
                    return 1
                projection = load_projection(Path(args.root))
                print(portfolio_report(projects, opportunities, causes=causes, guidance=projection.guidance))
        else:
            record = load_json(Path(args.path))
            if _print_issues(validate_opportunity(record, args.path)):
                return 1
            if args.command == "score":
                print(json.dumps(score_opportunity(record), indent=2, allow_nan=False))
            elif args.command == "brief":
                print(generate_candidate_brief(record))
            else:
                path = Path(args.path).resolve()
                root = Path(args.root).resolve() if args.root else path.parent.parent.parent
                _, _, issues = load_portfolio(root)
                if _print_issues(issues):
                    return 1
                if path.parent != root / "portfolio/opportunities":
                    raise ValueError("handoff must use its exact current portfolio record")
                projection = load_projection(root)
                print(generate_handoff(record, args.target, guidance=projection.guidance[record["id"]],
                                       route=projection.handoff_routes[args.target]))
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
