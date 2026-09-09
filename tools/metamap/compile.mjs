// Control-plane compiler only. No network, source execution, GitHub or state writes.
import fs from 'node:fs';
import { compileMetamap, compileProjection, ConstraintRegistry, RelationRegistry } from '@roryscot/metamap';
import routing from '@roryscot/metamap/relation-packs/routing.json' with { type: 'json' };

const manifest = JSON.parse(fs.readFileSync(new URL('./node_modules/@roryscot/metamap/package.json', import.meta.url), 'utf8'));
if (manifest.version !== '0.5.0') throw new Error('Humanifest requires Metamap v0.5.0');

export function compile(input) {
  const registry = new RelationRegistry();
  registry.registerPack(routing);
  registry.registerPack(input.pack);
  const constraints = new ConstraintRegistry();
  constraints.register('hf:exact-authority', (constraint, context) => {
    const { document } = context;
    const entities = new Map(document.entities.map(e => [e.id, e]));
    const links = (id, relation) => document.mappings.filter(m => context.activeMappings.has(m.id)
      && m.relation === relation && m.sources.includes(id)).flatMap(m => m.targets);
    const current = id => links(id, 'hf:current_record');
    const issues = [];
    const reject = (id, message) => issues.push({ severity: 'error', code: 'HUMANIFEST_AUTHORITY_MISMATCH', subjectId: id, message });
    for (const e of document.entities) {
      if (['hf:project', 'hf:opportunity'].includes(e.kind)) {
        const targets = current(e.id);
        const target = entities.get(targets[0]);
        const authority = context.graph.resolveAuthority(e.id, 'current-record');
        if (targets.length !== 1 || target?.kind !== 'hf:record'
          || target.attributes.path !== e.attributes.path || target.attributes.digest !== e.attributes.digest
          || authority.status !== 'resolved' || authority.canonical?.source !== targets[0]) {
          reject(e.id, 'Record must resolve to its exact current file authority');
        }
        for (const rel of ['hf:source', 'hf:evidence']) {
          for (const child of links(e.id, rel)) {
            if (JSON.stringify(current(child)) !== JSON.stringify(targets)) reject(child, 'Provenance belongs to a different record');
          }
        }
      }
      if (e.kind === 'hf:opportunity') {
        const projects = links(e.id, 'hf:project');
        if (projects.length !== 1 || entities.get(projects[0])?.attributes.recordId !== e.attributes.projectId) {
          reject(e.id, 'Project must match the authoritative opportunity record');
        }
        const routes = links(e.id, 'hf:handoff_route').map(id => entities.get(id)?.attributes.target).sort();
        if (JSON.stringify(routes) !== JSON.stringify([...constraint.parameters.handoffTargets].sort())) {
          reject(e.id, 'Every handoff route must resolve from the current native catalog');
        }
        const gates = links(e.id, 'hf:gate');
        const names = gates.map(id => entities.get(id)?.label).sort();
        if (JSON.stringify(names) !== JSON.stringify([...constraint.parameters.gates].sort())
          || JSON.stringify([...gates].sort()) !== JSON.stringify(links(e.id, 'hf:prerequisite').sort())) {
          reject(e.id, 'All native hard gates must be linked as prerequisites exactly once');
        }
        for (const gate of gates) {
          if (JSON.stringify(current(gate)) !== JSON.stringify(current(e.id))) reject(gate, 'Gate detached from current opportunity');
          const g = entities.get(gate);
          if (g?.label === 'maintainer_interest_confirmed') {
            const confirmations = links(gate, 'hf:confirmation');
            const confirmation = entities.get(confirmations[0]);
            if (confirmations.length !== 1 || confirmation?.attributes.confirmed !== g.attributes.passed
              || (g.attributes.passed && links(confirmation.id, 'hf:source').length === 0)) {
              reject(gate, 'Passing maintainer confirmation requires a cited confirmation record');
            }
          }
        }
        const outputs = links(e.id, 'hf:output');
        if (outputs.length !== 2 || JSON.stringify(outputs.map(id => entities.get(id)?.kind).sort()) !== JSON.stringify(['hf:handoff', 'hf:report'])) {
          reject(e.id, 'Exactly one report and one generated handoff must remain attached');
        }
        for (const out of outputs) {
          for (const rel of ['hf:current_record', 'hf:project', 'hf:guidance', 'hf:policy', 'hf:actor']) {
            if (JSON.stringify(links(out, rel)) !== JSON.stringify(links(e.id, rel))) reject(out, `Output detached through ${rel}`);
          }
        }
      }
      if (['hf:evidence', 'hf:gate', 'hf:confirmation'].includes(e.kind)) {
        for (const source of links(e.id, 'hf:source')) {
          if (JSON.stringify(current(source)) !== JSON.stringify(current(e.id))) reject(e.id, 'Citation belongs to a different record');
        }
      }
    }
    return issues;
  });
  const result = compileMetamap(input.graph, input.policy, {
    relationRegistry: registry, constraintRegistry: constraints,
    evaluatedAt: '2026-09-09T00:00:00.000Z',
  });
  if (result.status !== 'viable') return result;
  const linked = compileProjection(input.graph, result.generation, input.spec, { relationRegistry: registry });
  return linked.status === 'projected' ? { status: 'projected', generation: result.generation, projection: linked.projection } : linked;
}

const result = compile(JSON.parse(fs.readFileSync(0, 'utf8')));
process.stdout.write(JSON.stringify(result));
if (result.status !== 'projected') process.exitCode = 1;
