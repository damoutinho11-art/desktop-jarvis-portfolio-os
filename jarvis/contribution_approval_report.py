"""Readable contribution approval bridge report."""

from __future__ import annotations

from pathlib import Path

from .contribution_approval_bridge import load_plan_and_bridge


def build_contribution_approval_report(
    plan_path: str | Path,
    snapshot_path: str | Path,
    policy_path: str | Path,
    registry_path: str | Path,
) -> str:
    result = load_plan_and_bridge(plan_path, snapshot_path, policy_path, registry_path)
    lines = [
        "J.A.R.V.I.S. Contribution Approval Bridge Report",
        "Read-only bridge. No execution performed.",
        f"bridge status: {result.status}",
        f"generated approval requests: {len(result.approval_requests)}",
        f"manual approval required: {result.manual_approval_required}",
        f"execution forbidden: {result.execution_forbidden}",
        "blocked lines:",
    ]
    if result.blocked_lines:
        for blocked in result.blocked_lines:
            lines.append(f"- {blocked.plan_line.asset_id}: {', '.join(blocked.blockers)}")
    else:
        lines.append("- none")
    lines.append("warnings:")
    lines.extend(f"- {warning}" for warning in result.warnings) if result.warnings else lines.append("- none")
    lines.append("blockers:")
    lines.extend(f"- {blocker}" for blocker in result.blockers) if result.blockers else lines.append("- none")
    lines.append("No files written.")
    lines.append("No trades executed.")
    return "\n".join(lines)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Bridge draft contribution plans into manual approval request previews.")
    parser.add_argument("plan_path", nargs="?", default="jarvis/data/contribution_plan.example.json")
    parser.add_argument("snapshot_path", nargs="?", default="jarvis/data/manual_snapshot.example.json")
    parser.add_argument("policy_path", nargs="?", default="jarvis/data/portfolio_policy.example.json")
    parser.add_argument("registry_path", nargs="?", default="jarvis/data/candidate_assets.example.json")
    args = parser.parse_args()
    print(build_contribution_approval_report(args.plan_path, args.snapshot_path, args.policy_path, args.registry_path))


if __name__ == "__main__":
    main()
