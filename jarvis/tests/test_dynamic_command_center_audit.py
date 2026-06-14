import json
import tempfile
import unittest
from pathlib import Path

from jarvis.dynamic_command_center_audit import (
    STATUS_BLOCKED,
    STATUS_READY,
    audit_dynamic_command_center,
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
    return _write_json({
        "plan_id": "command_center_test_plan",
        "created_at": "2026-06-14T20:00:00+00:00",
        "contribution_amount_eur": 250.0,
        "frequency": "weekly",
        "strict_mode": True,
        "manual_approval_required": True,
    })


def _snapshot() -> Path:
    return _write_json({
        "snapshot_date": "2026-06-14",
        "base_currency": "EUR",
        "accounts": [
            {"account_id": "emergency", "platform": "bank", "role": "protected_cash", "cash_eur": 3000.0, "holdings": []},
            {"account_id": "spending", "platform": "bank", "role": "daily_spending", "cash_eur": 250.0, "holdings": []},
        ],
    })


def _disabled_bindings() -> Path:
    payload = json.loads(Path(BINDINGS).read_text(encoding="utf-8"))
    payload["bindings"][0]["enabled"] = False
    return _write_json(payload)


class DynamicCommandCenterAuditTests(unittest.TestCase):
    def test_command_center_is_ready_with_tracked_dynamic_fixtures(self) -> None:
        result = audit_dynamic_command_center(
            "20y", _plan(), _snapshot(), POLICY, REGISTRY, BINDINGS, MARKET_DATA
        )

        self.assertEqual(result.status, STATUS_READY)
        self.assertEqual(result.dashboard_status, "DYNAMIC_OPERATOR_STATUS_READY_SAFE")
        self.assertEqual(result.ready_status_count, 8)
        self.assertEqual(result.required_command_count, 8)
        self.assertFalse(result.blockers)
        self.assertTrue(result.manual_approval_required)
        self.assertTrue(result.fetching_forbidden)
        self.assertTrue(result.execution_forbidden)
        self.assertFalse(result.to_dict()["creates_buy_request"])
        self.assertTrue(result.to_dict()["no_trades_executed"])

    def test_command_center_blocks_when_dashboard_chain_blocks(self) -> None:
        result = audit_dynamic_command_center(
            "20y", _plan(), _snapshot(), POLICY, REGISTRY, _disabled_bindings(), MARKET_DATA
        )

        self.assertEqual(result.status, STATUS_BLOCKED)
        self.assertTrue(any("operator dashboard is not ready" in blocker for blocker in result.blockers))
        self.assertTrue(result.execution_forbidden)


if __name__ == "__main__":
    unittest.main()
