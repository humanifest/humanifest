# Open Food Facts search: SDK baseline and server filter

Verified September 9, 2026. This extends the
[initial contract audit](2026-09-09-openfoodfacts-search-contract-audit.md).
The existing PR remains another contributor's work; no target patch, formal
review, comment, authentication attempt or product-service query was submitted.

## Unchanged SDK baseline

Pinned PR #504: `970a7290a8a5869de8f5784324c166212fdd15ca`.
The disposable checkout is outside Humanifest at
`/private/tmp/humanifest-off-pr504-baseline`. Git hooks and credentials were
disabled during retrieval. Its manifest, lockfile, request code and API test
file were byte-compared with the inspected raw files before execution.

Read the pinned contribution guide, PR template, CI, manifest, lockfile,
pre-commit configuration, MIT license target and REUSE metadata. The template
requires maintainer agreement on assignment before acceptance, and disclosure
of LLM/version/mode, successful execution and screenshot/video proof. No such
assignment, human review or screenshot/video proof is claimed here. AI disclosure
requirements do not establish acceptance of this specific bot contribution.

The project has core requests/pydantic/tqdm dependencies and separate Redis,
Pillow and ML extras. No Docker/compose or conftest files were found in the
checkout. Imports create a requests session and declare dataset-cache paths;
they do not call the dataset download function in these API tests. Optional
Pillow imports are guarded. No pre-commit hook was installed or executed.

Using existing Python 3.11.10 and uv 0.8.22, a frozen, no-build sync installed
43 core/development wheel packages in about 51 seconds. The only non-registry
lock source is the virtual project. The child environment omits credentials,
uses a dedicated temporary cache and disables Python downloads/config discovery.
No source build, project installation, lock update, ML extra, database or server
was needed. CI uses Python 3.11 and uv 0.10.2 on Linux with all extras; this
macOS focused run is not an exact CI reproduction or full-suite result.

The unchanged `tests/unit/test_api.py` completed with **38 passed**. The runner
disables automatic pytest plugin loading and replaces Python socket connect,
bind/listen and DNS operations with immediate failures. Connection, DNS and bind
probes verified rejection before pytest. Requests mocks still service the tests.
This protects against accidental Python network calls, not arbitrary native code
or subprocesses. No production credentials or browser profile were present.

The [reusable baseline runner](fixtures/run_off_api_baseline.py) checks exact
source hashes before and after the run. The separate server-filter probe does
not replace the SDK tests. Tracked SDK files remained unchanged.

## Current server path and four filter cases

Server source is pinned independently to
`3a97b98032d27b7a5e33de0c2edcde0c21ddf4c3`. Read the route and display functions:

1. `Routing.pm::api_route` records the version and search action.
2. `cgi/display.pl` sends non-v3 search actions through `display_tag_page`.
3. The product-list branch reaches `search_and_display_products`, which calls
   `add_params_and_filters_to_query` before constructing the query results.
4. That filter's ignored-parameter table contains `search_terms`. The function
   deletes it before forwarding parameters to `add_params_to_query`.

The [server filter reproduction](fixtures/off-search-filter-reproduction.py)
hash-checks all three source files, extracts the original ignored-parameter table
and complete filter function, and executes them with system Perl 5.34.1. Request
retrieval, subsequent query construction and owner/country filtering are spies;
the full server, MongoDB, taxonomy loading and HTTP routing do not execute.

| Input | Parameters forwarded to query construction |
| --- | --- |
| `search_terms=mineral water` | none |
| `search_terms=humanifest-nonmatching-93f6` | none |
| no search text | none |
| search text plus `brands_tags=en:test-brand` | `brands_tags=en:test-brand` |

All four assertions pass. Page 2, page size 10 and sort order are retained at the
request level in every case, and owner/country filtering is invoked once. The
controls distinguish discarding text from discarding every parameter. These
results verify original filter behavior and agree with the official documented
v2 contract. They do not establish the deployed server revision or actual product
results for these queries. The SDK mock success and server-filter behavior must
not be presented as a complete end-to-end reproduction.

## Prepared verification note for the existing author

Not sent. A useful bounded message, after the required authorization and fresh
discussion check, would be:

> I checked PR #504's pinned head with OpenAI Codex. All 38 existing API tests pass
> locally, but I found a contract concern: the official v2 search documentation
> says full-text queries are unsupported. Current server source also explicitly
> removes `search_terms` before forwarding query filters. A hash-checked check of
> that original filter produces the same forwarded filters for ordinary text,
> a nonsense term and no text; a structured-brand control survives. This is a
> source/function check, not a live API result. The PR's fixed URL mocks cannot
> establish text-query semantics. Could we settle the intended authenticated
> search or supported full-text endpoint before treating the URL substitution as
> a fix? I can support verification of the agreed approach without a competing PR.

The precise auth/search compatibility contract, accepted support scope, bot
identity eligibility and reviewer commitment still need confirmation. Do not
change credential handling, assert a live outage is fixed, or submit a replacement
patch based only on these checks.

## Reproduce

After the inspected frozen environment exists:

```sh
python3 research/fixtures/run_off_api_baseline.py /absolute/path/to/pr504-checkout
python3 research/fixtures/off-search-filter-reproduction.py /absolute/path/to/server-source-files
```

The server source directory uses filenames with `/` replaced by `__`. Both
fixtures reject other source hashes. Installation used:

```sh
uv sync --frozen --no-build --no-install-project --no-default-groups --group dev \
  --no-config --python /absolute/path/to/python3.11
```

## Sources

Accessed September 9, 2026:

- [PR #504](https://github.com/openfoodfacts/openfoodfacts-python/pull/504)
- [Pinned SDK manifest](https://github.com/arybhatt4533/openfoodfacts-python/blob/970a7290a8a5869de8f5784324c166212fdd15ca/pyproject.toml)
- [Pinned PR template](https://github.com/arybhatt4533/openfoodfacts-python/blob/970a7290a8a5869de8f5784324c166212fdd15ca/.github/PULL_REQUEST_TEMPLATE.md)
- [Pinned API tests](https://github.com/arybhatt4533/openfoodfacts-python/blob/970a7290a8a5869de8f5784324c166212fdd15ca/tests/unit/test_api.py)
- [Server route](https://github.com/openfoodfacts/openfoodfacts-server/blob/3a97b98032d27b7a5e33de0c2edcde0c21ddf4c3/lib/ProductOpener/Routing.pm#L332)
- [Server dispatch](https://github.com/openfoodfacts/openfoodfacts-server/blob/3a97b98032d27b7a5e33de0c2edcde0c21ddf4c3/cgi/display.pl#L174)
- [Original parameter filter](https://github.com/openfoodfacts/openfoodfacts-server/blob/3a97b98032d27b7a5e33de0c2edcde0c21ddf4c3/lib/ProductOpener/Display.pm#L4685)
- [Official v2 search contract](https://openfoodfacts.github.io/documentation/docs/Product-Opener/v2/search/get-search/)
