"""CLI report for reviewed candidate snapshots."""

from __future__ import annotations

from pathlib import Path

from .reviewed_candidate_snapshot import build_reviewed_candidate_snapshot_from_files


def build_reviewed_candidate_snapshot_report(
    source_registry_path: str | Path,
    reviewed_registry_path: str | Path,
    verified_evidence_intake_path: str | Path,
    freshness_policy_path: str | Path,
    snapshot_config_path: str | Path,
) -> str:
    snapshot = build_reviewed_candidate_snapshot_from_files(
        source_registry_path,
        reviewed_registry_path,
        verified_evidence_intake_path,
        freshness_policy_path,
        snapshot_config_path,
    )
    lines = [
        "J.A.R.V.I.S. Reviewed Candidate Snapshot Report",
        "Read-only snapshot. No registry mutation is performed.",
        f"snapshot status: {snapshot.snapshot_status}",
        f"target asset: {snapshot.asset_id}",
        f"name: {snapshot.name}",
        f"asset_type: {snapshot.asset_type}",
        f"previous_status: {snapshot.previous_status}",
        f"current_status: {snapshot.current_status}",
        f"status_transition: {snapshot.status_transition}",
        f"verified evidence count: {snapshot.verified_evidence_count}",
        f"freshness status: {snapshot.freshness_status}",
        f"source count: {snapshot.source_count}",
        f"private evidence present: {snapshot.private_evidence_present}",
        "evidence types verified:",
    ]
    lines.extend(f"- {item}" for item in snapshot.evidence_types_verified) if snapshot.evidence_types_verified else lines.append("- none")
    lines.append("freshness summary:")
    lines.extend(f"- {item}" for item in snapshot.freshness_summary) if snapshot.freshness_summary else lines.append("- none")
    lines.append("future gates required:")
    lines.extend(f"- {gate}" for gate in snapshot.future_gates_required)
    lines.append("registry diffs:")
    if snapshot.registry_diffs:
        lines.extend(
            f"- {diff.asset_id}.{diff.field}: {diff.before} -> {diff.after}"
            for diff in snapshot.registry_diffs
        )
    else:
        lines.append("- none")
    lines.append("warnings:")
    lines.extend(f"- {warning}" for warning in snapshot.warnings) if snapshot.warnings else lines.append("- none")
    lines.append("blockers:")
    lines.extend(f"- {blocker}" for blocker in snapshot.blockers) if snapshot.blockers else lines.append("- none")
    lines.extend(
        [
            f"not approved_investable: {str(snapshot.not_approved_investable).lower()}",
            "no allocation recommendation: true",
            "no buy/sell requests: true",
            "no trade executed: true",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Build a reviewed candidate snapshot report.")
    parser.add_argument("source_registry_path", nargs="?", default="jarvis/data/candidate_assets.v2.example.json")
    parser.add_argument("reviewed_registry_path", nargs="?", default="jarvis/data/private/candidate_assets.v2.reviewed.local.json")
    parser.add_argument("verified_evidence_intake_path", nargs="?", default="jarvis/data/private/vwce_verified_evidence_combined.local.json")
    parser.add_argument("freshness_policy_path", nargs="?", default="jarvis/data/evidence_freshness_policy.example.json")
    parser.add_argument("snapshot_config_path", nargs="?", default="jarvis/data/reviewed_candidate_snapshot.example.json")
    args = parser.parse_args()
    print(
        build_reviewed_candidate_snapshot_report(
            args.source_registry_path,
            args.reviewed_registry_path,
            args.verified_evidence_intake_path,
            args.freshness_policy_path,
            args.snapshot_config_path,
        )
    )


if __name__ == "__main__":
    main()
