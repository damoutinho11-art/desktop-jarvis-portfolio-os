"""Report CLI for J.A.R.V.I.S. v12.1 local voice I/O shell."""

from __future__ import annotations

import argparse

from .jarvis_v12_1_local_voice_io_shell import (
    LocalVoiceIoShellResult,
    audit_v12_1_local_voice_io_shell,
)


def build_v12_1_local_voice_io_shell_report(result: LocalVoiceIoShellResult) -> str:
    lines = [
        "# J.A.R.V.I.S. v12.1 Local Voice I/O Shell",
        "",
        f"status: {result.status}",
        f"shell status: {result.shell_status}",
        f"recommended next stage: {result.recommended_next_stage}",
        f"boundary status: {result.boundary_status}",
        f"selected candidate id: {result.selected_candidate_id}",
        f"selected sleeve id: {result.selected_sleeve_id}",
        f"command center UI ready: {result.command_center_ui_ready}",
        f"voice summary ready: {result.voice_summary_ready}",
        f"command count: {result.command_count}",
        f"allowed turn count: {result.allowed_turn_count}",
        f"blocked turn count: {result.blocked_turn_count}",
        f"unknown turn count: {result.unknown_turn_count}",
        "",
        "## Shell Turns",
    ]

    for turn in result.turns:
        lines.extend(
            [
                "",
                f"### {turn.intent_id}",
                f"- input: {turn.input_text}",
                f"- intent status: {turn.intent_status}",
                f"- allowed: {turn.allowed}",
                f"- blocked: {turn.blocked}",
                f"- unknown: {turn.unknown}",
                f"- shell output: {turn.shell_output}",
                f"- creates buy request: {turn.creates_buy_request}",
                f"- connects broker: {turn.connects_broker}",
                f"- places order: {turn.places_order}",
                f"- executes trade: {turn.executes_trade}",
                f"- uses credentials: {turn.uses_credentials}",
                f"- ingests private account data: {turn.ingests_private_account_data}",
            ]
        )

    lines.extend(["", "## Warnings"])
    lines.extend(f"- {warning}" for warning in result.warnings) if result.warnings else lines.append("- none")

    lines.extend(["", "## Blockers"])
    lines.extend(f"- {blocker}" for blocker in result.blockers) if result.blockers else lines.append("- none")

    lines.extend(
        [
            "",
            "## Safety",
            f"- local voice I/O shell ready: {result.local_voice_io_shell_ready}",
            f"- typed terminal shell only: {result.typed_terminal_shell_only}",
            f"- interactive loop available: {result.interactive_loop_available}",
            f"- single command mode available: {result.single_command_mode_available}",
            f"- microphone available: {result.microphone_available}",
            f"- speech to text available: {result.speech_to_text_available}",
            f"- text to speech available: {result.text_to_speech_available}",
            f"- wake word detection available: {result.wake_word_detection_available}",
            f"- execution intents blocked: {result.execution_intents_blocked}",
            f"- final user buy action required: {result.final_user_buy_action_required}",
            f"- buy request deferred: {result.buy_request_deferred}",
            f"- broker connection forbidden: {result.broker_connection_forbidden}",
            f"- order placement forbidden: {result.order_placement_forbidden}",
            f"- no trades executed: {result.no_trades_executed}",
            f"- credentials forbidden: {result.credentials_forbidden}",
            f"- private account data ingestion forbidden: {result.private_account_data_ingestion_forbidden}",
        ]
    )

    return "\n".join(lines) + "\n"


def report_v12_1_local_voice_io_shell() -> str:
    return build_v12_1_local_voice_io_shell_report(audit_v12_1_local_voice_io_shell())


def main() -> None:
    parser = argparse.ArgumentParser(description="Report J.A.R.V.I.S. v12.1 local voice I/O shell.")
    parser.parse_args()
    print(report_v12_1_local_voice_io_shell())


if __name__ == "__main__":
    main()
