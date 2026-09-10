"""Run unchanged OpenAQ coverage functions in a new single-user PostgreSQL cluster.

Requires the locked response-probe environment. This checks pure calculation
and original model validation, not the deployed database schema or API router.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from openaq_coverage_response_probe import verify_sources


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', required=True, type=Path)
    parser.add_argument('--database-source', required=True, type=Path)
    parser.add_argument('--postgres-bin', required=True, type=Path)
    parser.add_argument('--work-area', required=True, type=Path)
    args = parser.parse_args()
    verify_sources(args.source)
    source_path = args.database_source / 'openaqdb/idempotent/util_functions.sql'
    body = source_path.read_bytes()
    assert hashlib.sha1(b'blob '+str(len(body)).encode()+b'\0'+body).hexdigest() == 'f16a45ad97c7642e76c02092aceeb7aab23326a5'
    functions = re.findall(r'CREATE OR REPLACE FUNCTION calculate_coverage\([\s\S]*?\$\$ LANGUAGE SQL PARALLEL SAFE;', body.decode())
    assert len(functions) == 2
    work = Path(tempfile.mkdtemp(prefix='coverage-pg-', dir=args.work_area))
    cluster = work / 'cluster'
    init = subprocess.run([str(args.postgres_bin/'initdb'), '-D', str(cluster),
        '--no-locale', '--encoding=UTF8', '--auth-local=reject', '--auth-host=reject'],
        text=True, capture_output=True)
    (work/'initdb.log').write_text(init.stdout + init.stderr)
    assert init.returncode == 0, init.stderr
    sql = '\n\n'.join(functions) + '''

CREATE FUNCTION probe_error(averaging numeric, logging numeric) RETURNS text AS $$
BEGIN
  PERFORM calculate_coverage(1, averaging, logging);
  RETURN 'none';
EXCEPTION WHEN division_by_zero THEN RETURN SQLSTATE;
END;
$$ LANGUAGE plpgsql;

SELECT json_build_object(
  'omitted_periods', calculate_coverage(1),
  'valid_periods', calculate_coverage(1,3600,3600),
  'both_periods_null', calculate_coverage(1,NULL,NULL),
  'averaging_null', calculate_coverage(1,NULL,3600),
  'logging_null', calculate_coverage(1,3600,NULL),
  'zero_observations', calculate_coverage(0,3600,3600),
  'timestamp_overload', calculate_coverage(1,3600,3600,'2026-09-10 00:00Z'::timestamptz,'2026-09-10 01:00Z'::timestamptz),
  'zero_averaging_error', probe_error(0,3600),
  'zero_logging_error', probe_error(3600,0)
) AS result;

'''
    (work/'probe.sql').write_text(sql)
    process = subprocess.run([str(args.postgres_bin/'postgres'), '--single', '-D',
        str(cluster), '-j', '-c', 'listen_addresses=', '-c', 'unix_socket_directories=',
        'postgres'], input=sql, text=True, capture_output=True)
    (work/'postgres.log').write_text(process.stdout + process.stderr)
    assert process.returncode == 0, process.stderr
    assert not re.search(r'\b(ERROR|FATAL|PANIC):', process.stderr), process.stderr
    lines = [line for line in process.stdout.splitlines() if 'result = "' in line]
    assert len(lines) == 1, process.stdout
    raw = lines[0].split('result = "', 1)[1].rsplit('"', 1)[0]
    results = json.loads(raw)
    assert results['valid_periods'] == results['omitted_periods'] == results['timestamp_overload']
    assert results['valid_periods']['expected_count'] == 1
    assert results['valid_periods']['percent_coverage'] == 100
    assert results['zero_observations']['observed_count'] == 0
    assert results['zero_observations']['percent_coverage'] == 0
    assert results['zero_averaging_error'] == results['zero_logging_error'] == '22012'

    sys.path.insert(0, str(args.source.resolve()))
    from openaq_api.v3.models.responses import SensorsResponse
    from pydantic import ValidationError
    expected_nulls = {
        'both_periods_null': ['expected_count','expected_interval','observed_interval','percent_complete','percent_coverage'],
        'averaging_null': ['expected_interval','observed_interval','percent_coverage'],
        'logging_null': ['expected_count','expected_interval','percent_complete'],
    }
    model_errors = {}
    for name, coverage in results.items():
        if name.endswith('_error'):
            continue
        actual_nulls = sorted(k for k,v in coverage.items() if v is None)
        assert actual_nulls == sorted(expected_nulls.get(name, [])), (name, actual_nulls)
        payload = {'results':[{'id':1,'name':'Synthetic sensor',
            'parameter':{'id':2,'name':'pm25','units':'µg/m³'}, 'coverage':coverage}]}
        errors = []
        try:
            SensorsResponse.model_validate(payload)
        except ValidationError as error:
            errors = [e['loc'][-1] for e in error.errors()]
        assert sorted(errors) == sorted(expected_nulls.get(name, [])), (name, errors)
        model_errors[name] = errors
    verify_sources(args.source)
    assert source_path.read_bytes() == body
    print(json.dumps({'postgres_version':subprocess.check_output([str(args.postgres_bin/'postgres'),'--version'],text=True).strip(),
        'work_area':str(work), 'single_user':True, 'original_function_definitions':len(functions),
        'results':results, 'original_model_errors':model_errors,
        'all_checks_passed':True},indent=2))


if __name__ == '__main__':
    main()
