"""Report CLI for J.A.R.V.I.S. dynamic market coverage audit."""

from __future__ import annotations

import argparse
from pathlib import Path

from .dynamic_market_coverage_audit import (
    DynamicMarketCoverageAuditResult,
    audit_dynamic_market_coverage,
)


DEFAULT_REGISTRY_PATH = "jarvis/data/candidate_assets.example.json"
DEFAULT_MARKET_DATA_PATH = "jarvis/data/market_data.example.json"


def build_dynamic_market_coverage_audit_report(result: DynamicMarketCoverageAuditResult) -> str:
    lines = [
        "J.A.R.V.I.S. Dynamic Market Coverage Audit",
        "Report-only optimizer readiness coverage check. No recommendations generated.",
        f"status: {result.status}",
        f"approved asset count: {result.approved_asset_count}",
        f"market metric count: {result.market_metric_count}",
        f"covered asset count: {result.covered_asset_count}",
        f"missing asset count: {result.missing_asset_count}",
        f"degraded asset count: {result.degraded_asset_count}",
        f"manual approval required: {result.manual_approval_required}",
        f"execution forbidden: {result.execution_forbidden}",
        "",
        "coverage rows:",
    ]

    if result.rows:
        for row in result.rows:
            lines.append(
                f"- {row.asset_id} / {row.sleeve} / {row.asset_type}: "
                f"{row.status}; has_market_data={row.has_market_data}; metric_ready={row.metric_ready}"
            )
            if row.warnings:
                for warning in row.warnings:
                    lines.append(f"  warning: {warning}")
    else:
        lines.append("- none")

    lines.append("")
    lines.append("warnings:")
    if result.warnings:
        lines.extend(f"- {warning}" for warning in result.warnings)
    else:
        lines.append("- none")

    lines.append("")
    lines.append("blockers:")
    if result.blockers:
        lines.extend(f"- {blocker}" for blocker in result.blockers)
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "Safety:",
            "- no buy request created",
            "- no approval granted",
            "- no broker integration",
            "- no execution",
            "- no trades executed",
        ]
    )

    return "\n".join(lines)


def report_dynamic_market_coverage_audit(
    registry_path: str | Path = DEFAULT_REGISTRY_PATH,
    market_data_path: str | Path | None = DEFAULT_MARKET_DATA_PATH,
) -> str:
    return build_dynamic_market_coverage_audit_report(
        audit_dynamic_market_coverage(registry_path, market_data_path)
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Audit approved-universe market data coverage for the dynamic optimizer."
    )
    parser.add_argument("registry_path", nargs="?", default=DEFAULT_REGISTRY_PATH)
    parser.add_argument("market_data_path", nargs="?", default=DEFAULT_MARKET_DATA_PATH)

    args = parser.parse_args()
    print(report_dynamic_market_coverage_audit(args.registry_path, args.market_data_path))


if __name__ == "__main__":
    main()
