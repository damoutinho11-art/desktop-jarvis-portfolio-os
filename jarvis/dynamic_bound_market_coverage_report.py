"""Report CLI for J.A.R.V.I.S. dynamic bound market coverage bridge."""

from __future__ import annotations

import argparse
from pathlib import Path

from .dynamic_bound_market_coverage import (
    DynamicBoundMarketCoverageResult,
    audit_dynamic_bound_market_coverage,
)


DEFAULT_REGISTRY_PATH = "jarvis/data/dynamic_approved_universe.example.json"
DEFAULT_BINDING_PATH = "jarvis/data/dynamic_market_source_bindings.example.json"
DEFAULT_MARKET_DATA_PATH = "jarvis/data/dynamic_market_data.approved_universe.example.json"


def build_dynamic_bound_market_coverage_report(result: DynamicBoundMarketCoverageResult) -> str:
    lines = [
        "J.A.R.V.I.S. Dynamic Bound Market Coverage Bridge",
        "Report-only binding-to-market coverage bridge. No fetching performed.",
        f"status: {result.status}",
        f"binding status: {result.binding_status}",
        f"coverage status: {result.coverage_status}",
        f"approved asset count: {result.approved_asset_count}",
        f"bound series ready count: {result.bound_series_ready_count}",
        f"missing bound series count: {result.missing_bound_series_count}",
        f"blocked binding count: {result.blocked_binding_count}",
        f"manual approval required: {result.manual_approval_required}",
        f"execution forbidden: {result.execution_forbidden}",
        "",
        "bound rows:",
    ]

    if result.rows:
        for row in result.rows:
            lines.append(
                f"- {row.asset_id} / {row.sleeve} / {row.asset_type}: "
                f"{row.status}; provider={row.source_provider}; symbol={row.source_symbol}; "
                f"cache_series_id={row.cache_series_id}; market_series_present={row.market_series_present}"
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
            "- no buy request created",
            "- no approval granted",
            "- no broker integration",
            "- no execution",
            "- no trades executed",
        ]
    )

    return "\n".join(lines)


def report_dynamic_bound_market_coverage(
    registry_path: str | Path = DEFAULT_REGISTRY_PATH,
    binding_path: str | Path = DEFAULT_BINDING_PATH,
    market_data_path: str | Path = DEFAULT_MARKET_DATA_PATH,
) -> str:
    return build_dynamic_bound_market_coverage_report(
        audit_dynamic_bound_market_coverage(registry_path, binding_path, market_data_path)
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Bridge dynamic source bindings to local market coverage."
    )
    parser.add_argument("registry_path", nargs="?", default=DEFAULT_REGISTRY_PATH)
    parser.add_argument("binding_path", nargs="?", default=DEFAULT_BINDING_PATH)
    parser.add_argument("market_data_path", nargs="?", default=DEFAULT_MARKET_DATA_PATH)

    args = parser.parse_args()
    print(
        report_dynamic_bound_market_coverage(
            args.registry_path,
            args.binding_path,
            args.market_data_path,
        )
    )


if __name__ == "__main__":
    main()
