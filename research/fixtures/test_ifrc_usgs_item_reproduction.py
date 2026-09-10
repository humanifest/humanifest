"""Reproduce current USGS economic item values using the real transformer.

Run with the pinned checkout's locked environment, pytest-recording's
--block-network --record-mode=none, and HUMANIFEST_IFRC_CHECKOUT set to it.
This confirms the existing behavior; it is not the proposed fix's acceptance test.
"""

import hashlib
import json
import os
import sys
from pathlib import Path

import pytest

ROOT = Path(os.environ["HUMANIFEST_IFRC_CHECKOUT"]).resolve()
source = ROOT / "pystac_monty/sources/usgs.py"
assert hashlib.sha256(source.read_bytes()).hexdigest() == (
    "e30b4bf9ecfe2eef9ccfe9c9da86af5e1dc0e660d5b6867f5b2df188e628a680"
), "Expected pinned unmodified transformer"
sys.path.insert(0, str(ROOT))

from pystac_monty.geocoding import WorldAdministrativeBoundariesGeocoder  # noqa: E402
from pystac_monty.sources.common import File, USGSDataSourceType  # noqa: E402
from pystac_monty.sources.gdacs import DataType  # noqa: E402
from pystac_monty.sources.usgs import USGSDataSource, USGSTransformer  # noqa: E402


@pytest.mark.parametrize(
    "lower,upper,current_value,scaled_before_rounding",
    [(0, 1, 0, 500_000), (1, 10, 5_000_000, 5_500_000), (0, 2, 1_000_000, 1_000_000)],
)
def test_current_economic_item_value(tmp_path, lower, upper, current_value, scaled_before_rounding):
    alert_data = json.loads((ROOT / "tests/data/usgs/venezuela_alerts.json").read_text())
    # Synthetic probability mass in one finite bin, expressed in millions USD.
    alert_data[0]["economic"]["bins"] = [
        {"color": "green", "min": lower, "max": upper, "probability": 1.0},
    ]
    alerts = tmp_path / "synthetic-alerts.json"
    alerts.write_text(json.dumps(alert_data))
    event = ROOT / "tests/data/usgs/venezuela_details.json"
    data_source = USGSDataSource(data=USGSDataSourceType(
        source_url=str(event),
        event_data=File(path=str(event), data_type=DataType.FILE),
        alerts_data=File(path=str(alerts), data_type=DataType.FILE),
    ))
    geocoder = WorldAdministrativeBoundariesGeocoder(
        str(ROOT / "tests/data-files/world-administrative-boundaries.fgb"), 0.1,
    )
    # Exercise validation of input models, event/hazard creation, impact creation
    # and output serialization. No external STAC schema validation is requested.
    documents = [item.to_dict() for item in USGSTransformer(data_source, geocoder).get_stac_items()]
    assert len(documents) == 4
    impacts = [doc for doc in documents if doc["properties"]["roles"] == ["source", "impact"]]
    assert len(impacts) == 2
    by_unit = {doc["properties"]["monty:impact_detail"]["unit"]: doc for doc in impacts}
    economic = by_unit["usd"]["properties"]["monty:impact_detail"]
    fatality = by_unit["people"]["properties"]["monty:impact_detail"]
    assert economic["value"] == current_value
    assert fatality["value"] == 139  # Existing fixture: 1.65 + 27.5 + 110, truncated.
    assert by_unit["usd"]["properties"]["monty:country_codes"] == ["VEN"]
    assert scaled_before_rounding - economic["value"] in {0, 500_000}
    print(json.dumps({"bin_million_usd": [lower, upper], "emitted_usd": economic["value"],
                      "scale_before_rounding_usd": scaled_before_rounding,
                      "fatality_control": fatality["value"]}))
