# Humanitarian OSS project discovery leads — 2026-09-30

These are **discovery leads**, not audited `portfolio/projects` records or approved
contribution opportunities. The existing portfolio remains 14 projects and 16
opportunities until the project policy and contribution pathway checks are done.
No target code was cloned, run, or changed, and no maintainer was contacted.

## IFRC GO web app — first project audit

- Cause pathway: disaster-risk and response coordination. IFRC describes GO as
  connecting information on emergency needs with the right response. A plausible
  software pathway is more reliable discovery of emergency information; benefit
  from any particular patch is unmeasured.
- [Repository](https://github.com/IFRCGo/go-web-app): public, unarchived,
  MIT, default branch `develop`; GitHub API reported `pushed_at`
  2026-09-30T10:07:42Z when checked on September 30.
- [Contribution guide](https://github.com/IFRCGo/go-web-app/blob/develop/CONTRIBUTING.md)
  welcomes individual contributors and points to issues and PRs. The README
  describes a React/Vite monorepo with submodules, pnpm, and environment setup.
- Candidate issue: [#2532](https://github.com/IFRCGo/go-web-app/issues/2532)
  identifies smart quotation marks in GO API wiki examples that break pasted
  JSON. The issue is open and unassigned; it says the change is not urgent.
  The wiki is outside this frontend repository, so locate its actual edit and
  review pathway before treating this as a code or documentation task.
- Avoid [#656](https://github.com/IFRCGo/go-web-app/issues/656) as a first patch:
  it bundles many search changes and references a private SharePoint sheet.
- Next: inspect the repository and organization contribution, AI, bot, conduct,
  and agreement policies; locate wiki ownership; ask about a bounded wiki fix
  only with target-specific authorization and verified `humanifest-bot`.

### October 7 update: DREF form link bug

- [Issue #2579](https://github.com/IFRCGo/go-web-app/issues/2579), opened
  October 6, reports that question-mark help links in the DREF application
  form point to an outdated Emergency Response Framework. The reporter gives
  the [replacement IFRC PDF](https://www.ifrc.org/sites/default/files/2026-04/IFRC%20Emergency%20Response%20Framework.pdf)
  and identifies the affected population and people-in-need fields. This is
  a bounded disaster-response usability candidate; no operational benefit
  from a future fix is measured.
- Accessed October 7, 2026 UTC: the issue was open, unassigned, and had no
  comments; the public repository was unarchived, MIT-licensed, and reported
  an October 7 push. Its default branch is `develop`. The existing
  [contribution guide](https://github.com/IFRCGo/go-web-app/blob/develop/CONTRIBUTING.md)
  is the initial review path, but current AI/bot policy and any organization
  requirements have not been cleared for this issue.
- A GitHub secondary rate limit stopped the competing-PR search. Do not infer
  that an unassigned issue is unclaimed. Next: inspect the current guide and
  organization policy, check for related open PRs and all affected link
  variants, then request maintainer scope if still needed. Only after those
  checks and specific bot write authority would a small tested patch or PR be
  eligible. No target code was changed or posted in this audit.

### October 7 reserve scan: Avni

- [Avni](https://avniproject.org/about/) describes a field platform for
  community health workers. Its public
  [server repository](https://github.com/avniproject/avni-server) was active
  on October 6, 2026 and is AGPL-3.0. A possible humanitarian pathway is
  more reliable field records, with no measured effect from a proposed patch.
- [Issue #909](https://github.com/avniproject/avni-server/issues/909) concerns
  a future birth date in CSV import, but a maintainer suggested it may already
  be fixed and another contributor reported a fix PR. [Issue #968](https://github.com/avniproject/avni-server/issues/968)
  concerns last-name validation in CSV import, but contributors have already
  claimed or requested the work. Neither is an unclaimed donation target.
- Next: find a fresh, unclaimed, bounded issue and check repository and
  organization contribution and AI/bot policy, competing work, test path,
  reviewer availability, and private-data dependence before promotion.

## OpenFn Lightning — second project audit

- Pathway: public-benefit service data integration. The project describes
  Lightning as workflow automation and interoperability used by NGOs and
  governments; no project-wide benefit is attributed to a future patch.
- [Repository](https://github.com/OpenFn/lightning): public, unarchived,
  GitHub API license `LGPL-3.0`, default branch `main`; API reported `pushed_at`
  2026-09-30T13:54:11Z when checked on September 30. The repository page also
  mentions GPL-3.0 files, so inspect file-level licensing before any patch.
- [Contribution instructions](https://github.com/OpenFn/lightning#contribute-to-this-project)
  tell contributors to choose an issue, announce work, write tests and a
  changelog entry, and submit a draft PR. Local setup includes Elixir/Erlang,
  PostgreSQL, bootstrap steps, and migrations; none was run.
- Candidate issue: [#5197](https://github.com/OpenFn/lightning/issues/5197)
  is an open, unassigned report that the GitHub sync UI says a new action will
  be committed to `main` even when a non-main branch is selected. The reporter
  is unsure whether the underlying behavior changed. The contract must be
  clarified before changing UI copy or tests.
- Next: inspect organization and repository AI/bot policies and the issue's
  relevant code/reviews; verify the intended GitHub sync behavior without live
  credentials before requesting maintainer scope. Do not run bootstrap or DB
  migrations on this discovery evidence.

## SORMAS — reserve lead

- Pathway: infectious-disease surveillance and outbreak response. The
  [project repository](https://github.com/SORMAS-Foundation/SORMAS-Project)
  describes web and mobile apps for this work. This is a broader public-health
  lead, not a confirmed fit for the four current cause records.
- Public, unarchived, GPL-3.0, default branch `development`; GitHub API reported
  `pushed_at` 2026-09-30T17:08:20Z when checked on September 30.
- The README points to mandatory contributing and development guides. Recent
  [issues](https://github.com/SORMAS-Foundation/SORMAS-Project/issues) include
  assigned disease-specific work. Do not claim an open task merely from issue
  count; find an unclaimed, bounded issue and inspect policy and reviewer path.
- Next: connect this lead to a current cause hypothesis or create a separately
  evidenced cause proposal through the governed route, then audit contribution
  policy before any test setup.

## Discovery rule for the scheduled cycle

After GitHub inbox review, reserve a bounded discovery pass on each run. Follow
the highest-priority evidenced cause pathway; search primary project/repository
sources for active OSS and current issues; deduplicate against portfolio and
earlier lead notes. Record a lead only with its URL, access date, humanitarian
pathway, current activity, plausible bounded task, contribution/policy unknowns,
and next verification step. Promote a lead to a project record only after the
repository and organization policy screen and required Orca/source-of-truth
route. Promote an issue to an opportunity only after checking current ownership,
existing PRs, affected subsystem, and maintainer review path. No discovery
quota grants permission to contact maintainers, implement, or open a PR.
