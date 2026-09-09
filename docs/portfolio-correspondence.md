# Derived portfolio correspondence

Humanifest's Python exporter emits a portable Metamap v0.5.0 shard from current
project and opportunity records. The existing native states, hard gates, evidence
types, scoring, capacity validation and protocol remain authoritative. A viable
generation establishes local correspondence, not truth, maintainer confirmation,
authenticated identity, permission to act, or humanitarian impact.

## The consumer and removed crosswalk

The CLI `report` and `handoff` paths consume the immutable compiled opportunity
projection. Their state-to-guidance lookup now comes from projected action links;
they no longer each route through the native state lookup while rendering. The
single native catalog in `humanifest/workflow.py` also serves standalone briefs
and lower-level pure rendering helpers. Closed state/gate values stay native.
The duplicated handoff-target crosswalk (CLI target choices plus renderer branches)
has been replaced by `HANDOFF_ROUTES` and compiled `hf:handoff_route` links. The
CLI renderer consumes projected route instructions; adding a destination changes
one catalog rather than several lists and conditionals. There is no second
hand-maintained opportunity-to-project or gate-name catalog.

The exporter binds project, opportunity, gate rationale, evidence item, source,
maintainer-confirmation record, proposed contribution, report, handoff, actor and
workflow-guidance identities to their current authority. Contribution identities
reflect recorded state, not proof of delivery. Workflow action handlers are
non-executable guidance references. `humanifest-bot` is a required identity
reference, not an authentication assertion; external writes still require live
identity verification and the actual applicable authorization.

The domain pack supplies project, provenance, gate/prerequisite, output and
current-record relationships. Metamap's routing pack supplies action-to-handler,
schema and policy relationships. Selector declarations cover whole relation
families; newly discovered members inherit coverage. Dynamic totality constraints
and a small `hf:exact-authority` evaluator reject broken references, incomplete
native gate sets, cross-record citations, detached outputs, and missing policy or
actor linkage. A passing maintainer gate must cite the record's own sources.
Other uncited gates remain uncited; the exporter never fabricates evidence or
upgrades a recorded claim to verified fact.

## Generate and check

```sh
npm ci --ignore-scripts --no-audit --no-fund --prefix tools/metamap
python3 -m scripts.compile_correspondence
python3 -m scripts.compile_correspondence --check
python3 -m unittest
python3 -m humanifest.cli validate --root .
python3 -m humanifest.cli report --root .
```

The compiler is pinned to the public v0.5.0 archive and its lockfile integrity.
Installation disables lifecycle scripts. It uses Node 22.12+; no target setup,
network, credentials or native source execution occurs during compilation.
The fixed compiler evaluation instant is September 9, 2026 UTC for reproducible
artifacts. No temporal waivers or live authorization are evaluated here.

`metamap/generated/` contains the portable shard, domain relation pack,
selector-based viability policy, projection specification, and the viable
generation/projection bundle. Generation writes only after successful compilation;
each output is replaced atomically. The runtime bundle is self-contained, so it
does not depend on reading intermediate outputs during replacement. CI recompiles
and compares every artifact without accepting changes.

Python report/handoff consumers need neither Node nor a graph traversal. They
check the complete input inventory and content fingerprints, projection checksum,
exact current opportunity/project authority, policy identity and workflow guidance,
then expose a read-only mapping. New/deleted records or changed controls invalidate
the projection. Checksums detect drift; they are not signatures or a defense
against an attacker who can replace both code and artifacts. Source URL contents
and claims are not refreshed or verified by these checks.

A CLI handoff must point to a file in the authoritative portfolio, with `--root`
when it cannot be inferred. Detached copies cannot masquerade as current handoffs.
Standalone `score` and `brief` still validate individual records without establishing
portfolio capacity. Pure Python rendering helpers remain lower-level interfaces;
they do not independently establish the complete portfolio correspondence.

## Authored prompts and exclusions

Existing Markdown prompts in `handoffs/` are authored reusable material, not
assertions that they were generated from today's record. Each is explicitly
excluded only from `hf:current_record` in `metamap/exclusions.json`, with a reason,
responsible repository owner and exact content digest. The guarded CLI is the path
for generating current record handoffs. These exclusions do not waive contribution
gates, authorization, source provenance, or implementation review.

The exporter rejects missing/duplicate exclusions, blank reasons or owners,
changed content, deleted excluded files and unknown relation scope. Metamap rejects
excluded subjects that are simultaneously mapped in the excluded relation.
Generated portfolio reports/handoffs cannot use these exclusions. Empty and
overlapping viability selectors reject compilation. Refreshing an authored prompt's
exclusion requires reviewing its scope and current contents; do not auto-refresh
exclusions as part of routine compilation.

Mutation tests exercise new unlinked opportunities, missing project/source paths,
uncited passing confirmation, missing individual gates and prerequisites, absent
policy/identity edges, detached handoffs, stale projections/exclusions and selector
errors. Valid compilation and the actual CLI consumers are tested as well.
