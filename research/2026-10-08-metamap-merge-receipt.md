# Metamap refresh and main-merge receipt — 2026-10-08

Status: **draft PR; merge blocked by stale generated projection**. This receipt
records observed execution, not Humanifest or Orca acceptance.

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
- The pinned `@roryscot/metamap@0.5.0` package is absent from
  `tools/metamap/node_modules`. The documented `npm ci --ignore-scripts
  --no-audit --no-fund --prefix tools/metamap` would write ignored dependencies
  and npm cache and may access GitHub/npm. Its separate installation approval
  is pending. No package installation or projection generation was run.

## Remote and scheduler state

- Committed the exclusion change as `40743db` with bot attribution, then pushed
  it non-force to `codex/inbox-contributions-2026-10-07` through the
  identity-guarded `humanifest-bot` connection.
- Opened [draft PR #5](https://github.com/humanifest/humanifest/pull/5) against
  `main`; GitHub reported `humanifest-bot` as author and head `40743db` when
  checked. Both required Python matrix checks failed at
  `stale generated artifact: portfolio.json`. No merge occurred.
- Updated the existing ACTIVE, chat-attached daily Humanifest schedule through
  the Codex automation tool. When all 16 portfolio opportunities remain gated,
  it now prioritizes a substantive search across distinct current projects or
  cause pathways, a complete policy/review-path audit for the best lead, and
  follow-up on IFRC GO #2579. The existing GitHub inbox, exact bot authority,
  and Gmail deferral boundaries were preserved. Future execution remains to be
  observed; the prompt update itself is not a donation.

## Next checks before merge

1. Once the pinned package installation is approved, regenerate and check all
   `metamap/generated/` outputs and `portfolio/status.md`.
2. Run the full test and validation commands in `AGENTS.md` with umask 077 and
   record actual results. Address any real failures without weakening gates.
3. Push the generated artifacts using verified `humanifest-bot`, wait for both
   required PR checks to pass, review the final diff, then merge PR #5 as
   requested. Leave Orca/source-of-truth acceptance separate from GitHub merge.
