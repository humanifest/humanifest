#!/usr/bin/env node
/* Probe the original MappingMapper, not a replacement implementation.
 * Usage: node <fixture> <screen-root> <typescript-module>
 * Requires previously inspected, checksum-verified files; makes no downloads.
 * API/model adapters expose published 2.40 schemas only. Expression parsing,
 * category-combo conversion and all unexpected module imports fail closed.
 * This is not the app, original test suite, or a DHIS2 server integration test.
 */
'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const crypto = require('node:crypto');
const [root, typescriptPath] = process.argv.slice(2);
assert(root && typescriptPath, 'Supply screen root and TypeScript module path');
const ts = require(path.resolve(typescriptPath));
const hashes = {
    'source/src/domain/mapping/helpers/MappingMapper.ts': '70b28a84d7d3dae804d08f5f8f7c6aeb7e393d3c1dab183d56fb4e5e01faf65f',
    'source/src/domain/metadata/utils.ts': '45fb8c92b3cf341c1d9937ecc85316b4387f1d8c8dd800a19805fc0419f6ae55',
    'packages/d2api/package/2.40/schemas.js': 'e3c46ca3eab2a2544f6b62987e0824ebd9923ca626bf117f31051642dda4dfdb',
    'packages/lodash/package/lodash.js': '5009c4c4d2bdbeb10b1c89bac5657beee324a0fb5e3de36ce2aefbac5bb5666f',
};
function verify() {
    for (const [file, hash] of Object.entries(hashes)) {
        assert.equal(crypto.createHash('sha256').update(fs.readFileSync(path.join(root, file))).digest('hex'), hash, file);
    }
}
verify();
const unexpected = name => () => { throw new Error(`Unexercised boundary invoked: ${name}`); };
function load(file, modules = {}) {
    const source = fs.readFileSync(path.join(root, file), 'utf8');
    const code = file.endsWith('.ts') ? ts.transpileModule(source, {
        compilerOptions: { target: ts.ScriptTarget.ES2020, module: ts.ModuleKind.CommonJS, esModuleInterop: true },
        fileName: file,
    }).outputText : source;
    const exports = {};
    const context = vm.createContext({
        exports, module: { exports },
        require: name => {
            assert(Object.hasOwn(modules, name), `Unexpected module: ${name}`);
            return modules[name];
        },
    });
    new vm.Script(code, { filename: file }).runInContext(context, { timeout: 5000 });
    return context.module.exports;
}
const lodash = load('packages/lodash/package/lodash.js');
assert.equal(lodash.VERSION, '4.18.0');
const { models: schemas } = load('packages/d2api/package/2.40/schemas.js');
assert.equal(schemas.indicators.properties.find(p => p.fieldName === 'indicatorType').propertyType, 'REFERENCE');
assert.equal(schemas.indicatorTypes.plural, 'indicatorTypes');
// Only schemas are exposed: constructing this adapter cannot access a server.
class SchemaOnlyApi {
    constructor() {
        this.models = Object.fromEntries(Object.entries(schemas).map(([key, schema]) => [key, { schema, modelName: key }]));
    }
}
const apiModule = { D2Api: SchemaOnlyApi, getApiModel: (api, key) => api.models[key] };
const utils = load('source/src/domain/metadata/utils.ts', {
    lodash, 'd2/uid': { isValidUid: unexpected('UID validation') }, '../../types/d2-api': apiModule,
});
const modelAdapter = {
    modelFactory: key => {
        const schema = schemas[key];
        assert(schema, `No published schema for ${key}`);
        return { getCollectionName: () => schema.collectionName };
    },
};
const { MappingMapper } = load('source/src/domain/mapping/helpers/MappingMapper.ts', {
    lodash,
    '../../../models/dhis/factory': modelAdapter,
    '../../../types/d2-api': apiModule,
    '../../../utils/expressionParser': { ExpressionParser: { parse: unexpected('expression parse'), build: unexpected('expression build') } },
    '../../../utils/synchronization': { mapCategoryOptionCombo: unexpected('category-combo conversion') },
    '../../metadata/utils': utils,
});
const normalize = value => JSON.parse(JSON.stringify(value));
const original = { indicators: [{ id: 'IndicSource', name: 'Synthetic indicator', indicatorType: { id: 'TypeSource1' } }] };
const mapping = (mappedId = 'TypeTarget1', global = true) => ({ indicatorTypes: { TypeSource1: { mappedId, global } } });
const results = [];
function check(name, payload, map, expected) {
    const before = JSON.stringify(payload);
    const actual = normalize(new MappingMapper(map, [], []).applyMapping(payload));
    assert.deepEqual(actual, expected, name);
    assert.equal(JSON.stringify(payload), before, 'Input was mutated');
    results.push({ name, actual });
}
check('no mapping preserves source reference', original, {}, original);
check('supplied mapping rewrites indicator-type reference', original, mapping(), {
    indicators: [{ ...original.indicators[0], indicatorType: { id: 'TypeTarget1' } }],
});
check('disabled mapping preserves source reference', original, mapping('DISABLED'), original);
check('unrelated mapping leaves indicator type unchanged', original, { categoryOptions: { OtherSource: { mappedId: 'OtherTarget' } } }, original);
check('lookup does not require the global flag', original, mapping('TypeTarget1', false), {
    indicators: [{ ...original.indicators[0], indicatorType: { id: 'TypeTarget1' } }],
});
const withType = { ...original, indicatorTypes: [{ id: 'TypeSource1', name: 'Source factor', factor: 100, number: false }] };
check('included type object also gets destination ID and retains source fields', withType, mapping(), {
    indicators: [{ ...original.indicators[0], indicatorType: { id: 'TypeTarget1' } }],
    indicatorTypes: [{ id: 'TypeTarget1', name: 'Source factor', factor: 100, number: false }],
});
check('existing category-option reference mapping remains active', {
    categories: [{ id: 'CategoryOne', categoryOptions: [{ id: 'OptionSrc01' }] }],
}, { categoryOptions: { OptionSrc01: { mappedId: 'OptionDst01' } } }, {
    categories: [{ id: 'CategoryOne', categoryOptions: [{ id: 'OptionDst01' }] }],
});
verify();
console.log(JSON.stringify({
    revision: '78c8b8c22278dcbb7d2d5678eaafaa80b0fd0cf9',
    node: process.version, typescript: ts.version, lodash: lodash.VERSION,
    d2Api: '1.21.0 / 2.40 static schemas', cases: results.length,
    boundary: 'Original full mapper and metadata helpers, schema-only API/model adapters; no expressions, UI, persistence or server imports.',
    sourceHashes: hashes, results,
}, null, 2));
