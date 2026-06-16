"""J.A.R.V.I.S. v12.1 local voice I/O shell.

This stage adds a local typed command shell around the v12.0 voice operator
interface boundary.

It does not implement microphone input, speech-to-text, text-to-speech, wake
word detection, broker access, credentials, private account ingestion, buy
requests, order placement, or trade execution.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import Any

from .jarvis_v12_0_voice_operator_interface_boundary import (
    INTENT_ALLOWED,
    INTENT_BLOCKED,
    INTENT_UNKNOWN,
    STATUS_READY as V12_0_STATUS_READY,
    VoiceOperatorBoundaryResult,
    VoiceOperatorIntent,
    audit_v12_0_voice_operator_interface_boundary,
    evaluate_voice_operator_command,
)


STATUS_READY = "JARVIS_V12_1_LOCAL_VOICE_IO_SHELL_READY_SAFE"
STATUS_BLOCKED = "JARVIS_V12_1_LOCAL_VOICE_IO_SHELL_BLOCKED_SAFE"

SHELL_READY = "LOCAL_VOICE_IO_SHELL_READY"
SHELL_BLOCKED = "LOCAL_VOICE_IO_SHELL_BLOCKED"

NEXT_STAGE = "v13_0_single_command_operator_launcher"

DEFAULT_COMMAND_SAMPLES = (
    "Jarvis, summarize operator status.",
    "Jarvis, explain the recommendation.",
    "Jarvis, explain missing data.",
    "Jarvis, show the command center.",
    "Jarvis, read the voice summary.",
    "Jarvis, buy BTC now.",
    "Jarvis, place a market order.",
    "Jarvis, connect my broker.",
    "Jarvis, tell me a joke.",
)


@dataclass(frozen=True)
class LocalVoiceIoTurn:
    input_text: str
    intent_id: str
    intent_status: str
    shell_output: str
    allowed: bool
    blocked: bool
    unknown: bool
    creates_buy_request: bool
    connects_broker: bool
    places_order: bool
    executes_trade: bool
    uses_credentials: bool
    ingests_private_account_data: bool

    def safe_turn_only(self) -> bool:
        return (
            not self.creates_buy_request
            and not self.connects_broker
            and not self.places_order
            and not self.executes_trade
            and not self.uses_credentials
            and not self.ingests_private_account_data
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "input_text": self.input_text,
            "intent_id": self.intent_id,
            "intent_status": self.intent_status,
            "shell_output": self.shell_output,
            "allowed": self.allowed,
            "blocked": self.blocked,
            "unknown": self.unknown,
            "creates_buy_request": self.creates_buy_request,
            "connects_broker": self.connects_broker,
            "places_order": self.places_order,
            "executes_trade": self.executes_trade,
            "uses_credentials": self.uses_credentials,
            "ingests_private_account_data": self.ingests_private_account_data,
            "safe_turn_only": self.safe_turn_only(),
        }


@dataclass(frozen=True)
class LocalVoiceIoShellResult:
    status: str
    shell_status: str
    recommended_next_stage: str
    boundary_status: str
    command_count: int
    allowed_turn_count: int
    blocked_turn_count: int
    unknown_turn_count: int
    selected_candidate_id: str
    selected_sleeve_id: str
    command_center_ui_ready: bool
    voice_summary_ready: bool
    turns: tuple[LocalVoiceIoTurn, ...]
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    local_voice_io_shell_ready: bool
    typed_terminal_shell_only: bool
    interactive_loop_available: bool
    single_command_mode_available: bool
    microphone_available: bool
    speech_to_text_available: bool
    text_to_speech_available: bool
    wake_word_detection_available: bool
    execution_intents_blocked: bool
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
            "shell_status": self.shell_status,
            "recommended_next_stage": self.recommended_next_stage,
            "boundary_status": self.boundary_status,
            "command_count": self.command_count,
            "allowed_turn_count": self.allowed_turn_count,
            "blocked_turn_count": self.blocked_turn_count,
            "unknown_turn_count": self.unknown_turn_count,
            "selected_candidate_id": self.selected_candidate_id,
            "selected_sleeve_id": self.selected_sleeve_id,
            "command_center_ui_ready": self.command_center_ui_ready,
            "voice_summary_ready": self.voice_summary_ready,
            "turns": [turn.to_dict() for turn in self.turns],
            "blockers": list(self.blockers),
            "warnings": list(self.warnings),
            "local_voice_io_shell_ready": self.local_voice_io_shell_ready,
            "typed_terminal_shell_only": self.typed_terminal_shell_only,
            "interactive_loop_available": self.interactive_loop_available,
            "single_command_mode_available": self.single_command_mode_available,
            "microphone_available": self.microphone_available,
            "speech_to_text_available": self.speech_to_text_available,
            "text_to_speech_available": self.text_to_speech_available,
            "wake_word_detection_available": self.wake_word_detection_available,
            "execution_intents_blocked": self.execution_intents_blocked,
            "final_user_buy_action_required": self.final_user_buy_action_required,
            "buy_request_deferred": self.buy_request_deferred,
            "broker_connection_forbidden": self.broker_connection_forbidden,
            "order_placement_forbidden": self.order_placement_forbidden,
            "no_trades_executed": self.no_trades_executed,
            "credentials_forbidden": self.credentials_forbidden,
            "private_account_data_ingestion_forbidden": self.private_account_data_ingestion_forbidden,
        }


def build_local_voice_shell_response(
    intent: VoiceOperatorIntent,
    *,
    boundary_result: VoiceOperatorBoundaryResult | None = None,
) -> str:
    candidate = getattr(boundary_result, "selected_candidate_id", "unknown")
    sleeve = getattr(boundary_result, "selected_sleeve_id", "unknown")
    ui_ready = bool(getattr(boundary_result, "command_center_ui_ready", False))
    voice_ready = bool(getattr(boundary_result, "voice_summary_ready", False))

    if intent.status == INTENT_BLOCKED:
        return (
            "BLOCKED: "
            + intent.response_text
            + " No execution action was taken."
        )

    if intent.status == INTENT_UNKNOWN:
        return (
            "UNKNOWN: I can summarize status, explain recommendations, read action briefs, "
            "explain missing data, show command center status, refresh public data status, "
            "or read the voice summary. I cannot buy, sell, trade, place orders, connect "
            "brokers, or use credentials."
        )

    if intent.intent_id == "summarize_operator_status":
        return (
            f"ALLOWED: J.A.R.V.I.S. operator status is available. Candidate: {candidate}. "
            f"Sleeve: {sleeve}. Command center UI ready: {ui_ready}. "
            f"Voice summary ready: {voice_ready}. No execution action was taken."
        )

    if intent.intent_id == "explain_recommendation":
        return (
            f"ALLOWED: The active recommendation context is candidate {candidate} in sleeve {sleeve}. "
            "Use the evidence pack and action brief before making any final manual buy outside J.A.R.V.I.S."
        )

    if intent.intent_id == "read_action_brief":
        return (
            f"ALLOWED: The action brief is available for {candidate} in {sleeve}. "
            "J.A.R.V.I.S. prepares the brief only; it does not buy or place orders."
        )

    if intent.intent_id == "explain_missing_data":
        return (
            "ALLOWED: Missing-data review is available. Current recommendation-quality data may still "
            "need confirmation if public data has not been refreshed in the latest run."
        )

    if intent.intent_id == "show_command_center":
        return (
            "ALLOWED: Command center status is available. Local UI output path is "
            "jarvis/local/ui/jarvis_command_center.html when generated by v11.0."
        )

    if intent.intent_id == "refresh_public_data_status":
        return (
            "ALLOWED: Public data refresh status can be reviewed through the v10.0/v10.1 runtime. "
            "This shell reports status only; it does not fetch private data or execute trades."
        )

    if intent.intent_id == "read_voice_summary":
        return (
            f"ALLOWED: Voice summary readiness is {voice_ready}. "
            "This is typed shell output only; microphone, STT, and TTS are not implemented."
        )

    return intent.response_text


def handle_local_voice_io_command(
    command_text: str,
    *,
    boundary_result: VoiceOperatorBoundaryResult | None = None,
) -> LocalVoiceIoTurn:
    intent = evaluate_voice_operator_command(command_text)
    shell_output = build_local_voice_shell_response(intent, boundary_result=boundary_result)

    return LocalVoiceIoTurn(
        input_text=command_text,
        intent_id=intent.intent_id,
        intent_status=intent.status,
        shell_output=shell_output,
        allowed=intent.allowed,
        blocked=intent.blocked,
        unknown=intent.status == INTENT_UNKNOWN,
        creates_buy_request=False,
        connects_broker=False,
        places_order=False,
        executes_trade=False,
        uses_credentials=False,
        ingests_private_account_data=False,
    )


def audit_v12_1_local_voice_io_shell(
    *,
    command_samples: tuple[str, ...] | None = None,
    boundary_result: VoiceOperatorBoundaryResult | None = None,
) -> LocalVoiceIoShellResult:
    effective_boundary = boundary_result or audit_v12_0_voice_operator_interface_boundary()
    samples = command_samples or DEFAULT_COMMAND_SAMPLES
    turns = tuple(
        handle_local_voice_io_command(command, boundary_result=effective_boundary)
        for command in samples
    )

    blockers: list[str] = []
    warnings: list[str] = [
        "v12.1 is a typed local voice I/O shell only.",
        "Microphone input is not implemented.",
        "Speech-to-text is not implemented.",
        "Text-to-speech is not implemented.",
        "Execution intents remain blocked by v12.0 and produce safe shell output only.",
    ]

    boundary_status = str(getattr(effective_boundary, "status", ""))
    if boundary_status != V12_0_STATUS_READY:
        blockers.append(f"v12.0 voice operator boundary is not ready: {boundary_status}")

    allowed_count = sum(1 for turn in turns if turn.allowed)
    blocked_count = sum(1 for turn in turns if turn.blocked)
    unknown_count = sum(1 for turn in turns if turn.unknown)

    if allowed_count == 0:
        blockers.append("At least one allowed local voice shell command must be available.")
    if blocked_count == 0:
        blockers.append("At least one blocked execution command must be demonstrated.")

    for turn in turns:
        if not turn.safe_turn_only():
            blockers.append(f"Unsafe shell turn detected: {turn.intent_id}.")
        if turn.blocked and "BLOCKED:" not in turn.shell_output:
            blockers.append(f"Blocked command must produce explicit blocked shell output: {turn.input_text}")
        if turn.allowed and "ALLOWED:" not in turn.shell_output:
            blockers.append(f"Allowed command must produce explicit allowed shell output: {turn.input_text}")

    execution_blocked = all(
        turn.blocked
        for turn in turns
        if any(word in turn.input_text.lower() for word in ("buy", "sell", "trade", "order", "broker", "credential"))
    )

    if not execution_blocked:
        blockers.append("Execution-like local voice commands must remain blocked.")

    unique_blockers = tuple(dict.fromkeys(blockers))
    unique_warnings = tuple(dict.fromkeys(warnings))
    ready = not unique_blockers

    return LocalVoiceIoShellResult(
        status=STATUS_READY if ready else STATUS_BLOCKED,
        shell_status=SHELL_READY if ready else SHELL_BLOCKED,
        recommended_next_stage=NEXT_STAGE,
        boundary_status=boundary_status,
        command_count=len(turns),
        allowed_turn_count=allowed_count,
        blocked_turn_count=blocked_count,
        unknown_turn_count=unknown_count,
        selected_candidate_id=str(getattr(effective_boundary, "selected_candidate_id", "unknown")),
        selected_sleeve_id=str(getattr(effective_boundary, "selected_sleeve_id", "unknown")),
        command_center_ui_ready=bool(getattr(effective_boundary, "command_center_ui_ready", False)),
        voice_summary_ready=bool(getattr(effective_boundary, "voice_summary_ready", False)),
        turns=turns,
        blockers=unique_blockers,
        warnings=unique_warnings,
        local_voice_io_shell_ready=ready,
        typed_terminal_shell_only=True,
        interactive_loop_available=True,
        single_command_mode_available=True,
        microphone_available=False,
        speech_to_text_available=False,
        text_to_speech_available=False,
        wake_word_detection_available=False,
        execution_intents_blocked=execution_blocked,
        final_user_buy_action_required=True,
        buy_request_deferred=True,
        broker_connection_forbidden=True,
        order_placement_forbidden=True,
        no_trades_executed=True,
        credentials_forbidden=True,
        private_account_data_ingestion_forbidden=True,
    )


def run_single_local_voice_command(command_text: str) -> str:
    boundary = audit_v12_0_voice_operator_interface_boundary()
    return handle_local_voice_io_command(command_text, boundary_result=boundary).shell_output


def run_interactive_local_voice_shell() -> None:
    boundary = audit_v12_0_voice_operator_interface_boundary()
    print("J.A.R.V.I.S. local voice shell. Type 'exit' to quit.")
    print("Typed shell only. No microphone, no STT, no TTS, no broker, no order, no trade.")

    while True:
        command = input("Jarvis> ").strip()
        if command.lower() in {"exit", "quit", "q"}:
            print("J.A.R.V.I.S. local voice shell closed.")
            return
        print(handle_local_voice_io_command(command, boundary_result=boundary).shell_output)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run J.A.R.V.I.S. v12.1 local typed voice I/O shell.")
    parser.add_argument("--command", help="Run one typed voice-like command and exit.")
    parser.add_argument("--demo", action="store_true", help="Run demo commands and exit.")
    parser.add_argument("--interactive", action="store_true", help="Start the typed local shell loop.")
    args = parser.parse_args()

    if args.command:
        print(run_single_local_voice_command(args.command))
        return

    if args.demo:
        boundary = audit_v12_0_voice_operator_interface_boundary()
        for command in DEFAULT_COMMAND_SAMPLES:
            turn = handle_local_voice_io_command(command, boundary_result=boundary)
            print(f"> {turn.input_text}")
            print(turn.shell_output)
        return

    if args.interactive:
        run_interactive_local_voice_shell()
        return

    result = audit_v12_1_local_voice_io_shell()
    print(result.status)
    print(f"shell status: {result.shell_status}")
    print(f"commands: {result.command_count}")
    print(f"allowed: {result.allowed_turn_count}")
    print(f"blocked: {result.blocked_turn_count}")
    print(f"unknown: {result.unknown_turn_count}")


if __name__ == "__main__":
    main()
