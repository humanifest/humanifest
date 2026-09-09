"""Build and smoke-test an installed wheel outside the source checkout.

Run with: python -m scripts.check_install
Uses the already-installed setuptools; build/install never access an index.
"""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import venv
import zipfile


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    environment = os.environ.copy()
    for key in ["PYTHONPATH", "PYTHONHOME"]:
        environment.pop(key, None)
    with tempfile.TemporaryDirectory(prefix="humanifest-install-") as temp:
        temporary = Path(temp)
        wheels = temporary / "wheels"
        subprocess.run([
            sys.executable, "-m", "pip", "wheel", "--no-deps", "--no-build-isolation",
            "--no-index", "--no-cache-dir", "--wheel-dir", str(wheels), str(root),
        ], cwd=temp, env=environment, check=True)
        wheel_files = list(wheels.glob("humanifest-*.whl"))
        if len(wheel_files) != 1:
            raise AssertionError(f"Expected one Humanifest wheel, found {wheel_files}")
        wheel = wheel_files[0]
        with zipfile.ZipFile(wheel) as archive:
            for name in archive.namelist():
                top = name.split("/")[0]
                if top != "humanifest" and not (top.startswith("humanifest-") and top.endswith(".dist-info")):
                    raise AssertionError(f"Unexpected packaged file: {name}")
        virtualenv = temporary / "venv"
        venv.create(virtualenv, with_pip=True)
        binaries = virtualenv / ("Scripts" if os.name == "nt" else "bin")
        python = binaries / ("python.exe" if os.name == "nt" else "python")
        cli = binaries / ("humanifest.exe" if os.name == "nt" else "humanifest")
        subprocess.run([
            str(python), "-m", "pip", "install", "--no-index", "--no-deps",
            "--no-cache-dir", str(wheel),
        ], cwd=temp, env=environment, check=True)
        # Synthetic records keep packaging checks independent of portfolio selection.
        from tests.test_models import opportunity

        record = opportunity()
        record["gates"]["maintainer_interest_confirmed"]["passed"] = False
        candidate = temporary / "candidate.json"
        candidate.write_text(json.dumps(record), encoding="utf-8")
        commands = [
            ["--help"], ["validate", "--root", str(root)], ["report", "--root", str(root)],
            ["score", str(candidate)], ["brief", str(candidate)],
            ["handoff", str(candidate), "--target", "codex"],
            ["sources", "--root", str(root), "--as-of", "2026-09-08", "--max-age-days", "30", "--format", "json"],
            ["work", "--root", str(root), "--as-of", "2026-09-08", "--format", "json"],
        ]
        for args in commands:
            result = subprocess.run([str(cli), *args], cwd=temp, env=environment,
                                    check=True, capture_output=True, text=True)
            if not result.stdout or result.stderr:
                raise AssertionError(f"Unexpected {args[0]} output: {result}")
            if args[0] == "score" and json.loads(result.stdout)["eligible_for_building"] is not False:
                raise AssertionError("Installed score bypassed the maintainer gate")
            if args[0] == "handoff" and "Implementation blocked" not in result.stdout:
                raise AssertionError("Installed handoff bypassed the maintainer gate")
            if args[0] == "sources" and json.loads(result.stdout)["as_of"] != "2026-09-08":
                raise AssertionError("Installed source review did not preserve its as-of date")
            if args[0] == "work" and json.loads(result.stdout)["as_of"] != "2026-09-08":
                raise AssertionError("Installed work view did not preserve its as-of date")
            print(f"Installed CLI passed: {args[0]}")
        invalid = subprocess.run([str(cli), "validate", "--root", temp], cwd=temp,
                                 env=environment, capture_output=True, text=True)
        if invalid.returncode != 1 or invalid.stdout or "required record directory" not in invalid.stderr:
            raise AssertionError(f"Installed CLI accepted a missing portfolio: {invalid}")
        record["gates"]["maintainer_interest_confirmed"]["passed"] = True
        del record["gates"]["maintainer_interest_confirmed"]["source_ids"]
        candidate.write_text(json.dumps(record), encoding="utf-8")
        uncited = subprocess.run([str(cli), "score", str(candidate)], cwd=temp,
                                 env=environment, capture_output=True, text=True)
        if uncited.returncode != 1 or uncited.stdout or "must cite confirmation evidence" not in uncited.stderr:
            raise AssertionError(f"Installed CLI accepted uncited confirmation: {uncited}")
    print("Wheel contents and installed CLI smoke checks passed.")


if __name__ == "__main__":
    main()
