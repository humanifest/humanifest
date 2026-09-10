# Impact Methodology

Humanifest scores opportunities from supplied evidence, not from scraped popularity alone.

Cause-area discovery is upstream of opportunity scoring. Use
[cause discovery](cause-discovery.md) to decide where to search for projects and
issues; use this document to decide whether a specific candidate contribution is
worth advancing.

Evidence types:

- `measured`: independently observed outcome or direct operational measurement.
- `modeled`: estimate derived from an explicit model.
- `self_reported`: project, steward, or organization claim.
- `inferred`: reasonable proxy that does not directly measure the claimed outcome.

Scores are directional and auditable. They are not causal estimates, funding recommendations, or claims that a particular pull request will improve lives.

The initial weights are:

- humanitarian benefit: `0.30`
- acceptance probability: `0.20`
- technical confidence: `0.20`
- review burden: `-0.20`
- deployment probability: `0.10`

Hard gates dominate scores. If any hard gate fails, the implementation score is zero.

Parked, declined, merged, and released records also have zero implementation score.
Raw scores remain available for auditing the supplied inputs, but reports list
candidates by state and ID rather than ranking blocked work by raw score.
Eligibility in single-record output covers only gates and state; portfolio capacity
and authorization remain separate requirements.

## Verify the contribution separately from the cause

A useful platform, a recognized public good, or a successful intervention does
not establish the value of a particular patch. Keep project-level evidence in
the project record and contribution-specific observations in the opportunity
record. A study of a software-enabled service evaluates that intervention and its
setting; do not attribute its full effect to the software or a later bug fix.

Use the existing `evidence` and `sources` fields to track these milestones as they
actually occur:

| Milestone | Evidence to record | Limit of the claim |
| --- | --- | --- |
| Correctness | Before/after reproduction, tested revision, command, and result using synthetic data | Shows behavior in the tested environment, not deployment |
| Acceptance | Maintainer review and actual merged commit or PR | Shows acceptance, not release or use |
| Availability | Release notes or tag containing the change | Shows availability, not adoption |
| Retention | Later source revision or maintainer report showing retention, reversion, or replacement | Source retention alone does not show users benefited |
| Operational benefit | Voluntary maintainer/operator feedback or public aggregate measurement tied to the affected workflow | Self-reported benefit stays self-reported; do not infer population effects |

Include source URLs, observation dates in claim text, and honest access dates.
Record missing evidence as unknown rather than zero benefit or assumed success.
Preserve negative findings, reverts, regressions, and reported review burden. Do
not invent runtime, token, cost, or time-saving measurements; record actual
measurements only when available. Avoid repeated requests for feedback that cost
maintainers more time than the contribution saves.

For CHT #10155, the immediate target is observable loading/error behavior and
submit protection with regression coverage. A synthetic demonstration can verify
those states. It cannot establish faster administration, fewer production
incidents, or better patient outcomes. Later acceptance, release, and operational
evidence belong in that opportunity's record when observed.
