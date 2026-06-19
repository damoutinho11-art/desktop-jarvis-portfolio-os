from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping

from jarvis.runtime.data_readiness_status import build_data_readiness_status_result
from jarvis.runtime.multi_candidate_instrument_selector import build_fast_product_instrument_summary
from jarvis.runtime.news_coverage_readiness import build_news_coverage_readiness_result
from jarvis.runtime.product_mode_operator import build_product_mode_result
from jarvis.runtime.safety import build_safety_check_console_output

STATUS_READY = "JARVIS_V96_0_PRODUCT_API_LAYER_READY_SAFE"
STATUS_REVIEW_REQUIRED = "JARVIS_V96_0_PRODUCT_API_LAYER_REVIEW_REQUIRED_SAFE"
DEFAULT_OUTPUT_PATH = "outputs/product_api_latest.json"


@dataclass(frozen=True)
class ProductApiResult:
    status: str
    current_date: str
    api_ready: bool
    dashboard_ready: bool
    chat_ready: bool
    voice_ready: bool
    product_recommendations_allowed: bool
    today_summary: dict[str, Any]
    week_plan: dict[str, Any]
    status_summary: dict[str, Any]
    data_readiness: dict[str, Any]
    news_coverage: dict[str, Any]
    instrument_summary: dict[str, Any]
    candidate_scores: list[dict[str, Any]]
    safety_status: dict[str, Any]
    warnings: list[str]
    blockers: list[str]
    report_written: bool
    report_path: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _plain(value: Any) -> dict[str, Any]:
    if isinstance(value, Mapping):
        return dict(value)
    if hasattr(value, "to_dict"):
        return value.to_dict()
    return dict(getattr(value, "__dict__", {}))


def _lines(value: Any, field: str) -> list[str]:
    raw = getattr(value, field, None)
    if raw is None:
        raw = _plain(value).get(field, [])
    return [str(item) for item in (raw or [])]


def _safety_status() -> dict[str, Any]:
    safety_output = build_safety_check_console_output()
    safety_blocked = "BLOCKED:" in safety_output and "No execution action was taken" in safety_output
    return {
        "safety_check_blocked_execution": safety_blocked,
        "manual_approval_required": True,
        "execution_forbidden": True,
        "allocation_mutation": False,
        "approval_ticket_mutation": False,
        "buy_request_created": False,
        "broker_connection": False,
        "credentials_used": False,
        "private_account_data_ingestion": False,
        "order_created": False,
        "trade_executed": False,
    }


def _money_field(data: Mapping[str, Any], key: str) -> float:
    try:
        return round(float(data.get(key) or 0.0), 2)
    except Exception:
        return 0.0


