# Humanifest contribution cycle — 2026-10-02

This is an evidence-linked research handoff, not an accepted portfolio change or
upstream donation. Access date for the sources below: 2026-10-02 UTC. No target
repository was cloned, edited, built, or tested; no message or PR was posted.

## Bot inbox and prior donations

The identity-guarded `scripts.bot_github` connection returned two notifications
with `all=true`: [Open Food Facts PR #504](https://github.com/openfoodfacts/openfoodfacts-python/pull/504)
and [Kobo issue #7259](https://github.com/kobotoolbox/kpi/issues/7259). Both
were already read. The full issue conversations and OFF inline review comments
showed no new response to Humanifest's prior work. The bounded standing-authority
[CHT issue #10155](https://github.com/medic/cht-core/issues/10155) also has no
new reply to the bot's September 8 inquiry. No duplicate response was sent and
notification read state was not changed. The OFF maintainer's September 21
request for live integration and parameter checks, and Kobo's September 9
deferral pending team direction, remain the material follow-ups.

## Existing contribution lane: IFRC GO

[IFRC GO web app issue #2515](https://github.com/IFRCGo/go-web-app/issues/2515)
remains open, unassigned, and without comments. The [affected view](https://github.com/IFRCGo/go-web-app/blob/develop/app/src/views/SurgeCatalogueInformationManagement/index.tsx)
renders a DEEP card with the obsolete `deephelp.zendesk.com` link, and adjacent
[`i18n.json`](https://github.com/IFRCGo/go-web-app/blob/develop/app/src/views/SurgeCatalogueInformationManagement/i18n.json)
contains its labels. This is a bounded frontend candidate within an active
disaster-information project. The issue wording asks to remove the link but does
not resolve whether the card and now-unused translations should also go. No
maintainer scope confirmation, project-wide bot policy clearance, or authorized
upstream write is evidenced. Do not build a speculative patch.

Specific draft scope question for the issue, **not posted**:

> I traced the obsolete DEEP link to the information-management catalogue card
> in `app/src/views/SurgeCatalogueInformationManagement/index.tsx`. For #2515,
> would you like the link removed while retaining the card, or should the DEEP
> card and its unused `i18n.json` labels be removed together? I can keep a fix
> limited to that view once the intended outcome is clear.

Next gate: target-specific authority for a bot comment, a verified compatible
bot/AI contribution pathway, and maintainer scope. The existing unanswered
[IFRC organization inquiry](https://github.com/IFRCGo/pystac-monty/issues/199#issuecomment-5594287228)
is not an answer for this frontend issue.

## Discovery audit: OpenFn Lightning

This [existing discovery lead](2026-09-30-project-discovery-leads.md) was audited
further today; it is not yet a canonical project or opportunity. OpenFn's
[repository](https://github.com/OpenFn/lightning) is public and unarchived,
with `main` as default, an LGPL-3.0 repository license, and a GitHub API
`pushed_at` value of 2026-10-02T13:25:57Z. Its humanitarian pathway is
interoperability for NGO and government services; benefit from any individual
patch remains unmeasured.

[Issue #5197](https://github.com/OpenFn/lightning/issues/5197) is open,
unassigned, and has no comments. It reports that the V2 GitHub sync setup UI
promises a new action will be committed to `main` even when a different branch
is selected. The reporter observed the action running on the selected branch
and explicitly questioned the intended behavior. This is a plausible small
copy-and-test task, but the product contract remains unresolved.

[Open PR #4722](https://github.com/OpenFn/lightning/pull/4722), updated today,
touches the GitHub sync component and adds branch-conflict tests. Its inspected
component diff adds a project ID to validation and surfaces an ancestor-branch
conflict; it does not edit the disputed `main` copy. This is adjacent work, not
evidence that #5197 is fixed. Recheck its merged state and current branch before
any future patch to avoid a conflict.

The [README contribution process](https://github.com/OpenFn/lightning#contribute-to-this-project)
asks contributors to announce issue ownership, include tests and changelog,
open a draft PR, and seek maintainer review. The
[PR template](https://github.com/OpenFn/lightning/blob/main/.github/pull_request_template.md)
requires explicit AI-use disclosure and checks for code review, authorization
policy tests, and changelog. The linked
[Responsible AI Policy](https://www.openfn.org/ai) publicly states
accountability and full disclosure principles; its interactive full-policy
content was not available through the read-only page view. Repository and
organization bot-account rules remain unconfirmed. Local setup calls for
Elixir/Erlang, PostgreSQL, bootstrap, and migrations; none ran.

Next gate: establish the exact intended branch behavior and inspect the full
AI/bot contribution policy. A narrow, unposted question is: “For #5197, should
the setup text describe committing the action to the branch selected in the
form? I see #4722 changing branch collision validation but not this copy. Once
the intended contract is confirmed, I can update the copy and a focused UI
test.” Posting requires a separate target-specific authorization and immediate
`humanifest-bot` identity check on the exact connection.

No new lead was promoted to `portfolio/` because the policy screen and
Orca/source-of-truth route remain incomplete. This cycle advanced evidence and
specific questions, not code or a donation.
