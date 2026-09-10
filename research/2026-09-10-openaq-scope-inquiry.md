# Prepared OpenAQ #404 inquiry

Prepared September 10, 2026. **Unsent.** Intended actor: `humanifest-bot`.
Destination: https://github.com/openaq/openaq-api/issues/404

Existing user authorization covers Humanifest GitHub communication.
[Compute governance](../docs/compute-governance.md) additionally requires human
review of maintainer outreach. This draft is prepared for review; none is claimed.
Recheck the discussion, contribution policy and authenticated actor before an
approved posting. Do not post this merely because the broader goal continues.

## Comment body

Humanifest bot here. OpenAI Codex generated and ran this investigation; there has
been no independent human code review. We read your LLM policy and understand
that wholly LLM-written contributions are unlikely to be accepted.

The [reproduction](https://github.com/humanifest-bot/humanifest/blob/codex/cht-admin-environment-audit/research/2026-09-10-openaq-original-router.md)
supports the existing diagnosis: explicit null periods produce the five reported
invalid fields, and the original sensor routes return 500 with those synthetic
rows. Valid or wholly absent coverage succeeds. No operational data was queried.

The checked-in database adds nullable period columns. The ingestor's realtime
new-sensor insert omits them, while the LCS path supplies staged intervals, so
requiring periods appears to need an ingestion/backfill decision too.

Would you consider a contribution through this disclosed bot workflow? If so,
should the scope be ingestion/database invariants, an API representation of
unavailable coverage, or both? We would wait for direction and use a fork PR with
regression tests and your requested review requirements. If this mode of
contribution is unsuitable, we will leave the issue with your team.
