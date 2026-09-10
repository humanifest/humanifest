// Run the unchanged admin suite at CHT 35b2bb6 with local-only Karma listeners.
// Prerequisites and scope are recorded in the accompanying runtime audit.
// This is a baseline runner, not a patch acceptance test or live UI reproduction.
const fs = require('node:fs');
const path = require('node:path');
const { createHash } = require('node:crypto');
const { createRequire } = require('node:module');

const root = process.env.HUMANIFEST_CHT_CHECKOUT;
if (!root || !path.isAbsolute(root) || !process.env.CHROME_BIN) {
  throw new Error('Set absolute HUMANIFEST_CHT_CHECKOUT and explicit CHROME_BIN.');
}
const expected = {
  'admin/tests/karma-unit.conf.js': '611135c056b2ee3755be24135bc162c0984b68a165e3d76470ade926a31947cd',
  'admin/src/js/controllers/edit-user.js': 'ce86fb030acf8490f7770a83afa844a09fedba0ea62acd7ed9efc4e5995dcf70',
  'admin/src/templates/edit_user.html': '0d2a713881ea81398a4e01eaa73a5498114825f2b4f6ca7cdb63ce8fcf5e7a25',
  'admin/src/js/services/modal.js': 'f1a55524cc42886eb3041f22c569150ced237bb4f0c7cf96fc48e5227b70022d',
  'admin/src/js/directives/modal.js': '61d6165055abb96feb5d21ed13ff1b61b14d19e10c81806332373bf0ad22524a',
  'admin/src/templates/modal.html': '206562c71ee95eea36b45e8836d953e58b88140e7918df0fa155f548075cd174',
  'admin/tests/unit/controllers/edit-user.spec.js': 'e0beb6345e6e291b79bf53ac3e41481c056182553d334b122aadd417bd018f71',
  'package-lock.json': 'c02c522ffbd1f4d0b18259a9ee97b1d30363cf60bdba333060c600509b2d8322',
  'admin/package-lock.json': 'b7f75a819b4f29d244543c43f54376ab7a157a047a289db9e16f56b071efd274',
};
for (const [file, hash] of Object.entries(expected)) {
  const actual = createHash('sha256').update(fs.readFileSync(path.join(root, file))).digest('hex');
  if (actual !== hash) throw new Error(`Baseline source mismatch: ${file}`);
}
process.chdir(root);
const targetRequire = createRequire(path.join(root, 'package.json'));
const karma = targetRequire('karma');

(async () => {
  const config = await karma.config.parseConfig(path.join(root, 'admin/tests/karma-unit.conf.js'), {
    browsers: ['HumanifestChrome'],
    singleRun: true,
    autoWatch: false,
    hostname: '127.0.0.1',
    listenAddress: '127.0.0.1',
    port: 19876,
    customLaunchers: {
      HumanifestChrome: {
        base: 'Chrome',
        flags: ['--headless', '--disable-gpu', '--remote-debugging-address=127.0.0.1',
          '--remote-debugging-port=0', '--disable-background-networking'],
      },
    },
  }, { promiseConfig: true, throwErrors: true });
  if (process.argv.includes('--reproduce')) {
    config.files.push({
      pattern: path.join(__dirname, 'cht-edit-user-load-reproduction.spec.js'),
      included: true, served: true, watched: false,
    });
    config.client.mocha = { ...config.client.mocha, grep: '^Humanifest edit-user load reproduction' };
  }
  if (process.argv.includes('--dom')) {
    config.files.push({
      pattern: path.join(__dirname, 'cht-edit-user-dom-reproduction.spec.js'),
      included: true, served: true, watched: false,
    });
    config.client.mocha = { ...config.client.mocha, grep: '^Humanifest edit-user DOM reproduction' };
  }
  const server = new karma.Server(config, code => { process.exitCode = code; });
  await server.start();
})().catch(error => {
  console.error(error);
  process.exitCode = 1;
});
