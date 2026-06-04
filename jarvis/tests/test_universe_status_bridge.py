import tempfile
import unittest
from pathlib import Path

from jarvis.universe_review_workflow import UniverseCandidateReview, UniverseReviewResult, UniverseReviewSummary
from jarvis.universe_status_bridge import bridge_universe_review, write_status_requests
from jarvis.asset_status_workflow import validate_asset_status_request


def _candidate(status: str, suggested: str | None, ready: bool = True, asset_type: str = "ETF") -> UniverseCandidateReview:
    return UniverseCandidateReview(
        asset_id=f"asset_{status}",
        asset_type=asset_type,
        sleeve="quality_factor",
        approval_status=status,
        final_candidate_score=75.0,
        review_status="review_ready" if ready else "blocked_missing_market_data",
        can_submit_for_manual_approval=ready,
        suggested_next_status=suggested,
        missing_evidence=() if ready else ("market_data",),
        warnings=(),
        blockers=(),
        manual_approval_required=True,
    )


def _review(*candidates: UniverseCandidateReview) -> UniverseReviewResult:
    return UniverseReviewResult(
        candidates=tuple(candidates),
        summary=UniverseReviewSummary(
            total_candidates=len(candidates),
            review_ready_count=sum(candidate.review_status == "review_ready" for candidate in candidates),
            blocked_count=sum(candidate.review_status.startswith("blocked_") for candidate in candidates),
            by_sleeve={},
            by_status={},
            approved_universe_count=0,
            allocation_ready=False,
            warnings=(),
            blockers=(),
        ),
    )


class UniverseStatusBridgeTests(unittest.TestCase):
    def test_review_ready_candidate_unreviewed_generates_candidate_reviewed_request(self) -> None:
        result = bridge_universe_review(_review(_candidate("candidate_unreviewed", "candidate_reviewed")))

        self.assertEqual(result.status_requests[0].requested_status, "candidate_reviewed")

    def test_review_ready_candidate_reviewed_generates_approved_watchlist_request(self) -> None:
        result = bridge_universe_review(_review(_candidate("candidate_reviewed", "approved_watchlist")))

        self.assertEqual(result.status_requests[0].requested_status, "approved_watchlist")

    def test_approved_watchlist_generates_investable_request_with_confirmations(self) -> None:
        result = bridge_universe_review(
            _review(_candidate("approved_watchlist", "eligible_for_manual_investable_review"))
        )
        request = result.status_requests[0]

        self.assertEqual(request.requested_status, "approved_investable")
        self.assertIn("manual_asset_approval_confirmed", request.required_confirmations)
        self.assertIn("expense_ratio_reviewed", request.required_confirmations)

    def test_blocked_candidate_creates_no_request(self) -> None:
        result = bridge_universe_review(_review(_candidate("candidate_unreviewed", None, ready=False)))

        self.assertEqual(result.status_requests, ())
        self.assertTrue(result.blocked_candidates)

    def test_rejected_candidate_creates_no_request(self) -> None:
        result = bridge_universe_review(_review(_candidate("rejected", None)))

        self.assertEqual(result.status_requests, ())
        self.assertTrue(result.blocked_candidates)

    def test_no_direct_candidate_unreviewed_to_approved_investable(self) -> None:
        result = bridge_universe_review(_review(_candidate("candidate_unreviewed", "approved_investable")))

        self.assertEqual(result.status_requests, ())
        self.assertTrue(result.blocked_candidates)

    def test_generated_requests_validate_through_asset_status_workflow(self) -> None:
        result = bridge_universe_review(_review(_candidate("candidate_reviewed", "approved_watchlist")))

        self.assertTrue(validate_asset_status_request(result.status_requests[0]).valid)

    def test_auto_execute_always_false(self) -> None:
        result = bridge_universe_review(_review(_candidate("candidate_unreviewed", "candidate_reviewed")))

        self.assertFalse(result.status_requests[0].auto_execute)

    def test_manual_approval_required_always_true(self) -> None:
        result = bridge_universe_review(_review(_candidate("candidate_unreviewed", "candidate_reviewed")))

        self.assertTrue(result.status_requests[0].manual_approval_required)

    def test_bridge_writes_nothing_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "requests.json"
            bridge_universe_review(_review(_candidate("candidate_unreviewed", "candidate_reviewed")))

            self.assertFalse(target.exists())

    def test_optional_writer_writes_when_called(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "requests.json"
            result = bridge_universe_review(_review(_candidate("candidate_unreviewed", "candidate_reviewed")))

            write_status_requests(result, target)

            self.assertTrue(target.exists())


if __name__ == "__main__":
    unittest.main()
