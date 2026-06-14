import json
import tempfile
import unittest
from pathlib import Path

from jarvis.dynamic_market_import_plan import (
    STATUS_BLOCKED,
    STATUS_READY,
    build_dynamic_market_import_plan,
)


REGISTRY = "jarvis/data/dynamic_approved_universe.example.json"
BINDINGS = "jarvis/data/dynamic_market_source_bindings.example.json"


def _write_json(payload: dict) -> Path:
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".json", delete=False) as file:
        json.dump(payload, file)
        return Path(file.name)


def _asset() -> dict:
    return {
        "asset_id": "CORE",
        "name": "CORE name",
        "asset_type": "ETF",
        "sleeve": "global_core",
        "ticker": "CORE",
        "isin_or_symbol": "CORE",
        "platforms": ["Lightyear"],
        "currency": "EUR",
        "domicile": "Ireland",
        "distribution_policy": "accumulating",
        "ter_or_fee": 0.2,
        "data_source": "manual_test",
        "approval_status": "approved_investable",
        "risk_level": "medium",
        "provider": "Provider",
        "index_tracked": "Index",
        "replication_method": "physical",
    }


def _registry() -> Path:
    return _write_json({"assets": [_asset()]})


def _bindings(**overrides) -> Path:
    binding = {
        "asset_id": "CORE",
        "source_provider": "manual_market_fixture",
        "source_symbol": "CORE",
        "cache_series_id": "CORE",
        "expected_currency": "EUR",
        "enabled": True,
    }
    binding.update(overrides)
    return _write_json(
        {
            "binding_pack_id": "test_import_bindings",
            "manual_review_required": True,
            "execution_forbidden": True,
            "fetching_forbidden": True,
            "bindings": [binding],
        }
    )


class DynamicMarketImportPlanTests(unittest.TestCase):
    def test_tracked_dynamic_fixtures_are_ready_safe(self) -> None:
        result = build_dynamic_market_import_plan(REGISTRY, BINDINGS)

        self.assertEqual(result.status, STATUS_READY)
        self.assertEqual(result.source_binding_status, "DYNAMIC_MARKET_SOURCE_BINDING_READY_SAFE")
        self.assertEqual(result.approved_asset_count, 6)
        self.assertEqual(result.ready_row_count, 6)
        self.assertEqual(result.blocked_row_count, 0)
        self.assertTrue(result.fetching_forbidden)
        self.assertTrue(result.execution_forbidden)
        self.assertFalse(result.to_dict()["creates_buy_request"])
        self.assertTrue(result.to_dict()["no_trades_executed"])

    def test_missing_expected_currency_blocks_safely(self) -> None:
        result = build_dynamic_market_import_plan(
            _registry(),
            _bindings(expected_currency=None),
        )

        self.assertEqual(result.status, STATUS_BLOCKED)
        self.assertEqual(result.ready_row_count, 0)
        self.assertEqual(result.blocked_row_count, 1)
        self.assertTrue(any("expected_currency is missing" in blocker for blocker in result.blockers))
        self.assertTrue(result.fetching_forbidden)

    def test_disabled_source_binding_blocks_import_plan(self) -> None:
        result = build_dynamic_market_import_plan(
            _registry(),
            _bindings(enabled=False),
        )

        self.assertEqual(result.status, STATUS_BLOCKED)
        self.assertEqual(result.blocked_row_count, 1)
        self.assertTrue(any("source binding audit is not ready" in blocker for blocker in result.blockers))
        self.assertTrue(result.execution_forbidden)


if __name__ == "__main__":
    unittest.main()
