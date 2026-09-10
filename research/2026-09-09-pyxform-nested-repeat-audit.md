# XLSForm nested-repeat investigation

Accessed September 9, 2026. Read-only source and discussion review; no clone,
dependency installation, target-code execution, upstream message or patch.

## Why this is queued

[XLSForm/pyxform #821](https://github.com/XLSForm/pyxform/issues/821) is open,
unassigned, and has a concrete request from lognaturel to investigate the effort
needed for consistent initial repeat instances at arbitrary nesting depths.
The inspected open-PR list contains only #830, which addresses entity allocation
for #829. This does not prove nobody is working privately on #821.

The pinned README identifies pyxform as the spreadsheet-to-XForm converter used
by ODK Collect, Web Forms and Enketo, maintained by ODK. ODK publishes an American
Red Cross crisis-response account. These establish a plausible public-benefit
pathway, not a measured benefit from this issue. The related Web Forms discussion
explicitly says the form is usable and the problem was not critical for 1.0.0.
Do not describe missing initial repeats as verified data loss or a high-impact fix.

## Source and test boundary

Inspected master: `26006d0830570ffa3caead24b0c9a470278af2cf`.
GitHub reports the repository unarchived and pushed August 27, 2026.

`Section.xml_instance` (section.py:126) passes an `append_template` flag down the
child tree and inserts a repeat template before the concrete child.
`RepeatingSection.xml_instance_template` (line 270) recursively emits a template
for a direct repeat child, while an intervening ordinary section takes the
`xml_instance` path. These different routes are a hypothesis for a useful test
matrix, not an executed reproduction or an agreed fix.

The two existing tests at test_repeat.py:1044 and :1086 check that templates and
concrete instances exist at nested paths. Their nested XPath expressions leave
the ancestor repeat's template status unconstrained. Consequently, those
assertions alone do not establish that a concrete inner instance exists *inside
the outer template*, which matters when the client creates another outer repeat.
Do not call the existing tests absent or claim they fail. Static AST inspection
finds 68 test methods in that file; none were run here.

The next bounded investigation is to run the unchanged repeat tests after the
remaining import/validator audit, then convert synthetic forms with one, two and
three repeat levels, both directly nested and separated by a group. Inspect
concrete descendants separately under template and concrete ancestors. Include
literal defaults, sibling repeats, and repeat_count absent/zero/nonzero controls.
Keep #462's repeat-count policy separate until maintainers agree the interaction.
A small XML matrix should establish effort and regression risk before a patch.
Client rendering, additions of repeats and saved submissions need separate
verification; converter XML alone cannot prove their behavior.

## Setup and contribution audit

Read the pinned README, PR template, manifest, license, both workflows, commit
scripts, package initializer, section generator and focused test/helper files.
The recursive tree is untruncated; no Dockerfile, conftest, AGENTS or separate
CONTRIBUTING file was found by the inspected filename search.

- README welcomes focused contributions, normally discussed first on the ODK
  forum or an issue. The PR template requires tests, unittest, Ruff and external
  source attribution. No explicit AI/bot policy was established in these files;
  absence is not permission or acceptance of Humanifest's identity.
- License is BSD-2-Clause. Manifest pins three core dependencies: openpyxl 3.1.5,
  defusedxml 0.7.1 and lark 1.3.1. Development adds FormEncode, lxml, psutil and
  Ruff. Flit is the build backend; no lockfile is present in the inspected tree.
- Verification CI tests Python 3.11–3.14 on Linux/macOS/Windows, plus a Python 3.13
  Linux run with ODK Validate. The focused helper defaults external validation
  off, but validator import and conversion call paths still need inspection.
  Java validation is distinct from Python conversion checks.
- pre-commit.sh runs Ruff with mutation enabled; post-commit.sh can amend a commit
  when `.commit` exists. Neither was installed or run. The release workflow uses
  a PyPI token to publish; it is not part of this research environment.

No environment-feasibility gate passes yet. A subsequent isolated setup should
use inspected, pinned wheel dependencies, disabled hooks, no inherited credentials
and a checked network guard, without publishing, launching services or executing
release scripts. No accepted contribution scope or reviewer commitment exists.

## Sources

All accessed September 9, 2026:

- [Repository metadata](https://api.github.com/repos/XLSForm/pyxform)
- [Investigation request](https://github.com/XLSForm/pyxform/issues/821#issuecomment-5208346343)
- [Related client discussion and priority](https://github.com/getodk/web-forms/issues/380#issuecomment-3993922608)
- [Repeat-count interaction #462](https://github.com/XLSForm/pyxform/issues/462)
- [Pinned README](https://github.com/XLSForm/pyxform/blob/26006d0830570ffa3caead24b0c9a470278af2cf/README.md)
- [Pinned generator](https://github.com/XLSForm/pyxform/blob/26006d0830570ffa3caead24b0c9a470278af2cf/pyxform/section.py#L126)
- [Pinned tests](https://github.com/XLSForm/pyxform/blob/26006d0830570ffa3caead24b0c9a470278af2cf/tests/test_repeat.py#L1044)
- [Pinned PR template](https://github.com/XLSForm/pyxform/blob/26006d0830570ffa3caead24b0c9a470278af2cf/.github/PULL_REQUEST_TEMPLATE.md)
- [Pinned manifest](https://github.com/XLSForm/pyxform/blob/26006d0830570ffa3caead24b0c9a470278af2cf/pyproject.toml)
- [ODK crisis-response account](https://getodk.org/success-stories/crisis-response/)

## Subsequent execution

The [runtime investigation](2026-09-09-pyxform-repeat-runtime.md) now records the
completed focused baseline and fifteen actual converter cases. It supersedes the
not-yet-run status above while preserving the original source-audit provenance.
The opportunity is at MAINTAINER-CHECK; no implementation or client outcome is claimed.
