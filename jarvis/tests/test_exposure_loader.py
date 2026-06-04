import json
import tempfile
import unittest
from pathlib import Path

from jarvis.exposure_loader import ExposureDataError, load_exposure_data


def _write_exposure(payload: dict) -> Path:
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".json", delete=False) as file:
        json.dump(payload, file)
        return Path(file.name)


def _valid_payload() -> dict:
    return {
        "as_of": "2026-06-04",
        "assets": [
            {
                "asset_id": "asset_a",
                "holdings": [
                    {"name": "Company A", "weight": 0.10},
                    {"name": "Company B", "weight": 0.05},
                    {"name": "Company C", "weight": 0.03},
                ],
                "countries": {"US": 0.70, "IE": 0.10},
                "sectors": {"Technology": 0.30, "Healthcare": 0.10},
            }
        ],
    }


class ExposureLoaderTests(unittest.TestCase):
    def test_valid_exposure_fixture_loads(self) -> None:
        snapshot = load_exposure_data("jarvis/data/asset_exposure.example.json")

        self.assertEqual(snapshot.as_of.isoformat(), "2026-06-04")
        self.assertEqual(len(snapshot.assets), 2)

    def test_invalid_date_rejected(self) -> None:
        payload = _valid_payload()
        payload["as_of"] = "June 4 2026"

        with self.assertRaisesRegex(ExposureDataError, "as_of must be a parseable ISO date"):
            load_exposure_data(_write_exposure(payload))

    def test_negative_weights_rejected(self) -> None:
        payload = _valid_payload()
        payload["assets"][0]["holdings"][0]["weight"] = -0.01

        with self.assertRaisesRegex(ExposureDataError, "holding weight must be non-negative"):
            load_exposure_data(_write_exposure(payload))

    def test_sparse_and_missing_exposure_warnings(self) -> None:
        payload = {
            "as_of": "2026-06-04",
            "assets": [{"asset_id": "asset_sparse", "holdings": [{"name": "Only", "weight": 0.01}]}],
        }

        snapshot = load_exposure_data(_write_exposure(payload))

        self.assertTrue(any("sparse holding" in warning for warning in snapshot.warnings))
        self.assertTrue(any("missing country" in warning for warning in snapshot.warnings))
        self.assertTrue(any("missing sector" in warning for warning in snapshot.warnings))

    def test_weight_sum_above_threshold_warns(self) -> None:
        payload = _valid_payload()
        payload["assets"][0]["countries"] = {"US": 0.80, "IE": 0.30}

        snapshot = load_exposure_data(_write_exposure(payload))

        self.assertTrue(any("materially above 1.05" in warning for warning in snapshot.warnings))


if __name__ == "__main__":
    unittest.main()
