from contextlib import redirect_stdout
import hashlib
from io import StringIO
import json
import os
from pathlib import Path
import tempfile
import unittest

from humanifest.inbox import decide_many, empty_ledger, posting_blockers, reconcile
from scripts.inbox_review import _verify_reply, fetch_snapshot, load_state, main, save_state


REPO = "kobotoolbox/kpi"
SUBJECT = "https://api.github.com/repos/kobotoolbox/kpi/issues/7259"
REPLY_URL = "https://github.com/kobotoolbox/kpi/issues/7259#issuecomment-6046366481"
REPLY_BODY = "@RuneO We will leave docs to the Kobo team."


def comment(comment_id, user, body, created_at):
    return {"id": comment_id, "kind": "issue_comment", "user": user, "body": body,
            "created_at": created_at,
            "html_url": f"https://github.com/kobotoolbox/kpi/issues/7259#issuecomment-{comment_id}"}


def kobo_snapshot(*, replied=False):
    comments = [
        comment(5593643546, "humanifest-bot", "Would a frozen-time test be welcome?", "2026-09-09T00:02:57Z"),
        comment(5600432460, "RuneO", "Thanks @humanifest-bot. A same-second test is welcome.",
                "2026-09-09T10:32:47Z"),
        comment(5600507492, "RuneO", "NB @humanifest-bot: I will handle docs after Kobo-team direction.",
                "2026-09-09T10:39:22Z"),
    ]
    if replied:
        comments.append(comment(6046366481, "humanifest-bot", REPLY_BODY,
                                "2026-10-07T20:36:09Z"))
    return {"complete": True, "notifications_checked": 1, "threads": [{
        "repository": REPO, "number": 7259, "kind": "Issue", "subject_api_url": SUBJECT,
        "unread": False, "notification_updated_at": "2026-09-09T10:39:22Z",
        "comments": comments,
    }]}


class FakeReader:
    def __init__(self, reply=None):
        self.reply = reply

    def get(self, endpoint):
        if endpoint.endswith("issues/comments/6046366481"):
            return self.reply
        if endpoint.endswith("issues/7259"):
            return {"state": "open", "locked": False}
        raise AssertionError(endpoint)

    def pages(self, endpoint):
        if endpoint == "notifications?all=true":
            return [{"repository": {"full_name": REPO, "private": False},
                     "subject": {"type": "Issue", "url": SUBJECT},
                     "unread": False, "updated_at": "2026-09-09T10:39:22Z"}]
        if endpoint.endswith("issues/7259/comments"):
            return [{"id": item["id"], "user": {"login": item["user"]},
                     "body": item["body"], "created_at": item["created_at"],
                     "html_url": item["html_url"]} for item in kobo_snapshot()["threads"][0]["comments"]]
        raise AssertionError(endpoint)


