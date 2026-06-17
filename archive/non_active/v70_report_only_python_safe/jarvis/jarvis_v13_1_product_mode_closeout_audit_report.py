"""Report CLI for J.A.R.V.I.S. v13.1 product mode closeout audit."""

from __future__ import annotations

import argparse

from .jarvis_v13_1_product_mode_closeout_audit import (
    ProductModeCloseoutAuditResult,
    audit_v13_1_product_mode_closeout_audit,
)


def build_v13_1_product_mode_closeout_audit_report(
    result: ProductModeCloseoutAuditResult,
) -> str:
    lines = [
        "# J.A.R.V.I.S. v13.1 Product Mode Closeout Audit",
        "",
        f"status: {result.status}",
        f"closeout status: {result.closeout_status}",
        f"recommended next stage: {result.recommended_next_stage}",
        f"launcher status: {result.launcher_status}",
        f"runtime status: {result.runtime_status}",
        f"UI shell status: {result.ui_shell_status}",
        f"voice shell status: {result.voice_shell_status}",
        f"selected candidate id: {result.selected_candidate_id}",
        f"selected sleeve id: {result.selected_sleeve_id}",
        f"output path: {result.output_path}",
        f"UI html written: {result.ui_html_written}",
        f"blocked execution command: {result.blocked_execution_command}",
        f"blocked execution command processed: {result.blocked_execution_command_processed}",
        f"blocked execution command blocked: {result.blocked_execution_command_blocked}",
        f"blocked buy command verified: {result.blocked_buy_command_verified}",
        f"blocker count: {result.blocker_count}",
        f"warning count: {result.warning_count}",
        "",
        "## Blocked Execution Command Output",
        result.blocked_execution_command_output or "none",
        "",
        "## Warnings",
    ]

    lines.extend(f"- {warning}" for warning in result.warnings) if result.warnings else lines.append("- none")

    lines.extend(["", "## Blockers"])
    lines.extend(f"- {blocker}" for blocker in result.blockers) if result.blockers else lines.append("- none")

    lines.extend(
        [
            "",
            "## Product Closeout",
            f"- product mode closeout ready: {result.product_mode_closeout_ready}",
            f"- launcher ready: {result.launcher_ready}",
            f"- runtime ready: {result.runtime_ready}",
            f"- UI shell ready: {result.ui_shell_ready}",
            f"- voice shell ready: {result.voice_shell_ready}",
            f"- local UI path available: {result.local_ui_path_available}",
            f"- typed voice shell available: {result.typed_voice_shell_available}",
            f"- no feature added: {result.no_feature_added}",
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


def report_v13_1_product_mode_closeout_audit(*, write_ui: bool = False) -> str:
    return build_v13_1_product_mode_closeout_audit_report(
        audit_v13_1_product_mode_closeout_audit(write_ui=write_ui)
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Report J.A.R.V.I.S. v13.1 product mode closeout audit.")
    parser.add_argument("--write-ui", action="store_true", help="Generate the static local command-center HTML through v13.0.")
    args = parser.parse_args()
    print(report_v13_1_product_mode_closeout_audit(write_ui=args.write_ui))


if __name__ == "__main__":
    main()
