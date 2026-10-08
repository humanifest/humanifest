# Codex implementation plan: CHT #10155

Status: **blocked at `MAINTAINER-CHECK`**. This plan is ready for execution only
after a CHT maintainer confirms the proposed scope and contribution pathway.

## Objective

Fix the CHT admin edit-user modal so a failed user-details request cannot leave
an apparently editable form with blank fields. The modal should show a loading
state while required details are pending, show the existing modal error path
when loading fails, and preserve the successful edit flow.

The live issue remains open, unassigned, and without a linked branch or pull
request as of 2026-09-18. An open Help wanted issue is not maintainer
confirmation; do not implement or post a PR until the scope is confirmed.

## Preconditions and gates

Before touching a target checkout:

1. Recheck issue #10155, its comments, timeline, and competing work.
2. Confirm the maintainer explicitly accepts this bounded scope and the
   disclosed Humanifest contribution pathway.
3. Re-read CHT contribution, AI-assistance, translation, security, and test
   guidance at the current target revision.
4. Inspect manifests, lockfiles, lifecycle hooks, CI, Docker/devcontainer
   files, requested services, ports, and secrets before running setup.
5. Validate the full Humanifest portfolio and confirm implementation capacity.
6. Use a disposable checkout and synthetic data only. Do not use CHT services,
   production credentials, private user data, or the user's personal GitHub
   account.

If any precondition fails, record the reason and stop. Do not advance the
Humanifest opportunity to `BUILDING` by inference.

## Bounded implementation

Expected target surfaces, to be rechecked at the confirmed revision:

- `admin/src/js/controllers/edit-user.js`
- the edit-user modal template
- the relevant admin translation entry
- `admin/tests/unit/controllers/edit-user.spec.js`

Expected controller behavior:

- initialize an explicit `loadingUserDetails` state;
- set `userDetailsLoadFailed` when required detail loading rejects;
- keep the form hidden or non-editable until loading succeeds;
- route the failure through the existing modal error mechanism;
- prevent submit while loading or after a failed load;
- leave successful username population, edit-mode locking, and existing submit
  behavior unchanged.

Do not broaden the change into authentication, API retry policy, modal
framework redesign, translation cleanup beyond the required message, or
production styling/video work.

## Verification plan

Add focused tests for:

1. pending detail requests show loading and prevent submit;
2. failed detail requests show the error state and prevent submit;
3. successful detail requests render the expected fields and preserve the
   existing edit behavior;
4. a failed request cannot be followed by a stale submit;
5. existing controller and modal behavior remains green.

Run the exact target test command only after setup has been audited and
approved, then run the narrowest relevant broader admin suite. Capture the
synthetic loading/error behavior requested in the prior review if the
maintainer still requires it. Record commands, revisions, test counts, and
failures in the Humanifest opportunity before any external write.

## Review and delivery sequence

```text
maintainer confirmation
→ current target recheck and setup audit
→ disposable reproduction baseline
→ smallest implementation and focused tests
→ admin regression suite
→ adversarial review
→ human line-by-line review
→ verify Humanifest bot identity and authorization
→ open one issue-linked PR, only if still authorized
```

The PR must disclose AI assistance and human responsibility, link #10155, show
the tested behavior, avoid claiming clinical impact, and include no secrets or
private data. If the maintainer does not confirm, the correct outcome is to
keep the opportunity in `MAINTAINER-CHECK` or park it—not to submit the prepared
patch.
