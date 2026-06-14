"""Report CLI for J.A.R.V.I.S. dynamic operator status dashboard."""

from __future__ import annotations

import argparse
from pathlib import Path

from .dynamic_operator_status_dashboard import (
    DEFAULT_ENDPOINT_PATH,
    DynamicOperatorStatusResult,
    build_dynamic_operator_status,
)


DEFAULT_HORIZON = "20y"
DEFAULT_PLAN_PATH = "jarvis/data/private/personal_weekly_contribution.local.json"
DEFAULT_SNAPSHOT_PATH = "jarvis/data/private/personal_snapshot.local.json"
DEFAULT_POLICY_PATH = "jarvis/data/portfolio_policy.example.json"
DEFAULT_REGISTRY_PATH = "jarvis/data/dynamic_approved_universe.example.json"
DEFAULT_BINDING_PATH = "jarvis/data/dynamic_market_source_bindings.example.json"
DEFAULT_MARKET_DATA_PATH = "jarvis/data/dynamic_market_data.approved_universe.example.json"


def build_dynamic_operator_status_report(result: DynamicOperatorStatusResult) -> str:
    lines = [
        "J.A.R.V.I.S. Dynamic Operator Status Dashboard",
        "Report-only status index. No fetching or execution performed.",
        f"status: {result.status}",
        f"horizon: {result.horizon}",
        "",
        "chain status:",
        f"- market import plan: {result.import_plan_status}",
        f"- public data fetcher adapter: {result.public_data_fetcher_adapter_status}",
        f"- market data intake: {result.market_data_intake_status}",
        f"- portfolio preflight: {result.preflight_status}",
        f"- bound market coverage: {result.bound_market_status}",
        f"- source binding: {result.binding_status}",
        f"- market coverage: {result.coverage_status}",
        f"- optimizer: {result.optimizer_status}",
        f"- weekly plan: {result.weekly_plan_status}",
        f"- contribution: {result.contribution_status}",
        "",
        "counts:",
        f"- import ready rows: {result.import_ready_rows}",
        f"- adapted public sources: {result.adapted_source_count}",
        f"- intake ready series: {result.intake_ready_series_count}",
        f"- weekly draft plan lines: {result.weekly_plan_line_count}",
        "",
        "operator gates:",
        f"- manual approval required: {result.manual_approval_required}",
        f"- fetching forbidden: {result.fetching_forbidden}",
        f"- execution forbidden: {result.execution_forbidden}",
        "",
        "warnings:",
    ]

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


def report_dynamic_operator_status(
    horizon: str = DEFAULT_HORIZON,
    plan_path: str | Path = DEFAULT_PLAN_PATH,
    snapshot_path: str | Path = DEFAULT_SNAPSHOT_PATH,
    policy_path: str | Path = DEFAULT_POLICY_PATH,
    registry_path: str | Path = DEFAULT_REGISTRY_PATH,
    binding_path: str | Path = DEFAULT_BINDING_PATH,
    market_data_path: str | Path = DEFAULT_MARKET_DATA_PATH,
    endpoint_path: str | Path = DEFAULT_ENDPOINT_PATH,
) -> str:
    return build_dynamic_operator_status_report(
        build_dynamic_operator_status(
            horizon=horizon,
            plan_path=plan_path,
            snapshot_path=snapshot_path,
            policy_path=policy_path,
            registry_path=registry_path,
            binding_path=binding_path,
            market_data_path=market_data_path,
            endpoint_path=endpoint_path,
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Run J.A.R.V.I.S. dynamic operator status dashboard.")
    parser.add_argument("horizon", nargs="?", default=DEFAULT_HORIZON)
    parser.add_argument("plan_path", nargs="?", default=DEFAULT_PLAN_PATH)
    parser.add_argument("snapshot_path", nargs="?", default=DEFAULT_SNAPSHOT_PATH)
    parser.add_argument("policy_path", nargs="?", default=DEFAULT_POLICY_PATH)
    parser.add_argument("registry_path", nargs="?", default=DEFAULT_REGISTRY_PATH)
    parser.add_argument("binding_path", nargs="?", default=DEFAULT_BINDING_PATH)
    parser.add_argument("market_data_path", nargs="?", default=DEFAULT_MARKET_DATA_PATH)
    parser.add_argument("endpoint_path", nargs="?", default=DEFAULT_ENDPOINT_PATH)
    args = parser.parse_args()

    print(
        report_dynamic_operator_status(
            horizon=args.horizon,
            plan_path=args.plan_path,
            snapshot_path=args.snapshot_path,
            policy_path=args.policy_path,
            registry_path=args.registry_path,
            binding_path=args.binding_path,
            market_data_path=args.market_data_path,
            endpoint_path=args.endpoint_path,
        )
    )


if __name__ == "__main__":
    main()
