import json
import tempfile
import unittest
from pathlib import Path

from jarvis.candidate_evidence_matrix import build_candidate_evidence_matrix


V2_REGISTRY = "jarvis/data/candidate_assets.v2.example.json"
MARKET = "jarvis/data/market_data.example.json"
EXPOSURE = "jarvis/data/asset_exposure.example.json"
POLICY = "jarvis/data/portfolio_policy.example.json"


def _write_json(payload: dict) -> Path:
    handle = tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".json", delete=False)
    with handle:
        json.dump(payload, handle)
    return Path(handle.name)


def _etf_asset(**overrides) -> dict:
    asset = {
        "asset_id": "eligible_etf",
        "name": "Eligible ETF candidate",
        "asset_type": "ETF",
        "sleeve": "global_core",
        "ticker": "EETF",
        "isin_or_symbol": "IE00TESTETF1",
        "platforms": ["Lightyear"],
        "currency": "EUR",
        "domicile": "Ireland",
        "distribution_policy": "accumulating",
        "ter_or_fee": 0.2,
        "provider": "Provider",
        "index_tracked": "Global Index",
        "replication_method": "physical",
        "data_source": "manual_test",
        "approval_status": "candidate_unreviewed",
        "risk_level": "medium",
        "notes": "Synthetic test candidate.",
    }
    asset.update(overrides)
    return asset


def _crypto_asset(**overrides) -> dict:
    asset = {
        "asset_id": "eligible_crypto",
        "name": "Eligible crypto candidate",
        "asset_type": "crypto",
        "sleeve": "crypto_core",
        "ticker": "COIN",
        "isin_or_symbol": "COIN",
        "platforms": ["Kraken"],
        "currency": "EUR",
        "domicile": "n/a",
        "distribution_policy": "n/a",
        "ter_or_fee": 0.0,
        "network_or_protocol": "TestNet",
        "custody_platforms": ["Kraken"],
        "transferable": True,
        "mica_route_possible": True,
        "data_source": "manual_test",
        "approval_status": "candidate_unreviewed",
        "risk_level": "high",
        "notes": "Synthetic crypto risk notes.",
    }
    asset.update(overrides)
    return asset


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
                        {"date": "2026-05-01", "close": 100.0},
                        {"date": "2026-06-01", "close": 101.0},
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
                    "countries": {"US": 0.6, "NL": 0.1},
                    "sectors": {"Technology": 0.25, "Healthcare": 0.15},
                }
                for asset_id in asset_ids
            ],
        }
    )


class CandidateEvidenceMatrixTests(unittest.TestCase):
    def test_v2_candidate_file_produces_25_evidence_rows(self) -> None:
        matrix = build_candidate_evidence_matrix(V2_REGISTRY, MARKET, EXPOSURE, POLICY)

        self.assertEqual(len(matrix.rows), 25)
        self.assertEqual(matrix.summary.total_candidates, 25)

    def test_etf_with_market_exposure_and_platform_evidence_can_be_eligible(self) -> None:
        registry = _write_json({"assets": [_etf_asset()]})
        matrix = build_candidate_evidence_matrix(registry, _market("eligible_etf"), _exposure("eligible_etf"), POLICY)

        self.assertTrue(matrix.rows[0].eligible_for_manual_review)
        self.assertEqual(matrix.rows[0].missing_evidence, ())

    def test_etf_missing_exposure_is_blocked(self) -> None:
        registry = _write_json({"assets": [_etf_asset()]})
        matrix = build_candidate_evidence_matrix(registry, _market("eligible_etf"), _exposure("other_asset"), POLICY)

        self.assertFalse(matrix.rows[0].eligible_for_manual_review)
        self.assertIn("exposure_data", matrix.rows[0].missing_evidence)

    def test_etf_missing_market_data_is_blocked(self) -> None:
        registry = _write_json({"assets": [_etf_asset()]})
        matrix = build_candidate_evidence_matrix(registry, _market("other_asset"), _exposure("eligible_etf"), POLICY)

        self.assertFalse(matrix.rows[0].eligible_for_manual_review)
        self.assertIn("market_data", matrix.rows[0].missing_evidence)

    def test_crypto_missing_market_data_is_blocked(self) -> None:
        registry = _write_json({"assets": [_crypto_asset()]})
        matrix = build_candidate_evidence_matrix(registry, _market("other_asset"), _exposure("eligible_etf"), POLICY)

        self.assertFalse(matrix.rows[0].eligible_for_manual_review)
        self.assertIn("market_data", matrix.rows[0].missing_evidence)

    def test_crypto_does_not_require_exposure_data(self) -> None:
        registry = _write_json({"assets": [_crypto_asset()]})
        matrix = build_candidate_evidence_matrix(registry, _market("eligible_crypto"), _exposure("other_asset"), POLICY)

        self.assertTrue(matrix.rows[0].eligible_for_manual_review)
        self.assertNotIn("exposure_data", matrix.rows[0].missing_evidence)

    def test_missing_platform_data_is_blocked(self) -> None:
        registry = _write_json({"assets": [_etf_asset(platforms=["unknown"])]})
        matrix = build_candidate_evidence_matrix(registry, _market("eligible_etf"), _exposure("eligible_etf"), POLICY)

        self.assertFalse(matrix.rows[0].eligible_for_manual_review)
        self.assertIn("platform_data", matrix.rows[0].missing_evidence)

    def test_evidence_score_is_clamped_0_to_100(self) -> None:
        matrix = build_candidate_evidence_matrix(V2_REGISTRY, MARKET, EXPOSURE, POLICY)

        self.assertTrue(all(0.0 <= row.evidence_score <= 100.0 for row in matrix.rows))

    def test_eligible_for_manual_review_never_changes_approval_status(self) -> None:
        registry = _write_json({"assets": [_etf_asset(approval_status="candidate_reviewed")]})
        matrix = build_candidate_evidence_matrix(registry, _market("eligible_etf"), _exposure("eligible_etf"), POLICY)

        self.assertTrue(matrix.rows[0].eligible_for_manual_review)
        self.assertEqual(matrix.rows[0].approval_status, "candidate_reviewed")

    def test_manual_approval_required_always_true(self) -> None:
        matrix = build_candidate_evidence_matrix(V2_REGISTRY, MARKET, EXPOSURE, POLICY)

        self.assertTrue(matrix.manual_approval_required)
        self.assertTrue(all(row.manual_approval_required for row in matrix.rows))

    def test_summary_counts_correct(self) -> None:
        matrix = build_candidate_evidence_matrix(V2_REGISTRY, MARKET, EXPOSURE, POLICY)

        self.assertEqual(matrix.summary.by_sleeve["global_core"], 5)
        self.assertEqual(matrix.summary.by_asset_type, {"ETF": 15, "crypto": 10})
        self.assertEqual(matrix.summary.missing_market_data_count, 25)
        self.assertEqual(matrix.summary.missing_exposure_data_count, 15)
        self.assertEqual(matrix.summary.missing_platform_data_count, 0)


if __name__ == "__main__":
    unittest.main()
