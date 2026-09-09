# Humanifest GitHub Identity

The user authorized Humanifest outreach and convenient bot setup on 2026-09-08,
with the condition that communication never use their personal account.
[The contribution protocol](contribution-protocol.md#communication-authorization)
controls the authorized contribution scope.

## Current state

- `humanifest` is a GitHub organization, not a login that can author comments.
- The default CLI and connected GitHub tool authenticate as `roryscot`.
- The user registered `humanifest-bot`; the public GitHub API verified that user
  identity (ID 326603023) on 2026-09-08. Browser and account-specific CLI
  authentication have both been verified as this user.
- The bot has read access to `humanifest/humanifest`. Upstream Write access is
  unnecessary: authorized contributions use its fork and a PR. The previous
  instruction to obtain upstream Write access was incorrect; no permission grant
  is required or part of this workflow.
- Configuration separation alone previously selected the personal credential
  despite bot login settings. Always select and verify the account-specific
  credential as described below.
- The [CHT #10155 inquiry](https://github.com/medic/cht-core/issues/10155#issuecomment-5590328371)
  was posted through that browser at 2026-09-08T19:02:19Z. A read-only API check
  verified its author and body. Do not post a duplicate.

## Bot authentication

A dedicated machine user is the simplest initial option for ordinary public OSS
issue and PR participation. A GitHub App installation token only reaches the
repositories granted to its installation; installing an app on Humanifest alone
does not grant it write access to `medic/cht-core`.

Account registration is complete. GitHub's account terms require a human to
create the account and accept responsibility for its automated actions.

Authenticate `humanifest-bot` through the GitHub CLI's browser login. This host
uses `GH_CONFIG_DIR=/Users/admin/.config/gh-humanifest` for bot login configuration,
but configuration separation alone does not isolate Keychain token selection.
Use `python3 -m scripts.bot_github <gh arguments>` for bot operations. The helper
selects the existing credential with `gh auth token --user humanifest-bot`, then
verifies GitHub's actual response before executing the requested command. It
does not grant authorization or bypass repository permissions. Keep credentials in the authentication tool's
credential store, never in this repository or a chat message. Verify the username
returned by the exact connection that will perform the write; signing one
connection in does not change the other connection.

## Resume checks

1. Use the approved `humanifest-bot` identity recorded in the contribution protocol.
2. Verify the authenticated actor matches it immediately before outbound work.
3. Select the next useful action under the contribution protocol. Check a waiting
   discussion when its recorded review date is due, an actionable reply arrives,
   or a dependent action requires fresh status. Do not poll CHT #10155 on every
   resume while independent work is available.
4. Before outbound work, check the relevant opportunity's existing message and
   PR records and current discussion. Reuse the existing thread; avoid duplicates.
5. Handle scoped coordination and routine follow-ups under standing authorization
   for audited candidates. Record actual maintainer confirmation before advancing
   the opportunity; keep independent work moving while waiting.

## Fork-based publication

For this control repository, use `humanifest-bot/humanifest` as the contribution
fork and `humanifest/humanifest` as upstream. Before reuse, verify that the fork
is owned by `humanifest-bot` and its parent is `humanifest/humanifest`. Use a
dedicated `codex/` branch based on the current upstream base; push that branch to
the fork and open a PR with explicit head and base repositories and branches.
Check for an existing PR before creating one. Follow the
[contribution protocol](contribution-protocol.md#fork-and-pull-request-workflow)
for review, disclosure, and authorization.

Git pushes must also use the credential returned by `bot_environment()` from
`scripts.bot_github`, passed only in the child environment. For HTTPS pushes,
clear inherited Git credential helpers for that command and use
`gh auth git-credential` with that environment. Ordinary Git pushes can otherwise
select the personal account even after a successful bot API check. Verify the
explicit push destination is the bot's fork; never put a token in the remote URL.

Use command-scoped or repository-local commit attribution:
`humanifest-bot <326603023+humanifest-bot@users.noreply.github.com>`.
Do not change global credentials or fabricate human authorship or review.
Commit attribution does not replace authenticated actor verification.

## Sources

Inspected 2026-09-08:

- [GitHub account types and attribution](https://docs.github.com/en/get-started/learning-about-github/types-of-github-accounts)
- [GitHub machine account registration requirements](https://docs.github.com/en/site-policy/github-terms/github-terms-of-service#3-account-requirements)
- [GitHub App installation access and token identity](https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/differences-between-github-apps-and-oauth-apps)
- [Reported config-directory and Keychain identity mismatch](https://github.com/cli/cli/issues/12885)
- [Contributing through a fork and pull request](https://docs.github.com/en/get-started/exploring-projects-on-github/contributing-to-a-project)
