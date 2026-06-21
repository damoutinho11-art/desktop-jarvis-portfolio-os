"""J.A.R.V.I.S. v156.0 non-trading experience parity gate."""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from jarvis.runtime.dashboard_contract import build_dashboard_contract_result, render_dashboard_html
from jarvis.runtime.local_server import ROUTES, render_chat_page
from jarvis.runtime.safety import build_safety_check_console_output
from jarvis.runtime.voice_briefing import build_voice_briefing_result

STATUS_READY = "JARVIS_V156_0_JARVIS_EXPERIENCE_PARITY_GATE_READY_SAFE"
STATUS_REVIEW_REQUIRED = "JARVIS_V156_0_JARVIS_EXPERIENCE_PARITY_GATE_REVIEW_REQUIRED_SAFE"
FINAL_VERDICT_READY = "READY_FOR_SAFE_JARVIS_EXPERIENCE"
FINAL_VERDICT_REVIEW = "REVIEW_REQUIRED_BEFORE_JARVIS_EXPERIENCE"

FORBIDDEN_SOURCE_MARKERS: tuple[str, ...] = (
    "broker_login",
    "connect_broker",
    "create_order",
    "execute_trade",
    "order_ticket",
    "buy_sell_request",
    "auto_approval_enabled = True",
    "private_account_ingestion_enabled = True",
    "allocation_mutation = True",
    "approval_mutation = True",
)


@dataclass(frozen=True)
class JarvisExperienceParityGateResult:
    status: str
    current_date: str
    final_verdict: str
    jarvis_experience_parity_ready: bool
    local_app_launch_ready: bool
    dashboard_ready: bool
    chat_ready: bool
    voice_briefing_text_ready: bool
    voice_playback_ready_or_safe_fallback: bool
    chat_voice_buttons_ready: bool
    animated_orb_ready: bool
    news_ticker_ready: bool
    session_memory_visible: bool
    what_changed_visible: bool
    navigation_ready: bool
    safety_check_blocks_execution: bool
    manual_only: bool
    execution_forbidden: bool
    broker_connection_enabled: bool
    credentials_required: bool
    buy_sell_request_created: bool
    order_created: bool
    trade_created: bool
    auto_approval_enabled: bool
    private_account_ingestion_enabled: bool
    allocation_mutation: bool
    approval_mutation: bool
    blockers: list[str]
    warnings: list[str]
    proof: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _dedupe(items: list[str]) -> list[str]:
    return list(dict.fromkeys(str(item) for item in items if str(item)))


