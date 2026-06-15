"""Report CLI for J.A.R.V.I.S. dynamic market data source quality gate."""

from __future__ import annotations

import argparse
from pathlib import Path

from .dynamic_market_data_source_quality_gate import (
    DynamicMarketDataSourceQualityResult,
    audit_dynamic_market_data_source_quality,
)


DEFAULT_REGISTRY_PATH = "jarvis/data/dynamic_approved_universe.example.json"
DEFAULT_BINDING_PATH = "jarvis/data/dynamic_market_source_bindings.example.json"
DEFAULT_ENDPOINT_PATH = "jarvis/data/dynamic_public_data_fetcher_endpoints.example.json"
DEFAULT_MARKET_DATA_PATH = "jarvis/data/dynamic_market_data.approved_universe.example.json"


def build_dynamic_market_data_source_quality_report(
    result: DynamicMarketDataSourceQualityResult,
) -> str:
    lines = [
        "J.A.R.V.I.S. Dynamic Market Data Source Quality Gate",
        "Report-only source quality gate. No fetching, broker integration, or execution performed.",
        f"status: {result.status}",
        f"approved asset count: {result.approved_asset_count}",
        f"endpoint count: {result.endpoint_count}",
        f"binding count: {result.binding_count}",
        f"market series count: {result.market_series_count}",
        f"ready row count: {result.ready_row_count}",
        f"blocked row count: {result.blocked_row_count}",
        f"manual approval required: {result.manual_approval_required}",
        f"raw data unverified: {result.raw_data_unverified}",
        f"execution forbidden: {result.execution_forbidden}",
        "",
        "rows:",
    ]

    if result.rows:
        for row in result.rows:
            lines.append(
                f"- {row.asset_id}: {row.status}; "
                f"source_provider={row.source_provider}; source_type={row.source_type}; "
                f"freshness={row.freshness_status}; identity={row.identity_status}"
            )
            for warning in row.warnings:
                lines.append(f"  warning: {warning}")
            for blocker in row.blockers:
                lines.append(f"  blocker: {blocker}")
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
            "- no market fetch performed",
            "- no broker integration",
            "- no buy request created",
            "- no approval granted",
            "- no execution",
            "- no trades executed",
        ]
    )

    return "\n".join(lines)


def report_dynamic_market_data_source_quality(
    registry_path: str | Path = DEFAULT_REGISTRY_PATH,
    binding_path: str | Path = DEFAULT_BINDING_PATH,
    endpoint_path: str | Path = DEFAULT_ENDPOINT_PATH,
    market_data_path: str | Path = DEFAULT_MARKET_DATA_PATH,
) -> str:
    return build_dynamic_market_data_source_quality_report(
        audit_dynamic_market_data_source_quality(
            registry_path,
            binding_path,
            endpoint_path,
            market_data_path,
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the dynamic market data source quality gate."
    )
    parser.add_argument("registry_path", nargs="?", default=DEFAULT_REGISTRY_PATH)
    parser.add_argument("binding_path", nargs="?", default=DEFAULT_BINDING_PATH)
    parser.add_argument("endpoint_path", nargs="?", default=DEFAULT_ENDPOINT_PATH)
    parser.add_argument("market_data_path", nargs="?", default=DEFAULT_MARKET_DATA_PATH)

    args = parser.parse_args()
    print(
        report_dynamic_market_data_source_quality(
            args.registry_path,
            args.binding_path,
            args.endpoint_path,
            args.market_data_path,
        )
    )


if __name__ == "__main__":
    main()
