# Portfolio Status

Projects: 11
Opportunities: 13
Active implementations: 0/1
Open external PRs: 0/2 (at most 1 per organization)

Status reflects supplied records; source access dates are not a live upstream check.
Scores do not authorize implementation or external writes. Candidates are listed by state and ID, not ranked by raw score.

- epanet-883-tank-volume-curve-validation: OPPORTUNITY-RESEARCH; score=0.0; failed_gates=12
  Next: Verify the issue is current and bound its code surface and regression strategy.
  - external_contributions_accepted: Not established in this bounded source intake; verify before implementation.
  - contribution_policy_understood: Not established in this bounded source intake; verify before implementation.
  - ai_policy_understood: Not established in this bounded source intake; verify before implementation.
  - problem_current_and_consequential: Current pinned runtime accepts invalid volume ordering and returns NaN diameter without errors. Operational consequences and practical priority remain unconfirmed.
  - change_bounded: Research can compare loader, assignment and later mutation. Production checks must preserve legitimate other curve types and agree error/rollback semantics.
  - regression_strategy_credible: Real-library controls now cover five entry paths and both unit systems. Existing Boost baseline, accepted failure/rollback semantics and production regression integration remain.
  - security_and_licensing_risk_acceptable: Not established in this bounded source intake; verify before implementation.
  - environment_feasible: Original native library builds and 34 public-API cases pass in isolation. Boost test dependencies and unchanged-suite baseline remain before full environment readiness.
  - maintainer_interest_confirmed: Issue open, unassigned and without comments; no Humanifest inquiry, acceptance or bot eligibility established.
  - probable_reviewer_identified: Not established in this bounded source intake; verify before implementation.
  - benefit_justifies_review_cost: Not established in this bounded source intake; verify before implementation.
  - user_can_explain_line_by_line: Not established in this bounded source intake; verify before implementation.
- odk-2169-worker-memory-threshold: OPPORTUNITY-RESEARCH; score=0.0; failed_gates=10
  Next: Verify the issue is current and bound its code surface and regression strategy.
  - contribution_policy_understood: Not established in the bounded source review; verify before implementation.
  - ai_policy_understood: Not established in the bounded source review; verify before implementation.
  - problem_current_and_consequential: Byte-threshold mismatch is present on production and development source; actual excess memory use, OOM frequency and deployment consequence are unmeasured.
  - change_bounded: A narrow unit-normalization/test proposal is plausible, but the intended threshold and separation from broader #2170 worker-sizing policy need confirmation.
  - security_and_licensing_risk_acceptable: Not established in the bounded source review; verify before implementation.
  - environment_feasible: Not established in the bounded source review; verify before implementation.
  - maintainer_interest_confirmed: No Humanifest scope inquiry or maintainer confirmation yet; an open unassigned issue is not approval.
  - probable_reviewer_identified: Not established in the bounded source review; verify before implementation.
  - benefit_justifies_review_cost: Not established in the bounded source review; verify before implementation.
  - user_can_explain_line_by_line: Not established in the bounded source review; verify before implementation.
- cht-10155-edit-user-load-failure: MAINTAINER-CHECK; score=0.0; failed_gates=1
  Next: Coordinate within standing authorization using the verified Humanifest identity; record current maintainer confirmation.
  - maintainer_interest_confirmed: Replacement inquiry sent as humanifest-bot at 2026-09-08T19:02:19Z. Await maintainer response; the outbound inquiry is not confirmation.
- cht-11342-dhis2-bs-month-export: MAINTAINER-CHECK; score=0.0; failed_gates=3
  Next: Coordinate within standing authorization using the verified Humanifest identity; record current maintainer confirmation.
  - change_bounded: Writer and exporter tags differ, but the admin picker retains a day-dependent timestamp and payload period remains Gregorian. Maintainers have not chosen whether lookup, picker, and label changes belong in one bounded fix. A backend-only change cannot yet be assumed to resolve the full report.
  - maintainer_interest_confirmed: September 9 fresh issue/timeline check found no assignment or comments. The prepared scope inquiry was not posted after automatic approval review rejected it. Neither the reproduction nor completed related epic establishes confirmation for this export contribution.
  - probable_reviewer_identified: No reviewer is assigned on the issue.
