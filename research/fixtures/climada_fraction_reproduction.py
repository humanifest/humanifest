"""Execute pinned original CLIMADA methods with small synthetic SciPy inputs.

Usage: python3 climada_fraction_reproduction.py /path/to/flattened-source-files
Requires an existing numpy/scipy environment. Does not import or install CLIMADA.
Source GPLv3 methods are extracted at runtime from the supplied original files;
no upstream implementation is reproduced in this Humanifest harness.
"""
import ast
import hashlib
import json
from pathlib import Path
import socket
import subprocess
import sys
import textwrap
from types import SimpleNamespace
import unittest

HASHES = {
    'climada__util__checker.py': '956e6e573fe7742f07f9e01a6126d2350a53f138b7acd5041e9a15cbeecce2cf',
    'climada__hazard__base.py': '18a6eeb9961d1820946571f7dd7ef5ca6a4b2d3efdb618dcadea0cf0495ae613',
    'climada__engine__impact_calc.py': 'c6b72f1b94085494cfd4c82507ee4b4903bd3871a179ba88218c188ffc9eda20',
    'climada__util__test__test_checker.py': '2571c0d425237549b85422b8f7beb9050f07d43adda9a39a5f67964e37fce7ca',
}


def verify(directory):
    for filename, expected in HASHES.items():
        if hashlib.sha256((directory / filename).read_bytes()).hexdigest() != expected:
            raise ValueError('Unexpected source revision: ' + filename)


def extract(directory, filename, name, namespace, class_name=None):
    source = (directory / filename).read_text()
    body = ast.parse(source).body
    if class_name:
        body = next(n for n in body if isinstance(n, ast.ClassDef) and n.name == class_name).body
    node = next(n for n in body if isinstance(n, ast.FunctionDef) and n.name == name)
    assert not node.decorator_list
    original = textwrap.dedent(ast.get_source_segment(source, node))
    exec(compile(original, filename + ':' + str(node.lineno), 'exec'), namespace)
    return namespace[name]


