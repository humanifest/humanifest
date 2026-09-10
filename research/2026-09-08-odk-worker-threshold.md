# Queue refill: ODK Central memory threshold

Source review on September 8, 2026 local time. Add one independent opportunity
for [ODK Central #2169](https://github.com/getodk/central/issues/2169): verify a
memory-unit mismatch in the backend worker-count decision. No target checkout,
dependency installation, deployment or target PR was created during the initial reproduction. Subsequent coordination is recorded below.

## Relevance and current scope

ODK's [crisis-response account](https://getodk.org/success-stories/crisis-response/)
identifies American Red Cross use of ODK for disaster-response data collection.
The [Central README](https://github.com/getodk/central/blob/47e2f807a8cf10e8c09a528876ebb5a20d9adf34/README.md)
identifies this repository as the deployment/operations layer for the server that
stores forms and accepts submissions. Efficient operation on constrained servers
has a plausible humanitarian pathway; no particular organization's configuration,
outage, cost saving or deployment benefit is established.

The issue was open and unassigned. Its inspected timeline links broader worker
sizing discussion [#2170](https://github.com/getodk/central/issues/2170), but no PR.
A public PR search for `repo:getodk/central is:pr 2169` returned zero matches. This
is a bounded duplicate check, not an exhaustive guarantee. A contributor's
[production-log excerpt](https://github.com/getodk/central/issues/2169#issuecomment-5450659716)
reports four workers at 2,023,899,136 bytes. That confirms reported units, but the
roughly 2 GB example alone does not distinguish the two threshold interpretations.

The README and [PR template](https://github.com/getodk/central/blob/bc46bbcb80bcb7a0cc04eb57aaeecd3590414671/.github/PULL_REQUEST_TEMPLATE.md)
require code PRs to branch from and target **`next`**, while `master` is production.
The complete inspected startup file is byte-identical on both pinned revisions:

- `master`: `47e2f807a8cf10e8c09a528876ebb5a20d9adf34`
- `next`: `bc46bbcb80bcb7a0cc04eb57aaeecd3590414671`
- Startup SHA-256: `c83aa91370757985a9e3e8f22dcf1437caf9f25213b5afffa9891ea4cc1c4c9f`

## Source and bounded execution

[Startup source](https://github.com/getodk/central/blob/bc46bbcb80bcb7a0cc04eb57aaeecd3590414671/files/service/scripts/start-odk.sh)
converts `/proc/meminfo` into bytes, or reads cgroup v1/v2 limits. The kernel's
[v2 documentation](https://docs.kernel.org/admin-guide/cgroup-v2.html#memory-interface-files)
specifies byte units; [v1 documentation](https://docs.kernel.org/admin-guide/cgroup-v1/memory.html)
documents `memory.limit_in_bytes`. The worker function nevertheless compares the
result with `1100000` and emits either four or one workers.

The [probe](fixtures/odk-worker-threshold-reproduction.py) checks the entire source
hash, extracts only `determine_worker_count`, and runs that function in Bash with
synthetic positional arguments and a minimal environment. It never executes the
rest of startup, which reads secrets, writes configuration, runs migrations and
starts cron/PM2. All eight cases pass:

| Memory input in bytes | Original workers | Comparison using a 1,100,000 KiB threshold |
| --- | ---: | ---: |
| 0 | 1 | 1 |
| 1,100,000 | 1 | 1 |
| 1,100,001 | 4 | 1 |
| 536,870,912 (512 MiB) | 4 | 1 |
| 1,073,741,824 (1 GiB) | 4 | 1 |
| 1,126,400,000 | 4 | 1 |
| 1,126,400,001 | 4 | 4 |
| 2,147,483,648 (2 GiB) | 4 | 4 |

```sh
python3 research/fixtures/odk-worker-threshold-reproduction.py /absolute/path/start-odk.sh
```

The KiB column is an explicitly conditional comparison, not an approved replacement
policy. The issue discusses an older vmstat-derived threshold, but its historical
unit description is imprecise; the [vmstat manual](https://man7.org/linux/man-pages/man8/vmstat.8.html)
distinguishes 1000/1024 and million-byte units. Confirm the intended threshold and
boundary behavior rather than silently changing worker-sizing policy. This probe
does not exercise actual cgroup discovery, Linux container startup, memory pressure,
CPU scheduling or throughput, and does not show a measured resource saving.

## Next bounded job

Inspect the contribution/AI guidance linked from the README and the development
branch's shell-test setup. Then establish whether maintainers want only a unit
normalization and boundary regression tests, separate from #2170's CPU/heap/shared
service sizing policy. Recheck linked work before outreach or implementation.
Use the bot fork and `next` as the upstream base if a contribution is confirmed.

The read service test file exercises DB_SSL startup behavior; no worker/memory
coverage was found in that file. The package manifest uses Node 24.16.0 and broader
tests include Docker, nginx and Playwright. The read Dockerfile installs packages,
sets up PostgreSQL client tooling and exposes the service port. Full setup and
dependency hooks remain unverified. The pure function probe is not full test-suite
or environment readiness evidence.

## Other discovery results

Ushahidi's returned client issues were mostly older test-automation tasks, several
assigned to existing contributors; no new candidate was selected from that list.
The initial `getodk/pyxform` lookup returned 404, so it was not treated as an audited
project. ODK Central's assigned backend-stream and frontend entity tasks were left
with their existing contributors. The worker-threshold investigation supplies a
new independent lane without reopening or repeatedly polling the waiting inquiries.

## Contribution check and subsequent coordination

The linked backend and frontend contribution guidelines were inspected at
`a61b0acbc7d5d8e3bc381523e78e108e60fddfdb` and
`7f40e6f565785da4a433e27f4f7902fa61b5560e`, respectively. Both request issue
coordination and regression tests. No AI-specific requirement was found in those
guides or Central's PR template; that bounded absence is not permission. The
public `getodk/.github` repository lookup returned 404. Central's pinned
`LICENSE.md` contains Apache 2.0 terms. No agreement was signed.

The `next` CI workflow runs shell conventions/ShellCheck, environment substitution,
service, nginx and image tests. The service job uses submodules and runs its npm
command from `test/nginx`; full dependency and container setup remain unverified.
None of these setup or publishing steps were executed.

A scoped inquiry was delivered through `humanifest-bot` at 2026-09-09T03:51:43Z:
[ODK #2169 inquiry](https://github.com/getodk/central/issues/2169#issuecomment-5595510841). The exact author and body were verified.
The issue remained open and unassigned, its discussion contained no competing
claim, the timeline only linked #2170, and a bounded PR search returned no matches.
The inquiry asks about the intended threshold and AI contribution requirements;
it does not claim implementation readiness or measured resource savings. Candidate
state and gates remain unchanged. A September 15 manual review date is recorded;
independent queue work can continue.
