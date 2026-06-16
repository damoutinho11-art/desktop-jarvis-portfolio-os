import unittest

from jarvis.jarvis_v10_1_unified_operator_runtime import (
    STATUS_READY,
    audit_v10_1_unified_operator_runtime,
    build_voice_ready_operator_summary,
)


class JarvisV101UnifiedOperatorRuntimeTests(unittest.TestCase):
    def test_unified_operator_runtime_is_ready(self) -> None:
        result = audit_v10_1_unified_operator_runtime()

        self.assertEqual(result.status, STATUS_READY)
        self.assertTrue(result.unified_operator_runtime_ready)
        self.assertEqual(result.recommended_next_stage, "v11_0_command_center_ui_shell")
        self.assertEqual(result.component_count, 6)
        self.assertEqual(result.ready_component_count, 6)
        self.assertEqual(result.blocked_component_count, 0)
        self.assertFalse(result.blockers)

    def test_existing_layers_are_integrated_without_rebuilding(self) -> None:
        result = audit_v10_1_unified_operator_runtime()
        component_ids = {component.component_id for component in result.components}

        self.assertIn("autonomous_public_data_refresh_runtime", component_ids)
        self.assertIn("public_market_intelligence_dashboard", component_ids)
        self.assertIn("weekly_recommendation_draft", component_ids)
        self.assertIn("recommendation_dashboard", component_ids)
        self.assertIn("weekly_recommendation_evidence_pack", component_ids)
        self.assertIn("portfolio_action_brief", component_ids)

        self.assertTrue(result.data_refresh_integrated)
        self.assertTrue(result.evidence_pack_integrated)
        self.assertTrue(result.recommendation_integrated)
        self.assertTrue(result.dashboard_integrated)
        self.assertTrue(result.action_brief_integrated)

    def test_data_status_is_visible_but_current_quality_is_not_overclaimed(self) -> None:
        result = audit_v10_1_unified_operator_runtime()

        self.assertTrue(result.data_source_manifest_loaded)
        self.assertTrue(result.autonomous_refresh_ready)
        self.assertTrue(result.ready_for_downstream_normalization)
        self.assertFalse(result.recommendation_quality_current_data)

    def test_voice_ready_summary_exists_without_claiming_voice_interface(self) -> None:
        result = audit_v10_1_unified_operator_runtime()

        self.assertTrue(result.voice_summary_ready)
        self.assertFalse(result.voice_interface_available)
        self.assertIn("J.A.R.V.I.S. operator summary", result.voice_summary)
        self.assertIn("No buy request", result.voice_summary)
        self.assertIn("final real-world buy", result.voice_summary)

    def test_manual_final_buy_safety_boundary_holds(self) -> None:
        payload = audit_v10_1_unified_operator_runtime().to_dict()

        self.assertTrue(payload["one_command_runtime"])
        self.assertTrue(payload["product_mode_runtime"])
        self.assertTrue(payload["final_user_buy_action_required"])
        self.assertTrue(payload["buy_request_deferred"])
        self.assertTrue(payload["broker_connection_forbidden"])
        self.assertTrue(payload["order_placement_forbidden"])
        self.assertTrue(payload["no_trades_executed"])
        self.assertTrue(payload["credentials_forbidden"])
        self.assertTrue(payload["private_account_data_ingestion_forbidden"])

        for component in payload["components"]:
            self.assertTrue(component["user_visible"])
            self.assertFalse(component["creates_buy_request"])
            self.assertFalse(component["connects_broker"])
            self.assertFalse(component["places_order"])
            self.assertFalse(component["executes_trade"])

    def test_voice_summary_builder_mentions_current_data_truthfully(self) -> None:
        summary = build_voice_ready_operator_summary(
            selected_candidate_id="btc_candidate",
            selected_sleeve_id="crypto_core_btc",
            data_ready=False,
            raw_public_data_refreshed=False,
            evidence_ready=True,
            recommendation_ready=True,
            action_brief_ready=True,
        )

        self.assertIn("btc_candidate", summary)
        self.assertIn("recommendation-quality current data is not yet confirmed", summary)
        self.assertIn("No broker is connected", summary)


if __name__ == "__main__":
    unittest.main()
