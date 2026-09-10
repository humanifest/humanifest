# Prepared MetaData Sync #1255 inquiry

Prepared September 10, 2026. **Unsent.** Intended actor: `humanifest-bot`.
Destination: https://github.com/EyeSeeTea/metadata-synchronization/issues/1255

Existing user authorization covers Humanifest GitHub communication.
[Compute governance](../docs/compute-governance.md) additionally requires human
review of maintainer outreach. This draft is prepared for that review; no human
review or maintainer acceptance is claimed. Verify the discussion, overlapping
PRs and authenticated actor again immediately before any approved posting.

## Comment body

Humanifest bot here, with AI-assisted verification of #1255 at development
`78c8b8c22278dcbb7d2d5678eaafaa80b0fd0cf9`.

The [original Global Mapping UI](https://github.com/humanifest-bot/humanifest/blob/codex/cht-admin-environment-audit/research/2026-09-10-mdsync-global-mapping-ui.md)
omits indicator types. A category control selects, saves, reloads and replaces
its mapping through the original UI/use cases/repository with synthetic
metadata and localStorage. Thirteen unchanged native tests and four additional
[workflow probes](https://github.com/humanifest-bot/humanifest/blob/codex/cht-admin-environment-audit/research/2026-09-10-mdsync-native-workflow.md)
also pass. No target production code was changed.

One scope question: the builder includes source indicator-type objects, and the
mapper preserves their fields while replacing their IDs. We have not tested a
real DHIS2 import. Should a mapped destination type be reused unchanged, or
should its fields be updated from the source? That decision would guide the
regression tests alongside the requested picker addition; we would keep global
import defaults unchanged.

Would a focused contribution through this bot account be welcome, subject to
your AI-assistance and review requirements? We would use a fork and wait for
scope confirmation. No independent human code review, production deployment or
measured health benefit is claimed.
