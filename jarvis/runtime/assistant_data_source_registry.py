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


STATUS_READY = "JARVIS_V109_0_ASSISTANT_DATA_SOURCE_REGISTRY_READY_SAFE"
STATUS_REVIEW_REQUIRED = "JARVIS_V109_0_ASSISTANT_DATA_SOURCE_REGISTRY_REVIEW_REQUIRED_SAFE"
DEFAULT_OUTPUT_PATH = "outputs/assistant_data_source_registry_latest.json"


@dataclass(frozen=True)
class AssistantDataSource:
    source_id: str
    provider_name: str
    data_type: str
    lane: str
    requires_api_key: bool
    live_fetch_supported: bool
    local_cache_path: str | None
    freshness_policy: str
    latest_as_of: str | None
    ready_for_assistant: bool
    warnings: list[str]
    blockers: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class AssistantDataSourceRegistryResult:
    status: str
    current_date: str
    registry_ready: bool
    source_count: int
    ready_source_count: int
    partial_source_count: int
    blocked_source_count: int
    sources: list[AssistantDataSource]
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
        data["sources"] = [source.to_dict() for source in self.sources]
        return data


def _exists(path: str | None) -> bool:
    return bool(path) and Path(path).exists()


def _ignored_local_cache(path: str | None) -> bool:
    if not path:
        return False
    normalized = path.replace("\\", "/")
    return normalized.startswith("jarvis/local/") or normalized.startswith("outputs/")


def _source(
    source_id: str,
    provider_name: str,
    data_type: str,
    lane: str,
    *,
    ready_for_assistant: bool,
    local_cache_path: str | None,
    freshness_policy: str,
    latest_as_of: str | None = None,
    requires_api_key: bool = False,
    live_fetch_supported: bool = False,
    warnings: list[str] | None = None,
    blockers: list[str] | None = None,
) -> AssistantDataSource:
    source_warnings = list(warnings or [])
    source_blockers = list(blockers or [])
    if local_cache_path and not _ignored_local_cache(local_cache_path):
        source_warnings.append("local cache path is not under the ignored local/output cache locations")
    if local_cache_path and not _exists(local_cache_path):
        source_warnings.append("local cache path is configured but not present in this checkout")
    return AssistantDataSource(
        source_id=source_id,
        provider_name=provider_name,
        data_type=data_type,
        lane=lane,
        requires_api_key=requires_api_key,
        live_fetch_supported=live_fetch_supported,
        local_cache_path=local_cache_path,
        freshness_policy=freshness_policy,
        latest_as_of=latest_as_of,
        ready_for_assistant=ready_for_assistant,
        warnings=source_warnings,
        blockers=source_blockers,
    )


def _safety_ok() -> bool:
    output = build_safety_check_console_output()
    return "BLOCKED:" in output and "No execution action was taken" in output


