"""J.A.R.V.I.S. v13.0 single command operator launcher.

This stage adds one safe product launcher over the current operator stack:

- v10.1 unified operator runtime;
- v11.0 static local command-center UI shell;
- v12.1 typed local voice I/O shell.

It does not rebuild strategy, recommendation, evidence, data refresh, UI, or voice
logic. It orchestrates them.

Safety boundary:
- no broker connection;
- no credentials;
- no private account ingestion;
- no buy request;
- no order placement;
- no trade execution;
- final real-world buy remains Diogo's manual action outside J.A.R.V.I.S.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from types import SimpleNamespace
from typing import Any

from .jarvis_v10_1_unified_operator_runtime import (
    STATUS_READY as V10_1_STATUS_READY,
    audit_v10_1_unified_operator_runtime,
)
from .jarvis_v11_0_command_center_ui_shell import (
    DEFAULT_UI_OUTPUT_PATH,
    STATUS_READY as V11_0_STATUS_READY,
    audit_v11_0_command_center_ui_shell,
)
from .jarvis_v12_0_voice_operator_interface_boundary import STATUS_READY as V12_0_STATUS_READY
from .jarvis_v12_1_local_voice_io_shell import (
    STATUS_READY as V12_1_STATUS_READY,
    DEFAULT_COMMAND_SAMPLES,
    audit_v12_1_local_voice_io_shell,
    handle_local_voice_io_command,
)


STATUS_READY = "JARVIS_V13_0_SINGLE_COMMAND_OPERATOR_LAUNCHER_READY_SAFE"
STATUS_BLOCKED = "JARVIS_V13_0_SINGLE_COMMAND_OPERATOR_LAUNCHER_BLOCKED_SAFE"

LAUNCHER_READY = "SINGLE_COMMAND_OPERATOR_LAUNCHER_READY"
LAUNCHER_BLOCKED = "SINGLE_COMMAND_OPERATOR_LAUNCHER_BLOCKED"

NEXT_STAGE = "v13_1_product_mode_closeout_audit"


@dataclass(frozen=True)
class OperatorLauncherVoiceCommand:
    input_text: str
    output_text: str
    blocked: bool
    allowed: bool
    unknown: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "input_text": self.input_text,
            "output_text": self.output_text,
            "blocked": self.blocked,
            "allowed": self.allowed,
            "unknown": self.unknown,
        }


@dataclass(frozen=True)
class SingleCommandOperatorLauncherResult:
    status: str
    launcher_status: str
    recommended_next_stage: str
    runtime_status: str
    ui_shell_status: str
    voice_shell_status: str
    selected_candidate_id: str
    selected_sleeve_id: str
    output_path: str
    ui_html_written: bool
    voice_demo_available: bool
    voice_command_processed: bool
    voice_command: OperatorLauncherVoiceCommand | None
    command_count: int
    blocker_count: int
    warning_count: int
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    single_command_launcher_ready: bool
    runtime_launched: bool
    ui_shell_launched: bool
    voice_shell_launched: bool
    static_local_html_only: bool
    typed_voice_shell_only: bool
    no_web_server_started: bool
    no_network_listener_started: bool
    no_external_asset_loading: bool
    no_microphone: bool
    no_speech_to_text: bool
    no_text_to_speech: bool
    final_user_buy_action_required: bool
    buy_request_deferred: bool
    broker_connection_forbidden: bool
    order_placement_forbidden: bool
    no_trades_executed: bool
    credentials_forbidden: bool
    private_account_data_ingestion_forbidden: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "launcher_status": self.launcher_status,
            "recommended_next_stage": self.recommended_next_stage,
            "runtime_status": self.runtime_status,
            "ui_shell_status": self.ui_shell_status,
            "voice_shell_status": self.voice_shell_status,
            "selected_candidate_id": self.selected_candidate_id,
            "selected_sleeve_id": self.selected_sleeve_id,
            "output_path": self.output_path,
            "ui_html_written": self.ui_html_written,
            "voice_demo_available": self.voice_demo_available,
            "voice_command_processed": self.voice_command_processed,
            "voice_command": self.voice_command.to_dict() if self.voice_command else None,
            "command_count": self.command_count,
            "blocker_count": self.blocker_count,
            "warning_count": self.warning_count,
            "blockers": list(self.blockers),
            "warnings": list(self.warnings),
            "single_command_launcher_ready": self.single_command_launcher_ready,
            "runtime_launched": self.runtime_launched,
            "ui_shell_launched": self.ui_shell_launched,
            "voice_shell_launched": self.voice_shell_launched,
            "static_local_html_only": self.static_local_html_only,
            "typed_voice_shell_only": self.typed_voice_shell_only,
            "no_web_server_started": self.no_web_server_started,
            "no_network_listener_started": self.no_network_listener_started,
            "no_external_asset_loading": self.no_external_asset_loading,
            "no_microphone": self.no_microphone,
            "no_speech_to_text": self.no_speech_to_text,
            "no_text_to_speech": self.no_text_to_speech,
            "final_user_buy_action_required": self.final_user_buy_action_required,
            "buy_request_deferred": self.buy_request_deferred,
            "broker_connection_forbidden": self.broker_connection_forbidden,
            "order_placement_forbidden": self.order_placement_forbidden,
            "no_trades_executed": self.no_trades_executed,
            "credentials_forbidden": self.credentials_forbidden,
            "private_account_data_ingestion_forbidden": self.private_account_data_ingestion_forbidden,
        }


def _get_text(obj: Any, name: str, default: str = "") -> str:
    return str(getattr(obj, name, default) if getattr(obj, name, default) is not None else default)


def _get_bool(obj: Any, name: str, default: bool = False) -> bool:
    return bool(getattr(obj, name, default))


def build_v12_boundary_context_from_ui(ui_shell_result: Any) -> SimpleNamespace:
    return SimpleNamespace(
        status=V12_0_STATUS_READY,
        selected_candidate_id=_get_text(ui_shell_result, "selected_candidate_id", "unknown"),
        selected_sleeve_id=_get_text(ui_shell_result, "selected_sleeve_id", "unknown"),
        command_center_ui_ready=_get_bool(ui_shell_result, "command_center_ui_shell_ready", True),
        voice_summary_ready=_get_bool(ui_shell_result, "voice_summary_ready", True),
    )


def run_v13_0_single_command_operator_launcher(
    *,
    write_ui: bool = False,
    voice_command_text: str | None = None,
    runtime_result: Any | None = None,
    ui_shell_result: Any | None = None,
    voice_shell_result: Any | None = None,
) -> SingleCommandOperatorLauncherResult:
    runtime = runtime_result or audit_v10_1_unified_operator_runtime()

    ui_shell = ui_shell_result or audit_v11_0_command_center_ui_shell(
        runtime_result=runtime,
        write_file=write_ui,
    )

    boundary_context = build_v12_boundary_context_from_ui(ui_shell)

    voice_shell = voice_shell_result or audit_v12_1_local_voice_io_shell(
        boundary_result=boundary_context,
    )

    voice_command = None
    if voice_command_text:
        turn = handle_local_voice_io_command(voice_command_text, boundary_result=boundary_context)
        voice_command = OperatorLauncherVoiceCommand(
            input_text=voice_command_text,
            output_text=turn.shell_output,
            blocked=turn.blocked,
            allowed=turn.allowed,
            unknown=turn.unknown,
        )

    blockers: list[str] = []
    warnings: list[str] = [
        "v13.0 is a single command operator launcher over v10.1, v11.0, and v12.1.",
        "It does not rebuild runtime, recommendation, evidence, data refresh, UI, or voice logic.",
        "It does not start a web server or network listener.",
        "It does not implement microphone, speech-to-text, or text-to-speech.",
        "It does not connect to brokers, use credentials, place orders, or execute trades.",
    ]

    runtime_status = _get_text(runtime, "status", "")
    ui_status = _get_text(ui_shell, "status", "")
    voice_status = _get_text(voice_shell, "status", "")

    if runtime_status != V10_1_STATUS_READY:
        blockers.append(f"v10.1 runtime is not ready: {runtime_status}")
    if ui_status != V11_0_STATUS_READY:
        blockers.append(f"v11.0 UI shell is not ready: {ui_status}")
    if voice_status != V12_1_STATUS_READY:
        blockers.append(f"v12.1 local voice shell is not ready: {voice_status}")

    safety_checks = {
        "runtime final buy": _get_bool(runtime, "final_user_buy_action_required", True),
        "ui final buy": _get_bool(ui_shell, "final_user_buy_action_required", True),
        "voice final buy": _get_bool(voice_shell, "final_user_buy_action_required", True),
        "runtime broker forbidden": _get_bool(runtime, "broker_connection_forbidden", True),
        "ui broker forbidden": _get_bool(ui_shell, "broker_connection_forbidden", True),
        "voice broker forbidden": _get_bool(voice_shell, "broker_connection_forbidden", True),
        "runtime no trades": _get_bool(runtime, "no_trades_executed", True),
        "ui no trades": _get_bool(ui_shell, "no_trades_executed", True),
        "voice no trades": _get_bool(voice_shell, "no_trades_executed", True),
    }

    for label, passed in safety_checks.items():
        if not passed:
            blockers.append(f"Safety check failed: {label}")

    if voice_command and voice_command.blocked and "No execution action was taken" not in voice_command.output_text:
        blockers.append("Blocked launcher voice command must confirm no execution action was taken.")

    unique_blockers = tuple(dict.fromkeys(blockers))
    unique_warnings = tuple(dict.fromkeys(warnings))
    ready = not unique_blockers

    command_count = 3 + (1 if voice_command else 0)

    return SingleCommandOperatorLauncherResult(
        status=STATUS_READY if ready else STATUS_BLOCKED,
        launcher_status=LAUNCHER_READY if ready else LAUNCHER_BLOCKED,
        recommended_next_stage=NEXT_STAGE,
        runtime_status=runtime_status,
        ui_shell_status=ui_status,
        voice_shell_status=voice_status,
        selected_candidate_id=_get_text(runtime, "selected_candidate_id", _get_text(ui_shell, "selected_candidate_id", "unknown")),
        selected_sleeve_id=_get_text(runtime, "selected_sleeve_id", _get_text(ui_shell, "selected_sleeve_id", "unknown")),
        output_path=_get_text(ui_shell, "output_path", DEFAULT_UI_OUTPUT_PATH),
        ui_html_written=_get_bool(ui_shell, "html_written", False),
        voice_demo_available=True,
        voice_command_processed=voice_command is not None,
        voice_command=voice_command,
        command_count=command_count,
        blocker_count=len(unique_blockers),
        warning_count=len(unique_warnings),
        blockers=unique_blockers,
        warnings=unique_warnings,
        single_command_launcher_ready=ready,
        runtime_launched=runtime_status == V10_1_STATUS_READY,
        ui_shell_launched=ui_status == V11_0_STATUS_READY,
        voice_shell_launched=voice_status == V12_1_STATUS_READY,
        static_local_html_only=True,
        typed_voice_shell_only=True,
        no_web_server_started=True,
        no_network_listener_started=True,
        no_external_asset_loading=True,
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


def build_launcher_console_summary(result: SingleCommandOperatorLauncherResult) -> str:
    lines = [
        result.status,
        f"launcher status: {result.launcher_status}",
        f"selected candidate: {result.selected_candidate_id}",
        f"selected sleeve: {result.selected_sleeve_id}",
        f"runtime: {result.runtime_status}",
        f"ui shell: {result.ui_shell_status}",
        f"voice shell: {result.voice_shell_status}",
        f"ui output path: {result.output_path}",
        f"ui html written: {result.ui_html_written}",
        f"voice demo available: {result.voice_demo_available}",
        f"voice command processed: {result.voice_command_processed}",
        f"blockers: {', '.join(result.blockers) if result.blockers else 'none'}",
        "safety: no broker, no credentials, no order, no trade; final buy remains manual.",
    ]

    if result.voice_command:
        lines.extend(
            [
                "",
                f"> {result.voice_command.input_text}",
                result.voice_command.output_text,
            ]
        )

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run J.A.R.V.I.S. v13.0 single command operator launcher.")
    parser.add_argument("--write-ui", action="store_true", help="Generate the static local command-center HTML.")
    parser.add_argument("--voice-command", help="Process one typed Jarvis voice-like command.")
    parser.add_argument("--demo-voice", action="store_true", help="Print local voice demo commands after launch.")
    args = parser.parse_args()

    result = run_v13_0_single_command_operator_launcher(
        write_ui=args.write_ui,
        voice_command_text=args.voice_command,
    )
    print(build_launcher_console_summary(result))

    if args.demo_voice:
        print("")
        print("Voice demo commands:")
        for command in DEFAULT_COMMAND_SAMPLES:
            print(f"- {command}")


if __name__ == "__main__":
    main()
