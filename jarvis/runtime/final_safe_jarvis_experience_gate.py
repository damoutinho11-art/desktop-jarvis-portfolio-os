"""J.A.R.V.I.S. v148.0 final safe daily-use experience gate."""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping

from jarvis.runtime.assistant_router import build_assistant_router_result
from jarvis.runtime.dashboard_calm_ui_freeze_gate import build_dashboard_calm_ui_freeze_gate_result
from jarvis.runtime.dashboard_noise_audit import build_dashboard_noise_audit_result
from jarvis.runtime.jarvis_session_memory import build_jarvis_session_memory_result, build_safe_session_snapshot
from jarvis.runtime.local_app_packaging_polish import build_local_app_packaging_polish_result
from jarvis.runtime.product_api import build_product_api_result
from jarvis.runtime.safety import build_safety_check_console_output
from jarvis.runtime.voice_briefing import build_voice_briefing_result
from jarvis.runtime.what_changed_since_last_time import build_what_changed_since_last_time_result

STATUS_READY = "JARVIS_V148_0_FINAL_SAFE_JARVIS_EXPERIENCE_GATE_READY_SAFE"
STATUS_REVIEW_REQUIRED = "JARVIS_V148_0_FINAL_SAFE_JARVIS_EXPERIENCE_GATE_REVIEW_REQUIRED_SAFE"
FINAL_VERDICT_READY = "READY_FOR_SAFE_DAILY_USE"
FINAL_VERDICT_REVIEW = "REVIEW_REQUIRED_BEFORE_DAILY_USE"


@dataclass(frozen=True)
class FinalSafeJarvisExperienceGateResult:
    status: str
    current_date: str
    final_verdict: str
    final_safe_jarvis_experience_ready: bool
    product_api_ready: bool
    dashboard_noise_audit_ready: bool
    calm_ui_freeze_ready: bool
    session_memory_ready: bool
    voice_briefing_ready: bool
    news_ticker_ready_or_optional: bool
    chat_personality_ready: bool
    what_changed_ready: bool
    local_app_packaging_ready: bool
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


def _plain(value: Any) -> dict[str, Any]:
    if isinstance(value, Mapping):
        return dict(value)
    if hasattr(value, "to_dict"):
        return value.to_dict()
    if hasattr(value, "__dict__"):
        return dict(value.__dict__)
    return {}


def _dedupe(items: list[str]) -> list[str]:
    return list(dict.fromkeys(str(item) for item in items if str(item)))


def _safety_check_ready() -> bool:
    text = build_safety_check_console_output()
    return "BLOCKED:" in text and "No execution action was taken" in text


def _news_ticker_ready_or_optional() -> tuple[bool, dict[str, Any]]:
    try:
        source = Path("jarvis/runtime/dashboard_contract.py").read_text(encoding="utf-8")
    except OSError as exc:
        return False, {"error": f"{type(exc).__name__}: {exc}"}
    required = [
        "Market Headlines",
        "News unavailable &mdash; not blocking today's manual plan.",
        "never recommend action from headline alone",
        "headline-tag",
    ]
    missing = [marker for marker in required if marker not in source]
    forbidden = ["buy because news", "sell because news", "stack trace", "raw JSON"]
    found = [marker for marker in forbidden if marker.lower() in source.lower()]
    return not missing and not found, {"missing": missing, "forbidden_found": found}


