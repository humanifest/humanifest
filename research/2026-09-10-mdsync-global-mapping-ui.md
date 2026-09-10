# MetaData Sync: original Global Mapping browser probe

Accessed and executed September 10, 2026. Target revision:
`78c8b8c22278dcbb7d2d5678eaafaa80b0fd0cf9`.

The original Global Mapping selector omits indicator types in the rendered
interface. A category control successfully selects, saves, reloads and replaces
its destination mapping. This narrows issue #1255 to the missing type and its
import semantics; it does not establish how a real DHIS2 destination would be
updated or grant permission to implement a feature.

## Observations

Using the Codex in-app browser against the loopback-only synthetic probe:

1. Opened the original `InstanceMappingPage` with router section `global`.
   Its menu displayed **Category, Category Combo, Category Option, Category
   Option Group, Category Option Group Set, Tracker Data Elements, Option**.
   No indicator-type item was present.
2. Opened **Set mapping** for `CatSource01`. The original `MappingDialog`
   displayed two synthetic destination categories, A and B.
3. Selected A. Closing the dialog showed `CatTarget01`, **Synthetic target
   category A**, and **Mapped (Global)** in the original table.
4. Reloaded the whole page. Those values survived. Reopening the picker showed
   **Only selected items** checked, A's checkbox checked and one visible row.
5. Cleared the selected-only filter and selected B. A became unchecked and B
   checked. Closing showed `CatTarget02`, **Synthetic target category B** and
   **Mapped (Global)**. A second full reload preserved B.
6. Expanded the probe's receipt. The original apply use case received
   `mappingType: categories`, `global: true`, selection `CatSource01` and
   destination `CatTarget02`. The original repository saved this mapping under
   namespace `mappings`; the prior reload had read A from the same stored object.

The receipt's final mapping dictionary was:

```json
{
  "categories": {
    "CatSource01": {
      "mappedId": "CatTarget02",
      "mappedName": "Synthetic target category B",
      "mappedCode": "TARGET_B",
      "code": "SOURCE",
      "conflicts": false,
      "global": true,
      "mapping": {}
    }
  }
}
```

These are manually observed browser checks, not an automated browser test suite.
The screenshot also showed the missing Material Icons font as clipped text in
one icon button. The accessible **Set mapping** action worked; this isolated
probe does not establish the full application's visual styling.

## Original code and synthetic boundaries

The [reusable fixture](fixtures/mdsync-global-mapping-ui/global-mapping-ui.tsx)
imports unchanged `InstanceMappingPage`, `MappingTable`, `MappingDialog`,
`MetadataTable`, original model classes, UI providers and DHIS2 API schemas.
It also uses original `ApplyMappingUseCase`/`GenericMappingUseCase`,
`GetMappingByOwnerUseCase`, `SaveMappingUseCase`, `DataSourceMapping` and
`MappingD2ApiRepository`. Neither UI components nor mapping algorithms are
reimplemented in the fixture.

AppContext composition wiring and instance validation are synthetic. Metadata
list/read/default-ID services return synthetic categories. The storage-client
boundary serializes to browser `localStorage` under the dedicated key
`humanifest-md-sync-synthetic-mapping`. Therefore this verifies the original
repository's serialization and UI restore path, **not DHIS2 datastore persistence**.
Only category data is implemented; selecting another collection deliberately
fails rather than inventing results. No operational instance or real category
was accessed. The fixture has no credentials.

## Reproduction and integrity

Use the already audited external checkout and its pinned Node 22.22.0/Yarn
4.12.0 dependency installation from the [native workflow audit](2026-09-10-mdsync-native-workflow.md).
For a fresh installation, inspect current setup instructions first and use
`--immutable --mode=skip-build`; `enableScripts: false` alone does not disable
workspace postinstall. Do not copy external target source into Humanifest.

Copy the three `.tsx`, `.html` and config files from
`research/fixtures/mdsync-global-mapping-ui/` into the target checkout's
`humanifest-probes/`. From that checkout:

```sh
node node_modules/vite/bin/vite.js build --config humanifest-probes/vite.ui.config.ts
python3 /path/to/humanifest/research/fixtures/mdsync-global-mapping-ui/serve.py humanifest-ui-dist
```

Use the pinned Node executable and an explicit environment without inherited
credentials. The observed build ran with OS network denial; Vite **4.5.14**
compiled 3,417 modules in 6.24 seconds initially and 8.53 seconds after the
config correction, with a chunk-size warning. This is a
probe bundle build, not the complete application build or a TypeScript check.
The final config imports no project proxy configuration and points env loading
at the probe directory, which has no `.env` files. The first probe config used
`envDir: false`, but Vite 4 treats that as the project root; that setting was
corrected after inspecting the installed loader. The initial build could read
the audited public root `.env`, but no proxy was configured and browser API
connections were denied by CSP. The corrected bundle was rebuilt and rechecked. It retains the project's browser polyfill and React plugin approach.

The server binds `127.0.0.1:8081` (matching the project's documented port), serves
only the compiled output, rejects directory listing, and sends CSP
`connect-src 'none'` with scripts restricted to the same origin. Open
`http://127.0.0.1:8081/humanifest-probes/global-mapping-ui.html` and follow the
observations above. The first run starts without a mapping; subsequent runs
restore the dedicated synthetic localStorage record. Stop the server afterward.

After build and browser checks, byte comparison against the previously
Git-blob-verified source archive confirmed **all 898 original files unchanged**.
Temporary receipts: `/tmp/humanifest-mdsync-native/ui-build.log` and
`ui-build-final.log` and `ui-source-integrity.json`. Fixtures are additional
research files only. The reusable server was exercised and its HTTP CSP headers
verified; the server and temporary browser tab were stopped after verification.

## Decision and limits

The [13 unchanged native tests and four workflow probes](2026-09-10-mdsync-native-workflow.md)
remain separate evidence. They show that included source indicator-type fields
survive under a mapped destination ID. The browser control now confirms that an
existing global category path works with synthetic services, but does not settle
whether indicator types should be reused unchanged, omitted from the import or
updated. Confirm desired semantics and AI/bot contribution eligibility with
maintainers before proposing a production change. No global import-default
change, new production patch, server import, deployed benefit or maintainer
acceptance is claimed.

Sources (accessed September 10, 2026):

- [Issue #1255](https://github.com/EyeSeeTea/metadata-synchronization/issues/1255)
- [Pinned original page](https://github.com/EyeSeeTea/metadata-synchronization/blob/78c8b8c22278dcbb7d2d5678eaafaa80b0fd0cf9/src/presentation/webapp/core/pages/instance-mapping/InstanceMappingPage.tsx)
- [Pinned original picker](https://github.com/EyeSeeTea/metadata-synchronization/blob/78c8b8c22278dcbb7d2d5678eaafaa80b0fd0cf9/src/presentation/react/core/components/mapping-dialog/MappingDialog.tsx)
- [Pinned original apply use case](https://github.com/EyeSeeTea/metadata-synchronization/blob/78c8b8c22278dcbb7d2d5678eaafaa80b0fd0cf9/src/domain/mapping/usecases/ApplyMappingUseCase.ts)