- climada-1312-wildfire-fraction-verification: MAINTAINER-CHECK; score=0.0; failed_gates=12
  Next: Coordinate within standing authorization using the verified Humanifest identity; record current maintainer confirmation.
  - external_contributions_accepted: General guide welcomes external fork contributions. Eligibility of this AI-assisted bot contribution is now explicitly asked in the delivered inquiry and remains unconfirmed.
  - contribution_policy_understood: Fork/develop, tests, Pylint, formatting and attribution requirements inspected. Final scope-specific checklist and bot pathway need agreement before implementation.
  - ai_policy_understood: No explicit AI/bot rule found in bounded repository and linked guide inspection. Delivered inquiry asks whether this bot pathway is welcome; absence of a rule is not acceptance.
  - problem_current_and_consequential: Current active COD artifact confirms duplicate fractions; original methods propagate out-of-range values. Operational consequences, population-weighted impact and review benefit remain unverified.
  - change_bounded: Synthetic method-level research is bounded. A production fix could belong in data generation, validation or warnings; generic max/clipping may corrupt valid matrix semantics.
  - regression_strategy_credible: Controlled method and public-file probes pass, but the intended fraction-validation/data-generation behavior has not been agreed for a production regression.
  - security_and_licensing_risk_acceptable: Bounded source/data path inspected, public artifact licensed CC BY 4.0 and pinned binary reader verified. Full native dependency/license and production change review remains incomplete.
  - environment_feasible: Bounded method/data probes are feasible and pass; full native/geospatial framework baseline remains unestablished.
  - maintainer_interest_confirmed: Verification and scope question delivered as humanifest-bot; posting does not establish maintainer acceptance or bot eligibility.
  - probable_reviewer_identified: Global CODEOWNERS identifies possible reviewers, but no reviewer has accepted this scope.
  - benefit_justifies_review_cost: Independent data confirmation was delivered; deployment need, reviewer interest and useful bounded change remain unconfirmed.
  - user_can_explain_line_by_line: Harnesses and exact results are documented; no independent human explanation or review is claimed.
- ifrc-usgs-economic-rounding: MAINTAINER-CHECK; score=0.0; failed_gates=7
  Next: Coordinate within standing authorization using the verified Humanifest identity; record current maintainer confirmation.
  - ai_policy_understood: No explicit AI/bot rule located in the bounded repository/default-policy review. The existing inquiry asks for acceptance; await its answer rather than infer approval from missing documentation.
  - problem_current_and_consequential: The archived public bins also exhibit the arithmetic discrepancy, but the 489394 USD difference is only about 0.000028% of the scale-first midpoint result. Frequency and downstream consequence remain unverified.
  - change_bounded: Candidate scope is economic scaling before integer rounding with fatality behavior preserved. Maintainers must confirm separation from the paused uncertainty/representation redesign.
  - maintainer_interest_confirmed: Inquiry delivered by humanifest-bot at 2026-09-09T01:18:23Z. Prior original-unit guidance and this outbound message do not establish approval of the new precision correction.
  - probable_reviewer_identified: Not yet established; complete the specific policy, scope or runtime check before advancing.
  - benefit_justifies_review_cost: No downstream impact established; the archived sample has a very small relative difference. Retain the focused boundary proposal without overstating priority; seek maintainer prioritization.
  - user_can_explain_line_by_line: No target implementation or independent human review has occurred.
- kobo-7259-incremental-sync-verification: MAINTAINER-CHECK; score=0.0; failed_gates=11
  Next: Coordinate within standing authorization using the verified Humanifest identity; record current maintainer confirmation.
  - ai_policy_understood: No explicit AI policy found in the inspected contribution/README/template text or policy/agent filenames of the complete pinned tree. This bounded absence is not approval; the existing scope inquiry remains pending.
  - problem_current_and_consequential: Not established in this initial research intake; inspect relevant evidence before advancing.
  - behavior_reproducible_or_verifiable: Original formatter/fallback behavior verified in isolated probes. The proposed same-second sync failure has not been reproduced through the target database/API stack; gate remains false.
  - change_bounded: One focused boundary-test/documentation proposal is prepared for coordination. No shared-format change, backfill or replacement implementation is authorized by this research finding.
  - regression_strategy_credible: Coverage matrix distinguishes actual new tests from real edit, API filtering, equal-time and delayed-visibility gaps. Complete target integration setup and selected cursor semantics remain unverified.
  - security_and_licensing_risk_acceptable: Not established in this initial research intake; inspect relevant evidence before advancing.
  - environment_feasible: The existing test path was traced through real Django/PostgreSQL fixtures and mocked Mongo. The local Docker engine is unavailable and inspected host dependencies lack PostGIS/GDAL/Redis. No installation or target test ran; an isolated runner matching the CI dependencies is still needed.
  - maintainer_interest_confirmed: Coordination question sent as humanifest-bot at 2026-09-09T00:02:57Z; outbound communication is not acceptance or maintainer confirmation.
  - probable_reviewer_identified: Not established in this initial research intake; inspect relevant evidence before advancing.
  - benefit_justifies_review_cost: Not established in this initial research intake; inspect relevant evidence before advancing.
  - user_can_explain_line_by_line: No implementation or human line-by-line review has occurred.
