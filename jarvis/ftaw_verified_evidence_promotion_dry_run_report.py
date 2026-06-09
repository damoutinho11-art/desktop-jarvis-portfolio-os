"""Readable report for FTAW verified evidence promotion dry-run."""

from __future__ import annotations

from pathlib import Path

from .ftaw_verified_evidence_promotion_dry_run import build_ftaw_verified_evidence_promotion_dry_run_from_files


def build_ftaw_verified_evidence_promotion_dry_run_report(
    source_registry_path: str | Path,
    reviewed_registry_copy_path: str | Path | None,
    url_fetch_config_path: str | Path,
    fact_intake_config_path: str | Path,
    identity_guard_config_path: str | Path,
    queue_config_path: str | Path,
    decision_config_path: str | Path,
    preview_bridge_config_path: str | Path,
    promotion_dry_run_config_path: str | Path,
) -> str:
    pack = build_ftaw_verified_evidence_promotion_dry_run_from_files(
        source_registry_path,
        reviewed_registry_copy_path,
        url_fetch_config_path,
        fact_intake_config_path,
        identity_guard_config_path,
        queue_config_path,
        decision_config_path,
        preview_bridge_config_path,
        promotion_dry_run_config_path,
    )
    lines = [
        "J.A.R.V.I.S. FTAW Verified Evidence Promotion Dry-Run Report",
        "Automated structure. Manual trust.",
        f"status: {pack.dry_run_status}",
        f"target asset: {pack.target_asset}",
        f"preview records count: {pack.preview_records_count}",
        f"planned_for_promotion count: {pack.planned_for_promotion_count}",
        f"blocked_or_excluded count: {pack.blocked_or_excluded_count}",
        "promotion dry-run is not verified evidence promotion.",
        "promotion dry-run is not asset approval.",
        "promotion dry-run is not registry mutation.",
        "promotion dry-run is not allocation advice.",
        "promotion dry-run is not a buy/sell request.",
        "promotion dry-run is not trade execution.",
        "plan items:",
    ]
    if pack.plan_records:
        for record in pack.plan_records:
            lines.append(
                f"- {record.asset_id} | evidence_type: {record.evidence_type} | "
                f"source: {record.source_name} | preview_status: {record.preview_status} | "
                f"planned_promotion_status: {record.planned_promotion_status} | reason: {record.reason}"
            )
    else:
        lines.append("- none")
    lines.append("warnings:")
    lines.extend(f"- {warning}" for warning in pack.warnings) if pack.warnings else lines.append("- none")
    lines.append("blockers:")
    lines.extend(f"- {blocker}" for blocker in pack.blockers) if pack.blockers else lines.append("- none")
    lines.extend(
        [
            "no verified evidence promotion: true",
            "no approvals created: true",
            "no registry mutation: true",
            "no allocation recommendation: true",
            "no buy/sell requests: true",
            "no trades executed: true",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Build FTAW verified evidence promotion dry-run report.")
    parser.add_argument("source_registry_path", nargs="?", default="jarvis/data/candidate_assets.v2.example.json")
    parser.add_argument("reviewed_registry_copy_path", nargs="?", default="jarvis/data/private/candidate_assets.v2.reviewed.local.json")
    parser.add_argument("url_fetch_config_path", nargs="?", default="jarvis/data/ftaw_public_url_fetch_adapter.example.json")
    parser.add_argument("fact_intake_config_path", nargs="?", default="jarvis/data/ftaw_source_fact_intake.example.json")
    parser.add_argument("identity_guard_config_path", nargs="?", default="jarvis/data/ftaw_source_identity_guard.example.json")
    parser.add_argument("queue_config_path", nargs="?", default="jarvis/data/ftaw_identity_guarded_verification_queue.example.json")
    parser.add_argument("decision_config_path", nargs="?", default="jarvis/data/ftaw_manual_verification_decision_recorder.example.json")
    parser.add_argument("preview_bridge_config_path", nargs="?", default="jarvis/data/ftaw_verified_evidence_preview_bridge.example.json")
    parser.add_argument("promotion_dry_run_config_path", nargs="?", default="jarvis/data/ftaw_verified_evidence_promotion_dry_run.example.json")
    args = parser.parse_args()
    print(
        build_ftaw_verified_evidence_promotion_dry_run_report(
            args.source_registry_path,
            args.reviewed_registry_copy_path,
            args.url_fetch_config_path,
            args.fact_intake_config_path,
            args.identity_guard_config_path,
            args.queue_config_path,
            args.decision_config_path,
            args.preview_bridge_config_path,
            args.promotion_dry_run_config_path,
        )
    )


if __name__ == "__main__":
    main()
