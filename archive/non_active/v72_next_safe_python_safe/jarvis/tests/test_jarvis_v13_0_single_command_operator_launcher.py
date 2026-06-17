from types import SimpleNamespace
import unittest

from jarvis.jarvis_v10_1_unified_operator_runtime import STATUS_READY as V10_1_STATUS_READY
from jarvis.jarvis_v11_0_command_center_ui_shell import STATUS_READY as V11_0_STATUS_READY
from jarvis.jarvis_v12_1_local_voice_io_shell import STATUS_READY as V12_1_STATUS_READY
from jarvis.jarvis_v13_0_single_command_operator_launcher import (
    STATUS_BLOCKED,
    STATUS_READY,
    build_launcher_console_summary,
    run_v13_0_single_command_operator_launcher,
)


def _runtime(status: str = V10_1_STATUS_READY):
    return SimpleNamespace(
        status=status,
        selected_candidate_id="btc_candidate",
        selected_sleeve_id="crypto_core_btc",
        final_user_buy_action_required=True,
        broker_connection_forbidden=True,
        no_trades_executed=True,
    )


def _ui(status: str = V11_0_STATUS_READY):
    return SimpleNamespace(
        status=status,
        selected_candidate_id="btc_candidate",
        selected_sleeve_id="crypto_core_btc",
        output_path="jarvis/local/ui/jarvis_command_center.html",
        html_written=False,
        command_center_ui_shell_ready=True,
        voice_summary_ready=True,
        final_user_buy_action_required=True,
        broker_connection_forbidden=True,
        no_trades_executed=True,
    )


def _voice(status: str = V12_1_STATUS_READY):
    return SimpleNamespace(
        status=status,
        final_user_buy_action_required=True,
        broker_connection_forbidden=True,
        no_trades_executed=True,
    )


class JarvisV130SingleCommandOperatorLauncherTests(unittest.TestCase):
    def test_launcher_ready_with_existing_stack_fixtures(self) -> None:
        result = run_v13_0_single_command_operator_launcher(
            runtime_result=_runtime(),
            ui_shell_result=_ui(),
            voice_shell_result=_voice(),
        )

        self.assertEqual(result.status, STATUS_READY)
        self.assertTrue(result.single_command_launcher_ready)
        self.assertTrue(result.runtime_launched)
        self.assertTrue(result.ui_shell_launched)
        self.assertTrue(result.voice_shell_launched)
        self.assertEqual(result.recommended_next_stage, "v13_1_product_mode_closeout_audit")
        self.assertFalse(result.blockers)

    def test_launcher_processes_blocked_voice_command_without_execution(self) -> None:
        result = run_v13_0_single_command_operator_launcher(
            runtime_result=_runtime(),
            ui_shell_result=_ui(),
            voice_shell_result=_voice(),
            voice_command_text="Jarvis, buy BTC now.",
        )

        self.assertEqual(result.status, STATUS_READY)
        self.assertTrue(result.voice_command_processed)
        self.assertIsNotNone(result.voice_command)
        self.assertTrue(result.voice_command.blocked)
        self.assertFalse(result.voice_command.allowed)
        self.assertIn("No execution action was taken", result.voice_command.output_text)

    def test_launcher_blocks_if_runtime_not_ready(self) -> None:
        result = run_v13_0_single_command_operator_launcher(
            runtime_result=_runtime(status="BLOCKED"),
            ui_shell_result=_ui(),
            voice_shell_result=_voice(),
        )

        self.assertEqual(result.status, STATUS_BLOCKED)
        self.assertTrue(any("v10.1 runtime is not ready" in blocker for blocker in result.blockers))

    def test_launcher_blocks_if_ui_not_ready(self) -> None:
        result = run_v13_0_single_command_operator_launcher(
            runtime_result=_runtime(),
            ui_shell_result=_ui(status="BLOCKED"),
            voice_shell_result=_voice(),
        )

        self.assertEqual(result.status, STATUS_BLOCKED)
        self.assertTrue(any("v11.0 UI shell is not ready" in blocker for blocker in result.blockers))

    def test_launcher_blocks_if_voice_shell_not_ready(self) -> None:
        result = run_v13_0_single_command_operator_launcher(
            runtime_result=_runtime(),
            ui_shell_result=_ui(),
            voice_shell_result=_voice(status="BLOCKED"),
        )

        self.assertEqual(result.status, STATUS_BLOCKED)
        self.assertTrue(any("v12.1 local voice shell is not ready" in blocker for blocker in result.blockers))

    def test_launcher_preserves_safety_flags(self) -> None:
        payload = run_v13_0_single_command_operator_launcher(
            runtime_result=_runtime(),
            ui_shell_result=_ui(),
            voice_shell_result=_voice(),
        ).to_dict()

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

    def test_console_summary_is_operator_friendly(self) -> None:
        result = run_v13_0_single_command_operator_launcher(
            runtime_result=_runtime(),
            ui_shell_result=_ui(),
            voice_shell_result=_voice(),
        )
        summary = build_launcher_console_summary(result)

        self.assertIn("JARVIS_V13_0_SINGLE_COMMAND_OPERATOR_LAUNCHER_READY_SAFE", summary)
        self.assertIn("btc_candidate", summary)
        self.assertIn("no broker", summary)


if __name__ == "__main__":
    unittest.main()