- off-496-text-search-contract-verification: MAINTAINER-CHECK; score=0.0; failed_gates=8
  Next: Coordinate within standing authorization using the verified Humanifest identity; record current maintainer confirmation.
  - problem_current_and_consequential: The current pinned server source supports the documented mismatch, and the SDK issue reports a failed search example. Deployment state, actual returned products and downstream consequence remain unverified.
  - change_bounded: Not established in this research intake; inspect supporting evidence before advancement.
  - regression_strategy_credible: Not established in this research intake; inspect supporting evidence before advancement.
  - security_and_licensing_risk_acceptable: Not established in this research intake; inspect supporting evidence before advancement.
  - maintainer_interest_confirmed: The maintainer previously explained CGI authentication. Humanifest has now delivered the bounded verification on PR #504, but no accepted search contract or Humanifest scope is established.
  - probable_reviewer_identified: Not established in this research intake; inspect supporting evidence before advancement.
  - benefit_justifies_review_cost: Not established in this research intake; inspect supporting evidence before advancement.
  - user_can_explain_line_by_line: Not established in this research intake; inspect supporting evidence before advancement.
- prism-1569-boundary-cache-verification: MAINTAINER-CHECK; score=0.0; failed_gates=12
  Next: Coordinate within standing authorization using the verified Humanifest identity; record current maintainer confirmation.
  - external_contributions_accepted: Not yet established by the bounded intake; verify before implementation.
  - contribution_policy_understood: Not yet established by the bounded intake; verify before implementation.
  - ai_policy_understood: Not yet established by the bounded intake; verify before implementation.
  - problem_current_and_consequential: No unmet repeat-payload case established: measured warm loads reuse all three boundary files and forced validation returns 304. Specific latency/eviction or deployment need remains to be demonstrated.
  - change_bounded: Research is limited to repeat-visit boundary transfers. Any implementation requires agreement on asset versioning, references and freshness; do not apply immutable caching to mutable data.
  - regression_strategy_credible: Cache semantics/freshness controls now execute, but no production change or agreed behavior is selected; full application regression plan remains unconfirmed.
  - security_and_licensing_risk_acceptable: Not yet established by the bounded intake; verify before implementation.
  - environment_feasible: Bounded wrapper and live-browser measurement feasible; full frontend build/Jest baseline and transitive lifecycle audit remain incomplete.
  - maintainer_interest_confirmed: Verified bot comment supplies measurements and asks for a specific unmet use case; delivery is not accepted scope, assignment or bot eligibility.
  - probable_reviewer_identified: Not yet established by the bounded intake; verify before implementation.
  - benefit_justifies_review_cost: Not yet established by the bounded intake; verify before implementation.
  - user_can_explain_line_by_line: Not yet established by the bounded intake; verify before implementation.
- pyxform-821-nested-repeat-instances: MAINTAINER-CHECK; score=0.0; failed_gates=10
  Next: Coordinate within standing authorization using the verified Humanifest identity; record current maintainer confirmation.
  - external_contributions_accepted: README welcomes focused contributions; eligibility of the required humanifest-bot identity is not established.
  - ai_policy_understood: Not yet established for this research candidate; inspect evidence before advancing.
  - problem_current_and_consequential: Open issue and August request support investigating current behavior, but the related client discussion calls it usable and noncritical. Consequential operational impact is not demonstrated.
  - change_bounded: The research matrix is bounded, but arbitrary nesting, groups, defaults and repeat_count make implementation scope and compatibility uncertain.
  - regression_strategy_credible: Not yet established for this research candidate; inspect evidence before advancing.
  - security_and_licensing_risk_acceptable: Not yet established for this research candidate; inspect evidence before advancing.
  - maintainer_interest_confirmed: The public request to explore effort supports research. Humanifest delivered its reproduction but has no confirmation of accepted implementation scope or bot contribution pathway.
  - probable_reviewer_identified: Not yet established for this research candidate; inspect evidence before advancing.
  - benefit_justifies_review_cost: Not yet established for this research candidate; inspect evidence before advancing.
  - user_can_explain_line_by_line: Not yet established for this research candidate; inspect evidence before advancing.
