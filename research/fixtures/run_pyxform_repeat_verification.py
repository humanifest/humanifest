"""Verify unchanged pinned pyxform repeat behavior without Java or services.

Usage: python3 run_pyxform_repeat_verification.py CHECKOUT baseline|matrix
Requires CHECKOUT/.venv with the inspected pinned wheel dependencies.
The Python guard prevents accidental network/subprocess use; it is not an OS sandbox.
"""
import hashlib
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import unittest

REVISION = '26006d0830570ffa3caead24b0c9a470278af2cf'
JAVA_TESTS = {
    'tests.test_repeat.TestRepeatParsing.test_empty_repeat__no_question__ok',
    'tests.test_repeat.TestRepeatParsing.test_empty_repeat__no_question_control__ok',
}


def verify_sources(checkout):
    def git(*args):
        return subprocess.check_output(['git', *args], cwd=checkout)
    if git('rev-parse', 'HEAD').decode().strip() != REVISION:
        raise ValueError('Unexpected pyxform revision')
    entries = git('ls-tree', '-r', '-z', REVISION).split(b'\0')
    count = 0
    for entry in filter(None, entries):
        metadata, path = entry.split(b'\t', 1)
        mode, kind, expected = metadata.split()
        if kind != b'blob' or mode == b'120000':
            raise ValueError('Unexpected non-file source entry')
        content = (checkout / os.fsdecode(path)).read_bytes()
        actual = hashlib.sha1(b'blob ' + str(len(content)).encode() + b'\0' + content).hexdigest()
        if actual != expected.decode():
            raise ValueError('Source differs: ' + os.fsdecode(path))
        count += 1
    return count


def guard():
    def deny(*args, **kwargs):
        raise RuntimeError('HUMANIFEST_EXTERNAL_CALL_BLOCKED')
    for name in ['connect', 'connect_ex', 'bind', 'listen']:
        setattr(socket.socket, name, deny)
    for name in ['create_connection', 'getaddrinfo', 'gethostbyname',
                 'gethostbyname_ex', 'gethostbyaddr', 'getnameinfo']:
        setattr(socket, name, deny)
    subprocess.Popen = deny
    os.system = deny
    for probe in [lambda: socket.create_connection(('example.invalid', 443)),
                  lambda: socket.getaddrinfo('example.invalid', 443),
                  lambda: subprocess.Popen(['java', '-version'])]:
        try:
            probe()
        except RuntimeError as error:
            assert str(error) == 'HUMANIFEST_EXTERNAL_CALL_BLOCKED'
        else:
            raise AssertionError('External-call guard failed')


def baseline():
    def flatten(suite):
        for item in suite:
            if isinstance(item, unittest.TestSuite):
                yield from flatten(item)
            else:
                yield item
    cases = list(flatten(unittest.defaultTestLoader.loadTestsFromName('tests.test_repeat')))
    deferred = {case.id() for case in cases if case.id() in JAVA_TESTS}
    assert deferred == JAVA_TESTS
    print('Deferred Java-only tests: ' + json.dumps(sorted(deferred)), flush=True)
    result = unittest.TextTestRunner(verbosity=1).run(
        unittest.TestSuite(case for case in cases if case.id() not in JAVA_TESTS)
    )
    return 0 if result.wasSuccessful() else 1


