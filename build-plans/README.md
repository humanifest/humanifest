# Build Plans

A build plan turns a researched, de-duplicated feature idea into a background
goal that a Humanifest-style operator can pursue without constant supervision.

## Lifecycle

A plan is only started after a dated research screen (in `research/`) answers:
- Does the feature already ship natively?
- Is a first-party PR, native PR, or crowded community plugin already covering
  the same surface?
- Does the target repository require a design review before implementation?
- Is the first PR-shaped slice small, focused, and issue-linked?

Plans proceed in three states:

1. `DRAFT` - research done, plan written, not yet commissioned.
2. `RUNNING` - one phase is active and tracked as a Humanifest opportunity
   record; the background loop advances it.
3. `HOLD` - stopped at a gate (design review pending, maintainer silence,
   competing work, benefit no longer justifies cost). Parking is a result, not
   a failure.

## Handoff to Humanifest records

Each plan's `Records & Status` section names the JSON records that carry it
through the normal pipeline:

- `portfolio/projects/<owner>.json` - audited project record (audience,
  license, contribution pathway, AI policy), created once per target
  repository.
- `portfolio/opportunities/<feature>-<id>.json` - one per feature slice, with
  gates, evidence, sources, and pipeline state. Portfolio capacity limits (one
  active implementation, two external PRs, one per organization) bind at most
  one `BUILDING` plan at a time.
- `research/YYYY-MM-DD-*.md` - dated, cite-able evidence for gate rationales.

The build plan document itself is the playbook; the JSON records are the
authoritative pipeline state.

## Who does what

- **Background loop** (scheduled, read-only where possible): refresh sources,
  re-run verifications, regenerate reports, check status gates, produce the
  next handoff.
- **User**: design-review approval, scope sign-off, final line-by-line review
  before `PR-OPEN`, and explicit authorization for any external write.
- **Verified Humanifest identity** (`humanifest-bot`): all external writes,
  never the user's personal account.

## Directory

- `TEMPLATE.md` - reusable skeleton for a new plan.
- `opencode-test-fix-command.md` - working example (test-fix loop for OpenCode).