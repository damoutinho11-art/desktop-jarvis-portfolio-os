"""J.A.R.V.I.S. v160.0 manual-only portfolio health report card."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping

from jarvis.runtime.product_api import build_product_api_result

STATUS_READY = "JARVIS_V160_0_PORTFOLIO_HEALTH_REPORT_CARD_READY_SAFE"
STATUS_REVIEW_REQUIRED = "JARVIS_V160_0_PORTFOLIO_HEALTH_REPORT_CARD_REVIEW_REQUIRED_SAFE"
DEFAULT_OUTPUT_PATH = "outputs/portfolio_health_report_card_latest.json"


@dataclass(frozen=True)
class PortfolioHealthReportCardResult:
    status: str
    current_date: str
    overall_status: str
    report_card_ready: bool
    readiness_score: int
    diversification_score: int
    concentration_risk: dict[str, Any]
    data_freshness_score: int
    emergency_fund_status: dict[str, Any]
    monthly_contribution_status: dict[str, Any]
    market_data_status: dict[str, Any]
    manual_plan_quality: dict[str, Any]
    safety_status: dict[str, Any]
    top_strengths: list[str]
    review_notes: list[str]
    blockers: list[str]
    warnings: list[str]
    score_components: dict[str, Any]
    financial_advice: bool
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


def _money(value: Any) -> float:
    try:
        return round(float(value or 0.0), 2)
    except Exception:
        return 0.0


def _dedupe(items: list[str]) -> list[str]:
    return list(dict.fromkeys(str(item) for item in items if str(item)))


def _bounded(value: float) -> int:
    return max(0, min(100, int(round(value))))


def _safety_status(product: Mapping[str, Any]) -> dict[str, Any]:
    raw = dict(product.get("safety_status") or {})
    safety_ready = bool(
        raw.get("safety_check_blocked_execution")
        and raw.get("manual_approval_required")
        and raw.get("execution_forbidden")
        and not raw.get("allocation_mutation")
        and not raw.get("approval_ticket_mutation")
        and not raw.get("buy_request_created")
        and not raw.get("broker_connection")
        and not raw.get("credentials_used")
        and not raw.get("private_account_data_ingestion")
        and not raw.get("order_created")
        and not raw.get("trade_executed")
    )
    return {
        "safety_ready": safety_ready,
        "manual_only": bool(raw.get("manual_approval_required")),
        "execution_forbidden": bool(raw.get("execution_forbidden")),
        "broker_connection_enabled": bool(raw.get("broker_connection")),
        "credentials_required": bool(raw.get("credentials_used")),
        "private_account_ingestion_enabled": bool(raw.get("private_account_data_ingestion")),
        "request_creation_enabled": bool(raw.get("buy_request_created")),
        "external_instruction_created": bool(raw.get("order_created")),
        "external_completion_recorded": bool(raw.get("trade_executed")),
        "auto_approval_enabled": False,
        "allocation_mutation": bool(raw.get("allocation_mutation")),
        "approval_mutation": bool(raw.get("approval_ticket_mutation")),
    }


def _diversification(holdings: Mapping[str, Any], week: Mapping[str, Any]) -> tuple[int, dict[str, Any], list[str]]:
    positions = list(holdings.get("positions") or [])
    confirmed = [item for item in positions if item.get("confirmed")]
    selected = list(week.get("selected_instruments") or [])
    warnings: list[str] = []
    if not confirmed:
        warnings.append("manual holdings missing; diversification uses current manual plan only")
        lanes = {str(item.get("lane") or "") for item in selected if item.get("lane")}
        score = 55 + min(len(lanes), 3) * 5
        concentration = {
            "status": "review_notes",
            "largest_position_pct": None,
            "positions_count": 0,
            "basis": "manual_plan_only",
            "notes": ["holdings are not confirmed locally"],
        }
        return _bounded(score), concentration, warnings

    values = [_money(item.get("market_value_eur") if item.get("market_value_eur") is not None else item.get("cost_basis_eur")) for item in confirmed]
    total = sum(values)
    largest = max(values) if values else 0.0
    largest_pct = round((largest / total) * 100, 2) if total else None
    count = len(confirmed)
    score = 45 + min(count, 8) * 5
    if largest_pct is not None and largest_pct > 50:
        score -= 20
    elif largest_pct is not None and largest_pct > 35:
        score -= 10
    concentration = {
        "status": "balanced" if largest_pct is not None and largest_pct <= 35 else "review_notes",
        "largest_position_pct": largest_pct,
        "positions_count": count,
        "basis": "manual_holdings",
        "notes": ["largest position share computed from confirmed manual holdings"],
    }
    return _bounded(score), concentration, warnings


def _data_freshness(product: Mapping[str, Any]) -> tuple[int, dict[str, Any]]:
    data = dict(product.get("data_readiness") or {})
    live = dict(product.get("live_news_context") or {})
    market_ready = bool(data.get("data_readiness_ready"))
    missing_data = list(data.get("missing_data") or [])
    missing_universe = list(data.get("missing_universe") or [])
    score = 80 if market_ready else 60
    score -= min(len(missing_data) * 6 + len(missing_universe) * 4, 35)
    if live.get("cache_loaded"):
        score += 5
    return _bounded(score), {
        "status": "ready" if score >= 70 else "review_notes",
        "data_readiness_ready": market_ready,
        "missing_data": missing_data,
        "missing_universe": missing_universe,
        "live_news_cache_loaded": bool(live.get("cache_loaded")),
        "source_failures": len(live.get("source_failures") or []),
    }


def _emergency_status(week: Mapping[str, Any]) -> dict[str, Any]:
    top_up = _money(week.get("emergency_top_up_eur"))
    return {
        "status": "ready" if top_up <= 0 else "review_notes",
        "top_up_eur": top_up,
        "explanation": "emergency sleeve has no top-up in current manual plan" if top_up <= 0 else "current manual plan includes emergency top-up",
    }


def _monthly_status(week: Mapping[str, Any]) -> dict[str, Any]:
    monthly = _money(week.get("monthly_contribution_eur"))
    lane_total = sum(_money(week.get(key)) for key in ("emergency_top_up_eur", "crypto_eur", "etf_fund_eur", "individual_stock_eur"))
    diff = round(monthly - lane_total, 2)
    return {
        "status": "ready" if monthly > 0 and abs(diff) <= 1.0 else "review_notes",
        "monthly_contribution_eur": monthly,
        "planned_lane_total_eur": round(lane_total, 2),
        "difference_eur": diff,
        "explanation": "manual plan total is close to monthly contribution" if abs(diff) <= 1.0 else "manual plan total needs review against monthly contribution",
    }


def _manual_plan_quality(week: Mapping[str, Any], product: Mapping[str, Any]) -> dict[str, Any]:
    selected = list(week.get("selected_instruments") or [])
    product_allowed = bool(product.get("product_recommendations_allowed"))
    selected_with_symbols = [item for item in selected if item.get("symbol")]
    status = "ready" if product_allowed and selected_with_symbols else "review_notes"
    return {
        "status": status,
        "selected_instruments_count": len(selected_with_symbols),
        "product_recommendations_allowed": product_allowed,
        "explanation": "manual plan has selected instrument context" if selected_with_symbols else "manual plan has no selected instrument context",
    }


def build_portfolio_health_report_card_result(
    *,
    current_date: str = "2026-06-21",
    product_api_result: Mapping[str, Any] | Any | None = None,
    write_report: bool = False,
    output_path: str | Path = DEFAULT_OUTPUT_PATH,
) -> PortfolioHealthReportCardResult:
    product = _plain(product_api_result) if product_api_result is not None else _plain(build_product_api_result(current_date=current_date))
    week = dict(product.get("week_plan") or {})
    holdings = dict(product.get("manual_holdings") or {})
    safety = _safety_status(product)
    diversification_score, concentration_risk, diversification_warnings = _diversification(holdings, week)
    data_freshness_score, market_data_status = _data_freshness(product)
    emergency_fund_status = _emergency_status(week)
    monthly_contribution_status = _monthly_status(week)
    manual_plan_quality = _manual_plan_quality(week, product)

    blockers: list[str] = []
    if not safety.get("safety_ready"):
        blockers.append("manual_only_safety_not_ready")
    if product.get("blockers"):
        blockers.extend(str(item) for item in product.get("blockers") or [])

    warnings: list[str] = [
        "portfolio health report card is local and read-only",
        "report card is not financial advice",
    ]
    warnings.extend(diversification_warnings)
    if not holdings.get("holdings_ready"):
        warnings.append("manual holdings missing or not confirmed; this is a warning, not a blocker")
    if product.get("warnings"):
        warning_count = len(product.get("warnings") or [])
        warnings.append(f"underlying product API emitted {warning_count} warning(s); review source context if needed")
    warnings = _dedupe(warnings)

    plan_score = 80 if manual_plan_quality.get("status") == "ready" else 60
    monthly_score = 85 if monthly_contribution_status.get("status") == "ready" else 60
    emergency_score = 85 if emergency_fund_status.get("status") == "ready" else 70
    safety_score = 100 if safety.get("safety_ready") else 0
    readiness_score = _bounded(
        diversification_score * 0.20
        + data_freshness_score * 0.25
        + plan_score * 0.20
        + monthly_score * 0.15
        + emergency_score * 0.10
        + safety_score * 0.10
    )

    top_strengths = []
    if safety.get("safety_ready"):
        top_strengths.append("manual-only safety invariant is active")
    if monthly_contribution_status.get("status") == "ready":
        top_strengths.append("monthly contribution math is explainable")
    if manual_plan_quality.get("status") == "ready":
        top_strengths.append("manual plan has selected instrument context")
    if market_data_status.get("data_readiness_ready"):
        top_strengths.append("market data readiness gate is available")

    review_notes = []
    if not holdings.get("holdings_ready"):
        review_notes.append("enter or confirm manual holdings when available")
    if concentration_risk.get("status") != "balanced":
        review_notes.append("review concentration after confirmed holdings are entered")
    if market_data_status.get("status") != "ready":
        review_notes.append("review missing market data fields before relying on context")
    if manual_plan_quality.get("status") != "ready":
        review_notes.append("review manual plan context before using the report card")

    report_card_ready = not blockers
    if report_card_ready and readiness_score >= 75:
        overall_status = "ready"
    elif report_card_ready:
        overall_status = "review_notes"
    else:
        overall_status = "blocked"

    result = PortfolioHealthReportCardResult(
        status=STATUS_READY if report_card_ready else STATUS_REVIEW_REQUIRED,
        current_date=current_date,
        overall_status=overall_status,
        report_card_ready=report_card_ready,
        readiness_score=readiness_score,
        diversification_score=diversification_score,
        concentration_risk=concentration_risk,
        data_freshness_score=data_freshness_score,
        emergency_fund_status=emergency_fund_status,
        monthly_contribution_status=monthly_contribution_status,
        market_data_status=market_data_status,
        manual_plan_quality=manual_plan_quality,
        safety_status=safety,
        top_strengths=_dedupe(top_strengths),
        review_notes=_dedupe(review_notes),
        blockers=_dedupe(blockers),
        warnings=warnings,
        score_components={
            "diversification_score": {"score": diversification_score, "weight": 0.20, "basis": concentration_risk.get("basis")},
            "data_freshness_score": {"score": data_freshness_score, "weight": 0.25, "basis": market_data_status},
            "manual_plan_score": {"score": plan_score, "weight": 0.20, "basis": manual_plan_quality},
            "monthly_contribution_score": {"score": monthly_score, "weight": 0.15, "basis": monthly_contribution_status},
            "emergency_fund_score": {"score": emergency_score, "weight": 0.10, "basis": emergency_fund_status},
            "safety_score": {"score": safety_score, "weight": 0.10, "basis": safety},
        },
        financial_advice=False,
        report_written=bool(write_report),
        report_path=str(output_path),
    )
    if write_report:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        Path(output_path).write_text(json.dumps(result.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def format_portfolio_health_report_card(result: PortfolioHealthReportCardResult) -> str:
    lines = [
        "J.A.R.V.I.S. PORTFOLIO HEALTH REPORT CARD",
        f"status: {result.status}",
        f"current date: {result.current_date}",
        f"overall status: {result.overall_status}",
        f"report card ready: {result.report_card_ready}",
        f"readiness score: {result.readiness_score}",
        f"diversification score: {result.diversification_score}",
        f"data freshness score: {result.data_freshness_score}",
        f"financial advice: {result.financial_advice}",
        "",
        "SECTION STATUS:",
        f"- concentration risk: {result.concentration_risk.get('status')}",
        f"- emergency fund: {result.emergency_fund_status.get('status')}",
        f"- monthly contribution: {result.monthly_contribution_status.get('status')}",
        f"- market data: {result.market_data_status.get('status')}",
        f"- manual plan quality: {result.manual_plan_quality.get('status')}",
        f"- safety: {result.safety_status.get('safety_ready')}",
        "",
        "TOP STRENGTHS:",
    ]
    lines.extend(f"- {item}" for item in result.top_strengths or ["none"])
    lines.extend(["", "REVIEW NOTES:"])
    lines.extend(f"- {item}" for item in result.review_notes or ["none"])
    lines.extend(["", "SCORE COMPONENTS:"])
    for key, item in result.score_components.items():
        lines.append(f"- {key}: score={item.get('score')}; weight={item.get('weight')}; basis={item.get('basis')}")
    lines.extend(["", "SAFETY STATUS:"])
    for key, value in result.safety_status.items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "WARNINGS:"])
    lines.extend(f"- {item}" for item in result.warnings or ["none"])
    lines.extend(["", "BLOCKERS:"])
    lines.extend(f"- {item}" for item in result.blockers or ["none"])
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build the manual-only portfolio health report card.")
    parser.add_argument("--portfolio-health-report-card", action="store_true")
    parser.add_argument("--current-date", default="2026-06-21")
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--output-path", default=DEFAULT_OUTPUT_PATH)
    args = parser.parse_args(argv)
    result = build_portfolio_health_report_card_result(
        current_date=args.current_date,
        write_report=args.write_report,
        output_path=args.output_path,
    )
    print(format_portfolio_health_report_card(result))
    return 0 if result.report_card_ready else 1


__all__ = [
    "STATUS_READY",
    "STATUS_REVIEW_REQUIRED",
    "PortfolioHealthReportCardResult",
    "build_portfolio_health_report_card_result",
    "format_portfolio_health_report_card",
    "main",
]


if __name__ == "__main__":
    raise SystemExit(main())


