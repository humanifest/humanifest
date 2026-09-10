# Crisis Cleanup #1164: current-source audit

The current project and opportunity JSON records control decisions. This note
explains the audit behind their 2026-09-08 update; it is not implementation or
outreach authorization.

## Result

Keep #1164 parked. The exact code and neighboring tests are now located, but the
current caller already waits for completion before success feedback. A speculative
missing-await patch would not address the inspected code. This is useful contrary
evidence, not proof that the production bug has been fixed.

All source inspection used commit `64f72babb32346cca0d32c97d6f6dfd8d9dc56c9`.
The recursive GitHub tree was not truncated. GitHub code search located the model
and hook; the actual hook was then fetched at the pinned commit. No target setup,
tests, app, or phone services were executed. Selected public source files were
read in a temporary audit folder, without cloning a target repository.

## Claim ledger

| Claim | Evidence and strength | Limit / next discriminating check |
| --- | --- | --- |
| The caller awaits completion before success. | A, direct source observation: `queue-caller-2026-09-08`, lines 310–313. | Depends on the action rejecting correctly; inspect runtime behavior through the ORM. |
| The model awaits its POST and the shared interceptor rethrows failures. | A, source observation: `queue-model-2026-09-08` and `queue-interceptor-2026-09-08`. | Plugin handling and deployed version could differ; no runtime reproduction. |
| A missing await explains the current issue. | E, contradicted for the inspected caller/model. | Another path, dependency behavior, or older deployment could explain the original report. |
| A focused synthetic regression is feasible. | C, inference from neighboring API mocks in `queue-model-tests-2026-09-08`. | A mocked action alone would assume away an ORM rejection defect; verify both layers. |
| External AI contributions are permitted under known terms. | D, unresolved: AI-tool instructions exist, but no explicit external policy was established. | The later check below retrieved the ICLA; disclosure expectations, signatory and agreement status remain unresolved. |

Source IDs above resolve to pinned URLs and access dates in
`portfolio/opportunities/crisiscleanup-success-banner-failure.json`.

## Cause and contribution verification

The pinned README still reports large disaster-response participation figures;
these remain self-reported reach, not independently demonstrated outcomes. Its
separate efficiency and monetary statistics are dated 2024-09-25 and are not
evidence that this individual fix would improve those outcomes.

The current README sends contributors to the older `crisiscleanup-3-web` guide.
That guide asks for focused, tested PRs and ongoing review participation, and
references a CLA. The contributions page returned only a JavaScript application
shell to the earlier text-only web fetch; the later browser inspection below
resolves that retrieval gap. Current
AGENTS.md and CLAUDE.md describe AI coding workflows but do not settle external
contributor disclosure requirements.

The next useful step, if this candidate is reconsidered, is a synthetic rejected
request through the real ORM and queue hook in an inspected environment. Do not
contact live phone endpoints or treat the open issue as an invitation to build.

## Later contribution-policy check: 2026-09-08

The [live contributions page](https://www.crisiscleanup.org/contributions) loaded
in the in-app browser and exposed the agreement links. The page asks contributors
to sign and email an individual agreement, and describes a signed ICLA as required
before commit rights. The [older guide](https://github.com/CrisisCleanup/crisiscleanup-3-web/blob/master/CONTRIBUTING.md)
subjects contributions to CLA terms but says physical signing may be requested
for larger changes. A fork avoids needing commit rights; it does not by itself
resolve the published contribution terms.

The linked [ICLA v1](https://www.crisiscleanup.org/assets/icla.pdf), dated
2020-10-18, was retrieved in full (four pages). It requests a signed agreement
from each contributor, grants copyright and patent licenses, and includes
representations about entitlement to contribute and original work. It also
addresses third-party submissions. These are observations of published terms,
not a determination of who may bind Humanifest or how those representations
apply to a particular AI-assisted patch.

The contribution-policy gate remains false for specific unresolved questions:
who the responsible signatory is, whether an agreement is already on file, and
what maintainers require for a bot-authored, AI-assisted submission. Neither the
website nor the ICLA establishes that last point. The corporate agreement was
linked by the page but not successfully retrieved in this check; no claim is made
that its terms are understood or applicable.

No form was filled, agreement signed, email sent, or maintainer contacted. If
this parked candidate becomes worth pursuing, settle these questions before
submission. The original reproducibility, issue-freshness, and maintainer-interest
blockers remain. Public source retrieval is complete for the ICLA; it should not
be repeated as though JavaScript still prevents access.
