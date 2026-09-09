# Contribution Protocol

Humanifest represents external work through this pipeline:

```text
QUEUED
→ PROJECT-AUDIT
→ OPPORTUNITY-RESEARCH
→ SHORTLISTED
→ MAINTAINER-CHECK
→ ENVIRONMENT-READY
→ REPRODUCED
→ BUILDING
→ ADVERSARIAL-REVIEW
→ HUMAN-REVIEW
→ PR-OPEN
→ MERGED / RELEASED / PARKED / DECLINED
```

## Communication Authorization

User authorization may cover a bounded contribution and its routine follow-ups;
it does not need to be requested again for each message. Consult the current
authorization before sending, and verify the actual authenticated GitHub actor.
Repository ownership and Git commit author settings do not establish the identity
that will publish a comment or PR.

On 2026-09-08, the user directed Humanifest to handle GitHub communication through
the Humanifest account and to keep working through and replenishing the queue.
This standing authorization covers scoped issue coordination and routine replies
for audited candidates, including the initially prepared CHT #10155 inquiry.
It also covers tested contribution PRs and review revisions once maintainers
confirm the scope and all applicable gates pass. Do not request another routine
user approval merely because the next audited candidate belongs to another team.

Before a new inquiry, read the current discussion and relevant source evidence,
check for existing work and duplicate messages, and prepare a concrete question
that helps the maintainer decide whether the bounded contribution is wanted.
For an existing contributor's PR, coordinate support instead of submitting a
replacement or an unsolicited formal automated review. Record the actual message
URL, authenticated author, sent time and agreed scope in the opportunity record;
an outbound inquiry is not maintainer confirmation.

Communication must use `humanifest-bot`, never the user's personal account.
Standing authorization does not waive maintainer confirmation, implementation
gates, portfolio limits, target contribution policies, or truthful AI and human
review disclosures. It does not cover email, signing agreements, account or
repository permission changes, or automatic merging. Ask only when a concrete
required action falls outside the established authorization.

