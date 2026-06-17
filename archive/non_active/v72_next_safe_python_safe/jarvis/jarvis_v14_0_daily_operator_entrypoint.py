"""J.A.R.V.I.S. v14.0 daily operator entrypoint.

This stage adds a daily-use entrypoint over the released v13.1 product-mode stack.

It does not add strategy, recommendation, evidence, data refresh, UI, voice,
broker, credential, order, or trading logic.

It provides a short operator command surface:

- daily launch;
- safety check;
- custom typed voice-like command;
- voice demo command list.

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
from typing import Any, Callable

from .jarvis_v13_0_single_command_operator_launcher import (
    STATUS_READY as V13_0_STATUS_READY,
    SingleCommandOperatorLauncherResult,
    run_v13_0_single_command_operator_launcher,
)
from .jarvis_v12_1_local_voice_io_shell import DEFAULT_COMMAND_SAMPLES


STATUS_READY = "JARVIS_V14_0_DAILY_OPERATOR_ENTRYPOINT_READY_SAFE"
STATUS_BLOCKED = "JARVIS_V14_0_DAILY_OPERATOR_ENTRYPOINT_BLOCKED_SAFE"

ENTRYPOINT_READY = "DAILY_OPERATOR_ENTRYPOINT_READY"
ENTRYPOINT_BLOCKED = "DAILY_OPERATOR_ENTRYPOINT_BLOCKED"

NEXT_STAGE = "v14_1_operator_readme_and_shortcuts_polish"

DAILY_STATUS_COMMAND = "Jarvis, summarize operator status."
SAFETY_CHECK_COMMAND = "Jarvis, buy BTC now."


@dataclass(frozen=True)
class DailyOperatorEntrypointResult:
    status: str
    entrypoint_status: str
    recommended_next_stage: str
    mode: str
    command_text: str
    launcher_status: str
    selected_candidate_id: str
    selected_sleeve_id: str
    output_path: str
    ui_html_written: bool
    voice_command_processed: bool
    voice_command_allowed: bool
    voice_command_blocked: bool
    voice_command_unknown: bool
    voice_command_output: str
    console_summary: str
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    daily_entrypoint_ready: bool
    wraps_released_launcher: bool
    short_root_command_available: bool
    daily_mode_available: bool
    safety_check_mode_available: bool
    custom_voice_command_available: bool
    demo_voice_mode_available: bool
    no_strategy_rebuild: bool
    no_recommendation_rebuild: bool
    no_evidence_rebuild: bool
    no_data_refresh_rebuild: bool
    no_ui_rebuild: bool
    no_voice_rebuild: bool
    static_local_html_only: bool
    typed_voice_shell_only: bool
    no_web_server_started: bool
    no_network_listener_started: bool
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
            "entrypoint_status": self.entrypoint_status,
            "recommended_next_stage": self.recommended_next_stage,
            "mode": self.mode,
            "command_text": self.command_text,
            "launcher_status": self.launcher_status,
            "selected_candidate_id": self.selected_candidate_id,
            "selected_sleeve_id": self.selected_sleeve_id,
            "output_path": self.output_path,
            "ui_html_written": self.ui_html_written,
            "voice_command_processed": self.voice_command_processed,
            "voice_command_allowed": self.voice_command_allowed,
            "voice_command_blocked": self.voice_command_blocked,
            "voice_command_unknown": self.voice_command_unknown,
            "voice_command_output": self.voice_command_output,
            "console_summary": self.console_summary,
            "blockers": list(self.blockers),
            "warnings": list(self.warnings),
            "daily_entrypoint_ready": self.daily_entrypoint_ready,
            "wraps_released_launcher": self.wraps_released_launcher,
            "short_root_command_available": self.short_root_command_available,
            "daily_mode_available": self.daily_mode_available,
            "safety_check_mode_available": self.safety_check_mode_available,
            "custom_voice_command_available": self.custom_voice_command_available,
            "demo_voice_mode_available": self.demo_voice_mode_available,
            "no_strategy_rebuild": self.no_strategy_rebuild,
            "no_recommendation_rebuild": self.no_recommendation_rebuild,
            "no_evidence_rebuild": self.no_evidence_rebuild,
            "no_data_refresh_rebuild": self.no_data_refresh_rebuild,
            "no_ui_rebuild": self.no_ui_rebuild,
            "no_voice_rebuild": self.no_voice_rebuild,
            "static_local_html_only": self.static_local_html_only,
            "typed_voice_shell_only": self.typed_voice_shell_only,
            "no_web_server_started": self.no_web_server_started,
            "no_network_listener_started": self.no_network_listener_started,
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
    value = getattr(obj, name, default)
    return str(value if value is not None else default)


def _get_bool(obj: Any, name: str, default: bool = False) -> bool:
    return bool(getattr(obj, name, default))


def _extract_voice_command_output(launcher: SingleCommandOperatorLauncherResult | Any) -> tuple[bool, bool, bool, bool, str]:
    voice_command = getattr(launcher, "voice_command", None)
    if not voice_command:
        return False, False, False, False, ""

    return (
        True,
        bool(getattr(voice_command, "allowed", False)),
        bool(getattr(voice_command, "blocked", False)),
        bool(getattr(voice_command, "unknown", False)),
        _get_text(voice_command, "output_text"),
    )


def run_v14_0_daily_operator_entrypoint(
    *,
    mode: str = "daily",
    command_text: str | None = None,
    launcher_runner: Callable[..., SingleCommandOperatorLauncherResult] = run_v13_0_single_command_operator_launcher,
) -> DailyOperatorEntrypointResult:
    if mode == "daily":
        effective_command = DAILY_STATUS_COMMAND
        write_ui = True
    elif mode == "safety_check":
        effective_command = SAFETY_CHECK_COMMAND
        write_ui = False
    elif mode == "custom":
        effective_command = command_text or DAILY_STATUS_COMMAND
        write_ui = False
    elif mode == "demo":
        effective_command = DAILY_STATUS_COMMAND
        write_ui = False
    else:
        effective_command = command_text or DAILY_STATUS_COMMAND
        write_ui = False

    launcher = launcher_runner(
        write_ui=write_ui,
        voice_command_text=effective_command,
    )

    voice_processed, voice_allowed, voice_blocked, voice_unknown, voice_output = _extract_voice_command_output(launcher)
    console_summary = "\n".join(
        [
            _get_text(launcher, "status"),
            f"selected candidate: {_get_text(launcher, 'selected_candidate_id', 'unknown')}",
            f"selected sleeve: {_get_text(launcher, 'selected_sleeve_id', 'unknown')}",
            f"ui output path: {_get_text(launcher, 'output_path', 'jarvis/local/ui/jarvis_command_center.html')}",
            f"ui html written: {_get_bool(launcher, 'ui_html_written')}",
            "safety: no broker, no credentials, no order, no trade; final buy remains manual.",
        ]
    )

    blockers: list[str] = []
    warnings: list[str] = [
        "v14.0 is a daily operator entrypoint over the released v13.1 product-mode stack.",
        "It adds no strategy, recommendation, evidence, data, UI, voice, broker, order, or trade logic.",
        "It is a convenience wrapper for daily local use.",
    ]

    launcher_status = _get_text(launcher, "status")
    if launcher_status != V13_0_STATUS_READY:
        blockers.append(f"v13.0 launcher is not ready: {launcher_status}")

    if not voice_processed:
        blockers.append("Daily operator entrypoint must process a typed voice-like command.")

    if mode == "daily" and not voice_allowed:
        blockers.append("Daily mode must allow the operator status command.")

    if mode == "safety_check" and not voice_blocked:
        blockers.append("Safety-check mode must block the buy command.")

    if mode == "safety_check" and "No execution action was taken" not in voice_output:
        blockers.append("Safety-check mode must confirm no execution action was taken.")

    safety_checks = {
        "static local HTML only": _get_bool(launcher, "static_local_html_only"),
        "typed voice shell only": _get_bool(launcher, "typed_voice_shell_only"),
        "no web server started": _get_bool(launcher, "no_web_server_started"),
        "no network listener started": _get_bool(launcher, "no_network_listener_started"),
        "no microphone": _get_bool(launcher, "no_microphone"),
        "no speech to text": _get_bool(launcher, "no_speech_to_text"),
        "no text to speech": _get_bool(launcher, "no_text_to_speech"),
        "final user buy action required": _get_bool(launcher, "final_user_buy_action_required"),
        "buy request deferred": _get_bool(launcher, "buy_request_deferred"),
        "broker connection forbidden": _get_bool(launcher, "broker_connection_forbidden"),
        "order placement forbidden": _get_bool(launcher, "order_placement_forbidden"),
        "no trades executed": _get_bool(launcher, "no_trades_executed"),
        "credentials forbidden": _get_bool(launcher, "credentials_forbidden"),
        "private account data ingestion forbidden": _get_bool(launcher, "private_account_data_ingestion_forbidden"),
    }

    for label, passed in safety_checks.items():
        if not passed:
            blockers.append(f"Safety check failed: {label}")

    unique_blockers = tuple(dict.fromkeys(blockers))
    unique_warnings = tuple(dict.fromkeys(warnings))
    ready = not unique_blockers

    return DailyOperatorEntrypointResult(
        status=STATUS_READY if ready else STATUS_BLOCKED,
        entrypoint_status=ENTRYPOINT_READY if ready else ENTRYPOINT_BLOCKED,
        recommended_next_stage=NEXT_STAGE,
        mode=mode,
        command_text=effective_command,
        launcher_status=launcher_status,
        selected_candidate_id=_get_text(launcher, "selected_candidate_id", "unknown"),
        selected_sleeve_id=_get_text(launcher, "selected_sleeve_id", "unknown"),
        output_path=_get_text(launcher, "output_path", "jarvis/local/ui/jarvis_command_center.html"),
        ui_html_written=_get_bool(launcher, "ui_html_written"),
        voice_command_processed=voice_processed,
        voice_command_allowed=voice_allowed,
        voice_command_blocked=voice_blocked,
        voice_command_unknown=voice_unknown,
        voice_command_output=voice_output,
        console_summary=console_summary,
        blockers=unique_blockers,
        warnings=unique_warnings,
        daily_entrypoint_ready=ready,
        wraps_released_launcher=True,
        short_root_command_available=True,
        daily_mode_available=True,
        safety_check_mode_available=True,
        custom_voice_command_available=True,
        demo_voice_mode_available=True,
        no_strategy_rebuild=True,
        no_recommendation_rebuild=True,
        no_evidence_rebuild=True,
        no_data_refresh_rebuild=True,
        no_ui_rebuild=True,
        no_voice_rebuild=True,
        static_local_html_only=_get_bool(launcher, "static_local_html_only"),
        typed_voice_shell_only=_get_bool(launcher, "typed_voice_shell_only"),
        no_web_server_started=_get_bool(launcher, "no_web_server_started"),
        no_network_listener_started=_get_bool(launcher, "no_network_listener_started"),
        no_microphone=_get_bool(launcher, "no_microphone"),
        no_speech_to_text=_get_bool(launcher, "no_speech_to_text"),
        no_text_to_speech=_get_bool(launcher, "no_text_to_speech"),
        final_user_buy_action_required=_get_bool(launcher, "final_user_buy_action_required"),
        buy_request_deferred=_get_bool(launcher, "buy_request_deferred"),
        broker_connection_forbidden=_get_bool(launcher, "broker_connection_forbidden"),
        order_placement_forbidden=_get_bool(launcher, "order_placement_forbidden"),
        no_trades_executed=_get_bool(launcher, "no_trades_executed"),
        credentials_forbidden=_get_bool(launcher, "credentials_forbidden"),
        private_account_data_ingestion_forbidden=_get_bool(launcher, "private_account_data_ingestion_forbidden"),
    )


def build_daily_operator_console_output(result: DailyOperatorEntrypointResult, *, include_demo: bool = False) -> str:
    lines = [
        result.status,
        f"entrypoint status: {result.entrypoint_status}",
        f"mode: {result.mode}",
        f"selected candidate: {result.selected_candidate_id}",
        f"selected sleeve: {result.selected_sleeve_id}",
        f"ui output path: {result.output_path}",
        f"ui html written: {result.ui_html_written}",
        f"voice command processed: {result.voice_command_processed}",
        f"blockers: {', '.join(result.blockers) if result.blockers else 'none'}",
        "safety: no broker, no credentials, no order, no trade; final buy remains manual.",
        "",
        f"> {result.command_text}",
        result.voice_command_output,
    ]

    if include_demo:
        lines.extend(["", "Available typed Jarvis commands:"])
        lines.extend(f"- {command}" for command in DEFAULT_COMMAND_SAMPLES)

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the J.A.R.V.I.S. daily operator entrypoint.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--daily", action="store_true", help="Run daily operator status with UI generation.")
    mode.add_argument("--safety-check", action="store_true", help="Verify that a buy command is blocked.")
    mode.add_argument("--voice-command", help="Run one custom typed Jarvis command.")
    mode.add_argument("--demo", action="store_true", help="Show demo typed Jarvis commands.")
    args = parser.parse_args()

    if args.safety_check:
        result = run_v14_0_daily_operator_entrypoint(mode="safety_check")
        print(build_daily_operator_console_output(result))
        return

    if args.voice_command:
        result = run_v14_0_daily_operator_entrypoint(mode="custom", command_text=args.voice_command)
        print(build_daily_operator_console_output(result))
        return

    if args.demo:
        result = run_v14_0_daily_operator_entrypoint(mode="demo")
        print(build_daily_operator_console_output(result, include_demo=True))
        return

    result = run_v14_0_daily_operator_entrypoint(mode="daily")
    print(build_daily_operator_console_output(result))


if __name__ == "__main__":
    main()

