"""Readable report for manual registry update dry-runs."""

from __future__ import annotations

from pathlib import Path

from .registry_update_dry_run import simulate_registry_update_from_files


def build_registry_update_dry_run_report(
    registry_path: str | Path,
    bridge_config_path: str | Path,
) -> str:
    result = simulate_registry_update_from_files(registry_path, bridge_config_path)
    lines = [
        "J.A.R.V.I.S. Registry Update Dry-Run Report",
        "Read-only simulator. No registry file is modified by default.",
        f"dry-run status: {result.dry_run_status}",
        f"total request previews: {result.total_request_previews}",
        f"simulated updates count: {len(result.simulated_changes)}",
        f"blocked requests count: {len(result.blocked_changes)}",
        "requested transitions:",
    ]
    changes = (*result.simulated_changes, *result.blocked_changes)
    if changes:
        for change in changes:
            lines.append(
                f"- {change.asset_id}: {change.current_status} -> {change.requested_status}; "
                f"would_update={change.would_update}"
            )
    else:
        lines.append("- none")

    lines.append("diff summary:")
    if result.simulated_changes:
        for change in result.simulated_changes:
            for diff in change.diff_summary:
                lines.append(f"- {change.asset_id}: {diff}")
    else:
        lines.append("- none")

    lines.append("warnings:")
    lines.extend(f"- {warning}" for warning in result.warnings) if result.warnings else lines.append("- none")
    lines.append("blockers:")
    lines.extend(f"- {blocker}" for blocker in result.blockers) if result.blockers else lines.append("- none")
    lines.extend(
        [
            f"registry mutation performed: {str(result.registry_mutation_performed).lower()}",
            "No approvals executed.",
            "No buy/sell requests created.",
            "No trades executed.",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Dry-run manual registry updates from status request previews.")
    parser.add_argument("registry_path", nargs="?", default="jarvis/data/candidate_assets.v2.example.json")
    parser.add_argument("bridge_config_path", nargs="?", default="jarvis/data/real_status_review_bridge.example.json")
    args = parser.parse_args()
    print(build_registry_update_dry_run_report(args.registry_path, args.bridge_config_path))


if __name__ == "__main__":
    main()
