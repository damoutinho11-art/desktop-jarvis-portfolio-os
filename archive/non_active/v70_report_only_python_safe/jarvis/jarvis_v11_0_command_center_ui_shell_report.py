"""Report CLI for J.A.R.V.I.S. v11.0 command center UI shell."""

from __future__ import annotations

import argparse

from .jarvis_v11_0_command_center_ui_shell import (
    CommandCenterUiShellResult,
    audit_v11_0_command_center_ui_shell,
)


def build_v11_0_command_center_ui_shell_report(result: CommandCenterUiShellResult) -> str:
    lines = [
        "# J.A.R.V.I.S. v11.0 Command Center UI Shell",
        "",
        f"status: {result.status}",
        f"ui shell status: {result.ui_shell_status}",
        f"recommended next stage: {result.recommended_next_stage}",
        f"runtime status: {result.runtime_status}",
        f"selected candidate id: {result.selected_candidate_id}",
        f"selected sleeve id: {result.selected_sleeve_id}",
        f"output path: {result.output_path}",
        f"html rendered: {result.html_rendered}",
        f"html written: {result.html_written}",
        f"section count: {result.section_count}",
        f"ready section count: {result.ready_section_count}",
        f"blocked section count: {result.blocked_section_count}",
        f"component count: {result.component_count}",
        f"voice summary ready: {result.voice_summary_ready}",
        f"voice interface available: {result.voice_interface_available}",
        "",
        "## UI Sections",
    ]

    for section in result.ui_sections:
        lines.extend(
            [
                "",
                f"### {section.section_id}",
                f"- title: {section.title}",
                f"- ready: {section.ready}",
                f"- summary: {section.summary}",
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
            f"- command center UI shell ready: {result.command_center_ui_shell_ready}",
            f"- static local HTML only: {result.static_local_html_only}",
            f"- web server started: {result.web_server_started}",
            f"- network listener started: {result.network_listener_started}",
            f"- external asset loading: {result.external_asset_loading}",
            f"- runtime rebuilt: {result.runtime_rebuilt}",
            f"- recommendation rebuilt: {result.recommendation_rebuilt}",
            f"- evidence rebuilt: {result.evidence_rebuilt}",
            f"- data refresh rebuilt: {result.data_refresh_rebuilt}",
            f"- voice interface built: {result.voice_interface_built}",
            f"- buy button disabled: {result.buy_button_disabled}",
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


def report_v11_0_command_center_ui_shell(*, write_file: bool = False) -> str:
    return build_v11_0_command_center_ui_shell_report(
        audit_v11_0_command_center_ui_shell(write_file=write_file)
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Report J.A.R.V.I.S. v11.0 command center UI shell.")
    parser.add_argument("--write-file", action="store_true", help="Write the static local HTML command center.")
    args = parser.parse_args()
    print(report_v11_0_command_center_ui_shell(write_file=args.write_file))


if __name__ == "__main__":
    main()
