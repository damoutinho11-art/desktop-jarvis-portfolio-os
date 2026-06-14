"""Report CLI for J.A.R.V.I.S. dynamic command-center audit."""

from __future__ import annotations

import argparse
from pathlib import Path

from .dynamic_command_center_audit import DynamicCommandCenterAuditResult, audit_dynamic_command_center


DEFAULT_HORIZON = "20y"
DEFAULT_PLAN_PATH = "jarvis/data/private/personal_weekly_contribution.local.json"
DEFAULT_SNAPSHOT_PATH = "jarvis/data/private/personal_snapshot.local.json"
DEFAULT_POLICY_PATH = "jarvis/data/portfolio_policy.example.json"
DEFAULT_REGISTRY_PATH = "jarvis/data/dynamic_approved_universe.example.json"
DEFAULT_BINDING_PATH = "jarvis/data/dynamic_market_source_bindings.example.json"
DEFAULT_MARKET_DATA_PATH = "jarvis/data/dynamic_market_data.approved_universe.example.json"


def build_dynamic_command_center_audit_report(result: DynamicCommandCenterAuditResult) -> str:
    lines = [
        "J.A.R.V.I.S. Dynamic Portfolio Command Center Audit",
        "Final report-only dynamic command-center audit. No fetching or execution performed.",
        f"status: {result.status}",
        f"dashboard status: {result.dashboard_status}",
        f"horizon: {result.horizon}",
        f"required command count: {result.required_command_count}",
        f"ready status count: {result.ready_status_count}",
        f"manual approval required: {result.manual_approval_required}",
        f"fetching forbidden: {result.fetching_forbidden}",
        f"execution forbidden: {result.execution_forbidden}",
        "",
        "chain statuses:",
    ]

    for name, status in result.chain_statuses.items():
        lines.append(f"- {name}: {status}")

    lines.append("")
    lines.append("operator commands:")
    for command in result.required_commands:
        lines.append(f"- {command}")

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


def report_dynamic_command_center_audit(
    horizon: str = DEFAULT_HORIZON,
    plan_path: str | Path = DEFAULT_PLAN_PATH,
    snapshot_path: str | Path = DEFAULT_SNAPSHOT_PATH,
    policy_path: str | Path = DEFAULT_POLICY_PATH,
    registry_path: str | Path = DEFAULT_REGISTRY_PATH,
    binding_path: str | Path = DEFAULT_BINDING_PATH,
    market_data_path: str | Path = DEFAULT_MARKET_DATA_PATH,
) -> str:
    return build_dynamic_command_center_audit_report(
        audit_dynamic_command_center(
            horizon,
            plan_path,
            snapshot_path,
            policy_path,
            registry_path,
            binding_path,
            market_data_path,
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Run J.A.R.V.I.S. dynamic command-center audit.")
    parser.add_argument("horizon", nargs="?", default=DEFAULT_HORIZON)
    parser.add_argument("plan_path", nargs="?", default=DEFAULT_PLAN_PATH)
    parser.add_argument("snapshot_path", nargs="?", default=DEFAULT_SNAPSHOT_PATH)
    parser.add_argument("policy_path", nargs="?", default=DEFAULT_POLICY_PATH)
    parser.add_argument("registry_path", nargs="?", default=DEFAULT_REGISTRY_PATH)
    parser.add_argument("binding_path", nargs="?", default=DEFAULT_BINDING_PATH)
    parser.add_argument("market_data_path", nargs="?", default=DEFAULT_MARKET_DATA_PATH)
    args = parser.parse_args()

    print(
        report_dynamic_command_center_audit(
            args.horizon,
            args.plan_path,
            args.snapshot_path,
            args.policy_path,
            args.registry_path,
            args.binding_path,
            args.market_data_path,
        )
    )


if __name__ == "__main__":
    main()