def build_final_safe_jarvis_experience_gate_result(
    *,
    current_date: str = "2026-06-20",
) -> FinalSafeJarvisExperienceGateResult:
    blockers: list[str] = []
    warnings: list[str] = [
        "final safe Jarvis gate is read-only and does not write dashboard, output, local memory, approval, or allocation files",
        "news and holdings remain optional warnings unless a strict gate is requested elsewhere",
    ]

    product = build_product_api_result(current_date=current_date)
    product_data = _plain(product)
    product_ready = bool(product_data.get("api_ready"))
    if not product_ready:
        blockers.append("product_api_not_ready")

    noise = build_dashboard_noise_audit_result(current_date=current_date)
    noise_ready = bool(noise.dashboard_noise_audit_ready)
    if not noise_ready:
        blockers.append("dashboard_noise_audit_not_ready")

    calm = build_dashboard_calm_ui_freeze_gate_result(current_date=current_date)
    calm_ready = bool(calm.calm_ui_freeze_gate_ready)
    if not calm_ready:
        blockers.append("calm_ui_freeze_gate_not_ready")

    session = build_jarvis_session_memory_result(mode="status", current_date=current_date)
    session_ready = bool(session.session_memory_ready)
    if not session_ready:
        blockers.append("session_memory_not_ready")

    voice = build_voice_briefing_result(current_date=current_date, product_api_result=product)
    voice_ready = bool(voice.voice_briefing_ready and "Good evening, Diogo." in voice.text)
    if not voice_ready:
        blockers.append("voice_briefing_not_ready")

    news_ready, news_proof = _news_ticker_ready_or_optional()
    if not news_ready:
        blockers.append("news_ticker_not_ready_or_optional")

    chat_plan = build_assistant_router_result(query="what is my plan today?", current_date=current_date)
    chat_refusal = build_assistant_router_result(query="buy BTC now", current_date=current_date)
    chat_ready = bool(
        chat_plan.intent == "today_plan"
        and "Good evening, Diogo." in chat_plan.reply
        and "Manual-only safety is active." in chat_plan.reply
        and chat_refusal.execution_refused
        and not chat_refusal.order_created
        and not chat_refusal.trade_executed
    )
    if not chat_ready:
        blockers.append("chat_personality_not_ready")

    current_snapshot = build_safe_session_snapshot(current_date=current_date, product_api_result=product)
    changed = build_what_changed_since_last_time_result(
        current_date=current_date,
        current_snapshot=current_snapshot,
    )
    changed_ready = bool(changed.what_changed_ready)
    if not changed_ready:
        blockers.append("what_changed_not_ready")

    packaging = build_local_app_packaging_polish_result()
    packaging_ready = bool(packaging.local_app_packaging_ready)
    if not packaging_ready:
        blockers.append("local_app_packaging_not_ready")

    safety_ready = _safety_check_ready()
    if not safety_ready:
        blockers.append("safety_check_did_not_block_execution")

    execution_forbidden = True
    broker_enabled = False
    credentials_required = False
    buy_sell_request_created = False
    order_created = False
    trade_created = False
    auto_approval = False
    private_account_ingestion = False
    allocation_mutation = False
    approval_mutation = False
    forbidden_flags_clear = not any(
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
    )
    if not (execution_forbidden and forbidden_flags_clear):
        blockers.append("forbidden_execution_path_enabled")

    warnings.extend(str(item) for item in product_data.get("warnings") or [])
    warnings.extend(noise.warnings)
    warnings.extend(calm.warnings)
    warnings.extend(session.warnings)
    warnings.extend(voice.warnings)
    warnings.extend(changed.warnings)
    warnings.extend(packaging.warnings)

    blockers = _dedupe(blockers)
    ready = not blockers
    return FinalSafeJarvisExperienceGateResult(
        status=STATUS_READY if ready else STATUS_REVIEW_REQUIRED,
        current_date=current_date,
        final_verdict=FINAL_VERDICT_READY if ready else FINAL_VERDICT_REVIEW,
        final_safe_jarvis_experience_ready=ready,
        product_api_ready=product_ready,
        dashboard_noise_audit_ready=noise_ready,
        calm_ui_freeze_ready=calm_ready,
        session_memory_ready=session_ready,
        voice_briefing_ready=voice_ready,
        news_ticker_ready_or_optional=news_ready,
        chat_personality_ready=chat_ready,
        what_changed_ready=changed_ready,
        local_app_packaging_ready=packaging_ready,
        safety_check_blocks_execution=safety_ready,
        manual_only=True,
        execution_forbidden=execution_forbidden,
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
        warnings=_dedupe(warnings),
        proof={
            "product_status": product_data.get("status"),
            "dashboard_noise_status": noise.status,
            "calm_ui_status": calm.status,
            "session_memory_status": session.status,
            "voice_status": voice.status,
            "news_ticker": news_proof,
            "chat_plan_status": chat_plan.status,
            "chat_refusal_status": chat_refusal.status,
            "what_changed_status": changed.status,
            "packaging_status": packaging.status,
            "safety_blocked": safety_ready,
        },
    )


def format_final_safe_jarvis_experience_gate(result: FinalSafeJarvisExperienceGateResult) -> str:
    lines = [
        "J.A.R.V.I.S. FINAL SAFE JARVIS EXPERIENCE GATE",
        f"status: {result.status}",
        f"current date: {result.current_date}",
        f"final verdict: {result.final_verdict}",
        f"final safe Jarvis experience ready: {result.final_safe_jarvis_experience_ready}",
        "",
        "CHECKS:",
        f"- product API ready: {result.product_api_ready}",
        f"- dashboard noise audit ready: {result.dashboard_noise_audit_ready}",
        f"- calm UI freeze ready: {result.calm_ui_freeze_ready}",
        f"- session memory ready: {result.session_memory_ready}",
        f"- voice briefing ready: {result.voice_briefing_ready}",
        f"- news ticker ready or safely optional: {result.news_ticker_ready_or_optional}",
        f"- chat personality ready: {result.chat_personality_ready}",
        f"- what-changed ready: {result.what_changed_ready}",
        f"- local app packaging ready: {result.local_app_packaging_ready}",
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
    parser = argparse.ArgumentParser(description="Run the final safe J.A.R.V.I.S. experience gate.")
    parser.add_argument("--final-safe-jarvis-experience-gate", action="store_true")
    parser.add_argument("--current-date", default="2026-06-20")
    args = parser.parse_args(argv)

    result = build_final_safe_jarvis_experience_gate_result(current_date=args.current_date)
    print(format_final_safe_jarvis_experience_gate(result))
    return 0 if result.final_safe_jarvis_experience_ready else 1


__all__ = [
    "FINAL_VERDICT_READY",
    "FINAL_VERDICT_REVIEW",
    "STATUS_READY",
    "STATUS_REVIEW_REQUIRED",
    "FinalSafeJarvisExperienceGateResult",
    "build_final_safe_jarvis_experience_gate_result",
    "format_final_safe_jarvis_experience_gate",
    "main",
]


if __name__ == "__main__":
    raise SystemExit(main())
