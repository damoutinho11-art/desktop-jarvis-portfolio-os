"""Report CLI for J.A.R.V.I.S. dynamic allocation optimizer."""

from __future__ import annotations

import argparse
from pathlib import Path

from .dynamic_allocation_optimizer import (
    DynamicAllocationResult,
    propose_dynamic_allocation,
)


DEFAULT_POLICY_PATH = "jarvis/data/portfolio_policy.example.json"
DEFAULT_REGISTRY_PATH = "jarvis/data/candidate_assets.example.json"


def _format_percent(value: float) -> str:
    return f"{value * 100:.2f}%"


def build_dynamic_allocation_optimizer_report(result: DynamicAllocationResult) -> str:
    lines = [
        "J.A.R.V.I.S. Dynamic Allocation Optimizer Report",
        "Report-only dynamic policy proposal. No recommendations executed.",
        f"horizon: {result.horizon}",
        f"status: {result.status}",
        f"approved asset count: {result.approved_asset_count}",
        f"scored asset count: {result.scored_asset_count}",
        f"risk metric count: {result.risk_metric_count}",
        f"manual approval required: {result.manual_approval_required}",
        f"execution forbidden: {result.execution_forbidden}",
        "",
        "baseline targets:",
    ]

    for sleeve_id, weight in sorted(result.baseline_targets.items()):
        lines.append(f"- {sleeve_id}: {_format_percent(weight)}")

    lines.append("")
    lines.append("proposed dynamic targets:")
    for sleeve_id, weight in sorted(result.proposed_targets.items()):
        lines.append(f"- {sleeve_id}: {_format_percent(weight)}")

    lines.append("")
    lines.append("reasons:")
    if result.reasons:
        lines.extend(f"- {reason}" for reason in result.reasons)
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


def report_dynamic_allocation_optimizer(
    horizon: str,
    policy_path: str | Path = DEFAULT_POLICY_PATH,
    registry_path: str | Path = DEFAULT_REGISTRY_PATH,
    market_data_path: str | Path | None = None,
) -> str:
    result = propose_dynamic_allocation(
        horizon=horizon,
        policy_path=policy_path,
        registry_path=registry_path,
        market_data_path=market_data_path,
    )
    return build_dynamic_allocation_optimizer_report(result)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a report-only dynamic allocation policy proposal."
    )
    parser.add_argument("horizon", nargs="?", default="10y", help="5y, 10y, or 20y")
    parser.add_argument("policy_path", nargs="?", default=DEFAULT_POLICY_PATH)
    parser.add_argument("registry_path", nargs="?", default=DEFAULT_REGISTRY_PATH)
    parser.add_argument("market_data_path", nargs="?", default=None)

    args = parser.parse_args()
    print(
        report_dynamic_allocation_optimizer(
            args.horizon,
            args.policy_path,
            args.registry_path,
            args.market_data_path,
        )
    )


if __name__ == "__main__":
    main()
