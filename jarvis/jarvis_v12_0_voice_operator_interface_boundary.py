"""J.A.R.V.I.S. v12.0 voice operator interface boundary.

This stage defines the safe command boundary for a future voice interface.

It does not implement microphone input, wake-word detection, speech-to-text,
text-to-speech, a broker connection, credentials, private account ingestion,
buy requests, order placement, or trade execution.

It routes voice-like text commands into allowed operator intents and blocks
execution intents.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .jarvis_v11_0_command_center_ui_shell import (
    STATUS_READY as V11_0_STATUS_READY,
    audit_v11_0_command_center_ui_shell,
)


STATUS_READY = "JARVIS_V12_0_VOICE_OPERATOR_INTERFACE_BOUNDARY_READY_SAFE"
STATUS_BLOCKED = "JARVIS_V12_0_VOICE_OPERATOR_INTERFACE_BOUNDARY_BLOCKED_SAFE"

BOUNDARY_READY = "VOICE_OPERATOR_INTERFACE_BOUNDARY_READY"
BOUNDARY_BLOCKED = "VOICE_OPERATOR_INTERFACE_BOUNDARY_BLOCKED"

NEXT_STAGE = "v12_1_local_voice_io_shell"

INTENT_ALLOWED = "ALLOWED_OPERATOR_INTENT"
INTENT_BLOCKED = "BLOCKED_EXECUTION_INTENT"
INTENT_UNKNOWN = "UNKNOWN_OPERATOR_INTENT"

ALLOWED_INTENTS = {
    "summarize_operator_status": (
        "operator status",
        "summarize operator",
        "summarize status",
        "portfolio status",
        "status overview",
        "summary status",
        "summarize",
        "overview",
        "what changed",
        "what should i review",
        "review",
    ),
    "explain_recommendation": (
        "explain recommendation",
        "the recommendation",
        "why this recommendation",
        "recommendation",
        "why",
        "candidate",
        "btc",
        "sleeve",
    ),
    "read_action_brief": (
        "action brief",
        "brief",
        "read brief",
        "prepare brief",
    ),
    "explain_missing_data": (
        "explain missing data",
        "missing data",
        "blocked",
        "not confirmed",
        "current data",
        "freshness",
        "source quality",
    ),
    "show_command_center": (
        "command center",
        "dashboard",
        "ui",
        "show dashboard",
        "open dashboard",
    ),
    "refresh_public_data_status": (
        "refresh public data status",
        "public data status",
        "refresh status",
        "public data",
        "data refresh",
        "manifest",
        "source manifest",
    ),
    "read_voice_summary": (
        "read the voice summary",
        "voice summary",
        "read voice summary",
        "jarvis voice summary",
    ),
}

BLOCKED_INTENTS = {
    "buy": ("buy", "purchase", "execute buy", "make the buy"),
    "sell": ("sell", "liquidate", "exit position"),
    "trade": ("trade", "execute trade", "trading"),
    "place_order": ("place order", "submit order", "market order", "limit order"),
    "connect_broker": ("connect broker", "broker", "lightyear", "lhv", "ibkr"),
    "use_credentials": ("credential", "password", "login", "api key", "secret"),
    "ingest_private_account_data": ("private account", "account data", "portfolio login"),
}


@dataclass(frozen=True)
class VoiceOperatorIntent:
    intent_id: str
    status: str
    spoken_text: str
    response_text: str
    matched_terms: tuple[str, ...]
    allowed: bool
    blocked: bool
    requires_manual_final_buy: bool
    creates_buy_request: bool = False
    connects_broker: bool = False
    places_order: bool = False
    executes_trade: bool = False
    uses_credentials: bool = False
    ingests_private_account_data: bool = False

    def safe_intent_only(self) -> bool:
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
            "intent_id": self.intent_id,
            "status": self.status,
            "spoken_text": self.spoken_text,
            "response_text": self.response_text,
            "matched_terms": list(self.matched_terms),
            "allowed": self.allowed,
            "blocked": self.blocked,
            "requires_manual_final_buy": self.requires_manual_final_buy,
            "creates_buy_request": self.creates_buy_request,
            "connects_broker": self.connects_broker,
            "places_order": self.places_order,
            "executes_trade": self.executes_trade,
            "uses_credentials": self.uses_credentials,
            "ingests_private_account_data": self.ingests_private_account_data,
            "safe_intent_only": self.safe_intent_only(),
        }


@dataclass(frozen=True)
class VoiceOperatorBoundaryResult:
    status: str
    boundary_status: str
    recommended_next_stage: str
    ui_shell_status: str
    command_count: int
    allowed_command_count: int
    blocked_command_count: int
    unknown_command_count: int
    voice_summary_ready: bool
    voice_interface_available: bool
    microphone_available: bool
    speech_to_text_available: bool
    text_to_speech_available: bool
    command_center_ui_ready: bool
    selected_candidate_id: str
    selected_sleeve_id: str
    intents: tuple[VoiceOperatorIntent, ...]
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    voice_operator_boundary_ready: bool
    text_command_boundary_only: bool
    microphone_not_implemented: bool
    speech_to_text_not_implemented: bool
    text_to_speech_not_implemented: bool
    execution_intents_blocked: bool
    allowed_operator_intents_available: bool
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
            "boundary_status": self.boundary_status,
            "recommended_next_stage": self.recommended_next_stage,
            "ui_shell_status": self.ui_shell_status,
            "command_count": self.command_count,
            "allowed_command_count": self.allowed_command_count,
            "blocked_command_count": self.blocked_command_count,
            "unknown_command_count": self.unknown_command_count,
            "voice_summary_ready": self.voice_summary_ready,
            "voice_interface_available": self.voice_interface_available,
            "microphone_available": self.microphone_available,
            "speech_to_text_available": self.speech_to_text_available,
            "text_to_speech_available": self.text_to_speech_available,
            "command_center_ui_ready": self.command_center_ui_ready,
            "selected_candidate_id": self.selected_candidate_id,
            "selected_sleeve_id": self.selected_sleeve_id,
            "intents": [intent.to_dict() for intent in self.intents],
            "blockers": list(self.blockers),
            "warnings": list(self.warnings),
            "voice_operator_boundary_ready": self.voice_operator_boundary_ready,
            "text_command_boundary_only": self.text_command_boundary_only,
            "microphone_not_implemented": self.microphone_not_implemented,
            "speech_to_text_not_implemented": self.speech_to_text_not_implemented,
            "text_to_speech_not_implemented": self.text_to_speech_not_implemented,
            "execution_intents_blocked": self.execution_intents_blocked,
            "allowed_operator_intents_available": self.allowed_operator_intents_available,
            "final_user_buy_action_required": self.final_user_buy_action_required,
            "buy_request_deferred": self.buy_request_deferred,
            "broker_connection_forbidden": self.broker_connection_forbidden,
            "order_placement_forbidden": self.order_placement_forbidden,
            "no_trades_executed": self.no_trades_executed,
            "credentials_forbidden": self.credentials_forbidden,
            "private_account_data_ingestion_forbidden": self.private_account_data_ingestion_forbidden,
        }


def _matches(text: str, terms: tuple[str, ...]) -> tuple[str, ...]:
    normalized = text.lower()
    return tuple(term for term in terms if term in normalized)


def evaluate_voice_operator_command(spoken_text: str) -> VoiceOperatorIntent:
    text = (spoken_text or "").strip()

    if not text:
        return VoiceOperatorIntent(
            intent_id="empty",
            status=INTENT_UNKNOWN,
            spoken_text=spoken_text,
            response_text="I did not receive an operator command.",
            matched_terms=(),
            allowed=False,
            blocked=False,
            requires_manual_final_buy=True,
        )

    blocked_matches: list[str] = []
    blocked_intent_id = ""

    for intent_id, terms in BLOCKED_INTENTS.items():
        matches = _matches(text, terms)
        if matches:
            blocked_matches.extend(matches)
            blocked_intent_id = intent_id
            break

    if blocked_matches:
        return VoiceOperatorIntent(
            intent_id=blocked_intent_id,
            status=INTENT_BLOCKED,
            spoken_text=spoken_text,
            response_text=(
                "I cannot execute that command. J.A.R.V.I.S. can prepare data, evidence, "
                "recommendations, dashboards, and summaries, but Diogo must perform the final "
                "real-world buy outside the system."
            ),
            matched_terms=tuple(blocked_matches),
            allowed=False,
            blocked=True,
            requires_manual_final_buy=True,
            creates_buy_request=blocked_intent_id == "buy",
            connects_broker=blocked_intent_id == "connect_broker",
            places_order=blocked_intent_id == "place_order",
            executes_trade=blocked_intent_id in {"sell", "trade", "place_order"},
            uses_credentials=blocked_intent_id == "use_credentials",
            ingests_private_account_data=blocked_intent_id == "ingest_private_account_data",
        )

    for intent_id, terms in ALLOWED_INTENTS.items():
        matches = _matches(text, terms)
        if matches:
            return VoiceOperatorIntent(
                intent_id=intent_id,
                status=INTENT_ALLOWED,
                spoken_text=spoken_text,
                response_text=(
                    "Allowed operator command. I can answer using the J.A.R.V.I.S. runtime, "
                    "command center, evidence, recommendation, action brief, and voice-ready summary."
                ),
                matched_terms=matches,
                allowed=True,
                blocked=False,
                requires_manual_final_buy=True,
            )

    return VoiceOperatorIntent(
        intent_id="unknown",
        status=INTENT_UNKNOWN,
        spoken_text=spoken_text,
        response_text=(
            "I can help with operator status, recommendations, action briefs, data freshness, "
            "missing data, command center status, and voice summaries. I cannot buy, sell, trade, "
            "place orders, connect brokers, or use credentials."
        ),
        matched_terms=(),
        allowed=False,
        blocked=False,
        requires_manual_final_buy=True,
    )


def build_default_voice_operator_command_samples() -> tuple[str, ...]:
    return (
        "Jarvis, summarize operator status.",
        "Jarvis, explain the recommendation.",
        "Jarvis, read the action brief.",
        "Jarvis, explain missing data.",
        "Jarvis, show the command center.",
        "Jarvis, refresh public data status.",
        "Jarvis, read the voice summary.",
        "Jarvis, buy BTC now.",
        "Jarvis, sell the position.",
        "Jarvis, place a market order.",
        "Jarvis, connect my broker.",
        "Jarvis, use my credentials.",
    )


def audit_v12_0_voice_operator_interface_boundary(
    *,
    command_samples: tuple[str, ...] | None = None,
    ui_shell_result: Any | None = None,
) -> VoiceOperatorBoundaryResult:
    effective_ui = ui_shell_result or audit_v11_0_command_center_ui_shell()
    samples = command_samples or build_default_voice_operator_command_samples()
    intents = tuple(evaluate_voice_operator_command(sample) for sample in samples)

    blockers: list[str] = []
    warnings: list[str] = [
        "v12.0 is a voice operator interface boundary only.",
        "It accepts voice-like text commands, not microphone audio.",
        "Speech-to-text and text-to-speech are not implemented in v12.0.",
        "Execution commands are blocked.",
        "The final real-world buy remains manual and outside J.A.R.V.I.S.",
    ]

    ui_status = str(getattr(effective_ui, "status", ""))
    if ui_status != V11_0_STATUS_READY:
        blockers.append(f"v11.0 command center UI shell is not ready: {ui_status}")

    allowed_count = sum(1 for intent in intents if intent.allowed)
    blocked_count = sum(1 for intent in intents if intent.blocked)
    unknown_count = sum(1 for intent in intents if intent.status == INTENT_UNKNOWN)

    if allowed_count == 0:
        blockers.append("At least one allowed operator voice intent must be available.")
    if blocked_count == 0:
        blockers.append("At least one blocked execution voice intent must be validated.")

    for intent in intents:
        if not intent.safe_intent_only() and intent.status != INTENT_BLOCKED:
            blockers.append(f"Unsafe non-blocked voice intent detected: {intent.intent_id}.")
        if intent.status == INTENT_BLOCKED and intent.allowed:
            blockers.append(f"Blocked voice intent must not be allowed: {intent.intent_id}.")

    execution_blocked = all(
        intent.status == INTENT_BLOCKED
        for intent in intents
        if any(term in intent.spoken_text.lower() for terms in BLOCKED_INTENTS.values() for term in terms)
    )

    if not execution_blocked:
        blockers.append("All execution-related voice commands must be blocked.")

    unique_blockers = tuple(dict.fromkeys(blockers))
    unique_warnings = tuple(dict.fromkeys(warnings))
    ready = not unique_blockers

    return VoiceOperatorBoundaryResult(
        status=STATUS_READY if ready else STATUS_BLOCKED,
        boundary_status=BOUNDARY_READY if ready else BOUNDARY_BLOCKED,
        recommended_next_stage=NEXT_STAGE,
        ui_shell_status=ui_status,
        command_count=len(intents),
        allowed_command_count=allowed_count,
        blocked_command_count=blocked_count,
        unknown_command_count=unknown_count,
        voice_summary_ready=bool(getattr(effective_ui, "voice_summary_ready", False)),
        voice_interface_available=False,
        microphone_available=False,
        speech_to_text_available=False,
        text_to_speech_available=False,
        command_center_ui_ready=ui_status == V11_0_STATUS_READY,
        selected_candidate_id=str(getattr(effective_ui, "selected_candidate_id", "unknown")),
        selected_sleeve_id=str(getattr(effective_ui, "selected_sleeve_id", "unknown")),
        intents=intents,
        blockers=unique_blockers,
        warnings=unique_warnings,
        voice_operator_boundary_ready=ready,
        text_command_boundary_only=True,
        microphone_not_implemented=True,
        speech_to_text_not_implemented=True,
        text_to_speech_not_implemented=True,
        execution_intents_blocked=execution_blocked,
        allowed_operator_intents_available=allowed_count > 0,
        final_user_buy_action_required=True,
        buy_request_deferred=True,
        broker_connection_forbidden=True,
        order_placement_forbidden=True,
        no_trades_executed=True,
        credentials_forbidden=True,
        private_account_data_ingestion_forbidden=True,
    )

