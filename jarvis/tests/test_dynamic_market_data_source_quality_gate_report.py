import json
import tempfile
import unittest
from pathlib import Path

from jarvis.dynamic_market_data_source_quality_gate_report import (
    report_dynamic_market_data_source_quality,
)


DEFAULT_REGISTRY = "jarvis/data/dynamic_approved_universe.example.json"
DEFAULT_BINDINGS = "jarvis/data/dynamic_market_source_bindings.example.json"
DEFAULT_ENDPOINTS = "jarvis/data/dynamic_public_data_fetcher_endpoints.example.json"
DEFAULT_MARKET_DATA = "jarvis/data/dynamic_market_data.approved_universe.example.json"


def _write_json(payload: dict) -> Path:
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".json", delete=False) as file:
        json.dump(payload, file)
        return Path(file.name)


def _ready_paths() -> tuple[Path, Path, Path, Path]:
    asset_id = "vwce_global_core_candidate"
    registry = _write_json(
        {
            "assets": [
                {
                    "asset_id": asset_id,
                    "name": "VWCE asset",
                    "asset_type": "ETF",
                    "sleeve": "global_core",
                    "ticker": "VWCE",
                    "isin_or_symbol": "IE00BK5BQT80",
                    "platforms": ["Manual Public Source Review"],
                    "currency": "EUR",
                    "domicile": "Ireland",
                    "distribution_policy": "accumulating",
                    "ter_or_fee": 0.22,
                    "data_source": "verified_public_source_reference_for_quality_gate",
                    "approval_status": "approved_investable",
                    "risk_level": "medium",
                    "provider": "Vanguard",
                    "index_tracked": "Index",
                    "replication_method": "physical",
                }
            ]
        }
    )
    bindings = _write_json(
        {
            "binding_pack_id": "report_ready_bindings",
            "manual_review_required": True,
            "execution_forbidden": True,
            "fetching_forbidden": True,
            "bindings": [
                {
                    "asset_id": asset_id,
                    "source_provider": "stooq_public_csv",
                    "source_symbol": "VWCE",
                    "cache_series_id": asset_id,
                    "expected_currency": "EUR",
                    "enabled": True,
                }
            ],
        }
    )
    endpoints = _write_json(
        {
            "endpoint_pack_id": "report_ready_endpoints",
            "manual_review_required": True,
            "authorization_required_before_fetch": True,
            "execution_forbidden": True,
            "endpoints": [
                {
                    "asset_id": asset_id,
                    "source_type": "public_market_data_csv",
                    "source_url": "https://stooq.local.test/market-data/vwce.csv",
                    "update_frequency": "daily",
                    "public_source_only": True,
                    "requires_authentication": False,
                    "requires_credentials": False,
                    "broker_or_trading_api": False,
                    "contains_private_data": False,
                    "cross_check_source": "manual_secondary_public_market_source",
                }
            ],
        }
    )
    market_data = _write_json(
        {
            "as_of": "2026-06-14",
            "base_currency": "EUR",
            "raw_data_unverified": True,
            "execution_forbidden": True,
            "creates_buy_request": False,
            "no_trades_executed": True,
            "series": [
                {
                    "asset_id": asset_id,
                    "currency": "EUR",
                    "prices": [
                        {"date": f"2026-06-{day:02d}", "close": 100.0 + day}
                        for day in range(1, 14)
                    ],
                }
            ],
        }
    )
    return registry, bindings, endpoints, market_data


class DynamicMarketDataSourceQualityGateReportTests(unittest.TestCase):
    def test_default_report_surfaces_blockers_and_safety(self) -> None:
        report = report_dynamic_market_data_source_quality(
            DEFAULT_REGISTRY,
            DEFAULT_BINDINGS,
            DEFAULT_ENDPOINTS,
            DEFAULT_MARKET_DATA,
        )

        self.assertIn("J.A.R.V.I.S. Dynamic Market Data Source Quality Gate", report)
        self.assertIn("status: DYNAMIC_MARKET_DATA_SOURCE_QUALITY_BLOCKED_SAFE", report)
        self.assertIn("approved asset count: 6", report)
        self.assertIn("blocked row count: 6", report)
        self.assertIn("example.com", report)
        self.assertIn("manual_market_fixture", report)
        self.assertIn("synthetic or fixture", report)
        self.assertIn("- no market fetch performed", report)
        self.assertIn("- no broker integration", report)
        self.assertIn("- no buy request created", report)
        self.assertIn("- no approval granted", report)
        self.assertIn("- no execution", report)
        self.assertIn("- no trades executed", report)

    def test_ready_report_prints_rows_and_counts(self) -> None:
        report = report_dynamic_market_data_source_quality(*_ready_paths())

        self.assertIn("status: DYNAMIC_MARKET_DATA_SOURCE_QUALITY_READY_SAFE", report)
        self.assertIn("ready row count: 1", report)
        self.assertIn("blocked row count: 0", report)
        self.assertIn("vwce_global_core_candidate: SOURCE_QUALITY_READY", report)
        self.assertIn("source_provider=stooq_public_csv", report)
        self.assertIn("freshness=FRESH_ENOUGH", report)
        self.assertIn("blockers:\n- none", report)


if __name__ == "__main__":
    unittest.main()
