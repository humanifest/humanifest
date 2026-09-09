# Open Food Facts: verify the existing text-search fix

Read-only intake on September 9, 2026. Existing PR #504 belongs to
`arybhatt4533`; its head is `970a7290a8a5869de8f5784324c166212fdd15ca`.
Both changed-file diffs, issue #496's discussion, PR comments and reviews were
read. No replacement implementation or external message was created.

## Why this is worth verifying

Open Food Facts describes itself as a nonprofit providing open food information
for public use, research and sustainability work. The official Python SDK exposes
product lookup and text search. Reliable retrieval supports that public-benefit
pathway; no Humanifest measurement establishes health outcomes, deployment reach
or compute savings from this particular issue.

Issue #496 reports that the README's `text_search` example returns HTTP 503.
A maintainer explains that its existing CGI endpoint now requires authentication.
Another contributor has already asked which authentication/search contract is
intended. Those questions remain unresolved in the retrieved discussion.

PR #504 changes the request URL to `/api/v2/search`, keeps `search_terms`, and
updates its mocked test URLs. However, the current official v2 documentation says
that this endpoint does **not** support full-text search. The server's API overview
separately describes v2 search as structured filtering and points to
Search-a-licious for full-text search. That is a specific contract mismatch worth
checking before an endpoint substitution is treated as a fix.

The changed test registers predetermined product lists for the new URLs and
asserts that those lists are returned. It can check request construction but
cannot prove the remote endpoint applies the text query. No runtime, server-side
or production behavior was reproduced by this intake. Do not claim that current
v2 requests ignore the query solely from a mock or documentation statement.

## Bounded next contribution

Support the existing author with verification of the intended search contract:

1. Inspect the pinned PR's test setup, dependencies, CI and remaining contribution
   policies before running its unchanged unit tests in an isolated environment.
2. Trace current server-side search parameter handling or use an appropriate
   bounded, documented test service to verify query semantics. Compare a matching
   query with a deliberately nonmatching query; a successful HTTP response alone
   is insufficient. Observe the API's field/page limits and request identification.
3. Recheck the discussion and coordinate the documented mismatch with the current
   author if authorized. Agree authentication, supported search endpoint and
   compatibility behavior before altering the SDK. Avoid credentials in URLs.

`CONTRIBUTING.md` on current develop welcomes fork-based PRs against develop and
requires tests/CI. Its setup instructions have been read, not executed. Remaining
AI, license, dependency and test-environment checks are incomplete. No maintainer
confirmation, reviewer commitment or accepted solution is recorded. The item is
OPPORTUNITY-RESEARCH and has no implementation score.

Issue #507 already has two contributors describing the same prepared search
configuration fix. Do not compete with that separate work. A SonarQube quality
comment on #504 is not proof of correct server search semantics; no human reviews
were returned by the inspected PR reviews endpoint.

## Sources

Accessed September 9, 2026:

- [Official public-benefit statement](https://blog.openfoodfacts.org/en/news/why-open-food-facts-is-independent-and-open-and-why-that-matters)
- [SDK repository](https://github.com/openfoodfacts/openfoodfacts-python)
- [Reported search failure #496](https://github.com/openfoodfacts/openfoodfacts-python/issues/496)
- [Maintainer's authentication clarification](https://github.com/openfoodfacts/openfoodfacts-python/issues/496#issuecomment-4865954261)
- [Existing contributor's contract question](https://github.com/openfoodfacts/openfoodfacts-python/issues/496#issuecomment-5027419427)
- [Existing PR #504](https://github.com/openfoodfacts/openfoodfacts-python/pull/504)
- [Pinned proposed request code](https://github.com/arybhatt4533/openfoodfacts-python/blob/970a7290a8a5869de8f5784324c166212fdd15ca/src/openfoodfacts/api.py)
- [Pinned proposed tests](https://github.com/arybhatt4533/openfoodfacts-python/blob/970a7290a8a5869de8f5784324c166212fdd15ca/tests/unit/test_api.py)
- [Official v2 search documentation](https://openfoodfacts.github.io/documentation/docs/Product-Opener/v2/search/get-search/)
- [Official server API overview](https://github.com/openfoodfacts/openfoodfacts-server/blob/main/docs/api/index.md)
- [Current contribution guide](https://github.com/openfoodfacts/openfoodfacts-python/blob/34d0629c970b3887a63c615ace7497a9a28b294b/CONTRIBUTING.md)
