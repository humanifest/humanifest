/* Read-only reproduction against CHT 35b2bb6d. No database or target edits.
 * Usage: TZ=UTC node this-file.cjs /absolute/path/to/audited/cht-baseline
 * Requires the previously inspected/installed dependencies of that checkout.
 * VM contexts isolate dependency wiring; they are not a security sandbox.
 */
const assert = require('node:assert/strict');
const crypto = require('node:crypto');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const { createRequire } = require('node:module');
const root = path.resolve(process.argv[2] || '');
assert.equal(process.env.TZ, 'UTC', 'Use explicit TZ=UTC for reproducible dates');
const hashes = {
  'api/src/services/export/dhis.js': '3499a7304215ecd75da3fa98320b661e1e6513fc461c0ebd18115c59ebfff70b',
  'shared-libs/calendar-interval/src/index.js': 'aa6f5b7735e82cca48b49ef83d7433283694d063057ae9777e07302b3a8d56cb',
  'shared-libs/rules-engine/src/provider-wireup.js': '502eb01a652780d962bb87e990e243b2f6fc8fb37ce0359e346686fc5b38df5c',
  'admin/src/js/controllers/export-dhis.js': '2ed27e30ff2a7d9c9de1e0300819b98bd8af1a686e707d3b1928945f77808aca',
  'package-lock.json': 'c02c522ffbd1f4d0b18259a9ee97b1d30363cf60bdba333060c600509b2d8322',
};
const source = {};
for (const [name, expected] of Object.entries(hashes)) {
  const bytes = fs.readFileSync(path.join(root, name));
  assert.equal(crypto.createHash('sha256').update(bytes).digest('hex'), expected, name);
  source[name] = bytes.toString('utf8');
}
const requireTarget = createRequire(path.join(root, 'package.json'));
const moment = requireTarget('moment');
const lodash = requireTarget('lodash');
const bikram = requireTarget('bikram-sambat');
function evaluate(name, dependencies, globals = {}) {
  const module = { exports: {} };
  vm.runInNewContext(source[name], {
    module, ...globals,
    require(id) {
      assert(Object.hasOwn(dependencies, id), `Unexpected dependency: ${id}`);
      return dependencies[id];
    },
  }, { filename: name, timeout: 1000 });
  return module.exports;
}
const calendar = evaluate('shared-libs/calendar-interval/src/index.js', {
  moment, 'bikram-sambat': bikram,
});
const writerSource = source['shared-libs/rules-engine/src/provider-wireup.js']
  .match(/const getTargetDocTag = \(filterInterval\) => \{[\s\S]*?\n\};/);
