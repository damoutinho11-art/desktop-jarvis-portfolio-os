"""Report CLI for J.A.R.V.I.S. v13.0 single command operator launcher."""

from __future__ import annotations

import argparse

from .jarvis_v13_0_single_command_operator_launcher import (
    SingleCommandOperatorLauncherResult,
    run_v13_0_single_command_operator_launcher,
)


def build_v13_0_single_command_operator_launcher_report(
    result: SingleCommandOperatorLauncherResult,
) -> str:
    lines = [
        "# J.A.R.V.I.S. v13.0 Single Command Operator Launcher",
        "",
        f"status: {result.status}",
        f"launcher status: {result.launcher_status}",
        f"recommended next stage: {result.recommended_next_stage}",
        f"runtime status: {result.runtime_status}",
        f"ui shell status: {result.ui_shell_status}",
        f"voice shell status: {result.voice_shell_status}",
        f"selected candidate id: {result.selected_candidate_id}",
        f"selected sleeve id: {result.selected_sleeve_id}",
        f"output path: {result.output_path}",
        f"ui html written: {result.ui_html_written}",
        f"voice demo available: {result.voice_demo_available}",
        f"voice command processed: {result.voice_command_processed}",
        f"command count: {result.command_count}",
        f"blocker count: {result.blocker_count}",
        f"warning count: {result.warning_count}",
        "",
        "## Voice Command",
    ]

    if result.voice_command:
        lines.extend(
            [
                f"- input: {result.voice_command.input_text}",
                f"- allowed: {result.voice_command.allowed}",
                f"- blocked: {result.voice_command.blocked}",
                f"- unknown: {result.voice_command.unknown}",
                f"- output: {result.voice_command.output_text}",
            ]
        )
    else:
        lines.append("- none")

    lines.extend(["", "## Warnings"])
    lines.extend(f"- {warning}" for warning in result.warnings) if result.warnings else lines.append("- none")

    lines.extend(["", "## Blockers"])
    lines.extend(f"- {blocker}" for blocker in result.blockers) if result.blockers else lines.append("- none")

    lines.extend(
        [
            "",
            "## Safety",
            f"- single command launcher ready: {result.single_command_launcher_ready}",
            f"- runtime launched: {result.runtime_launched}",
            f"- UI shell launched: {result.ui_shell_launched}",
            f"- voice shell launched: {result.voice_shell_launched}",
            f"- static local HTML only: {result.static_local_html_only}",
            f"- typed voice shell only: {result.typed_voice_shell_only}",
            f"- no web server started: {result.no_web_server_started}",
            f"- no network listener started: {result.no_network_listener_started}",
            f"- no external asset loading: {result.no_external_asset_loading}",
            f"- no microphone: {result.no_microphone}",
            f"- no speech to text: {result.no_speech_to_text}",
            f"- no text to speech: {result.no_text_to_speech}",
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


def report_v13_0_single_command_operator_launcher(*, write_ui: bool = False) -> str:
    return build_v13_0_single_command_operator_launcher_report(
        run_v13_0_single_command_operator_launcher(write_ui=write_ui)
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Report J.A.R.V.I.S. v13.0 single command operator launcher.")
    parser.add_argument("--write-ui", action="store_true", help="Generate the static local command-center HTML.")
    args = parser.parse_args()
    print(report_v13_0_single_command_operator_launcher(write_ui=args.write_ui))


if __name__ == "__main__":
    main()
