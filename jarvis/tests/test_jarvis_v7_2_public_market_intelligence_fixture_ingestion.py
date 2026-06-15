import unittest
from dataclasses import replace

from jarvis.jarvis_v7_0_autonomous_market_intelligence_expansion import SIGNAL_BLOCKING
from jarvis.jarvis_v7_2_public_market_intelligence_fixture_ingestion import (
    FIXTURE_DATASET_ID,
    INGESTION_STATUS_READY,
    STATUS_BLOCKED,
    STATUS_READY,
    audit_v7_2_public_market_intelligence_fixture_ingestion,
)


class JarvisV72PublicMarketIntelligenceFixtureIngestionTests(unittest.TestCase):
    def test_fixture_ingestion_is_ready_and_points_to_live_fetch_boundary(self) -> None:
        result = audit_v7_2_public_market_intelligence_fixture_ingestion()

        self.assertEqual(result.status, STATUS_READY)
        self.assertEqual(result.ingestion_status, INGESTION_STATUS_READY)
        self.assertEqual(result.recommended_next_stage, "v7_3_live_public_market_intelligence_fetcher_boundary")
        self.assertTrue(result.fixture_ingestion_ready)
        self.assertTrue(result.compatible_with_v7_1_contract)
        self.assertTrue(result.selected_candidate_supported)
        self.assertFalse(result.selected_candidate_blocked)
        self.assertEqual(result.fixture_row_count, result.ingested_record_count)
        self.assertEqual(result.ingested_record_count, result.generated_signal_count)
        self.assertFalse(result.blockers)

    def test_fixture_rows_are_non_executable_and_not_live_fetched(self) -> None:
        result = audit_v7_2_public_market_intelligence_fixture_ingestion()

        for row in result.fixture_rows:
            self.assertEqual(row.fixture_dataset_id, FIXTURE_DATASET_ID)
            self.assertFalse(row.live_fetch_attempted)
            self.assertFalse(row.creates_buy_request)
            self.assertFalse(row.connects_broker)
            self.assertFalse(row.places_order)
            self.assertFalse(row.executes_trade)
            self.assertTrue(row.safe_fixture_row_only())

    def test_ingested_records_are_adapter_shaped_and_non_executable(self) -> None:
        result = audit_v7_2_public_market_intelligence_fixture_ingestion()

        for record in result.ingested_adapter_records:
            self.assertEqual(record.adapter_name, "jarvis_v7_2_fixture_ingestion_adapter")
            self.assertFalse(record.live_fetch_attempted)
            self.assertFalse(record.creates_buy_request)
            self.assertFalse(record.connects_broker)
            self.assertFalse(record.places_order)
            self.assertFalse(record.executes_trade)
            self.assertTrue(record.safe_adapter_record_only())

    def test_invalid_override_blocks_safely(self) -> None:
        blocked = audit_v7_2_public_market_intelligence_fixture_ingestion(object())

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("Fixture override must be" in blocker for blocker in blocked.blockers))

    def test_empty_rows_block(self) -> None:
        blocked = audit_v7_2_public_market_intelligence_fixture_ingestion(())

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("No public market intelligence fixture rows" in blocker for blocker in blocked.blockers))

    def test_duplicate_fixture_row_id_blocks(self) -> None:
        result = audit_v7_2_public_market_intelligence_fixture_ingestion()
        blocked = audit_v7_2_public_market_intelligence_fixture_ingestion(
            result.fixture_rows + (result.fixture_rows[0],)
        )

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("unique" in blocker for blocker in blocked.blockers))

    def test_unsafe_fixture_row_blocks(self) -> None:
        result = audit_v7_2_public_market_intelligence_fixture_ingestion()
        bad = replace(
            result.fixture_rows[0],
            live_fetch_attempted=True,
            creates_buy_request=True,
            connects_broker=True,
            places_order=True,
            executes_trade=True,
        )

        blocked = audit_v7_2_public_market_intelligence_fixture_ingestion(
            (bad,) + result.fixture_rows[1:]
        )

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("live fetching is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("buy request creation is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("broker connection is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("order placement is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("trade execution is forbidden" in blocker for blocker in blocked.blockers))

    def test_invalid_dataset_id_blocks(self) -> None:
        result = audit_v7_2_public_market_intelligence_fixture_ingestion()
        bad = replace(result.fixture_rows[0], fixture_dataset_id="wrong_dataset")

        blocked = audit_v7_2_public_market_intelligence_fixture_ingestion(
            (bad,) + result.fixture_rows[1:]
        )

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("fixture dataset ID is invalid" in blocker for blocker in blocked.blockers))

    def test_blocking_selected_candidate_blocks_ingestion(self) -> None:
        result = audit_v7_2_public_market_intelligence_fixture_ingestion()
        selected_rows = [
            row for row in result.fixture_rows if row.candidate_id == result.selected_candidate_id
        ]
        bad = replace(
            selected_rows[0],
            severity=SIGNAL_BLOCKING,
            blocks_recommendation=True,
        )
        rows = tuple(
            bad if row.fixture_row_id == bad.fixture_row_id else row
            for row in result.fixture_rows
        )

        blocked = audit_v7_2_public_market_intelligence_fixture_ingestion(rows)

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(blocked.selected_candidate_blocked)
        self.assertTrue(any("block the selected weekly candidate" in blocker for blocker in blocked.blockers))

    def test_safety_flags_preserve_no_execution_boundary(self) -> None:
        result = audit_v7_2_public_market_intelligence_fixture_ingestion()
        payload = result.to_dict()

        self.assertTrue(payload["fixture_ingestion_only"])
        self.assertTrue(payload["live_fetch_deferred"])
        self.assertTrue(payload["final_user_buy_action_required"])
        self.assertTrue(payload["buy_request_deferred"])
        self.assertTrue(payload["broker_connection_forbidden"])
        self.assertTrue(payload["order_placement_forbidden"])
        self.assertTrue(payload["no_trades_executed"])


if __name__ == "__main__":
    unittest.main()
