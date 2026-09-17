# OpenCode Feature-Gap Screen

- Date: 2026-09-16
- Target repository: `anomalyco/opencode` (https://github.com/anomalyco/opencode)
- Purpose: decide which of 13 candidate features are genuinely open for a
  low-burden contribution before writing any build plan.
- Method: delegated research subagents fetched the repo README, CONTRIBUTING,
  AGENTS.md, product docs, and performed web searches on 2026-09-16. Claims
  sourced from pages fetched directly are marked `fetched`; claims reported by
  the search agent without an independent re-fetch are marked `secondhand` and
  need confirmation before a build plan relies on them. This screen read
  nothing in the target codebase locally.

## What the target is

OpenCode is an open-source AI coding agent for the terminal. Current iteration
is a TypeScript/Bun monorepo (`fetched`, README/CONTRIBUTING). Interfaces: TUI
(primary), desktop Electron app, web app, IDE extension, headless `serve` +
`attach`, and a `--mini` CLI. Providers are pluggable via Models.dev. The repo
was rewritten from an earlier Go implementation that survives as a separate
project.

Architecture (`fetched` via deepwiki/secondhand summary of AGENTS.md and
`CONTEXT.md`): Turborepo + Bun workspaces; client/server split with a headless
API server and generated SDK clients; heavy use of Effect (services, httpapi,
schema); SQLite (effect-sqlite-bun + Drizzle) for sessions and events; SolidJS
+ OpenTUI for the TUI; Vercel AI SDK providers under custom wrappers. Contract
order is Schema -> Core/Protocol -> Server; after changing the Protocol or
HttpApi run `bun run generate` from `packages/client`.

## Feature coverage / de-duplication matrix

### Already shipped natively (do not build)
- Per-hunk diff review and TUI diff viewer with compare-to-branch (shipped,
  `secondhand` release notes).
- Context/session compaction (`fetched`: `compaction` config, compaction agent,
  plugin compaction hooks).
- GitHub Action / PR bot: `anomalyco/opencode/github@latest`, `opencode github
  install/run`, GitHub App, `/opencode` mention bot, bundled `/review-pr`
  (`fetched`: CONTRIBUTING/product docs).
- Team policy: remote config, managed config files, macOS MDM profile,
  `experimental.policies` (`secondhand`, needs confirmation before relying on
  exact names).
- Session share links via `/share` and programmatic share API (`fetched`:
  product docs).
- Web search `websearch` and `webfetch` tools plus a `scout` subagent
  (`fetched`: CONTRIBUTING/tool docs).

### Covered by active first-party work or crowded plugins (likely redundant)
- Browser automation: first-party browser-control + BrowserHost + native
  Playwright browser tools behind `OPENCODE_ENABLE_BROWSER` are in progress
  (`secondhand`: PR #7302, PR #46531, PR #38626); Playwright MCP is the
  documented standard path (`fetched`).
- Persistent memory: native memory tool PR in flight (`secondhand`: PR #44539);
  10+ community plugins (opencode-memory-plugin, opencode-memfs, supermemory,
  `vestige` MCP, and more, all `secondhand`).
- Voice input: contributor PR open (`secondhand`: PR #29663); community STT
  plugins exist (`secondhand`). Native/TUI voice slot still open in principle.
- Usage dashboards: CLI `opencode stats` ships (`secondhand`); UI dashboards are
  feature requests (`secondhand`: #42295, #38255, #46931). Community dashboards
  already exist (`secondhand`: opencode-stats, @sleipi/opencode-usage-stats,
  opencode-wakatime). Building another dashboard is likely redundant unless it
  targets a native gap.

### Genuinely open candidates
1. Test-fix-test run loop. Only closed issue #4122 was found (`secondhand`);
   nothing active ships a run-tests -> read failures -> fix -> re-run loop.
2. Background/non-blocking bash and asynchronous task dispatch. Multiple open
   issues (`secondhand`: #5887, #28034, #31495, #18372, #30020, #36518, #41914)
   and an experimental background-subagents flag. Engine-adjacent and therefore
   higher risk for a first contribution.
3. Cloud/remote sandbox execution. No OpenCode-managed sandbox found
   (`secondhand`). Heavy lift; likely enterprise-scoped.

## Contribution constraints (target repository)

- Default branch is `dev`; Bun 1.3+; `bun install`, then `bun dev <dir>`
  (`fetched`: CONTRIBUTING).
- Issue-first: every PR must reference an existing issue (`Fixes #...`); PRs
  without a linked issue may be closed without review (`fetched`:
  CONTRIBUTING).
- Any UI or core product feature must pass a design review with the core team
  before implementation; feature PRs that skip it are likely closed (`fetched`:
  CONTRIBUTING). Feature requests start as a design conversation.
- Small + focused PRs; UI changes need before/after screenshots or videos; logic
  changes must state how they were verified (`fetched`: CONTRIBUTING).
- "No AI-generated walls of text": long formulaic PR/issue bodies are rejected
  (`fetched`: CONTRIBUTING). Keep Humanifest-authored descriptions short and
  specific.
- Style (AGENTS.md, `secondhand`): no `else`, no `try/catch` (prefer
  `.catch(...)`), no `any`, Effect-schema parsing over `JSON.parse`, snake_case
  Drizzle fields, branch names <= 3 hyphenated words without `feat/` prefix,
  `bun typecheck` from package dirs, tests never run from the repo root.
- Conventional-commit titles with a package scope (e.g. `feat(tui)`,
  `fix(stats)`).
- Issues must use a template (bug/feature/question); an automated check
  auto-closes non-compliant issues, giving a 2-hour edit window.
- Feature cadence credits external contributors in every release; small
  community PRs land with few review comments (`secondhand`: recent merged PRs).

## Open verification items (do before relying on a build plan)

- Re-fetch CONTRIBUTING.md, AGENTS.md, CONTEXT.md directly and pin the commit.
- Confirm exact current status of: PR #29663 (voice), PR #44539 (memory),
  PR #7302 / #46531 / #38626 (browser), PR #43870 (persistent memory), and the
  open background-task issues (#5887, #28034, #31495, #18372, #30020, #36518,
  #41914).
- Confirm whether a native `websearch` gate exists (tools are gated to specific
  providers per CONTRIBUTING).
- Confirm the closed test-loop issue #4122 and whether "help wanted"/design
  intent remains.
- Verify community plugin/NPM claims below before using them as de-dup
  evidence. These are `secondhand` and may be stale or wrong:
  - `opencode-wakatime`, `opencode-stats`, `@sleipi/opencode-usage-stats`,
    `opencode-browser-control`, `openmemory-plugin` variants, `vestige`,
    `@renjfk/opencode-voice`, `opencode-voice`, `awesome-opencode` directory.

## Honest-scope note

OpenCode is developer tooling (public-benefit open source in the broad sense)
rather than a humanitarian-operations platform. Contributions to it are
defensible under Humanifest's "humanitarian and public-interest" mission but
their humanitarian-benefit score is indirect and must be recorded as such rather
than overstated. The tool's genuine public interest is that it is widely
deployed open-source infrastructure for AI-assisted engineering; a merged,
maintainer-wanted fix helps a large user base at low marginal coordination cost.