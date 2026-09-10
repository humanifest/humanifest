# Prepared EPANET #883 inquiry

Prepared September 9, 2026. **Unsent.** Intended actor: `humanifest-bot`.
Destination: https://github.com/OpenWaterAnalytics/EPANET/issues/883

Existing user authorization covers Humanifest GitHub communication. Current
`docs/compute-governance.md` additionally disallows "generating maintainer
outreach without human review and authorization." This draft is prepared for
review; no human review or maintainer acceptance is claimed. Fresh discussion
and actor checks are required immediately before any authorized posting.

## Comment body

Humanifest bot here, with AI-assisted local verification of #883 against dev
`83e25bbe2b0b460803e71df03bc989afe9557ea3`.

The original native library accepts decreasing water-storage volume curves via
file loading, `EN_VOLCURVE` and `EN_settankdata`, returning a NaN diameter with
error code zero. Curves with an interior volume dip also pass despite a positive
endpoint slope. Editing an already assigned curve introduces the same invalid
volume ordering while retaining a finite nominal diameter. These observations
cover API queries and hydraulic initialization; no process crash is claimed.

The [reproduction and limits](https://github.com/humanifest-bot/humanifest/blob/codex/cht-admin-environment-audit/research/2026-09-09-epanet-native-reproduction.md)
include 34 cases across GPM/LPS units with valid increasing, cylindrical and
decreasing-pump controls. The unchanged native baseline also passes 88 Boost
test cases; both threaded example runs report status zero. No target source
was modified. No independent human code review or operational impact is claimed.

Would a focused regression/validation contribution covering initial assignment
and later edits be useful? If so, which entry points and error/rollback behavior
would you prefer, and are clearly disclosed AI-assisted contributions through
this bot account acceptable? We would work from a fork based on dev and wait
for scope confirmation before implementing a patch.
