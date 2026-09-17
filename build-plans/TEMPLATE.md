# Build Plan: {{FEATURE_NAME}}

> Copy `build-plans/TEMPLATE.md`, replace every `{{PLACEHOLDER}}`, then link the
> research screen in `research/` that justified starting. Keep claims honest:
> mark what was directly fetched versus secondhand, record access dates, and do
> not assert maintainer interest that was never confirmed.

## Metadata

- Plan id: `{{PLAN_ID}}` (e.g. `opencode-test-fix`)
- State: `DRAFT | RUNNING | HOLD`
- Target repository: `{{OWNER/REPO}}`
- Feature: {{ONE-LINE DESCRIPTION}}
- Commissioned by: {{WHO}} on {{YYYY-MM-DD}}
- Research screen: `research/{{DATE}}-{{SCREEN-SLUG}}.md`
- Upstream issue to link the PR to: {{ISSUE URL or "open new feature issue"}}

## 1. Research Digest & De-duplication

> Answer these in 2-5 lines each. Cite the screen and note `fetched` vs
> `secondhand` for anything the plan relies on.

- Does it ship natively today? {{YES/NO + details}}
- Active first-party PR or branch? {{NONE / link}}
- Crowded community plugin/MCP/skill coverage? {{NONE / links}}
- Is explicit design-review approval required before implementation?
  {{YES/NO + who approves + how to request}}

## 2. Target Repository Constraints

{{Branch, runtime/version, install+tests commands, contribution guide rules
(issue-first, design review, PR size, screenshots, AI-text policy), style
guide, title convention. Pin the commit/documents reviewed.}}

Verification commands used in this plan:

- Install: `{{...}}`
- Type/lint: `{{...}}`
- Unit tests: `{{...}}`
- Targeted tests: `{{...}}`
- Snapshot/UI tests (if applicable): `{{...}}`

## 3. Feasibility Assessment

Map the slice to Humanifest hard gates. Fill only what is known today; leave
the rest as open questions, not assumed passes.

| Gate | Today | Evidence / open question |
| --- | --- | --- |
| humanitarian_relevance_supported | {{T/F/?}} | {{honest note on indirect benefit}} |
| repository_active | {{T/F/?}} | {{last activity / issue recency}} |
| external_contributions_accepted | {{T/F/?}} | {{contributing docs}} |
| contribution_policy_understood | {{T/F/?}} | {{link, date}} |
| ai_policy_understood | {{T/F/?}} | {{AI disclosure rules, date}} |
| problem_current_and_consequential | {{T/F/?}} | {{issue is open? consequential?}} |
| behavior_reproducible_or_verifiable | {{T/F/?}} | {{can we run tests?}} |
| code_and_tests_located | {{T/F/?}} | {{file paths, commit/pin}} |
| change_bounded | {{T/F/?}} | {{smallest first slice defined?}} |
| regression_strategy_credible | {{T/F/?}} | {{tests encode the new behavior?}} |
| no_private_data_required | {{T/F/?}} | {{}} |
| security_and_licensing_risk_acceptable | {{T/F/?}} | {{}} |
| environment_feasible | {{T/F/?}} | {{bun install + run OK?}} |
| maintainer_interest_confirmed | {{T/F/?}} | {{real confirmation, linked}} |
| probable_reviewer_identified | {{T/F/?}} | {{}} |
| benefit_justifies_review_cost | {{T/F/?}} | {{}} |
| user_can_explain_line_by_line | {{T/F/?}} | {{}} |

First-slice working score inputs: humanitarian_benefit {{0-5}},
acceptance_probability {{0-5}}, technical_confidence {{0-5}},
review_burden {{0-5}} (lower = better), deployment_probability {{0-5}}.

## 4. Workstreams

> Each phase must have an exit criterion that a background loop can check
> without the user, or explicitly name the human gate.

- **Phase 0 - Design & issue**: open/refresh the feature issue, request design
  review, get an explicit go/no-go. Exit: issue exists with a scoped design and
  core-team intent. Human: approval.
- **Phase 1 - Baseline**: clone on `dev`, pin commit, install, run full test +
  typecheck suites. Exit: baseline green, commands recorded verbatim.
- **Phase 2 - Prototype slice**: build the smallest bounded change inside the
  repo with tests and docs. Exit: targeted tests green, `bun typecheck` clean.
- **Phase 3 - Adversarial review**: review correctness, scope, security, test
  gaps, maintainer burden; check CONTRIBUTING compliance (title, issue link,
  screenshots for UI, verification notes). Exit: checklist satisfied.
- **Phase 4 - Human review**: user reads the diff line by line. Exit: user sign-
  off, standing authorization confirmed, portfolio capacity rechecked.
- **Phase 5 - PR**: open the PR via the verified Humanifest identity, reference
  the issue. Exit: PR open; background loop only handles replies within
  authorization.
- **Phase 6 - Follow-up**: respond to review, revise, track merge. Exit:
  merged / parked / declined recorded honestly.

## 5. PR Plan

- Title (conventional-commit + scope): `{{feat(tui): ...}}`
- Issue linked: `Fixes #{{N}}`
- Files expected (first slice): {{list, keep tiny}}
- Docs to update: {{if any}}
- Verification statement to include: {{1-3 concrete commands + result}}
- Screenshots/recording (UI only): {{yes/no + where}}

## 6. Risk Register

| Risk | Likelihood | Impact | Mitigation |
| --- | --- | --- | --- |
| {{e.g. maintainer wants larger scope}} | {{}} | {{}} | {{}} |
| {{e.g. competing native PR appears}} | {{}} | {{}} | {{re-screen before BUILDING}} |
| {{e.g. design review rejects approach}} | {{}} | {{}} | {{do design in issue first}} |
| {{e.g. tool loop behavior flaky across repos}} | {{}} | {{}} | {{}} |

## 7. Background Execution Loop

What a scheduled operator can do without the user:

- {{refresh status sources / re-run verifications / regenerate reports}}
- {{produce the next handoff}}

What always needs the user:

- {{design-review sign-off, scope approval, human review, PR authorization}}

Cadence: {{}}
Stopping conditions: {{park if stale/assigned/competing/too broad; do not
"fix" a foreign repo's process}}.

## 8. Records & Status

- Project record: `portfolio/projects/{{owner}}.json` {{new/updated, id}}
- Opportunity records: {{per-slice list, pipeline states}}
- Research notes: {{dated md files}}
- Portfolio capacity at start: active=0/1, PRs=0/2 (must be rechecked at each
  phase transition).

## Changelog

- {{YYYY-MM-DD}} State {{DRAFT -> RUNNING}}; {{what happened}}.