import json
import tempfile
import unittest
from pathlib import Path

from jarvis.dynamic_market_coverage_audit import (
    STATUS_BLOCKED,
    STATUS_PARTIAL,
    STATUS_READY,
    audit_dynamic_market_coverage,
)


def _write_json(payload: dict) -> Path:
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".json", delete=False) as file:
        json.dump(payload, file)
        return Path(file.name)


def _asset(asset_id: str, sleeve: str = "global_core") -> dict:
    return {
        "asset_id": asset_id,
        "name": f"{asset_id} name",
        "asset_type": "ETF",
        "sleeve": sleeve,
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


def _price_series(asset_id: str, dates: list[str] | None = None) -> dict:
    dates = dates or [
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
    return {
        "asset_id": asset_id,
        "currency": "EUR",
        "prices": [{"date": date, "close": 100.0 + index * 2.0} for index, date in enumerate(dates)],
    }


def _market_data(asset_ids: list[str], as_of: str = "2026-06-04", short: bool = False) -> Path:
    dates = ["2026-06-01", "2026-06-02"] if short else None
    return _write_json(
        {
            "as_of": as_of,
            "base_currency": "EUR",
            "series": [_price_series(asset_id, dates=dates) for asset_id in asset_ids],
        }
    )


class DynamicMarketCoverageAuditTests(unittest.TestCase):
    def test_missing_market_data_is_partial_safe(self) -> None:
        result = audit_dynamic_market_coverage(
            _registry(_asset("CORE")),
            _market_data(["NOT_APPROVED"]),
        )

        self.assertEqual(result.status, STATUS_PARTIAL)
        self.assertEqual(result.approved_asset_count, 1)
        self.assertEqual(result.covered_asset_count, 0)
        self.assertEqual(result.missing_asset_count, 1)
        self.assertEqual(result.rows[0].status, "MISSING_MARKET_DATA")
        self.assertTrue(any("non-approved asset ids" in warning for warning in result.warnings))
        self.assertTrue(result.execution_forbidden)

    def test_complete_matching_market_data_is_ready_safe(self) -> None:
        result = audit_dynamic_market_coverage(
            _registry(_asset("CORE"), _asset("QUALITY", "quality_factor")),
            _market_data(["CORE", "QUALITY"]),
        )

        self.assertEqual(result.status, STATUS_READY)
        self.assertEqual(result.covered_asset_count, 2)
        self.assertEqual(result.missing_asset_count, 0)
        self.assertEqual(result.degraded_asset_count, 0)
        self.assertTrue(all(row.metric_ready for row in result.rows))
        self.assertFalse(result.blockers)

    def test_degraded_market_data_is_partial_safe(self) -> None:
        result = audit_dynamic_market_coverage(
            _registry(_asset("CORE")),
            _market_data(["CORE"], short=True),
        )

        self.assertEqual(result.status, STATUS_PARTIAL)
        self.assertEqual(result.covered_asset_count, 1)
        self.assertEqual(result.degraded_asset_count, 1)
        self.assertEqual(result.rows[0].status, "DEGRADED_MARKET_DATA")
        self.assertFalse(result.rows[0].metric_ready)

    def test_empty_approved_universe_blocks_safely(self) -> None:
        result = audit_dynamic_market_coverage(
            _registry(),
            _market_data(["CORE"]),
        )

        self.assertEqual(result.status, STATUS_BLOCKED)
        self.assertIn("approved universe is empty.", result.blockers)
        self.assertTrue(result.manual_approval_required)
        self.assertTrue(result.execution_forbidden)


if __name__ == "__main__":
    unittest.main()
