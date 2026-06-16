from types import SimpleNamespace
import unittest

from jarvis.jarvis_v13_0_single_command_operator_launcher import STATUS_READY as V13_0_STATUS_READY
from jarvis.jarvis_v13_1_product_mode_closeout_audit import (
    BLOCKED_EXECUTION_COMMAND,
    STATUS_BLOCKED,
    STATUS_READY,
    audit_v13_1_product_mode_closeout_audit,
)


def _voice_command(blocked: bool = True, output: str = "BLOCKED: No execution action was taken."):
    return SimpleNamespace(
        input_text=BLOCKED_EXECUTION_COMMAND,
        output_text=output,
        blocked=blocked,
        allowed=False,
        unknown=False,
    )


def _launcher(status: str = V13_0_STATUS_READY):
    return SimpleNamespace(
        status=status,
        runtime_status="JARVIS_V10_1_UNIFIED_OPERATOR_RUNTIME_READY_SAFE",
        ui_shell_status="JARVIS_V11_0_COMMAND_CENTER_UI_SHELL_READY_SAFE",
        voice_shell_status="JARVIS_V12_1_LOCAL_VOICE_IO_SHELL_READY_SAFE",
        selected_candidate_id="btc_candidate",
        selected_sleeve_id="crypto_core_btc",
        output_path="jarvis/local/ui/jarvis_command_center.html",
        ui_html_written=False,
        voice_command_processed=True,
        voice_command=_voice_command(),
        runtime_launched=True,
        ui_shell_launched=True,
        voice_shell_launched=True,
        static_local_html_only=True,
        typed_voice_shell_only=True,
        no_web_server_started=True,
        no_network_listener_started=True,
        no_external_asset_loading=True,
        no_microphone=True,
        no_speech_to_text=True,
        no_text_to_speech=True,
        final_user_buy_action_required=True,
        buy_request_deferred=True,
        broker_connection_forbidden=True,
        order_placement_forbidden=True,
        no_trades_executed=True,
        credentials_forbidden=True,
        private_account_data_ingestion_forbidden=True,
    )


class JarvisV131ProductModeCloseoutAuditTests(unittest.TestCase):
    def test_closeout_ready_with_launcher_fixture(self) -> None:
        result = audit_v13_1_product_mode_closeout_audit(launcher_result=_launcher())

        self.assertEqual(result.status, STATUS_READY)
        self.assertTrue(result.product_mode_closeout_ready)
        self.assertTrue(result.launcher_ready)
        self.assertTrue(result.runtime_ready)
        self.assertTrue(result.ui_shell_ready)
        self.assertTrue(result.voice_shell_ready)
        self.assertTrue(result.blocked_buy_command_verified)
        self.assertFalse(result.blockers)
        self.assertEqual(result.recommended_next_stage, "release_tag_product_mode_v13_1")

    def test_closeout_blocks_if_launcher_not_ready(self) -> None:
        result = audit_v13_1_product_mode_closeout_audit(launcher_result=_launcher(status="BLOCKED"))

        self.assertEqual(result.status, STATUS_BLOCKED)
        self.assertTrue(any("v13.0 launcher is not ready" in blocker for blocker in result.blockers))

    def test_closeout_blocks_if_buy_command_not_verified(self) -> None:
        launcher = _launcher()
        launcher.voice_command = _voice_command(blocked=False, output="ALLOWED")
        result = audit_v13_1_product_mode_closeout_audit(launcher_result=launcher)

        self.assertEqual(result.status, STATUS_BLOCKED)
        self.assertTrue(any("Blocked buy command was not verified" in blocker for blocker in result.blockers))

    def test_closeout_confirms_no_feature_rebuild(self) -> None:
        payload = audit_v13_1_product_mode_closeout_audit(launcher_result=_launcher()).to_dict()

        self.assertTrue(payload["no_feature_added"])
        self.assertTrue(payload["no_strategy_rebuild"])
        self.assertTrue(payload["no_recommendation_rebuild"])
        self.assertTrue(payload["no_evidence_rebuild"])
        self.assertTrue(payload["no_data_refresh_rebuild"])
        self.assertTrue(payload["no_ui_rebuild"])
        self.assertTrue(payload["no_voice_rebuild"])

    def test_closeout_preserves_safety_boundary(self) -> None:
        payload = audit_v13_1_product_mode_closeout_audit(launcher_result=_launcher()).to_dict()

        self.assertTrue(payload["static_local_html_only"])
        self.assertTrue(payload["typed_voice_shell_only"])
        self.assertTrue(payload["no_web_server_started"])
        self.assertTrue(payload["no_network_listener_started"])
        self.assertTrue(payload["no_external_asset_loading"])
        self.assertTrue(payload["no_microphone"])
        self.assertTrue(payload["no_speech_to_text"])
        self.assertTrue(payload["no_text_to_speech"])
        self.assertTrue(payload["final_user_buy_action_required"])
        self.assertTrue(payload["buy_request_deferred"])
        self.assertTrue(payload["broker_connection_forbidden"])
        self.assertTrue(payload["order_placement_forbidden"])
        self.assertTrue(payload["no_trades_executed"])
        self.assertTrue(payload["credentials_forbidden"])
        self.assertTrue(payload["private_account_data_ingestion_forbidden"])


if __name__ == "__main__":
    unittest.main()
