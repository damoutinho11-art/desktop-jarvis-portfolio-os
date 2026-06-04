import json
import tempfile
import unittest
from pathlib import Path

from jarvis.universe_review_workflow import build_universe_review


def _write_json(payload: dict) -> Path:
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".json", delete=False) as file:
        json.dump(payload, file)
        return Path(file.name)


def _asset(asset_id: str, status: str = "candidate_unreviewed", asset_type: str = "ETF") -> dict:
    asset = {
        "asset_id": asset_id,
        "name": asset_id,
        "asset_type": asset_type,
        "sleeve": "quality_factor" if asset_type == "ETF" else "crypto_core",
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
    }
    if asset_type == "ETF":
        asset.update({"provider": "Provider", "index_tracked": "Index", "replication_method": "physical"})
    if asset_type == "crypto":
        asset.update(
            {
                "network_or_protocol": "Bitcoin",
                "custody_platforms": ["LHV Crypto Investments"],
                "transferable": False,
                "mica_route_possible": True,
            }
        )
    return asset


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


POLICY = "jarvis/data/portfolio_policy.example.json"


class UniverseReviewWorkflowTests(unittest.TestCase):
    def _review_one(self, asset: dict, include_market=True, include_exposure=True):
        asset_id = asset["asset_id"]
        return build_universe_review(
            _registry(asset),
            _market(asset_id) if include_market else _market("other"),
            _exposure(asset_id) if include_exposure else _exposure("other"),
            POLICY,
        ).candidates[0]

    def test_candidate_unreviewed_review_ready_suggests_candidate_reviewed(self) -> None:
        candidate = self._review_one(_asset("asset_unreviewed", "candidate_unreviewed"))

        self.assertEqual(candidate.suggested_next_status, "candidate_reviewed")

    def test_candidate_reviewed_review_ready_suggests_approved_watchlist(self) -> None:
        candidate = self._review_one(_asset("asset_reviewed", "candidate_reviewed"))

        self.assertEqual(candidate.suggested_next_status, "approved_watchlist")

    def test_approved_watchlist_review_ready_suggests_manual_investable_review(self) -> None:
        candidate = self._review_one(_asset("asset_watchlist", "approved_watchlist"))

        self.assertEqual(candidate.suggested_next_status, "eligible_for_manual_investable_review")

    def test_rejected_asset_suggests_no_promotion(self) -> None:
        candidate = self._review_one(_asset("asset_rejected", "rejected"))

        self.assertIsNone(candidate.suggested_next_status)

    def test_blocked_candidate_has_no_suggested_promotion(self) -> None:
        candidate = self._review_one(_asset("asset_blocked", "candidate_unreviewed"), include_market=False)

        self.assertEqual(candidate.review_status, "blocked_missing_market_data")
        self.assertIsNone(candidate.suggested_next_status)

    def test_no_registry_mutation(self) -> None:
        registry = _registry(_asset("asset_unreviewed", "candidate_unreviewed"))
        before = registry.read_text(encoding="utf-8")

        build_universe_review(registry, _market("asset_unreviewed"), _exposure("asset_unreviewed"), POLICY)

        self.assertEqual(registry.read_text(encoding="utf-8"), before)

    def test_no_approvals_created(self) -> None:
        result = build_universe_review(
            _registry(_asset("asset_unreviewed", "candidate_unreviewed")),
            _market("asset_unreviewed"),
            _exposure("asset_unreviewed"),
            POLICY,
        )

        self.assertFalse(hasattr(result, "approval_requests"))

    def test_manual_approval_required_always_true(self) -> None:
        candidate = self._review_one(_asset("asset_unreviewed", "candidate_unreviewed"))

        self.assertTrue(candidate.manual_approval_required)

    def test_summary_counts_correct(self) -> None:
        result = build_universe_review(
            _registry(_asset("asset_a", "candidate_unreviewed"), _asset("asset_b", "candidate_reviewed")),
            _market("asset_a", "asset_b"),
            _exposure("asset_a", "asset_b"),
            POLICY,
        )

        self.assertEqual(result.summary.total_candidates, 2)
        self.assertEqual(result.summary.review_ready_count, 2)
        self.assertEqual(result.summary.by_status["candidate_unreviewed"], 1)
        self.assertEqual(result.summary.by_status["candidate_reviewed"], 1)


if __name__ == "__main__":
    unittest.main()
