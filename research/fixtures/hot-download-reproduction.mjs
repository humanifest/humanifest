// Run against the separately downloaded, inspected upstream file; no dependencies.
// This probes the original handler with mock browser/network objects, not React UI.
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFileSync } from 'node:fs';
import vm from 'node:vm';

const path = process.argv[2];
assert.ok(path, 'Pass the pinned downloadOsmData.js path');
const source = readFileSync(path, 'utf8');
assert.equal(
  createHash('sha256').update(source).digest('hex'),
  'f8ba9d083a30ad719f9f8dae10500088200edae655f87ba2826c99a1f1732038',
  'Source differs from tasking-manager 2b917a14ea7b0b76935c4e2d6985ab25764cd1c9',
);
const start = '  const downloadS3File = ';
const end = ';\n  useEffect(';
assert.equal(source.split(start).length, 2);
const remainder = source.split(start)[1];
const endIndex = remainder.indexOf(end);
assert.ok(endIndex > 0);
const handler = remainder.slice(0, endIndex);

async function probe({ status = 200, popupBlocked = false, networkError = false }) {
  const events = [];
  const states = [];
  const errors = [];
  let popup = false;
  const context = {
    EXPORT_TOOL_S3_URL: 'https://example.invalid',
    datasetConfig: { dataset_folder: 'TM', dataset_prefix: 'hotosm_project_1' },
    project: { projectId: 1 },
    setIsDownloadingState: (state) => states.push(state),
    setShowPopup: (value) => { popup = value; },
    console: { error: (...args) => errors.push(args.join(' ')) },
    fetch: async (_url, options) => {
      assert.equal(options.method, 'HEAD');
      events.push('HEAD');
      if (networkError) throw new Error('simulated network failure');
      return {
        status,
        get ok() {
          events.push('check-status');
          return status >= 200 && status < 300;
        },
      };
    },
    window: {
      open: () => {
        events.push('open');
        return popupBlocked ? null : { blur: () => events.push('blur') };
      },
      focus: () => events.push('focus'),
    },
  };
  // Only the hash-checked, inspected handler is evaluated. No target imports,
  // setup hooks, real browser, credentials or real network are supplied.
  const download = vm.runInNewContext(`(${handler})`, context, { timeout: 1000 });
  await download('buildings', 'GeoJSON', 'polygons');
  assert.equal(states[0].isDownloading, true);
  assert.equal(states.at(-1).isDownloading, false);
  return { events, popup, errors };
}

const success = await probe({});
assert.equal(success.popup, false);
assert.deepEqual(success.errors, []);

const absent = await probe({ status: 404 });
assert.equal(absent.popup, true);
assert.ok(absent.events.indexOf('open') < absent.events.indexOf('check-status'));

const blocked = await probe({ popupBlocked: true });
assert.equal(blocked.popup, true);
assert.equal(blocked.events.includes('check-status'), false);
assert.match(blocked.errors.join(' '), /blur/);

const unavailableNetwork = await probe({ networkError: true });
assert.equal(unavailableNetwork.popup, true);
assert.equal(unavailableNetwork.events.includes('open'), false);

console.log(JSON.stringify({
  sourceRevision: '2b917a14ea7b0b76935c4e2d6985ab25764cd1c9',
  runtime: process.version,
  scope: 'Original handler with mocked HEAD and window; no UI or deployment reproduction',
  success, absent, blocked, unavailableNetwork,
}, null, 2));
