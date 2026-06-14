import copy
import json
import tempfile
import unittest
from pathlib import Path

from jarvis.dynamic_market_data_intake_validator import (
    STATUS_BLOCKED,
    STATUS_READY,
    validate_dynamic_market_data_intake,
)


REGISTRY = "jarvis/data/dynamic_approved_universe.example.json"
BINDINGS = "jarvis/data/dynamic_market_source_bindings.example.json"
MARKET_DATA = "jarvis/data/dynamic_market_data.approved_universe.example.json"


def _write_json(payload: dict) -> Path:
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".json", delete=False) as file:
        json.dump(payload, file)
        return Path(file.name)


def _market_data_copy(transform) -> Path:
    payload = json.loads(Path(MARKET_DATA).read_text(encoding="utf-8"))
    transform(payload)
    return _write_json(payload)


class DynamicMarketDataIntakeValidatorTests(unittest.TestCase):
    def test_tracked_dynamic_market_data_is_ready_safe(self) -> None:
        result = validate_dynamic_market_data_intake(REGISTRY, BINDINGS, MARKET_DATA)

        self.assertEqual(result.status, STATUS_READY)
        self.assertEqual(result.import_plan_status, "DYNAMIC_MARKET_IMPORT_PLAN_READY_SAFE")
        self.assertEqual(result.expected_series_count, 6)
        self.assertEqual(result.ready_series_count, 6)
        self.assertEqual(result.blocked_series_count, 0)
        self.assertEqual(result.extra_series_count, 0)
        self.assertTrue(all(row.price_count == 13 for row in result.rows))
        self.assertTrue(result.manual_approval_required)
        self.assertTrue(result.fetching_forbidden)
        self.assertTrue(result.execution_forbidden)
        self.assertFalse(result.to_dict()["creates_buy_request"])
        self.assertTrue(result.to_dict()["no_trades_executed"])

    def test_currency_mismatch_blocks_safely(self) -> None:
        def transform(payload: dict) -> None:
            payload["series"][0]["currency"] = "USD"

        result = validate_dynamic_market_data_intake(
            REGISTRY, BINDINGS, _market_data_copy(transform)
        )

        self.assertEqual(result.status, STATUS_BLOCKED)
        self.assertGreaterEqual(result.blocked_series_count, 1)
        self.assertTrue(any("currency mismatch" in blocker for blocker in result.blockers))
        self.assertTrue(result.fetching_forbidden)
        self.assertTrue(result.execution_forbidden)

    def test_duplicate_price_date_blocks_safely(self) -> None:
        def transform(payload: dict) -> None:
            duplicate = copy.deepcopy(payload["series"][0]["prices"][0])
            payload["series"][0]["prices"].append(duplicate)

        result = validate_dynamic_market_data_intake(
            REGISTRY, BINDINGS, _market_data_copy(transform)
        )

        self.assertEqual(result.status, STATUS_BLOCKED)
        self.assertTrue(any("duplicate price date" in blocker for blocker in result.blockers))
        self.assertTrue(result.execution_forbidden)

    def test_extra_series_warns_without_blocking(self) -> None:
        def transform(payload: dict) -> None:
            extra = copy.deepcopy(payload["series"][0])
            extra["asset_id"] = "unexpected_extra_series"
            payload["series"].append(extra)

        result = validate_dynamic_market_data_intake(
            REGISTRY, BINDINGS, _market_data_copy(transform)
        )

        self.assertEqual(result.status, STATUS_READY)
        self.assertEqual(result.extra_series_count, 1)
        self.assertTrue(any("extra series ids" in warning for warning in result.warnings))


if __name__ == "__main__":
    unittest.main()
