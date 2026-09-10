"""Exercise pinned OpenAQ sensor routes with synthetic rows at DB.fetch.

Imports the original router, queries and response models. Executes the original
DB.fetchPage method extracted without edits; substitutes its connection layer.
No original app startup, DB connection, SQL execution or operational data access.
"""
import argparse
import ast
from copy import deepcopy
import errno
import hashlib
import json
from pathlib import Path
import socket
import sys
import types

EXPECTED = {'openaq_api/__init__.py': 'e69de29bb2d1d6434b8b29ae775ad8c2e48c5391', 'openaq_api/models/responses.py': 'a8ef354c3a9bc20ca5d3fcbef0b95ec33d14e9fc', 'openaq_api/db.py': '767cc0c8e55abced25607018f02f22fc43925299', 'openaq_api/v3/models/__init__.py': 'e69de29bb2d1d6434b8b29ae775ad8c2e48c5391', 'openaq_api/v3/routers/__init__.py': 'e69de29bb2d1d6434b8b29ae775ad8c2e48c5391', 'openaq_api/v3/models/responses.py': '44736f6efd54c2da8005d28764f18042a5457344', 'openaq_api/v3/models/utils.py': '9c824efe2991175c4c0197d024dfc2b3986ddad4', 'openaq_api/v3/models/queries.py': '644e6be4d02a9b94c4ff474686c0d977748f5d63', 'openaq_api/v3/routers/sensors.py': '3fcb04486bd4b73adfa4fb3ca4adfb71b6539125'}