The approved posting identity is `humanifest-bot`, registered by the user and
verified as a GitHub user on 2026-09-08. `humanifest` is the organization that
owns this repository. The browser session was verified as `humanifest-bot`, and
the authorized [CHT #10155 inquiry](https://github.com/medic/cht-core/issues/10155#issuecomment-5590328371)
was posted at 2026-09-08T19:02:19Z. GitHub's API confirmed the author and body.
Isolated CLI authentication subsequently completed and its API identity was
verified as `humanifest-bot`. The default CLI and connected GitHub tool still
resolve to `roryscot`. Configuration separation alone proved insufficient for
Keychain isolation; use `scripts.bot_github` to select and verify the bot's actual
credential before writes. Upstream Write permission is not required for the
fork-and-PR workflow below.
Before posting, verify that the exact connection used authenticates as
`humanifest-bot`. Do not fall back to personal credentials. See
[GitHub identity setup](github-identity.md) for the separate bot CLI configuration.

GitHub documents [account attribution](https://docs.github.com/en/get-started/learning-about-github/types-of-github-accounts)
and [user versus app token identities](https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/differences-between-github-apps-and-oauth-apps)
(accessed 2026-09-08). Organization ownership alone cannot make an issue comment
appear under the organization's name.

## Fork and Pull Request Workflow

On 2026-09-08, the user explicitly directed Humanifest to use forks and pull
requests. Their standing authorization to improve this system covers creating
the bot-owned Humanifest fork, pushing useful tested changes on dedicated
branches, opening PRs, and handling routine review revisions through the bot.
It does not authorize permission grants or automatic merging. External project
work must match the audited opportunity's scope and retain all opportunity gates.

1. Read the target's contribution and AI policies, check existing work, and
   confirm the authorized scope. For external opportunities, preserve maintainer
   confirmation and portfolio gates before implementation or PR submission.
2. Verify `humanifest-bot` with the account-specific credential helper. Create or
   reuse its fork and verify that the fork's parent is the intended upstream.
3. Start a dedicated `codex/` branch from the current upstream base. Keep unrelated
   work out of the PR; keep external checkouts outside this control repository.
4. Make the bounded change, run applicable checks, and inspect the final diff.
   Use truthful commit attribution and follow the target's signoff requirements.
5. Push only the contribution branch to the verified bot-owned fork, using the
   same verified bot credential. Open a PR with an explicit upstream repository,
   base branch, and bot-fork head. No upstream Write grant is needed.
6. Explain the problem, resulting behavior, validation, and remaining limits.
   Disclose AI assistance and only claim human review actually performed. Verify
   the published PR's author, head, base, and checks; address review in the same
   branch. Leave merging to the upstream maintainer unless separately authorized.

This follows GitHub's [fork-based contribution workflow](https://docs.github.com/en/get-started/exploring-projects-on-github/contributing-to-a-project)
(accessed 2026-09-08). Do not treat permission to write to the bot's fork as
permission to merge or change upstream repository settings.

## Hard Gates

No opportunity may reach `BUILDING` unless every gate in `humanifest.models.HARD_GATES` passes:

- humanitarian relevance is supported;
- repository and affected subsystem are active;
- external contributions are accepted;
- contribution and AI policies are understood;
- problem is current and consequential;
- behavior is reproducible or objectively verifiable;
- relevant code and tests are located;
- change is bounded;
- regression protection is credible;
- no private operational data are required;
- security and licensing risks are acceptable;
- environment setup is feasible;
- maintainer has indicated the work is wanted or appropriate;
- probable reviewer exists;
- benefit justifies review cost;
- user can explain the change line by line.

## Stopping Conditions

Validation enforces maintainer confirmation from `ENVIRONMENT-READY` through
`RELEASED`, and every hard gate from `BUILDING` through `RELEASED`. `PARKED` and
`DECLINED` records retain their unresolved gates without being treated as active
work. Gate results must be booleans with non-empty rationales. Generated handoffs
include failed gates and explicitly block implementation while any gate fails.

Gate rationales can cite evidence using an optional `source_ids` list. If present,
the list must be non-empty, contain unique non-empty IDs, and reference entries in
the opportunity's own `sources` list. A passing `maintainer_interest_confirmed`
gate requires this list in every state. Link the actual confirmation and explain
the agreed scope in the rationale; an issue being open or labelled "help wanted"
does not establish current maintainer interest.

For example, after inspecting an actual confirmation and adding its source entry:

```json
"maintainer_interest_confirmed": {
  "passed": true,
  "rationale": "The maintainer confirmed the bounded approach described in this record.",
  "source_ids": ["maintainer-confirmation"]
}
```

The `maintainer-confirmation` source must include its real URL and access date.
The validator checks traceability, not the source's meaning, author identity, or
continuing relevance. A reviewer must still verify those claims. Unconfirmed gates
remain false and do not need invented citations. Existing records with a passing
maintainer gate but no citation must add verified evidence or correct that gate
before validation, scoring, or handoff generation can succeed.

Park the work if the issue is stale, already assigned, already under PR, too broad, security-sensitive without the target disclosure path, or dependent on private data.

## Portfolio Capacity

### Keep work moving while reviews are pending

The user clarified on 2026-09-08 that donated compute should continue through the
queue and identify additional high-impact work while earlier contributions await
responses. A pending inquiry or PR blocks its dependent steps, not independent
research or another eligible contribution. Discovery and source inspection do
not consume implementation or external-PR slots.

Choose the next useful action in this order:

1. Address actionable maintainer feedback on an existing contribution.
2. Advance a confirmed, gate-passing contribution when capacity permits.
3. Resolve a specific evidence, scope, policy, or reproduction-planning gap in
   another candidate using the permitted level of source inspection.
4. Refill the research queue with a small batch of promising opportunities from
   other maintainer teams. Verify the cause, current issue, competing work, and
   contribution policy; record an exact next investigation and why it matters.

Prefer operational correctness, access to useful data, accessibility, and
reliability where evidence supports likely benefit. Public reach alone is not
proof of a high-impact patch. Keep unconfirmed work in a research state and
explain prioritization without assigning it a nonzero implementation score.
Do not crowd out another active contributor or inflate the queue with vague work.

Do not repeatedly poll unchanged discussions in consecutive work cycles. Unless
a maintainer asks for faster follow-up or a deadline warrants it, schedule the
next manual external-status check about a week after the last one and spend the
intervening work on independent candidates. A recorded check date is a work plan,
not an installed monitor or permission to send reminders.

Only treat the portfolio as blocked after checking the actionable queue and a
bounded refill for useful independent work. Per-project confirmation, setup,
privacy, authorization, and review-capacity requirements still apply. Waiting on
Humanifest's own control-repository PRs does not consume external-contribution
slots or prevent queue research.

### Implementation and publication limits

`validate` and `report` enforce one active implementation across `BUILDING`,
`ADVERSARIAL-REVIEW`, and `HUMAN-REVIEW`. A `PR-OPEN` record occupies one of two
portfolio PR slots and its organization's single PR slot. Stopped and completed
records occupy neither kind of slot. These checks use recorded states; they do not
query upstream PR status or track unrecorded work.

For GitHub repository URLs, the review organization defaults to
`github.com/<owner>` in lowercase, shared across that owner's repositories.
Projects on other hosts must supply a non-empty `review_organization` before an
opportunity reaches `PR-OPEN`. This optional project field also groups an
organization spread across hosts: use the same stable value on every affected
project. Explicit values are compared without surrounding whitespace or case.
Only use an override supported by the project's actual review ownership; do not
split one organization into different values to evade the limit.

Single-record scores and handoffs do not establish portfolio capacity or grant
authorization. Validate the full portfolio and check actual upstream status before
starting an implementation or opening a PR. Parked, declined, merged, and released
records have zero implementation score even if their historical gates all pass.
