// Humanifest research harness. Original UI and mapping code; synthetic service boundaries.
import React from 'react';
import ReactDOM from 'react-dom';
import { MemoryRouter, Route } from 'react-router-dom';
import { LoadingProvider, SnackbarProvider } from '@eyeseetea/d2-ui-components';
import { AppContext } from '../src/presentation/react/core/contexts/AppContext';
import InstanceMappingPage from '../src/presentation/webapp/core/pages/instance-mapping/InstanceMappingPage';
import { Instance } from '../src/domain/instance/entities/Instance';
import { Either } from '../src/domain/common/entities/Either';
import { MappingD2ApiRepository } from '../src/data/mapping/MappingD2ApiRepository';
import { ApplyMappingUseCase } from '../src/domain/mapping/usecases/ApplyMappingUseCase';
import { GetMappingByOwnerUseCase } from '../src/domain/mapping/usecases/GetMappingByOwnerUseCase';
import { SaveMappingUseCase } from '../src/domain/mapping/usecases/SaveMappingUseCase';
import { D2Api } from '../src/types/d2-api';

const storageKey = 'humanifest-md-sync-synthetic-mapping';
const audit: any[] = [];
const log = (method: string, data: unknown) => {
    audit.push({ method, data });
    const output = document.getElementById('receipt');
    if (output) output.textContent = JSON.stringify({ saved: JSON.parse(localStorage.getItem(storageKey) || 'null'), calls: audit }, null, 2);
};
const origin = Instance.build({ id: 'LOCAL', type: 'local', name: 'Synthetic origin', url: 'http://origin.test', version: '2.40' });
const destination = Instance.build({ id: 'DESTINATION', type: 'dhis', name: 'Synthetic destination', url: 'http://destination.test', version: '2.40' });
const datasets: Record<string, any[]> = {
    LOCAL: [{ id: 'CatSource01', name: 'Synthetic source category', displayName: 'Synthetic source category', code: 'SOURCE', lastUpdated: '2026-09-10T00:00:00.000' }],
    DESTINATION: [
        { id: 'CatTarget01', name: 'Synthetic target category A', displayName: 'Synthetic target category A', code: 'TARGET_A', lastUpdated: '2026-09-10T00:00:00.000' },
        { id: 'CatTarget02', name: 'Synthetic target category B', displayName: 'Synthetic target category B', code: 'TARGET_B', lastUpdated: '2026-09-10T00:00:00.000' },
    ],
};
const rows = (params: any, source = origin) => {
    if (params.type !== 'categories') throw new Error('Unimplemented synthetic collection: ' + params.type);
    return datasets[source.id].filter(row => !params.showOnlySelected || params.selectedIds?.includes(row.id));
};
const storage = {
    saveObjectInCollection: async (namespace: string, value: any) => { localStorage.setItem(storageKey, JSON.stringify(value)); log('storage.save', { namespace, value }); },
    listObjectsInCollection: async () => { const raw = localStorage.getItem(storageKey); return raw ? [JSON.parse(raw)] : []; },
    getObjectInCollection: async () => JSON.parse(localStorage.getItem(storageKey) || 'null'),
};
const mappingRepository = new MappingD2ApiRepository({ getStorageClientPromise: async () => storage } as any);
const factory: any = {
    mappingRepository: () => mappingRepository,
    metadataRepository: (source: Instance) => ({
        getMetadataByIds: async (ids: string[]) => { log('metadata.getByIds', { source: source.id, ids }); return { categories: datasets[source.id].filter(row => ids.includes(row.id)) }; },
        getDefaultIds: async () => [],
        lookupSimilar: async () => { throw new Error('Unexpected synthetic lookupSimilar'); },
    }),
};
const apply = new ApplyMappingUseCase(factory, origin);
const get = new GetMappingByOwnerUseCase(factory, origin);
const save = new SaveMappingUseCase(factory, origin);
const api = new D2Api({ baseUrl: 'http://origin.test' });
const compositionRoot: any = {
    localInstance: origin,
    instances: {
        getById: async (id: string) => { if (id !== destination.id) throw new Error('Unexpected instance'); return Either.success(destination); },
        getApi: () => api,
        validate: async () => Either.success(undefined),
    },
    metadata: {
        listAll: async (params: any, source?: Instance) => rows(params, source),
        list: async (params: any, source?: Instance) => { const objects = rows(params, source); return { objects, pager: { page: 1, pageSize: 25, total: objects.length } }; },
    },
    responsibles: { list: async () => [] },
    mapping: {
        get: async (owner: any) => { const result = await get.execute(owner); log('mapping.get', result?.toObject() ?? null); return result; },
        save: async (mapping: any) => save.execute(mapping),
        apply: async (...args: any[]) => { log('mapping.apply', args[3]); return apply.execute(...args as Parameters<typeof apply.execute>); },
    },
};
ReactDOM.render(
    <AppContext.Provider value={{ api, d2: {}, compositionRoot, newCompositionRoot: {} as any }}>
        <MemoryRouter initialEntries={['/instances/DESTINATION/global']}>
            <LoadingProvider><SnackbarProvider>
                <Route path="/instances/:id/:section"><InstanceMappingPage showHeader={false} /></Route>
            </SnackbarProvider></LoadingProvider>
        </MemoryRouter>
    </AppContext.Provider>, document.getElementById('root')
);
log('harness.ready', { source: '78c8b8c22278dcbb7d2d5678eaafaa80b0fd0cf9', synthetic: true });
