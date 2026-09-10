# Cause-led discovery: malaria commodity supply chains

Accessed September 10, 2026. Read-only first screen; no target clone, setup,
service execution, operational credential use, outreach or new implementation opportunity.

## Burden and falsifiable software pathway

WHO's current malaria fact sheet reports estimated **282 million cases and
610,000 deaths in 2024**. These are burden estimates, not benefits attributable
to software. They support prioritizing cause discovery alongside the new
Humanifest malaria cause record; no claim about engineering neglectedness is
established by the burden alone.

The software hypothesis is that reliable commodity requisition and stock data
can reduce avoidable ordering/fulfillment mistakes in malaria programs. This
needs a current, deployed software workflow, a reproduced defect affecting it,
and a maintainer-supported release path. Reject or defer the pathway if those
links are absent; an active repository alone cannot establish health benefit.

## OpenLMIS evidence and limits

OpenLMIS's Tanzania implementation page describes its historical extension for
multiple commodity programs, explicitly including malaria, and rollout beginning
in 2013–2015. It describes requisition and warehouse integration. This provides
an actual historical software-to-program link, not proof that today's upstream
services/version still operate there or that any new contribution would deploy.
Do not attribute the page's historical supply-chain outcome claims to code alone.

The public GitHub organization inventory returned 84 repositories. Multiple
unarchived core services were pushed September 8–9, 2026: requisition, stock
management, fulfillment, reporting and UI components. This supports current
maintenance at the organization level only; it does not identify unowned work.

Public default-branch READMEs for requisition and stock management were read.
They describe Docker/Compose, Java/Gradle, PostgreSQL, environment configuration
and separate unit/integration-test tasks. Some instructions reference old tool
versions. **No quick-start command was executed**; lifecycle hooks, build images,
CI, license/contributor requirements and bot policy remain unaudited. No real
configuration file or operational credential was retrieved.

The complete first-page open lists (each below the 100-item page limit) show:

- Requisition: **14 pull requests and no standalone issues**. The raw repository
  `open_issues_count` includes PRs and is not a count of available tasks.
- Stock management: **10 PRs and two standalone issues**. #39 is a 2023 usage
  question about warehouse transfers; #80 is generic environment-file prose
  without a verified defect. Neither is promoted as actionable work.

Existing PR titles include zero-quantity order prevention and duplicate validation.
These are already proposed work, not invitations for a competing patch. Their
contents, current discussion, deployment relevance and need for verification
support would require inspection before considering a contribution.

## Next action

Find the current public planning/backlog and contribution policies (many PR titles
refer to OLMIS tracker identifiers), check bot/AI eligibility and contributor
agreement requirements, and trace an actively maintained service/release to a
malaria commodity workflow. If this yields a bounded unresolved problem or a
maintainer-welcomed test-support task, create an audited project/opportunity record.
Otherwise retain the negative screen and investigate another cause-led pathway.

This work can proceed while the prepared EPANET inquiry awaits the human review
required by current compute governance. It does not consume an implementation
or upstream PR slot.

## Sources

Accessed September 10, 2026:

- [WHO malaria fact sheet](https://www.who.int/news-room/fact-sheets/detail/malaria)
- [OpenLMIS Tanzania implementation](https://openlmis.org/implementation_region/tanzania/)
- [OpenLMIS organization](https://github.com/OpenLMIS)
- [Requisition README](https://github.com/OpenLMIS/openlmis-requisition/blob/master/README.md)
- [Stock-management README](https://github.com/OpenLMIS/openlmis-stockmanagement/blob/master/README.md)
- [Requisition open issues/PRs](https://api.github.com/repos/OpenLMIS/openlmis-requisition/issues?state=open&per_page=100)
- [Stock-management open issues/PRs](https://api.github.com/repos/OpenLMIS/openlmis-stockmanagement/issues?state=open&per_page=100)

Local public source snapshots are under `/tmp/humanifest-openlmis-screen`.
This first screen is not a pinned source/build audit.