def build_assistant_data_source_registry_result(
    *,
    current_date: str = "2026-06-18",
    output_path: str | Path = DEFAULT_OUTPUT_PATH,
    write_report: bool = False,
) -> AssistantDataSourceRegistryResult:
    data = build_data_readiness_status_result(current_date=current_date)
    news = build_news_coverage_readiness_result(current_date=current_date)
    product = build_product_api_result(current_date=current_date)
    dashboard = build_dashboard_contract_result(current_date=current_date)
    safety_ok = _safety_ok()

    sources = [
        _source(
            "crypto_prices",
            "local public/free crypto cache readiness",
            "market_price",
            "crypto",
            ready_for_assistant=bool(data.crypto_data_ready),
            local_cache_path="jarvis/local/free_research_api_cache.local.json",
            freshness_policy="must be confirmed by data_readiness_status; no live fetch in assistant registry",
            latest_as_of=None,
            warnings=["no live crypto price fetch is enabled here; use local cache/readiness only"],
            blockers=[] if data.crypto_data_ready else ["crypto_data_ready is false"],
        ),
        _source(
            "etf_fund_prices",
            "local ETF/fund public cache readiness",
            "market_price",
            "etf_fund",
            ready_for_assistant=bool(data.etf_fund_data_ready),
            local_cache_path="outputs/approval_ticket_latest.json",
            freshness_policy="must be confirmed by data_readiness_status; no live fetch in assistant registry",
            latest_as_of=None,
            blockers=[] if data.etf_fund_data_ready else ["etf_fund_data_ready is false"],
        ),
        _source(
            "stock_prices",
            "local stock public evidence readiness",
            "market_price",
            "individual_stock",
            ready_for_assistant=bool(data.stock_data_ready),
            local_cache_path="outputs/approval_ticket_latest.json",
            freshness_policy="requires symbol, price, and as_of in local public evidence",
            latest_as_of=None,
            blockers=[] if data.stock_data_ready else ["stock_data_ready is false"],
        ),
        _source(
            "fx",
            "local FX/public cache readiness",
            "fx_rate",
            "fx",
            ready_for_assistant=bool(data.fx_data_ready),
            local_cache_path="jarvis/local/free_research_api_cache.local.json",
            freshness_policy="must be confirmed by data_readiness_status",
            latest_as_of=None,
            blockers=[] if data.fx_data_ready else ["fx_data_ready is false"],
        ),
        _source(
            "macro_news",
            "news coverage readiness policy",
            "news_context",
            "macro_news",
            ready_for_assistant=bool(news.news_coverage_ready),
            local_cache_path=None,
            freshness_policy="policy/readiness only; live news fetch disabled",
            latest_as_of=None,
            live_fetch_supported=False,
            warnings=["live news fetch is disabled; no headlines are invented"],
            blockers=[] if news.news_coverage_ready else list(news.blockers),
        ),
        _source(
            "portfolio_manual_plan",
            "product API weekly/today plan",
            "portfolio_plan",
            "portfolio",
            ready_for_assistant=bool(product.api_ready),
            local_cache_path=None,
            freshness_policy="computed locally for requested current_date",
            latest_as_of=current_date,
            blockers=[] if product.api_ready else list(product.blockers),
        ),
        _source(
            "candidate_scoring",
            "product API instrument summary candidate scores",
            "candidate_score",
            "candidate_universe",
            ready_for_assistant=bool(product.candidate_scores),
            local_cache_path=None,
            freshness_policy="computed locally from current candidate/product inputs",
            latest_as_of=current_date if product.candidate_scores else None,
            blockers=[] if product.candidate_scores else ["candidate_scores are unavailable"],
        ),
        _source(
            "emergency_fund_monthly_contribution",
            "product API contribution and emergency plan",
            "personal_finance_plan",
            "personal_finance",
            ready_for_assistant=bool(product.api_ready),
            local_cache_path="jarvis/local/monthly_expenses.local.json",
            freshness_policy="manual local finance inputs where available; no private auto-ingest",
            latest_as_of=current_date,
            warnings=["private/manual finance files are not auto-ingested by assistant registry"],
            blockers=[] if product.api_ready else list(product.blockers),
        ),
        _source(
            "data_readiness_gates",
            "data readiness status",
            "readiness_gate",
            "system",
            ready_for_assistant=True,
            local_cache_path=None,
            freshness_policy="current run aggregates existing gates",
            latest_as_of=current_date,
            warnings=list(data.warnings),
        ),
        _source(
            "dashboard_product_api",
            "dashboard contract and product API",
            "operator_surface",
            "dashboard",
            ready_for_assistant=bool(product.api_ready and dashboard.dashboard_contract_ready),
            local_cache_path="outputs/dashboard_latest.html",
            freshness_policy="generated locally on demand; not market-live",
            latest_as_of=current_date,
            blockers=[] if product.api_ready and dashboard.dashboard_contract_ready else list(product.blockers) + list(dashboard.blockers),
        ),
    ]

    blockers: list[str] = []
    if not safety_ok:
        blockers.append("safety check did not block execution")
    missing_major = [source.source_id for source in sources if not source.ready_for_assistant and source.blockers]
    warnings = [
        "assistant data source registry is read-only and does not fetch live market/news data",
        "latest_as_of is only populated when an existing local surface exposes a deterministic date",
        "local cache paths under jarvis/local and outputs are ignored/generated locations, not committed private data",
    ]
    if missing_major:
        warnings.append("some sources are partial or unavailable and must be disclosed by assistant replies")

    ready_count = sum(1 for source in sources if source.ready_for_assistant)
    blocked_count = sum(1 for source in sources if source.blockers)
    partial_count = len(sources) - ready_count
    registry_ready = not blockers

    result = AssistantDataSourceRegistryResult(
        status=STATUS_READY if registry_ready else STATUS_REVIEW_REQUIRED,
        current_date=current_date,
        registry_ready=registry_ready,
        source_count=len(sources),
        ready_source_count=ready_count,
        partial_source_count=partial_count,
        blocked_source_count=blocked_count,
        sources=sources,
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


def format_assistant_data_source_registry(result: AssistantDataSourceRegistryResult) -> str:
    lines = [
        "J.A.R.V.I.S. ASSISTANT DATA SOURCE REGISTRY",
        f"status: {result.status}",
        f"current date: {result.current_date}",
        f"registry ready: {result.registry_ready}",
        f"source count: {result.source_count}",
        f"ready sources: {result.ready_source_count}",
        f"partial sources: {result.partial_source_count}",
        f"blocked sources: {result.blocked_source_count}",
        "",
        "SOURCES:",
    ]
    for source in result.sources:
        lines.append(
            f"- {source.source_id}: ready={source.ready_for_assistant}; type={source.data_type}; "
            f"lane={source.lane}; live_fetch_supported={source.live_fetch_supported}; "
            f"requires_api_key={source.requires_api_key}; latest_as_of={source.latest_as_of}"
        )
        lines.append(f"  provider: {source.provider_name}")
        lines.append(f"  local_cache_path: {source.local_cache_path or 'none'}")
        lines.append(f"  freshness_policy: {source.freshness_policy}")
        for warning in source.warnings:
            lines.append(f"  warning: {warning}")
        for blocker in source.blockers:
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
            "",
            "WARNINGS:",
        ]
    )
    lines.extend(f"- {warning}" for warning in result.warnings or ["none"])
    lines.append("")
    lines.append("BLOCKERS:")
    lines.extend(f"- {blocker}" for blocker in result.blockers or ["none"])
    lines.append("")
    lines.append(f"report written: {result.report_written}")
    lines.append(f"report path: {result.report_path}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run J.A.R.V.I.S. assistant data source registry.")
    parser.add_argument("--assistant-data-sources", action="store_true")
    parser.add_argument("--current-date", default="2026-06-18")
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--output-path", default=DEFAULT_OUTPUT_PATH)
    args = parser.parse_args(argv)

    result = build_assistant_data_source_registry_result(
        current_date=args.current_date,
        output_path=args.output_path,
        write_report=args.write_report,
    )
    print(format_assistant_data_source_registry(result))
    return 0 if result.registry_ready else 1


__all__ = [
    "STATUS_READY",
    "STATUS_REVIEW_REQUIRED",
    "AssistantDataSource",
    "AssistantDataSourceRegistryResult",
    "build_assistant_data_source_registry_result",
    "format_assistant_data_source_registry",
    "main",
]
