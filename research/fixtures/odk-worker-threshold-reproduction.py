"""Run only ODK's inspected worker-count function with synthetic byte amounts.

Usage: python3 research/fixtures/odk-worker-threshold-reproduction.py /path/start-odk.sh
Never source or execute the complete startup script: it reads secrets, writes
configuration, runs database migrations and starts services.
"""

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path


def main(path):
    source = path.read_bytes()
    assert hashlib.sha256(source).hexdigest() == (
        "c83aa91370757985a9e3e8f22dcf1437caf9f25213b5afffa9891ea4cc1c4c9f"
    ), "Expected inspected ODK startup source"
    match = re.search(r"^determine_worker_count\(\) \{\n.*?^\}", source.decode(), re.M | re.S)
    assert match, "Expected standalone worker-count function"
    function = match.group(0)
    cases = [
        (0, 1), (1_100_000, 1), (1_100_001, 4),
        (512 * 1024**2, 4), (1024**3, 4),
        (1_100_000 * 1024, 4), (1_100_000 * 1024 + 1, 4), (2 * 1024**3, 4),
    ]
    results = []
    for memory_bytes, expected_current in cases:
        result = subprocess.run(
            ["/bin/bash", "--noprofile", "--norc", "-c",
             function + '\ndetermine_worker_count "$1"', "worker-probe", str(memory_bytes)],
            env={"PATH": "/usr/bin:/bin"}, capture_output=True, text=True, check=True,
        )
        assert result.stderr == "", result.stderr
        actual = int(result.stdout)
        assert actual == expected_current, (memory_bytes, actual)
        results.append({"memory_bytes": memory_bytes, "current_workers": actual,
                        "comparison_if_threshold_is_1100000_KiB": 4 if memory_bytes > 1_100_000 * 1024 else 1})
    print(json.dumps({"scope": "Original worker-count function only; no cgroup discovery, server, or resource measurement",
                      "cases": results}, indent=2))


if __name__ == "__main__":
    main(Path(sys.argv[1]))
