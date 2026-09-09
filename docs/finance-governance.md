# Finance Governance

Humanifest is currently fiscally administered by Avaelus LLC/Inc.

This means Avaelus may provide the business bank account, Stripe Connect
identity, bookkeeping support, and administrative handling needed for GitHub
Sponsors payouts while Humanifest is not yet operating through its own dedicated
legal entity, bank account, or fiscal host. This arrangement is temporary and
must stay visible anywhere Humanifest asks for donations.

## Stewardship rules

- Humanifest funds must be tracked separately from Avaelus operating funds.
- Sponsorship income must not buy project ranking, outreach priority, favorable
  scoring, maintainer contact, pull requests, merge outcomes, or public claims
  of impact.
- Humanifest must not imply that donations are tax deductible unless a qualified
  tax-exempt fiscal host or entity has confirmed that status.
- Reimbursements or expenses paid from Humanifest funds must support
  coordination work, reproducible environments, maintainer-approved
  contributions, evidence review, documentation, adversarial review, or
  governance.
- Conflicts of interest must be recorded when a donor, sponsor, Avaelus client,
  contributor, or fiscal steward could benefit from project selection,
  opportunity scoring, public claims, or paid work.
- Private donor information must not be committed to the repository.

## Ledger categories

Use `portfolio/funding-ledger.json` for public aggregate records. The ledger
tracks categories and policy context, not private donor data.

Allowed transaction categories:

- `sponsorship-income`
- `fiscal-admin`
- `engineering`
- `evidence-review`
- `maintainer-coordination`
- `environment`
- `adversarial-review`
- `documentation`
- `governance`
- `reimbursement`
- `reserve`

Allowed conflict statuses:

- `none-known`
- `disclosed`
- `requires-review`

## Oversight

Run finance validation before publishing funding changes:

```bash
python3 -m humanifest.cli finance --root .
```

CI must also run this check. A valid ledger does not establish that the entries
are complete, tax-ready, or legally sufficient; it only checks that public
records follow the current governance contract.

## Review cadence

Publish a plain-language finance update at least monthly when Humanifest receives
or spends sponsorship funds. The update should summarize aggregate income,
expenses by category, reserve balance, fiscal-steward status, conflicts requiring
review, and known limitations.

Owner decisions still required:

- whether Avaelus is LLC, Inc., or another exact legal form for public wording;
- whether to continue with Avaelus, create a Humanifest entity, or move to a
  fiscal host;
- who besides the fiscal steward can approve expenses or conflict resolutions.
