# IFRC contribution requirements and impact check

Reviewed September 8, 2026 local time, using the clean target checkout at
`7dd2d48cd599c3e0b894f1676b5de88c19028c46` and the public sources below.

## Documented contribution path

The pinned [README](https://github.com/IFRCGo/pystac-monty/blob/7dd2d48cd599c3e0b894f1676b5de88c19028c46/README.md)
welcomes issues and PRs and describes pytest with recorded HTTP responses.
[CI](https://github.com/IFRCGo/pystac-monty/blob/7dd2d48cd599c3e0b894f1676b5de88c19028c46/.github/workflows/ci.yml)
checks out the schema submodule and tests Python 3.11–3.13 on Ubuntu; it also checks
hazard-taxonomy drift. The separate lint workflow runs pre-commit. The
[hook configuration](https://github.com/IFRCGo/pystac-monty/blob/7dd2d48cd599c3e0b894f1676b5de88c19028c46/.pre-commit-config.yaml)
includes Ruff lint/format, Pyright, locked dependency checks, conventional commit
messages, basic file checks and a 100 KiB added-file limit. A separate
[PR-title workflow](https://github.com/IFRCGo/pystac-monty/blob/7dd2d48cd599c3e0b894f1676b5de88c19028c46/.github/workflows/lint-pr-title.yml)
requires a semantic title. Existing local USGS tests do not prove this entire matrix.

The complete tracked target tree contains no separate CONTRIBUTING, CODEOWNERS,
CLA/DCO, NOTICE or PR-template file. Searches of README, docs, workflows, manifest
and hook configuration found no explicit bot/AI rule. GitHub's
[community profile](https://api.github.com/repos/IFRCGo/pystac-monty/community/profile)
returned null contribution, code-of-conduct and PR-template fields. The public
`IFRCGo/.github` repository lookup returned HTTP 404. Those bounded observations
do not establish that no organization policy or separate agreement exists.
The schema submodule has its own code of conduct; its presence is not evidence
of an AI rule for this Python repository.

The [license notice](https://github.com/IFRCGo/pystac-monty/blob/7dd2d48cd599c3e0b894f1676b5de88c19028c46/LICENSE)
and manifest explicitly declare Apache-2.0. GitHub's profile reports NOASSERTION;
that scanner result does not override the explicit source declaration. The full
[Apache 2.0 terms](https://www.apache.org/licenses/LICENSE-2.0) were read: preserve
applicable notices, include the license when redistributing, identify changed files,
and retain applicable NOTICE attribution. Contributions default to those terms
unless explicitly stated otherwise; separate agreements are not superseded.
No agreement was signed, trademark permission claimed, or target package distributed.

The documented contribution workflow and narrow licensing review are now complete.
The proposed work adds no dependency, secret or external service. Bot/AI acceptance,
current scope, reviewer availability and benefit remain unresolved. The existing
[bot inquiry](https://github.com/IFRCGo/pystac-monty/issues/199#issuecomment-5594287228)
already asks about scope and AI acceptance; no duplicate message was posted.

## Check against an archived public input

The [archived payload](fixtures/usgs-us6000t7zp-alerts.json) contains the exact 1,455
bytes retrieved during the earlier September 8 audit from the versioned
[USGS product URL](https://earthquake.usgs.gov/product/losspager/us6000t7zp/us/1783916550513/json/alerts.json).
SHA-256: `4058bea104960004b80cde32d21e3465d5bde9104fcd097eb5fe92d475177b68`.
The browser fetch in this review failed; this run uses the archived bytes, not a
claimed fresh retrieval. Both the payload and original transformer are hash-checked.

The [extended arithmetic probe](fixtures/ifrc-usgs-rounding-reproduction.py) retains
its four synthetic/control cases and adds the archived economic bins. All five pass:

```sh
python3 research/fixtures/ifrc-usgs-rounding-reproduction.py /absolute/path/to/pystac_monty/sources/usgs.py
```

| Same midpoint formula | Output in USD |
| --- | ---: |
| Original helper truncates, then caller scales | 1,768,846,000,000 |
| Independent Decimal calculation scales before truncation | 1,768,846,489,394 |
| Difference | 489,394 |

The difference is approximately 0.00002767% of the scale-first result. This confirms
that the arithmetic discrepancy occurs for these archived bins, but does not
demonstrate meaningful downstream harm in this sample. The synthetic submillion
case remains a useful boundary test; its frequency in consumed data is unknown.
Neither output is asserted to be an observed loss, an official USGS point estimate,
or a validated substitute for the distribution. USGS's
[PAGER background](https://earthquake.usgs.gov/data/pager/background.php) describes
estimated loss ranges and emphasizes uncertainty; this check preserves the existing
library midpoint formula rather than validating that model.

Keep `problem_current_and_consequential` and `benefit_justifies_review_cost` false
until downstream use or maintainer prioritization supports them. Remove the completed
policy-review step from the active research queue; continue other candidates while
this scoped inquiry awaits a useful response.
