# HOT #7227: archive selection and download error handling

Accessed 2026-09-08. This investigation finds two distinct paths: archived
projects are excluded from the active-project selection used by the extractor;
the frontend also reports several unrelated failures as unavailable extraction.
A frontend correction alone would not restore archived-project artifacts.

## Source trace

Tasking Manager source is pinned to
`2b917a14ea7b0b76935c4e2d6985ab25764cd1c9`:

- [DownloadOsmData](https://github.com/hotosm/tasking-manager/blob/2b917a14ea7b0b76935c4e2d6985ab25764cd1c9/frontend/src/components/projectDetail/downloadOsmData.js)
  builds an artifact ZIP URL and sends a HEAD request. It calls `window.open`,
  then dereferences the returned handle, before checking `responsehead.ok`.
  Both HTTP errors and exceptions open the same extraction-unavailable popup.
  Metadata HEAD requests also read size and modification headers without checking
  HTTP success. That latter observation was inspected, not executed here.
- [Messages](https://github.com/hotosm/tasking-manager/blob/2b917a14ea7b0b76935c4e2d6985ab25764cd1c9/frontend/src/components/projectDetail/messages.js)
  tell users to ensure the extract is active, even when a browser-handle error
  caused the popup. The handler does not establish extract activation status.
- [Existing download-button tests](https://github.com/hotosm/tasking-manager/blob/2b917a14ea7b0b76935c4e2d6985ab25764cd1c9/frontend/src/components/projectDetail/tests/downloadButtons.test.js)
  test the AOI button. They do not exercise `DownloadOsmData`.
- [ProjectService.get_active_projects](https://github.com/hotosm/tasking-manager/blob/2b917a14ea7b0b76935c4e2d6985ab25764cd1c9/backend/services/project_service.py#L789)
  first selects recent task-history or project-chat activity, then requires
  `ProjectStatus.PUBLISHED`. Archived projects are excluded at this service layer.
- [Extractor configuration](https://github.com/hotosm/tasking-manager/blob/2b917a14ea7b0b76935c4e2d6985ab25764cd1c9/scripts/aws/lambda/TM-Extractor/_envcommon/lambda.hcl)
  references TM-Extractor v1.0.1 and a daily schedule. The
  [resolved tree](https://api.github.com/repos/hotosm/TM-Extractor/git/trees/v1.0.1?recursive=1)
  was `070ea82acecde3be49fc5b8622f365840011943a`.
- [Extractor source](https://github.com/hotosm/TM-Extractor/blob/070ea82acecde3be49fc5b8622f365840011943a/tm_extractor.py)
  queries `/projects/queries/active/?interval=...`; its Lambda handler defaults
  to 24 hours. It submits snapshot POSTs with a Raw Data API token. It also has
  an explicit-project path, but that is not a user-facing, authorized refresh
  feature. No credentials were requested or extraction invoked.

The pinned configuration and code are evidence of the intended path, not proof
of the deployed configuration or the missing artifact's actual production cause.
The historical member explanation in #7227 remains separately attributed.

## Reproduction

[The dependency-free probe](fixtures/hot-download-reproduction.mjs) reads the
original download handler from a separately retrieved upstream file. It checks
the complete source SHA-256 before evaluating the inspected handler with mocked
HEAD responses, browser methods, and state setters. It neither copies the target
implementation into this repository nor imports target dependencies.

Retrieve the pinned `downloadOsmData.js` linked above as a local file, then run:

```sh
node research/fixtures/hot-download-reproduction.mjs /absolute/path/downloadOsmData.js
```

Observed with Node v22.16.0 on 2026-09-08:

| Input | Observed original behavior |
| --- | --- |
| HEAD 200, browser handle returned | Opens URL; no error popup; loading clears |
| HEAD 404, browser handle returned | Opens URL before checking status, then shows error; loading clears |
| HEAD 200, browser returns null | Handle dereference throws before status check; shows error; loading clears |
| HEAD rejects | Shows error without opening URL; loading clears |

All four assertions passed. These are function-level observations under supplied
conditions. No browser popup-blocking frequency, React rendering, HTTP/CORS
behavior, archived-project end-to-end reproduction, or impact was measured.
No target setup, production interaction, target suite, or fix was run.

## Bounded next contribution

A useful scope discussion can now distinguish:

1. **Download failure handling:** check unsuccessful HEAD results before opening
   the artifact; handle a null window handle explicitly; present guidance based
   on what is actually known. Any navigation design must be tested for browser
   user-activation rules rather than assuming a delayed popup will be allowed.
2. **Archived artifact refresh:** agree on freshness, authorization, workload
   limits, and the final-completion lifecycle. This crosses protected scheduling
   and potentially permission boundaries, requiring maintainer supervision.

Do not describe option 1 as closing #7227. Proposed component tests should cover
200/404/network failures, null handles, loading cleanup, and rejected metadata
requests. Published and archived project cases must stay distinct; the UI must
not promise a refresh it cannot perform. No upstream patch or inquiry was sent.

## Readiness and policy

The [frontend manifest](https://github.com/hotosm/tasking-manager/blob/2b917a14ea7b0b76935c4e2d6985ab25764cd1c9/frontend/package.json)
uses lint plus CRACO/jsdom for tests. Its start/build scripts include a nested
sandbox-iD installation; builds can upload Sentry sourcemaps. They were inspected
and not executed. Full environment/CI/hook inspection remains incomplete.

The [BSD-2-Clause license](https://github.com/hotosm/tasking-manager/blob/2b917a14ea7b0b76935c4e2d6985ab25764cd1c9/LICENSE.md)
and [PR instructions](https://github.com/hotosm/tasking-manager/blob/2b917a14ea7b0b76935c4e2d6985ab25764cd1c9/docs/developers/submit-pr.md)
were read. HOT's linked [full AI guide](https://responsibleai.guide/ai-assisted-coding-guide/)
adds human authorship of PR descriptions and explicit human approval for shared
code updates. Record these constraints alongside the repository's disclosure
levels and protected workflows; do not claim independent human review occurred.
They constrain this candidate, not independent work elsewhere in the portfolio.

The opportunity remains in research. Next independent job: inspect the existing
Kobo incremental-sync PR's actual diff and tests; do not poll unchanged CHT PRs.

## Coordination delivered

The [first scope question](https://github.com/hotosm/tasking-manager/issues/7227#issuecomment-5594446967)
was posted as `humanifest-bot` at 2026-09-09T01:38:11Z (September 8 local
time), under the user's standing direction to handle GitHub communication. The
issue was open and unassigned, the inspected head unchanged, and no duplicate
bot message present. GitHub confirmed the returned author and exact body.
The question separates frontend error handling from archived-data refresh and
states the mocked-probe and AI-review limits. No target patch was submitted.

The opportunity is now `MAINTAINER-CHECK`; the planned September 15 status check
remains in place absent an actionable reply. Target environment verification can
proceed independently without treating the outbound inquiry as acceptance.
