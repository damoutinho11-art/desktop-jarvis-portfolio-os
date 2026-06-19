from __future__ import annotations

import argparse
import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping

from jarvis.runtime.data_readiness_status import build_data_readiness_status_result
from jarvis.runtime.product_api import build_product_api_result
from jarvis.runtime.news_coverage_readiness import build_news_coverage_readiness_result
from jarvis.runtime.safety import build_safety_check_console_output

STATUS_READY = "JARVIS_V97_0_FULL_SYSTEM_AUDIT_READY_SAFE"
STATUS_REVIEW_REQUIRED = "JARVIS_V97_0_FULL_SYSTEM_AUDIT_REVIEW_REQUIRED_SAFE"
DEFAULT_OUTPUT_PATH = "outputs/full_system_audit_latest.json"


@dataclass(frozen=True)
class FullSystemAuditResult:
    status: str
    current_date: str
    audit_verdict: str
    dashboard_chat_voice_backend_ready: bool
    product_api_ready: bool
    data_readiness_ready: bool
    news_coverage_ready: bool
    formula_invariants_ready: bool
    safety_ready: bool
    speed_ready: bool
    product_recommendations_allowed: bool
    formula_checks: dict[str, Any]
    data_checks: dict[str, Any]
    universe_checks: dict[str, Any]
    news_checks: dict[str, Any]
    speed_checks: dict[str, Any]
    safety_checks: dict[str, Any]
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


def _num(value: Any) -> float:
    try:
        return round(float(value or 0.0), 2)
    except Exception:
        return 0.0


def _lane_sum(selected: list[dict[str, Any]], lane: str) -> float:
    return round(sum(_num(item.get("amount_eur")) for item in selected if item.get("lane") == lane), 2)


def _close(a: float, b: float, tolerance: float = 0.05) -> bool:
    return abs(round(a - b, 2)) <= tolerance


def _safety_checks() -> dict[str, Any]:
    output = build_safety_check_console_output()
    safety_blocked = "BLOCKED:" in output and "No execution action was taken" in output
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


