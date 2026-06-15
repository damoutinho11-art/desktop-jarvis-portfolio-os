import unittest
from dataclasses import replace

from jarvis.jarvis_v7_3_live_public_market_intelligence_fetcher_boundary import (
    BOUNDARY_STATUS_READY,
    STATUS_BLOCKED,
    STATUS_READY,
    audit_v7_3_live_public_market_intelligence_fetcher_boundary,
)


class JarvisV73LivePublicMarketIntelligenceFetcherBoundaryTests(unittest.TestCase):
    def test_live_fetch_boundary_is_ready_and_points_to_dry_run_planner(self) -> None:
        result = audit_v7_3_live_public_market_intelligence_fetcher_boundary()

        self.assertEqual(result.status, STATUS_READY)
        self.assertEqual(result.boundary_status, BOUNDARY_STATUS_READY)
        self.assertEqual(result.recommended_next_stage, "v7_4_live_public_market_intelligence_dry_run_planner")
        self.assertTrue(result.live_fetch_boundary_ready)
        self.assertTrue(result.compatible_with_v7_2_fixture_ingestion)
        self.assertGreaterEqual(result.fetch_boundary_request_count, 4)
        self.assertEqual(result.disabled_live_fetch_count, result.fetch_boundary_request_count)
        self.assertEqual(result.network_call_attempt_count, 0)
        self.assertFalse(result.blockers)

    def test_fetch_requests_are_disabled_and_non_executable(self) -> None:
        result = audit_v7_3_live_public_market_intelligence_fetcher_boundary()

        for request in result.fetch_boundary_requests:
            self.assertFalse(request.live_fetch_enabled)
            self.assertFalse(request.network_call_attempted)
            self.assertFalse(request.stores_raw_response)
            self.assertFalse(request.creates_buy_request)
            self.assertFalse(request.connects_broker)
            self.assertFalse(request.places_order)
            self.assertFalse(request.executes_trade)
            self.assertTrue(request.safe_boundary_only())

    def test_selected_candidate_has_fetch_boundary_request(self) -> None:
        result = audit_v7_3_live_public_market_intelligence_fetcher_boundary()
        selected = [
            request
            for request in result.fetch_boundary_requests
            if request.candidate_id == result.selected_candidate_id
        ]

        self.assertTrue(selected)

    def test_invalid_override_blocks_safely(self) -> None:
        blocked = audit_v7_3_live_public_market_intelligence_fetcher_boundary(object())

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("Fetch request override must be" in blocker for blocker in blocked.blockers))

    def test_empty_requests_block(self) -> None:
        blocked = audit_v7_3_live_public_market_intelligence_fetcher_boundary(())

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("No live public market fetch boundary requests" in blocker for blocker in blocked.blockers))

    def test_duplicate_request_id_blocks(self) -> None:
        result = audit_v7_3_live_public_market_intelligence_fetcher_boundary()
        blocked = audit_v7_3_live_public_market_intelligence_fetcher_boundary(
            result.fetch_boundary_requests + (result.fetch_boundary_requests[0],)
        )

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("unique" in blocker for blocker in blocked.blockers))

    def test_enabling_live_fetch_blocks(self) -> None:
        result = audit_v7_3_live_public_market_intelligence_fetcher_boundary()
        bad = replace(result.fetch_boundary_requests[0], live_fetch_enabled=True)

        blocked = audit_v7_3_live_public_market_intelligence_fetcher_boundary(
            (bad,) + result.fetch_boundary_requests[1:]
        )

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("live fetching must be disabled" in blocker for blocker in blocked.blockers))

    def test_network_call_attempt_blocks(self) -> None:
        result = audit_v7_3_live_public_market_intelligence_fetcher_boundary()
        bad = replace(result.fetch_boundary_requests[0], network_call_attempted=True)

        blocked = audit_v7_3_live_public_market_intelligence_fetcher_boundary(
            (bad,) + result.fetch_boundary_requests[1:]
        )

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("network calls are forbidden" in blocker for blocker in blocked.blockers))

    def test_unsafe_request_blocks(self) -> None:
        result = audit_v7_3_live_public_market_intelligence_fetcher_boundary()
        bad = replace(
            result.fetch_boundary_requests[0],
            creates_buy_request=True,
            connects_broker=True,
            places_order=True,
            executes_trade=True,
        )

        blocked = audit_v7_3_live_public_market_intelligence_fetcher_boundary(
            (bad,) + result.fetch_boundary_requests[1:]
        )

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("buy request creation is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("broker connection is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("order placement is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("trade execution is forbidden" in blocker for blocker in blocked.blockers))

    def test_safety_flags_preserve_no_execution_boundary(self) -> None:
        result = audit_v7_3_live_public_market_intelligence_fetcher_boundary()
        payload = result.to_dict()

        self.assertTrue(payload["boundary_only"])
        self.assertTrue(payload["live_fetch_disabled_by_default"])
        self.assertTrue(payload["network_calls_deferred"])
        self.assertTrue(payload["final_user_buy_action_required"])
        self.assertTrue(payload["buy_request_deferred"])
        self.assertTrue(payload["broker_connection_forbidden"])
        self.assertTrue(payload["order_placement_forbidden"])
        self.assertTrue(payload["no_trades_executed"])


if __name__ == "__main__":
    unittest.main()
