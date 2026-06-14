"""Report CLI for J.A.R.V.I.S. dynamic market import plan."""

from __future__ import annotations

import argparse
from pathlib import Path

from .dynamic_market_import_plan import DynamicMarketImportPlanResult, build_dynamic_market_import_plan


DEFAULT_REGISTRY_PATH = "jarvis/data/dynamic_approved_universe.example.json"
DEFAULT_BINDING_PATH = "jarvis/data/dynamic_market_source_bindings.example.json"


def build_dynamic_market_import_plan_report(result: DynamicMarketImportPlanResult) -> str:
    lines = [
        "J.A.R.V.I.S. Dynamic Market Import Plan",
        "Report-only market import contract. No fetching performed.",
        f"status: {result.status}",
        f"source binding status: {result.source_binding_status}",
        f"approved asset count: {result.approved_asset_count}",
        f"import plan row count: {result.import_plan_row_count}",
        f"ready row count: {result.ready_row_count}",
        f"blocked row count: {result.blocked_row_count}",
        f"manual approval required: {result.manual_approval_required}",
        f"execution forbidden: {result.execution_forbidden}",
        f"fetching forbidden: {result.fetching_forbidden}",
        "",
        "import rows:",
    ]

    for row in result.rows:
        lines.append(
            f"- {row.asset_id} / {row.sleeve} / {row.asset_type}: {row.status}; "
            f"provider={row.source_provider}; symbol={row.source_symbol}; "
            f"series={row.planned_market_series_id}; currency={row.expected_currency}"
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


def report_dynamic_market_import_plan(
    registry_path: str | Path = DEFAULT_REGISTRY_PATH,
    binding_path: str | Path = DEFAULT_BINDING_PATH,
) -> str:
    return build_dynamic_market_import_plan_report(
        build_dynamic_market_import_plan(registry_path, binding_path)
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a dynamic market import plan.")
    parser.add_argument("registry_path", nargs="?", default=DEFAULT_REGISTRY_PATH)
    parser.add_argument("binding_path", nargs="?", default=DEFAULT_BINDING_PATH)

    args = parser.parse_args()
    print(report_dynamic_market_import_plan(args.registry_path, args.binding_path))


if __name__ == "__main__":
    main()
