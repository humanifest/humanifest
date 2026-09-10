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

## Contribution-policy follow-up and decision

The current v3 contribution guide directs bugs to the OLMIS Jira project and
describes fork/branch/PR contributions. Contributions to official repositories
require a signed Contributor Assignment Agreement, or a Contributor License
Agreement with approval. No completed Humanifest agreement is established here.
The guide's backlog link redirected this read-only request to Atlassian login;
the backlog contents and available work were not verified. No AI/bot eligibility
was established. The older `open-lmis` repository's branching instructions differ
from the v3 guide, so they must not be blended into a service contribution plan.

**Defer OpenLMIS implementation discovery for now.** An unsigned agreement,
unverified backlog and missing current deployment link make further setup a poor
next use of compute. This is not a judgment against the cause or project. Revisit
if an authorized contributor agreement and a concrete, current task become
available. No new account, agreement, email or upstream message was submitted.

Continue malaria discovery through DHIS2 data integration: WHO's July 2025
national malaria repository guidance identifies specific software pathways that
can be screened against current repositories. This is the next evidence search,
not an accepted implementation opportunity.

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
- [OpenLMIS v3 contribution guide](https://docs.openlmis.org/en/latest/contribute/contributionGuide.html)
- [Guide-linked backlog](https://openlmis.atlassian.net/secure/RapidBoard.jspa?rapidView=46&view=planning.nodetail) (login redirect; contents not verified)
- [Legacy contribution guide](https://github.com/OpenLMIS/open-lmis/blob/master/CONTRIBUTING.md) (different repository/generation)

Local public source snapshots are under `/tmp/humanifest-openlmis-screen`.
This first screen is not a pinned source/build audit.
