"""Readable report for private status review to registry dry-run bridge."""

from __future__ import annotations

from pathlib import Path

from .private_registry_dry_run_bridge import build_private_registry_dry_run_bridge_from_files


def build_private_registry_dry_run_report(
    registry_path: str | Path,
    intake_path: str | Path,
    freshness_policy_path: str | Path,
    private_status_config_path: str | Path,
    private_registry_dry_run_config_path: str | Path,
) -> str:
    result = build_private_registry_dry_run_bridge_from_files(
        registry_path,
        intake_path,
        freshness_policy_path,
        private_status_config_path,
        private_registry_dry_run_config_path,
    )
    dry_run = result.dry_run
    lines = [
        "J.A.R.V.I.S. Private Registry Dry-Run Bridge Report",
        "Read-only registry update simulation. No registry file is modified by default.",
        f"private registry dry-run bridge status: {result.bridge_status}",
        f"request previews count: {dry_run.total_request_previews}",
        f"simulated updates count: {len(dry_run.simulated_changes)}",
        f"blocked requests count: {len(dry_run.blocked_changes)}",
        "requested transitions:",
    ]
    changes = (*dry_run.simulated_changes, *dry_run.blocked_changes)
    if changes:
        for change in changes:
            lines.append(
                f"- {change.asset_id}: {change.current_status} -> {change.requested_status}; would_update={change.would_update}"
            )
    else:
        lines.append("- none")
    lines.append("diff summary:")
    if dry_run.simulated_changes:
        for change in dry_run.simulated_changes:
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

    parser = argparse.ArgumentParser(description="Dry-run registry changes from private status review previews.")
    parser.add_argument("registry_path", nargs="?", default="jarvis/data/candidate_assets.v2.example.json")
    parser.add_argument("intake_path", nargs="?", default="jarvis/data/private/vwce_verified_evidence_combined.local.json")
    parser.add_argument("freshness_policy_path", nargs="?", default="jarvis/data/evidence_freshness_policy.example.json")
    parser.add_argument("private_status_config_path", nargs="?", default="jarvis/data/private_status_review_bridge.example.json")
    parser.add_argument("private_registry_dry_run_config_path", nargs="?", default="jarvis/data/private_registry_dry_run_bridge.example.json")
    args = parser.parse_args()
    print(
        build_private_registry_dry_run_report(
            args.registry_path,
            args.intake_path,
            args.freshness_policy_path,
            args.private_status_config_path,
            args.private_registry_dry_run_config_path,
        )
    )


if __name__ == "__main__":
    main()
