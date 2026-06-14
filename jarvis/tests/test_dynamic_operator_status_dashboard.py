import json
import tempfile
import unittest
from pathlib import Path

from jarvis.dynamic_operator_status_dashboard import (
    STATUS_BLOCKED,
    STATUS_READY,
    build_dynamic_operator_status,
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
            "plan_id": "dynamic_operator_status_test_plan",
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
                {"account_id": "emergency", "platform": "bank", "role": "protected_cash", "cash_eur": 3000.0, "holdings": []},
                {"account_id": "spending", "platform": "bank", "role": "daily_spending", "cash_eur": 250.0, "holdings": []},
            ],
        }
    )


def _disabled_bindings() -> Path:
    payload = json.loads(Path(BINDINGS).read_text(encoding="utf-8"))
    payload["bindings"][0]["enabled"] = False
    return _write_json(payload)


class DynamicOperatorStatusDashboardTests(unittest.TestCase):
    def test_tracked_dynamic_chain_is_ready_safe(self) -> None:
        result = build_dynamic_operator_status(
            "20y", _plan(), _snapshot(), POLICY, REGISTRY, BINDINGS, MARKET_DATA
        )

        self.assertEqual(result.status, STATUS_READY)
        self.assertEqual(result.import_plan_status, "DYNAMIC_MARKET_IMPORT_PLAN_READY_SAFE")
        self.assertEqual(result.market_data_intake_status, "DYNAMIC_MARKET_DATA_INTAKE_READY_SAFE")
        self.assertEqual(result.preflight_status, "DYNAMIC_PORTFOLIO_PREFLIGHT_READY_SAFE")
        self.assertEqual(result.optimizer_status, "DYNAMIC_POLICY_READY_SAFE")
        self.assertEqual(result.weekly_plan_status, "DYNAMIC_WEEKLY_PLAN_READY_SAFE")
        self.assertEqual(result.import_ready_rows, 6)
        self.assertEqual(result.intake_ready_series_count, 6)
        self.assertEqual(result.weekly_plan_line_count, 6)
        self.assertTrue(result.manual_approval_required)
        self.assertTrue(result.fetching_forbidden)
        self.assertTrue(result.execution_forbidden)
        self.assertFalse(result.to_dict()["creates_buy_request"])
        self.assertTrue(result.to_dict()["no_trades_executed"])
        self.assertFalse(result.blockers)

    def test_dashboard_blocks_when_import_and_preflight_are_not_ready(self) -> None:
        result = build_dynamic_operator_status(
            "20y", _plan(), _snapshot(), POLICY, REGISTRY, _disabled_bindings(), MARKET_DATA
        )

        self.assertEqual(result.status, STATUS_BLOCKED)
        self.assertTrue(any("import plan is not ready" in blocker for blocker in result.blockers))
        self.assertTrue(any("market data intake is not ready" in blocker for blocker in result.blockers))
        self.assertTrue(any("preflight is not ready" in blocker for blocker in result.blockers))
        self.assertTrue(result.execution_forbidden)


if __name__ == "__main__":
    unittest.main()
