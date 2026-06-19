from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from jarvis.runtime.dashboard_contract import build_dashboard_contract_result
from jarvis.runtime.data_readiness_status import build_data_readiness_status_result
from jarvis.runtime.news_coverage_readiness import build_news_coverage_readiness_result
from jarvis.runtime.product_api import build_product_api_result
from jarvis.runtime.safety import build_safety_check_console_output


STATUS_READY = "JARVIS_V108_0_ASSISTANT_TOOL_REGISTRY_READY_SAFE"
STATUS_REVIEW_REQUIRED = "JARVIS_V108_0_ASSISTANT_TOOL_REGISTRY_REVIEW_REQUIRED_SAFE"
DEFAULT_OUTPUT_PATH = "outputs/assistant_tool_registry_latest.json"

REQUIRED_TOOL_IDS = (
    "portfolio_overview",
    "today_plan",
    "asset_lookup",
    "crypto_market_context",
    "etf_context",
    "stock_context",
    "news_context",
    "allocation_explanation",
    "risk_summary",
    "data_freshness",
    "blockers",
    "safety_status",
    "dashboard_link",
    "manual_action_checklist",
)

FORBIDDEN_TOOL_TERMS = (
    "broker",
    "credential",
    "order",
    "trade",
    "execution",
    "auto_approval",
    "buy_request",
    "sell_request",
)


@dataclass(frozen=True)
class AssistantToolContract:
    tool_id: str
    display_name: str
    description: str
    readiness: str
    data_sources_used: list[str]
    live_fetch_required: bool
    local_cache_supported: bool
    freshness_required: bool
    safety_level: str
    blockers: list[str]
    warnings: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class AssistantToolRegistryResult:
    status: str
    current_date: str
    registry_ready: bool
    tool_count: int
    ready_tool_count: int
    partial_tool_count: int
    missing_tool_count: int
    tools: list[AssistantToolContract]
    forbidden_tools_present: bool
    manual_only: bool
    execution_forbidden: bool
    broker_connection: bool
    credentials_used: bool
    order_created: bool
    trade_executed: bool
    warnings: list[str]
    blockers: list[str]
    report_written: bool
    report_path: str

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["tools"] = [tool.to_dict() for tool in self.tools]
        return data


def _safety_blocked_execution() -> bool:
    output = build_safety_check_console_output()
    return "BLOCKED:" in output and "No execution action was taken" in output


def _tool(
    tool_id: str,
    display_name: str,
    description: str,
    *,
    readiness: str,
    data_sources_used: list[str],
    live_fetch_required: bool = False,
    local_cache_supported: bool = True,
    freshness_required: bool = True,
    blockers: list[str] | None = None,
    warnings: list[str] | None = None,
) -> AssistantToolContract:
    return AssistantToolContract(
        tool_id=tool_id,
        display_name=display_name,
        description=description,
        readiness=readiness,
        data_sources_used=data_sources_used,
        live_fetch_required=live_fetch_required,
        local_cache_supported=local_cache_supported,
        freshness_required=freshness_required,
        safety_level="read_only_manual_only_no_execution",
        blockers=list(blockers or []),
        warnings=list(warnings or []),
    )


