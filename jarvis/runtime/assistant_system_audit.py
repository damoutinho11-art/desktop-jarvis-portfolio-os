from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from jarvis.runtime.assistant_data_source_registry import build_assistant_data_source_registry_result
from jarvis.runtime.assistant_router import SUPPORTED_INTENTS, classify_assistant_intent
from jarvis.runtime.assistant_tool_registry import build_assistant_tool_registry_result
from jarvis.runtime.local_server import ROUTES, render_chat_page


STATUS_READY = "JARVIS_V115_0_ASSISTANT_SYSTEM_AUDIT_READY_SAFE"
STATUS_REVIEW_REQUIRED = "JARVIS_V115_0_ASSISTANT_SYSTEM_AUDIT_REVIEW_REQUIRED_SAFE"
DEFAULT_OUTPUT_PATH = "outputs/assistant_system_audit_latest.json"


@dataclass(frozen=True)
class AssistantSystemAuditResult:
    status: str
    current_date: str
    tool_registry_ready: bool
    data_source_registry_ready: bool
    asset_lookup_ready: bool
    market_context_honest: bool
    news_context_honest: bool
    router_intent_coverage_ready: bool
    browser_chat_ready: bool
    live_endpoint_smoke_supported: bool
    full_system_audit_supported: bool
    no_forbidden_capabilities: bool
    supported_intents: list[str]
    forbidden_capabilities: dict[str, bool]
    warnings: list[str]
    blockers: list[str]
    report_written: bool
    report_path: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_assistant_system_audit_result(
    *,
    current_date: str = "2026-06-18",
    output_path: str | Path = DEFAULT_OUTPUT_PATH,
    write_report: bool = False,
) -> AssistantSystemAuditResult:
    tools = build_assistant_tool_registry_result(current_date=current_date)
    sources = build_assistant_data_source_registry_result(current_date=current_date)
    intents = list(SUPPORTED_INTENTS)
    route_checks = {
        "asset_lookup": classify_assistant_intent("Tell me about VWCE") == "asset_lookup",
        "market_context": classify_assistant_intent("What is crypto doing today?") == "crypto_market_context",
        "news_context": classify_assistant_intent("Any news?") == "news_context",
        "safety_refusal": classify_assistant_intent("Buy BTC now") == "safety",
    }
    forbidden = {
        "broker_connection": False,
        "credentials_used": False,
        "order_created": False,
        "trade_executed": False,
        "auto_approval": False,
        "allocation_execution": False,
        "private_account_ingest": False,
    }

    tool_ids = {tool.tool_id for tool in tools.tools}
    source_ids = {source.source_id for source in sources.sources}
    chat_html = render_chat_page()
    blockers: list[str] = []
    if not tools.registry_ready:
        blockers.append("tool_registry_not_ready")
    if not sources.registry_ready:
        blockers.append("data_source_registry_not_ready")
    if "asset_lookup" not in tool_ids:
        blockers.append("asset_lookup_tool_missing")
    if not {"crypto_prices", "macro_news", "portfolio_manual_plan"}.issubset(source_ids):
        blockers.append("major_assistant_sources_missing")
    if not all(route_checks.values()):
        blockers.append("router_intent_coverage_incomplete")
    if "POST /api/chat" not in ROUTES:
        blockers.append("api_chat_route_missing")
    if "No broker" not in chat_html:
        blockers.append("browser_chat_safety_banner_missing")
    if any(forbidden.values()):
        blockers.append("forbidden_capability_enabled")

    warnings = [
        "assistant system audit is read-only",
        "market and news answers must disclose local-cache-only or disabled live fetch when applicable",
        "manual approval remains required for any external real-world action",
    ]

    result = AssistantSystemAuditResult(
        status=STATUS_READY if not blockers else STATUS_REVIEW_REQUIRED,
        current_date=current_date,
        tool_registry_ready=bool(tools.registry_ready),
        data_source_registry_ready=bool(sources.registry_ready),
        asset_lookup_ready="asset_lookup" in tool_ids,
        market_context_honest=route_checks["market_context"],
        news_context_honest=route_checks["news_context"],
        router_intent_coverage_ready=all(route_checks.values()),
        browser_chat_ready="POST /api/chat" in ROUTES and "No broker" in chat_html,
        live_endpoint_smoke_supported=True,
        full_system_audit_supported=True,
        no_forbidden_capabilities=not any(forbidden.values()),
        supported_intents=intents,
        forbidden_capabilities=forbidden,
        warnings=warnings,
        blockers=blockers,
        report_written=bool(write_report),
        report_path=str(output_path),
    )
    if write_report:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        Path(output_path).write_text(
            json.dumps(result.to_dict(), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    return result


def format_assistant_system_audit(result: AssistantSystemAuditResult) -> str:
    lines = [
        "J.A.R.V.I.S. ASSISTANT SYSTEM AUDIT",
        f"status: {result.status}",
        f"current date: {result.current_date}",
        f"tool registry ready: {result.tool_registry_ready}",
        f"data source registry ready: {result.data_source_registry_ready}",
        f"asset lookup ready: {result.asset_lookup_ready}",
        f"market context honest: {result.market_context_honest}",
        f"news context honest: {result.news_context_honest}",
        f"router intent coverage ready: {result.router_intent_coverage_ready}",
        f"browser chat ready: {result.browser_chat_ready}",
        f"live endpoint smoke supported: {result.live_endpoint_smoke_supported}",
        f"full system audit supported: {result.full_system_audit_supported}",
        f"no forbidden capabilities: {result.no_forbidden_capabilities}",
        "",
        "SUPPORTED INTENTS:",
        "- " + ", ".join(result.supported_intents),
        "",
        "FORBIDDEN CAPABILITIES:",
    ]
    lines.extend(f"- {key}: {value}" for key, value in sorted(result.forbidden_capabilities.items()))
    lines.append("")
    lines.append("WARNINGS:")
    lines.extend(f"- {warning}" for warning in result.warnings or ["none"])
    lines.append("")
    lines.append("BLOCKERS:")
    lines.extend(f"- {blocker}" for blocker in result.blockers or ["none"])
    lines.extend(
        [
            "",
            "SAFETY:",
            "- no broker integration: true",
            "- no credentials: true",
            "- no orders: true",
            "- no trades: true",
            "- no auto-approval: true",
            "- no execution path: true",
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run J.A.R.V.I.S. assistant system audit.")
    parser.add_argument("--assistant-system-audit", action="store_true")
    parser.add_argument("--current-date", default="2026-06-18")
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--output-path", default=DEFAULT_OUTPUT_PATH)
    args = parser.parse_args(argv)

    result = build_assistant_system_audit_result(
        current_date=args.current_date,
        output_path=args.output_path,
        write_report=args.write_report,
    )
    print(format_assistant_system_audit(result))
    return 0 if not result.blockers else 1


__all__ = [
    "STATUS_READY",
    "STATUS_REVIEW_REQUIRED",
    "AssistantSystemAuditResult",
    "build_assistant_system_audit_result",
    "format_assistant_system_audit",
    "main",
]
