from types import SimpleNamespace
import unittest

from jarvis.jarvis_v12_0_voice_operator_interface_boundary import STATUS_READY as V12_0_STATUS_READY
from jarvis.jarvis_v12_1_local_voice_io_shell import (
    STATUS_BLOCKED,
    STATUS_READY,
    audit_v12_1_local_voice_io_shell,
    handle_local_voice_io_command,
)


def _boundary(status: str = V12_0_STATUS_READY):
    return SimpleNamespace(
        status=status,
        selected_candidate_id="btc_candidate",
        selected_sleeve_id="crypto_core_btc",
        command_center_ui_ready=True,
        voice_summary_ready=True,
    )


class JarvisV121LocalVoiceIoShellTests(unittest.TestCase):
    def test_allowed_command_produces_allowed_shell_output(self) -> None:
        turn = handle_local_voice_io_command(
            "Jarvis, summarize operator status.",
            boundary_result=_boundary(),
        )

        self.assertTrue(turn.allowed)
        self.assertFalse(turn.blocked)
        self.assertIn("ALLOWED:", turn.shell_output)
        self.assertIn("btc_candidate", turn.shell_output)
        self.assertTrue(turn.safe_turn_only())

    def test_blocked_buy_command_produces_blocked_shell_output_without_execution(self) -> None:
        turn = handle_local_voice_io_command(
            "Jarvis, buy BTC now.",
            boundary_result=_boundary(),
        )

        self.assertFalse(turn.allowed)
        self.assertTrue(turn.blocked)
        self.assertIn("BLOCKED:", turn.shell_output)
        self.assertIn("No execution action was taken", turn.shell_output)
        self.assertFalse(turn.creates_buy_request)
        self.assertFalse(turn.connects_broker)
        self.assertFalse(turn.places_order)
        self.assertFalse(turn.executes_trade)
        self.assertTrue(turn.safe_turn_only())

    def test_unknown_command_is_safe_and_guided(self) -> None:
        turn = handle_local_voice_io_command(
            "Jarvis, tell me a joke.",
            boundary_result=_boundary(),
        )

        self.assertFalse(turn.allowed)
        self.assertFalse(turn.blocked)
        self.assertTrue(turn.unknown)
        self.assertIn("UNKNOWN:", turn.shell_output)
        self.assertIn("I cannot buy", turn.shell_output)
        self.assertTrue(turn.safe_turn_only())

    def test_specific_voice_commands_have_specific_shell_outputs(self) -> None:
        cases = {
            "Jarvis, explain missing data.": "Missing-data review is available",
            "Jarvis, show the command center.": "jarvis/local/ui/jarvis_command_center.html",
            "Jarvis, read the voice summary.": "microphone, STT, and TTS are not implemented",
        }

        for command, expected in cases.items():
            with self.subTest(command=command):
                turn = handle_local_voice_io_command(command, boundary_result=_boundary())
                self.assertTrue(turn.allowed)
                self.assertIn("ALLOWED:", turn.shell_output)
                self.assertIn(expected, turn.shell_output)

    def test_shell_audit_is_ready_with_boundary(self) -> None:
        result = audit_v12_1_local_voice_io_shell(boundary_result=_boundary())

        self.assertEqual(result.status, STATUS_READY)
        self.assertTrue(result.local_voice_io_shell_ready)
        self.assertEqual(result.recommended_next_stage, "v13_0_single_command_operator_launcher")
        self.assertGreater(result.allowed_turn_count, 0)
        self.assertGreater(result.blocked_turn_count, 0)
        self.assertGreater(result.unknown_turn_count, 0)
        self.assertTrue(result.execution_intents_blocked)
        self.assertFalse(result.blockers)

    def test_shell_blocks_when_boundary_not_ready(self) -> None:
        result = audit_v12_1_local_voice_io_shell(boundary_result=_boundary(status="BLOCKED"))

        self.assertEqual(result.status, STATUS_BLOCKED)
        self.assertTrue(any("v12.0 voice operator boundary is not ready" in blocker for blocker in result.blockers))

    def test_shell_does_not_claim_audio_implementation(self) -> None:
        payload = audit_v12_1_local_voice_io_shell(boundary_result=_boundary()).to_dict()

        self.assertTrue(payload["typed_terminal_shell_only"])
        self.assertTrue(payload["interactive_loop_available"])
        self.assertTrue(payload["single_command_mode_available"])
        self.assertFalse(payload["microphone_available"])
        self.assertFalse(payload["speech_to_text_available"])
        self.assertFalse(payload["text_to_speech_available"])
        self.assertFalse(payload["wake_word_detection_available"])

    def test_manual_final_buy_boundary_holds(self) -> None:
        payload = audit_v12_1_local_voice_io_shell(boundary_result=_boundary()).to_dict()

        self.assertTrue(payload["final_user_buy_action_required"])
        self.assertTrue(payload["buy_request_deferred"])
        self.assertTrue(payload["broker_connection_forbidden"])
        self.assertTrue(payload["order_placement_forbidden"])
        self.assertTrue(payload["no_trades_executed"])
        self.assertTrue(payload["credentials_forbidden"])
        self.assertTrue(payload["private_account_data_ingestion_forbidden"])


if __name__ == "__main__":
    unittest.main()
