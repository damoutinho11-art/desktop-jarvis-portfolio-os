from types import SimpleNamespace
import unittest

from jarvis.jarvis_v11_0_command_center_ui_shell import STATUS_READY as V11_0_STATUS_READY
from jarvis.jarvis_v12_0_voice_operator_interface_boundary import (
    INTENT_ALLOWED,
    INTENT_BLOCKED,
    INTENT_UNKNOWN,
    STATUS_BLOCKED,
    STATUS_READY,
    audit_v12_0_voice_operator_interface_boundary,
    evaluate_voice_operator_command,
)


def _ui(status: str = V11_0_STATUS_READY):
    return SimpleNamespace(
        status=status,
        voice_summary_ready=True,
        selected_candidate_id="btc_candidate",
        selected_sleeve_id="crypto_core_btc",
    )


class JarvisV120VoiceOperatorInterfaceBoundaryTests(unittest.TestCase):
    def test_allowed_operator_command_is_allowed(self) -> None:
        intent = evaluate_voice_operator_command("Jarvis, summarize operator status.")

        self.assertEqual(intent.status, INTENT_ALLOWED)
        self.assertTrue(intent.allowed)
        self.assertFalse(intent.blocked)
        self.assertTrue(intent.safe_intent_only())

    def test_buy_command_is_blocked(self) -> None:
        intent = evaluate_voice_operator_command("Jarvis, buy BTC now.")

        self.assertEqual(intent.status, INTENT_BLOCKED)
        self.assertFalse(intent.allowed)
        self.assertTrue(intent.blocked)
        self.assertTrue(intent.creates_buy_request)
        self.assertIn("cannot execute", intent.response_text.lower())

    def test_order_broker_credentials_and_private_data_commands_are_blocked(self) -> None:
        samples = (
            "Jarvis, place a market order.",
            "Jarvis, connect my broker.",
            "Jarvis, use my credentials.",
            "Jarvis, ingest private account data.",
        )

        results = [evaluate_voice_operator_command(sample) for sample in samples]

        self.assertTrue(all(result.status == INTENT_BLOCKED for result in results))
        self.assertTrue(results[0].places_order)
        self.assertTrue(results[1].connects_broker)
        self.assertTrue(results[2].uses_credentials)
        self.assertTrue(results[3].ingests_private_account_data)

    def test_unknown_command_is_not_execution(self) -> None:
        intent = evaluate_voice_operator_command("Jarvis, tell me a joke.")

        self.assertEqual(intent.status, INTENT_UNKNOWN)
        self.assertFalse(intent.allowed)
        self.assertFalse(intent.blocked)
        self.assertTrue(intent.safe_intent_only())

    def test_specific_allowed_commands_route_to_specific_intents(self) -> None:
        cases = {
            "Jarvis, explain missing data.": "explain_missing_data",
            "Jarvis, refresh public data status.": "refresh_public_data_status",
            "Jarvis, read the voice summary.": "read_voice_summary",
            "Jarvis, show the command center.": "show_command_center",
        }

        for command, expected_intent in cases.items():
            with self.subTest(command=command):
                intent = evaluate_voice_operator_command(command)
                self.assertEqual(intent.status, INTENT_ALLOWED)
                self.assertEqual(intent.intent_id, expected_intent)
                self.assertTrue(intent.allowed)
                self.assertFalse(intent.blocked)

    def test_boundary_is_ready_with_ui_shell(self) -> None:
        result = audit_v12_0_voice_operator_interface_boundary(ui_shell_result=_ui())

        self.assertEqual(result.status, STATUS_READY)
        self.assertTrue(result.voice_operator_boundary_ready)
        self.assertTrue(result.command_center_ui_ready)
        self.assertEqual(result.recommended_next_stage, "v12_1_local_voice_io_shell")
        self.assertGreater(result.allowed_command_count, 0)
        self.assertGreater(result.blocked_command_count, 0)
        self.assertTrue(result.execution_intents_blocked)
        self.assertFalse(result.blockers)

    def test_boundary_blocks_when_ui_shell_not_ready(self) -> None:
        result = audit_v12_0_voice_operator_interface_boundary(ui_shell_result=_ui(status="BLOCKED"))

        self.assertEqual(result.status, STATUS_BLOCKED)
        self.assertTrue(any("v11.0 command center UI shell is not ready" in blocker for blocker in result.blockers))

    def test_voice_boundary_does_not_claim_audio_implementation(self) -> None:
        result = audit_v12_0_voice_operator_interface_boundary(ui_shell_result=_ui())
        payload = result.to_dict()

        self.assertFalse(payload["voice_interface_available"])
        self.assertFalse(payload["microphone_available"])
        self.assertFalse(payload["speech_to_text_available"])
        self.assertFalse(payload["text_to_speech_available"])
        self.assertTrue(payload["text_command_boundary_only"])
        self.assertTrue(payload["microphone_not_implemented"])
        self.assertTrue(payload["speech_to_text_not_implemented"])
        self.assertTrue(payload["text_to_speech_not_implemented"])

    def test_manual_final_buy_safety_boundary_holds(self) -> None:
        payload = audit_v12_0_voice_operator_interface_boundary(ui_shell_result=_ui()).to_dict()

        self.assertTrue(payload["final_user_buy_action_required"])
        self.assertTrue(payload["buy_request_deferred"])
        self.assertTrue(payload["broker_connection_forbidden"])
        self.assertTrue(payload["order_placement_forbidden"])
        self.assertTrue(payload["no_trades_executed"])
        self.assertTrue(payload["credentials_forbidden"])
        self.assertTrue(payload["private_account_data_ingestion_forbidden"])


if __name__ == "__main__":
    unittest.main()

