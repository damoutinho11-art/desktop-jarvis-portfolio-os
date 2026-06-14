import json
import tempfile
import unittest
from pathlib import Path

from jarvis.dynamic_bound_market_coverage import (
    STATUS_BLOCKED,
    STATUS_PARTIAL,
    STATUS_READY,
    audit_dynamic_bound_market_coverage,
)


def _write_json(payload: dict) -> Path:
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".json", delete=False) as file:
        json.dump(payload, file)
        return Path(file.name)


def _asset(asset_id: str = "CORE") -> dict:
    return {
        "asset_id": asset_id,
        "name": f"{asset_id} name",
        "asset_type": "ETF",
        "sleeve": "global_core",
        "ticker": asset_id,
        "isin_or_symbol": asset_id,
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


def _registry(*assets: dict) -> Path:
    return _write_json({"assets": list(assets)})


def _binding(asset_id: str = "CORE", cache_series_id: str | None = None, enabled: bool = True) -> dict:
    return {
        "asset_id": asset_id,
        "source_provider": "manual_market_fixture",
        "source_symbol": asset_id,
        "cache_series_id": cache_series_id or asset_id,
        "expected_currency": "EUR",
        "enabled": enabled,
    }


def _bindings(*bindings: dict) -> Path:
    return _write_json(
        {
            "binding_pack_id": "test_bindings",
            "manual_review_required": True,
            "execution_forbidden": True,
            "fetching_forbidden": True,
            "bindings": list(bindings),
        }
    )


def _market_data(*asset_ids: str) -> Path:
    dates = [
        "2025-06-01",
        "2025-07-01",
        "2025-08-01",
        "2025-09-01",
        "2025-10-01",
        "2025-11-01",
        "2025-12-01",
        "2026-01-01",
        "2026-02-01",
        "2026-03-01",
        "2026-04-01",
        "2026-05-01",
        "2026-06-01",
    ]
    return _write_json(
        {
            "as_of": "2026-06-04",
            "base_currency": "EUR",
            "series": [
                {
                    "asset_id": asset_id,
                    "currency": "EUR",
                    "prices": [
                        {"date": date, "close": 100.0 + index * 2.0}
                        for index, date in enumerate(dates)
                    ],
                }
                for asset_id in asset_ids
            ],
        }
    )


class DynamicBoundMarketCoverageTests(unittest.TestCase):
    def test_ready_when_binding_and_market_series_match(self) -> None:
        result = audit_dynamic_bound_market_coverage(
            _registry(_asset("CORE")),
            _bindings(_binding("CORE")),
            _market_data("CORE"),
        )

        self.assertEqual(result.status, STATUS_READY)
        self.assertEqual(result.bound_series_ready_count, 1)
        self.assertEqual(result.missing_bound_series_count, 0)
        self.assertEqual(result.blocked_binding_count, 0)
        self.assertFalse(result.blockers)
        self.assertTrue(result.manual_approval_required)
        self.assertTrue(result.execution_forbidden)
        self.assertFalse(result.to_dict()["creates_buy_request"])
        self.assertTrue(result.to_dict()["no_trades_executed"])

    def test_blocked_when_binding_cache_series_missing_from_market_data(self) -> None:
        result = audit_dynamic_bound_market_coverage(
            _registry(_asset("CORE")),
            _bindings(_binding("CORE", cache_series_id="CORE_MISSING")),
            _market_data("CORE"),
        )

        self.assertEqual(result.status, STATUS_BLOCKED)
        self.assertEqual(result.missing_bound_series_count, 1)
        self.assertTrue(
            any("bound cache_series_id is not present" in blocker for blocker in result.blockers)
        )

    def test_blocked_when_binding_itself_is_not_ready(self) -> None:
        result = audit_dynamic_bound_market_coverage(
            _registry(_asset("CORE")),
            _bindings(_binding("CORE", enabled=False)),
            _market_data("CORE"),
        )

        self.assertEqual(result.status, STATUS_BLOCKED)
        self.assertEqual(result.blocked_binding_count, 1)
        self.assertTrue(any("source binding audit is not ready" in blocker for blocker in result.blockers))

    def test_partial_when_one_bound_series_ready_and_one_missing(self) -> None:
        result = audit_dynamic_bound_market_coverage(
            _registry(_asset("CORE"), _asset("GROWTH")),
            _bindings(_binding("CORE"), _binding("GROWTH", cache_series_id="GROWTH_MISSING")),
            _market_data("CORE"),
        )

        self.assertEqual(result.status, STATUS_PARTIAL)
        self.assertEqual(result.bound_series_ready_count, 1)
        self.assertEqual(result.missing_bound_series_count, 1)


if __name__ == "__main__":
    unittest.main()

