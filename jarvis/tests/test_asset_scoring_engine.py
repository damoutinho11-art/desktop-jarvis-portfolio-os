import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from jarvis.asset_registry import CandidateAsset
from jarvis.asset_scoring_engine import clamp_score, score_asset, score_registry


def _write_registry(payload: dict) -> Path:
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".json", delete=False) as file:
        json.dump(payload, file)
        return Path(file.name)


def _etf_asset(**overrides) -> dict:
    asset = {
        "asset_id": "quality_candidate",
        "name": "Quality candidate",
        "asset_type": "ETF",
        "sleeve": "quality_etf",
        "ticker": "QETF",
        "isin_or_symbol": "IE00TEST0001",
        "platforms": ["Lightyear"],
        "currency": "EUR",
        "domicile": "Ireland",
        "distribution_policy": "accumulating",
        "ter_or_fee": 0.2,
        "data_source": "manual_test",
        "approval_status": "candidate_unreviewed",
        "risk_level": "medium",
        "provider": "Provider",
        "index_tracked": "Quality Index",
        "replication_method": "physical",
    }
    asset.update(overrides)
    return asset


def _crypto_asset(**overrides) -> dict:
    asset = {
        "asset_id": "btc_candidate",
        "name": "Bitcoin candidate",
        "asset_type": "crypto",
        "sleeve": "btc",
        "ticker": "BTC",
        "isin_or_symbol": "BTC",
        "platforms": ["LHV Crypto Investments"],
        "currency": "EUR",
        "domicile": "not_applicable",
        "distribution_policy": "not_applicable",
        "ter_or_fee": 0.0,
        "data_source": "manual_test",
        "approval_status": "test_position",
        "risk_level": "high",
        "network_or_protocol": "Bitcoin",
        "custody_platforms": ["LHV Crypto Investments"],
        "transferable": False,
        "mica_route_possible": True,
    }
    asset.update(overrides)
    return asset


class AssetScoringEngineTests(unittest.TestCase):
    def test_valid_etf_scorecard_generated(self) -> None:
        scorecard = score_registry(_write_registry({"assets": [_etf_asset()]}))[0]

        self.assertEqual(scorecard.asset_id, "quality_candidate")
        self.assertEqual(scorecard.asset_type, "ETF")
        self.assertIn("cost_score", scorecard.score_breakdown)

    def test_valid_crypto_scorecard_generated(self) -> None:
        scorecard = score_registry(_write_registry({"assets": [_crypto_asset()]}))[0]

        self.assertEqual(scorecard.asset_id, "btc_candidate")
        self.assertEqual(scorecard.asset_type, "crypto")
        self.assertIn("complexity_penalty", scorecard.score_breakdown)

    def test_final_score_is_clamped_between_zero_and_one_hundred(self) -> None:
        self.assertEqual(clamp_score(-10), 0.0)
        self.assertEqual(clamp_score(150), 100.0)

    def test_candidate_unreviewed_remains_blocked(self) -> None:
        scorecard = score_registry(_write_registry({"assets": [_etf_asset(approval_status="candidate_unreviewed")]}))[0]

        self.assertFalse(scorecard.approved_for_allocation)
        self.assertIn("not approved_investable", scorecard.blockers[0])

    def test_test_position_remains_blocked(self) -> None:
        scorecard = score_registry(_write_registry({"assets": [_crypto_asset(approval_status="test_position")]}))[0]

        self.assertFalse(scorecard.approved_for_allocation)
        self.assertIn("test_position", scorecard.blockers[0])

    def test_approved_investable_can_pass_allocation_gate(self) -> None:
        asset = CandidateAsset(
            asset_id="approved_test_asset",
            name="Approved test asset",
            asset_type="ETF",
            sleeve="quality_etf",
            ticker="QETF",
            isin_or_symbol="IE00TEST0001",
            platforms=("Lightyear",),
            currency="EUR",
            domicile="Ireland",
            distribution_policy="accumulating",
            ter_or_fee=0.2,
            data_source="manual_test",
            approval_status="approved_investable",
            risk_level="medium",
            provider="Provider",
            index_tracked="Quality Index",
            replication_method="physical",
        )

        scorecard = score_asset(asset)

        self.assertTrue(scorecard.approved_for_allocation)
        self.assertEqual(scorecard.blockers, ())

    def test_non_eur_asset_receives_warning_and_penalty(self) -> None:
        scorecard = score_registry(_write_registry({"assets": [_etf_asset(currency="USD")]}))[0]

        self.assertTrue(any("USD" in warning for warning in scorecard.warnings))
        self.assertGreater(scorecard.score_breakdown["complexity_penalty"], 0)

    def test_high_fee_etf_receives_lower_cost_score(self) -> None:
        low_fee = score_registry(_write_registry({"assets": [_etf_asset(asset_id="low_fee", ter_or_fee=0.1)]}))[0]
        high_fee = score_registry(_write_registry({"assets": [_etf_asset(asset_id="high_fee", ter_or_fee=0.9)]}))[0]

        self.assertLess(high_fee.score_breakdown["cost_score"], low_fee.score_breakdown["cost_score"])

    def test_missing_optional_data_creates_warning(self) -> None:
        scorecard = score_registry(
            _write_registry({"assets": [_etf_asset(ticker="UNKNOWN", provider="unknown", index_tracked="unknown")]})
        )[0]

        self.assertTrue(any("incomplete" in warning for warning in scorecard.warnings))

    def test_current_example_candidates_remain_not_approved_for_allocation(self) -> None:
        scorecards = score_registry("jarvis/data/candidate_assets.example.json")

        self.assertTrue(scorecards)
        self.assertTrue(all(not scorecard.approved_for_allocation for scorecard in scorecards))

    def test_cli_runs_without_error(self) -> None:
        result = subprocess.run(
            [sys.executable, "-m", "jarvis.asset_scoring_engine", "jarvis/data/candidate_assets.example.json"],
            check=True,
            capture_output=True,
            text=True,
        )

        payload = json.loads(result.stdout)
        self.assertEqual(payload[0]["asset_id"], "quality_etf_candidate")


if __name__ == "__main__":
    unittest.main()
