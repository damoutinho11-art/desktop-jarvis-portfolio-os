"""Readable contribution plan report."""

from __future__ import annotations

from pathlib import Path

from .contribution_planner import load_and_plan_contribution


def _money(value: float) -> str:
    return f"EUR {value:.2f}"


def build_contribution_plan_report(
    plan_path: str | Path,
    snapshot_path: str | Path,
    policy_path: str | Path,
    registry_path: str | Path,
) -> str:
    result = load_and_plan_contribution(plan_path, snapshot_path, policy_path, registry_path)
    lines = [
        "J.A.R.V.I.S. Contribution Plan Report",
        "Draft-only contribution diagnostics. No recommendations generated.",
        f"status: {result.status}",
        f"contribution amount: {_money(result.contribution_amount_eur)}",
        f"creates_buy_request: {result.creates_buy_request}",
        "plan lines:",
    ]
    if result.plan_lines:
        for line in result.plan_lines:
            lines.append(
                f"- {line.sleeve_id} / {line.asset_id} / {line.platform}: {_money(line.amount_eur)}; {line.reason}"
            )
    else:
        lines.append("- none")
    lines.append("blockers:")
    lines.extend(f"- {blocker}" for blocker in result.blockers) if result.blockers else lines.append("- none")
    lines.append("warnings:")
    lines.extend(f"- {warning}" for warning in result.warnings) if result.warnings else lines.append("- none")
    lines.append(f"manual_approval_required: {result.manual_approval_required}")
    lines.append("No buy/sell requests created.")
    lines.append("No trades executed.")
    return "\n".join(lines)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Draft read-only contribution plan diagnostics.")
    parser.add_argument("plan_path", nargs="?", default="jarvis/data/contribution_plan.example.json")
    parser.add_argument("snapshot_path", nargs="?", default="jarvis/data/manual_snapshot.example.json")
    parser.add_argument("policy_path", nargs="?", default="jarvis/data/portfolio_policy.example.json")
    parser.add_argument("registry_path", nargs="?", default="jarvis/data/candidate_assets.example.json")
    args = parser.parse_args()
    print(build_contribution_plan_report(args.plan_path, args.snapshot_path, args.policy_path, args.registry_path))


if __name__ == "__main__":
    main()
