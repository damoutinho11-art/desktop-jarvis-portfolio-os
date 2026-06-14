"""Report CLI for J.A.R.V.I.S. dynamic market source binding audit."""

from __future__ import annotations

import argparse
from pathlib import Path

from .dynamic_market_source_binding import (
    DynamicMarketSourceBindingResult,
    audit_dynamic_market_source_bindings,
)


DEFAULT_REGISTRY_PATH = "jarvis/data/dynamic_approved_universe.example.json"
DEFAULT_BINDING_PATH = "jarvis/data/dynamic_market_source_bindings.example.json"


def build_dynamic_market_source_binding_report(result: DynamicMarketSourceBindingResult) -> str:
    lines = [
        "J.A.R.V.I.S. Dynamic Market Source Binding Audit",
        "Report-only source binding check. No fetching performed.",
        f"status: {result.status}",
        f"approved asset count: {result.approved_asset_count}",
        f"binding count: {result.binding_count}",
        f"ready binding count: {result.ready_binding_count}",
        f"missing binding count: {result.missing_binding_count}",
        f"blocked binding count: {result.blocked_binding_count}",
        f"manual approval required: {result.manual_approval_required}",
        f"execution forbidden: {result.execution_forbidden}",
        "",
        "binding rows:",
    ]

    if result.rows:
        for row in result.rows:
            lines.append(
                f"- {row.asset_id} / {row.sleeve} / {row.asset_type}: "
                f"{row.status}; provider={row.source_provider}; "
                f"symbol={row.source_symbol}; cache_series_id={row.cache_series_id}; enabled={row.enabled}"
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


def report_dynamic_market_source_bindings(
    registry_path: str | Path = DEFAULT_REGISTRY_PATH,
    binding_path: str | Path = DEFAULT_BINDING_PATH,
) -> str:
    return build_dynamic_market_source_binding_report(
        audit_dynamic_market_source_bindings(registry_path, binding_path)
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Audit market source bindings for dynamic approved assets."
    )
    parser.add_argument("registry_path", nargs="?", default=DEFAULT_REGISTRY_PATH)
    parser.add_argument("binding_path", nargs="?", default=DEFAULT_BINDING_PATH)

    args = parser.parse_args()
    print(report_dynamic_market_source_bindings(args.registry_path, args.binding_path))


if __name__ == "__main__":
    main()
