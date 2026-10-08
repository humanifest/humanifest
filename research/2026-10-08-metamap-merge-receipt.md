# Metamap refresh and main-merge receipt — 2026-10-08

Status at this revision: **Metamap regenerated and local checks passed; draft
PR checks and merge pending**. This receipt records observed execution, not
Humanifest or Orca acceptance.

## Scope and inputs

- User requested an updated Metamap projection, merge to `main`, and a stronger
  scheduled search for useful humanitarian OSS work.
- Effective local user: `legion`; checkout:
  `/Users/legion/dev/humanifest/humanifest`.
- The branch already contained four commits ahead of `origin/main`. The
  repository rules rejected a direct `main` push and require a PR and two
  status checks. No force push or personal GitHub identity was used.

## Local Metamap work

- Reviewed the three newly authored handoffs and added their exact path,
  SHA-256 digest, reason, owner, and `hf:current_record` exclusion to
  `metamap/exclusions.json`. These are authored plans, not generated current
  portfolio handoffs.
- Ran `PYTHONDONTWRITEBYTECODE=1 python3 -c 'from pathlib import Path; from
  humanifest.correspondence import export_shard; s=export_shard(Path("."));
  print(len(s["graph"]["entities"]))'` with umask 077. Result: **861 entities;
  exit 0**. This reads project controls and records; it writes no repository
  files. `git diff --check` passed.
- After the user approved the blocked Metamap generation and merge, ran
  `npm ci --ignore-scripts --no-audit --no-fund --prefix tools/metamap --cache
  /Users/legion/Documents/Codex/Humanifest/npm-cache` with umask 077. Result:
  **8 pinned packages installed; exit 0**. This wrote ignored
  `tools/metamap/node_modules` and an external npm cache, accessed the package
  sources, and skipped lifecycle scripts. No target project setup or service
  ran.
- Ran `PYTHONDONTWRITEBYTECODE=1 python3 -m scripts.compile_correspondence`:
  **exit 0**. It regenerated the five `metamap/generated/` outputs atomically;
  three differ from the previous checked-in files. Generated
  `portfolio/status.md` from `humanifest.cli report --root .` after successful
  CLI execution; the report matches its checked-in bytes.
- With umask 077, `python3 -m scripts.compile_correspondence --check` passed;
  `python3 -m unittest` passed **89 tests**; `humanifest.cli validate`,
  `finance`, `compute`, and `operate` each exited 0. The checked-in report
  comparison and `git diff --check` passed. The local Python environment lacks
  `jsonschema`, so `scripts.check_schemas` was not run locally; CI installs its
  pinned check dependencies and runs it. The local installed-wheel smoke check
  was also left to CI rather than installing another local package.

## Remote and scheduler state

- Committed the exclusion change as `40743db` with bot attribution, then pushed
  it non-force to `codex/inbox-contributions-2026-10-07` through the
  identity-guarded `humanifest-bot` connection.
- Opened [draft PR #5](https://github.com/humanifest/humanifest/pull/5) against
  `main`; GitHub reported `humanifest-bot` as author. Both required Python
  matrix checks on the prior head failed at
  `stale generated artifact: portfolio.json`. The regenerated artifacts have
  not yet been checked on GitHub at this receipt revision. No merge occurred.
- Updated the existing ACTIVE, chat-attached daily Humanifest schedule through
  the Codex automation tool. When all 16 portfolio opportunities remain gated,
  it now prioritizes a substantive search across distinct current projects or
  cause pathways, a complete policy/review-path audit for the best lead, and
  follow-up on IFRC GO #2579. The existing GitHub inbox, exact bot authority,
  and Gmail deferral boundaries were preserved. Future execution remains to be
  observed; the prompt update itself is not a donation.

## Next checks before merge

1. Push the generated artifacts using verified `humanifest-bot`, wait for both
   required PR checks to pass, review the final diff, then merge PR #5 as
   requested. Leave Orca/source-of-truth acceptance separate from GitHub merge.
