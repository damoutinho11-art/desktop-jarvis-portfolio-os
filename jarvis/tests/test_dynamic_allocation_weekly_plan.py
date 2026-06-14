import json
import tempfile
import unittest
from pathlib import Path

from jarvis.dynamic_allocation_weekly_plan import build_dynamic_weekly_plan
from jarvis.dynamic_allocation_optimizer import STATUS_PARTIAL


POLICY = "jarvis/data/portfolio_policy.example.json"


def _write_json(payload: dict) -> Path:
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".json", delete=False) as file:
        json.dump(payload, file)
        return Path(file.name)


def _asset(asset_id: str, sleeve: str, asset_type: str = "ETF", risk_level: str = "medium", multi: bool = False) -> dict:
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
        "risk_level": risk_level,
        "multi_asset_allowed": multi,
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
                _asset("GROWTH", "growth_innovation", risk_level="high"),
                _asset("QUALITY", "quality_factor"),
                _asset("BTC", "crypto_core", "crypto", risk_level="high"),
                _asset("HYPE", "speculative_crypto", "crypto", risk_level="very_high", multi=True),
                _asset("TAO", "speculative_crypto", "crypto", risk_level="very_high", multi=True),
            ]
        }
    )


def _plan(amount: float = 250.0, manual: bool = True) -> Path:
    return _write_json(
        {
            "plan_id": "dynamic_weekly_plan_test",
            "created_at": "2026-06-14T20:00:00+00:00",
            "contribution_amount_eur": amount,
            "frequency": "weekly",
            "strict_mode": True,
            "manual_approval_required": manual,
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


def _price_series(asset_id: str) -> dict:
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
    return {
        "asset_id": asset_id,
        "currency": "EUR",
        "prices": [{"date": date, "close": 100.0 + index * 2.0} for index, date in enumerate(dates)],
    }


def _market_data(asset_ids: list[str]) -> Path:
    return _write_json(
        {
            "as_of": "2026-06-14",
            "base_currency": "EUR",
            "series": [_price_series(asset_id) for asset_id in asset_ids],
        }
    )


class DynamicAllocationWeeklyPlanTests(unittest.TestCase):
    def test_partial_optimizer_still_feeds_existing_weekly_planner_safely(self) -> None:
        result = build_dynamic_weekly_plan(
            horizon="20y",
            plan_path=_plan(),
            snapshot_path=_snapshot(),
            policy_path=POLICY,
            registry_path=_registry(),
            market_data_path=_market_data(["NOT_APPROVED"]),
        )

        self.assertEqual(result.status, "DYNAMIC_WEEKLY_PLAN_PARTIAL_SAFE")
        self.assertEqual(result.optimizer_result.status, STATUS_PARTIAL)
        self.assertEqual(result.contribution_result.status, "DRAFT_PLAN")
        self.assertFalse(result.blockers)
        self.assertTrue(result.manual_approval_required)
        self.assertTrue(result.execution_forbidden)
        self.assertFalse(result.to_dict()["creates_buy_request"])
        self.assertTrue(result.to_dict()["no_trades_executed"])
        self.assertGreater(len(result.contribution_result.plan_lines), 0)

    def test_dynamic_targets_respect_policy_minimums_before_planning(self) -> None:
        result = build_dynamic_weekly_plan(
            horizon="20y",
            plan_path=_plan(),
            snapshot_path=_snapshot(),
            policy_path=POLICY,
            registry_path=_registry(),
            market_data_path=_market_data(["NOT_APPROVED"]),
        )

        self.assertGreaterEqual(result.optimizer_result.proposed_targets["tactical_cash"], 0.05)
        self.assertEqual(result.contribution_result.status, "DRAFT_PLAN")
        self.assertFalse(result.blockers)

    def test_blocked_optimizer_does_not_call_weekly_planner(self) -> None:
        result = build_dynamic_weekly_plan(
            horizon="99y",
            plan_path=_plan(),
            snapshot_path=_snapshot(),
            policy_path=POLICY,
            registry_path=_registry(),
        )

        self.assertEqual(result.status, "DYNAMIC_WEEKLY_PLAN_BLOCKED_SAFE")
        self.assertIsNone(result.contribution_result)
        self.assertTrue(any("horizon must be one of" in blocker for blocker in result.blockers))
        self.assertTrue(result.execution_forbidden)

    def test_blocked_contribution_plan_stays_blocked_safely(self) -> None:
        result = build_dynamic_weekly_plan(
            horizon="20y",
            plan_path=_plan(amount=0.0),
            snapshot_path=_snapshot(),
            policy_path=POLICY,
            registry_path=_registry(),
        )

        self.assertEqual(result.status, "DYNAMIC_WEEKLY_PLAN_BLOCKED_SAFE")
        self.assertEqual(result.contribution_result.status, "BLOCKED")
        self.assertTrue(any("contribution_amount_eur must be > 0" in blocker for blocker in result.blockers))
        self.assertTrue(result.execution_forbidden)


if __name__ == "__main__":
    unittest.main()
