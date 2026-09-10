# Cause Discovery

Humanifest starts with causes, not repositories. The default discovery mode is
`global-impact`: look first for large, neglected, tractable sources of harm, then
ask where donated software work can plausibly improve a real operational pathway.
The user's personal skills matter as a feasibility and explanation constraint,
but they are not the first ranking criterion.

This restores the intended loop from the "Continuously Seek Worthy Causes"
planning thread:

```text
global burden signal
→ neglectedness and tractability review
→ software-leverage hypothesis
→ active OSS project search
→ issue/opportunity audit
→ maintainer check
→ bounded contribution
→ acceptance, release, and benefit evidence
```

## Cause Records

Cause records live in `portfolio/causes/*.json` and validate against
`schemas/cause.schema.json`. They are upstream of project and opportunity
records:

- cause records decide where discovery attention should go;
- project records decide whether an OSS project is a credible pathway;
- opportunity records decide whether a specific issue is ready for contribution.

Do not use a cause score to claim realized impact. A high cause score means only
that Humanifest should spend discovery effort there. A patch still needs its own
evidence, gates, tests, maintainer confirmation, and deployment path.

## Decision Modes

`global-impact` is the default. It ranks by expected public benefit before
personal fit.

`personal-fit` is allowed only when the user explicitly wants to spend a fixed
block of their own time where their skills are unusually helpful. Even then,
cause burden and maintainer burden stay visible.

## Metrics

Cause scores use six directional inputs from 0 to 5:

- `global_burden`: deaths, DALYs, affected people, economic disruption, or other
  public-harm measure, with the unit named in evidence.
- `neglectedness`: whether the problem receives less engineering support than
  its burden and tractability suggest.
- `tractability`: whether known interventions or operational improvements exist.
- `software_leverage`: whether software quality, interoperability, automation,
  data quality, or reliability plausibly affects the intervention pathway.
- `maintainer_pathway`: whether active, contribution-friendly OSS projects are
  visible enough to seed project records.
- `uncertainty_penalty`: weakness, staleness, indirectness, or missingness in the
  evidence.

Weights live in `humanifest.models.CAUSE_SCORE_WEIGHTS`. They are deliberately
simple so reviewers can argue with them.

## Search Discipline

Prefer public, stable sources for first-pass burden metrics: WHO, IHME/GBD, UN
agencies, World Bank, peer-reviewed systematic reviews, and project-maintainer
documentation. Record access dates. If a claim depends on current facts, refresh
the source before relying on it.

Move from cause to project only after writing a falsifiable software-leverage
hypothesis, for example: "offline malaria case reporting failures create delayed
surveillance records that an active OSS workflow could reduce." Then look for
real projects and current issues. Park the cause or pathway if the software link
is too speculative, private data would be needed, or maintainers would absorb
more burden than the contribution can justify.

## Commands

```bash
python3 -m humanifest.cli causes --root .
python3 -m humanifest.cli cause-score portfolio/causes/malaria-control-data-systems.json
python3 -m humanifest.cli validate --root .
```
