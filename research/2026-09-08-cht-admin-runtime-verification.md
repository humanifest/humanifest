# CHT #10155: admin baseline and controller reproduction

Executed September 8, 2026 local time (September 9 UTC), against an unmodified
archive of `medic/cht-core@35b2bb6dac0844bee3228476591d08d56c5dd10d`.
All **431 existing admin tests** pass. Three additional synthetic probes of the
original Angular controller also pass: successful SSO lookup populates the edit
model; rejected SSO lookup and failed settings leave it unset and call the logger
without calling the modal's error callback. These are current-behavior assertions,
not acceptance assertions for a fix.

The opportunity stays in `MAINTAINER-CHECK`. A subsequent two-case DOM run below
extends the controller evidence to the compiled modal. Neither run establishes a
new maintainer reply, production-styled modal appearance, a loading-state video,
translation review, or permission to implement. No target source or existing
preparation patch changed.

## Inspected setup and actual runner

The earlier [source audit](2026-09-08-cht-admin-environment-audit.md) identified the
root/admin lockfiles, hooks, CI, browser launcher, dependency patches and builders.
This run additionally inspected the admin entry point, datasource compiler
configuration, root workspace lifecycle declarations and installed Chrome launcher.
The root lock has 3,561 package entries, including native/browser-driver hooks and
one Git dependency. The admin lock has 105 entries and a core-js hook. All automatic
install hooks were disabled. The pinned [Git dependency manifest](https://github.com/medic/openrosa-formlist/blob/3ce85a8678411f7cefb09227f5e7ac07829ab233/package.json)
declares test/doc scripts but no installation or prepare hook (accessed September 8).

Docker was unavailable: the authorized daemon check returned “Cannot connect to
the Docker daemon.” The actual runner was a separate temporary local directory,
`/private/tmp/humanifest-cht-baseline`, on macOS 26.6.2 arm64. It is **not a VM or
container security boundary**. Node 22.16.0, npm 11.6.2, Chrome 153.0.8010.36 and
Karma 6.4.4 were used. The nine modified files in the separate historical
`/private/tmp/humanifest-cht-core` checkout remain untouched.

Child environments were constructed from an allowlist, without inherited account
tokens, SSH agent, production settings or registry credentials. npm used an empty
user/global configuration and separate temporary cache. Git used no system/global
configuration, an empty credential helper, disabled prompts, and a process-local
SSH-to-HTTPS rewrite for the pinned public Git dependency. No global configuration
was changed. Dependency installation was not a vulnerability audit.

## Executed sequence

An archive from Git's committed objects supplied the clean baseline. From its root,
the following commands ran in order with the inspected Node binary on PATH:

```sh
npm ci --ignore-scripts --no-audit --no-fund
npm --prefix admin ci --ignore-scripts --no-audit --no-fund
node node_modules/patch-package/index.js
node node_modules/typescript/bin/tsc -p shared-libs/cht-datasource/tsconfig.build.json
node scripts/build/build-angularjs-template-cache.js
PATH="$PWD/node_modules/.bin:$PATH" bash scripts/build/browserify-admin.sh
```

The admin installation was actually invoked with `admin/` as its working directory;
the prefix form above expresses the same scoped command. Automatic hooks stayed
disabled; only the two inspected patches and explicit compiler/bundler steps ran.
The datasource build is necessary because the admin data-context service imports
its generated `dist` entry point. The broader build/CI scripts, webapp build,
CouchDB, API, Docker images and publication steps were not run.

After freshly generating the bundles, set `HUMANIFEST_CHT_CHECKOUT` to the absolute
baseline path and `CHROME_BIN` to the explicit browser executable. Run these from
the Humanifest checkout in the same sanitized environment:

```sh
node research/fixtures/run_cht_admin_baseline.cjs
node research/fixtures/run_cht_admin_baseline.cjs --reproduce
```

The [runner](fixtures/run_cht_admin_baseline.cjs) verifies SHA-256 hashes of both
lockfiles and the original Karma config, edit-user controller, template and test
file. Its only baseline runner changes are single-run/nonwatch mode, a custom
headless Chrome launcher and loopback binding. Karma reports
`http://127.0.0.1:19876/`; Chrome debugging uses loopback and an ephemeral port.
The installed Chrome launcher supplies a fresh temporary user profile. No
`--no-sandbox` flag or personal browser profile is used. This is not a claim that
the entire test process had network egress blocked.

The reproduction mode adds the [three synthetic controller probes](fixtures/cht-edit-user-load-reproduction.spec.js)
and selects only their describe block. They use Q as the upstream tests do and
mock HTTP, settings and datasource inputs. Modal rendering and contact widgets are
deliberately not invoked. The actual controller and browser bundle are exercised.

## Results and limits

| Step | Observed result | Wall time |
| --- | --- | --- |
| Root locked install | 3,456 packages installed; exit 0 | 227.2 seconds |
| Admin locked install | 94 packages installed; exit 0 | 6.4 seconds |
| Apply target dependency patches | Both applied; exit 0 | 0.1 seconds |
| Compile datasource | Exit 0 | 1.1 seconds |
| Generate templates / main bundle | Both exit 0 | <0.1 / 3.1 seconds |
| Existing admin suite | 431 of 431 pass; exit 0 | 6.9 seconds |
| Synthetic controller probes | 3 of 3 pass; exit 0 | 1.7 seconds |

Measured disk usage was approximately 1.4 GiB for the baseline and 246 MiB for its
separate npm cache (`du -sh` rounded values). Peak RAM and CPU use were not measured.
All 2,767 tracked blobs in the archive were compared with the pinned Git objects
after the build and matched. No lockfile edits or target fixes were needed.
Karma warned about a duplicate Chai entry already present in the upstream config;
there were no test failures. npm emitted dependency deprecation warnings.

The browser user-agent reports macOS 10.15.7; the host version above comes from
`sw_vers`, not that reduced user-agent string. Runtime feasibility is established
for these admin tests on this host, not for every supported platform or full CHT
deployment. Controller failure is reproduced; the subsequent DOM run below verifies
the compiled modal, while the requested video remains separate work. Once scope is confirmed, a patch needs
new assertions for visible loading/error behavior and unchanged successful flows;
these current-fault probes must not be treated as the fix's acceptance criteria.

## Compiled modal verification

The additional [DOM probes](fixtures/cht-edit-user-dom-reproduction.spec.js) run with:

```sh
node research/fixtures/run_cht_admin_baseline.cjs --dom
```

The original `Modal` service constructs the scope and status callbacks. The original
controller, `edit_user.html`, `mmModal` directive and `modal.html` are compiled by
Angular and attached to the Chrome test document. The runner now also checks hashes
for the modal service, directive and template. HTTP, permission and translation
inputs are synthetic; unexpected database access is forbidden in the test injector.
Bootstrap's window creation is stubbed, and contact-widget initialization remains
deferred. No production styles or complete live CHT application are loaded.

Two tests pass in Chrome (2.4 seconds wall time):

- While the existing user's SSO lookup is pending, the username input is connected,
  has nonzero layout height, is empty and enabled; the title says `Add User`, the
  visible submit action is enabled, and there is no modal error alert. Resolving
  that same lookup fills `synthetic-user`, disables username editing and changes
  the title to `Edit User`.
- After a rejected lookup, the form retains that same blank `Add User` state, with
  no error alert and `status.error` false; the controller logged the failure.

These DOM measurements demonstrate the misleading pending/failure state. They do
not establish what submitting that form would do, production CSS appearance,
screen-reader behavior, translation quality, or a corrected loading-state video.
The assertions intentionally describe the fault; a fix needs opposite expectations.

The first two harness attempts failed because CHT's document-ready bootstrap ran
after the test had attached an already-compiled modal. A second injector attempted
to compile it again, triggered the real local session lookup, and produced
transclusion errors plus a login-page reload. Adding provider stubs alone did not
fix this ordering problem. The final harness waits for document-ready callbacks
to finish on the empty page before attaching test DOM. The passing run had no
session request or reload; it retained the known duplicate-Chai warning and a
local 404 for the unserved password-icon SVG. These harness failures are not
additional CHT issue reproductions.

The completed DOM research step has been removed from the opportunity record.
Further implementation remains gated on confirmation, while independent research
for other candidates remains available.
