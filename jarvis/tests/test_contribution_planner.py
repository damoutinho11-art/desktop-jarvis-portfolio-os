import json
import tempfile
import unittest
from pathlib import Path

from jarvis.contribution_planner import parse_contribution_plan, plan_contribution


def _write_json(payload: dict) -> Path:
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".json", delete=False) as file:
        json.dump(payload, file)
        return Path(file.name)


def _plan(amount=100.0, manual=True):
    return parse_contribution_plan(
        {
            "plan_id": "plan",
            "created_at": "2026-06-04T11:00:00+00:00",
            "contribution_amount_eur": amount,
            "frequency": "weekly",
            "strict_mode": True,
            "manual_approval_required": manual,
        }
    )


def _snapshot(holdings=None, emergency=0.0, daily=0.0) -> Path:
    accounts = []
    if emergency:
        accounts.append({"account_id": "emergency_fund", "platform": "bank", "role": "protected_cash", "cash_eur": emergency, "holdings": []})
    if daily:
        accounts.append({"account_id": "daily_spending", "platform": "bank", "role": "daily_spending", "cash_eur": daily, "holdings": []})
    accounts.append({"account_id": "lightyear", "platform": "Lightyear", "role": "ETF_engine", "cash_eur": 0.0, "holdings": holdings or []})
    return _write_json({"snapshot_date": "2026-06-04", "base_currency": "EUR", "accounts": accounts})


def _holding(symbol, value, asset_class="etf"):
    return {"asset_symbol": symbol, "asset_class": asset_class, "market_value_eur": value}


def _asset(asset_id, sleeve="global_core", status="approved_investable", multi=False, asset_type="ETF"):
    asset = {
        "asset_id": asset_id,
        "name": asset_id,
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
        "approval_status": status,
        "risk_level": "medium",
        "multi_asset_allowed": multi,
    }
    if asset_type == "ETF":
        asset.update({"provider": "Provider", "index_tracked": "Index", "replication_method": "physical"})
    if asset_type == "cash":
        asset["asset_type"] = "cash"
    return asset


def _registry(*assets):
    return _write_json({"assets": list(assets)})


POLICY = "jarvis/data/portfolio_policy.example.json"


class ContributionPlannerTests(unittest.TestCase):
    def test_blocked_when_approved_universe_empty(self) -> None:
        result = plan_contribution(_plan(), _snapshot(), POLICY, _registry())

        self.assertEqual(result.status, "BLOCKED")
        self.assertIn("approved universe is empty.", result.blockers)
        self.assertEqual(result.plan_lines, ())

    def test_blocked_when_drift_allocation_ready_false(self) -> None:
        result = plan_contribution(_plan(), _snapshot([_holding("MYSTERY", 10.0)]), POLICY, _registry(_asset("global_core_etf")))

        self.assertEqual(result.status, "BLOCKED")
        self.assertIn("portfolio drift allocation_ready is false.", result.blockers)

    def test_blocked_when_contribution_amount_not_positive(self) -> None:
        result = plan_contribution(_plan(0.0), _snapshot([_holding("global_core_etf", 10.0)]), POLICY, _registry(_asset("global_core_etf")))

        self.assertEqual(result.status, "BLOCKED")
        self.assertIn("contribution_amount_eur must be > 0.", result.blockers)

    def test_protected_and_daily_cash_are_not_used(self) -> None:
        result = plan_contribution(
            _plan(50.0),
            _snapshot([_holding("global_core_etf", 10.0)], emergency=3000.0, daily=500.0),
            POLICY,
            _registry(_asset("global_core_etf")),
        )

        self.assertLessEqual(sum(line.amount_eur for line in result.plan_lines), 50.0)

    def test_planner_uses_only_new_contribution_amount(self) -> None:
        result = plan_contribution(_plan(25.0), _snapshot([_holding("global_core_etf", 1000.0)]), POLICY, _registry(_asset("global_core_etf")))

        self.assertLessEqual(sum(line.amount_eur for line in result.plan_lines), 25.0)

    def test_approved_asset_receives_contribution(self) -> None:
        result = plan_contribution(
            _plan(100.0),
            _snapshot([_holding("global_core_etf", 10.0), _holding("EUR", 90.0, "cash")]),
            POLICY,
            _registry(_asset("global_core_etf"), _asset("EUR", "tactical_cash", asset_type="cash")),
        )

        self.assertEqual(result.status, "DRAFT_PLAN")
        self.assertEqual(result.plan_lines[0].asset_id, "global_core_etf")

    def test_sleeve_above_max_receives_no_contribution(self) -> None:
        result = plan_contribution(_plan(100.0), _snapshot([_holding("global_core_etf", 100.0)]), POLICY, _registry(_asset("global_core_etf")))

        self.assertEqual(result.status, "BLOCKED")
        self.assertEqual(result.plan_lines, ())

    def test_required_underweight_sleeve_prioritized(self) -> None:
        result = plan_contribution(
            _plan(100.0),
            _snapshot([_holding("global_core_etf", 10.0), _holding("EUR", 90.0, "cash")]),
            POLICY,
            _registry(_asset("global_core_etf"), _asset("EUR", "tactical_cash", asset_type="cash")),
        )

        self.assertEqual(result.status, "DRAFT_PLAN")
        self.assertEqual(result.plan_lines[0].sleeve_id, "global_core")

    def test_multiple_assets_same_sleeve_blocked_unless_allowed(self) -> None:
        blocked = plan_contribution(
            _plan(100.0),
            _snapshot([_holding("global_core_etf", 10.0), _holding("EUR", 90.0, "cash")]),
            POLICY,
            _registry(_asset("global_core_etf"), _asset("quality_etf", "global_core"), _asset("EUR", "tactical_cash", asset_type="cash")),
        )
        allowed = plan_contribution(
            _plan(100.0),
            _snapshot([_holding("global_core_etf", 10.0), _holding("EUR", 90.0, "cash")]),
            POLICY,
            _registry(
                _asset("global_core_etf", multi=True),
                _asset("quality_etf", "global_core", multi=True),
                _asset("EUR", "tactical_cash", asset_type="cash"),
            ),
        )

        self.assertEqual(blocked.status, "BLOCKED")
        self.assertTrue(any("multiple approved assets" in blocker for blocker in blocked.blockers))
        self.assertEqual(allowed.status, "DRAFT_PLAN")
        self.assertEqual(len(allowed.plan_lines), 2)

    def test_draft_plan_never_creates_buy_request(self) -> None:
        result = plan_contribution(
            _plan(100.0),
            _snapshot([_holding("global_core_etf", 10.0), _holding("EUR", 90.0, "cash")]),
            POLICY,
            _registry(_asset("global_core_etf"), _asset("EUR", "tactical_cash", asset_type="cash")),
        )

        self.assertEqual(result.status, "DRAFT_PLAN")
        self.assertFalse(result.creates_buy_request)

    def test_manual_approval_required_false_rejected(self) -> None:
        result = plan_contribution(
            _plan(100.0, manual=False),
            _snapshot([_holding("global_core_etf", 10.0), _holding("EUR", 90.0, "cash")]),
            POLICY,
            _registry(_asset("global_core_etf"), _asset("EUR", "tactical_cash", asset_type="cash")),
        )

        self.assertEqual(result.status, "BLOCKED")
        self.assertIn("manual_approval_required must be true.", result.blockers)


if __name__ == "__main__":
    unittest.main()
