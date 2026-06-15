import unittest
from dataclasses import replace

from jarvis.jarvis_v8_2_weekly_recommendation_evidence_pack_integration import (
    PACK_STATUS_READY,
    SECTION_STATE_BLOCKED,
    SECTION_STATE_READY,
    SECTION_STATE_WATCH,
    STATUS_BLOCKED,
    STATUS_READY,
    audit_v8_2_weekly_recommendation_evidence_pack_integration,
)


class JarvisV82WeeklyRecommendationEvidencePackIntegrationTests(unittest.TestCase):
    def test_evidence_pack_integration_is_ready_and_points_to_action_brief(self) -> None:
        result = audit_v8_2_weekly_recommendation_evidence_pack_integration()

        self.assertEqual(result.status, STATUS_READY)
        self.assertEqual(result.pack_status, PACK_STATUS_READY)
        self.assertEqual(result.recommended_next_stage, "v8_3_portfolio_action_brief_generator")
        self.assertTrue(result.evidence_pack_integration_ready)
        self.assertTrue(result.compatible_with_v8_1_research_cycle_panel)
        self.assertGreaterEqual(result.section_count, 6)
        self.assertEqual(result.included_section_count, result.section_count)
        self.assertGreaterEqual(result.ready_section_count, 5)
        self.assertGreaterEqual(result.watch_section_count, 1)
        self.assertEqual(result.blocked_section_count, 0)
        self.assertEqual(result.ready_for_pack_section_count, result.section_count)
        self.assertEqual(result.user_visible_section_count, result.section_count)
        self.assertEqual(result.live_fetch_enabled_section_count, 0)
        self.assertEqual(result.network_call_enabled_section_count, 0)
        self.assertEqual(result.raw_response_storage_enabled_section_count, 0)
        self.assertEqual(result.live_adapter_record_emission_enabled_section_count, 0)
        self.assertFalse(result.blockers)

    def test_required_sections_exist(self) -> None:
        result = audit_v8_2_weekly_recommendation_evidence_pack_integration()
        section_ids = {section.section_id for section in result.sections}

        self.assertIn("research_cycle_review_summary", section_ids)
        self.assertIn("selected_candidate_evidence_context", section_ids)
        self.assertIn("public_intelligence_readiness_context", section_ids)
        self.assertIn("provider_binding_context", section_ids)
        self.assertIn("live_data_freshness_watch_context", section_ids)
        self.assertIn("execution_boundary_context", section_ids)

    def test_sections_are_visible_included_and_non_executable(self) -> None:
        result = audit_v8_2_weekly_recommendation_evidence_pack_integration()

        for section in result.sections:
            self.assertTrue(section.user_visible)
            self.assertTrue(section.included_in_weekly_pack)
            self.assertTrue(section.ready_for_pack)
            self.assertTrue(section.final_user_action_required)
            self.assertFalse(section.live_fetch_enabled)
            self.assertFalse(section.network_call_enabled)
            self.assertFalse(section.raw_response_storage_enabled)
            self.assertFalse(section.live_adapter_record_emission_enabled)
            self.assertFalse(section.creates_buy_request)
            self.assertFalse(section.connects_broker)
            self.assertFalse(section.places_order)
            self.assertFalse(section.executes_trade)
            self.assertTrue(section.safe_evidence_pack_section_only())

    def test_watch_section_explains_missing_live_data(self) -> None:
        result = audit_v8_2_weekly_recommendation_evidence_pack_integration()
        watch_sections = [
            section for section in result.sections if section.section_id == "live_data_freshness_watch_context"
        ]

        self.assertEqual(len(watch_sections), 1)
        self.assertEqual(watch_sections[0].state, SECTION_STATE_WATCH)
        self.assertTrue(watch_sections[0].watch_only)
        self.assertTrue(watch_sections[0].ready_for_pack)
        self.assertIn("disabled", watch_sections[0].status_reason.lower())

    def test_product_integration_flags_are_visible(self) -> None:
        result = audit_v8_2_weekly_recommendation_evidence_pack_integration()

        self.assertTrue(result.product_integration_stage)
        self.assertTrue(result.research_review_integrated)
        self.assertTrue(result.selected_candidate_integrated)
        self.assertTrue(result.public_intelligence_integrated)
        self.assertTrue(result.freshness_watch_integrated)
        self.assertTrue(result.execution_boundary_integrated)

    def test_invalid_override_blocks_safely(self) -> None:
        blocked = audit_v8_2_weekly_recommendation_evidence_pack_integration(object())

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("Evidence pack section override must be" in blocker for blocker in blocked.blockers))

    def test_empty_sections_block(self) -> None:
        blocked = audit_v8_2_weekly_recommendation_evidence_pack_integration(())

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("No weekly recommendation evidence pack sections" in blocker for blocker in blocked.blockers))

    def test_duplicate_section_id_blocks(self) -> None:
        result = audit_v8_2_weekly_recommendation_evidence_pack_integration()
        blocked = audit_v8_2_weekly_recommendation_evidence_pack_integration(
            result.sections + (result.sections[0],)
        )

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("unique" in blocker for blocker in blocked.blockers))

    def test_missing_required_section_blocks(self) -> None:
        result = audit_v8_2_weekly_recommendation_evidence_pack_integration()
        sections = tuple(section for section in result.sections if section.section_id != "execution_boundary_context")

        blocked = audit_v8_2_weekly_recommendation_evidence_pack_integration(sections)

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("must include all required" in blocker for blocker in blocked.blockers))

    def test_watch_section_requires_reason(self) -> None:
        result = audit_v8_2_weekly_recommendation_evidence_pack_integration()
        bad = replace(result.sections[0], state=SECTION_STATE_WATCH, status_reason="")

        blocked = audit_v8_2_weekly_recommendation_evidence_pack_integration(
            (bad,) + result.sections[1:]
        )

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("watch sections require" in blocker for blocker in blocked.blockers))

    def test_blocked_section_requires_reason(self) -> None:
        result = audit_v8_2_weekly_recommendation_evidence_pack_integration()
        bad = replace(result.sections[0], state=SECTION_STATE_BLOCKED, status_reason="")

        blocked = audit_v8_2_weekly_recommendation_evidence_pack_integration(
            (bad,) + result.sections[1:]
        )

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("blocked sections require" in blocker for blocker in blocked.blockers))

    def test_not_included_or_not_ready_section_blocks(self) -> None:
        result = audit_v8_2_weekly_recommendation_evidence_pack_integration()
        bad = replace(
            result.sections[0],
            included_in_weekly_pack=False,
            ready_for_pack=False,
        )

        blocked = audit_v8_2_weekly_recommendation_evidence_pack_integration(
            (bad,) + result.sections[1:]
        )

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("must be included in weekly pack" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("must be ready for pack integration" in blocker for blocker in blocked.blockers))

    def test_watch_only_must_use_watch_state(self) -> None:
        result = audit_v8_2_weekly_recommendation_evidence_pack_integration()
        bad = replace(result.sections[0], state=SECTION_STATE_READY, watch_only=True)

        blocked = audit_v8_2_weekly_recommendation_evidence_pack_integration(
            (bad,) + result.sections[1:]
        )

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("watch-only sections must use WATCH state" in blocker for blocker in blocked.blockers))

    def test_hidden_or_unsafe_section_blocks(self) -> None:
        result = audit_v8_2_weekly_recommendation_evidence_pack_integration()
        bad = replace(
            result.sections[0],
            user_visible=False,
            final_user_action_required=False,
            live_fetch_enabled=True,
            network_call_enabled=True,
            raw_response_storage_enabled=True,
            live_adapter_record_emission_enabled=True,
        )

        blocked = audit_v8_2_weekly_recommendation_evidence_pack_integration(
            (bad,) + result.sections[1:]
        )

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("must be user-visible" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("final user action boundary" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("live fetching is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("network calls are forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("raw response storage is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("live adapter record emission is forbidden" in blocker for blocker in blocked.blockers))

    def test_execution_fields_block(self) -> None:
        result = audit_v8_2_weekly_recommendation_evidence_pack_integration()
        bad = replace(
            result.sections[0],
            creates_buy_request=True,
            connects_broker=True,
            places_order=True,
            executes_trade=True,
        )

        blocked = audit_v8_2_weekly_recommendation_evidence_pack_integration(
            (bad,) + result.sections[1:]
        )

        self.assertEqual(blocked.status, STATUS_BLOCKED)
        self.assertTrue(any("buy request creation is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("broker connection is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("order placement is forbidden" in blocker for blocker in blocked.blockers))
        self.assertTrue(any("trade execution is forbidden" in blocker for blocker in blocked.blockers))

    def test_safety_flags_preserve_no_execution_boundary(self) -> None:
        result = audit_v8_2_weekly_recommendation_evidence_pack_integration()
        payload = result.to_dict()

        self.assertTrue(payload["product_integration_stage"])
        self.assertTrue(payload["live_fetch_deferred"])
        self.assertTrue(payload["network_calls_deferred"])
        self.assertTrue(payload["raw_response_storage_deferred"])
        self.assertTrue(payload["live_adapter_record_emission_deferred"])
        self.assertTrue(payload["final_user_buy_action_required"])
        self.assertTrue(payload["buy_request_deferred"])
        self.assertTrue(payload["broker_connection_forbidden"])
        self.assertTrue(payload["order_placement_forbidden"])
        self.assertTrue(payload["no_trades_executed"])


if __name__ == "__main__":
    unittest.main()
