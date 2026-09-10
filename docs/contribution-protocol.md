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

On 2026-09-08, the user authorized posting the prepared CHT #10155 inquiry,
handling its follow-ups, and submitting a tested PR and review revisions if
maintainers confirm the scope, without further routine approvals. Communication
must use a Humanifest identity, never the user's personal account. This
authorization does not waive maintainer confirmation, implementation gates,
portfolio limits, or truthful AI and review disclosures.

The approved posting identity is `humanifest-bot`, registered by the user and
verified as a GitHub user on 2026-09-08. `humanifest` is the organization that
owns this repository. The browser session was verified as `humanifest-bot`, and
the authorized [CHT #10155 inquiry](https://github.com/medic/cht-core/issues/10155#issuecomment-5590328371)
was posted at 2026-09-08T19:02:19Z. GitHub's API confirmed the author and body.
Isolated CLI authentication subsequently completed and its API identity was
verified as `humanifest-bot`. The default CLI and connected GitHub tool still
resolve to `roryscot`. Configuration separation alone proved insufficient for
Keychain isolation; use `scripts.bot_github` to select and verify the bot's actual
credential before writes. Repository push permission remains pending.
Before posting, verify that the exact connection used authenticates as
`humanifest-bot`. Do not fall back to personal credentials. See
[GitHub identity setup](github-identity.md) for the separate bot CLI configuration.

GitHub documents [account attribution](https://docs.github.com/en/get-started/learning-about-github/types-of-github-accounts)
and [user versus app token identities](https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/differences-between-github-apps-and-oauth-apps)
(accessed 2026-09-08). Organization ownership alone cannot make an issue comment
appear under the organization's name.

## Policy discovery before target testing

During `PROJECT-AUDIT`, inspect the target repository's contribution guide,
license, templates and linked policies, then inspect its owner's public `.github`
repository and organization contribution documentation for AI/LLM, bot, conduct
and agreement rules. Record source URLs, revisions where available and access
dates. A community-profile response or a generic invitation to contribute does
not prove that an organization has no additional policy.

Complete this policy screen before substantial target installation or repeated
runtime reproduction. If a policy excludes the proposed contribution mode, park
that mode; if review is case-by-case, record the uncertainty before investing
further compute. Understanding a policy is distinct from eligibility or maintainer
acceptance. Preserve the actual authorship and human-review status in disclosures.
Do not continue testing merely to accumulate evidence for work the project does
not want.

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
