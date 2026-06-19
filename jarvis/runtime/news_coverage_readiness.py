from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from jarvis.runtime.safety import build_safety_check_console_output

STATUS_READY = "JARVIS_V98_0_NEWS_COVERAGE_READINESS_READY_SAFE"
STATUS_REVIEW_REQUIRED = "JARVIS_V98_0_NEWS_COVERAGE_READINESS_REVIEW_REQUIRED_SAFE"
DEFAULT_OUTPUT_PATH = "outputs/news_coverage_readiness_latest.json"

REQUIRED_CATEGORIES = [
    "macro",
    "crypto",
    "etf_fund",
    "individual_stock",
    "portfolio_risk",
]

DEFAULT_NEWS_COVERAGE_POLICY = {
    "macro": {
        "covered": True,
        "source_type": "policy_placeholder",
        "description": "macro headlines and rate/FX context must be reviewed before dashboard display",
    },
    "crypto": {
        "covered": True,
        "source_type": "policy_placeholder",
        "description": "crypto market/regulatory headlines must be reviewed before dashboard display",
    },
    "etf_fund": {
        "covered": True,
        "source_type": "policy_placeholder",
        "description": "ETF/fund market context and broad equity news must be reviewed before dashboard display",
    },
    "individual_stock": {
        "covered": True,
        "source_type": "policy_placeholder",
        "description": "selected-stock headlines and company-specific risk must be reviewed before dashboard display",
    },
    "portfolio_risk": {
        "covered": True,
        "source_type": "policy_placeholder",
        "description": "portfolio-level concentration, volatility, and risk headlines must be reviewed before dashboard display",
    },
}


@dataclass(frozen=True)
class NewsCoverageReadinessResult:
    status: str
    current_date: str
    news_coverage_ready: bool
    live_news_fetch_enabled: bool
    manual_review_required: bool
    required_categories: list[str]
    covered_categories: list[str]
    missing_categories: list[str]
    coverage_policy: dict[str, Any]
    warnings: list[str]
    blockers: list[str]
    safety_check_blocked_execution: bool
    broker_connection: bool
    credentials_used: bool
    order_created: bool
    trade_executed: bool
    report_written: bool
    report_path: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_news_coverage_readiness_result(
    *,
    current_date: str = "2026-06-18",
    output_path: str | Path = DEFAULT_OUTPUT_PATH,
    write_report: bool = False,
) -> NewsCoverageReadinessResult:
    coverage_policy = dict(DEFAULT_NEWS_COVERAGE_POLICY)
    covered = [
        category
        for category in REQUIRED_CATEGORIES
        if bool((coverage_policy.get(category) or {}).get("covered"))
    ]
    missing = [category for category in REQUIRED_CATEGORIES if category not in covered]

    safety_output = build_safety_check_console_output()
    safety_blocked = "BLOCKED:" in safety_output and "No execution action was taken" in safety_output

    blockers = list(missing)
    if not safety_blocked:
        blockers.append("safety_check_did_not_block_execution")

    warnings = [
        "news coverage lane is first-class and read-only",
        "live news fetching is not enabled in v98; this is a policy/readiness coverage contract",
        "manual review remains required before acting on any headline or recommendation",
    ]

    result = NewsCoverageReadinessResult(
        status=STATUS_READY if not blockers else STATUS_REVIEW_REQUIRED,
        current_date=current_date,
        news_coverage_ready=not blockers,
        live_news_fetch_enabled=False,
        manual_review_required=True,
        required_categories=list(REQUIRED_CATEGORIES),
        covered_categories=covered,
        missing_categories=missing,
        coverage_policy=coverage_policy,
        warnings=warnings,
        blockers=blockers,
        safety_check_blocked_execution=safety_blocked,
        broker_connection=False,
        credentials_used=False,
        order_created=False,
        trade_executed=False,
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


def format_news_coverage_readiness(result: NewsCoverageReadinessResult) -> str:
    lines = [
        "J.A.R.V.I.S. NEWS COVERAGE READINESS",
        f"status: {result.status}",
        f"current date: {result.current_date}",
        f"news coverage ready: {result.news_coverage_ready}",
        f"live news fetch enabled: {result.live_news_fetch_enabled}",
        f"manual review required: {result.manual_review_required}",
        "",
        "CATEGORIES:",
        f"- required: {', '.join(result.required_categories)}",
        f"- covered: {', '.join(result.covered_categories) or 'none'}",
        f"- missing: {', '.join(result.missing_categories) or 'none'}",
        "",
        "SAFETY:",
        f"- safety-check blocked execution: {result.safety_check_blocked_execution}",
        f"- broker connection: {result.broker_connection}",
        f"- credentials used: {result.credentials_used}",
        f"- order created: {result.order_created}",
        f"- trade executed: {result.trade_executed}",
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
    parser = argparse.ArgumentParser(description="Run J.A.R.V.I.S. news coverage readiness.")
    parser.add_argument("--news-coverage-readiness", action="store_true")
    parser.add_argument("--current-date", default="2026-06-18")
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--output-path", default=DEFAULT_OUTPUT_PATH)
    args = parser.parse_args(argv)

    result = build_news_coverage_readiness_result(
        current_date=args.current_date,
        output_path=args.output_path,
        write_report=args.write_report,
    )
    print(format_news_coverage_readiness(result))
    return 0 if not result.blockers else 1


__all__ = [
    "STATUS_READY",
    "STATUS_REVIEW_REQUIRED",
    "NewsCoverageReadinessResult",
    "build_news_coverage_readiness_result",
    "format_news_coverage_readiness",
    "main",
]


if __name__ == "__main__":
    raise SystemExit(main())
