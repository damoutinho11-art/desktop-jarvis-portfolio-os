"""Report CLI for J.A.R.V.I.S. dynamic allocation weekly plan bridge."""

from __future__ import annotations

import argparse
from pathlib import Path

from .dynamic_allocation_weekly_plan import DynamicWeeklyPlanResult, build_dynamic_weekly_plan


DEFAULT_PLAN_PATH = "jarvis/data/private/personal_weekly_contribution.local.json"
DEFAULT_SNAPSHOT_PATH = "jarvis/data/private/personal_snapshot.local.json"
DEFAULT_POLICY_PATH = "jarvis/data/portfolio_policy.example.json"
DEFAULT_REGISTRY_PATH = "jarvis/data/dynamic_approved_universe.example.json"
DEFAULT_MARKET_DATA_PATH = "jarvis/data/dynamic_market_data.approved_universe.example.json"


def _format_percent(value: float) -> str:
    return f"{value * 100:.2f}%"


def _format_eur(value: float) -> str:
    return f"EUR {value:.2f}"


def build_dynamic_weekly_plan_report(result: DynamicWeeklyPlanResult) -> str:
    lines = [
        "J.A.R.V.I.S. Dynamic Weekly Plan Report",
        "Report-only dynamic contribution bridge. No recommendations executed.",
        f"status: {result.status}",
        f"optimizer status: {result.optimizer_result.status}",
        f"contribution status: {result.contribution_result.status if result.contribution_result else 'none'}",
        f"horizon: {result.optimizer_result.horizon}",
        f"manual approval required: {result.manual_approval_required}",
        f"execution forbidden: {result.execution_forbidden}",
        "",
        "dynamic target weights:",
    ]

    for sleeve_id, weight in sorted(result.optimizer_result.proposed_targets.items()):
        lines.append(f"- {sleeve_id}: {_format_percent(weight)}")

    lines.append("")
    lines.append("weekly draft plan lines:")
    if result.contribution_result and result.contribution_result.plan_lines:
        for line in result.contribution_result.plan_lines:
            lines.append(
                f"- {line.sleeve_id} / {line.asset_id} / {line.platform}: "
                f"{_format_eur(line.amount_eur)}; {line.reason}"
            )
    else:
        lines.append("- none")

    lines.append("")
    lines.append("reasons:")
    if result.optimizer_result.reasons:
        lines.extend(f"- {reason}" for reason in result.optimizer_result.reasons)
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


def report_dynamic_weekly_plan(
    horizon: str,
    plan_path: str | Path = DEFAULT_PLAN_PATH,
    snapshot_path: str | Path = DEFAULT_SNAPSHOT_PATH,
    policy_path: str | Path = DEFAULT_POLICY_PATH,
    registry_path: str | Path = DEFAULT_REGISTRY_PATH,
    market_data_path: str | Path | None = DEFAULT_MARKET_DATA_PATH,
) -> str:
    return build_dynamic_weekly_plan_report(
        build_dynamic_weekly_plan(
            horizon=horizon,
            plan_path=plan_path,
            snapshot_path=snapshot_path,
            policy_path=policy_path,
            registry_path=registry_path,
            market_data_path=market_data_path,
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a report-only dynamic weekly contribution plan."
    )
    parser.add_argument("horizon", nargs="?", default="20y", help="5y, 10y, or 20y")
    parser.add_argument("plan_path", nargs="?", default=DEFAULT_PLAN_PATH)
    parser.add_argument("snapshot_path", nargs="?", default=DEFAULT_SNAPSHOT_PATH)
    parser.add_argument("policy_path", nargs="?", default=DEFAULT_POLICY_PATH)
    parser.add_argument("registry_path", nargs="?", default=DEFAULT_REGISTRY_PATH)
    parser.add_argument("market_data_path", nargs="?", default=DEFAULT_MARKET_DATA_PATH)

    args = parser.parse_args()
    print(
        report_dynamic_weekly_plan(
            horizon=args.horizon,
            plan_path=args.plan_path,
            snapshot_path=args.snapshot_path,
            policy_path=args.policy_path,
            registry_path=args.registry_path,
            market_data_path=args.market_data_path,
        )
    )


if __name__ == "__main__":
    main()