def matrix():
    from lxml import etree
    from pyxform.xls2xform import convert
    namespaces = {'x': 'http://www.w3.org/2002/xforms',
                  'h': 'http://www.w3.org/1999/xhtml',
                  'jr': 'http://openrosa.org/javarosa'}
    results = []
    for depth in [1, 2, 3]:
        for grouped in ([False] if depth == 1 else [False, True]):
            for count in ['', '0', '2']:
                rows = []
                for level in range(1, depth + 1):
                    if grouped and level > 1:
                        rows.append({'type': 'begin group', 'name': f'g{level}', 'label': f'Group {level}'})
                    rows.append({'type': 'begin repeat', 'name': f'r{level}',
                                 'label': f'Repeat {level}', 'repeat_count': count})
                    rows.append({'type': 'text', 'name': f'q{level}',
                                 'label': f'Question {level}', 'default': f'default-{level}'})
                for level in range(depth, 0, -1):
                    rows.append({'type': 'end repeat'})
                    if grouped and level > 1:
                        rows.append({'type': 'end group'})
                # Independent sibling ensures the template flag does not leak out.
                rows.extend([{'type': 'begin repeat', 'name': 'sibling', 'label': 'Sibling'},
                             {'type': 'text', 'name': 'sibling_q', 'label': 'Sibling question', 'default': 'sibling-default'},
                             {'type': 'end repeat'}])
                result = convert({'survey': rows, 'settings': [{'form_id': 'repeat_probe', 'form_title': 'Synthetic repeat probe'}]},
                                 validate=False, pretty_print=False)
                root = etree.fromstring(result.xform.encode())
                data = root.xpath('/h:html/h:head/x:model/x:instance[1]/*', namespaces=namespaces)[0]
                paths = []
                def walk(node, path=''):
                    name = etree.QName(node).localname
                    kind = 'T' if node.get('{'+namespaces['jr']+'}template') is not None else 'C'
                    here = path + '/' + name + ':' + kind
                    if (name.startswith('r') and name[1:].isdigit()) or name == 'sibling':
                        paths.append(here)
                    if name.startswith('r') and name[1:].isdigit():
                        question = node.find('{'+namespaces['x']+'}q'+name[1:])
                        assert question is not None and question.text == 'default-' + name[1:]
                    if name.startswith('q') and name[1:].isdigit():
                        assert node.text == 'default-' + name[1:]
                    if name == 'sibling_q':
                        assert node.text == 'sibling-default'
                    for child in node:
                        walk(child, here)
                walk(data)
                assert len(data.xpath('x:sibling[@jr:template]', namespaces=namespaces)) == 1
                assert len(data.xpath('x:sibling[not(@jr:template)]', namespaces=namespaces)) == 1
                if depth > 1:
                    nested = 'g2:C/r2:C' if grouped else 'r2:C'
                    assert ('/data:C/r1:T/' + nested in paths) is grouped
                    assert '/data:C/r1:C/' + nested in paths
                count_binds = root.xpath('/h:html/h:head/x:model/x:bind[@calculate]', namespaces=namespaces)
                count_values = [bind.get('calculate') for bind in count_binds]
                assert count_values == ([] if not count else [count] * depth)
                results.append({'depth': depth, 'grouped': grouped, 'repeat_count': count or 'absent',
                                'count_calculations': count_values,
                                'warnings': result.warnings, 'repeat_paths': paths})
    for depth in [1, 2, 3]:
        for grouped in ([False] if depth == 1 else [False, True]):
            shapes = [r['repeat_paths'] for r in results if r['depth'] == depth and r['grouped'] == grouped]
            assert shapes[0] == shapes[1] == shapes[2]
    print(json.dumps(results, indent=2))
    return 0


def main():
    if sys.argv[1] == '--child':
        guard()
        sys.path.insert(0, str(Path.cwd()))
        return baseline() if sys.argv[2] == 'baseline' else matrix()
    checkout = Path(sys.argv[1]).resolve()
    mode = sys.argv[2]
    if mode not in {'baseline', 'matrix'}:
        raise ValueError('Choose baseline or matrix')
    count = verify_sources(checkout)
    result = subprocess.run([str(checkout / '.venv/bin/python'), str(Path(__file__).resolve()), '--child', mode],
                            cwd=checkout, env={'PATH': '/usr/bin:/bin', 'PYTHONDONTWRITEBYTECODE': '1',
                                              'PYXFORM_TESTS_RUN_ODK_VALIDATE': 'false', 'TZ': 'UTC'}, timeout=120)
    assert verify_sources(checkout) == count
    print(f'Verified {count} unchanged tracked source files before and after execution.', file=sys.stderr)
    return result.returncode


if __name__ == '__main__':
    raise SystemExit(main())
