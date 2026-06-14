import json
import tempfile
import unittest
from pathlib import Path

from jarvis.dynamic_allocation_optimizer_report import report_dynamic_allocation_optimizer


POLICY = "jarvis/data/portfolio_policy.example.json"


def _write_json(payload: dict) -> Path:
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".json", delete=False) as file:
        json.dump(payload, file)
        return Path(file.name)


def _asset(asset_id: str, sleeve: str, asset_type: str = "ETF") -> dict:
    asset = {
        "asset_id": asset_id,
        "name": f"{asset_id} name",
        "asset_type": asset_type,
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
    }
    if asset_type == "ETF":
        asset.update(
            {
                "provider": "Provider",
                "index_tracked": "Index",
                "replication_method": "physical",
            }
        )
    if asset_type == "crypto":
        asset.update(
            {
                "network_or_protocol": "Protocol",
                "custody_platforms": ["LHV Crypto Investments"],
                "transferable": False,
                "mica_route_possible": True,
            }
        )
    return asset


def _registry() -> Path:
    return _write_json(
        {
            "assets": [
                _asset("CORE", "global_core"),
                _asset("GROWTH", "growth_innovation"),
                _asset("QUALITY", "quality_factor"),
                _asset("BTC", "crypto_core", "crypto"),
                _asset("SPEC", "speculative_crypto", "crypto"),
            ]
        }
    )


class DynamicAllocationOptimizerReportTests(unittest.TestCase):
    def test_report_contains_status_targets_and_safety_boundary(self) -> None:
        report = report_dynamic_allocation_optimizer("20y", POLICY, _registry())

        self.assertIn("J.A.R.V.I.S. Dynamic Allocation Optimizer Report", report)
        self.assertIn("status: DYNAMIC_POLICY_PARTIAL_SAFE", report)
        self.assertIn("baseline targets:", report)
        self.assertIn("proposed dynamic targets:", report)
        self.assertIn("manual approval required: True", report)
        self.assertIn("execution forbidden: True", report)
        self.assertIn("- no buy request created", report)
        self.assertIn("- no trades executed", report)

    def test_report_blocks_unknown_horizon_safely(self) -> None:
        report = report_dynamic_allocation_optimizer("99y", POLICY, _registry())

        self.assertIn("status: DYNAMIC_POLICY_BLOCKED_SAFE", report)
        self.assertIn("horizon must be one of: 5y, 10y, 20y", report)
        self.assertIn("- no execution", report)


if __name__ == "__main__":
    unittest.main()
