"""Report CLI for J.A.R.V.I.S. dynamic portfolio preflight."""

from __future__ import annotations

import argparse
from pathlib import Path

from .dynamic_portfolio_preflight import (
    DynamicPortfolioPreflightResult,
    run_dynamic_portfolio_preflight,
)


DEFAULT_HORIZON = "20y"
DEFAULT_PLAN_PATH = "jarvis/data/private/personal_weekly_contribution.local.json"
DEFAULT_SNAPSHOT_PATH = "jarvis/data/private/personal_snapshot.local.json"
DEFAULT_POLICY_PATH = "jarvis/data/portfolio_policy.example.json"
DEFAULT_REGISTRY_PATH = "jarvis/data/dynamic_approved_universe.example.json"
DEFAULT_BINDING_PATH = "jarvis/data/dynamic_market_source_bindings.example.json"
DEFAULT_MARKET_DATA_PATH = "jarvis/data/dynamic_market_data.approved_universe.example.json"


def build_dynamic_portfolio_preflight_report(result: DynamicPortfolioPreflightResult) -> str:
    lines = [
        "J.A.R.V.I.S. Dynamic Portfolio Preflight",
        "Report-only dynamic operator preflight. No fetching or execution performed.",
        f"status: {result.status}",
        f"horizon: {result.horizon}",
        f"bound market status: {result.bound_market_status}",
        f"binding status: {result.binding_status}",
        f"coverage status: {result.coverage_status}",
        f"weekly plan status: {result.weekly_plan_status}",
        f"optimizer status: {result.optimizer_status}",
        f"contribution status: {result.contribution_status}",
        f"manual approval required: {result.manual_approval_required}",
        f"execution forbidden: {result.execution_forbidden}",
        "",
        "dynamic target weights:",
    ]

    if result.dynamic_target_weights:
        for sleeve, weight in sorted(result.dynamic_target_weights.items()):
            lines.append(f"- {sleeve}: {weight:.2%}")
    else:
        lines.append("- none")

    lines.append("")
    lines.append("weekly draft plan lines:")
    if result.weekly_plan_lines:
        for line in result.weekly_plan_lines:
            sleeve = line.get("sleeve")
            asset_id = line.get("asset_id")
            platform = line.get("platform")
            amount = line.get("amount_eur")
            reason = line.get("reason")
            if isinstance(amount, int | float):
                amount_text = f"EUR {amount:.2f}"
            else:
                amount_text = str(amount)
            lines.append(f"- {sleeve} / {asset_id} / {platform}: {amount_text}; {reason}")
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


def report_dynamic_portfolio_preflight(
    horizon: str = DEFAULT_HORIZON,
    plan_path: str | Path = DEFAULT_PLAN_PATH,
    snapshot_path: str | Path = DEFAULT_SNAPSHOT_PATH,
    policy_path: str | Path = DEFAULT_POLICY_PATH,
    registry_path: str | Path = DEFAULT_REGISTRY_PATH,
    binding_path: str | Path = DEFAULT_BINDING_PATH,
    market_data_path: str | Path = DEFAULT_MARKET_DATA_PATH,
) -> str:
    return build_dynamic_portfolio_preflight_report(
        run_dynamic_portfolio_preflight(
            horizon=horizon,
            plan_path=plan_path,
            snapshot_path=snapshot_path,
            policy_path=policy_path,
            registry_path=registry_path,
            binding_path=binding_path,
            market_data_path=market_data_path,
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Run J.A.R.V.I.S. dynamic portfolio preflight.")
    parser.add_argument("horizon", nargs="?", default=DEFAULT_HORIZON)
    parser.add_argument("plan_path", nargs="?", default=DEFAULT_PLAN_PATH)
    parser.add_argument("snapshot_path", nargs="?", default=DEFAULT_SNAPSHOT_PATH)
    parser.add_argument("policy_path", nargs="?", default=DEFAULT_POLICY_PATH)
    parser.add_argument("registry_path", nargs="?", default=DEFAULT_REGISTRY_PATH)
    parser.add_argument("binding_path", nargs="?", default=DEFAULT_BINDING_PATH)
    parser.add_argument("market_data_path", nargs="?", default=DEFAULT_MARKET_DATA_PATH)

    args = parser.parse_args()
    print(
        report_dynamic_portfolio_preflight(
            horizon=args.horizon,
            plan_path=args.plan_path,
            snapshot_path=args.snapshot_path,
            policy_path=args.policy_path,
            registry_path=args.registry_path,
            binding_path=args.binding_path,
            market_data_path=args.market_data_path,
        )
    )


if __name__ == "__main__":
    main()