def experiment(directory):
    def deny(*args, **kwargs):
        raise RuntimeError('HUMANIFEST_EXTERNAL_CALL_BLOCKED')
    for name in ['connect', 'connect_ex', 'bind', 'listen']:
        setattr(socket.socket, name, deny)
    for name in ['create_connection', 'getaddrinfo', 'gethostbyname',
                 'gethostbyname_ex', 'gethostbyaddr', 'getnameinfo']:
        setattr(socket, name, deny)
    subprocess.Popen = deny
    for probe in [lambda: socket.create_connection(('example.invalid', 443)),
                  lambda: socket.getaddrinfo('example.invalid', 443),
                  lambda: subprocess.Popen(['false'])]:
        try:
            probe()
        except RuntimeError as error:
            assert str(error) == 'HUMANIFEST_EXTERNAL_CALL_BLOCKED'
        else:
            raise AssertionError('External-call guard failed')
    import numpy as np
    import scipy
    from scipy import sparse

    namespace = {'np': np, 'sparse': sparse}
    prune = extract(directory, 'climada__util__checker.py', 'prune_csr_matrix', namespace)
    namespace['u_check'] = SimpleNamespace(prune_csr_matrix=prune)
    hazard_methods = {name: extract(directory, 'climada__hazard__base.py', name, namespace, 'Hazard')
                      for name in ['check_matrices', '_get_fraction']}
    calc_methods = {name: extract(directory, 'climada__engine__impact_calc.py', name, namespace, 'ImpactCalc')
                    for name in ['__init__', 'impact_matrix']}
    HazardProbe = type('HazardProbe', (), hazard_methods)
    CalcProbe = type('CalcProbe', (), calc_methods)
    original_test = extract(directory, 'climada__util__test__test_checker.py',
                            'test_prune_csr_matrix', namespace, 'TestChecks')
    TestOriginal = type('TestOriginal', (unittest.TestCase,), {'test_prune_csr_matrix': original_test})
    result = unittest.TextTestRunner().run(unittest.defaultTestLoader.loadTestsFromTestCase(TestOriginal))
    assert result.wasSuccessful() and result.testsRun == 1

    def duplicate(values):
        return sparse.csr_matrix((values, [0, 0, 1], [0, 3]), shape=(1, 2))
    cases = [
        ('duplicate ones', duplicate([1., 1., 1.]), [50., 100.]),
        ('unique ones', sparse.csr_matrix([[1., 1.]]), [25., 100.]),
        ('bounded fractions', sparse.csr_matrix([[.25, .75]]), [6.25, 75.]),
        ('fractional duplicates', duplicate([.25, .25, .75]), [12.5, 75.]),
        ('negative fraction', sparse.csr_matrix([[-.25, .75]]), [-6.25, 75.]),
        ('fraction above one', sparse.csr_matrix([[1.5, 1.]]), [37.5, 100.]),
        ('empty fraction', sparse.csr_matrix((1, 2)), [25., 100.]),
        ('explicit zero fraction', sparse.csr_matrix(([0., 0.], [0, 1], [0, 2]), shape=(1, 2)), [25., 100.]),
    ]
    reports = []
    for name, fraction, expected in cases:
        # Observe an independent copy; sparse observations can canonicalize their receiver.
        raw_data, raw_indices, raw_indptr = fraction.data.copy(), fraction.indices.copy(), fraction.indptr.copy()
        raw_nnz = fraction.nnz
        apparent_before = fraction.copy().toarray()
        np.testing.assert_array_equal(fraction.data, raw_data)
        np.testing.assert_array_equal(fraction.indices, raw_indices)
        np.testing.assert_array_equal(fraction.indptr, raw_indptr)
        hazard = HazardProbe()
        hazard.intensity = sparse.csr_matrix([[1., 1.]])
        hazard.fraction = fraction
        calls = []
        def get_mdr(indices, impact_function):
            calls.append((indices.copy(), impact_function))
            return sparse.csr_matrix([[.25, .5]])
        hazard.get_mdr = get_mdr  # Disclosed test double; no impact function is evaluated.
        calc = CalcProbe(SimpleNamespace(gdf=SimpleNamespace(shape=(2, 1))), None, hazard)
        np.testing.assert_array_equal(hazard.fraction.toarray(), apparent_before)
        assert hazard.fraction.has_canonical_format
        sentinel = object()
        values = calc.impact_matrix(np.array([100., 200.]), np.array([0, 1]), sentinel).toarray()[0]
        np.testing.assert_array_equal(values, expected)
        assert len(calls) == 1 and calls[0][1] is sentinel
        np.testing.assert_array_equal(calls[0][0], [0, 1])
        reports.append({'case': name, 'raw_data': raw_data.tolist(), 'raw_nnz': int(raw_nnz),
                        'apparent_before': apparent_before.tolist(), 'canonical_data': hazard.fraction.data.tolist(),
                        'canonical_nnz': int(hazard.fraction.nnz), 'impact': values.tolist(), 'total': float(values.sum())})
    bad = HazardProbe()
    bad.intensity, bad.fraction = sparse.csr_matrix([[1., 1.]]), sparse.csr_matrix([[1.]])
    try:
        CalcProbe(SimpleNamespace(gdf=SimpleNamespace(shape=(2, 1))), None, bad)
    except ValueError as error:
        assert str(error) == 'Intensity and fraction matrices must have the same shape'
    else:
        raise AssertionError('Shape mismatch was not rejected')
    assert not any(name == 'climada' or name.startswith('climada.') for name in sys.modules)
    print(json.dumps({'python': sys.version.split()[0], 'numpy': np.__version__, 'scipy': scipy.__version__,
                      'original_tests_passed': 1, 'impact_cases': reports, 'shape_mismatch_rejected': True}, indent=2))


def main():
    directory = Path(sys.argv[-1]).resolve()
    verify(directory)
    if sys.argv[1] == '--child':
        experiment(directory)
        verify(directory)
        return 0
    result = subprocess.run([sys.executable, str(Path(__file__).resolve()), '--child', str(directory)],
                            env={'PATH': '/usr/bin:/bin', 'PYTHONDONTWRITEBYTECODE': '1', 'TZ': 'UTC',
                                 'OPENBLAS_NUM_THREADS': '1', 'OMP_NUM_THREADS': '1'}, timeout=60)
    verify(directory)
    return result.returncode


if __name__ == '__main__':
    raise SystemExit(main())