def build_product_api_result(
    *,
    current_date: str = "2026-06-18",
    output_path: str | Path = DEFAULT_OUTPUT_PATH,
    write_report: bool = False,
) -> ProductApiResult:
    today = build_product_mode_result(mode="today", current_date=current_date)
    week = build_product_mode_result(mode="week", current_date=current_date)
    status_result = build_product_mode_result(mode="status", current_date=current_date)
    data_readiness = build_data_readiness_status_result(current_date=current_date)
    news_coverage = build_news_coverage_readiness_result(current_date=current_date)

    week_data = _plain(week)
    data_readiness_data = _plain(data_readiness)
    news_coverage_data = _plain(news_coverage)

    crypto_eur = _money_field(week_data, "recommended_crypto_eur")
    etf_fund_eur = _money_field(week_data, "recommended_etf_fund_eur")
    stock_eur = _money_field(week_data, "recommended_individual_stock_eur")

    instrument_summary = build_fast_product_instrument_summary(
        crypto_lane_eur=crypto_eur,
        etf_fund_lane_eur=etf_fund_eur,
        individual_stock_lane_eur=stock_eur,
        current_date=current_date,
    )
    instrument_summary_data = instrument_summary.to_dict()

    safety = _safety_status()

    product_mode_blockers = [str(item) for item in (week_data.get("blockers") or [])]
    api_relevant_product_blockers = [
        blocker
        for blocker in product_mode_blockers
        if not blocker.startswith("unresolved local imports:")
    ]

    blockers: list[str] = []
    blockers.extend(api_relevant_product_blockers)
    blockers.extend(str(item) for item in (data_readiness_data.get("blockers") or []))
    if not data_readiness_data.get("product_recommendations_allowed"):
        blockers.append("data_readiness_does_not_allow_product_recommendations")
    if not news_coverage_data.get("news_coverage_ready"):
        blockers.append("news_coverage_not_ready")
    if not safety.get("safety_check_blocked_execution"):
        blockers.append("safety_check_did_not_block_execution")

    blockers = list(dict.fromkeys(item for item in blockers if item))

    api_ready = not blockers
    dashboard_ready = api_ready
    chat_ready = api_ready
    voice_ready = api_ready

    warnings = [
        "product API is read-only and exposes dashboard/chat/voice payloads only",
        "manual approval remains required; no execution path is created",
    ]
    warnings.extend(
        f"product-mode audit warning: {blocker}"
        for blocker in product_mode_blockers
        if blocker.startswith("unresolved local imports:")
    )
    warnings.extend(str(item) for item in (week_data.get("warnings") or []))
    warnings.extend(str(item) for item in (data_readiness_data.get("warnings") or []))
    warnings.extend(str(item) for item in (news_coverage_data.get("warnings") or []))
    warnings.extend(str(item) for item in (instrument_summary_data.get("warnings") or []))
    warnings = list(dict.fromkeys(item for item in warnings if item))

    result = ProductApiResult(
        status=STATUS_READY if api_ready else STATUS_REVIEW_REQUIRED,
        current_date=current_date,
        api_ready=api_ready,
        dashboard_ready=dashboard_ready,
        chat_ready=chat_ready,
        voice_ready=voice_ready,
        product_recommendations_allowed=bool(data_readiness_data.get("product_recommendations_allowed")),
        today_summary={
            "status": getattr(today, "status", None),
            "verdict": getattr(today, "product_verdict", None),
            "lines": _lines(today, "today_lines"),
        },
        week_plan={
            "status": getattr(week, "status", None),
            "verdict": getattr(week, "product_verdict", None),
            "monthly_contribution_eur": _money_field(week_data, "monthly_contribution_eur"),
            "emergency_top_up_eur": _money_field(week_data, "recommended_emergency_top_up_eur"),
            "crypto_eur": crypto_eur,
            "etf_fund_eur": etf_fund_eur,
            "individual_stock_eur": stock_eur,
            "lines": _lines(week, "week_lines"),
            "selected_instruments": instrument_summary_data.get("selections", []),
            "lane_totals": instrument_summary_data.get("lane_totals", {}),
        },
        status_summary={
            "status": getattr(status_result, "status", None),
            "verdict": getattr(status_result, "product_verdict", None),
            "lines": _lines(status_result, "status_lines"),
        },
        data_readiness=data_readiness_data,
        news_coverage=news_coverage_data,
        instrument_summary=instrument_summary_data,
        candidate_scores=instrument_summary_data.get("candidate_scores", []),
        safety_status=safety,
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


def format_product_api(result: ProductApiResult) -> str:
    lines = [
        "J.A.R.V.I.S. PRODUCT API",
        f"status: {result.status}",
        f"current date: {result.current_date}",
        f"api ready: {result.api_ready}",
        f"dashboard ready: {result.dashboard_ready}",
        f"chat ready: {result.chat_ready}",
        f"voice ready: {result.voice_ready}",
        f"product recommendations allowed: {result.product_recommendations_allowed}",
        "",
        "WEEK PLAN:",
        f"- monthly contribution: EUR {result.week_plan.get('monthly_contribution_eur', 0.0):.2f}",
        f"- emergency top-up: EUR {result.week_plan.get('emergency_top_up_eur', 0.0):.2f}",
        f"- crypto: EUR {result.week_plan.get('crypto_eur', 0.0):.2f}",
        f"- ETF/fund: EUR {result.week_plan.get('etf_fund_eur', 0.0):.2f}",
        f"- individual stock: EUR {result.week_plan.get('individual_stock_eur', 0.0):.2f}",
        "",
        "SELECTED INSTRUMENTS:",
    ]

    selected = result.week_plan.get("selected_instruments", []) or []
    if selected:
        for item in selected:
            lines.append(
                f"- {item.get('lane')}: {item.get('symbol')} EUR {float(item.get('amount_eur') or 0.0):.2f}"
            )
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "NEWS COVERAGE:",
            f"- news coverage ready: {result.news_coverage.get('news_coverage_ready')}",
            f"- live news fetch enabled: {result.news_coverage.get('live_news_fetch_enabled')}",
            f"- covered categories: {', '.join(result.news_coverage.get('covered_categories') or []) or 'none'}",
            "",
            "DATA READINESS:",
            f"- readiness ready: {result.data_readiness.get('data_readiness_ready')}",
            f"- missing data: {', '.join(result.data_readiness.get('missing_data') or []) or 'none'}",
            f"- missing universe: {', '.join(result.data_readiness.get('missing_universe') or []) or 'none'}",
            "",
            "SAFETY:",
            f"- safety-check blocked execution: {result.safety_status.get('safety_check_blocked_execution')}",
            f"- broker connection: {result.safety_status.get('broker_connection')}",
            f"- credentials used: {result.safety_status.get('credentials_used')}",
            f"- order created: {result.safety_status.get('order_created')}",
            f"- trade executed: {result.safety_status.get('trade_executed')}",
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
    parser = argparse.ArgumentParser(description="Run J.A.R.V.I.S. product API layer.")
    parser.add_argument("--product-api-status", action="store_true")
    parser.add_argument("--current-date", default="2026-06-18")
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--output-path", default=DEFAULT_OUTPUT_PATH)
    args = parser.parse_args(argv)

    result = build_product_api_result(
        current_date=args.current_date,
        write_report=args.write_report,
        output_path=args.output_path,
    )
    print(format_product_api(result))
    return 0 if result.api_ready else 1


__all__ = [
    "STATUS_READY",
    "STATUS_REVIEW_REQUIRED",
    "ProductApiResult",
    "build_product_api_result",
    "format_product_api",
    "main",
]


if __name__ == "__main__":
    raise SystemExit(main())
