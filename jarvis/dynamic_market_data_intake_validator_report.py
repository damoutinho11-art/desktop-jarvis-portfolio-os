"""Report CLI for J.A.R.V.I.S. dynamic market data intake validator."""

from __future__ import annotations

import argparse
from pathlib import Path

from .dynamic_market_data_intake_validator import (
    DynamicMarketDataIntakeResult,
    validate_dynamic_market_data_intake,
)


DEFAULT_REGISTRY_PATH = "jarvis/data/dynamic_approved_universe.example.json"
DEFAULT_BINDING_PATH = "jarvis/data/dynamic_market_source_bindings.example.json"
DEFAULT_MARKET_DATA_PATH = "jarvis/data/dynamic_market_data.approved_universe.example.json"


def build_dynamic_market_data_intake_report(result: DynamicMarketDataIntakeResult) -> str:
    lines = [
        "J.A.R.V.I.S. Dynamic Market Data Intake Validator",
        "Report-only local market-data intake validation. No fetching performed.",
        f"status: {result.status}",
        f"import plan status: {result.import_plan_status}",
        f"expected series count: {result.expected_series_count}",
        f"ready series count: {result.ready_series_count}",
        f"blocked series count: {result.blocked_series_count}",
        f"extra series count: {result.extra_series_count}",
        f"manual approval required: {result.manual_approval_required}",
        f"fetching forbidden: {result.fetching_forbidden}",
        f"execution forbidden: {result.execution_forbidden}",
        "",
        "intake rows:",
    ]

    for row in result.rows:
        lines.append(
            f"- {row.asset_id} / {row.sleeve} / {row.asset_type}: {row.status}; "
            f"series={row.planned_market_series_id}; currency={row.observed_currency}; "
            f"prices={row.price_count}"
        )
        for warning in row.warnings:
            lines.append(f"  warning: {warning}")
        for blocker in row.blockers:
            lines.append(f"  blocker: {blocker}")

    if not result.rows:
        lines.append("- none")

    lines.append("")
    lines.append("warnings:")
    lines.extend(f"- {warning}" for warning in result.warnings) if result.warnings else lines.append("- none")

    lines.append("")
    lines.append("blockers:")
    lines.extend(f"- {blocker}" for blocker in result.blockers) if result.blockers else lines.append("- none")

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


def report_dynamic_market_data_intake(
    registry_path: str | Path = DEFAULT_REGISTRY_PATH,
    binding_path: str | Path = DEFAULT_BINDING_PATH,
    market_data_path: str | Path = DEFAULT_MARKET_DATA_PATH,
) -> str:
    return build_dynamic_market_data_intake_report(
        validate_dynamic_market_data_intake(registry_path, binding_path, market_data_path)
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate local dynamic market data intake.")
    parser.add_argument("registry_path", nargs="?", default=DEFAULT_REGISTRY_PATH)
    parser.add_argument("binding_path", nargs="?", default=DEFAULT_BINDING_PATH)
    parser.add_argument("market_data_path", nargs="?", default=DEFAULT_MARKET_DATA_PATH)
    args = parser.parse_args()

    print(report_dynamic_market_data_intake(args.registry_path, args.binding_path, args.market_data_path))


if __name__ == "__main__":
    main()
