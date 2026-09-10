# IFRC USGS runtime verification

Verified on 2026-09-08 local time. The rounding finding now reproduces through
the unmodified transformer into serialized STAC impact items, with networking
blocked. This strengthens the earlier arithmetic probe; it is not a production
incident, scientific validation of the midpoint model, or a completed fix.

## Environment and inspected setup

- Temporary checkout: `/private/tmp/humanifest-ifrc-pystac-monty`, outside Humanifest.
- Source: `7dd2d48cd599c3e0b894f1676b5de88c19028c46`.
- Schema submodule: `b363a751f2d51b4169cd08aa5c17f0fc7b985763`, retrieved over HTTPS;
  a local URL override avoids requiring SSH credentials. No tracked file changed.
- Actual interpreter: `/opt/homebrew/bin/python3.13`, Python **3.13.9**.
- `uv.lock` SHA-256: `099f95a6e2fad445dd30d5d4c0805a328b91d1ae0a33245869340c4c05f24055`.
- Installed 86 locked packages into the temporary `.venv`, with a temporary cache,
  using `uv sync --frozen --no-build --no-install-project`. Only prebuilt wheels
  were permitted; no target package build or global package installation occurred.

The manifest, lockfile source types, pre-commit hooks, workflow files, test
configuration, imported transformer modules and submodule configuration were
inspected first. The repository has no Docker setup in the inspected tree.
The development hooks can modify files, install their own tools and validate the
lockfile; none were installed or run. Publishing/docs workflows were not invoked.
The focused test path needs local fixtures and the schema submodule, not secrets,
listening ports, a database or a deployment.

Two early installation attempts stopped before dependency installation because
the command environments resolved `python3` differently and selected Python 3.14.
The pinned Fiona version lacks the required 3.14 wheel. Selecting the verified
absolute 3.13 executable resolved this without enabling source builds. Use the
explicit interpreter in this setup recipe; do not rely on the name `python3`.

## Executed checks

From the temporary checkout, using its `.venv`:

```sh
HUMANIFEST_IFRC_CHECKOUT=/private/tmp/humanifest-ifrc-pystac-monty \
  .venv/bin/python -m pytest \
  /Users/admin/dev/humanifest/research/fixtures/test_ifrc_usgs_item_reproduction.py \
  --block-network --record-mode=none -q -s
.venv/bin/python -m pytest tests/extensions/test_usgs.py \
  --block-network --record-mode=none -q
```

Results:

- **3/3 item-level reproduction cases passed** in 21.97 seconds. They use real
  input models, event/hazard construction, the local geocoder, impact construction
  and output serialization. No external STAC schema validation is requested by
  the new probe. Four items are emitted in each case; two have impact roles.
- Economic outputs: **0 USD** for a synthetic 0–1 million bin; **5,000,000 USD**
  for a 1–10 million bin; **1,000,000 USD** for the exact-integer control.
- The existing synthetic fatality fixture remains **139 people** in all three
  cases. The economic item's country code remains `VEN`.
- **8/8 existing USGS tests passed** in 1.91 seconds, including their existing
  schema checks, with network blocking and cassette rewriting disabled.
- Ruff passed for the new reproduction module. Both test commands exited zero.
  The sandbox emitted Arrow CPU-capability warnings and a shutdown
  `sys.excepthook` diagnostic without an exception body; no test failure was
  reported. These diagnostics remain an environment limitation, not a claimed
  target regression.

The [reproduction module](fixtures/test_ifrc_usgs_item_reproduction.py) verifies
the unmodified transformer's source hash before importing it. Its assertions
confirm the currently observed incorrect values; a future fix needs separate
acceptance assertions for 500,000 and 5,500,000 USD and unchanged controls.
It deliberately cannot silently run against a modified transformer.

## Remaining decisions

The focused environment and runtime reproduction gates can now pass. The whole
project suite, all supported Python versions, deployment, and realized benefit
have not been verified. Scope confirmation and contribution/AI expectations are
still needed before implementation. The unit-conversion precision proposal must
preserve fatality behavior and remain separate from the paused uncertainty-model
redesign. The current target checkout is clean and reusable for that work.

## Coordination

The [precision-fix inquiry](https://github.com/IFRCGo/pystac-monty/issues/199#issuecomment-5594287228)
was delivered by `humanifest-bot` at 2026-09-09T01:18:23Z (September 8 local
time), under the user's standing GitHub communication authorization. It reports
the synthetic runtime evidence and asks for scope and bot/AI-contribution
acceptance. Source head and issue openness were checked immediately beforehand;
GitHub confirmed author and exact body. This is not maintainer confirmation.
The opportunity remains gated in `MAINTAINER-CHECK`, with September 15 as the
planned status check absent an actionable reply. Independent work can continue.
