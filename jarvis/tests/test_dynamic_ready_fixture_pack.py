import json
import tempfile
import unittest
from pathlib import Path

from jarvis.dynamic_allocation_optimizer import STATUS_READY, propose_dynamic_allocation
from jarvis.dynamic_allocation_weekly_plan import build_dynamic_weekly_plan
from jarvis.dynamic_market_coverage_audit import STATUS_READY as COVERAGE_READY
from jarvis.dynamic_market_coverage_audit import audit_dynamic_market_coverage


POLICY = "jarvis/data/portfolio_policy.example.json"
REGISTRY = "jarvis/data/dynamic_approved_universe.example.json"
MARKET_DATA = "jarvis/data/dynamic_market_data.approved_universe.example.json"


def _write_json(payload: dict) -> Path:
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".json", delete=False) as file:
        json.dump(payload, file)
        return Path(file.name)


def _plan() -> Path:
    return _write_json(
        {
            "plan_id": "dynamic_ready_fixture_plan",
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


class DynamicReadyFixturePackTests(unittest.TestCase):
    def test_tracked_fixtures_make_market_coverage_ready_safe(self) -> None:
        result = audit_dynamic_market_coverage(REGISTRY, MARKET_DATA)

        self.assertEqual(result.status, COVERAGE_READY)
        self.assertEqual(result.approved_asset_count, 6)
        self.assertEqual(result.covered_asset_count, 6)
        self.assertEqual(result.missing_asset_count, 0)
        self.assertEqual(result.degraded_asset_count, 0)
        self.assertFalse(result.blockers)
        self.assertTrue(result.execution_forbidden)

    def test_tracked_fixtures_make_optimizer_ready_safe(self) -> None:
        result = propose_dynamic_allocation("20y", POLICY, REGISTRY, MARKET_DATA)

        self.assertEqual(result.status, STATUS_READY)
        self.assertEqual(result.approved_asset_count, 6)
        self.assertEqual(result.risk_metric_count, 6)
        self.assertFalse(result.blockers)
        self.assertGreaterEqual(result.proposed_targets["tactical_cash"], 0.05)
        self.assertAlmostEqual(sum(result.proposed_targets.values()), 1.0, places=5)
        self.assertTrue(result.execution_forbidden)

    def test_tracked_fixtures_make_dynamic_weekly_plan_ready_safe(self) -> None:
        result = build_dynamic_weekly_plan(
            horizon="20y",
            plan_path=_plan(),
            snapshot_path=_snapshot(),
            policy_path=POLICY,
            registry_path=REGISTRY,
            market_data_path=MARKET_DATA,
        )

        self.assertEqual(result.status, "DYNAMIC_WEEKLY_PLAN_READY_SAFE")
        self.assertEqual(result.optimizer_result.status, STATUS_READY)
        self.assertEqual(result.contribution_result.status, "DRAFT_PLAN")
        self.assertFalse(result.blockers)
        self.assertGreater(len(result.contribution_result.plan_lines), 0)
        self.assertFalse(result.to_dict()["creates_buy_request"])
        self.assertTrue(result.to_dict()["no_trades_executed"])
        self.assertTrue(result.execution_forbidden)


if __name__ == "__main__":
    unittest.main()
