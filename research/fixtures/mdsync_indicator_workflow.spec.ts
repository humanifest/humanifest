// Copy into humanifest-probes/ in the pinned external checkout before running Vitest.
// Original model/mapper/builder/repository; synthetic metadata and memory storage boundary.
// No actual DHIS2 import or browser interaction is tested.
import { describe, expect, it } from 'vitest';
import { anything, instance, mock, when } from 'ts-mockito';
import { modelFactory } from '../src/models/dhis/factory';
import { MappingMapper } from '../src/domain/mapping/helpers/MappingMapper';
import { DataSourceMapping } from '../src/domain/mapping/entities/DataSourceMapping';
import { MappingD2ApiRepository } from '../src/data/mapping/MappingD2ApiRepository';
import { MetadataPayloadBuilder } from '../src/domain/metadata/builders/MetadataPayloadBuilder';
import { DynamicRepositoryFactory } from '../src/domain/common/factories/DynamicRepositoryFactory';
import { Instance } from '../src/domain/instance/entities/Instance';
import { MetadataRepository } from '../src/domain/metadata/repositories/MetadataRepository';
import { InstanceRepository } from '../src/domain/instance/repositories/InstanceRepository';
import { MetadataPackage } from '../src/domain/metadata/entities/MetadataEntities';
import { StorageClientFactory } from '../src/data/config/StorageClientFactory';

const origin = Instance.build({ type: 'local', name: 'Synthetic origin', url: 'http://origin.test', version: '2.40' });
const indicator = { id: 'IndicSource', name: 'Synthetic malaria indicator', shortName: 'Synthetic indicator', numerator: '1', denominator: '1', indicatorType: { id: 'TypeSource1' } };
const indicatorType = { id: 'TypeSource1', name: 'Synthetic percentage', factor: 100, number: false };
const mapping = { indicatorTypes: { TypeSource1: { mappedId: 'TypeTarget1', global: true } } };
const raw = { indicators: [indicator], indicatorTypes: [indicatorType] } as unknown as MetadataPackage;
const copy = <T>(value: T): T => JSON.parse(JSON.stringify(value));

function buildOriginalPayloadBuilder() {
    const metadataRepository = mock<MetadataRepository>();
    when(metadataRepository.getByFilterRules(anything())).thenResolve([]);
    when(metadataRepository.listAllMetadata(anything())).thenResolve([]);
    const selected = (ids: string[]) => Object.fromEntries(Object.entries(raw).map(([type, objects]) => [type, objects?.filter(object => ids.includes(object.id))]).filter(([, objects]) => (objects as any[])?.length));
    when(metadataRepository.getMetadataByIds(anything(), anything())).thenCall((ids: string[]) => Promise.resolve(copy(selected(ids))));
    when(metadataRepository.getMetadataByIds(anything())).thenCall((ids: string[]) => Promise.resolve(copy(selected(ids))));
    const instanceRepository = mock<InstanceRepository>();
    when(instanceRepository.getById(anything())).thenResolve(origin);
    const factory = mock<DynamicRepositoryFactory>();
    when(factory.metadataRepository(anything())).thenReturn(instance(metadataRepository));
    when(factory.instanceRepository(anything())).thenReturn(instance(instanceRepository));
    return new MetadataPayloadBuilder(instance(factory), origin);
}

describe('Humanifest original indicator-type workflow probes', () => {
    it('resolves the published indicator type with the original model factory', () => {
        expect(modelFactory('indicatorTypes').getCollectionName()).toBe('indicatorTypes');
        expect(modelFactory('indicatorType').getCollectionName()).toBe('indicatorTypes');
    });
    it('rewrites a reference through the original mapper, parser and API schemas', () => {
        const payload = copy(raw);
        const result = new MappingMapper(mapping, [], []).applyMapping(payload);
        expect(result.indicators?.[0].indicatorType.id).toBe('TypeTarget1');
        expect(result.indicators?.[0].numerator).toBe('1');
        expect(result.indicators?.[0].denominator).toBe('1');
        expect(result.indicatorTypes?.[0]).toEqual({ ...indicatorType, id: 'TypeTarget1' });
        expect(payload).toEqual(raw);
    });
    it('round-trips mapping through the original repository with a memory storage boundary', async () => {
        let saved: any;
        const storage = {
            saveObjectInCollection: async (_namespace: string, value: unknown) => { saved = copy(value); },
            listObjectsInCollection: async () => saved ? [{ id: saved.id, owner: saved.owner }] : [],
            getObjectInCollection: async () => copy(saved),
        };
        const storageFactory = mock<StorageClientFactory>();
        when(storageFactory.getStorageClientPromise()).thenResolve(storage as any);
        const repository = new MappingD2ApiRepository(instance(storageFactory));
        const owner = { type: 'instance' as const, id: 'DESTINATION' };
        const source = DataSourceMapping.build({ id: 'MappingOne1', owner, mappingDictionary: {} }).updateMappingDictionary(mapping);
        expect((await repository.save(source)).isSuccess()).toBe(true);
        const restored = await repository.getByOwner(owner);
        expect(restored?.mappingDictionary).toEqual(mapping);
        const result = new MappingMapper(restored!.mappingDictionary, [], []).applyMapping(copy(raw));
        expect(result.indicators?.[0].indicatorType.id).toBe('TypeTarget1');
    });
    it('includes the source indicator type through original default builder rules', async () => {
        const payload = await buildOriginalPayloadBuilder().build({ originInstance: 'LOCAL', metadataIds: ['IndicSource'], excludedIds: [] });
        expect(payload.indicators?.[0].indicatorType.id).toBe('TypeSource1');
        expect(payload.indicatorTypes).toEqual([indicatorType]);
        const result = new MappingMapper(mapping, [], []).applyMapping(payload);
        expect(result.indicators?.[0].indicatorType.id).toBe('TypeTarget1');
        expect(result.indicatorTypes).toEqual([{ ...indicatorType, id: 'TypeTarget1' }]);
    });
});
