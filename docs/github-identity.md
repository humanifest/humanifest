# Humanifest GitHub Identity

The user authorized Humanifest outreach and convenient bot setup on 2026-09-08,
with the condition that communication never use their personal account.
[The contribution protocol](contribution-protocol.md#communication-authorization)
controls the authorized contribution scope.

## Current state

- `humanifest` is a GitHub organization, not a login that can author comments.
- The default CLI and connected GitHub tool authenticate as `roryscot`.
- The user registered `humanifest-bot`; the public GitHub API verified that user
  identity on 2026-09-08. The in-app browser session is verified as this user;
  isolated CLI authentication is now verified as this user. After expired device flows, a
  fresh browser authorization reached GitHub's existing-access confirmation.
  Automatic approval review blocked completing it because the displayed scopes
  include private repository control, workflow updates, gist creation, and
  organization/team read access. The pending flow later completed outside the
  rejected action; a fresh CLI API check confirmed `humanifest-bot` (ID 326603023).
- Correction: a configuration-only check appeared to show push permission, but
  the next identity guard found that credential resolved to `roryscot`. An
  account-specific credential check on 2026-09-08 verified `humanifest-bot` and
  `push: false`. Bot Write access to `humanifest/humanifest` remains pending
  explicit approval after automatic approval review rejected granting it.
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

Authenticate `humanifest-bot` through the GitHub CLI's browser login using a
dedicated, user-owned authentication configuration. Do not copy credentials
between macOS users or rely on configuration-directory separation alone to
isolate Keychain token selection.
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
3. Recheck CHT #10155 for replies, assignment, closure, or competing work.
4. Use the published inquiry above; do not send it again.
5. Handle routine follow-ups within the existing authorization. Record actual
   maintainer confirmation before advancing the opportunity.

For Humanifest repository pushes, verify the new account has access and configure
repository-local commit attribution using its actual verified or GitHub-provided
no-reply address. Do not change global credentials or fabricate attribution.

## Sources

Inspected 2026-09-08:

- [GitHub account types and attribution](https://docs.github.com/en/get-started/learning-about-github/types-of-github-accounts)
- [GitHub machine account registration requirements](https://docs.github.com/en/site-policy/github-terms/github-terms-of-service#3-account-requirements)
- [GitHub App installation access and token identity](https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/differences-between-github-apps-and-oauth-apps)
- [Reported config-directory and Keychain identity mismatch](https://github.com/cli/cli/issues/12885)
