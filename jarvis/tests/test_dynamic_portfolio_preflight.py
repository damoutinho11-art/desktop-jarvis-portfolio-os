import json
import tempfile
import unittest
from pathlib import Path

from jarvis.dynamic_portfolio_preflight import (
    STATUS_BLOCKED,
    STATUS_READY,
    run_dynamic_portfolio_preflight,
)


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
            "plan_id": "dynamic_preflight_test_plan",
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


def _disabled_binding_fixture() -> Path:
    payload = json.loads(Path(BINDINGS).read_text(encoding="utf-8"))
    payload["bindings"][0]["enabled"] = False
    return _write_json(payload)


class DynamicPortfolioPreflightTests(unittest.TestCase):
    def test_ready_preflight_with_tracked_dynamic_fixtures(self) -> None:
        result = run_dynamic_portfolio_preflight(
            horizon="20y",
            plan_path=_plan(),
            snapshot_path=_snapshot(),
            policy_path=POLICY,
            registry_path=REGISTRY,
            binding_path=BINDINGS,
            market_data_path=MARKET_DATA,
        )

        self.assertEqual(result.status, STATUS_READY)
        self.assertEqual(result.bound_market_status, "DYNAMIC_BOUND_MARKET_COVERAGE_READY_SAFE")
        self.assertEqual(result.binding_status, "DYNAMIC_MARKET_SOURCE_BINDING_READY_SAFE")
        self.assertEqual(result.coverage_status, "DYNAMIC_MARKET_COVERAGE_READY_SAFE")
        self.assertEqual(result.weekly_plan_status, "DYNAMIC_WEEKLY_PLAN_READY_SAFE")
        self.assertEqual(result.optimizer_status, "DYNAMIC_POLICY_READY_SAFE")
        self.assertEqual(result.contribution_status, "DRAFT_PLAN")
        self.assertFalse(result.blockers)
        self.assertGreater(len(result.weekly_plan_lines), 0)
        self.assertTrue(all(line["sleeve"] for line in result.weekly_plan_lines))
        self.assertTrue(result.manual_approval_required)
        self.assertTrue(result.execution_forbidden)
        self.assertFalse(result.to_dict()["creates_buy_request"])
        self.assertTrue(result.to_dict()["no_trades_executed"])

    def test_preflight_blocks_when_bound_market_binding_is_not_ready(self) -> None:
        result = run_dynamic_portfolio_preflight(
            horizon="20y",
            plan_path=_plan(),
            snapshot_path=_snapshot(),
            policy_path=POLICY,
            registry_path=REGISTRY,
            binding_path=_disabled_binding_fixture(),
            market_data_path=MARKET_DATA,
        )

        self.assertEqual(result.status, STATUS_BLOCKED)
        self.assertEqual(result.weekly_plan_status, "DYNAMIC_WEEKLY_PLAN_READY_SAFE")
        self.assertTrue(any("bound market coverage is not ready" in blocker for blocker in result.blockers))
        self.assertTrue(result.execution_forbidden)


if __name__ == "__main__":
    unittest.main()
