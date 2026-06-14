import json
import tempfile
import unittest
from pathlib import Path

from jarvis.dynamic_market_coverage_audit_report import report_dynamic_market_coverage_audit


def _write_json(payload: dict) -> Path:
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".json", delete=False) as file:
        json.dump(payload, file)
        return Path(file.name)


def _asset(asset_id: str) -> dict:
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


def _registry() -> Path:
    return _write_json({"assets": [_asset("CORE")]})


def _market_data(asset_ids: list[str]) -> Path:
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
                    "prices": [{"date": date, "close": 100.0 + index * 2.0} for index, date in enumerate(dates)],
                }
                for asset_id in asset_ids
            ],
        }
    )


class DynamicMarketCoverageAuditReportTests(unittest.TestCase):
    def test_report_contains_ready_status_rows_and_safety_boundary(self) -> None:
        report = report_dynamic_market_coverage_audit(
            _registry(),
            _market_data(["CORE"]),
        )

        self.assertIn("J.A.R.V.I.S. Dynamic Market Coverage Audit", report)
        self.assertIn("status: DYNAMIC_MARKET_COVERAGE_READY_SAFE", report)
        self.assertIn("covered asset count: 1", report)
        self.assertIn("CORE / global_core / ETF: MARKET_DATA_READY", report)
        self.assertIn("manual approval required: True", report)
        self.assertIn("execution forbidden: True", report)
        self.assertIn("- no buy request created", report)
        self.assertIn("- no trades executed", report)

    def test_report_surfaces_missing_market_data(self) -> None:
        report = report_dynamic_market_coverage_audit(
            _registry(),
            _market_data(["NOT_APPROVED"]),
        )

        self.assertIn("status: DYNAMIC_MARKET_COVERAGE_PARTIAL_SAFE", report)
        self.assertIn("missing asset count: 1", report)
        self.assertIn("CORE / global_core / ETF: MISSING_MARKET_DATA", report)
        self.assertIn("non-approved asset ids", report)


if __name__ == "__main__":
    unittest.main()
