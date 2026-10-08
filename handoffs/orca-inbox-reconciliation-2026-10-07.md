# Orca handoff: message-level GitHub inbox decisions

Original user request: keep a durable repository/thread/comment disposition;
reopen unresolved mentions despite read or unchanged notifications; require a
decision for every direct mention after the bot's last reply; gate posting by
full-thread duplicate, policy, exact authority, and verified bot identity; and
regress Kobo #7259's two RuneO mentions before and after the verified bot reply.

Controlling files: `AGENTS.md`, `GOALS.md`, `docs/contribution-protocol.md`,
`docs/model-routing.md`, `docs/github-identity.md`,
`docs/bot-operator-runbook.md`, and the current Kobo opportunity record.
The user authorized a reversible implementation and local fixture tests. No
blanket authority to post other GitHub replies was created.

Implemented locally in `humanifest/inbox.py`, `scripts/inbox_review.py`,
`tests/test_inbox.py`, and `docs/github-inbox-reconciliation.md`. The scanner
uses the existing `scripts.bot_github` identity guard, reads all public issue/PR
notifications and full comment surfaces, persists a private state file outside
the repository, includes follow-up comments after the bot's last reply even
without an explicit handle, and groups adjacent mentions into one response
case. It has no GitHub write operation. The posting preflight is read-only and
fail-closed;
operator-supplied policy or authority fields remain claims to verify, not an
approval mechanism. The GitHub Actions operator workflow is unchanged.

Observed on 2026-10-07: first live scan found both RuneO mentions as one pending
case. The existing [bot reply](https://github.com/kobotoolbox/kpi/issues/7259#issuecomment-6046366481)
was re-fetched, actor/thread/time verified, and recorded for both message IDs.
A second live scan yielded zero pending or new cases. Focused offline tests
exercise the read notification, unchanged next day, cold start after reply,
private state, authority/policy blockers, and no duplicate after verified reply.

After including follow-up comments that omit the handle, the live scan found
four messages on [Open Food Facts PR #504](https://github.com/openfoodfacts/openfoodfacts-python/pull/504).
The two author comments are recorded as waiting for named maintainer direction
or a new direct request. TaciteOFF's question was answered by the author, and
the SonarQube report was automated; both have reasoned no-reply decisions.
The repeat scan found zero new messages and one persistent named-wait case.
No reply was posted. The focused fixture suite passed 8 tests.

Follow-on implementation, 2026-10-07: response cases now use contiguous
comment runs, so the two separated author comments on Open Food Facts PR #504
are distinct cases. The scanner refetches all tracked threads, including those
whose prior messages were settled and whose notifications disappear. New reply
receipts require the exact GitHub body, its SHA-256 digest, the addressed source
comment IDs, and an explicit coverage reason. A named wait now requires a
same-thread actor-and-time condition; matches are surfaced for review, not
automatically resolved. The scanner flags older receipts and free-text waits
until upgraded.

The existing private ledger was upgraded without clearing its dispositions.
The two Open Food Facts waits now watch named reviewer or maintainer comments
after the recorded decision time. The existing Kobo reply was fetched through
the guarded bot connection, and its actor, thread, timestamp, exact body, and
coverage of the two RuneO messages were verified. A repeat live scan reported
zero new messages, zero event candidates, zero uncheckable waits, and zero
legacy reply verifications; it retained two separate named-wait cases. The
focused fixture suite passed 11 tests. No GitHub write was made.

The existing daily heartbeat automation
`humanifest-contribution-and-github-inbox-cycle` was updated in the app and
verified ACTIVE, attached to this chat. Its prompt now requires the private
ledger scan, explicit disposition of each pending message, and the separate
posting checks. This activates the scheduled instruction; a future scheduled
run has not yet been observed under the updated prompt. No new GitHub comment
was posted by this implementation.
The prompt was also updated to require review of event candidates, conversion
of legacy waits, and verification of old reply receipts. Its ACTIVE status and
chat attachment were verified, but the next scheduled execution remains
unobserved.

Orca/source-of-truth review remains required for the operator-loop and
automation-boundary change under `docs/model-routing.md`. Check the current
diff, private-state location and permissions, target-policy interpretation,
and scheduled prompt before acceptance. Do not grant broader posting authority
or add a write token to GitHub Actions. If Orca is unavailable, record that gap
without treating this handoff as accepted work.
