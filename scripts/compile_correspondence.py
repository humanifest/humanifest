"""Compile the portable Python shard with pinned Metamap v0.5.0.

Run `npm ci --ignore-scripts --prefix tools/metamap` once, then
`python -m scripts.compile_correspondence [--root PATH] [--check]`.
"""
import argparse
import json
from pathlib import Path
import subprocess
import tempfile

from humanifest.correspondence import digest, export_shard

TOOLS = Path(__file__).resolve().parents[1] / 'tools/metamap'


def compile_input(shard):
    process = subprocess.run(['node', str(TOOLS / 'compile.mjs')], input=json.dumps(shard),
                             text=True, capture_output=True, timeout=60)
    if process.returncode:
        raise ValueError('Metamap compilation rejected: ' + (process.stdout or process.stderr))
    return json.loads(process.stdout)


def compile_portfolio(root, *, check=False):
    shard = export_shard(root)
    result = compile_input(shard)
    artifact = {'compiler': '@roryscot/metamap@0.5.0', 'inputs': shard['inputs'],
                'generation': result['generation'], 'projection': result['projection'],
                'projection_checksum': digest(result['projection'])}
    outputs = {'portfolio.json': artifact, 'shard.json': shard['graph'], 'viability.json': shard['policy'],
               'relations.json': shard['pack'], 'projection-spec.json': shard['spec']}
    destination = root / 'metamap/generated'
    if check:
        for name, value in outputs.items():
            if json.loads((destination / name).read_text()) != value:
                raise ValueError(f'stale generated artifact: {name}')
    else:
        destination.mkdir(parents=True, exist_ok=True)
        for name, value in outputs.items():
            with tempfile.NamedTemporaryFile(mode='w', dir=destination, delete=False) as out:
                json.dump(value, out, indent=2, ensure_ascii=False)
                out.write('\n')
                temporary = Path(out.name)
            temporary.replace(destination / name)
    return artifact


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path('.'))
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    compile_portfolio(args.root.resolve(), check=args.check)
    print('Metamap portfolio projection verified' if args.check else 'Metamap portfolio projection generated')


if __name__ == '__main__':
    main()
