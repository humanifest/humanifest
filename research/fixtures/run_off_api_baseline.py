"""Run the unchanged pinned Open Food Facts API tests with a Python network guard.

Requires the inspected wheel-only virtualenv at CHECKOUT/.venv. This guard blocks
accidental Python socket/DNS calls, not arbitrary native code or subprocesses.
"""

import hashlib
from pathlib import Path
import subprocess
import sys


HASHES = {
    "pyproject.toml": "48f1179cf5bf656f41036cca85e22cb083d76ca61f7ffcbfd149a98b60358cea",
    "uv.lock": "e4d13339a3ae068ec6325cf60c37900a69e9bd51d752948d5c2aae4889ba83b1",
    "src/openfoodfacts/api.py": "f1ceb8ab73858588c8db55745b0617f65afde3314aa18dd4a52c77a6590e95de",
    "tests/unit/test_api.py": "569ca35239f7a2cd37bb91245bd254734318ace04d5e2a0933baa533bc122fbf",
}

RUNNER = '''
import socket

def deny(*args, **kwargs):
    raise RuntimeError("HUMANIFEST_NETWORK_BLOCKED")

for name in ["connect", "connect_ex", "bind", "listen"]:
    setattr(socket.socket, name, deny)
for name in ["create_connection", "getaddrinfo", "gethostbyname",
             "gethostbyname_ex", "gethostbyaddr", "getnameinfo"]:
    setattr(socket, name, deny)

with socket.socket() as probe:
    for check in [lambda: socket.create_connection(("example.invalid", 443)),
                  lambda: socket.getaddrinfo("example.invalid", 443),
                  lambda: probe.bind(("127.0.0.1", 0))]:
        try:
            check()
        except RuntimeError as error:
            assert str(error) == "HUMANIFEST_NETWORK_BLOCKED"
        else:
            raise AssertionError("Network guard did not reject operation")

import pytest
raise SystemExit(pytest.main(["tests/unit/test_api.py", "-q"]))
'''


def verify(checkout):
    for filename, expected in HASHES.items():
        if hashlib.sha256((checkout / filename).read_bytes()).hexdigest() != expected:
            raise ValueError(f"Unexpected source revision: {filename}")


def main():
    checkout = Path(sys.argv[1]).resolve()
    verify(checkout)
    result = subprocess.run(
        [str(checkout / ".venv/bin/python"), "-c", RUNNER], cwd=checkout,
        env={"PATH": "/usr/bin:/bin", "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1",
             "PYTHONDONTWRITEBYTECODE": "1", "TZ": "UTC"},
        timeout=120,
    )
    verify(checkout)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
