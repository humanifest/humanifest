# Outreach

Humanifest should be introduced as a maintainer-respecting contribution system,
not as an autonomous AI coding service.

## Core message

Humanifest helps volunteers and AI-assisted coding agents find high-leverage
humanitarian open-source work, verify that it is wanted, and contribute
responsibly without burdening maintainers.

Useful phrases:

- donated compute for public-good software;
- evidence before implementation;
- read-only by default;
- maintainer-approved, low-burden contributions;
- a governed contribution pipeline for humanitarian open source.

Avoid saying that Humanifest autonomously fixes charity software, ranks
maintainers, guarantees impact, or uses sponsorship to buy priority.

## Short public description

Humanifest is an open-source protocol and toolkit for directing donated
engineering and AI-assisted review time toward humanitarian and public-interest
software. It starts read-only, checks evidence and governance records, and blocks
implementation until maintainers have indicated the work is wanted.

## Social post

Humanifest turns donated AI-assisted engineering time into maintainer-approved
contributions for humanitarian open source.

It is read-only by default: first verify evidence, policies, compute use, and
maintainer interest; only then prepare a narrow, tested contribution.

Run it locally:

```bash
python3 -m humanifest.cli operate --root . --as-of "$(date -u +%F)" --max-age-days 30
```

## Longer announcement

Humanifest is now open for contributors who want to help public-good software
without adding noise to maintainers' queues.

The project is a source-of-truth control repository for humanitarian open-source
contribution work. It tracks cause areas, projects, opportunities, evidence,
finance governance, compute governance, and hard gates that prevent premature
implementation.

The first thing a new operator runs is read-only. The operator loop validates
local records, identifies stale sources, shows top cause pathways, summarizes
opportunity states, and reports safe next actions. It does not post comments,
open pull requests, contact maintainers, fetch remote sources, publish packages,
or mutate records.

Good first contributions include refreshing stale evidence, improving records,
hardening validation, reviewing handoffs, and documenting repeatable workflows.
Writing code comes later, after every gate passes and the maintainer has
confirmed the work is wanted.

## Maintainer-safe note

Use this only when a maintainer or project community has invited more context:

> Humanifest is reviewing public-good open-source issues where AI-assisted
> engineering might help without adding maintainer burden. We are not asking you
> to review a patch yet. Before any implementation, we want to confirm whether
> this bounded area is useful to you, whether AI-assisted work is acceptable
> under your project rules, and who should review it if it proceeds.

Do not send maintainer notes unless `docs/contribution-protocol.md`, the target
record, and current authorization permit that specific communication.

## Audiences

Good places to share Humanifest:

- humanitarian open-source communities;
- civic tech networks;
- open-source maintainers discussing AI contribution quality;
- developers looking for responsible volunteer work;
- companies with unused or sponsored compute that can support public-good
  verification work;
- AI safety and beneficial-AI communities focused on concrete public benefit.

## Calls to action

Use calls to action that match the reader's likely role:

- Clone the repository and run the read-only operator loop.
- Suggest a cause area.
- Nominate a humanitarian open-source project.
- Refresh stale evidence.
- Donate governed compute or sponsorship.
- Review a handoff for overclaiming.
- Help improve validation, reports, schemas, and automation.

Do not ask people to mass-comment on external issues or open drive-by pull
requests.
