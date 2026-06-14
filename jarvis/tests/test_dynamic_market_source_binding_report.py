import json
import tempfile
import unittest
from pathlib import Path

from jarvis.dynamic_market_source_binding_report import report_dynamic_market_source_bindings


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


def _bindings(enabled: bool = True) -> Path:
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
                    "cache_series_id": "CORE",
                    "expected_currency": "EUR",
                    "enabled": enabled,
                }
            ],
        }
    )


class DynamicMarketSourceBindingReportTests(unittest.TestCase):
    def test_report_contains_ready_rows_and_safety_boundary(self) -> None:
        report = report_dynamic_market_source_bindings(_registry(), _bindings())

        self.assertIn("J.A.R.V.I.S. Dynamic Market Source Binding Audit", report)
        self.assertIn("status: DYNAMIC_MARKET_SOURCE_BINDING_READY_SAFE", report)
        self.assertIn("ready binding count: 1", report)
        self.assertIn("CORE / global_core / ETF: BINDING_READY", report)
        self.assertIn("- no market fetch performed", report)
        self.assertIn("- no trades executed", report)

    def test_report_surfaces_blocked_binding(self) -> None:
        report = report_dynamic_market_source_bindings(_registry(), _bindings(enabled=False))

        self.assertIn("status: DYNAMIC_MARKET_SOURCE_BINDING_BLOCKED_SAFE", report)
        self.assertIn("binding is not enabled", report)
        self.assertIn("- no execution", report)


if __name__ == "__main__":
    unittest.main()
