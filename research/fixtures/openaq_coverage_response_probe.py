"""Research probe of pinned OpenAQ models; synthetic FastAPI boundary, not its router.

Run with the selected upstream lockfile dependencies and --source pointing to
an external copy of the original API files. No target production edits needed.
"""
import argparse
from copy import deepcopy
import errno
import hashlib
import importlib.metadata
import json
from pathlib import Path
import socket
import sys

EXPECTED = {
    "openaq_api/v3/models/responses.py": "44736f6efd54c2da8005d28764f18042a5457344",
    "openaq_api/v3/models/utils.py": "9c824efe2991175c4c0197d024dfc2b3986ddad4",
}


def verify_sources(root):
    for name, expected in EXPECTED.items():
        body = (root / name).read_bytes()
        actual = hashlib.sha1(b"blob " + str(len(body)).encode() + b"\0" + body).hexdigest()
        assert actual == expected, (name, actual)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--require-network-denial", action="store_true")
    args = parser.parse_args()
    verify_sources(args.source)
    if args.require_network_denial:
        with socket.socket() as control:
            try:
                control.bind(("127.0.0.1", 0))
            except OSError as error:
                assert error.errno in (errno.EPERM, errno.EACCES), error
            else:
                raise AssertionError("Network-denial control unexpectedly succeeded")

    sys.path.insert(0, str(args.source.resolve()))
    from openaq_api.v3.models.responses import SensorsResponse
    from pydantic import ValidationError
    from fastapi import FastAPI
    from fastapi.testclient import TestClient

    sensor = {
        "id": 1, "name": "Synthetic PM2.5 sensor",
        "parameter": {"id": 2, "name": "pm25", "units": "µg/m³"},
        "coverage": {
            "expected_count": 24, "expected_interval": "24:00:00",
            "observed_count": 24, "observed_interval": "24:00:00",
            "percent_complete": 100.0, "percent_coverage": 100.0,
        },
    }
    invalid_fields = ["expected_count", "expected_interval", "observed_interval",
                      "percent_complete", "percent_coverage"]
    absent = deepcopy(sensor); absent.pop("coverage")
    null = deepcopy(sensor); null["coverage"] = None
    zero = deepcopy(sensor)
    zero["coverage"].update(observed_count=0, observed_interval="00:00:00",
                            percent_complete=0.0, percent_coverage=0.0)
    partial = deepcopy(sensor)
    partial["coverage"].update({field: None for field in invalid_fields})
    mixed_bad = deepcopy(partial); mixed_bad["id"] = 2
    empty = deepcopy(sensor); empty["coverage"] = {}
    camel = deepcopy(sensor)
    camel["coverage"] = {"expectedCount": 24, "expectedInterval": "24:00:00",
                         "observedCount": 24, "observedInterval": "24:00:00",
                         "percentComplete": 100.0, "percentCoverage": 100.0}
    scenarios = [
        ("valid", [sensor], [], 200),
        ("coverage_absent", [absent], [], 200),
        ("coverage_null", [null], [], 200),
        ("valid_zero_observations", [zero], [], 200),
        ("partial_null_fields", [partial], invalid_fields, 500),
        ("valid_and_invalid_sensors", [sensor, mixed_bad], invalid_fields, 500),
        ("empty_coverage_object", [empty], ["expectedCount", "expectedInterval",
            "observedCount", "observedInterval", "percentComplete", "percentCoverage"], 500),
        ("camel_case_input", [camel], [], 200),
    ]
    results = []
    for name, sensors, expected_errors, expected_status in scenarios:
        payload = {"results": deepcopy(sensors)}
        before = deepcopy(payload)
        errors = []
        try:
            validated = SensorsResponse.model_validate(payload)
            assert not expected_errors, name
            if name in ("coverage_absent", "coverage_null"):
                assert validated.results[0].coverage is None
            if name == "valid_zero_observations":
                assert validated.results[0].coverage.percent_coverage == 0.0
        except ValidationError as error:
            errors = [{"loc": list(e["loc"]), "type": e["type"]} for e in error.errors()]
            assert sorted(e["loc"][-1] for e in errors) == sorted(expected_errors), (name, errors)
            index = 1 if name == "valid_and_invalid_sensors" else 0
            assert all(e["loc"][:3] == ["results", index, "coverage"] for e in errors)
        assert payload == before

        app = FastAPI()
        async def endpoint():
            return deepcopy(payload)
        app.get("/probe", response_model=SensorsResponse)(endpoint)
        with TestClient(app, raise_server_exceptions=False) as client:
            response = client.get("/probe")
        assert response.status_code == expected_status, (name, response.status_code)
        if expected_status == 200:
            assert len(response.json()["results"]) == len(sensors)
            if name in ("valid", "camel_case_input"):
                assert response.json()["results"][0]["coverage"]["expectedCount"] == 24
        else:
            assert response.text == "Internal Server Error"
        assert payload == before
        results.append({"scenario": name, "model_errors": errors,
                        "synthetic_http_status": response.status_code, "passed": True})
    verify_sources(args.source)
    print(json.dumps({"original_model_files_unchanged": True,
        "network_denial_control_passed": args.require_network_denial,
        "versions": {name: importlib.metadata.version(name) for name in
                     ["pydantic", "pydantic-core", "fastapi", "starlette", "httpx", "pyhumps"]},
        "boundary": "Original response models in a synthetic FastAPI route; no original router, SQL, middleware or operational API",
        "scenarios": results}, indent=2))


if __name__ == "__main__":
    main()