assert(writerSource, 'Expected writer helper boundary');
function writerTag(interval, bs) {
  return vm.runInNewContext(writerSource[0] + '\ngetTargetDocTag(interval);', {
    interval, moment, rulesStateStore: { getUseBikramSambatMonths: () => bs },
    require(id) { assert.equal(id, 'bikram-sambat'); return bikram; },
    console: { warn() { throw Error('Unexpected calendar fallback'); } },
  }, { timeout: 1000 });
}
async function exportCase(date, startDay, bs, expectedWriter, expectedReader) {
  const from = moment.utc(date).valueOf();
  const interval = calendar.getInterval(startDay, from, bs);
  const tag = writerTag(interval, bs);
  assert.equal(tag, expectedWriter);
  const readerTag = bs ? (() => {
    const d = bikram.toBik(date);
    return `${d.year}-${String(d.month).padStart(2, '0')}`;
  })() : date.slice(0, 7);
  assert.equal(readerTag, expectedReader);
  const contact = { _id: 'owner', dhis: { dataSet: 'ds', orgUnit: 'ou' } };
  const targetDoc = (month, total) => ({ _id: `target~${month}~owner`, owner: 'owner',
    targets: [{ id: 'count', value: { total } }] });
  const docs = [targetDoc(readerTag, 11)];
  if (tag !== readerTag) docs.push(targetDoc(tag, 29));
  let queriedRange;
  const settings = { dhis_data_sets: [{ id: 'ds' }],
    uhc: { month_start_date: startDay, visit_count: { month_start_date: startDay, use_bikram_sambat_months: bs } },
    tasks: { targets: { items: [{ id: 'count', dhis: { dataElement: 'de', dataSet: 'ds' } }] } } };
  const service = evaluate('api/src/services/export/dhis.js', {
    lodash, moment, 'bikram-sambat': bikram,
    '../../config': { get: () => settings },
    '@medic/logger': { error(message) { throw Error(message); } },
    '../../db': { medic: {
      async allDocs(options) {
        if (options.keys) { assert.equal(options.keys.join(','), 'owner'); return { rows: [{ doc: contact }] }; }
        queriedRange = options;
        return { rows: docs.filter(d => d._id >= options.startkey && d._id <= options.endkey).map(doc => ({ doc })) };
      },
      async query(view) {
        assert.equal(view, 'medic-admin/contacts_by_dhis_orgunit');
        return { rows: [{ doc: contact }] };
      },
    } },
  });
  const result = await service({ dataSet: 'ds', date: { from } });
  assert.equal(queriedRange.startkey, `target~${readerTag}~`);
  assert.equal(result.dataValues.length, 1);
  assert.equal(result.dataValues[0].value, 11);
  assert.equal(result.period, date.slice(0, 7).replace('-', ''));
  return { date, startDay, calendar: bs ? 'BS' : 'Gregorian',
    intervalStart: moment.utc(interval.start).format('YYYY-MM-DD'),
    intervalEnd: moment.utc(interval.end).format('YYYY-MM-DD'),
    writerTag: tag, exporterTag: readerTag, exportedValue: result.dataValues[0].value,
    containingIntervalValue: tag === readerTag ? 11 : 29, exportedPeriod: result.period };
}
async function picker(clock) {
  let controller;
  const oldNow = moment.now;
  const timestamp = moment.utc(clock).valueOf();
  moment.now = () => timestamp;
  try {
    evaluate('admin/src/js/controllers/export-dhis.js', { lodash, moment }, {
      angular: { module() { return { controller(name, fn) { assert.equal(name, 'ExportDhisCtrl'); controller = fn; } }; } },
    });
    const scope = {};
    controller(scope, () => ({ query: async () => ({ rows: [] }) }),
      () => { throw Error('Export must not be invoked'); }, async () => ({ dhis_data_sets: [{ id: 'ds' }] }));
    await Promise.resolve();
    return scope.periods[1];
  } finally { moment.now = oldNow; }
}
(async () => {
  const cases = [];
  for (const args of [
    ['2026-07-14', 15, false, '2026-07', '2026-07'],
    ['2026-07-15', 15, false, '2026-08', '2026-07'],
    ['2026-07-15', 1, false, '2026-07', '2026-07'],
    ['2026-12-31', 15, false, '2027-01', '2026-12'],
    ['2026-07-05', 15, true, '2083-04', '2083-03'],
    ['2026-07-30', 15, true, '2083-04', '2083-04'],
    ['2026-07-31', 15, true, '2083-05', '2083-04'],
    ['2026-07-31', 1, true, '2083-04', '2083-04'],
  ]) cases.push(await exportCase(...args));
  const early = await picker('2026-08-14');
  const late = await picker('2026-08-15');
  assert.equal(early.description, 'July, 2026');
  assert.equal(late.description, early.description);
  const earlyTag = writerTag(calendar.getInterval(15, Number(early.timestamp), false), false);
  const lateTag = writerTag(calendar.getInterval(15, Number(late.timestamp), false), false);
  assert.equal(earlyTag, '2026-07');
  assert.equal(lateTag, '2026-08');
  console.log(JSON.stringify({ cases, picker: { early, late, containingTags: [earlyTag, lateTag] },
    limitations: 'Synthetic DB responses; original exporter/controller and extracted writer helper. No real DB, DOM, deployment, or approved reporting semantics.' }, null, 2));
})().catch(error => { console.error(error); process.exitCode = 1; });
