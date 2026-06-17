from types import SimpleNamespace
import unittest

from jarvis.jarvis_v13_0_single_command_operator_launcher import STATUS_READY as V13_0_STATUS_READY
from jarvis.jarvis_v14_0_daily_operator_entrypoint import (
    DAILY_STATUS_COMMAND,
    SAFETY_CHECK_COMMAND,
    STATUS_BLOCKED,
    STATUS_READY,
    build_daily_operator_console_output,
    run_v14_0_daily_operator_entrypoint,
)


def _voice_command(*, allowed=False, blocked=False, unknown=False, output=""):
    return SimpleNamespace(
        allowed=allowed,
        blocked=blocked,
        unknown=unknown,
        output_text=output,
    )


def _launcher_runner(status=V13_0_STATUS_READY, voice_command=None):
    def runner(*, write_ui=False, voice_command_text=None):
        command = voice_command or _voice_command(
            allowed=voice_command_text == DAILY_STATUS_COMMAND,
            blocked=voice_command_text == SAFETY_CHECK_COMMAND,
            unknown=False,
            output="No execution action was taken." if voice_command_text == SAFETY_CHECK_COMMAND else "ALLOWED: operator status",
        )
        return SimpleNamespace(
            status=status,
            selected_candidate_id="btc_candidate",
            selected_sleeve_id="crypto_core_btc",
            output_path="jarvis/local/ui/jarvis_command_center.html",
            ui_html_written=write_ui,
            voice_command=command,
            static_local_html_only=True,
            typed_voice_shell_only=True,
            no_web_server_started=True,
            no_network_listener_started=True,
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

    return runner


class JarvisV140DailyOperatorEntrypointTests(unittest.TestCase):
    def test_daily_mode_is_ready_and_writes_ui(self) -> None:
        result = run_v14_0_daily_operator_entrypoint(
            mode="daily",
            launcher_runner=_launcher_runner(),
        )

        self.assertEqual(result.status, STATUS_READY)
        self.assertTrue(result.daily_entrypoint_ready)
        self.assertEqual(result.command_text, DAILY_STATUS_COMMAND)
        self.assertTrue(result.ui_html_written)
        self.assertTrue(result.voice_command_allowed)
        self.assertFalse(result.blockers)

    def test_safety_check_blocks_buy_command(self) -> None:
        result = run_v14_0_daily_operator_entrypoint(
            mode="safety_check",
            launcher_runner=_launcher_runner(),
        )

        self.assertEqual(result.status, STATUS_READY)
        self.assertEqual(result.command_text, SAFETY_CHECK_COMMAND)
        self.assertTrue(result.voice_command_blocked)
        self.assertIn("No execution action was taken", result.voice_command_output)

    def test_custom_command_is_available(self) -> None:
        result = run_v14_0_daily_operator_entrypoint(
            mode="custom",
            command_text="Jarvis, summarize operator status.",
            launcher_runner=_launcher_runner(),
        )

        self.assertEqual(result.status, STATUS_READY)
        self.assertTrue(result.custom_voice_command_available)
        self.assertTrue(result.voice_command_processed)

    def test_blocks_when_launcher_not_ready(self) -> None:
        result = run_v14_0_daily_operator_entrypoint(
            mode="daily",
            launcher_runner=_launcher_runner(status="BLOCKED"),
        )

        self.assertEqual(result.status, STATUS_BLOCKED)
        self.assertTrue(any("v13.0 launcher is not ready" in blocker for blocker in result.blockers))

    def test_safety_check_blocks_if_buy_command_not_blocked(self) -> None:
        result = run_v14_0_daily_operator_entrypoint(
            mode="safety_check",
            launcher_runner=_launcher_runner(
                voice_command=_voice_command(allowed=True, blocked=False, output="ALLOWED")
            ),
        )

        self.assertEqual(result.status, STATUS_BLOCKED)
        self.assertTrue(any("Safety-check mode must block" in blocker for blocker in result.blockers))

    def test_no_rebuild_and_safety_flags_hold(self) -> None:
        payload = run_v14_0_daily_operator_entrypoint(
            mode="daily",
            launcher_runner=_launcher_runner(),
        ).to_dict()

        self.assertTrue(payload["short_root_command_available"])
        self.assertTrue(payload["no_strategy_rebuild"])
        self.assertTrue(payload["no_recommendation_rebuild"])
        self.assertTrue(payload["no_evidence_rebuild"])
        self.assertTrue(payload["no_data_refresh_rebuild"])
        self.assertTrue(payload["no_ui_rebuild"])
        self.assertTrue(payload["no_voice_rebuild"])
        self.assertTrue(payload["no_web_server_started"])
        self.assertTrue(payload["no_network_listener_started"])
        self.assertTrue(payload["no_microphone"])
        self.assertTrue(payload["no_speech_to_text"])
        self.assertTrue(payload["no_text_to_speech"])
        self.assertTrue(payload["broker_connection_forbidden"])
        self.assertTrue(payload["order_placement_forbidden"])
        self.assertTrue(payload["no_trades_executed"])

    def test_console_output_is_short_and_operator_friendly(self) -> None:
        result = run_v14_0_daily_operator_entrypoint(
            mode="daily",
            launcher_runner=_launcher_runner(),
        )
        output = build_daily_operator_console_output(result)

        self.assertIn("JARVIS_V14_0_DAILY_OPERATOR_ENTRYPOINT_READY_SAFE", output)
        self.assertIn("btc_candidate", output)
        self.assertIn("safety: no broker", output)


if __name__ == "__main__":
    unittest.main()