def build_assistant_tool_registry_result(
    *,
    current_date: str = "2026-06-18",
    output_path: str | Path = DEFAULT_OUTPUT_PATH,
    write_report: bool = False,
) -> AssistantToolRegistryResult:
    product = build_product_api_result(current_date=current_date)
    data_readiness = build_data_readiness_status_result(current_date=current_date)
    news = build_news_coverage_readiness_result(current_date=current_date)
    dashboard = build_dashboard_contract_result(current_date=current_date)
    safety_ok = _safety_blocked_execution()

    product_ready = bool(product.api_ready)
    data_ready = bool(data_readiness.data_readiness_ready)
    news_ready = bool(news.news_coverage_ready)
    dashboard_ready = bool(dashboard.dashboard_contract_ready)

    tools = [
        _tool(
            "portfolio_overview",
            "Portfolio overview",
            "Summarizes local product API portfolio and weekly plan state.",
            readiness="ready" if product_ready else "partial",
            data_sources_used=["product_api", "dashboard_contract"],
            blockers=[] if product_ready else list(product.blockers),
        ),
        _tool(
            "today_plan",
            "Today's plan",
            "Explains the current manual-only weekly/today plan.",
            readiness="ready" if product_ready else "partial",
            data_sources_used=["product_api.week_plan"],
            blockers=[] if product_ready else list(product.blockers),
        ),
        _tool(
            "asset_lookup",
            "Asset lookup",
            "Looks up symbols and candidate/plan metadata. Dedicated implementation arrives in v110.",
            readiness="partial",
            data_sources_used=["product_api.instrument_summary", "candidate_scores"],
            blockers=["dedicated assistant_asset_lookup tool not implemented yet"],
            warnings=["available only through existing product API summaries until v110"],
        ),
        _tool(
            "crypto_market_context",
            "Crypto market context",
            "Explains crypto lane context from local cache/readiness without pretending live data exists.",
            readiness="partial" if data_readiness.crypto_data_ready else "missing",
            data_sources_used=["data_readiness_status", "product_api.week_plan"],
            live_fetch_required=False,
            blockers=[] if data_readiness.crypto_data_ready else ["crypto data readiness is not ready"],
            warnings=["live market/news fetch is not enabled by this tool registry"],
        ),
        _tool(
            "etf_context",
            "ETF context",
            "Explains ETF/fund lane context from local product and readiness data.",
            readiness="partial" if data_readiness.etf_fund_data_ready else "missing",
            data_sources_used=["data_readiness_status", "product_api.week_plan"],
            blockers=[] if data_readiness.etf_fund_data_ready else ["ETF/fund data readiness is not ready"],
        ),
        _tool(
            "stock_context",
            "Stock context",
            "Explains individual stock lane context from local product and readiness data.",
            readiness="partial" if data_readiness.stock_data_ready else "missing",
            data_sources_used=["data_readiness_status", "product_api.week_plan"],
            blockers=[] if data_readiness.stock_data_ready else ["stock data readiness is not ready"],
        ),
        _tool(
            "news_context",
            "News context",
            "Reports news readiness and local/cached availability honestly.",
            readiness="ready" if news_ready else "partial",
            data_sources_used=["news_coverage_readiness"],
            live_fetch_required=False,
            blockers=[] if news_ready else list(news.blockers),
            warnings=["live news fetching is disabled unless a future explicit cache layer is added"],
        ),
        _tool(
            "allocation_explanation",
            "Allocation explanation",
            "Explains why current manual-only plan amounts exist; does not create orders.",
            readiness="ready" if product_ready else "partial",
            data_sources_used=["product_api.week_plan", "data_readiness_status"],
            blockers=[] if product_ready else list(product.blockers),
        ),
        _tool(
            "risk_summary",
            "Risk summary",
            "Summarizes safety, data freshness, lane risks, and blockers.",
            readiness="ready" if safety_ok else "missing",
            data_sources_used=["product_api", "data_readiness_status", "safety"],
            blockers=[] if safety_ok else ["safety check did not block execution"],
        ),
        _tool(
            "data_freshness",
            "Data freshness",
            "Reports local freshness/readiness status by lane.",
            readiness="ready" if data_ready else "partial",
            data_sources_used=["data_readiness_status"],
            blockers=[] if data_ready else list(data_readiness.blockers),
        ),
        _tool(
            "blockers",
            "Blockers",
            "Lists current product, data, and safety blockers.",
            readiness="ready",
            data_sources_used=["product_api.blockers", "data_readiness_status.blockers"],
            freshness_required=False,
        ),
        _tool(
            "safety_status",
            "Safety status",
            "Confirms no broker, credentials, orders, trades, auto-approval, or execution path.",
            readiness="ready" if safety_ok else "missing",
            data_sources_used=["safety"],
            freshness_required=False,
            blockers=[] if safety_ok else ["safety check did not block execution"],
        ),
        _tool(
            "dashboard_link",
            "Dashboard link",
            "Returns the local dashboard link/path.",
            readiness="ready" if dashboard_ready else "partial",
            data_sources_used=["dashboard_contract"],
            freshness_required=False,
            blockers=[] if dashboard_ready else list(dashboard.blockers),
        ),
        _tool(
            "manual_action_checklist",
            "Manual action checklist",
            "Lists manual checks before any external user action.",
            readiness="ready",
            data_sources_used=["safety", "product_api", "data_readiness_status"],
            freshness_required=False,
            warnings=["manual action happens outside J.A.R.V.I.S.; no buy/sell request is created"],
        ),
    ]

    tool_ids = {tool.tool_id for tool in tools}
    missing_required = [tool_id for tool_id in REQUIRED_TOOL_IDS if tool_id not in tool_ids]
    forbidden_tools_present = any(
        term in tool.tool_id.lower() for term in FORBIDDEN_TOOL_TERMS for tool in tools
    )

    blockers: list[str] = []
    if missing_required:
        blockers.append(f"missing required tools: {', '.join(missing_required)}")
    if forbidden_tools_present:
        blockers.append("forbidden execution/broker/order/trade tool id present")
    if not safety_ok:
        blockers.append("safety check did not block execution")

    warnings = [
        "assistant tool registry is a read-only capability map; it does not run broker/order/trade actions",
        "partial and missing tools are intentionally disclosed until dedicated implementations exist",
        "live market/news fetch is not enabled by this registry",
    ]

    ready_count = sum(1 for tool in tools if tool.readiness == "ready")
    partial_count = sum(1 for tool in tools if tool.readiness == "partial")
    missing_count = sum(1 for tool in tools if tool.readiness == "missing")
    registry_ready = not blockers

    result = AssistantToolRegistryResult(
        status=STATUS_READY if registry_ready else STATUS_REVIEW_REQUIRED,
        current_date=current_date,
        registry_ready=registry_ready,
        tool_count=len(tools),
        ready_tool_count=ready_count,
        partial_tool_count=partial_count,
        missing_tool_count=missing_count,
        tools=tools,
        forbidden_tools_present=forbidden_tools_present,
        manual_only=True,
        execution_forbidden=True,
        broker_connection=False,
        credentials_used=False,
        order_created=False,
        trade_executed=False,
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


def format_assistant_tool_registry(result: AssistantToolRegistryResult) -> str:
    lines = [
        "J.A.R.V.I.S. ASSISTANT TOOL REGISTRY",
        f"status: {result.status}",
        f"current date: {result.current_date}",
        f"registry ready: {result.registry_ready}",
        f"tool count: {result.tool_count}",
        f"ready tools: {result.ready_tool_count}",
        f"partial tools: {result.partial_tool_count}",
        f"missing tools: {result.missing_tool_count}",
        "",
        "TOOLS:",
    ]
    for tool in result.tools:
        lines.append(
            f"- {tool.tool_id}: {tool.readiness}; safety={tool.safety_level}; "
            f"live_fetch_required={tool.live_fetch_required}; local_cache_supported={tool.local_cache_supported}"
        )
        lines.append(f"  sources: {', '.join(tool.data_sources_used) or 'none'}")
        for warning in tool.warnings:
            lines.append(f"  warning: {warning}")
        for blocker in tool.blockers:
            lines.append(f"  blocker: {blocker}")

    lines.extend(
        [
            "",
            "SAFETY:",
            f"- manual-only: {result.manual_only}",
            f"- execution forbidden: {result.execution_forbidden}",
            f"- broker connection: {result.broker_connection}",
            f"- credentials used: {result.credentials_used}",
            f"- order created: {result.order_created}",
            f"- trade executed: {result.trade_executed}",
            f"- forbidden tools present: {result.forbidden_tools_present}",
            "",
            "WARNINGS:",
        ]
    )
    lines.extend(f"- {item}" for item in result.warnings or ["none"])
    lines.append("")
    lines.append("BLOCKERS:")
    lines.extend(f"- {item}" for item in result.blockers or ["none"])
    lines.append("")
    lines.append(f"report written: {result.report_written}")
    lines.append(f"report path: {result.report_path}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run J.A.R.V.I.S. assistant tool registry.")
    parser.add_argument("--assistant-tool-registry", action="store_true")
    parser.add_argument("--current-date", default="2026-06-18")
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--output-path", default=DEFAULT_OUTPUT_PATH)
    args = parser.parse_args(argv)

    result = build_assistant_tool_registry_result(
        current_date=args.current_date,
        output_path=args.output_path,
        write_report=args.write_report,
    )
    print(format_assistant_tool_registry(result))
    return 0 if result.registry_ready else 1


__all__ = [
    "STATUS_READY",
    "STATUS_REVIEW_REQUIRED",
    "REQUIRED_TOOL_IDS",
    "AssistantToolContract",
    "AssistantToolRegistryResult",
    "build_assistant_tool_registry_result",
    "format_assistant_tool_registry",
    "main",
]