def verify_sources(root):
    for name, expected in EXPECTED.items():
        body = (root / name).read_bytes()
        actual = hashlib.sha1(b"blob " + str(len(body)).encode() + b"\0" + body).hexdigest()
        assert actual == expected, (name, actual)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', required=True, type=Path)
    parser.add_argument('--coverage-results', required=True, type=Path)
    parser.add_argument('--require-network-denial', action='store_true')
    args = parser.parse_args()
    verify_sources(args.source)
    if args.require_network_denial:
        with socket.socket() as control:
            try:
                control.bind(('127.0.0.1', 0))
            except OSError as error:
                assert error.errno in (errno.EACCES, errno.EPERM), error
            else:
                raise AssertionError('Network denial control unexpectedly succeeded')

    sys.path.insert(0, str(args.source.resolve()))
    from fastapi import FastAPI, Request
    from fastapi.exceptions import ResponseValidationError
    from fastapi.testclient import TestClient
    from openaq_api.models.responses import Meta, OpenAQResult

    # Keep the exact method body/defaults/annotations; do not import DB's settings,
    # cache decorators, authentication or network dependencies.
    db_path = args.source / 'openaq_api/db.py'
    db_class = next(n for n in ast.parse(db_path.read_text()).body
                    if isinstance(n, ast.ClassDef) and n.name == 'DB')
    method = next(n for n in db_class.body
                  if isinstance(n, ast.AsyncFunctionDef) and n.name == 'fetchPage')
    namespace = {'Meta': Meta, 'OpenAQResult': OpenAQResult, 'DEFAULT_CONNECTION_TIMEOUT': 6}
    exec(compile(ast.Module(body=[method], type_ignores=[]), str(db_path), 'exec'), namespace)

    class FixtureDB:
        def __init__(self, request: Request):
            self.request = request

        async def fetch(self, query, kwargs, timeout, config):
            state = self.request.app.state
            state.calls.append({'query': query, 'params': deepcopy(kwargs)})
            return deepcopy(state.rows)

        fetchPage = namespace['fetchPage']

    module = types.ModuleType('openaq_api.db')
    module.DB = FixtureDB
    assert 'openaq_api.db' not in sys.modules
    sys.modules['openaq_api.db'] = module
    from openaq_api.v3.routers.sensors import router

    receipt = json.loads(args.coverage_results.read_text())
    assert receipt['api_revision'] == '87c060c28f5b484e0e9953d247082f5e678935c9'
    assert receipt['database_revision'] == '0e49c258186372f4af6c5679a4e1ab47157f0158'
    coverage = receipt['sql_probe']['results']
    base = {'id': 1, 'name': 'Synthetic sensor',
            'parameter': {'id': 2, 'name': 'pm25', 'units': 'µg/m³'}}
    def sensor(value):
        return dict(deepcopy(base), coverage=deepcopy(value))
    cases = [
        ('valid', [sensor(coverage['valid_periods'])], []),
        ('zero_observations', [sensor(coverage['zero_observations'])], []),
        ('coverage_absent', [deepcopy(base)], []),
        ('coverage_null', [sensor(None)], []),
        ('both_periods_null', [sensor(coverage['both_periods_null'])],
         ['expected_count', 'expected_interval', 'observed_interval', 'percent_complete', 'percent_coverage']),
        ('averaging_null', [sensor(coverage['averaging_null'])],
         ['expected_interval', 'observed_interval', 'percent_coverage']),
        ('logging_null', [sensor(coverage['logging_null'])],
         ['expected_count', 'expected_interval', 'percent_complete']),
        ('mixed', [sensor(coverage['valid_periods']), dict(sensor(coverage['both_periods_null']), id=2)],
         ['expected_count', 'expected_interval', 'observed_interval', 'percent_complete', 'percent_coverage']),
        ('empty_coverage', [sensor({})],
         ['expectedCount', 'expectedInterval', 'observedCount', 'observedInterval', 'percentComplete', 'percentCoverage']),
        ('no_results', [], []),
    ]
    app = FastAPI()
    app.include_router(router)
    outputs = []
    for name, rows, expected_errors in cases:
        for kind, url, key, clause in [
            ('location', '/v3/locations/1/sensors', 'locations_id', 'n.sensor_nodes_id = :locations_id'),
            ('sensor', '/v3/sensors/1', 'sensors_id', 's.sensors_id = :sensors_id'),
        ]:
            app.state.rows = deepcopy(rows)
            app.state.calls = []
            errors = []
            with TestClient(app, raise_server_exceptions=True) as client:
                try:
                    response = client.get(url)
                except ResponseValidationError as error:
                    errors = error.errors()
                    assert expected_errors, (name, errors)
                else:
                    assert not expected_errors, (name, response.status_code)
            assert sorted(e['loc'][-1] for e in errors) == sorted(expected_errors)
            if errors:
                index = 1 if name == 'mixed' else 0
                assert all(tuple(e['loc'][:4]) == ('response', 'results', index, 'coverage') for e in errors)
                # Verify the HTTP effect separately; unexpected exceptions above
                # cannot be mistaken for the reported validation mechanism.
                with TestClient(app, raise_server_exceptions=False) as client:
                    response = client.get(url)
                assert response.status_code == 500
                assert response.text == 'Internal Server Error'
            elif kind == 'sensor' and name == 'no_results':
                assert response.status_code == 404
                assert response.json()['detail'] == 'Sensor not found'
            else:
                assert response.status_code == 200, (kind, name, response.text)
                assert len(response.json()['results']) == len(rows)
                assert response.json()['meta']['found'] == len(rows)
                if name == 'zero_observations':
                    assert response.json()['results'][0]['coverage']['percentCoverage'] == 0
            assert len(app.state.calls) == (2 if errors else 1)
            for call in app.state.calls:
                sql = ' '.join(call['query'].split())
                assert f'WHERE {clause} AND n.is_public AND s.is_public' in sql
                assert 'calculate_coverage( r.value_count, s.data_averaging_period_seconds, s.data_logging_period_seconds )' in sql
                assert call['params'] == {key: 1, 'offset': 0}
            assert app.state.rows == rows
            outputs.append({'scenario': name, 'route': kind, 'status': response.status_code,
                            'validation_fields': [e['loc'][-1] for e in errors],
                            'query_and_params_checked': True})

    for url in ['/v3/locations/0/sensors', '/v3/locations/not-an-id/sensors',
                '/v3/sensors/0', '/v3/sensors/not-an-id']:
        app.state.calls = []
        with TestClient(app) as client:
            response = client.get(url)
        assert response.status_code == 422, (url, response.text)
        assert not app.state.calls
        outputs.append({'scenario': 'invalid_path', 'path': url, 'status': 422,
                        'database_not_called': True})
    assert 'openaq_api.settings' not in sys.modules
    assert 'asyncpg' not in sys.modules
    verify_sources(args.source)
    print(json.dumps({'api_revision': receipt['api_revision'],
        'boundary': 'Original sensor router, query builder, response models and extracted unedited DB.fetchPage; synthetic DB.fetch rows, no SQL execution or full app middleware',
        'original_sources_unchanged': True, 'network_denial_control_passed': args.require_network_denial,
        'scenarios': outputs, 'all_checks_passed': True}, indent=2))


if __name__ == '__main__':
    main()
