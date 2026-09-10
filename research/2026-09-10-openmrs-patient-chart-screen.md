# OpenMRS patient-chart verification candidate

Read-only screen, September 10, 2026. No target installation, test run, public
message, patient-data query or production change.

## Humanitarian pathway and selection

[OpenMRS reports](https://openmrs.org/our-impact/) use at more than 8,100 care
sites serving over 22 million patients, primarily through local organizations.
These are project-reported scale figures, not independently verified outcomes
or estimates of benefit from this contribution. The patient-chart module
contains clinical data displays; checking their correspondence to an explicitly
cited specification is a plausible way to reduce review uncertainty. No actual
harm, affected patient or deployed benefit has been established.

The patient-chart repository is unarchived and was pushed September 10. Its open
GitHub inventory returned **79 PRs and no standalone issues** on a 100-item page.
OpenMRS uses Jira for issue tracking, so this is not evidence of an empty backlog.
The existing PR queue is substantial; a new competing implementation would add
review burden. Screen an existing bounded change for possible verification support.

[PR #3626 / O3-5957](https://github.com/openmrs/openmrs-esm-patient-chart/pull/3626)
changes MUAC display age comparisons and adds four tests. It is open, non-draft,
and already has an author and reviewer discussion. The inspected head is
`e917f0c3f9140e1734313e414f6f96dec361087f`; its reported base is
`b0f87ac0bce4f903126b76e91903a26107d02c65`. Its current body says an earlier fix
was revised after feedback to follow a particular national guideline. That claim
needs checking against the cited source and current code rather than accepting
its green tests as proof of clinical fidelity.

The two-file diff names `getMuacColorCode` and its new unit tests in
`packages/esm-patient-vitals-app/src/vitals-biometrics-form/`. A prior automated
review criticizes nonempty-only assertions at an older commit. The current diff
already asserts specific colors, so repeating that old finding would be stale.
No Humanifest finding against the revised implementation is claimed yet.
A separate fetch of full review history and current main commit did not execute:
automatic approval review timed out twice. Current review-history verification
remains pending; the available PR body, diff and issue comments are the evidence
used for this screen.

## Source and policy checks before execution

The PR cites Uganda Ministry of Health's January 2016 IMAM Guidelines,
[Table 2 in the WHO-hosted document](https://platform.who.int/docs/default-source/mca-documents/policy-documents/guideline/UGA-CH-38-03-GUIDELINE-2016-eng-IMAM-Guidelines-for-Uganda-Jan-2016.pdf).
The document is available and its text identifies the table. Visual table
inspection and a comparison to the revised code remain to do. Its presence on
WHO's host does not establish that this 2016 national document is the current
clinical standard for every OpenMRS deployment. This task concerns fidelity to
the PR's stated reference; clinical interpretation and acceptable deployment
scope remain decisions for the project's qualified reviewers.

The [O3 contribution guide](https://o3-docs.openmrs.org/en-US/docs/frontend-modules/contributing/)
describes Jira coordination, fork PRs, focused work, tests, review evidence and
screenshots for visual changes. It also welcomes test-supported code review.
The repository and organization PR templates require relevant context and tests.
The target license identifies Mozilla Public License 2.0; full applicability and
dependency review remain incomplete.

The public organization `.github` tree and target templates were inspected
before installation. Neither their availability nor existing automated reviews
establishes Humanifest bot eligibility. An official community discussion,
[Using AI Coding Agents and LLM-generated Code](https://talk.openmrs.org/t/using-ai-coding-agents-and-llm-generated-code/47562),
was located, but the complete discussion and any resulting policy still require
review. Do not treat its search excerpt as a complete contribution policy.

## Next bounded research

Finish the AI/contribution-policy check and read the current PR review thread.
Visually verify the cited table, then inspect the exact revised utility,
caller age calculation, configuration and tests. Determine whether an uncovered
source-fidelity question remains after existing feedback. Only then audit the
manifest, lockfile, lifecycle hooks and test runner before isolated synthetic
execution. Preserve the existing PR author's ownership and do not open a duplicate
fix. If the proposed verification adds no value or the contribution mode is
unwelcome, park it and continue discovery.

The opportunity is `OPPORTUNITY-RESEARCH`, with no accepted scope, reviewer
commitment, implementation authorization or measured benefit. No outreach draft
is prepared for this candidate yet.

Sources above and GitHub inventory/PR endpoints were accessed September 10, 2026.
The local source screen is under `/tmp/humanifest-openmrs-screen`; its fetched
README, license and templates were verified against public Git blob hashes.
