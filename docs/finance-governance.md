# Finance Governance

Humanifest funding supports coordination work that lowers maintainer burden:
evidence review, reproducible environments, source refreshes, adversarial review,
accessibility or security checks, and small approved upstream contributions.

Funding is not a purchase of priority, rankings, outreach, maintainer attention,
or a guaranteed contribution. Sponsorship may not override the gates in
`docs/contribution-protocol.md`.

## Required Checks

Before spending or allocating funds, verify:

- the transaction appears in `portfolio/funding-ledger.json`;
- the purpose is public-interest or humanitarian coordination work;
- the expense is proportionate to the evidence quality and current pipeline state;
- no donor, sponsor, or contributor is being given unsupported influence over project selection;
- paid compute or services also pass `docs/compute-governance.md` when applicable;
- the resulting work remains reproducible, traceable, and explainable.

If the purpose is unclear, record the uncertainty instead of spending.

## Ledger Rule

The funding ledger is a public accountability record, not an accounting system.
Entries should preserve date, amount, type, status, and purpose. Private payment
instrument details, donor addresses, tax identifiers, and similar sensitive data
must not be recorded here.

Use `python3 -m humanifest.cli finance --root .` before relying on recorded
funds for a Humanifest task.
