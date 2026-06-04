import json
import tempfile
import unittest
from pathlib import Path

from jarvis.candidate_review_engine import build_candidate_review_packs


def _write_json(payload: dict) -> Path:
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".json", delete=False) as file:
        json.dump(payload, file)
        return Path(file.name)


def _etf(asset_id: str = "etf_candidate", approval_status: str = "candidate_unreviewed") -> dict:
    return {
        "asset_id": asset_id,
        "name": "ETF candidate",
        "asset_type": "ETF",
        "sleeve": "quality_etf",
        "ticker": "ETF",
        "isin_or_symbol": "IE00TEST0001",
        "platforms": ["Lightyear"],
        "currency": "EUR",
        "domicile": "Ireland",
        "distribution_policy": "accumulating",
        "ter_or_fee": 0.2,
        "data_source": "manual_test",
        "approval_status": approval_status,
        "risk_level": "medium",
        "provider": "Provider",
        "index_tracked": "Index",
        "replication_method": "physical",
    }


def _crypto(asset_id: str = "crypto_candidate", approval_status: str = "candidate_unreviewed") -> dict:
    return {
        "asset_id": asset_id,
        "name": "Crypto candidate",
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
        "approval_status": approval_status,
        "risk_level": "high",
        "network_or_protocol": "Bitcoin",
        "custody_platforms": ["LHV Crypto Investments"],
        "transferable": False,
        "mica_route_possible": True,
    }


def _registry(*assets: dict) -> Path:
    return _write_json({"assets": list(assets)})


def _market(*asset_ids: str) -> Path:
    return _write_json(
        {
            "as_of": "2026-06-04",
            "base_currency": "EUR",
            "series": [
                {
                    "asset_id": asset_id,
                    "currency": "EUR",
                    "prices": [
                        {"date": "2025-06-01", "close": 100.0},
                        {"date": "2025-12-01", "close": 105.0},
                        {"date": "2026-06-01", "close": 110.0},
                    ],
                }
                for asset_id in asset_ids
            ],
        }
    )


def _exposure(*asset_ids: str) -> Path:
    return _write_json(
        {
            "as_of": "2026-06-04",
            "assets": [
                {
                    "asset_id": asset_id,
                    "holdings": [
                        {"name": "Company A", "weight": 0.05},
                        {"name": "Company B", "weight": 0.04},
                        {"name": "Company C", "weight": 0.03},
                    ],
                    "countries": {"US": 0.60},
                    "sectors": {"Technology": 0.25},
                }
                for asset_id in asset_ids
            ],
        }
    )


class CandidateReviewEngineTests(unittest.TestCase):
    def test_etf_with_scorecard_market_and_exposure_is_review_ready_but_not_approved(self) -> None:
        packs = build_candidate_review_packs(
            _registry(_etf()),
            _market("etf_candidate"),
            _exposure("etf_candidate"),
        )

        self.assertEqual(packs[0].review_status, "review_ready")
        self.assertTrue(packs[0].can_submit_for_manual_approval)
        self.assertFalse(packs[0].approved_for_allocation)

    def test_etf_missing_exposure_is_blocked(self) -> None:
        pack = build_candidate_review_packs(_registry(_etf()), _market("etf_candidate"), None)[0]

        self.assertEqual(pack.review_status, "blocked_missing_exposure_data")

    def test_etf_missing_market_data_is_blocked(self) -> None:
        pack = build_candidate_review_packs(_registry(_etf()), None, _exposure("etf_candidate"))[0]

        self.assertEqual(pack.review_status, "blocked_missing_market_data")

    def test_crypto_with_scorecard_and_market_is_review_ready_without_exposure(self) -> None:
        pack = build_candidate_review_packs(_registry(_crypto()), _market("crypto_candidate"), None)[0]

        self.assertEqual(pack.review_status, "review_ready")
        self.assertTrue(pack.can_submit_for_manual_approval)

    def test_candidate_unreviewed_remains_not_approved_for_allocation(self) -> None:
        pack = build_candidate_review_packs(
            _registry(_etf(approval_status="candidate_unreviewed")),
            _market("etf_candidate"),
            _exposure("etf_candidate"),
        )[0]

        self.assertFalse(pack.approved_for_allocation)

    def test_test_position_remains_not_approved_for_allocation(self) -> None:
        pack = build_candidate_review_packs(_registry(_crypto(approval_status="test_position")), _market("crypto_candidate"))[0]

        self.assertFalse(pack.approved_for_allocation)

    def test_rejected_asset_cannot_be_review_ready(self) -> None:
        pack = build_candidate_review_packs(
            _registry(_etf(approval_status="rejected")),
            _market("etf_candidate"),
            _exposure("etf_candidate"),
        )[0]

        self.assertEqual(pack.review_status, "blocked_by_approval_gate")
        self.assertFalse(pack.can_submit_for_manual_approval)

    def test_manual_approval_required_is_always_true(self) -> None:
        pack = build_candidate_review_packs(_registry(_crypto()), _market("crypto_candidate"))[0]

        self.assertTrue(pack.manual_approval_required)

    def test_can_submit_never_changes_approval_status(self) -> None:
        pack = build_candidate_review_packs(
            _registry(_etf(approval_status="candidate_unreviewed")),
            _market("etf_candidate"),
            _exposure("etf_candidate"),
        )[0]

        self.assertTrue(pack.can_submit_for_manual_approval)
        self.assertEqual(pack.approval_status, "candidate_unreviewed")


if __name__ == "__main__":
    unittest.main()
