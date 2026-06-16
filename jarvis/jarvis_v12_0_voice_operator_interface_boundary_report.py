"""Report CLI for J.A.R.V.I.S. v12.0 voice operator interface boundary."""

from __future__ import annotations

import argparse

from .jarvis_v12_0_voice_operator_interface_boundary import (
    VoiceOperatorBoundaryResult,
    audit_v12_0_voice_operator_interface_boundary,
)


def build_v12_0_voice_operator_interface_boundary_report(
    result: VoiceOperatorBoundaryResult,
) -> str:
    lines = [
        "# J.A.R.V.I.S. v12.0 Voice Operator Interface Boundary",
        "",
        f"status: {result.status}",
        f"boundary status: {result.boundary_status}",
        f"recommended next stage: {result.recommended_next_stage}",
        f"ui shell status: {result.ui_shell_status}",
        f"selected candidate id: {result.selected_candidate_id}",
        f"selected sleeve id: {result.selected_sleeve_id}",
        f"command count: {result.command_count}",
        f"allowed command count: {result.allowed_command_count}",
        f"blocked command count: {result.blocked_command_count}",
        f"unknown command count: {result.unknown_command_count}",
        f"voice summary ready: {result.voice_summary_ready}",
        f"voice interface available: {result.voice_interface_available}",
        f"microphone available: {result.microphone_available}",
        f"speech to text available: {result.speech_to_text_available}",
        f"text to speech available: {result.text_to_speech_available}",
        f"command center UI ready: {result.command_center_ui_ready}",
        "",
        "## Voice Intent Samples",
    ]

    for intent in result.intents:
        lines.extend(
            [
                "",
                f"### {intent.intent_id}",
                f"- status: {intent.status}",
                f"- spoken text: {intent.spoken_text}",
                f"- allowed: {intent.allowed}",
                f"- blocked: {intent.blocked}",
                f"- matched terms: {', '.join(intent.matched_terms) if intent.matched_terms else 'none'}",
                f"- response: {intent.response_text}",
                f"- creates buy request: {intent.creates_buy_request}",
                f"- connects broker: {intent.connects_broker}",
                f"- places order: {intent.places_order}",
                f"- executes trade: {intent.executes_trade}",
                f"- uses credentials: {intent.uses_credentials}",
                f"- ingests private account data: {intent.ingests_private_account_data}",
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
            f"- voice operator boundary ready: {result.voice_operator_boundary_ready}",
            f"- text command boundary only: {result.text_command_boundary_only}",
            f"- microphone not implemented: {result.microphone_not_implemented}",
            f"- speech to text not implemented: {result.speech_to_text_not_implemented}",
            f"- text to speech not implemented: {result.text_to_speech_not_implemented}",
            f"- execution intents blocked: {result.execution_intents_blocked}",
            f"- allowed operator intents available: {result.allowed_operator_intents_available}",
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


def report_v12_0_voice_operator_interface_boundary() -> str:
    return build_v12_0_voice_operator_interface_boundary_report(
        audit_v12_0_voice_operator_interface_boundary()
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Report J.A.R.V.I.S. v12.0 voice operator boundary.")
    parser.parse_args()
    print(report_v12_0_voice_operator_interface_boundary())


if __name__ == "__main__":
    main()
