# XLSForm #821: nested-repeat runtime evidence

Verified September 9, 2026. This continues the [source/setup audit](2026-09-09-pyxform-nested-repeat-audit.md).
No upstream patch, message, assignment or accepted scope is claimed.

## Environment and unchanged baseline

Disposable checkout: `/private/tmp/humanifest-pyxform-baseline`, pinned to
`26006d0830570ffa3caead24b0c9a470278af2cf`. The inspected raw files matched the
checkout. The runner verifies all **249 tracked source files** against that
revision's Git blob hashes before and after execution, not just selected files.
Git hooks and inherited Git configuration/credentials were disabled for retrieval.

After inspecting the converter, builder, test helper and validator imports, the
existing Python 3.13.7 created a separate virtual environment. Wheel-only pip
installation used the seven exact core/dev versions in the manifest and resolved
et-xmlfile 2.0.0. Installed versions: openpyxl 3.1.5, defusedxml 0.7.1, lark 1.3.1,
FormEncode 2.1.1, lxml 6.1.1, psutil 7.2.2, Ruff 0.15.21 and et-xmlfile 2.0.0.
No project build/install, global environment change, release hook or server ran.
The manifest has no lockfile; this is a recorded wheel resolution, not a frozen
upstream lock reproduction.

The [runner](fixtures/run_pyxform_repeat_verification.py) starts a child with a
minimal environment and disables Python socket connection/DNS/bind/listen,
subprocess.Popen and os.system before target imports. Connection, DNS and process
launch probes confirm rejection. This prevents accidental calls through those
Python interfaces; it is not an OS sandbox or native-code isolation guarantee.

The original `tests.test_repeat` suite collected 68 tests. Two explicitly invoke
Java even when the general validation flag is false. macOS java_home reports no
Java runtime, so the runner names and defers exactly those two empty-repeat tests:
`test_empty_repeat__no_question__ok` and
`test_empty_repeat__no_question_control__ok`. Of the remaining **66 tests,
65 passed and one retained its upstream slow-performance skip** (0.113 seconds).
No test body or target source was edited. The full suite, Java validator and CI
platform matrix were not run; this is a focused Python baseline.

## Fifteen actual converter cases

The runner calls the original `convert(..., validate=False)` on synthetic forms:
one, two and three repeat levels; direct nesting or a group between levels; and
repeat_count absent, zero or two. Each repeat has a literal default. An independent
sibling repeat tests that template state does not leak out of the nested branch.
These are actual conversions and parsed output assertions, not mocked generators.

| Structure, with repeat_count absent | Inside outer template | Inside initial concrete outer repeat |
| --- | --- | --- |
| One repeat level | No inner repeat | No inner repeat |
| Two directly nested repeats | Inner template only | Concrete inner instance |
| Two repeats separated by a group | Inner template **and concrete inner instance** | Concrete inner instance |
| Three directly nested repeats | Template chain only | Concrete chain |
| Three levels separated by groups | Concrete children also occur under template ancestors | Concrete chain |

All **15 cases** satisfy the recorded current-behavior checks. Direct nesting
omits the concrete inner child under the outer template; the grouped control has
one. Every repeat's own question/default and the sibling template/concrete pair
survive. Zero/two repeat_count produces the corresponding calculation bindings,
but the initial instance tree is identical across the three count settings. That
last result is an XML fact, not a conclusion about runtime client repeat counts.

The existing nested-template tests pass because their ancestor predicates allow
template and concrete branches to be searched together. They do not assert a
concrete inner child specifically under the outer template. This supports adding
ancestor-specific assertions once the desired compatibility contract is agreed.

## Interpretation and next action

The source hypothesis is now reproduced: direct-repeat recursion in
`RepeatingSection.xml_instance_template` and the ordinary-group recursion route
produce different initial structures. A fix cannot be justified solely by adding
one child everywhere: arbitrary nesting, template uniqueness, defaults and
repeat_count interactions require an agreed contract. #462 remains a separate
policy question. Actual client rendering, adding repeats and saved submissions
were not exercised; data loss, deployment benefit and criticality remain unproven.

A concise verification message is prepared, **not sent**:

> Using OpenAI Codex, I checked pinned master 26006d0 for #821. The unchanged repeat
> tests pass in a focused Python run: 65 passed, one upstream skip, and two
> Java-only tests deferred. Fifteen actual converter cases distinguish concrete
> children under template versus concrete ancestors. Directly nested repeats lack
> a concrete inner child under the outer template, while an intervening group
> creates one; literal defaults and sibling controls survive. I have not tested
> client behavior or changed the generator. Would an ancestor-specific XML matrix
> and effort assessment be useful before agreeing a compatibility fix, keeping
> #462's repeat-count policy separate?

Confirm the bot contribution pathway, accepted support scope and reviewer before
advancing beyond MAINTAINER-CHECK. Recheck discussion and posting authorization
before delivering the note.

## Reproduce

After the audited wheel environment exists:

```sh
python3 research/fixtures/run_pyxform_repeat_verification.py /absolute/path/to/pinned-checkout baseline
python3 research/fixtures/run_pyxform_repeat_verification.py /absolute/path/to/pinned-checkout matrix
```

The matrix prints each repeat path with `T` for template or `C` for concrete,
plus the repeat-count calculations and warnings. The research runner and synthetic
inputs are Humanifest additions; all target code remains original.

Sources, accessed September 9, are linked in the preceding audit, including the
[pinned generator](https://github.com/XLSForm/pyxform/blob/26006d0830570ffa3caead24b0c9a470278af2cf/pyxform/section.py#L270),
[existing tests](https://github.com/XLSForm/pyxform/blob/26006d0830570ffa3caead24b0c9a470278af2cf/tests/test_repeat.py#L1044),
and [maintainer investigation request](https://github.com/XLSForm/pyxform/issues/821#issuecomment-5208346343).
