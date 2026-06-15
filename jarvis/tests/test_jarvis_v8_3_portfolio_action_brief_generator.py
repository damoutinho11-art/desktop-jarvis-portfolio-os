import unittest
from dataclasses import replace

from jarvis.jarvis_v8_3_portfolio_action_brief_generator import (
    BRIEF_STATUS_READY,
    STATUS_BLOCKED,
    STATUS_READY,
    audit_v8_3_portfolio_action_brief_generator,
)


class JarvisV83PortfolioActionBriefGeneratorTests(unittest.TestCase):
    def test_action_brief_is_ready_and_preparatory(self) -> None:
        result = audit_v8_3_portfolio_action_brief_generator()

        self.assertEqual(result.status, STATUS_READY)
        self.assertEqual(result.brief_status, BRIEF_STATUS_READY)
        self.assertEqual(result.recommended_next_stage, "v8_4_operator_command_center_closeout")
        self.assertTrue(result.action_brief_ready)
        self.assertTrue(result.compatible_with_v8_2_evidence_pack)
        self.assertGreaterEqual(result.evidence_section_count, 6)
        self.assertGreaterEqual(result.ready_evidence_section_count, 5)
        self.assertGreaterEqual(result.watch_evidence_section_count, 1)
        self.assertEqual(result.blocked_evidence_section_count, 0)
        self.assertFalse(result.blockers)

    def test_brief_answers_core_operator_questions(self) -> None:
        result = audit_v8_3_portfolio_action_brief_generator()
        brief = result.brief

        self.assertTrue(brief.headline)
        self.assertTrue(brief.preparation_reason)
        self.assertIn("Ready evidence sections", brief.evidence_summary)
        self.assertIn("Watch-only sections", brief.watch_summary)
        self.assertIn("Blocked sections", brief.blocked_summary)
        self.assertIn("manual", brief.final_manual_action.lower())
        self.assertIn("not", brief.operator_instruction.lower())

    def test_brief_is_non_executable(self) -> None:
        brief = audit_v8_3_portfolio_action_brief_generator().brief

        self.assertTrue(brief.user_visible)
        self.assertFalse(brief.creates_buy_request)
        self.assertFalse(brief.connects_broker)
        self.assertFalse(brief.places_order)
        self.assertFalse(brief.executes_trade)
        self.assertFalse(brief.live_fetch_enabled)
        self.assertFalse(brief.network_call_enabled)
        self.assertFalse(brief.raw_response_storage_enabled)
        self.assertFalse(brief.live_adapter_record_emission_enabled)
        self.assertTrue(brief.safe_brief_only())

    def test_invalid_override_blocks_safely(self) -> None:
        blocked = audit_v8_3_portfolio_action_brief_generator(object())

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("Brief override must be" in blocker for blocker in blocked.blockers))

    def test_executable_brief_blocks(self) -> None:
        result = audit_v8_3_portfolio_action_brief_generator()
        bad = replace(
            result.brief,
            creates_buy_request=True,
            connects_broker=True,
            places_order=True,
            executes_trade=True,
            live_fetch_enabled=True,
            network_call_enabled=True,
        )

        blocked = audit_v8_3_portfolio_action_brief_generator(bad)

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("Buy request creation is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("Broker connection is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("Order placement is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("Trade execution is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("Live fetching is forbidden" in blocker for blocker in blocked.blockers))

    def test_safety_flags_preserve_boundaries(self) -> None:
        payload = audit_v8_3_portfolio_action_brief_generator().to_dict()

        self.assertTrue(payload["product_brief_stage"])
        self.assertTrue(payload["final_user_buy_action_required"])
        self.assertTrue(payload["buy_request_deferred"])
        self.assertTrue(payload["broker_connection_forbidden"])
        self.assertTrue(payload["order_placement_forbidden"])
        self.assertTrue(payload["no_trades_executed"])
        self.assertTrue(payload["live_fetch_deferred"])
        self.assertTrue(payload["network_calls_deferred"])


if __name__ == "__main__":
    unittest.main()
