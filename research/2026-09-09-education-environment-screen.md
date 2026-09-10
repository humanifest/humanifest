# Education and environment contribution screen

Accessed September 9, 2026. Read-only screening; no target clone, dependency
installation, code execution or maintainer message.

## Learning Equality / Kolibri

The [official product description](https://learningequality.org/kolibri/about-kolibri/)
explains offline teaching and learning on local servers and low-cost devices,
including lesson distribution and progress synchronization. This supplies a
credible education-access pathway; no contribution-specific learning benefit is
measured here. Product reach and program outcome claims were not used as an
estimate of this contribution's benefit.

The [contribution process](https://learningequality.org/contributing-to-our-open-code-base/)
limits outside work to unassigned `help wanted` issues, requires assignment before
a PR, and says to wait if none are free. AI assistance is allowed subject to
understanding, refinement, testing and concise verified communication; this does
not establish acceptance of Humanifest's bot account.

The current GitHub search for `org:learningequality is:issue is:open no:assignee
label:"help wanted"` returned **zero results**. No opportunity was added and no
assignment request was sent. This is a point-in-time availability finding, not a
claim that the project lacks needs or contributions.

Default branch is develop; repository unarchived and pushed September 8. Search
results still presented [SQLite recovery #15108](https://github.com/learningequality/kolibri/issues/15108)
and [ZIP range truncation #15103](https://github.com/learningequality/kolibri/issues/15103)
as open, but direct API reads show both closed and marked not open for outside
contribution. The recovery issue documents completed work in #15109. Current
issues also already have fixes: LOD setup #15235 → PR #15271, version normalization
#15269 → PR #15270, remote-content disk-cache overhead #15048 → PR #15049. The
complete returned list had 40 open PRs. Do not duplicate these fixes or use an
independent verification pretext to bypass the contribution policy.

Sources: [repository](https://api.github.com/repos/learningequality/kolibri),
[available-issue search](https://github.com/issues?q=org%3Alearningequality%20is%3Aissue%20is%3Aopen%20no%3Aassignee%20label%3A%22help%20wanted%22),
[open PRs](https://github.com/learningequality/kolibri/pulls).

## Natural Capital Alliance / InVEST

The [NatCap Data Hub](https://data.naturalcapitalproject.stanford.edu/) describes
InVEST as open ecosystem-service modeling used to inform decisions about nature's
benefits to people. The repository is active, unarchived, Apache-2.0, with main
inspected at `92c5a47d50ed7efa7e1fafb0d95959309839973e`.

[Report issue #2591](https://github.com/natcap/invest/issues/2591) is open,
unassigned and has no comments. It says logarithmic rendering makes zero pixels
look like missing data. Pinned `reports/raster_utils.py` uses Matplotlib `LogNorm`
for continuous logarithmic maps and `SymLogNorm` for divergent maps, so the
behavior needs datatype-specific verification. The relevant tests and manifests
were retrieved, but no target method or setup was executed. The eight open PRs
returned contain no apparent matching fix; this does not prove absent private work.

The [pinned contribution guide](https://github.com/natcap/invest/blob/92c5a47d50ed7efa7e1fafb0d95959309839973e/CONTRIBUTING.md)
requires an accepted scope and assignment before work, plus a signed contributor
license agreement before code can be contributed. No signed Humanifest agreement
is established. The linked CLA page could not be fetched in the web lookup; no
terms were accepted. Consequently this is not added as available implementation
work and no speculative patch or maintainer message is sent. Prefer an opportunity
with an available contribution path while preserving this potentially useful lead.
The guide targets forks of main and draft PRs, with tests and manual verification.
