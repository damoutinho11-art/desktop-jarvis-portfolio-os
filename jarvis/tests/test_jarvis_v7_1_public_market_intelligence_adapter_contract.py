import unittest
from dataclasses import replace

from jarvis.jarvis_v7_1_public_market_intelligence_adapter_contract import (
    ADAPTER_STATUS_CONTRACT_READY,
    SIGNAL_BLOCKING,
    STATUS_BLOCKED,
    STATUS_READY,
    audit_v7_1_public_market_intelligence_adapter_contract,
)


class JarvisV71PublicMarketIntelligenceAdapterContractTests(unittest.TestCase):
    def test_adapter_contract_is_ready_and_points_to_fixture_ingestion(self) -> None:
        result = audit_v7_1_public_market_intelligence_adapter_contract()

        self.assertEqual(result.status, STATUS_READY)
        self.assertEqual(result.adapter_status, ADAPTER_STATUS_CONTRACT_READY)
        self.assertEqual(result.recommended_next_stage, "v7_2_public_market_intelligence_fixture_ingestion")
        self.assertTrue(result.adapter_contract_ready)
        self.assertTrue(result.compatible_with_v7_0)
        self.assertTrue(result.selected_candidate_supported)
        self.assertFalse(result.selected_candidate_blocked)
        self.assertGreaterEqual(result.adapter_record_count, 4)
        self.assertEqual(result.adapter_record_count, result.generated_signal_count)
        self.assertFalse(result.blockers)

    def test_contract_does_not_live_fetch(self) -> None:
        result = audit_v7_1_public_market_intelligence_adapter_contract()

        for record in result.public_adapter_records:
            self.assertFalse(record.live_fetch_attempted)
            self.assertIn("example.invalid", record.source_url)
            self.assertTrue(record.safe_adapter_record_only())

    def test_generated_signals_are_v7_0_compatible_and_non_executable(self) -> None:
        result = audit_v7_1_public_market_intelligence_adapter_contract()

        for signal in result.generated_signals:
            self.assertFalse(signal.creates_buy_request)
            self.assertFalse(signal.connects_broker)
            self.assertFalse(signal.places_order)
            self.assertFalse(signal.executes_trade)
            self.assertTrue(signal.safe_signal_only())

    def test_invalid_override_blocks_safely(self) -> None:
        blocked = audit_v7_1_public_market_intelligence_adapter_contract(object())

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("Adapter override must be" in blocker for blocker in blocked.blockers))

    def test_empty_records_block(self) -> None:
        blocked = audit_v7_1_public_market_intelligence_adapter_contract(())

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("No public market intelligence adapter records" in blocker for blocker in blocked.blockers))

    def test_duplicate_record_id_blocks(self) -> None:
        result = audit_v7_1_public_market_intelligence_adapter_contract()
        blocked = audit_v7_1_public_market_intelligence_adapter_contract(
            result.public_adapter_records + (result.public_adapter_records[0],)
        )

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("unique" in blocker for blocker in blocked.blockers))

    def test_unsafe_adapter_record_blocks(self) -> None:
        result = audit_v7_1_public_market_intelligence_adapter_contract()
        bad = replace(
            result.public_adapter_records[0],
            live_fetch_attempted=True,
            creates_buy_request=True,
            connects_broker=True,
            places_order=True,
            executes_trade=True,
        )

        blocked = audit_v7_1_public_market_intelligence_adapter_contract(
            (bad,) + result.public_adapter_records[1:]
        )

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("live fetching is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("buy request creation is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("broker connection is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("order placement is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("trade execution is forbidden" in blocker for blocker in blocked.blockers))

    def test_invalid_source_quality_blocks(self) -> None:
        result = audit_v7_1_public_market_intelligence_adapter_contract()
        bad = replace(result.public_adapter_records[0], public_source_quality="UNTRUSTED_UNKNOWN")

        blocked = audit_v7_1_public_market_intelligence_adapter_contract(
            (bad,) + result.public_adapter_records[1:]
        )

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("public source quality is not allowed" in blocker for blocker in blocked.blockers))

    def test_blocking_selected_candidate_blocks_contract(self) -> None:
        result = audit_v7_1_public_market_intelligence_adapter_contract()
        selected_records = [
            record for record in result.public_adapter_records if record.candidate_id == result.selected_candidate_id
        ]
        bad = replace(
            selected_records[0],
            severity=SIGNAL_BLOCKING,
            blocks_recommendation=True,
        )
        records = tuple(
            bad if record.record_id == bad.record_id else record
            for record in result.public_adapter_records
        )

        blocked = audit_v7_1_public_market_intelligence_adapter_contract(records)

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(blocked.selected_candidate_blocked)
        self.assertTrue(any("block the selected weekly candidate" in blocker for blocker in blocked.blockers))

    def test_safety_flags_preserve_no_execution_boundary(self) -> None:
        result = audit_v7_1_public_market_intelligence_adapter_contract()
        payload = result.to_dict()

        self.assertTrue(payload["contract_only"])
        self.assertTrue(payload["live_fetch_deferred"])
        self.assertTrue(payload["final_user_buy_action_required"])
        self.assertTrue(payload["buy_request_deferred"])
        self.assertTrue(payload["broker_connection_forbidden"])
        self.assertTrue(payload["order_placement_forbidden"])
        self.assertTrue(payload["no_trades_executed"])


if __name__ == "__main__":
    unittest.main()
