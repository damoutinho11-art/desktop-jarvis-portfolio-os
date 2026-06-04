import json
import tempfile
import unittest
from pathlib import Path

from jarvis.approved_universe import build_approved_universe
from jarvis.portfolio_policy import (
    PortfolioPolicyError,
    load_portfolio_policy,
    validate_policy_against_approved_universe,
)


def _write_json(payload: dict) -> Path:
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".json", delete=False) as file:
        json.dump(payload, file)
        return Path(file.name)


def _policy(**overrides) -> dict:
    policy = json.loads(Path("jarvis/data/portfolio_policy.example.json").read_text(encoding="utf-8"))
    policy.update(overrides)
    return policy


def _approved_asset(asset_id="core_asset", sleeve="global_core", status="approved_investable") -> dict:
    return {
        "asset_id": asset_id,
        "name": f"{asset_id} name",
        "asset_type": "ETF",
        "sleeve": sleeve,
        "ticker": "ETF",
        "isin_or_symbol": "IE00TEST0001",
        "platforms": ["Lightyear"],
        "currency": "EUR",
        "domicile": "Ireland",
        "distribution_policy": "accumulating",
        "ter_or_fee": 0.2,
        "data_source": "manual_test",
        "approval_status": status,
        "risk_level": "medium",
        "provider": "Provider",
        "index_tracked": "Index",
        "replication_method": "physical",
    }


class PortfolioPolicyTests(unittest.TestCase):
    def test_valid_policy_loads(self) -> None:
        policy = load_portfolio_policy("jarvis/data/portfolio_policy.example.json")

        self.assertEqual(policy.base_currency, "EUR")
        self.assertTrue(policy.manual_approval_required)

    def test_target_weights_must_sum_to_one(self) -> None:
        policy = _policy()
        policy["sleeves"][0]["target_weight"] = 0.40

        with self.assertRaisesRegex(PortfolioPolicyError, "target weights must sum"):
            load_portfolio_policy(_write_json(policy))

    def test_invalid_min_target_max_rejected(self) -> None:
        policy = _policy()
        policy["sleeves"][0]["min_weight"] = 0.50

        with self.assertRaisesRegex(PortfolioPolicyError, "min_weight <= target_weight <= max_weight"):
            load_portfolio_policy(_write_json(policy))

    def test_duplicate_sleeve_rejected(self) -> None:
        policy = _policy()
        policy["sleeves"][1]["sleeve_id"] = policy["sleeves"][0]["sleeve_id"]

        with self.assertRaisesRegex(PortfolioPolicyError, "sleeve_id values must be unique"):
            load_portfolio_policy(_write_json(policy))

    def test_manual_approval_required_false_rejected(self) -> None:
        with self.assertRaisesRegex(PortfolioPolicyError, "manual_approval_required must be true"):
            load_portfolio_policy(_write_json(_policy(manual_approval_required=False)))

    def test_no_leverage_false_rejected(self) -> None:
        policy = _policy()
        policy["constraints"]["no_leverage"] = False

        with self.assertRaisesRegex(PortfolioPolicyError, "no_leverage must be true"):
            load_portfolio_policy(_write_json(policy))

    def test_no_auto_execution_false_rejected(self) -> None:
        policy = _policy()
        policy["constraints"]["no_auto_execution"] = False

        with self.assertRaisesRegex(PortfolioPolicyError, "no_auto_execution must be true"):
            load_portfolio_policy(_write_json(policy))

    def test_crypto_cap_above_limit_rejected(self) -> None:
        policy = _policy()
        policy["constraints"]["max_total_crypto_weight"] = 0.30

        with self.assertRaisesRegex(PortfolioPolicyError, "max_total_crypto_weight"):
            load_portfolio_policy(_write_json(policy))

    def test_required_sleeve_missing_approved_asset_blocks_allocation_readiness(self) -> None:
        policy = load_portfolio_policy("jarvis/data/portfolio_policy.example.json")
        universe = build_approved_universe(_write_json({"assets": []}), etf_universe_expected=False, crypto_universe_expected=False)

        result = validate_policy_against_approved_universe(policy, universe)

        self.assertFalse(result.allocation_ready)
        self.assertTrue(any("required sleeve global_core" in blocker for blocker in result.blockers))

    def test_empty_approved_universe_blocks_allocation_readiness(self) -> None:
        policy = load_portfolio_policy("jarvis/data/portfolio_policy.example.json")
        universe = build_approved_universe(
            _write_json({"assets": [_approved_asset(status="candidate_unreviewed")]}),
            etf_universe_expected=False,
            crypto_universe_expected=False,
        )

        result = validate_policy_against_approved_universe(policy, universe)

        self.assertFalse(result.allocation_ready)
        self.assertIn("approved universe is empty.", result.blockers)

    def test_approved_asset_matching_sleeve_passes_coverage_check(self) -> None:
        policy = load_portfolio_policy("jarvis/data/portfolio_policy.example.json")
        universe = build_approved_universe(
            _write_json({"assets": [_approved_asset()]}),
            etf_universe_expected=False,
            crypto_universe_expected=False,
        )

        result = validate_policy_against_approved_universe(policy, universe)

        self.assertTrue(result.allocation_ready)


if __name__ == "__main__":
    unittest.main()
