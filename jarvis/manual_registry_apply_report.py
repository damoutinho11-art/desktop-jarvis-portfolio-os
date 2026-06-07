"""Readable report for manual registry apply approval packs."""

from __future__ import annotations

from pathlib import Path

from .manual_registry_apply_pack import build_manual_registry_apply_pack_from_files


def build_manual_registry_apply_report(
    registry_path: str | Path,
    intake_path: str | Path,
    freshness_policy_path: str | Path,
    private_status_config_path: str | Path,
    private_registry_dry_run_config_path: str | Path,
    manual_apply_config_path: str | Path,
) -> str:
    pack = build_manual_registry_apply_pack_from_files(
        registry_path,
        intake_path,
        freshness_policy_path,
        private_status_config_path,
        private_registry_dry_run_config_path,
        manual_apply_config_path,
    )
    lines = [
        "J.A.R.V.I.S. Manual Registry Apply Approval Pack Report",
        "Read-only approval pack. No registry file is written by default.",
        "manual registry apply pack status: " + ("APPLY_ALLOWED" if pack.apply_allowed else "BLOCKED"),
        f"target asset: {pack.target_asset_id}",
        f"current_status: {pack.current_status}",
        f"requested_status: {pack.requested_status}",
        f"apply_allowed: {pack.apply_allowed}",
        f"output_path: {pack.output_path}",
        "required confirmations:",
    ]
    lines.extend(f"- {confirmation}" for confirmation in pack.required_confirmations)
    lines.append("diff summary:")
    lines.extend(f"- {diff}" for diff in pack.diff_summary) if pack.diff_summary else lines.append("- none")
    lines.append("warnings:")
    lines.extend(f"- {warning}" for warning in pack.warnings) if pack.warnings else lines.append("- none")
    lines.append("blockers:")
    lines.extend(f"- {blocker}" for blocker in pack.blockers) if pack.blockers else lines.append("- none")
    lines.extend(
        [
            "default write performed: false",
            "no approved_investable: true",
            "no buy/sell requests: true",
            "no trades executed: true",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Build a manual approval pack for writing a registry copy.")
    parser.add_argument("registry_path", nargs="?", default="jarvis/data/candidate_assets.v2.example.json")
    parser.add_argument("intake_path", nargs="?", default="jarvis/data/private/vwce_verified_evidence_combined.local.json")
    parser.add_argument("freshness_policy_path", nargs="?", default="jarvis/data/evidence_freshness_policy.example.json")
    parser.add_argument("private_status_config_path", nargs="?", default="jarvis/data/private_status_review_bridge.example.json")
    parser.add_argument("private_registry_dry_run_config_path", nargs="?", default="jarvis/data/private_registry_dry_run_bridge.example.json")
    parser.add_argument("manual_apply_config_path", nargs="?", default="jarvis/data/manual_registry_apply_pack.example.json")
    args = parser.parse_args()
    print(
        build_manual_registry_apply_report(
            args.registry_path,
            args.intake_path,
            args.freshness_policy_path,
            args.private_status_config_path,
            args.private_registry_dry_run_config_path,
            args.manual_apply_config_path,
        )
    )


if __name__ == "__main__":
    main()
