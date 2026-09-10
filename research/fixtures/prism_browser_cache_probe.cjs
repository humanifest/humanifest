/** Execute the pinned original PRISM request wrapper in an isolated browser.
 * Usage: NODE_PATH=<bundled packages> node prism_browser_cache_probe.cjs SOURCE.ts
 * Requires Node 24 and existing Playwright; installs nothing. This probes the
 * request wrapper, not the full dashboard, using controlled loopback JSON data.
 */
const assert = require('node:assert/strict');
const crypto = require('node:crypto');
const fs = require('node:fs');
const http = require('node:http');
const { stripTypeScriptTypes } = require('node:module');
const { chromium } = require('playwright');
const SOURCE_HASH = '46f41fab3666449322c1c63146111ff3bae52bc53cba1afcf32a753fca69b54f';
const sourcePath = process.argv[2];
const original = fs.readFileSync(sourcePath, 'utf8');
const digest = text => crypto.createHash('sha256').update(text).digest('hex');
assert.equal(digest(original), SOURCE_HASH);
const imports = original.match(/^import .*;$/gm);
assert.deepEqual(imports, [
  "import { addNotification } from 'context/notificationStateSlice';",
  "import { Dispatch } from 'redux';",
  "import { HTTPError } from './error-utils';",
]);
// Remove only the three reviewed imports and erase TypeScript syntax. Error/UI
// dependencies are fail-fast sentinels: these success/cache cases must not use them.
const body = stripTypeScriptTypes(original.replace(/^import .*;$/gm, ''), { mode: 'strip' });
const moduleCode = `const addNotification = () => { throw new Error('Unexpected notification dependency'); };
class HTTPError { constructor() { throw new Error('Unexpected HTTPError dependency'); } }
${body}`;
let version = 1;
const requests = [];
const payload = v => JSON.stringify({ version: v, padding: 'x'.repeat(4096) });
const server = http.createServer((req, res) => {
  const pathname = new URL(req.url, 'http://localhost').pathname;
  if (pathname === '/') {
    res.writeHead(200, { 'Content-Type': 'text/html', 'Cache-Control': 'no-store' });
    res.end('<!doctype html><title>Humanifest cache probe</title><p>Controlled synthetic boundary data.</p>');
  } else if (pathname === '/wrapper.js') {
    res.writeHead(200, { 'Content-Type': 'text/javascript', 'Cache-Control': 'no-store' });
    res.end(moduleCode);
  } else if (['/boundary.json', '/native.json', '/immutable-v1.json', '/immutable-v2.json'].includes(pathname)) {
    const immutable = pathname.startsWith('/immutable-');
    const v = immutable ? Number(pathname.match(/v(\d)/)[1]) : version;
    const etag = `"version-${v}"`;
    const text = payload(v);
    const headers = { 'Content-Type': 'application/json', ETag: etag,
      'Cache-Control': immutable ? 'public, max-age=31536000, immutable' : 'public, max-age=2' };
    const notModified = req.headers['if-none-match'] === etag;
    const status = notModified ? 304 : 200;
    if (!notModified) headers['Content-Length'] = Buffer.byteLength(text);
    requests.push({ pathname, status, ifNoneMatch: req.headers['if-none-match'] ?? null,
      requestCacheControl: req.headers['cache-control'] ?? null,
      bodyBytes: notModified ? 0 : Buffer.byteLength(text), version: v });
    res.writeHead(status, headers);
    res.end(notModified ? undefined : text);
  } else { res.writeHead(404); res.end(); }
});
(async () => {
  let browser;
  const watchdog = setTimeout(() => { console.error('Probe timed out'); process.exit(2); }, 45000);
  try {
    await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
    const origin = `http://127.0.0.1:${server.address().port}`;
    browser = await chromium.launch({ executablePath: '/Applications/Google Chrome Canary.app/Contents/MacOS/Google Chrome Canary', headless: true });
    const context = await browser.newContext({ serviceWorkers: 'block' });
    const page = await context.newPage();
    await page.goto(origin);
    const reports = [];
    async function run(name, pathname, expectedVersion, expectedStatus, native = false) {
      const before = requests.length;
      const observation = await page.evaluate(async ({ pathname, native }) => {
        const { fetchWithTimeout } = await import('/wrapper.js');
        performance.clearResourceTimings();
        // Empty options mirror the current boundary loader. No fetch mocks or
        // request routing: the actual browser HTTP cache talks to the local server.
        const response = native ? await fetch(pathname) : await fetchWithTimeout(pathname, undefined, {});
        const data = await response.json();
        const entry = performance.getEntriesByName(new URL(pathname, location.href).href).at(-1);
        return { responseStatus: response.status, version: data.version,
          timing: entry ? { transferSize: entry.transferSize, encodedBodySize: entry.encodedBodySize,
            decodedBodySize: entry.decodedBodySize } : null };
      }, { pathname, native });
      const traffic = requests.slice(before);
      assert.equal(observation.version, expectedVersion, name);
      assert.equal(observation.responseStatus, 200, name);
      if (expectedStatus === null) assert.deepEqual(traffic, [], name);
      else { assert.equal(traffic.length, 1, name); assert.equal(traffic[0].status, expectedStatus, name); }
      reports.push({ name, pathname, observation, traffic });
    }
    await run('first request', '/boundary.json', 1, 200);
    await run('warm request', '/boundary.json', 1, null);
    await page.reload();
    await run('warm request after navigation', '/boundary.json', 1, null);
    await new Promise(resolve => setTimeout(resolve, 2300));
    await run('expired unchanged content', '/boundary.json', 1, 304);
    version = 2;
    await run('changed server content while cache remains fresh', '/boundary.json', 1, null);
    await new Promise(resolve => setTimeout(resolve, 2300));
    await run('changed content after expiry', '/boundary.json', 2, 200);
    await run('native fetch control first', '/native.json', 2, 200, true);
    await run('native fetch control warm', '/native.json', 2, null, true);
    await run('versioned URL initial', '/immutable-v1.json', 1, 200);
    await run('versioned URL warm', '/immutable-v1.json', 1, null);
    await run('different versioned URL discovers new content', '/immutable-v2.json', 2, 200);
    assert.equal(digest(fs.readFileSync(sourcePath, 'utf8')), SOURCE_HASH);
    console.log(JSON.stringify({ node: process.version, playwright: require('playwright/package.json').version,
      browser: browser.version(), sourceHash: SOURCE_HASH, synthetic: true, ttlSeconds: 2,
      casesPassed: reports.length, reports }, null, 2));
  } finally {
    if (browser) await browser.close();
    await new Promise(resolve => server.close(resolve));
    clearTimeout(watchdog);
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
