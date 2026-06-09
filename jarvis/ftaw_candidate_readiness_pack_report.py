"""Readable report for FTAW candidate readiness pack."""

from __future__ import annotations

from pathlib import Path

from .ftaw_candidate_readiness_pack import build_ftaw_candidate_readiness_pack


def build_ftaw_candidate_readiness_pack_report(
    source_registry_path: str | Path,
    reviewed_registry_copy_path: str | Path | None,
    url_fetch_config_path: str | Path,
    fact_intake_config_path: str | Path,
    identity_guard_config_path: str | Path,
    queue_config_path: str | Path,
    decision_config_path: str | Path,
    preview_bridge_config_path: str | Path,
    promotion_dry_run_config_path: str | Path,
    readiness_config_path: str | Path,
) -> str:
    pack = build_ftaw_candidate_readiness_pack(
        source_registry_path,
        reviewed_registry_copy_path,
        url_fetch_config_path,
        fact_intake_config_path,
        identity_guard_config_path,
        queue_config_path,
        decision_config_path,
        preview_bridge_config_path,
        promotion_dry_run_config_path,
        readiness_config_path,
    )
    lines = [
        "J.A.R.V.I.S. FTAW Candidate Readiness Pack Report",
        "Automated structure. Manual trust.",
        f"target asset: {pack.target_asset}",
        f"candidate readiness status: {pack.candidate_readiness_status}",
        f"source fact status: {pack.source_fact_status}",
        f"identity guard status: {pack.identity_guard_status}",
        f"verification queue status: {pack.verification_queue_status}",
        f"manual decision status: {pack.manual_decision_status}",
        f"preview bridge status: {pack.preview_bridge_status}",
        f"promotion dry-run status: {pack.promotion_dry_run_status}",
        f"required evidence types count: {pack.required_evidence_types_count}",
        f"planned promotion evidence types count: {pack.planned_promotion_evidence_types_count}",
        f"missing evidence types count: {pack.missing_evidence_types_count}",
        "planned promotion evidence types:",
    ]
    lines.extend(f"- {item}" for item in pack.planned_promotion_evidence_types) if pack.planned_promotion_evidence_types else lines.append("- none")
    lines.append("missing evidence types:")
    lines.extend(f"- {item}" for item in pack.missing_evidence_types) if pack.missing_evidence_types else lines.append("- none")
    lines.append("blocked reasons:")
    lines.extend(f"- {item}" for item in pack.blocked_reasons) if pack.blocked_reasons else lines.append("- none")
    lines.extend(
        [
            f"next manual action: {pack.next_manual_action}",
            f"ready for manual approval review: {str(pack.ready_for_manual_approval_review).lower()}",
            "candidate readiness is not asset approval.",
            "candidate readiness is not verified evidence promotion.",
            "candidate readiness is not registry mutation.",
            "candidate readiness is not allocation advice.",
            "candidate readiness is not a buy/sell request.",
            "candidate readiness is not trade execution.",
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

    parser = argparse.ArgumentParser(description="Build FTAW candidate readiness pack report.")
    parser.add_argument("source_registry_path", nargs="?", default="jarvis/data/candidate_assets.v2.example.json")
    parser.add_argument("reviewed_registry_copy_path", nargs="?", default="jarvis/data/private/candidate_assets.v2.reviewed.local.json")
    parser.add_argument("url_fetch_config_path", nargs="?", default="jarvis/data/ftaw_public_url_fetch_adapter.example.json")
    parser.add_argument("fact_intake_config_path", nargs="?", default="jarvis/data/ftaw_source_fact_intake.example.json")
    parser.add_argument("identity_guard_config_path", nargs="?", default="jarvis/data/ftaw_source_identity_guard.example.json")
    parser.add_argument("queue_config_path", nargs="?", default="jarvis/data/ftaw_identity_guarded_verification_queue.example.json")
    parser.add_argument("decision_config_path", nargs="?", default="jarvis/data/ftaw_manual_verification_decision_recorder.example.json")
    parser.add_argument("preview_bridge_config_path", nargs="?", default="jarvis/data/ftaw_verified_evidence_preview_bridge.example.json")
    parser.add_argument("promotion_dry_run_config_path", nargs="?", default="jarvis/data/ftaw_verified_evidence_promotion_dry_run.example.json")
    parser.add_argument("readiness_config_path", nargs="?", default="jarvis/data/ftaw_candidate_readiness_pack.example.json")
    args = parser.parse_args()
    print(
        build_ftaw_candidate_readiness_pack_report(
            args.source_registry_path,
            args.reviewed_registry_copy_path,
            args.url_fetch_config_path,
            args.fact_intake_config_path,
            args.identity_guard_config_path,
            args.queue_config_path,
            args.decision_config_path,
            args.preview_bridge_config_path,
            args.promotion_dry_run_config_path,
            args.readiness_config_path,
        )
    )


if __name__ == "__main__":
    main()
