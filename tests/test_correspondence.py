"""Mutation checks at the actual Metamap compiler and CLI consumer boundaries."""
from contextlib import redirect_stdout, redirect_stderr
from copy import deepcopy
from io import StringIO
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from humanifest.cli import main
from humanifest.correspondence import CONTROL_FILES, export_shard, identity, load_projection
from scripts.compile_correspondence import compile_input, compile_portfolio
from tests.test_models import opportunity


class CorrespondenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        source = Path(__file__).resolve().parents[1]
        for name in CONTROL_FILES:
            target = self.root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source / name, target)
        self.write('metamap/exclusions.json', {'exclusions': []})
        self.record = opportunity()
        self.write('portfolio/opportunities/sample.json', self.record)
        self.write('portfolio/projects/sample.json', {
            'id': 'sample-project', 'name': 'Sample', 'repository': 'https://example.test/repo',
            'homepage': 'https://example.test', 'license': 'MIT', 'humanitarian_domain': 'Health',
            'maintenance': {}, 'contribution': {}, 'impact_evidence': [], 'sources': self.record['sources']})
        self.shard = export_shard(self.root)

    def write(self, path, value):
        p = self.root / path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(value))

    def remove_links(self, shard, predicate):
        shard['graph']['mappings'] = [m for m in shard['graph']['mappings'] if not predicate(m)]

    def test_valid_portfolio_compiles_and_consumes_immutable_projection(self):
        artifact = compile_portfolio(self.root)
        self.assertEqual(artifact['compiler'], '@roryscot/metamap@0.5.0')
        guidance = load_projection(self.root).guidance
        self.assertIn('maintainer inquiry', guidance['sample'])
        with self.assertRaises(TypeError):
            guidance['sample'] = 'Implement now'
        before = (self.root / 'portfolio/opportunities/sample.json').read_bytes()
        for args in [('report', '--root', str(self.root)),
                     ('handoff', str(self.root / 'portfolio/opportunities/sample.json'), '--target', 'codex')]:
            out, err = StringIO(), StringIO()
            with redirect_stdout(out), redirect_stderr(err):
                status = main(list(args))
            self.assertEqual((status, err.getvalue()), (0, ''))
            self.assertIn(guidance['sample'], out.getvalue())
        self.assertEqual((self.root / 'portfolio/opportunities/sample.json').read_bytes(), before)

    def test_new_opportunity_missing_project_or_source_fails(self):
        for field in ['project_id', 'sources']:
            record = deepcopy(self.record)
            record['id'] = 'new-opportunity'
            record[field] = 'missing-project' if field == 'project_id' else []
            self.write('portfolio/opportunities/new.json', record)
            with self.assertRaises(ValueError):
                export_shard(self.root)
        # The graph compiler also governs newly discovered entities without a
        # manually appended list of mapping IDs or per-record constraints.
        shard = deepcopy(self.shard)
        entity = next(deepcopy(e) for e in shard['graph']['entities'] if e['kind'] == 'hf:opportunity')
        entity['id'] = identity('hf:opportunity', 'unlinked-new')
        shard['graph']['entities'].append(entity)
        with self.assertRaises(ValueError):
            compile_input(shard)

    def test_passing_confirmation_without_cited_evidence_fails(self):
        record = deepcopy(self.record)
        del record['gates']['maintainer_interest_confirmed']['source_ids']
        self.write('portfolio/opportunities/sample.json', record)
        with self.assertRaisesRegex(ValueError, 'must cite confirmation evidence'):
            export_shard(self.root)
        shard = deepcopy(self.shard)
        confirmations = {e['id'] for e in shard['graph']['entities'] if e['kind'] == 'hf:confirmation'}
        self.remove_links(shard, lambda m: m['relation'] == 'hf:source' and m['sources'][0] in confirmations)
        with self.assertRaises(ValueError):
            compile_input(shard)

    def test_handoff_detached_from_current_record_fails(self):
        shard = deepcopy(self.shard)
        handoff = next(e['id'] for e in shard['graph']['entities'] if e['kind'] == 'hf:handoff')
        self.remove_links(shard, lambda m: m['relation'] == 'hf:current_record' and handoff in m['sources'])
        with self.assertRaises(ValueError):
            compile_input(shard)

    def test_wrong_existing_authority_and_cross_record_citation_fail(self):
        for relation, kind in [("hf:current_record", "hf:handoff"), ("hf:source", "hf:gate")]:
            shard = deepcopy(self.shard)
            subject = next(e['id'] for e in shard['graph']['entities'] if e['kind'] == kind
                           and (kind != 'hf:gate' or e['attributes']['cited']))
            project = next(e['id'] for e in shard['graph']['entities'] if e['kind'] == 'hf:project')
            other = next(m['targets'][0] for m in shard['graph']['mappings']
                         if m['relation'] == relation and project in m['sources'])
            link = next(m for m in shard['graph']['mappings'] if m['relation'] == relation and subject in m['sources'])
            link['targets'] = [other]
            with self.subTest(relation=relation), self.assertRaises(ValueError):
                compile_input(shard)

    def test_missing_gate_policy_or_actor_fails(self):
        for relation in ['hf:gate', 'hf:prerequisite', 'routing:authorized_by', 'hf:actor', 'hf:handoff_route']:
            shard = deepcopy(self.shard)
            link = next(m for m in shard['graph']['mappings'] if m['relation'] == relation)
            shard['graph']['mappings'].remove(link)
            with self.subTest(relation=relation), self.assertRaises(ValueError):
                compile_input(shard)

    def test_empty_and_overlapping_selectors_fail(self):
        for selector in [{'relations': ['hf:absent']}, self.shard['policy']['mappings'][0]['select']]:
            shard = deepcopy(self.shard)
            declaration = deepcopy(shard['policy']['mappings'][0])
            declaration['select'] = selector
            shard['policy']['mappings'].append(declaration)
            with self.assertRaises(ValueError):
                compile_input(shard)

    def test_stale_projection_and_detached_cli_handoff_fail(self):
        compile_portfolio(self.root)
        self.record['title'] = 'Changed record'
        self.write('portfolio/opportunities/sample.json', self.record)
        with self.assertRaisesRegex(ValueError, 'stale Metamap'):
            load_projection(self.root)
        out, err = StringIO(), StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            status = main(['report', '--root', str(self.root)])
        self.assertEqual((status, out.getvalue()), (1, ''))
        compile_portfolio(self.root)
        self.write('detached.json', self.record)
        with redirect_stdout(StringIO()), redirect_stderr(err):
            status = main(['handoff', str(self.root / 'detached.json'), '--root', str(self.root), '--target', 'codex'])
        self.assertEqual(status, 1)
        self.assertIn('exact current portfolio record', err.getvalue())

    def test_projection_tampering_fails(self):
        artifact = compile_portfolio(self.root)
        artifact['projection']['entries'][0]['subject']['label'] = 'tampered'
        self.write('metamap/generated/portfolio.json', artifact)
        with self.assertRaisesRegex(ValueError, 'checksum'):
            load_projection(self.root)

    def test_exclusions_require_reason_owner_current_digest_and_exact_relation(self):
        path = self.root / 'handoffs/authored.md'
        path.parent.mkdir()
        path.write_text('Authored prompt, intentionally outside generated guidance.')
        import hashlib
        exclusion = {'path': 'handoffs/authored.md', 'digest': 'sha256:' + hashlib.sha256(path.read_bytes()).hexdigest(),
                     'relations': ['hf:current_record'], 'reason': 'Authored prompt', 'owner': 'Test repository owner'}
        for change in [{'reason': ''}, {'owner': ''}, {'digest': 'old'}, {'relations': []}]:
            self.write('metamap/exclusions.json', {'exclusions': [{**exclusion, **change}]})
            with self.assertRaisesRegex(ValueError, 'stale or invalid'):
                export_shard(self.root)
        self.write('metamap/exclusions.json', {'exclusions': [exclusion]})
        shard = export_shard(self.root)
        compile_input(shard)
        excluded = next(e['id'] for e in shard['graph']['entities'] if e['kind'] == 'hf:authored-handoff')
        mapping = deepcopy(next(m for m in shard['graph']['mappings'] if m['relation'] == 'hf:current_record'))
        mapping.update(id=identity('mapping', 'excluded-but-mapped'), sources=[excluded])
        shard['graph']['mappings'].append(mapping)
        with self.assertRaises(ValueError):
            compile_input(shard)
        path.unlink()
        with self.assertRaisesRegex(ValueError, 'stale projection exclusion'):
            export_shard(self.root)
