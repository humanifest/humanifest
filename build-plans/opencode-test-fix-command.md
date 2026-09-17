# Build Plan: Opencode Test-Fix Command

> First commissioned example. Research screen:
> `research/2026-09-16-opencode-feature-gap-screen.md`.

## Metadata

- Plan id: `opencode-test-fix`
- State: `DRAFT` (research done; design-review approval still required)
- Target repository: `anomalyco/opencode`
- Feature: a first-class `/test-fix` command (and/or `build` subagent option)
  that runs the project's test command, reads failures and stack traces, edits,
  re-runs the failing subset, and loops to green before presenting the final
  diff and full-suite result.
- Commissioned by: user (roryscot) on 2026-09-16
- Research screen: `research/2026-09-16-opencode-feature-gap-screen.md`
- Upstream issue to link the PR to: closed #4122 exists; this needs a NEW open
  feature issue (closed issues may not satisfy the issue-first rule). Compare
  with #4122 in the design conversation and reference it.

## 1. Research Digest & De-duplication

- Ships natively today? No (`secondhand`: only closed #4122; nothing active).
- Active first-party PR? No known open PR for a test-fix loop (`secondhand`).
- Crowded plugin coverage? No plugin/skill named for this surfaced in the
  ecosystem screen (`secondhand`); users work around it with `plan`+`build` and
  a bash test loop, which is exactly the friction the command addresses.
- Design review required before implementation? YES - this is a core-product
  command surface. A feature issue must start a design conversation and get
  core-team intent before any PR (`fetched`: CONTRIBUTING).

## 2. Target Repository Constraints

Default branch `dev`; Bun 1.3+; monorepo with Turborepo + Bun workspaces.
Contribution rules (`fetched` via CONTRIBUTING, need re-fetch + pin):
issue-first PRs (`Fixes #N`), small+focused, UI change needs screenshots/video,
logic change states how it was verified, no AI-generated walls of text, design
review before UI/core feature PRs. Style (`secondhand` via AGENTS.md): no
`else`, prefer `.catch(...)` over `try/catch`, no `any`, Effect-schema parsing,
`bun typecheck` from package dirs, tests not run from repo root. Titles:
`feat(opencode): ...` style with package scope.

Verification commands used in this plan:

- Install: `bun install`
- Typecheck: `bun run typecheck` (from `packages/opencode` and wherever the
  change lands)
- Unit tests: `bun run test` in the affected package dir
- Targeted: single-spec runs for the new command/subagent
- Baseline of the full suite before and after the change

## 3. Feasibility Assessment

| Gate | Today | Evidence / open question |
| --- | --- | --- |
| humanitarian_relevance_supported | T (qualified) | Public-benefit developer infrastructure at large scale; indirect, must not overclaim |
| repository_active | T | ~15k commits, releases through v1.18.x (`secondhand`) |
| external_contributions_accepted | T | contributing docs; community PRs merge each release (`fetched`/`secondhand`) |
| contribution_policy_understood | T | issue-first, design review, small PRs, AI-text ban (`fetched`) |
| ai_policy_understood | ? | check repo AGENTS.md/SECURITY.md for disclosure expectations; record date |
| problem_current_and_consequential | T (mostly) | test-fix friction is a recurring user ask; still need an open feature issue |
| behavior_reproducible_or_verifiable | T | a failing-fixture repo reproduces the loop; snapshot tests exist for TUI |
| code_and_tests_located | ? | candidates: `packages/opencode/src/command/`, `packages/opencode/src/agent/`, tool registry `packages/opencode/src/tool/registry.ts`; must pin |
| change_bounded | T (draft) | first slice is command + adaptive test-runner + loop for one common runner config |
| regression_strategy_credible | T | unit tests for the loop against a tiny fixture project |
| no_private_data_required | T | fixture repo only |
| security_and_licensing_risk_acceptable | T | no secrets; MIT-licensed target |
| environment_feasible | T | local Bun workspace; verify before BUILDING |
| maintainer_interest_confirmed | ? | NEEDS design-review + maintainer intent via new feature issue |
| probable_reviewer_identified | ? | from the design conversation; not yet known |
| benefit_justifies_review_cost | T (draft) | recurring ask, small surface; confirm with maintainers |
| user_can_explain_line_by_line | T (draft) | keep first slice small enough |

First-slice working score inputs: humanitarian_benefit 1.5 (indirect),
acceptance_probability 3.0, technical_confidence 3.0,
review_burden 2.0, deployment_probability 3.0.

## 4. Workstreams

- **Phase 0 - Design & issue** (current): draft the feature issue, reference
  closed #4122, propose the bounded scope, request design review. Exit:
  open feature issue plus explicit core-team intent on the scope. HUMAN GATE.
- **Phase 1 - Baseline**: clone on `dev`, pin commit, `bun install`, run
  typecheck + full test suites, record exact commands and pass counts. Exit:
  green baseline recorded in a research note (`secondhand` ok for commands,
  `fetched` for the pinned commit).
- **Phase 2 - Prototype**: implement the command + loop against a fixture repo
  (detect test command from package.json/make/other common runners; cap loop
  iterations; fail closed on repeated identical failures; emit summary + diff).
  Add unit tests. Exit: targeted tests green, typecheck clean, manual repro on
  a fixture that fails then passes.
- **Phase 3 - Adversarial review**: check scope, loop termination, permission
  behavior (does it need new tool permissions or reuse `bash`?), PR compliance
  (title, issue link, verification notes). Exit: checklist satisfied.
- **Phase 4 - Human review**: user reads the diff line by line; standing
  authorization + portfolio capacity rechecked. Exit: sign-off.
- **Phase 5 - PR**: open via `humanifest-bot`, `Fixes` the new issue, short
  self-verification note, no boilerplate. Exit: PR open.
- **Phase 6 - Follow-up**: respond within authorization, revise, track merge.

## 5. PR Plan

- Title: `feat(opencode): add test-fix command` (confirm exact scope with core)
- Issue linked: `Fixes #{{NEW_FEATURE_ISSUE}}` (references #4122 in body)
- Files expected (first slice): command module + a couple of unit tests;
  possibly a small TUI/palette entry only if design requires it. Keep tiny.
- Docs to update: `packages/web` docs page for commands if one exists.
- Verification to include: 3 concrete commands + results (baseline suite,
  targeted spec, typecheck).
- Screenshots/recording: only if the TUI palette/palette entry changes.

## 6. Risk Register

| Risk | Likelihood | Impact | Mitigation |
| --- | --- | --- | --- |
| Maintainer wants broader scope (all runners) | Med | High | Lock "one common runner + adapter seam" in the design conversation |
| Test command detection is flaky across repos | Med | Med | Fixture-driven tests; documented detection order; opt-in override |
| Loop needs new tool permissions / doom-loop guard interplay | Low-Med | Med | Reuse `bash`; verify permission rules with core during design |
| Competing native PR appears mid-plan | Low | Med | Re-screen before BUILDING; park if merged |
| Design review rejects the approach | Med | High | Do design in the issue first; keep PR size small to reduce churn |

## 7. Background Execution Loop

Without the user (scheduled): refresh issue/design status, re-run baseline
verifications on `dev`, regenerate this plan's status, prepare the next
handoff for phase transitions.

Always needs the user: design-review sign-off (Phase 0), final line-by-line
human review (Phase 4), explicit PR authorization (Phase 5).

Cadence: nightly status + weekly re-screen against the ecosystem while in
DRAFT; nightly baseline runs once RUNNING.

Stopping conditions: park if the issue stays without core-team intent > 30
days after posting, is assigned elsewhere, a first-party PR lands, or the
approved scope exceeds the bounded slice we can explain line by line. Do not
"fix" OpenCode's own process friction uninvited.

## 8. Records & Status

- Project record: `portfolio/projects/opencode.json` - create on commission
  (audit human-policy, project activity, AI contribution stance; record access
  date).
- Opportunity record: `portfolio/opportunities/opencode-test-fix-loop.json` -
  create at Phase 1 start with `pipeline_state: QUEUED|PROJECT-AUDIT`, all
  gates from section 3, and source entries pointing at the pinned CONTRIBUTING,
  the new issue, and this screen.
- Research notes: this screen + `2026-09-16-opencode-baseline.md` (Phase 1) +
  design-conversation notes (Phase 0).
- Capacity at start: active=0/1, PRs=0/2, one per organization - recheck at
  each phase transition.

## Changelog

- 2026-09-16 State DRAFT created; research screen complete; de-duplicated
  against diff-review/compaction/GH-bot/team-policy/memory/browser/voice twins;
  design review identified as the required human gate before implementation.