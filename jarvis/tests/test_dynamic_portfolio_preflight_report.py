import json
import tempfile
import unittest
from pathlib import Path

from jarvis.dynamic_portfolio_preflight_report import report_dynamic_portfolio_preflight


POLICY = "jarvis/data/portfolio_policy.example.json"
REGISTRY = "jarvis/data/dynamic_approved_universe.example.json"
BINDINGS = "jarvis/data/dynamic_market_source_bindings.example.json"
MARKET_DATA = "jarvis/data/dynamic_market_data.approved_universe.example.json"


def _write_json(payload: dict) -> Path:
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".json", delete=False) as file:
        json.dump(payload, file)
        return Path(file.name)


def _plan() -> Path:
    return _write_json(
        {
            "plan_id": "dynamic_preflight_report_test_plan",
            "created_at": "2026-06-14T20:00:00+00:00",
            "contribution_amount_eur": 250.0,
            "frequency": "weekly",
            "strict_mode": True,
            "manual_approval_required": True,
        }
    )


def _snapshot() -> Path:
    return _write_json(
        {
            "snapshot_date": "2026-06-14",
            "base_currency": "EUR",
            "accounts": [
                {
                    "account_id": "emergency_fund",
                    "platform": "bank",
                    "role": "protected_cash",
                    "cash_eur": 3000.0,
                    "holdings": [],
                },
                {
                    "account_id": "daily_spending",
                    "platform": "bank",
                    "role": "daily_spending",
                    "cash_eur": 250.0,
                    "holdings": [],
                },
            ],
        }
    )


class DynamicPortfolioPreflightReportTests(unittest.TestCase):
    def test_report_contains_ready_chain_plan_lines_and_safety_boundary(self) -> None:
        report = report_dynamic_portfolio_preflight(
            horizon="20y",
            plan_path=_plan(),
            snapshot_path=_snapshot(),
            policy_path=POLICY,
            registry_path=REGISTRY,
            binding_path=BINDINGS,
            market_data_path=MARKET_DATA,
        )

        self.assertIn("J.A.R.V.I.S. Dynamic Portfolio Preflight", report)
        self.assertIn("status: DYNAMIC_PORTFOLIO_PREFLIGHT_READY_SAFE", report)
        self.assertIn("bound market status: DYNAMIC_BOUND_MARKET_COVERAGE_READY_SAFE", report)
        self.assertIn("weekly plan status: DYNAMIC_WEEKLY_PLAN_READY_SAFE", report)
        self.assertIn("optimizer status: DYNAMIC_POLICY_READY_SAFE", report)
        self.assertIn("global_core / vwce_global_core_candidate / Lightyear", report)
        self.assertNotIn("None / vwce_global_core_candidate", report)
        self.assertIn("- no market fetch performed", report)
        self.assertIn("- no trades executed", report)


if __name__ == "__main__":
    unittest.main()
