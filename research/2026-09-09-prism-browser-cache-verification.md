# PRISM browser cache verification

September 9, 2026. The existing request wrapper and public staging app already
avoid repeat JSON payload transfers in the measured cases. The historical 30–50%
saving proposed in #1569 remains unverified. No cache implementation or production
configuration was changed.

## Original request path and execution boundary

Pinned master: `603710958a025f15507164ccdaa24bc2515b70dc`.
`frontend/src/utils/fetch-with-timeout.ts` forwards the caller's options to native
fetch and adds an AbortController signal. The boundary loader passes `{}`, so
this path does not select a cache-bypassing mode. Wrapper SHA-256:
`46f41fab3666449322c1c63146111ff3bae52bc53cba1afcf32a753fca69b54f`.

[Controlled harness](fixtures/prism_browser_cache_probe.cjs) verifies that hash,
removes exactly three reviewed import lines and uses Node's built-in TypeScript
syntax erasure. The original function body executes in the browser, including its
timeout/finally path. Notification and HTTP-error imports are fail-fast sentinels;
these success/cache cases must not invoke them. This does not test error handling,
Redux, the complete boundary loader, GIS processing or the full frontend suite.
No third-party PRISM dependency is installed or imported on the host.

Runtime: Node **24.19.0**, bundled Playwright **1.62.1**, automated headless Google
Chrome Canary **155.0.8046.0**, fresh browser context, local HTTP server bound to
127.0.0.1. Automated browser/network instrumentation was used to measure cache
behavior, without a personal browser profile. No request interception or cache
disabling was used. Synthetic test service workers are blocked. Source hash remains
unchanged after execution; the server and browser close on completion.

```bash
NODE_PATH=/Users/admin/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules \
/Users/admin/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node \
research/fixtures/prism_browser_cache_probe.cjs \
/tmp/humanifest-prism-screen/frontend__src__utils__fetch-with-timeout.ts
```

The source file must be retrieved unchanged from the pinned revision. No upstream
source is embedded in this harness. Node reports its TypeScript eraser as
experimental; the observed runtime version is therefore part of reproducibility.

## Eleven controlled cases passed

The synthetic JSON response body is 4,122 bytes; ordinary responses have a
**two-second** cache lifetime. Server logs provide request/status/body-byte counts;
Resource Timing is separate browser telemetry, not a packet capture.

| Case | Server request/status | Server body bytes | Returned version |
| --- | --- | ---: | ---: |
| Initial wrapper fetch | 200 | 4,122 | 1 |
| Warm wrapper fetch | none | 0 | 1 |
| Warm fetch after document navigation | none | 0 | 1 |
| Expired unchanged content | conditional 304 | 0 | 1 |
| Server changed, cached response still fresh | none | 0 | 1 |
| Changed content after expiry | conditional 200 | 4,122 | 2 |
| Native-fetch initial control | 200 | 4,122 | 2 |
| Native-fetch warm control | none | 0 | 2 |
| Versioned-URL initial control | 200 | 4,122 | 1 |
| Same versioned URL warm | none | 0 | 1 |
| Different versioned URL | 200 | 4,122 | 2 |

All wrapper responses expose status 200 to JavaScript, including the response
whose network validation was 304. Resource Timing reports 0 transferSize for warm
cache hits, 300 for revalidation, and 4,422 for an uncached body. These browser
figures must not be confused with the independently logged response-body bytes.
Versioned URLs are manually defined controls, not an implemented content-hash build.
A mutable URL continues to return cached old data while fresh, showing why simply
extending that freshness period could delay discovery of updated boundaries.

## Actual public staging app

[Live observation harness](fixtures/prism_live_cache_observation.cjs) observes
`https://staging-prism-frontend.web.app/` in a separate fresh Canary context. It
loads the dashboard twice, waits 12 seconds after each DOM load and records only
the three Mozambique boundary requests. The map and boundary overlay rendered;
page title and UI text were captured and the screenshot was visually inspected.
The app's deployed source revision is **not verified as the pinned master**.

| File | Cold Brotli body bytes | Decoded bytes | Warm transferSize |
| --- | ---: | ---: | ---: |
| `moz_bnd_adm1_WFP.json` | 480,585 | 3,369,959 | 0 |
| `moz_bnd_adm2_WFP.json` | 1,666,098 | 11,592,429 | 0 |
| `moz_bnd_adm3_WFP.json` | 2,338,876 | 17,207,428 | 0 |
| Total | **4,485,559** | **32,169,816** | **0** |

The second page load reports `fromDiskCache: true`, `fromServiceWorker: false`
and zero CDP encodedDataLength for all three files. This is observed warm cache
reuse, not an estimate derived from file sizes. The first live run established
cold/warm behavior; a second fresh run added the revalidation control below and
confirmed the same payload counts. No further duplicate run was needed.

In the second run, explicit same-origin `fetch(path, {cache: 'no-cache'})` GETs
then forced conditional validation for all three files. CDP's network extra-info
statuses were **304**, while JavaScript received 200 responses containing the
cached decoded bodies. CDP encodedDataLength was 257, 256 and 255 bytes respectively
(total **768**); Resource Timing reported 300 each (900 total). Neither measure is
claimed to capture complete TLS/network overhead. Response headers retained
`max-age=3600` and Brotli-specific ETags. No full JSON payload was retransferred
in that control.

This control did **not** wait for natural one-hour expiry and did not alter the
app's actual default options or the server's data. Synthetic expiry/freshness
results must stay separate from live forced validation. Browser restart, cache
eviction, other browsers, weak-network latency, all country deployments and user
revisit distributions remain untested. The production-named host's HTML fallback
from the intake was not used as boundary evidence.

The observation script uses existing Playwright, performs no writes to the remote
app and uses no user credentials. A stop threshold at 65 MB of observed completed
response bytes was not reached; the completed second run observed 7,266,968 encoded
bytes across all network resources. This is not a measure of total project impact.
The script is an observation recorder, not an assertion of all dashboard features.

## Setup and contribution limits

Front/common lockfiles were retrieved: 1,631 and 290 `resolved` entries respectively,
all pointing to registry.yarnpkg.com. That is an inventory, **not** a package or
lifecycle security audit. No full lockfile installation, build, Jest baseline or
previous three boundary-cache unit tests were executed. The scoped wrapper uses
browser-native APIs and reviewed sentinels, so it does not need those packages;
full frontend implementation remains gated on its normal setup and tests.

The organization `.github` repository root contains `.gitignore`, `LICENSE` and
`profile`; no root contribution-policy file was found there. This does not prove
absence of policy elsewhere or bot acceptance. Existing README/PR template and
CODEOWNERS were inspected at intake. No assignment or Humanifest scope is yet
confirmed.

The next useful external decision is whether maintainers have a specific case
that retransfers payloads or a latency/freshness requirement that justifies asset
versioning. Share these measurements and request that scope; do not turn an
unverified historical percentage into a production optimization claim.

The findings and bounded follow-up question were [delivered as humanifest-bot](https://github.com/WFP-VAM/prism-app/issues/1569#issuecomment-5600104762)
at `2026-09-09T10:06:07Z`; a separate GitHub GET verified exact author/body.
The opportunity now waits for scope feedback, with a manual September 15 review.
