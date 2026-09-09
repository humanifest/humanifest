# Agent Instructions

Humanifest is the source-of-truth control repository for humanitarian OSS contribution work.

## Authority Model

- `GOALS.md`, `README.md`, and `docs/contribution-protocol.md` are controlling protocol documents.
- `docs/finance-governance.md` controls fiscal-steward, sponsorship, ledger, and conflict-of-interest records.
- `docs/compute-governance.md` controls donated, free, sponsored, paid, and self-hosted compute-resource records.
- `schemas/*.schema.json` and `humanifest/models.py` define the current machine-readable record contract.
- `humanifest/finance.py` and `portfolio/funding-ledger.json` define and store the current public finance-governance contract.
- `humanifest/compute.py` and `portfolio/compute-resources.json` define and store the current public compute-governance contract.
- `portfolio/projects/*.json` and `portfolio/opportunities/*.json` are current audited records.
- `research/*.md` contains evidence synthesis and is not a substitute for project records.
- `handoffs/*.md` contains reusable prompts derived from current records.

If these conflict, prefer current project records for a specific candidate, then the contribution protocol, then general docs. Do not silently blend conflicting claims.

## Operating Rules

- No issue comments, maintainer messages, pull requests, repository creation, package publication, or other external writes without explicit user authorization.
- Honor standing authorization in `docs/contribution-protocol.md`; do not ask again for covered routine actions. Verify the authenticated GitHub actor before writing: outreach must use a Humanifest user or bot identity, never the user's personal account.
- Do not clone external target repositories into this repository.
- Use read-only source browsing before cloning.
- Do not execute third-party setup code until manifests, lifecycle hooks, Dockerfiles, CI, requested privileges, ports, services, and secrets have been inspected.
- Do not advance an opportunity past `MAINTAINER-CHECK` without maintainer confirmation.
- Do not advance an opportunity to `BUILDING` unless every hard gate passes.
- Preserve evidence provenance and access dates.

## Validation

Run:

```bash
python3 -m unittest
python3 -m humanifest.cli validate --root .
python3 -m humanifest.cli finance --root .
python3 -m humanifest.cli compute --root .
python3 -m humanifest.cli report --root .
```
