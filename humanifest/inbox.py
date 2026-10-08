"""Reconcile bot mentions with a private, read-only GitHub inbox ledger.

This module never posts to GitHub. A notification is only a discovery hint:
decisions are keyed to individual comments and survive read-state changes.
"""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import re
from typing import Any


BOT_LOGIN = "humanifest-bot"
STATUSES = {"reply_needed", "draft_awaiting_authority", "waiting_for_named_event", "no_reply_needed"}
MENTION = re.compile(r"(?<![\w-])@humanifest-bot(?![\w-])", re.IGNORECASE)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def message_key(repository: str, number: int, kind: str, comment_id: int) -> str:
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository):
        raise ValueError("invalid GitHub repository name")
    if number <= 0 or comment_id <= 0 or kind not in {"issue_comment", "review", "review_comment"}:
        raise ValueError("invalid GitHub comment identity")
    return f"{repository.lower()}#{number}:{kind}:{comment_id}"


def empty_ledger() -> dict[str, Any]:
    return {"version": 1, "decisions": {}}


def _timestamp(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (AttributeError, ValueError) as error:
        raise ValueError("invalid inbox timestamp") from error
    if parsed.tzinfo is None:
        raise ValueError("inbox timestamp needs a timezone")
    return parsed.astimezone(timezone.utc)


def _validate_wait_condition(condition: dict[str, Any], repository: str, number: int) -> None:
    if not isinstance(condition, dict) or condition.get("kind") != "new_comment_by_actor":
        raise ValueError("unsupported named wait condition")
    if condition.get("source_url") not in {
        f"https://github.com/{repository}/issues/{number}",
        f"https://github.com/{repository}/pull/{number}",
    }:
        raise ValueError("named wait source must be the tracked thread")
    actors = condition.get("actors")
    if (not isinstance(actors, list) or not actors or len(actors) > 10 or
            any(not isinstance(actor, str) or not re.fullmatch(r"[A-Za-z0-9-]+", actor)
                for actor in actors) or len({actor.lower() for actor in actors}) != len(actors)):
        raise ValueError("named wait needs distinct GitHub actors")
    _timestamp(condition.get("after"))


def validate_ledger(ledger: dict[str, Any]) -> None:
    if not isinstance(ledger, dict) or ledger.get("version") != 1 or not isinstance(ledger.get("decisions"), dict):
        raise ValueError("invalid inbox decision ledger")
    for key, decision in ledger["decisions"].items():
        if not isinstance(decision, dict) or decision.get("key") != key:
            raise ValueError("invalid inbox decision identity")
        if decision.get("status") not in STATUSES or not decision.get("reason"):
            raise ValueError("invalid inbox decision status or reason")
        if decision["status"] == "draft_awaiting_authority" and (
            not decision.get("draft") or not decision.get("authority_gap")
        ):
            raise ValueError("draft awaiting authority requires a draft and exact gap")
        if decision["status"] == "waiting_for_named_event" and not decision.get("wait_event"):
            raise ValueError("waiting requires a named event")
        if decision.get("wait_condition") is not None:
            _validate_wait_condition(decision["wait_condition"], decision["repository"], decision["number"])
        if decision.get("reply_body_sha256") is not None:
            digest = decision["reply_body_sha256"]
            if (not decision.get("bot_reply_url") or not isinstance(digest, str) or
                    not re.fullmatch(r"[0-9a-f]{64}", digest) or
                    not decision.get("reply_coverage_reason") or
                    not isinstance(decision.get("reply_addressed_comment_ids"), list) or
                    decision["comment_id"] not in decision["reply_addressed_comment_ids"]):
                raise ValueError("invalid verified reply coverage")


def _validate_snapshot(snapshot: dict[str, Any]) -> None:
    if not isinstance(snapshot, dict) or snapshot.get("complete") is not True:
        raise ValueError("inbox snapshot is incomplete")
    if not isinstance(snapshot.get("threads"), list):
        raise ValueError("inbox snapshot has no thread list")
    seen_threads: set[tuple[str, int]] = set()
    for thread in snapshot["threads"]:
        if not isinstance(thread, dict):
            raise ValueError("invalid inbox thread")
        repository, number = thread.get("repository"), thread.get("number")
        if not isinstance(repository, str) or type(number) is not int:
            raise ValueError("invalid inbox thread identity")
        message_key(repository, number, "issue_comment", 1)
        identity = (repository.lower(), number)
        if identity in seen_threads or thread.get("kind") not in {"Issue", "PullRequest"}:
            raise ValueError("duplicate or unsupported inbox thread")
        seen_threads.add(identity)
        if not isinstance(thread.get("comments"), list) or not thread.get("subject_api_url"):
            raise ValueError("inbox thread discussion is incomplete")
        seen_comments: set[str] = set()
        for comment in thread["comments"]:
            if not isinstance(comment, dict) or type(comment.get("id")) is not int:
                raise ValueError("invalid inbox comment")
            key = message_key(repository, number, comment.get("kind"), comment["id"])
            if key in seen_comments or not all(isinstance(comment.get(field), str) for field in
                                            ("user", "body", "created_at", "html_url")):
                raise ValueError("duplicate or incomplete inbox comment")
            seen_comments.add(key)


def reconcile(snapshot: dict[str, Any], ledger: dict[str, Any], *, checked_at: str) -> dict[str, Any]:
    """Retain unresolved messages even if notifications are read or unchanged."""
    _validate_snapshot(snapshot)
    validate_ledger(ledger)
    decisions = {key: value.copy() for key, value in ledger["decisions"].items()}
    seen: set[str] = set()
    new: list[str] = []
    for thread in snapshot["threads"]:
        repository, number = thread["repository"], thread["number"]
        comments = sorted(thread["comments"], key=lambda item: (item["created_at"], item["id"]))
        last_bot_at = max((item["created_at"] for item in comments
                           if item["user"].lower() == BOT_LOGIN), default="")
        previous_author = None
        case_id = None
        for comment in comments:
            key = message_key(repository, number, comment["kind"], comment["id"])
            author = comment["user"].lower()
            if author != previous_author:
                case_id = key
            previous_author = author
            if key in decisions:
                seen.add(key)
                decisions[key]["case_id"] = case_id
                decisions[key]["last_seen_at"] = checked_at
                decisions[key]["thread_checked_at"] = checked_at
                continue
            if comment["user"].lower() == BOT_LOGIN:
                continue
            mentioned = bool(MENTION.search(comment["body"]))
            follows_bot = bool(last_bot_at and comment["created_at"] > last_bot_at)
            if not mentioned and not follows_bot:
                continue
            # A later bot comment may address an older mention. Never infer that it
            # did: cold-start ledgers must surface the case for duplicate review.
            reason = ("A later bot comment exists; verify whether it answered this direct mention."
                      if mentioned and comment["created_at"] <= last_bot_at else
                      "Direct mention after the bot's last comment requires an explicit reply decision."
                      if mentioned else
                      "New comment after the bot's last reply requires an explicit follow-up decision.")
            decisions[key] = {
                "key": key,
                "case_id": case_id,
                "repository": repository,
                "number": number,
                "thread_kind": thread["kind"],
                "subject_api_url": thread["subject_api_url"],
                "source_url": comment["html_url"],
                "source_author": comment["user"],
                "source_created_at": comment["created_at"],
                "comment_id": comment["id"],
                "comment_kind": comment["kind"],
                "status": "reply_needed",
                "reason": reason,
                "bot_reply_url": None,
                "first_seen_at": checked_at,
                "last_seen_at": checked_at,
                "thread_checked_at": checked_at,
            }
            seen.add(key)
            new.append(key)
    # Keep prior unresolved decisions even if a later snapshot omits the thread.
    # The run must surface that missing coverage instead of reporting no action.
    pending_messages = [value for value in decisions.values() if value["status"] != "no_reply_needed"]
    missing = [value["key"] for value in pending_messages if value["key"] not in seen]
    pending_messages.sort(key=lambda item: (item["first_seen_at"], item["key"]))
    # Two adjacent mentions from one person can require one substantive answer.
    # Keep both per-comment records while presenting one reply decision.
    cases: dict[tuple[str, str], dict[str, Any]] = {}
    for decision in pending_messages:
        identity = (decision.get("case_id", decision["key"]), decision["status"])
        case = cases.setdefault(identity, {
            "repository": decision["repository"], "number": decision["number"],
            "source_author": decision["source_author"], "status": decision["status"],
            "keys": [], "source_urls": [], "messages": [],
            "thread_checked_at": decision["thread_checked_at"],
        })
        case["keys"].append(decision["key"])
        case["source_urls"].append(decision["source_url"])
        case["messages"].append({
            "key": decision["key"], "reason": decision["reason"],
            "draft": decision.get("draft"), "authority_gap": decision.get("authority_gap"),
            "wait_event": decision.get("wait_event"),
        })
    pending = list(cases.values())
    pending.sort(key=lambda item: (item["repository"], item["number"], item["source_author"], item["status"]))
    threads = {(item["repository"].lower(), item["number"]): item for item in snapshot["threads"]}
    event_candidates = []
    uncheckable_waits = []
    for decision in pending_messages:
        if decision["status"] != "waiting_for_named_event":
            continue
        condition = decision.get("wait_condition")
        if condition is None:
            uncheckable_waits.append(decision["key"])
            continue
        thread = threads.get((decision["repository"].lower(), decision["number"]))
        if thread is None:
            continue
        after = _timestamp(condition["after"])
        actors = {actor.lower() for actor in condition["actors"]}
        for comment in thread["comments"]:
            if comment["user"].lower() in actors and _timestamp(comment["created_at"]) > after:
                event_candidates.append({"key": decision["key"], "event_url": comment["html_url"],
                                         "actor": comment["user"], "created_at": comment["created_at"]})
    legacy_reply_verifications = [item["key"] for item in decisions.values()
                                  if item.get("bot_reply_url") and not item.get("reply_body_sha256")]
    result = {"version": 1, "decisions": decisions}
    validate_ledger(result)
    return {"ledger": result, "new": new, "pending": pending,
            "pending_messages": pending_messages, "missing_from_snapshot": missing,
            "event_candidates": event_candidates, "uncheckable_waits": uncheckable_waits,
            "legacy_reply_verifications": legacy_reply_verifications}


def decide(ledger: dict[str, Any], key: str, *, status: str, reason: str,
           draft: str | None = None, authority_gap: str | None = None,
           wait_event: str | None = None, wait_condition: dict[str, Any] | None = None,
           bot_reply_url: str | None = None, reply_body_sha256: str | None = None,
           reply_addressed_comment_ids: list[int] | None = None,
           reply_coverage_reason: str | None = None,
           decided_at: str | None = None) -> dict[str, Any]:
    """Record an explicit human/operator disposition, never a posting grant."""
    validate_ledger(ledger)
    if key not in ledger["decisions"] or status not in STATUSES or not reason.strip():
        raise ValueError("unknown message or invalid disposition")
    if status == "draft_awaiting_authority" and (not draft or not authority_gap):
        raise ValueError("draft awaiting authority requires a draft and exact gap")
    if status == "waiting_for_named_event":
        if not wait_event or wait_condition is None:
            raise ValueError("waiting requires a named event and checkable condition")
        current = ledger["decisions"][key]
        _validate_wait_condition(wait_condition, current["repository"], current["number"])
    if bot_reply_url and status != "no_reply_needed":
        raise ValueError("a posted reply must close the pending disposition")
    if bot_reply_url and (not reply_body_sha256 or not reply_coverage_reason or
                          not reply_addressed_comment_ids or
                          ledger["decisions"][key]["comment_id"] not in reply_addressed_comment_ids):
        raise ValueError("posted reply needs verified body and explicit source coverage")
    decision = ledger["decisions"][key].copy()
    decision.update(status=status, reason=reason.strip(), draft=draft,
                    authority_gap=authority_gap, wait_event=wait_event,
                    wait_condition=wait_condition, bot_reply_url=bot_reply_url,
                    reply_body_sha256=reply_body_sha256,
                    reply_addressed_comment_ids=reply_addressed_comment_ids,
                    reply_coverage_reason=reply_coverage_reason,
                    decided_at=decided_at or utc_now())
    result = {"version": 1, "decisions": {**ledger["decisions"], key: decision}}
    validate_ledger(result)
    return result


def decide_many(ledger: dict[str, Any], keys: list[str], **kwargs: Any) -> dict[str, Any]:
    """Apply one verified response decision to every comment it addresses."""
    if not keys or len(keys) != len(set(keys)):
        raise ValueError("decision requires unique message keys")
    identities = {ledger["decisions"][key].get("case_id", key) for key in keys}
    if len(identities) != 1:
        raise ValueError("one decision may only cover one contiguous response case")
    if kwargs.get("bot_reply_url") and kwargs.get("reply_addressed_comment_ids") != sorted(
            ledger["decisions"][key]["comment_id"] for key in keys):
        raise ValueError("reply coverage must name the exact source comment IDs")
    result = ledger
    for key in keys:
        result = decide(result, key, **kwargs)
    return result


def posting_blockers(ledger: dict[str, Any], keys: list[str], thread: dict[str, Any], *,
                     draft: str, actor: str, policy: dict[str, Any] | None,
                     authority: dict[str, Any] | None) -> list[str]:
    """Check a proposed reply; an empty list is not permission to post.

    The operator must still establish that the cited policy and authority are
    genuine and verify the bot connection immediately before the actual write.
    """
    validate_ledger(ledger)
    if not keys or len(keys) != len(set(keys)):
        return ["missing_or_duplicate_message_keys"]
    decisions = []
    for key in keys:
        if key not in ledger["decisions"]:
            return ["unknown_message_key"]
        decisions.append(ledger["decisions"][key])
    repository, number = decisions[0]["repository"], decisions[0]["number"]
    blockers: list[str] = []
    if any(item["repository"].lower() != repository.lower() or item["number"] != number
           for item in decisions):
        blockers.append("messages_span_multiple_threads")
    if any(item["status"] == "no_reply_needed" for item in decisions):
        blockers.append("message_already_disposed")
    if actor != BOT_LOGIN:
        blockers.append("wrong_github_actor")
    if not draft.strip():
        blockers.append("missing_specific_reply_draft")
    if thread.get("repository", "").lower() != repository.lower() or thread.get("number") != number:
        blockers.append("wrong_or_unchecked_thread")
    if thread.get("state") != "open" or thread.get("locked") is not False:
        blockers.append("thread_closed_or_locked")
    comments = thread.get("comments")
    if not isinstance(comments, list):
        blockers.append("full_discussion_not_checked")
        comments = []
    by_key = {message_key(repository, number, item["kind"], item["id"]): item for item in comments
              if isinstance(item, dict) and type(item.get("id")) is int and item.get("kind") in
              {"issue_comment", "review", "review_comment"}}
    for item in decisions:
        found = by_key.get(item["key"])
        if not found or found.get("user") != item["source_author"] or found.get("html_url") != item["source_url"]:
            blockers.append("source_message_missing_or_changed")
            break
    earliest = min(item.get("source_created_at", "") for item in decisions)
    if any(item.get("user", "").lower() == BOT_LOGIN and item.get("created_at", "") > earliest
           for item in comments):
        blockers.append("later_bot_comment_requires_duplicate_review")
    if not policy or policy.get("repository", "").lower() != repository.lower() or not policy.get("bot_allowed") or not policy.get("source_url"):
        blockers.append("missing_target_bot_policy_evidence")
    digest = hashlib.sha256(draft.encode("utf-8")).hexdigest()
    if (not authority or authority.get("repository", "").lower() != repository.lower()
            or authority.get("number") != number or authority.get("comment_ids") !=
            sorted(item["comment_id"] for item in decisions)
            or authority.get("body_sha256") != digest or not authority.get("source")):
        blockers.append("missing_exact_target_and_content_authority")
    return blockers
