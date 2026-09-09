# Compute Governance

Humanifest may use donated, free, sponsored, or paid compute resources to reduce
coordination cost and increase review quality. Compute is treated like money:
the source, permitted use, limits, and conflicts must be visible before it
drives project selection, implementation, or maintainer-facing work.

GitHub Copilot is an allowed compute source when used through an account or
organization seat that is permitted to use it. GitHub currently documents
Copilot Free as including limited monthly completions and premium requests with
no subscription, and states that Copilot Free is intended for personal use only,
not managed organization or enterprise users. Humanifest must not pool personal
free accounts, share credentials, evade usage limits, or use free allowances as
a reason to increase maintainer burden.

Sources accessed 2026-09-09:

- GitHub Docs, [About individual GitHub Copilot plans and benefits](https://docs.github.com/en/copilot/managing-copilot/managing-copilot-as-an-individual-subscriber/getting-started-with-copilot-on-your-personal-account/about-individual-copilot-plans-and-benefits)
- GitHub Docs, [Setting up GitHub Copilot for yourself](https://docs.github.com/en/copilot/how-tos/copilot-on-github/set-up-copilot/enable-copilot/set-up-for-self)

## Allowed uses

- source review and summarization;
- bounded code search and explanation;
- test design and failure analysis;
- draft handoffs for human review;
- implementation only after Humanifest gates allow implementation;
- adversarial review of proposed changes;
- documentation and validation improvements.

## Disallowed uses

- bypassing provider limits, billing, identity, or access controls;
- credential sharing or account pooling;
- generating maintainer outreach without human review and authorization;
- increasing the number of contacted projects, issues, or pull requests merely
  because extra compute is available;
- using proprietary, private, patient, survivor, volunteer, employee, or
  operational data unless the governing record explicitly permits it;
- treating a model answer as evidence without a cited source.

## Registry

Use `portfolio/compute-resources.json` for public compute-resource records. Each
resource must record its provider, account scope, cost basis, allowed tasks,
limits, policy URL, access date, and oversight notes.

Run compute validation before adding or changing resource records:

```bash
python3 -m humanifest.cli compute --root .
```

The registry is public and must not contain API keys, tokens, bank data, private
account identifiers, or private billing details.
