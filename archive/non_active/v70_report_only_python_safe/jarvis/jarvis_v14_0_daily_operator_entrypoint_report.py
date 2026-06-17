"""Report CLI for J.A.R.V.I.S. v14.0 daily operator entrypoint."""

from __future__ import annotations

import argparse

from .jarvis_v14_0_daily_operator_entrypoint import (
    DailyOperatorEntrypointResult,
    run_v14_0_daily_operator_entrypoint,
)


def build_v14_0_daily_operator_entrypoint_report(result: DailyOperatorEntrypointResult) -> str:
    lines = [
        "# J.A.R.V.I.S. v14.0 Daily Operator Entrypoint",
        "",
        f"status: {result.status}",
        f"entrypoint status: {result.entrypoint_status}",
        f"recommended next stage: {result.recommended_next_stage}",
        f"mode: {result.mode}",
        f"command text: {result.command_text}",
        f"launcher status: {result.launcher_status}",
        f"selected candidate id: {result.selected_candidate_id}",
        f"selected sleeve id: {result.selected_sleeve_id}",
        f"output path: {result.output_path}",
        f"UI html written: {result.ui_html_written}",
        f"voice command processed: {result.voice_command_processed}",
        f"voice command allowed: {result.voice_command_allowed}",
        f"voice command blocked: {result.voice_command_blocked}",
        f"voice command unknown: {result.voice_command_unknown}",
        "",
        "## Voice Command Output",
        result.voice_command_output or "none",
        "",
        "## Warnings",
    ]

    lines.extend(f"- {warning}" for warning in result.warnings) if result.warnings else lines.append("- none")

    lines.extend(["", "## Blockers"])
    lines.extend(f"- {blocker}" for blocker in result.blockers) if result.blockers else lines.append("- none")

    lines.extend(
        [
            "",
            "## Daily Use",
            f"- daily entrypoint ready: {result.daily_entrypoint_ready}",
            f"- wraps released launcher: {result.wraps_released_launcher}",
            f"- short root command available: {result.short_root_command_available}",
            f"- daily mode available: {result.daily_mode_available}",
            f"- safety check mode available: {result.safety_check_mode_available}",
            f"- custom voice command available: {result.custom_voice_command_available}",
            f"- demo voice mode available: {result.demo_voice_mode_available}",
            "",
            "## No Rebuilds",
            f"- no strategy rebuild: {result.no_strategy_rebuild}",
            f"- no recommendation rebuild: {result.no_recommendation_rebuild}",
            f"- no evidence rebuild: {result.no_evidence_rebuild}",
            f"- no data refresh rebuild: {result.no_data_refresh_rebuild}",
            f"- no UI rebuild: {result.no_ui_rebuild}",
            f"- no voice rebuild: {result.no_voice_rebuild}",
            "",
            "## Safety",
            f"- static local HTML only: {result.static_local_html_only}",
            f"- typed voice shell only: {result.typed_voice_shell_only}",
            f"- no web server started: {result.no_web_server_started}",
            f"- no network listener started: {result.no_network_listener_started}",
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


def report_v14_0_daily_operator_entrypoint(*, mode: str = "daily") -> str:
    return build_v14_0_daily_operator_entrypoint_report(
        run_v14_0_daily_operator_entrypoint(mode=mode)
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Report J.A.R.V.I.S. v14.0 daily operator entrypoint.")
    parser.add_argument("--safety-check", action="store_true", help="Report safety-check mode instead of daily mode.")
    args = parser.parse_args()

    mode = "safety_check" if args.safety_check else "daily"
    print(report_v14_0_daily_operator_entrypoint(mode=mode))


if __name__ == "__main__":
    main()
