# PRISM boundary caching: verify savings before changing freshness

Initial intake, September 9, 2026: source/configuration inspection and three
read-only HEAD requests. Subsequent [browser verification](2026-09-09-prism-browser-cache-verification.md)
now measures original-wrapper controls, actual staging loads and conditional GETs;
this initial note records the earlier evidence boundary.

## Why this lead merits research

[WFP's PRISM description](https://innovation.wfp.org/project/prism) connects climate
hazards, vulnerability and exposure data to government and humanitarian analysis.
The plausible benefit here is reducing repeat loading cost for a mapping tool used
in that work. It is not measured assistance delivery, improved forecasts or a
population-level benefit.

[Issue #1569](https://github.com/WFP-VAM/prism-app/issues/1569) remains open,
unassigned and without comments. The author proposes fingerprinting large static
JSON files and assigning long cache lifetimes. Their historical estimate of
30–50% less transferred data and a 4.5 MB/9 MB example is **self-reported**, from
an older preview deployment. It is not a current measured saving. The complete
returned list of 13 open PRs contains no apparent matching asset-versioning fix;
this does not exclude private or differently described work.

## Pinned source and existing caching

Master: `603710958a025f15507164ccdaa24bc2515b70dc`. Repository is unarchived,
pushed September 9; root license is MIT. The full recursive tree was not truncated.

- Mozambique `layers.json` references three stable `data/mozambique/moz_bnd_adm*_WFP.json`
  paths. Their Git blob sizes are 3,369,959, 11,592,429 and 17,207,428 bytes, totaling
  32,169,816 **uncompressed source bytes**. These are not network-transfer bytes.
- Vite config builds into `build`, with a plugin that removes other countries'
  data. No hashing/rewriting of public JSON paths appears in this config or the
  inspected country-build script. Vite's public-directory documentation describes
  copying these files with their original names; a full PRISM build was not run.
- Four Firebase hosting targets configure SPA fallback and no custom cache headers.
  Source configuration alone does not establish which revision or rules a live
  deployment currently uses.
- `BoundaryCacheManager` already stores data and pending promises in in-memory Maps,
  scoped by layer and optional ISO3. It has force-refresh generation protection.
  This addresses within-session repeated loads; do not propose a duplicate cache.
- Existing `boundary-cache.test.ts` has three cases for stale in-flight refresh,
  empty PMTiles results and ISO3-scoped retrieval. These mock the network loader;
  they do not establish browser HTTP cache behavior across sessions.
- The boundary GeoJSON loader calls `fetchWithTimeout` with an empty options object.
  The wrapper's final request options still need inspection. The entry point calls
  `serviceWorker.unregister()`; merely finding a service-worker file is not proof
  of an active persistent cache.

## Live header checks and a disconfirming result

Hosts below come from the repository's `.firebaserc` site mappings. The checked
path on each host was `/data/mozambique/moz_bnd_adm3_WFP.json`.

| Host | Status | Content type | Declared length | Cache-Control |
| --- | --- | --- | ---: | --- |
| `prism-frontend.web.app` | 200 | text/html | 642 | max-age=3600 |
| `staging-prism-frontend.web.app` | 200 | application/json | 17,207,428 | max-age=3600 |

The production-named host returned HTML at this path, not the requested boundary
JSON. It cannot be used as evidence of production boundary-data caching. No claim
is made about all WFP country deployments or whether that host is an active user
entry point. The staging response is consistent with the source file size, but
its body was not downloaded or hash-matched to the current commit.

The staging JSON ETag was
`"a4a2966ce5a12ee2985e8c283266951c396fa36eaf8b0da00c8113e0c94fb7ba"`.
A subsequent **HEAD with If-None-Match returned 304**, retaining `max-age=3600`.
Requests were made around 09:31–09:34 UTC on September 9; returned Last-Modified
for staging was May 18, 2026. No cookies, account or API credentials were used.

This establishes that the endpoint supports conditional revalidation. It weakens
the assumption that each visit after one hour necessarily retransfers the entire
file. HEAD has no response body and does not measure browser GET traffic, cache
retention, compression, rendering latency, eviction or actual user revisit patterns.
Do not count a 17 MB Content-Length as 17 MB transferred in these checks.

## Initial research plan (now executed in bounded browser verification)

Trace the final fetch options and all references relevant to these three boundary
files; complete the lockfile/lifecycle audit before executing target code. Then
measure the actual boundary-fetch path with a controlled browser cache: first load,
warm reload, expired-cache conditional response and changed-content response.
Record request count, actual transfer bytes and freshness, with controls showing
that new boundary content is obtained. Use small synthetic fixtures for controlled
expiry/content changes, and explicitly separate them from any read-only live-app
observations. A frozen full frontend baseline may be needed for that path; avoid
running deploy scripts or supplying operational secrets.

If revalidation already avoids the claimed transfer, report that negative finding
and reassess whether request latency or cache eviction justifies further work.
Only then scope a content-addressed build manifest and reference rewrite, if wanted
by maintainers. Never assign year-long immutable caching to mutable JSON paths or
dynamic dates/alerts. A versioning change must preserve country filtering, all
consumer references, update discovery and rollback behavior.

## Contribution and setup constraints

No CONTRIBUTING file was found in the recursive tree; a root request returned 404.
README, MIT license, PR template and CODEOWNERS were inspected. No explicit AI/bot
rule or CLA requirement was established in those files; absence is not acceptance,
and organization-wide policy still needs checking. CODEOWNERS names ericboucher
and wadhwamatic; neither has agreed a Humanifest scope or review commitment.

The PR template asks for tests with RBD, Cambodia and Mozambique plus relevant
tests/docs and screenshots. Fork contributions should target the repository's
master branch once scope is accepted. Existing JSON-helper issue #1829 already has
PRs #1911 and #2019 with two contributors; do not create a third competing fix.
Most newer PRISM issues are assigned; they were not treated as free work.

Frontend requires Node >=20.6.0, Yarn 1.22.22, React 19, Vite 6 and a local common
package. Inspected scripts include Husky/lint-staged, common-package rebuilds,
country output removal, Firebase deploy commands and a Node 20 Dockerfile exposing
port 3000. Vite's server binds all interfaces; future local verification should
explicitly bind loopback. No scripts ran. Lockfiles and transitive lifecycle hooks
are not yet audited. CI runs lint, Jest, JSON/layer/boundary checks and builds;
country Cypress end-to-end jobs are currently disabled with `if: false`. Deploy
jobs use Firebase, telemetry and other secrets; those jobs are outside this research.

## Sources

All accessed September 9, 2026:

- [Current issue #1569](https://github.com/WFP-VAM/prism-app/issues/1569)
- [Pinned Vite configuration](https://github.com/WFP-VAM/prism-app/blob/603710958a025f15507164ccdaa24bc2515b70dc/frontend/vite.config.ts)
- [Pinned Firebase configuration](https://github.com/WFP-VAM/prism-app/blob/603710958a025f15507164ccdaa24bc2515b70dc/frontend/firebase.json)
- [Pinned boundary cache](https://github.com/WFP-VAM/prism-app/blob/603710958a025f15507164ccdaa24bc2515b70dc/frontend/src/utils/boundary-cache.ts)
- [Pinned boundary loader](https://github.com/WFP-VAM/prism-app/blob/603710958a025f15507164ccdaa24bc2515b70dc/frontend/src/context/layers/boundary.ts)
- [Pinned cache tests](https://github.com/WFP-VAM/prism-app/blob/603710958a025f15507164ccdaa24bc2515b70dc/frontend/src/utils/boundary-cache.test.ts)
- [Pinned frontend CI](https://github.com/WFP-VAM/prism-app/blob/603710958a025f15507164ccdaa24bc2515b70dc/.github/workflows/frontend.yml)
- [Vite public-directory behavior](https://vite.dev/guide/assets#the-public-directory)
- [Checked staging JSON endpoint](https://staging-prism-frontend.web.app/data/mozambique/moz_bnd_adm3_WFP.json)