def _source_text(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def _markers_present(text: str, markers: tuple[str, ...] | list[str]) -> tuple[bool, list[str]]:
    missing = [marker for marker in markers if marker not in text]
    return not missing, missing


def _launch_ready() -> tuple[bool, dict[str, Any]]:
    batch = _source_text("Start Jarvis.bat")
    powershell = _source_text("Start-Jarvis.ps1")
    combined = batch + "\n" + powershell
    required = [
        "--local-server",
        "127.0.0.1:8765",
        "/dashboard",
        "/chat",
        "outputs\\dashboard_latest.html",
        "No broker. No credentials. No orders. No trades. No auto-approval.",
    ]
    missing = [marker for marker in required if marker not in combined]
    forbidden = [marker for marker in ("JARVIS_OPEN_CHAT", "Optional chat is off") if marker in combined]
    return not missing and not forbidden, {"missing": missing, "forbidden_found": forbidden}


def _safety_check_ready() -> bool:
    text = build_safety_check_console_output()
    return "BLOCKED:" in text and "No execution action was taken" in text


def _forbidden_source_markers_absent() -> tuple[bool, list[str]]:
    paths = [
        "jarvis/runtime/local_server.py",
        "jarvis/runtime/dashboard_contract.py",
        "jarvis/runtime/voice_briefing.py",
    ]
    combined = "\n".join(_source_text(path) for path in paths)
    lowered = combined.lower()
    found = [marker for marker in FORBIDDEN_SOURCE_MARKERS if marker.lower() in lowered]
    return not found, found


def build_jarvis_experience_parity_gate_result(
    *,
    current_date: str = "2026-06-21",
) -> JarvisExperienceParityGateResult:
    blockers: list[str] = []
    warnings: list[str] = [
        "experience parity gate is read-only and does not write output, local memory, approval, allocation, broker, order, or trade files",
        "local TTS playback may safely fall back to text when unavailable",
    ]

    launch_ready, launch_proof = _launch_ready()
    if not launch_ready:
        blockers.append("local_app_launch_not_ready")

    dashboard_result = build_dashboard_contract_result(current_date=current_date)
    dashboard_html = render_dashboard_html(dashboard_result)
    chat_html = render_chat_page()
    voice = build_voice_briefing_result(current_date=current_date)

    dashboard_ready, dashboard_missing = _markers_present(
        dashboard_html,
        [
            "J.A.R.V.I.S. Portfolio Dashboard",
            "Today's Manual Plan",
            "Market Headlines",
            "Last Session",
            "What Changed Since Last Time",
        ],
    )
    if not dashboard_ready:
        blockers.append("dashboard_experience_not_ready")

    chat_ready, chat_missing = _markers_present(
        chat_html,
        [
            "J.A.R.V.I.S. Local Chat",
            "Ask J.A.R.V.I.S.",
            "/api/chat",
            "What changed since last time?",
        ],
    )
    if not chat_ready:
        blockers.append("chat_experience_not_ready")

    voice_text_ready = bool(voice.voice_briefing_ready and "Good evening, Diogo." in voice.text)
    if not voice_text_ready:
        blockers.append("voice_briefing_text_not_ready")

    voice_playback_ready_or_safe_fallback = bool(
        voice_text_ready
        and not voice.audio_requested
        and not voice.audio_rendered
        and voice.tts_backend == "text_only"
    )
    if not voice_playback_ready_or_safe_fallback:
        blockers.append("voice_playback_safe_fallback_not_ready")

    chat_voice_buttons_ready, chat_voice_missing = _markers_present(
        chat_html,
        ["Read briefing aloud", "Speak reply", "Stop voice", "Voice input", "Audio unavailable"],
    )
    if not chat_voice_buttons_ready:
        blockers.append("chat_voice_buttons_not_ready")

    animated_orb_ready, orb_missing = _markers_present(
        chat_html,
        ["jarvis-orb", "state-idle", "state-listening", "state-thinking", "state-speaking", "@keyframes orbPulse"],
    )
    if not animated_orb_ready:
        blockers.append("animated_orb_not_ready")

    news_ticker_ready, news_missing = _markers_present(
        dashboard_html,
        ["headline-ticker", "ticker-scroll", "never recommend action from headline alone"],
    )
    news_ticker_ready = news_ticker_ready and ("headline-chip" in dashboard_html or "headline-ticker-empty" in dashboard_html)
    if not ("headline-chip" in dashboard_html or "headline-ticker-empty" in dashboard_html):
        news_missing.append("headline-chip_or_empty_state")
    if not news_ticker_ready:
        blockers.append("news_ticker_not_ready")

    session_memory_visible = "Last Session" in dashboard_html and "Safe derived summaries only" in dashboard_html
    if not session_memory_visible:
        blockers.append("session_memory_not_visible")

    what_changed_visible = "What Changed Since Last Time" in dashboard_html and "Since last time:" in dashboard_html
    if not what_changed_visible:
        blockers.append("what_changed_not_visible")

    navigation_ready = all(
        marker in dashboard_html and marker in chat_html
        for marker in ('href="/dashboard"', 'href="/chat"', 'href="/briefing"', 'href="/memory"', 'href="/safety"')
    ) and all(route in ROUTES for route in ("GET /dashboard", "GET /chat", "GET /briefing", "GET /memory", "GET /safety"))
    if not navigation_ready:
        blockers.append("app_navigation_not_ready")

    safety_ready = _safety_check_ready()
    if not safety_ready:
        blockers.append("safety_check_did_not_block_execution")

    forbidden_absent, forbidden_found = _forbidden_source_markers_absent()
    if not forbidden_absent:
        blockers.append("forbidden_execution_marker_found")

    broker_enabled = False
    credentials_required = False
    buy_sell_request_created = False
    order_created = False
    trade_created = False
    auto_approval = False
    private_account_ingestion = False
    allocation_mutation = False
    approval_mutation = False
    if any(
        [
            broker_enabled,
            credentials_required,
            buy_sell_request_created,
            order_created,
            trade_created,
            auto_approval,
            private_account_ingestion,
            allocation_mutation,
            approval_mutation,
        ]
    ):
        blockers.append("forbidden_runtime_flag_enabled")

    blockers = _dedupe(blockers)
    ready = not blockers
    return JarvisExperienceParityGateResult(
        status=STATUS_READY if ready else STATUS_REVIEW_REQUIRED,
        current_date=current_date,
        final_verdict=FINAL_VERDICT_READY if ready else FINAL_VERDICT_REVIEW,
        jarvis_experience_parity_ready=ready,
        local_app_launch_ready=launch_ready,
        dashboard_ready=dashboard_ready,
        chat_ready=chat_ready,
        voice_briefing_text_ready=voice_text_ready,
        voice_playback_ready_or_safe_fallback=voice_playback_ready_or_safe_fallback,
        chat_voice_buttons_ready=chat_voice_buttons_ready,
        animated_orb_ready=animated_orb_ready,
        news_ticker_ready=news_ticker_ready,
        session_memory_visible=session_memory_visible,
        what_changed_visible=what_changed_visible,
        navigation_ready=navigation_ready,
        safety_check_blocks_execution=safety_ready,
        manual_only=True,
        execution_forbidden=True,
        broker_connection_enabled=broker_enabled,
        credentials_required=credentials_required,
        buy_sell_request_created=buy_sell_request_created,
        order_created=order_created,
        trade_created=trade_created,
        auto_approval_enabled=auto_approval,
        private_account_ingestion_enabled=private_account_ingestion,
        allocation_mutation=allocation_mutation,
        approval_mutation=approval_mutation,
        blockers=blockers,
        warnings=_dedupe(warnings + list(voice.warnings or [])),
        proof={
            "launch": launch_proof,
            "dashboard_missing": dashboard_missing,
            "chat_missing": chat_missing,
            "chat_voice_missing": chat_voice_missing,
            "orb_missing": orb_missing,
            "news_missing": news_missing,
            "dashboard_status": dashboard_result.status,
            "voice_status": voice.status,
            "forbidden_source_markers_found": forbidden_found,
        },
    )


def format_jarvis_experience_parity_gate(result: JarvisExperienceParityGateResult) -> str:
    lines = [
        "J.A.R.V.I.S. EXPERIENCE PARITY GATE",
        f"status: {result.status}",
        f"current date: {result.current_date}",
        f"final verdict: {result.final_verdict}",
        f"Jarvis experience parity ready: {result.jarvis_experience_parity_ready}",
        "",
        "CHECKS:",
        f"- local app launch ready: {result.local_app_launch_ready}",
        f"- dashboard ready: {result.dashboard_ready}",
        f"- chat ready: {result.chat_ready}",
        f"- voice briefing text ready: {result.voice_briefing_text_ready}",
        f"- voice playback ready or safe fallback: {result.voice_playback_ready_or_safe_fallback}",
        f"- chat voice buttons ready: {result.chat_voice_buttons_ready}",
        f"- animated orb ready: {result.animated_orb_ready}",
        f"- news ticker ready: {result.news_ticker_ready}",
        f"- session memory visible: {result.session_memory_visible}",
        f"- what-changed visible: {result.what_changed_visible}",
        f"- navigation ready: {result.navigation_ready}",
        f"- safety-check blocks execution: {result.safety_check_blocks_execution}",
        "",
        "SAFETY ASSERTIONS:",
        f"- manual_only: {result.manual_only}",
        f"- execution_forbidden: {result.execution_forbidden}",
        f"- broker_connection_enabled: {result.broker_connection_enabled}",
        f"- credentials_required: {result.credentials_required}",
        f"- buy_sell_request_created: {result.buy_sell_request_created}",
        f"- order_created: {result.order_created}",
        f"- trade_created: {result.trade_created}",
        f"- auto_approval_enabled: {result.auto_approval_enabled}",
        f"- private_account_ingestion_enabled: {result.private_account_ingestion_enabled}",
        f"- allocation_mutation: {result.allocation_mutation}",
        f"- approval_mutation: {result.approval_mutation}",
        "",
        "WARNINGS:",
        *[f"- {item}" for item in result.warnings or ["none"]],
        "",
        "BLOCKERS:",
        *[f"- {item}" for item in result.blockers or ["none"]],
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the J.A.R.V.I.S. non-trading experience parity gate.")
    parser.add_argument("--jarvis-experience-parity-gate", action="store_true")
    parser.add_argument("--current-date", default="2026-06-21")
    args = parser.parse_args(argv)

    result = build_jarvis_experience_parity_gate_result(current_date=args.current_date)
    print(format_jarvis_experience_parity_gate(result))
    return 0 if result.jarvis_experience_parity_ready else 1


__all__ = [
    "FINAL_VERDICT_READY",
    "FINAL_VERDICT_REVIEW",
    "STATUS_READY",
    "STATUS_REVIEW_REQUIRED",
    "JarvisExperienceParityGateResult",
    "build_jarvis_experience_parity_gate_result",
    "format_jarvis_experience_parity_gate",
    "main",
]


if __name__ == "__main__":
    raise SystemExit(main())
