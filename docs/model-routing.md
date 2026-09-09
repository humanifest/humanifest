# Model Routing

Primary Codex owns portfolio decisions, synthesis, source-of-truth updates, root-cause analysis, implementation integration, and final go/no-go decisions.

Use Orca, the repo-orchestrator workflow, when a task spans project governance,
public positioning, donation ethics, contribution policy, maintainer
communication, licensing, source-of-truth updates, and downstream handoffs. Orca
must identify the controlling files before work begins, keep external-write
authorization separate from ordinary documentation edits, and leave a durable
handoff when the next step is not immediately executed.

Finance and sponsorship changes must also route through Orca unless they only add
ledger entries that already satisfy `docs/finance-governance.md`.

Use faster Codex or Spark for bounded, independently verifiable work:

- test or lint fixes with known failures;
- mechanical documentation updates from named authority files;
- data extraction;
- narrow review;
- handoff generation.

Use Cursor or another independent model for:

- IDE-native inspection;
- frontend interaction;
- second-family critique;
- adversarial review of a proposed diff.

Open-source enablement and sponsorship changes are not merely marketing edits.
They can change who contributes, whether outside work is accepted, how conflicts
of interest are handled, and how much burden reaches upstream maintainers. Route
those tasks through Orca unless they are narrow text-only edits against already
approved policy.

Every delegated prompt must include objective, context, exact scope, authority
files to read, files and actions not to touch, acceptance criteria, verification
commands, constraints, stopping condition, and required return format.
