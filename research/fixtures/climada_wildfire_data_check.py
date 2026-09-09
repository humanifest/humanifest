"""Read the pinned public COD v1.1 HDF5 sparse fields; never import CLIMADA.

Usage: python climada_wildfire_data_check.py SOURCE_DIRECTORY DATASET.hdf5
Requires h5py, NumPy and SciPy; no downloads or package installation are performed.
The adjacent synthetic harness verifies and extracts the original canonicalizer.
"""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

DATA_SHA256 = 'e62c41b250786ff36bdf6400d7e84cc38cc650a3ceab67c4c00ce3a53f6aeb8f'
DATA_BYTES = 31323560


def check_file(path):
    assert path.stat().st_size == DATA_BYTES
    assert hashlib.sha256(path.read_bytes()).hexdigest() == DATA_SHA256


def experiment(source, path):
    import socket
    import platform
    # Prime the standard-library uname cache before denying child processes.
    # h5py queries it during import; no third-party code has run yet.
    platform.processor()
    def deny(*args, **kwargs):
        raise RuntimeError('HUMANIFEST_EXTERNAL_CALL_BLOCKED')
    for name in ['connect', 'connect_ex', 'bind', 'listen']:
        setattr(socket.socket, name, deny)
    for name in ['create_connection', 'getaddrinfo', 'gethostbyname',
                 'gethostbyname_ex', 'gethostbyaddr', 'getnameinfo']:
        setattr(socket, name, deny)
    subprocess.Popen = deny
    import h5py
    import numpy as np
    import scipy
    from scipy import sparse
    from climada_fraction_reproduction import verify, extract
    verify(source)
    prune = extract(source, 'climada__util__checker.py', 'prune_csr_matrix',
                    {'np': np, 'sparse': sparse})
    reports = {}
    matrices = {}
    with h5py.File(path, 'r') as f:
        for name in ['intensity', 'fraction']:
            assert isinstance(f.get(name, getlink=True), h5py.HardLink)
            group = f[name]
            shape = tuple(int(n) for n in group.attrs['shape'])
            assert len(shape) == 2 and all(0 < n < 10_000_000 for n in shape)
            arrays = {}
            for field in ['data', 'indices', 'indptr']:
                assert isinstance(group.get(field, getlink=True), h5py.HardLink)
                dataset = group[field]
                assert not dataset.is_virtual and not dataset.external
                assert dataset.ndim == 1 and dataset.dtype.kind in 'fiu'
                assert dataset.size * dataset.dtype.itemsize < 100_000_000
                assert dataset.compression in (None, 'gzip', 'lzf', 'szip')
                arrays[field] = dataset[:]
            raw = sparse.csr_matrix((arrays['data'], arrays['indices'], arrays['indptr']), shape=shape)
            raw.check_format(full_check=True)
            assert np.isfinite(raw.data).all()
            # Independent row-wise index counts avoid inferring duplicates solely
            # from the canonicalizer whose effect is being investigated.
            duplicate_entries = 0
            duplicated_cells = 0
            for start, end in zip(raw.indptr[:-1], raw.indptr[1:]):
                _, counts = np.unique(raw.indices[start:end], return_counts=True)
                duplicate_entries += int(np.sum(counts - 1))
                duplicated_cells += int(np.count_nonzero(counts > 1))
            canonical = raw.copy()
            prune(canonical)
            assert canonical.has_canonical_format
            assert raw.nnz == arrays['data'].size
            np.testing.assert_array_equal(raw.data, arrays['data'])
            np.testing.assert_array_equal(raw.indices, arrays['indices'])
            np.testing.assert_array_equal(raw.indptr, arrays['indptr'])
            np.testing.assert_allclose(raw.data.sum(), canonical.data.sum(), rtol=1e-12)
            values, counts = np.unique(canonical.data, return_counts=True)
            reports[name] = {
                'shape': list(shape), 'raw_nnz': int(raw.nnz),
                'raw_min': float(raw.data.min()), 'raw_max': float(raw.data.max()),
                'raw_all_ones': bool(np.all(raw.data == 1)),
                'raw_zeros': int(np.count_nonzero(raw.data == 0)),
                'duplicate_extra_entries': duplicate_entries,
                'duplicated_cells': duplicated_cells,
                'canonical_nnz': int(canonical.nnz),
                'canonical_min': float(canonical.data.min()),
                'canonical_max': float(canonical.data.max()),
                'canonical_above_one': int(np.count_nonzero(canonical.data > 1)),
                'raw_sum': float(raw.data.sum()), 'canonical_sum': float(canonical.data.sum()),
                'canonical_histogram': {str(float(v)): int(c) for v, c in zip(values, counts)} if len(values) < 20 else None,
            }
            matrices[name] = canonical
    fraction = matrices['fraction']
    assert fraction.shape == matrices['intensity'].shape
    binary = fraction.copy()
    binary.data[:] = 1
    reports['diagnostic_only'] = {
        'sum_fraction_over_binary_support': float(fraction.data.sum() / binary.nnz),
        'fraction_above_one_with_positive_intensity': int((fraction > 1).multiply(matrices['intensity'] > 0).nnz),
        'note': 'Binary support is a counterfactual comparison, not an approved repair or population-weighted/full-model impact estimate.',
    }
    assert not any(n == 'climada' or n.startswith('climada.') for n in sys.modules)
    verify(source)
    check_file(path)
    print(json.dumps({'dataset_sha256': DATA_SHA256, 'python': sys.version.split()[0],
                      'numpy': np.__version__, 'scipy': scipy.__version__,
                      'h5py': h5py.__version__, 'hdf5': h5py.version.hdf5_version,
                      'results': reports}, indent=2))


def main():
    source, path = (Path(p).resolve() for p in sys.argv[-2:])
    check_file(path)
    if sys.argv[1] == '--child':
        experiment(source, path)
        return 0
    result = subprocess.run([sys.executable, str(Path(__file__).resolve()), '--child', str(source), str(path)],
                            env={'PATH': '/usr/bin:/bin', 'PYTHONDONTWRITEBYTECODE': '1',
                                 'TZ': 'UTC', 'OPENBLAS_NUM_THREADS': '1', 'OMP_NUM_THREADS': '1',
                                 'HDF5_PLUGIN_PRELOAD': '::', 'HDF5_PLUGIN_PATH': '/nonexistent'}, timeout=60)
    check_file(path)
    return result.returncode


if __name__ == '__main__':
    raise SystemExit(main())
