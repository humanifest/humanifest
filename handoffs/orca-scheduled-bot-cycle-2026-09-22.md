# Orca handoff: scheduled Humanifest bot cycle

## Original request and current boundary

The user wants Humanifest to keep donating work to high-impact humanitarian
projects, consider all 16 current opportunities, improve previous donations,
and run those goals on scheduled tasks. Reviewing the bot's GitHub inbox and
responding to messages must be a normal part of each cycle. The user identified
a Gmail inbox used through iOS Mail, but explicitly prioritized GitHub and
deferred the mail connection. Keep the account address out of this public repo.

The existing `.github/workflows/operator-loop.yml` runs daily at 13:00 UTC and
on manual dispatch. It uses `contents: read`, does not retain checkout
credentials, and calls the offline `humanifest.cli operate` command. Public
GitHub Actions runs on 2026-09-20 through 2026-09-22 succeeded. The local
`operate` changes add source, cause, active-opportunity, and previous-donation
follow-up work queues, but they are uncommitted and therefore are not in that
active workflow. See `docs/opportunity-audit-2026-09-22.md` for the bounded
16-opportunity audit.

An identity-guarded read through `scripts.bot_github` on 2026-09-22 returned no
unread public participating GitHub notifications. The `all=true` view returned
two already-read public threads: Open Food Facts PR #504 (`comment`) and Kobo
issue #7259 (`mention`). This does not establish that every thread is fully
answered. No message was posted or marked read during this check.

## Driver and authority

Route this change through Orca per `docs/model-routing.md`: it affects bot
identity, external writes, automation, and donated compute. Read `AGENTS.md`,
`GOALS.md`, `README.md`, `docs/contribution-protocol.md`,
`docs/github-identity.md`, `docs/setup.md`, `docs/compute-governance.md`,
`docs/bot-operator-runbook.md`, and the current opportunity records before
making implementation decisions. Preserve the original user request alongside
the extracted requirements. Keep the default GitHub Actions operator loop
read-only. Do not add a bot token or write-capable workflow to Actions as setup.

The standing protocol authorizes bounded CHT #10155 inquiry follow-ups and a
tested PR if its maintainers confirm scope. It does not turn every GitHub
notification into permission to post. The user's new request explicitly calls
for responses as part of the cycle; Orca must define the allowed response scope
in a separate, reviewable authority record before unattended posting. Preserve
target AI/bot policies, maintainer confirmation gates, identity checks, and
portfolio capacity. Never use the default `roryscot` CLI or GitHub connector for
Humanifest messages; `scripts.bot_github` verifies `humanifest-bot` using the
account-specific credential immediately before a `gh` command.

## Deliverables

1. Implement a GitHub inbox review step for every scheduled bot cycle. Read all
   relevant pages of notifications, including already-read threads needing
   follow-up. Record the notification ID, repository, subject URL, reason,
   unread state, updated time, last relevant comment, and review outcome.
   Keep private or unrelated notifications out of ordinary reports. A failed
   identity check, API call, or pagination must fail the inbox step visibly.
2. Reconcile each notification with a current Humanifest opportunity and its
   authorization, project policy, gates, and latest upstream state. Classify it
   as response needed, monitor, record update, or no action. Check the entire
   thread for the last bot response and later human messages; a `comment` or
   `mention` reason alone does not prove a reply is needed. Include previous
   donations and open PRs in this review.
3. Generate a specific, evidence-linked response for an authorized message.
   Before posting, re-fetch the thread, verify `humanifest-bot` on the exact
   connection, confirm the target and current permission, and detect duplicate
   replies. Record the posted URL, actor, UTC time, source message, decision,
   and applicable authority. Do not send generic acknowledgements or mark a
   notification read merely because it was fetched. If scope or policy is
   uncertain, leave a review item for the operator without posting.
4. Schedule the inbox and opportunity cycle in an environment with the required
   bot credential and explicitly approved network and write boundary. Preserve
   the existing read-only Actions job. The schedule should surface failures and
   required decisions, but remain quiet when nothing actionable changed. Use
   an idempotent receipt so a retry cannot send the same reply twice.
5. Document setup, stop controls, response scope, receipts, and verification in
   the operator runbook. Leave Gmail disconnected for now; record it as a later
   integration with separate identity, privacy, and sending authorization.

## Acceptance evidence

- A scheduled run is observed with its actual scheduler, identity, repository
  revision, time, and complete inbox-fetch result. A checked-in workflow or
  prompt alone is not activation evidence.
- Fixtures cover pagination, already-read but unanswered threads, no-op cycles,
  later human follow-up, duplicate suppression, stale thread state, wrong actor,
  unauthorized target, policy exclusion, and API failure. Verify that no
  outbound operation occurs for blocked or no-op cases.
- A response is considered delivered only with a GitHub URL and verified
  `humanifest-bot` authorship. If no response is due, a no-op receipt explains
  why. Tests or schema-valid receipts alone do not prove a live response.
- The 16-opportunity report and current portfolio records remain distinct from
  live upstream status. Do not advance an opportunity or claim impact solely
  because the bot reviewed or replied to a thread.

## Status as of 2026-09-30

The chat-attached `humanifest-contribution-and-github-inbox-cycle` task is active
on a daily schedule. Its 2026-09-29 run used the identity-guarded bot connection
to review GitHub notifications and all 16 upstream issue/PR statuses. It posted
no message or patch. On 2026-09-30, the saved prompt was revised to advance one
bounded work item per run and distinguish actual donated work from monitoring.
That revised prompt has not yet completed a scheduled run. No upstream code
donation or new maintainer response is established by task activation.

The repository's separate GitHub Actions job remains read-only and has no bot
inbox access or write credential. No Orca route is exposed in this session;
source-of-truth acceptance and broader bot-write design remain with Orca and
human review. All 16 current opportunity records still fail at least one hard
gate, so the scheduled task must not start an upstream implementation merely
to produce activity.
