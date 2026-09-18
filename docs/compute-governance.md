# Compute Governance

Humanifest may use donated, free, sponsored, local, or paid compute only when the
resource is recorded, policy-compatible, and proportionate to a maintainer-approved
or evidence-preserving task.

Compute capacity is not a reason to advance an opportunity. The contribution
protocol still controls maintainer confirmation, external writes, portfolio
capacity, private-data limits, security review, and line-by-line explainability.

## Required Checks

Before using or recommending a compute resource, verify:

- the resource appears in `portfolio/compute-resources.json`;
- its status is `available`;
- allowed and prohibited uses cover the proposed task;
- external writes are separately authorized by `docs/contribution-protocol.md`;
- the actual posting or publishing identity is verified when the task can affect an external project;
- the work is bounded enough that compute use will reduce maintainer burden rather than create speculative output.

If any check fails, record the blocker or use the lowest-risk local/read-only
alternative.

## Resource States

- `available`: verified for the recorded allowed uses.
- `unverified`: known or proposed capacity, but not approved for use yet.
- `paused`: previously usable, currently held pending review.
- `exhausted`: no usable quota or budget remains.
- `retired`: preserved history; do not use.

## Allocation Rule

An allocation records a specific approved purpose. It does not authorize outreach,
issue comments, pull requests, publishing, package uploads, or other external
writes. Those actions require the communication authorization and identity checks
in the contribution protocol.

Do not execute third-party setup code merely because compute is available. Inspect
manifests, lifecycle hooks, Dockerfiles, CI, requested privileges, ports, services,
and secrets first.
