# GitHub inbox reconciliation

The scheduled Humanifest chat reviews the `humanifest-bot` GitHub inbox before
choosing contribution work. The local operator loop and GitHub Actions workflow
remain read-only. The inbox scanner is also read-only on GitHub: it uses
`scripts.bot_github` for identity-guarded GET requests and never posts, marks a
notification read, or opens a PR.

## Daily scan

Run with Legion's intentional umask 077:

```bash
python3 -m scripts.inbox_review scan --live \
  --state /Users/legion/Documents/Codex/Humanifest/inbox-state.json
```

The state file is local, private (0600), atomic, and outside the public source
repository. It records repository, thread, comment identity, source URL,
disposition, reason, draft or blocker when present, and verified bot reply URL.
It does not store fetched comment bodies or unrelated private notifications.
Do not copy this file into the repository or publish it. An incomplete fetch,
identity failure, unsupported actionable subject, or pagination cap fails the
scan without replacing the previous state. Report the failure; do not treat the
inbox as empty.

The scan requests all notifications, including already-read ones, and fetches
full issue comments plus PR issue comments, reviews, and inline review comments.
It also rechecks every tracked thread, including settled ones, when GitHub no
longer returns a notification. Read status and `updated_at` never clear a
pending mention. Each direct `@humanifest-bot` mention receives a message-keyed
disposition. Only contiguous comments from one author form one response case;
separate exchanges stay separate even when the author and status match. A
comment after the bot's last reply also gets a decision when it omits the
handle. A cold start after a bot comment still surfaces older mentions for
duplicate review instead of assuming the comment answered them.

## Required decision

For each pending response case, read every listed source comment and the full
thread. Then record one of:

- `reply_needed`: a specific response is needed; it is not posting authority.
- `draft_awaiting_authority`: include the exact proposed reply and the missing
  target/content authorization or policy evidence.
- `waiting_for_named_event`: name the event and give a checkable condition.
  Currently supported: a new comment by one of the named GitHub actors after
  a recorded timestamp on the same issue or PR. The scanner reports matches
  as `event_candidates`; it does not interpret their meaning or close the wait.
- `no_reply_needed`: give a concrete reason. When a bot reply was posted, include
  its URL and exact body; the command verifies actor, thread, time, and body.
  Record which source comment IDs it addresses and why the text covers them.

Supply a decision JSON on stdin, so draft text need not appear in shell
arguments. One decision may cover multiple contiguous comments by the same
author in one thread:

```bash
python3 -m scripts.inbox_review decide \
  --state /Users/legion/Documents/Codex/Humanifest/inbox-state.json \
  --input -
```

The JSON has `keys` (the scan's message keys), `status`, and `reason`.
`draft_awaiting_authority` also requires `draft` and `authority_gap`;
`waiting_for_named_event` requires `wait_event` and `wait_condition`:

```json
{"kind":"new_comment_by_actor","actors":["teolemon","hangy"],"after":"2026-10-07T21:49:07Z","source_url":"https://github.com/openfoodfacts/openfoodfacts-python/pull/504"}
```

Use an `after` timestamp at or after the decision, so old comments do not
trigger the wait. The scan reports `uncheckable_waits` for older free-text waits
until they are converted. A posted reply uses `no_reply_needed` plus
`bot_reply_url`, `bot_reply_body` (the exact fetched text), sorted
`addressed_comment_ids`, and a specific `reply_coverage_reason`. The ledger
stores the body's SHA-256 digest and the source IDs, not the reply body. Older
reply receipts lacking this verification appear in
`legacy_reply_verifications`; recheck them before relying on closure. A
`no_reply_needed` decision without a reply URL must explain why no message
should be sent. Do not use a generic acknowledgment to clear a case. If a
later bot comment appears, inspect whether it addressed the source; the
scanner does not infer that from chronology.

## Posting boundary

No scanner command posts. Before a separately authorized manual comment, check
the full current discussion for a later bot comment or duplicate, target AI/bot
policy, the exact target and content authority, issue/PR state, and the actor on
the **same** connection that will write. `preflight --input proposal.json`
performs a conservative, read-only check and reports blockers and the proposed
text. Its policy and authority evidence are operator-supplied; an empty blocker
list is not approval. The proposal JSON contains `repository`, `number`,
`keys`, `draft`, and separate `policy` and `authority` objects. Policy needs
`repository`, `bot_allowed`, and `source_url`. Authority needs `repository`,
`number`, sorted `comment_ids`, `body_sha256` of the exact draft, and `source`.
The operator must verify those sources and use only current, narrow authority.
Immediately before any write, re-fetch the thread and verify `humanifest-bot`
again via `scripts.bot_github`. After posting, verify the returned URL, actor,
body, and time, then record the reply against every addressed source comment.

The only standing follow-up authority in the contribution protocol is the
bounded CHT #10155 scope. It does not cover other notifications. A direct user
instruction for a named reply can provide one-off authority for that reply;
unattended posting elsewhere needs a separate reviewable authority record per
`docs/model-routing.md`. If authority or policy is missing, save the exact draft
and blocker and surface them in the scheduled chat instead of reporting a no-op.

## Kobo regression receipt

On October 7, 2026, the first live scan found two RuneO mentions on
[Kobo #7259](https://github.com/kobotoolbox/kpi/issues/7259) as one response
case even though the notification was already read. The known
[bot reply](https://github.com/kobotoolbox/kpi/issues/7259#issuecomment-6046366481)
was verified and recorded against both messages. A repeat live scan returned
zero new and zero pending decisions. The offline regression fixture replays the
pre-reply state, an unchanged next-day scan, and the verified reply.