class InboxTests(unittest.TestCase):
    def test_kobo_read_thread_persists_one_case_until_verified_reply(self):
        first = reconcile(kobo_snapshot(), empty_ledger(), checked_at="2026-10-01T14:00:00Z")
        self.assertEqual(len(first["new"]), 2)
        self.assertEqual(len(first["ledger"]["decisions"]), 2)
        self.assertEqual(len(first["pending"]), 1)
        self.assertEqual(len(first["pending"][0]["keys"]), 2)

        next_day = reconcile(kobo_snapshot(), first["ledger"], checked_at="2026-10-02T14:00:00Z")
        self.assertEqual(next_day["new"], [])
        self.assertEqual(len(next_day["pending"]), 1)
        self.assertEqual(next_day["pending"][0]["keys"], first["pending"][0]["keys"])

        reply = {"user": {"login": "humanifest-bot"}, "html_url": REPLY_URL,
                 "issue_url": SUBJECT, "created_at": "2026-10-07T20:36:09Z", "body": REPLY_BODY}
        for key in next_day["pending"][0]["keys"]:
            _verify_reply(FakeReader(reply), next_day["ledger"]["decisions"][key], REPLY_URL, REPLY_BODY)
        with self.assertRaisesRegex(ValueError, "exact source comment IDs"):
            decide_many(next_day["ledger"], next_day["pending"][0]["keys"],
                        status="no_reply_needed", reason="Incorrectly mapped reply.",
                        bot_reply_url=REPLY_URL,
                        reply_body_sha256=hashlib.sha256(REPLY_BODY.encode()).hexdigest(),
                        reply_addressed_comment_ids=[5600507492],
                        reply_coverage_reason="Missing one source comment.")
        closed = decide_many(next_day["ledger"], next_day["pending"][0]["keys"],
                             status="no_reply_needed", reason="Verified bot response addressed both mentions.",
                             bot_reply_url=REPLY_URL,
                             reply_body_sha256=hashlib.sha256(REPLY_BODY.encode()).hexdigest(),
                             reply_addressed_comment_ids=[5600432460, 5600507492],
                             reply_coverage_reason="One reply addresses the test scope and documentation deferral.",
                             decided_at="2026-10-07T20:37:00Z")
        after_reply = reconcile(kobo_snapshot(replied=True), closed, checked_at="2026-10-08T14:00:00Z")
        self.assertEqual(after_reply["new"], [])
        self.assertEqual(after_reply["pending"], [])
        self.assertEqual({item["bot_reply_url"] for item in after_reply["ledger"]["decisions"].values()},
                         {REPLY_URL})
        self.assertEqual(after_reply["legacy_reply_verifications"], [])

    def test_live_reader_fetches_already_read_and_full_comments(self):
        snapshot = fetch_snapshot(FakeReader(), empty_ledger())
        self.assertTrue(snapshot["complete"])
        self.assertFalse(snapshot["threads"][0]["unread"])
        self.assertEqual(len(snapshot["threads"][0]["comments"]), 3)
        self.assertEqual(len(reconcile(snapshot, empty_ledger(), checked_at="2026-10-07T14:00:00Z")["pending"]), 1)

    def test_cold_start_after_bot_reply_still_requires_explicit_disposition(self):
        result = reconcile(kobo_snapshot(replied=True), empty_ledger(), checked_at="2026-10-08T14:00:00Z")
        self.assertEqual(len(result["pending"]), 1)
        self.assertEqual(len(result["pending"][0]["keys"]), 2)
        self.assertTrue(all("later bot comment" in item["reason"] for item in result["pending_messages"]))

    def test_followup_without_handle_after_bot_reply_gets_own_decision(self):
        snapshot = kobo_snapshot(replied=True)
        snapshot["threads"][0]["comments"].append(
            comment(6046366500, "RuneO", "The frozen-time test should cover the next second too.",
                    "2026-10-07T21:00:00Z"))
        result = reconcile(snapshot, empty_ledger(), checked_at="2026-10-08T14:00:00Z")
        key = "kobotoolbox/kpi#7259:issue_comment:6046366500"
        self.assertIn(key, result["ledger"]["decisions"])
        self.assertIn("follow-up decision", result["ledger"]["decisions"][key]["reason"])

    def test_separated_comments_from_one_author_are_different_cases(self):
        snapshot = kobo_snapshot()
        snapshot["threads"][0]["comments"].extend([
            comment(5600507493, "OtherReviewer", "Can we see a regression?", "2026-09-09T11:00:00Z"),
            comment(5600507494, "RuneO", "A later, separate question.", "2026-09-10T11:00:00Z"),
        ])
        result = reconcile(snapshot, empty_ledger(), checked_at="2026-10-01T14:00:00Z")
        rune_cases = [case for case in result["pending"] if case["source_author"] == "RuneO"]
        self.assertEqual(sorted(len(case["keys"]) for case in rune_cases), [1, 2])
        with self.assertRaisesRegex(ValueError, "contiguous response case"):
            decide_many(result["ledger"], [rune_cases[0]["keys"][0], rune_cases[1]["keys"][0]],
                        status="no_reply_needed", reason="Conflated")

    def test_settled_thread_is_refetched_without_notification(self):
        first = reconcile(kobo_snapshot(), empty_ledger(), checked_at="2026-10-01T14:00:00Z")
        keys = first["pending"][0]["keys"]
        settled = decide_many(first["ledger"], keys, status="no_reply_needed",
                              reason="Already answered elsewhere.")

        class SilentReader(FakeReader):
            def pages(self, endpoint):
                if endpoint == "notifications?all=true":
                    return []
                if endpoint.endswith("issues/7259/comments"):
                    items = kobo_snapshot(replied=True)["threads"][0]["comments"]
                    items.append(comment(6046366500, "RuneO", "Please check this new edge case.",
                                         "2026-10-07T21:00:00Z"))
                    return [{"id": item["id"], "user": {"login": item["user"]},
                             "body": item["body"], "created_at": item["created_at"],
                             "html_url": item["html_url"]} for item in items]
                return super().pages(endpoint)

        snapshot = fetch_snapshot(SilentReader(), settled)
        self.assertEqual(snapshot["notifications_checked"], 0)
        again = reconcile(snapshot, settled, checked_at="2026-10-08T14:00:00Z")
        self.assertEqual(again["new"], ["kobotoolbox/kpi#7259:issue_comment:6046366500"])
        self.assertEqual(len(again["pending"]), 1)

    def test_named_wait_surfaces_new_actor_comment_and_legacy_gap(self):
        first = reconcile(kobo_snapshot(), empty_ledger(), checked_at="2026-10-01T14:00:00Z")
        keys = first["pending"][0]["keys"]
        condition = {"kind": "new_comment_by_actor", "actors": ["teolemon"],
                     "after": "2026-10-01T14:00:00Z",
                     "source_url": "https://github.com/kobotoolbox/kpi/issues/7259"}
        waiting = decide_many(first["ledger"], keys, status="waiting_for_named_event",
                              reason="Awaiting maintainer direction.", wait_event="teolemon replies",
                              wait_condition=condition)
        unchanged = reconcile(kobo_snapshot(), waiting, checked_at="2026-10-02T14:00:00Z")
        self.assertEqual(unchanged["event_candidates"], [])
        with_event = kobo_snapshot()
        with_event["threads"][0]["comments"].append(
            comment(6046366500, "teolemon", "Please test one more case.", "2026-10-03T14:00:00Z"))
        found = reconcile(with_event, waiting, checked_at="2026-10-04T14:00:00Z")
        self.assertEqual({item["key"] for item in found["event_candidates"]}, set(keys))
        self.assertEqual(len(found["pending"]), 2)  # The wait and the new comment remain reviewable.
        legacy = {"version": 1, "decisions": {key: value.copy() for key, value in waiting["decisions"].items()}}
        for value in legacy["decisions"].values():
            value.pop("wait_condition")
        self.assertEqual(set(reconcile(kobo_snapshot(), legacy,
                                       checked_at="2026-10-05T14:00:00Z")["uncheckable_waits"]), set(keys))

    def test_authority_draft_requires_specific_gap_and_unseen_case_remains_visible(self):
        result = reconcile(kobo_snapshot(), empty_ledger(), checked_at="2026-10-01T14:00:00Z")
        key = result["pending"][0]["keys"][0]
        with self.assertRaisesRegex(ValueError, "draft and exact gap"):
            decide_many(result["ledger"], [key], status="draft_awaiting_authority",
                        reason="Needs posting authority", draft="Specific reply")
        updated = decide_many(result["ledger"], [key], status="draft_awaiting_authority",
                              reason="Needs posting authority", draft="Specific reply",
                              authority_gap="User approval for Kobo #7259")
        unseen = reconcile({"complete": True, "threads": []}, updated, checked_at="2026-10-02T14:00:00Z")
        self.assertIn(key, unseen["missing_from_snapshot"])
        self.assertEqual(len(unseen["pending"]), 2)  # One draft, one unresolved mention.
        draft_case = next(item for item in unseen["pending"] if item["status"] == "draft_awaiting_authority")
        self.assertEqual(draft_case["messages"][0]["draft"], "Specific reply")
        self.assertEqual(draft_case["messages"][0]["authority_gap"], "User approval for Kobo #7259")

    def test_bad_snapshot_and_unverified_actor_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "incomplete"):
            reconcile({"complete": False, "threads": []}, empty_ledger(), checked_at="2026-10-01T14:00:00Z")
        result = reconcile(kobo_snapshot(), empty_ledger(), checked_at="2026-10-01T14:00:00Z")
        key = result["pending"][0]["keys"][0]
        with self.assertRaisesRegex(ValueError, "not verified"):
            _verify_reply(FakeReader({"user": {"login": "roryscot"}, "html_url": REPLY_URL,
                                      "issue_url": SUBJECT, "created_at": "2026-10-07T20:36:09Z",
                                      "body": REPLY_BODY}),
                          result["ledger"]["decisions"][key], REPLY_URL, REPLY_BODY)
        with self.assertRaisesRegex(ValueError, "reply body"):
            _verify_reply(FakeReader({"user": {"login": "humanifest-bot"}, "html_url": REPLY_URL,
                                      "issue_url": SUBJECT, "created_at": "2026-10-07T20:36:09Z",
                                      "body": "Different reply"}),
                          result["ledger"]["decisions"][key], REPLY_URL, REPLY_BODY)

    def test_preflight_requires_exact_authority_policy_and_no_later_bot_comment(self):
        result = reconcile(kobo_snapshot(), empty_ledger(), checked_at="2026-10-01T14:00:00Z")
        keys = result["pending"][0]["keys"]
        thread = {**kobo_snapshot()["threads"][0], "state": "open", "locked": False}
        draft = "We will focus on the same-second regression and defer docs."
        self.assertEqual(posting_blockers(result["ledger"], keys, thread, draft=draft,
                                          actor="humanifest-bot", policy=None, authority=None),
                         ["missing_target_bot_policy_evidence", "missing_exact_target_and_content_authority"])
        policy = {"repository": REPO, "bot_allowed": True,
                  "source_url": "https://github.com/kobotoolbox/kpi/blob/main/CONTRIBUTING.md"}
        authority = {"repository": REPO, "number": 7259,
                     "comment_ids": [5600432460, 5600507492],
                     "body_sha256": hashlib.sha256(draft.encode()).hexdigest(),
                     "source": "one-off user authorization for the exact Kobo reply"}
        self.assertEqual(posting_blockers(result["ledger"], keys, thread, draft=draft,
                                          actor="humanifest-bot", policy=policy, authority=authority), [])
        after = {**kobo_snapshot(replied=True)["threads"][0], "state": "open", "locked": False}
        self.assertIn("later_bot_comment_requires_duplicate_review",
                      posting_blockers(result["ledger"], keys, after, draft=draft,
                                       actor="humanifest-bot", policy=policy, authority=authority))
        self.assertIn("wrong_github_actor",
                      posting_blockers(result["ledger"], keys, thread, draft=draft,
                                       actor="roryscot", policy=policy, authority=authority))

    def test_cli_persists_private_state_without_network(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            state, source = root / "inbox-state.json", root / "snapshot.json"
            source.write_text(json.dumps(kobo_snapshot()), encoding="utf-8")
            output = StringIO()
            with redirect_stdout(output):
                self.assertEqual(main(["scan", "--input", str(source), "--state", str(state)]), 0)
            self.assertEqual(len(json.loads(output.getvalue())["pending"]), 1)
            self.assertEqual(len(load_state(state)["decisions"]), 2)
            self.assertEqual(os.stat(state).st_mode & 0o777, 0o600)
            before = state.read_bytes()
            source.write_text('{"complete": false, "threads": []}', encoding="utf-8")
            self.assertEqual(main(["scan", "--input", str(source), "--state", str(state)]), 1)
            self.assertEqual(state.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
