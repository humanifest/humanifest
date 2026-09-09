# Orca Open-Source Governance Handoff

Objective: keep Humanifest's open-source, sponsorship, and public-contribution
work aligned with the repository authority model and maintainer-burden
constraints.

Use this handoff for changes involving public onboarding, donations, GitHub
Sponsors, licensing, governance, contributor permissions, maintainer outreach,
project selection influence, or claims about humanitarian impact.

Authority files to read first:

- `AGENTS.md`
- `GOALS.md`
- `README.md`
- `CONTRIBUTING.md`
- `docs/contribution-protocol.md`
- `docs/governance.md`
- `docs/licensing.md`
- `docs/impact-methodology.md`
- `docs/model-routing.md`
- `docs/finance-governance.md`
- `portfolio/funding-ledger.json`
- `.github/FUNDING.yml`, when present

Complexity to preserve:

- Humanifest is MIT licensed; inbound contributions still need DCO signoff unless
  a later CLA process is adopted.
- Donations support coordination capacity, not project ranking, outreach priority,
  guaranteed pull requests, merge outcomes, or favorable scoring.
- Humanifest is currently fiscally administered by Avaelus LLC/Inc.; funding
  records must keep Humanifest funds separate from Avaelus operating funds.
- External maintainer contact, issue comments, upstream pull requests, and other
  external writes require explicit authorization and the verified Humanifest
  identity.
- Contribution pathways should include evidence refreshes, negative findings,
  gate review, documentation, tests, adversarial review, and tooling, not only
  implementation.
- Humanifest must keep maintainer burden, conflicts of interest, source
  provenance, and impact uncertainty visible in public-facing material.
- Do not advance records, gates, or pipeline states merely because public
  documentation, funding configuration, or contributor onboarding changed.

Scope:

- Update policy and onboarding documents only when they agree with the authority
  files above.
- Add or revise job cards when future agents need repeatable routing.
- Keep donation and sponsorship language non-transactional and conflict-aware.

Files and actions not to touch without explicit authorization:

- Do not contact external maintainers.
- Do not post issue comments or open upstream pull requests.
- Do not create package releases or repository publications.
- Do not change project or opportunity pipeline states unless evidence supports
  the transition under the contribution protocol.
- Do not resolve the repository license choice on behalf of the owner.

Acceptance criteria:

- Public docs distinguish Humanifest repository contributions from upstream
  humanitarian project contributions.
- Sponsorship language cannot reasonably be read as paid prioritization.
- Fiscal-steward, ledger, and conflict language remain consistent with
  `docs/finance-governance.md`.
- Contributor guidance invites useful negative findings and evidence-preserving
  review.
- External-write constraints remain visible.
- The model routing doc identifies Orca as the driver for cross-policy,
  governance, donation, and public-positioning work.

Verification:

```bash
python3 -m unittest
python3 -m humanifest.cli validate --root .
python3 -m humanifest.cli finance --root .
python3 -m humanifest.cli report --root .
```

Return format:

- Driver used and why.
- Files changed.
- Policy complexity preserved.
- Commands run and results.
- Remaining owner decisions.
