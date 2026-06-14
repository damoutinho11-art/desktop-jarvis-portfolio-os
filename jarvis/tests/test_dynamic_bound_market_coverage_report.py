import json
import tempfile
import unittest
from pathlib import Path

from jarvis.dynamic_bound_market_coverage_report import report_dynamic_bound_market_coverage


def _write_json(payload: dict) -> Path:
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".json", delete=False) as file:
        json.dump(payload, file)
        return Path(file.name)


def _registry() -> Path:
    return _write_json(
        {
            "assets": [
                {
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
            ]
        }
    )


def _bindings(cache_series_id: str = "CORE") -> Path:
    return _write_json(
        {
            "binding_pack_id": "report_test_bindings",
            "manual_review_required": True,
            "execution_forbidden": True,
            "fetching_forbidden": True,
            "bindings": [
                {
                    "asset_id": "CORE",
                    "source_provider": "manual_market_fixture",
                    "source_symbol": "CORE",
                    "cache_series_id": cache_series_id,
                    "expected_currency": "EUR",
                    "enabled": True,
                }
            ],
        }
    )


def _market_data(asset_id: str = "CORE") -> Path:
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
            ],
        }
    )


class DynamicBoundMarketCoverageReportTests(unittest.TestCase):
    def test_report_contains_ready_status_rows_and_safety_boundary(self) -> None:
        report = report_dynamic_bound_market_coverage(
            _registry(),
            _bindings(),
            _market_data(),
        )

        self.assertIn("J.A.R.V.I.S. Dynamic Bound Market Coverage Bridge", report)
        self.assertIn("status: DYNAMIC_BOUND_MARKET_COVERAGE_READY_SAFE", report)
        self.assertIn("binding status: DYNAMIC_MARKET_SOURCE_BINDING_READY_SAFE", report)
        self.assertIn("coverage status: DYNAMIC_MARKET_COVERAGE_READY_SAFE", report)
        self.assertIn("CORE / global_core / ETF: BOUND_MARKET_SERIES_READY", report)
        self.assertIn("- no market fetch performed", report)
        self.assertIn("- no trades executed", report)

    def test_report_surfaces_missing_bound_series(self) -> None:
        report = report_dynamic_bound_market_coverage(
            _registry(),
            _bindings(cache_series_id="MISSING"),
            _market_data(),
        )

        self.assertIn("status: DYNAMIC_BOUND_MARKET_COVERAGE_BLOCKED_SAFE", report)
        self.assertIn("MISSING_BOUND_MARKET_SERIES", report)
        self.assertIn("bound cache_series_id is not present", report)
        self.assertIn("- no execution", report)


if __name__ == "__main__":
    unittest.main()