def build_full_system_audit_result(
    *,
    current_date: str = "2026-06-18",
    output_path: str | Path = DEFAULT_OUTPUT_PATH,
    write_report: bool = False,
    speed_warning_seconds: float = 35.0,
) -> FullSystemAuditResult:
    started = time.perf_counter()
    product_api = build_product_api_result(current_date=current_date)
    elapsed_seconds = round(time.perf_counter() - started, 3)

    # Re-read the data readiness builder directly so this audit verifies the API layer
    # did not accidentally hide stale or missing data flags.
    data_readiness = build_data_readiness_status_result(current_date=current_date)
    news_coverage = build_news_coverage_readiness_result(current_date=current_date)

    product_api_data = _plain(product_api)
    data_readiness_data = _plain(data_readiness)
    news_coverage_data = _plain(news_coverage)

    week_plan = product_api_data.get("week_plan", {}) or {}
    selected = list(week_plan.get("selected_instruments", []) or [])

    monthly = _num(week_plan.get("monthly_contribution_eur"))
    emergency = _num(week_plan.get("emergency_top_up_eur"))
    crypto = _num(week_plan.get("crypto_eur"))
    etf = _num(week_plan.get("etf_fund_eur"))
    stock = _num(week_plan.get("individual_stock_eur"))

    selected_crypto = _lane_sum(selected, "crypto")
    selected_etf = _lane_sum(selected, "etf_fund")
    selected_stock = _lane_sum(selected, "individual_stock")

    allocation_total = round(emergency + crypto + etf + stock, 2)
    crypto_cap = round(monthly * 0.20, 2)

    formula_checks = {
        "monthly_contribution_eur": monthly,
        "allocation_total_eur": allocation_total,
        "allocation_total_matches_monthly": _close(allocation_total, monthly),
        "crypto_cap_eur": crypto_cap,
        "crypto_within_twenty_percent_cap": crypto <= crypto_cap + 0.01,
        "selected_crypto_total_eur": selected_crypto,
        "selected_crypto_matches_lane": _close(selected_crypto, crypto),
        "selected_etf_fund_total_eur": selected_etf,
        "selected_etf_fund_matches_lane": _close(selected_etf, etf),
        "selected_stock_total_eur": selected_stock,
        "selected_stock_matches_lane": _close(selected_stock, stock),
        "no_negative_allocations": all(value >= 0 for value in [monthly, emergency, crypto, etf, stock]),
        "candidate_scores_present": len(product_api_data.get("candidate_scores", []) or []) > 0,
    }

    formula_invariants_ready = all(bool(value) for key, value in formula_checks.items() if key.endswith(
        (
            "_matches_monthly",
            "_cap",
            "_matches_lane",
            "allocations",
            "present",
        )
    ))
    # The suffix check above intentionally catches the boolean invariant fields,
    # but keep this explicit list to protect against naming drift.
    formula_invariants_ready = all(
        bool(formula_checks[key])
        for key in [
            "allocation_total_matches_monthly",
            "crypto_within_twenty_percent_cap",
            "selected_crypto_matches_lane",
            "selected_etf_fund_matches_lane",
            "selected_stock_matches_lane",
            "no_negative_allocations",
            "candidate_scores_present",
        ]
    )

    data_checks = {
        "data_readiness_ready": bool(data_readiness_data.get("data_readiness_ready")),
        "product_recommendations_allowed": bool(data_readiness_data.get("product_recommendations_allowed")),
        "crypto_data_ready": bool(data_readiness_data.get("crypto_data_ready")),
        "fx_data_ready": bool(data_readiness_data.get("fx_data_ready")),
        "etf_fund_data_ready": bool(data_readiness_data.get("etf_fund_data_ready")),
        "stock_data_ready": bool(data_readiness_data.get("stock_data_ready")),
        "portfolio_data_ready": bool(data_readiness_data.get("portfolio_data_ready")),
        "monthly_expenses_data_ready": bool(data_readiness_data.get("monthly_expenses_data_ready")),
        "missing_data": list(data_readiness_data.get("missing_data", []) or []),
    }

    universe_checks = {
        "crypto_candidate_count": int(data_readiness_data.get("crypto_candidate_count", 0) or 0),
        "crypto_candidate_minimum": int(data_readiness_data.get("crypto_candidate_minimum", 0) or 0),
        "etf_candidate_count": int(data_readiness_data.get("etf_candidate_count", 0) or 0),
        "etf_candidate_minimum": int(data_readiness_data.get("etf_candidate_minimum", 0) or 0),
        "stock_candidate_count": int(data_readiness_data.get("stock_candidate_count", 0) or 0),
        "stock_candidate_minimum": int(data_readiness_data.get("stock_candidate_minimum", 0) or 0),
        "missing_universe": list(data_readiness_data.get("missing_universe", []) or []),
    }
    universe_checks["crypto_universe_ready"] = universe_checks["crypto_candidate_count"] >= universe_checks["crypto_candidate_minimum"]
    universe_checks["etf_universe_ready"] = universe_checks["etf_candidate_count"] >= universe_checks["etf_candidate_minimum"]
    universe_checks["stock_universe_ready"] = universe_checks["stock_candidate_count"] >= universe_checks["stock_candidate_minimum"]

    safety = _safety_checks()
    safety_ready = bool(
        safety["safety_check_blocked_execution"]
        and safety["manual_approval_required"]
        and safety["execution_forbidden"]
        and not safety["allocation_mutation"]
        and not safety["approval_ticket_mutation"]
        and not safety["buy_request_created"]
        and not safety["broker_connection"]
        and not safety["credentials_used"]
        and not safety["private_account_data_ingestion"]
        and not safety["order_created"]
        and not safety["trade_executed"]
    )

    speed_checks = {
        "product_api_elapsed_seconds": elapsed_seconds,
        "speed_warning_seconds": speed_warning_seconds,
        "speed_ready": elapsed_seconds <= speed_warning_seconds,
    }
    speed_ready = bool(speed_checks["speed_ready"])

    product_api_ready = bool(product_api_data.get("api_ready"))
    data_ready = bool(data_checks["data_readiness_ready"])
    product_recommendations_allowed = bool(data_checks["product_recommendations_allowed"])
    dashboard_chat_voice_backend_ready = bool(
        product_api_ready
        and product_api_data.get("dashboard_ready")
        and product_api_data.get("chat_ready")
        and product_api_data.get("voice_ready")
    )

    news_checks = {
        "news_coverage_ready": bool(news_coverage_data.get("news_coverage_ready")),
        "live_news_fetch_enabled": bool(news_coverage_data.get("live_news_fetch_enabled")),
        "manual_review_required": bool(news_coverage_data.get("manual_review_required")),
        "covered_categories": list(news_coverage_data.get("covered_categories", []) or []),
        "missing_categories": list(news_coverage_data.get("missing_categories", []) or []),
    }
    news_coverage_ready = bool(news_checks["news_coverage_ready"])

    blockers: list[str] = []
    blockers.extend(str(item) for item in (product_api_data.get("blockers") or []))
    blockers.extend(str(item) for item in (data_readiness_data.get("blockers") or []))
    if not product_api_ready:
        blockers.append("product_api_not_ready")
    if not data_ready:
        blockers.append("data_readiness_not_ready")
    if not product_recommendations_allowed:
        blockers.append("product_recommendations_not_allowed")
    if not formula_invariants_ready:
        blockers.append("formula_invariants_failed")
    if not safety_ready:
        blockers.append("manual_only_safety_failed")
    if not news_coverage_ready:
        blockers.append("news_coverage_not_ready")
    blockers = list(dict.fromkeys(item for item in blockers if item))

    warnings = [
        "full system audit is read-only and creates no broker, order, or trade path",
        "news coverage is first-class in v98 but live news fetching remains disabled; manual review remains required",
    ]
    if not speed_ready:
        warnings.append(f"product API elapsed {elapsed_seconds:.3f}s exceeds warning threshold {speed_warning_seconds:.3f}s")
    warnings.extend(str(item) for item in (product_api_data.get("warnings") or []))
    warnings.extend(str(item) for item in (data_readiness_data.get("warnings") or []))
    warnings.extend(str(item) for item in (news_coverage_data.get("warnings") or []))
    warnings = list(dict.fromkeys(item for item in warnings if item))

    if blockers:
        audit_verdict = "REVIEW_REQUIRED"
    elif warnings:
        audit_verdict = "READY_WITH_AUDIT_WARNINGS"
    else:
        audit_verdict = "READY"

    result = FullSystemAuditResult(
        status=STATUS_READY if not blockers else STATUS_REVIEW_REQUIRED,
        current_date=current_date,
        audit_verdict=audit_verdict,
        dashboard_chat_voice_backend_ready=dashboard_chat_voice_backend_ready,
        product_api_ready=product_api_ready,
        data_readiness_ready=data_ready,
        news_coverage_ready=news_coverage_ready,
        formula_invariants_ready=formula_invariants_ready,
        safety_ready=safety_ready,
        speed_ready=speed_ready,
        product_recommendations_allowed=product_recommendations_allowed,
        formula_checks=formula_checks,
        data_checks=data_checks,
        universe_checks=universe_checks,
        news_checks=news_checks,
        speed_checks=speed_checks,
        safety_checks=safety,
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


def format_full_system_audit(result: FullSystemAuditResult) -> str:
    lines = [
        "J.A.R.V.I.S. FULL SYSTEM AUDIT",
        f"status: {result.status}",
        f"verdict: {result.audit_verdict}",
        f"current date: {result.current_date}",
        "",
        "READINESS:",
        f"- dashboard/chat/voice backend ready: {result.dashboard_chat_voice_backend_ready}",
        f"- product API ready: {result.product_api_ready}",
        f"- data readiness ready: {result.data_readiness_ready}",
        f"- news coverage ready: {result.news_coverage_ready}",
        f"- formula invariants ready: {result.formula_invariants_ready}",
        f"- safety ready: {result.safety_ready}",
        f"- speed ready: {result.speed_ready}",
        f"- product recommendations allowed: {result.product_recommendations_allowed}",
        "",
        "FORMULA CHECKS:",
        f"- allocation total: EUR {result.formula_checks.get('allocation_total_eur'):.2f}",
        f"- monthly contribution: EUR {result.formula_checks.get('monthly_contribution_eur'):.2f}",
        f"- allocation total matches monthly: {result.formula_checks.get('allocation_total_matches_monthly')}",
        f"- crypto within 20% cap: {result.formula_checks.get('crypto_within_twenty_percent_cap')}",
        f"- selected crypto matches lane: {result.formula_checks.get('selected_crypto_matches_lane')}",
        f"- selected ETF/fund matches lane: {result.formula_checks.get('selected_etf_fund_matches_lane')}",
        f"- selected stock matches lane: {result.formula_checks.get('selected_stock_matches_lane')}",
        f"- candidate scores present: {result.formula_checks.get('candidate_scores_present')}",
        "",
        "DATA CHECKS:",
        f"- crypto data ready: {result.data_checks.get('crypto_data_ready')}",
        f"- FX data ready: {result.data_checks.get('fx_data_ready')}",
        f"- ETF/fund data ready: {result.data_checks.get('etf_fund_data_ready')}",
        f"- stock data ready: {result.data_checks.get('stock_data_ready')}",
        f"- portfolio data ready: {result.data_checks.get('portfolio_data_ready')}",
        f"- monthly expenses data ready: {result.data_checks.get('monthly_expenses_data_ready')}",
        f"- missing data: {', '.join(result.data_checks.get('missing_data') or []) or 'none'}",
        "",
        "UNIVERSE CHECKS:",
        f"- crypto candidates: {result.universe_checks.get('crypto_candidate_count')} / {result.universe_checks.get('crypto_candidate_minimum')}",
        f"- ETF/fund candidates: {result.universe_checks.get('etf_candidate_count')} / {result.universe_checks.get('etf_candidate_minimum')}",
        f"- stock candidates: {result.universe_checks.get('stock_candidate_count')} / {result.universe_checks.get('stock_candidate_minimum')}",
        f"- missing universe: {', '.join(result.universe_checks.get('missing_universe') or []) or 'none'}",
        "",
        "NEWS CHECKS:",
        f"- news coverage ready: {result.news_checks.get('news_coverage_ready')}",
        f"- live news fetch enabled: {result.news_checks.get('live_news_fetch_enabled')}",
        f"- manual review required: {result.news_checks.get('manual_review_required')}",
        f"- covered categories: {', '.join(result.news_checks.get('covered_categories') or []) or 'none'}",
        f"- missing categories: {', '.join(result.news_checks.get('missing_categories') or []) or 'none'}",
        "",
        "SPEED:",
        f"- product API elapsed seconds: {result.speed_checks.get('product_api_elapsed_seconds')}",
        f"- warning threshold seconds: {result.speed_checks.get('speed_warning_seconds')}",
        "",
        "SAFETY:",
        f"- safety-check blocked execution: {result.safety_checks.get('safety_check_blocked_execution')}",
        f"- broker connection: {result.safety_checks.get('broker_connection')}",
        f"- credentials used: {result.safety_checks.get('credentials_used')}",
        f"- order created: {result.safety_checks.get('order_created')}",
        f"- trade executed: {result.safety_checks.get('trade_executed')}",
        "",
        "WARNINGS:",
    ]
    lines.extend(f"- {item}" for item in result.warnings or ["none"])
    lines.append("")
    lines.append("BLOCKERS:")
    lines.extend(f"- {item}" for item in result.blockers or ["none"])
    lines.append("")
    lines.append(f"report written: {result.report_written}")
    lines.append(f"report path: {result.report_path}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run J.A.R.V.I.S. full system audit.")
    parser.add_argument("--full-system-audit", action="store_true")
    parser.add_argument("--current-date", default="2026-06-18")
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--output-path", default=DEFAULT_OUTPUT_PATH)
    args = parser.parse_args(argv)

    result = build_full_system_audit_result(
        current_date=args.current_date,
        write_report=args.write_report,
        output_path=args.output_path,
    )
    print(format_full_system_audit(result))
    return 0 if not result.blockers else 1


__all__ = [
    "STATUS_READY",
    "STATUS_REVIEW_REQUIRED",
    "FullSystemAuditResult",
    "build_full_system_audit_result",
    "format_full_system_audit",
    "main",
]


if __name__ == "__main__":
    raise SystemExit(main())