- cht-10241-unique-race: PARKED; score=0.0; failed_gates=8
  Next: Keep parked until the stopping reason is resolved and evidence supports reconsideration.
  - behavior_reproducible_or_verifiable: Reproduction depends on timing/resource constraints and was not independently reproduced in this run.
  - code_and_tests_located: Exact code and test surface not yet located.
  - change_bounded: Potential solutions alter concurrency behavior across endpoints.
  - regression_strategy_credible: A credible deterministic concurrency test has not been designed.
  - security_and_licensing_risk_acceptable: Concurrency and API behavior risks remain unresolved.
  - maintainer_interest_confirmed: Rechecked 2026-09-08: the inspected discussion still contains no selected approach following the maintainer objection to a global queue.
  - benefit_justifies_review_cost: Potential benefit is high, but review/design cost is also high.
  - user_can_explain_line_by_line: Not until a bounded approach is selected and reproduced.
- crisiscleanup-1164-success-banner-failure: PARKED; score=0.0; failed_gates=7
  Next: Keep parked until the stopping reason is resolved and evidence supports reconsideration.
  - contribution_policy_understood: Retrieved the live contribution page and ICLA. Published guidance differs on signing expectations; Humanifest signatory and agreement status, including application to bot/AI-assisted submissions, are unresolved. Retrieval is complete, but contribution readiness is not. No agreement was signed or submitted.
  - ai_policy_understood: Current AGENTS.md and CLAUDE.md provide AI-tool development instructions, but these are not an explicit external AI-assisted contribution policy. Disclosure and accountability requirements remain unconfirmed.
  - problem_current_and_consequential: Rechecked 2026-09-08: open but last updated 2024-10-02, with no comments; current behavior remains unconfirmed.
  - behavior_reproducible_or_verifiable: No reproduction performed and may require phone workflow context.
  - maintainer_interest_confirmed: Rechecked 2026-09-08: no comments or assignees; no current maintainer confirmation was found.
  - probable_reviewer_identified: No reviewer identified.
  - benefit_justifies_review_cost: Staleness and uncertainty make review cost unjustified until confirmed.
- hot-7227-archived-project-data-access: PARKED; score=0.0; failed_gates=12
  Next: Keep parked until the stopping reason is resolved and evidence supports reconsideration.
  - external_contributions_accepted: External human contributions are welcomed, but the September 9 shared HOT guide explicitly rejects automated bot/AI accounts. Humanifest's required posting identity is humanifest-bot; no compatible exception or pathway is established.
  - problem_current_and_consequential: Operational need is reported, but the issue was last updated in April; current deployed behavior must be checked without triggering production extraction.
  - behavior_reproducible_or_verifiable: Four isolated handler cases verified against pinned source. The archived-project end-to-end failure and deployed extractor configuration remain unverified, so the original opportunity gate stays false.
  - code_and_tests_located: Download handler, messages, extractor and active-project service read. The neighboring tests exercise AOI download, not this handler; target regression coverage still needs implementation after scope confirmation.
  - change_bounded: A frontend error-handling scope is identifiable but does not restore archived data. Maintainers must choose whether that separate contribution or a supervised refresh design is wanted.
  - regression_strategy_credible: Not established in this initial research intake; inspect relevant evidence before advancing.
  - security_and_licensing_risk_acceptable: Not established in this initial research intake; inspect relevant evidence before advancing.
  - environment_feasible: Setup and contribution-policy audit completed, but the single frozen frontend install timed out during fetching after 1,200 seconds. No component test ran; feasibility remains unconfirmed until a bounded target baseline passes.
  - maintainer_interest_confirmed: Scoped inquiry delivered by humanifest-bot at 2026-09-09T01:38:11Z; no reply or acceptance is established by the outbound message.
  - probable_reviewer_identified: Not established in this initial research intake; inspect relevant evidence before advancing.
  - benefit_justifies_review_cost: Not established in this initial research intake; inspect relevant evidence before advancing.
  - user_can_explain_line_by_line: No implementation or human line-by-line review has occurred.
