from types import SimpleNamespace
import tempfile
import unittest
from pathlib import Path

from jarvis.jarvis_v10_1_unified_operator_runtime import STATUS_READY as V10_1_STATUS_READY
from jarvis.jarvis_v11_0_command_center_ui_shell import (
    STATUS_BLOCKED,
    STATUS_READY,
    audit_v11_0_command_center_ui_shell,
    build_command_center_ui_sections,
    render_command_center_html,
)


def _component(component_id: str = "component"):
    return SimpleNamespace(
        component_id=component_id,
        status="READY",
        ready=True,
        summary="ready component",
        creates_buy_request=False,
        connects_broker=False,
        places_order=False,
        executes_trade=False,
    )


def _runtime(status: str = V10_1_STATUS_READY):
    return SimpleNamespace(
        status=status,
        runtime_status="UNIFIED_OPERATOR_RUNTIME_READY",
        selected_candidate_id="btc_candidate",
        selected_sleeve_id="crypto_core_btc",
        component_count=2,
        components=(_component("data"), _component("brief")),
        data_refresh_integrated=True,
        data_source_manifest_loaded=True,
        autonomous_refresh_ready=True,
        raw_public_data_refreshed=False,
        recommendation_quality_current_data=False,
        evidence_pack_integrated=True,
        evidence_pack_status="EVIDENCE_READY",
        recommendation_integrated=True,
        recommendation_status="RECOMMENDATION_READY",
        recommendation_dashboard_status="DASHBOARD_READY",
        dashboard_integrated=True,
        public_market_dashboard_status="PUBLIC_DASHBOARD_READY",
        action_brief_integrated=True,
        action_brief_status="ACTION_BRIEF_READY",
        voice_ready_summary_integrated=True,
        voice_summary_ready=True,
        voice_interface_available=False,
        voice_summary="J.A.R.V.I.S. operator summary. No buy request. No broker is connected.",
        final_user_buy_action_required=True,
        broker_connection_forbidden=True,
        order_placement_forbidden=True,
        no_trades_executed=True,
    )


class JarvisV110CommandCenterUiShellTests(unittest.TestCase):
    def test_sections_are_built_from_runtime_fixture(self) -> None:
        sections = build_command_center_ui_sections(_runtime())

        self.assertEqual(len(sections), 7)
        self.assertTrue(any(section.section_id == "data_refresh" for section in sections))
        self.assertTrue(any(section.section_id == "manual_buy_boundary" for section in sections))
        self.assertTrue(all(section.ready for section in sections))

    def test_html_renders_static_command_center(self) -> None:
        html = render_command_center_html(_runtime())

        self.assertIn("J.A.R.V.I.S. Command Center", html)
        self.assertIn("btc_candidate", html)
        self.assertIn("crypto_core_btc", html)
        self.assertIn("No broker / no order / no trade", html)
        self.assertIn("disabled", html)
        self.assertNotIn("http://", html)
        self.assertNotIn("https://", html)

    def test_audit_ready_without_writing_file(self) -> None:
        result = audit_v11_0_command_center_ui_shell(runtime_result=_runtime())

        self.assertEqual(result.status, STATUS_READY)
        self.assertTrue(result.command_center_ui_shell_ready)
        self.assertTrue(result.html_rendered)
        self.assertFalse(result.html_written)
        self.assertEqual(result.recommended_next_stage, "v12_0_voice_operator_interface_boundary")
        self.assertEqual(result.section_count, 7)
        self.assertEqual(result.ready_section_count, 7)
        self.assertEqual(result.blocked_section_count, 0)
        self.assertFalse(result.blockers)

    def test_audit_writes_local_html_when_requested(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = audit_v11_0_command_center_ui_shell(
                runtime_result=_runtime(),
                write_file=True,
                output_path="jarvis/local/ui/test_command_center.html",
                root=temp_dir,
            )

            self.assertEqual(result.status, STATUS_READY)
            self.assertTrue(result.html_written)
            output = Path(temp_dir) / "jarvis/local/ui/test_command_center.html"
            self.assertTrue(output.is_file())
            self.assertIn("J.A.R.V.I.S. Command Center", output.read_text(encoding="utf-8"))

    def test_blocked_runtime_blocks_ui_shell(self) -> None:
        result = audit_v11_0_command_center_ui_shell(runtime_result=_runtime(status="BLOCKED"))

        self.assertEqual(result.status, STATUS_BLOCKED)
        self.assertTrue(any("v10.1 unified operator runtime is not ready" in blocker for blocker in result.blockers))

    def test_safety_flags_preserve_no_execution_boundary(self) -> None:
        payload = audit_v11_0_command_center_ui_shell(runtime_result=_runtime()).to_dict()

        self.assertTrue(payload["static_local_html_only"])
        self.assertFalse(payload["web_server_started"])
        self.assertFalse(payload["network_listener_started"])
        self.assertFalse(payload["external_asset_loading"])
        self.assertFalse(payload["runtime_rebuilt"])
        self.assertFalse(payload["recommendation_rebuilt"])
        self.assertFalse(payload["evidence_rebuilt"])
        self.assertFalse(payload["data_refresh_rebuilt"])
        self.assertFalse(payload["voice_interface_built"])
        self.assertTrue(payload["buy_button_disabled"])
        self.assertTrue(payload["final_user_buy_action_required"])
        self.assertTrue(payload["broker_connection_forbidden"])
        self.assertTrue(payload["order_placement_forbidden"])
        self.assertTrue(payload["no_trades_executed"])


if __name__ == "__main__":
    unittest.main()
