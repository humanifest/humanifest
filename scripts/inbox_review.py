"""Identity-guarded, read-only GitHub inbox scan with a private decision ledger.

Usage:
  python3 -m scripts.inbox_review scan --live --state /absolute/private/state.json
  python3 -m scripts.inbox_review scan --input fixture.json --state /absolute/private/state.json
  python3 -m scripts.inbox_review decide --input decision.json --state /absolute/private/state.json

There is deliberately no GitHub POST, notification read, or PR command here.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
import tempfile
from typing import Any

from humanifest.inbox import decide_many, empty_ledger, posting_blockers, reconcile, utc_now, validate_ledger


SUBJECT = re.compile(r"https://api\.github\.com/repos/([^/]+/[^/]+)/(issues|pulls)/(\d+)\Z")
REPLY = re.compile(r"https://github\.com/([^/]+/[^/]+)/(?:issues|pull)/(\d+)#issuecomment-(\d+)\Z")
REVIEW_REPLY = re.compile(r"https://github\.com/([^/]+/[^/]+)/pull/(\d+)#pullrequestreview-(\d+)\Z")
INLINE_REPLY = re.compile(r"https://github\.com/([^/]+/[^/]+)/pull/(\d+)#discussion_r(\d+)\Z")
MAX_PAGES = 20


class BotGitHubReader:
    """Read through the existing account-specific identity guard only."""

    def get(self, endpoint: str) -> Any:
        command = [sys.executable, "-m", "scripts.bot_github", "api", "--method", "GET", endpoint]
        result = subprocess.run(command, capture_output=True, text=True, check=False)
        if result.returncode:
            raise RuntimeError("identity-guarded GitHub read failed")
        try:
            return json.loads(result.stdout)
        except ValueError as error:
            raise RuntimeError("GitHub returned invalid JSON") from error

    def pages(self, endpoint: str) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        for page in range(1, MAX_PAGES + 1):
            join = "&" if "?" in endpoint else "?"
            batch = self.get(f"{endpoint}{join}per_page=100&page={page}")
            if not isinstance(batch, list) or not all(isinstance(item, dict) for item in batch):
                raise RuntimeError("GitHub pagination returned an invalid page")
            items.extend(batch)
            if len(batch) < 100:
                return items
        raise RuntimeError("GitHub pagination exceeded the bounded page limit")


def _comment(item: dict[str, Any], kind: str) -> dict[str, Any]:
    user = item.get("user")
    if not isinstance(user, dict):
        raise RuntimeError("GitHub comment has no author")
    return {
        "id": item.get("id"), "kind": kind, "user": user.get("login"),
        "body": item.get("body") or "", "created_at": item.get("created_at"),
        "html_url": item.get("html_url"),
    }


def _identity(subject_api_url: str) -> tuple[str, str, int]:
    match = SUBJECT.fullmatch(subject_api_url)
    if not match:
        raise RuntimeError("unsupported GitHub notification subject")
    repository, route, number = match.groups()
    return repository, "PullRequest" if route == "pulls" else "Issue", int(number)


def fetch_snapshot(reader: BotGitHubReader, ledger: dict[str, Any]) -> dict[str, Any]:
    """Fetch all public issue/PR notifications and every known decision thread."""
    notifications = reader.pages("notifications?all=true")
    subjects: dict[tuple[str, int], dict[str, Any]] = {}
    private_skipped = 0
    for notification in notifications:
        repository = notification.get("repository") or {}
        subject = notification.get("subject") or {}
        if repository.get("private"):
            private_skipped += 1
            continue  # Never put private repository content into this ledger.
        if subject.get("type") not in {"Issue", "PullRequest"}:
            if notification.get("reason") in {"mention", "team_mention", "comment", "review_requested"}:
                raise RuntimeError("actionable GitHub notification has an unsupported subject type")
            continue
        api_url = subject.get("url")
        if not isinstance(api_url, str):
            raise RuntimeError("GitHub notification has no subject URL")
        name, kind, number = _identity(api_url)
        if name.lower() != str(repository.get("full_name", "")).lower() or kind != subject["type"]:
            raise RuntimeError("GitHub notification subject does not match its repository")
        identity = (name.lower(), number)
        subjects[identity] = {
            "repository": name, "number": number, "kind": kind,
            "subject_api_url": api_url,
            "unread": notification.get("unread"),
            "notification_updated_at": notification.get("updated_at"),
        }

    for decision in ledger["decisions"].values():
        identity = (decision["repository"].lower(), decision["number"])
        subjects.setdefault(identity, {
            "repository": decision["repository"], "number": decision["number"],
            "kind": decision["thread_kind"], "subject_api_url": decision["subject_api_url"],
            "unread": None, "notification_updated_at": None,
        })

    threads: list[dict[str, Any]] = []
    for thread in subjects.values():
        repository, number = thread["repository"], thread["number"]
        issue = reader.get(f"repos/{repository}/issues/{number}")
        if not isinstance(issue, dict) or issue.get("state") not in {"open", "closed"}:
            raise RuntimeError("GitHub issue or PR state could not be verified")
        comments = [_comment(item, "issue_comment") for item in
                    reader.pages(f"repos/{repository}/issues/{number}/comments")]
        if thread["kind"] == "PullRequest":
            comments.extend(_comment(item, "review") for item in
                            reader.pages(f"repos/{repository}/pulls/{number}/reviews") if item.get("body"))
            comments.extend(_comment(item, "review_comment") for item in
                            reader.pages(f"repos/{repository}/pulls/{number}/comments"))
        threads.append({**thread, "state": issue["state"], "locked": issue.get("locked"),
                        "comments": comments})
    return {"complete": True, "threads": threads, "notifications_checked": len(notifications),
            "private_notifications_skipped": private_skipped}


def _private_state_path(path: Path) -> Path:
    if not path.is_absolute():
        raise ValueError("inbox state path must be absolute")
    if path == Path("/Users/admin") or Path("/Users/admin") in path.parents or path.is_symlink():
        raise ValueError("inbox state must not access another macOS user's home")
    resolved = path.resolve(strict=False)
    if resolved == Path("/Users/admin") or Path("/Users/admin") in resolved.parents:
        raise ValueError("inbox state must not access another macOS user's home")
    if resolved.is_relative_to(Path(__file__).resolve().parents[1]):
        raise ValueError("inbox state must be outside the source repository")
    return resolved


def load_state(path: Path) -> dict[str, Any]:
    path = _private_state_path(path)
    if not path.exists():
        return empty_ledger()
    mode = path.stat().st_mode
    if not stat.S_ISREG(mode) or mode & 0o077:
        raise ValueError("inbox state must be a private regular file (0600)")
    ledger = json.loads(path.read_text(encoding="utf-8"))
    validate_ledger(ledger)
    return ledger


def save_state(path: Path, ledger: dict[str, Any]) -> None:
    path = _private_state_path(path)
    validate_ledger(ledger)
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd, temporary = tempfile.mkstemp(prefix=".inbox-", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(ledger, stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temporary, 0o600)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def _verify_reply(reader: BotGitHubReader, decision: dict[str, Any], url: str,
                  expected_body: str) -> str:
    match = REPLY.fullmatch(url) or REVIEW_REPLY.fullmatch(url) or INLINE_REPLY.fullmatch(url)
    if not match or match.group(1).lower() != decision["repository"].lower() or int(match.group(2)) != decision["number"]:
        raise ValueError("reply URL does not match the reviewed thread")
    if REPLY.fullmatch(url):
        endpoint = f"repos/{decision['repository']}/issues/comments/{match.group(3)}"
        thread_field, thread_route = "issue_url", "issues"
    elif REVIEW_REPLY.fullmatch(url):
        endpoint = f"repos/{decision['repository']}/pulls/{decision['number']}/reviews/{match.group(3)}"
        thread_field, thread_route = "pull_request_url", "pulls"
    else:
        endpoint = f"repos/{decision['repository']}/pulls/comments/{match.group(3)}"
        thread_field, thread_route = "pull_request_url", "pulls"
    comment = reader.get(endpoint)
    if not isinstance(comment, dict) or comment.get("user", {}).get("login") != "humanifest-bot":
        raise ValueError("reply URL is not verified as humanifest-bot")
    if comment.get("html_url") != url or not str(comment.get(thread_field, "")).endswith(
        f"/{thread_route}/{decision['number']}"):
        raise ValueError("reply URL does not identify this GitHub issue")
    if str(comment.get("created_at", "")) <= decision.get("source_created_at", ""):
        raise ValueError("reply predates the message it is said to answer")
    if not expected_body.strip() or comment.get("body") != expected_body:
        raise ValueError("reply body does not match the reviewed text")
    return hashlib.sha256(expected_body.encode("utf-8")).hexdigest()


def _input_json(path: Path) -> dict[str, Any]:
    raw = sys.stdin.read() if str(path) == "-" else path.read_text(encoding="utf-8")
    value = json.loads(raw)
    if not isinstance(value, dict):
        raise ValueError("input must be a JSON object")
    return value


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["scan", "decide", "preflight"])
    parser.add_argument("--state", required=True, type=Path)
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--live", action="store_true", help="Read through the verified bot GitHub connection")
    source.add_argument("--input", type=Path, help="Read a complete offline snapshot or decision JSON")
    args = parser.parse_args(argv)
    old_umask = os.umask(0o077)
    try:
        ledger = load_state(args.state)
        if args.command == "scan":
            if args.live == bool(args.input):
                raise ValueError("scan requires exactly one of --live or --input")
            snapshot = fetch_snapshot(BotGitHubReader(), ledger) if args.live else _input_json(args.input)
            result = reconcile(snapshot, ledger, checked_at=utc_now())
            save_state(args.state, result["ledger"])
            print(json.dumps({"new": result["new"], "pending": result["pending"],
                              "pending_message_count": len(result["pending_messages"]),
                              "missing_from_snapshot": result["missing_from_snapshot"],
                              "event_candidates": result["event_candidates"],
                              "uncheckable_waits": result["uncheckable_waits"],
                              "legacy_reply_verifications": result["legacy_reply_verifications"],
                              "notifications_checked": snapshot.get("notifications_checked"),
                              "private_notifications_skipped": snapshot.get("private_notifications_skipped")}, indent=2))
        elif args.command == "decide":
            if args.live or not args.input:
                raise ValueError("decide requires --input with one decision JSON")
            payload = _input_json(args.input)
            keys = payload.get("keys", [payload.get("key")])
            if not isinstance(keys, list) or not all(isinstance(key, str) for key in keys):
                raise ValueError("decision requires message keys")
            reply_digest = None
            addressed_ids = payload.get("addressed_comment_ids")
            if payload.get("bot_reply_url"):
                if (not isinstance(payload.get("bot_reply_body"), str) or
                        not isinstance(addressed_ids, list) or
                        addressed_ids != sorted(ledger["decisions"][key]["comment_id"] for key in keys) or
                        not isinstance(payload.get("reply_coverage_reason"), str) or
                        not payload["reply_coverage_reason"].strip()):
                    raise ValueError("posted reply needs exact body, source IDs, and coverage reason")
                reader = BotGitHubReader()
                for key in keys:
                    reply_digest = _verify_reply(reader, ledger["decisions"][key],
                                                 payload["bot_reply_url"], payload["bot_reply_body"])
            updated = decide_many(ledger, keys, status=payload["status"], reason=payload["reason"],
                                  draft=payload.get("draft"), authority_gap=payload.get("authority_gap"),
                                  wait_event=payload.get("wait_event"),
                                  wait_condition=payload.get("wait_condition"),
                                  bot_reply_url=payload.get("bot_reply_url"),
                                  reply_body_sha256=reply_digest,
                                  reply_addressed_comment_ids=addressed_ids,
                                  reply_coverage_reason=payload.get("reply_coverage_reason"))
            save_state(args.state, updated)
            print(json.dumps({"keys": keys, "status": payload["status"],
                              "bot_reply_url": payload.get("bot_reply_url")}))
        else:
            if args.live or not args.input:
                raise ValueError("preflight requires --input with one proposed reply JSON")
            payload = _input_json(args.input)
            reader = BotGitHubReader()
            actor = reader.get("user").get("login")
            snapshot = fetch_snapshot(reader, ledger)
            selected = [item for item in snapshot["threads"] if
                        item["repository"].lower() == payload["repository"].lower()
                        and item["number"] == payload["number"]]
            thread = selected[0] if len(selected) == 1 else {}
            blockers = posting_blockers(ledger, payload["keys"], thread,
                                        draft=payload["draft"], actor=actor,
                                        policy=payload.get("policy"), authority=payload.get("authority"))
            print(json.dumps({"keys": payload["keys"], "draft": payload["draft"],
                              "blockers": blockers, "actor": actor,
                              "note": "An empty blocker list is not posting authorization; verify cited authority and actor again at write time."},
                             indent=2))
            if blockers:
                return 2
    except (OSError, ValueError, KeyError, RuntimeError) as error:
        print(f"inbox review: {error}", file=sys.stderr)
        return 1
    finally:
        os.umask(old_umask)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
