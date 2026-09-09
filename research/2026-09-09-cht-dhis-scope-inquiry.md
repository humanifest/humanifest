# CHT #11342: prepared scope inquiry

Prepared September 9, 2026. **Not sent.** Automatic approval review rejected the
posting action because it interpreted the recorded authorization as covering only
CHT #10155, not this new comment's technical claims and AI disclosure. The exact
message below is ready for user approval. No maintainer interest is inferred.

## Fresh source checks

The issue is open, unassigned and had zero comments immediately before the
attempt. Its timeline contains label/type events, without a linked PR. Separate
open-PR searches for `dhis` and `11342` returned zero matches. These searches are
bounded duplicate checks, not proof that no related work exists.

The linked calendar epic #10707 is now closed (August 28), with completed
milestones and an assignee. Its earlier DMP reservation concerns that epic;
Humanifest is not taking over its work. PR #11237 was merged August 10. These
facts supersede relying on the August 10 issue description's unreleased-epic
status; release inclusion and deployment were not independently established.

An open-PR search for `Bikram` found #11414, which changes date serialization in
calendar interval, writer and webapp code for Nepali locale handling. Its six-file
diff was read. It does not change the DHIS exporter or admin picker; it is related
acceptance context and must be respected in future implementation. Its reported
test results were not independently rerun.

At current master `372677567640d1d3e77e6e46f168fe69a8a9e218`, the exporter and
admin picker have exactly the same SHA-256 hashes as the earlier reproduction:

- Exporter: `3499a7304215ecd75da3fa98320b661e1e6513fc461c0ebd18115c59ebfff70b`
- Picker: `2ed27e30ff2a7d9c9de1e0300819b98bd8af1a686e707d3b1928945f77808aca`

This checks those two source files, not all dependencies or a new full-suite run.
CHT's AI assistance and development workflow pages were re-read; the message
discloses tool use and asks for scope before proposing shared code changes.

## Exact prepared message

Humanifest can help with a bounded contribution here if it is wanted. Before implementing, could we confirm the reporting-period contract?

At `35b2bb6d` (the exporter and admin picker are byte-identical at current master `37267756`), an original-code reproduction with distinct synthetic totals shows that Gregorian `from=2026-07-15` and start day 15 selects July's total, while the writer tags the containing interval August. The same mismatch appears in BS boundary cases. There is also a picker complication: opening it on August 14 versus 15 gives the same “July, 2026” label but retains July 14 versus 15, which fall in different reporting intervals.

Should `from` identify the containing interval, or a fixed period represented by the picker label? Should the smallest fix normalize the picker too, and what should the exported `period` mean in BS mode?

[Reproduction and eight cases](https://github.com/humanifest-bot/humanifest/blob/2da188389c094256faff8a4d4a034d73770f23ce/research/2026-09-09-cht-dhis-period-reproduction.md). The existing 37 calendar tests pass; these probes use synthetic DB/config wiring, not a full deployment. The completed #10707 and open locale fix #11414 were checked; this inquiry is about the remaining export contract, without taking over that locale work.

AI disclosure: OpenAI Codex performed the source audit, wrote and ran the reproduction, and drafted this comment. No human review or production impact measurement is claimed. If this scope is appropriate, we can prepare a focused fork-based PR after the intended behavior is agreed.

## Sources

Accessed September 9, 2026:

- [Issue #11342](https://github.com/medic/cht-core/issues/11342)
- [Completed calendar epic #10707](https://github.com/medic/cht-core/issues/10707)
- [Merged BS target support #11237](https://github.com/medic/cht-core/pull/11237)
- [Open Nepali locale fix #11414](https://github.com/medic/cht-core/pull/11414)
- [Current exporter](https://github.com/medic/cht-core/blob/372677567640d1d3e77e6e46f168fe69a8a9e218/api/src/services/export/dhis.js)
- [Current picker](https://github.com/medic/cht-core/blob/372677567640d1d3e77e6e46f168fe69a8a9e218/admin/src/js/controllers/export-dhis.js)
- [AI guidelines](https://docs.communityhealthtoolkit.org/community/contributing/ai-guidelines/)
- [Development workflow](https://docs.communityhealthtoolkit.org/community/contributing/code/workflow/)
