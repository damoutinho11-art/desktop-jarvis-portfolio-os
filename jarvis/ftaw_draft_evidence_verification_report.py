"""Readable report for the FTAW draft evidence verification queue."""

from __future__ import annotations

from pathlib import Path

from .ftaw_draft_evidence_verification_queue import build_ftaw_draft_evidence_verification_queue_from_files


def build_ftaw_draft_evidence_verification_report(
    source_registry_path: str | Path,
    reviewed_registry_copy_path: str | Path | None,
    queue_config_path: str | Path,
    batch_config_path: str | Path,
    expander_config_path: str | Path,
    planner_config_path: str | Path,
    source_collection_pack_config_path: str | Path,
    public_research_config_path: str | Path,
    verification_config_path: str | Path,
) -> str:
    queue = build_ftaw_draft_evidence_verification_queue_from_files(
        source_registry_path,
        reviewed_registry_copy_path,
        queue_config_path,
        batch_config_path,
        expander_config_path,
        planner_config_path,
        source_collection_pack_config_path,
        public_research_config_path,
        verification_config_path,
    )
    lines = [
        "J.A.R.V.I.S. FTAW Draft Evidence Verification Queue Report",
        "Read-only manual review queue. No evidence is verified by default.",
        f"FTAW verification queue status: {queue.queue_status}",
        f"target asset: {queue.target_asset_id}",
        f"draft records count: {queue.draft_records_count}",
        f"pending verification tasks count: {len(queue.verification_tasks)}",
        "recommended decisions by evidence type:",
    ]
    lines.extend(
        f"- {evidence_type}: {decision}"
        for evidence_type, decision in queue.recommended_decisions_by_evidence_type.items()
    ) if queue.recommended_decisions_by_evidence_type else lines.append("- none")
    lines.extend(
        [
            f"accepted preview count: {queue.accepted_preview_count}",
            "warnings:",
        ]
    )
    lines.extend(f"- {warning}" for warning in queue.warnings) if queue.warnings else lines.append("- none")
    lines.append("blockers:")
    lines.extend(f"- {blocker}" for blocker in queue.blockers) if queue.blockers else lines.append("- none")
    lines.extend(
        [
            "manual verification required: true",
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

    parser = argparse.ArgumentParser(description="Build FTAW draft evidence verification queue report.")
    parser.add_argument("source_registry_path", nargs="?", default="jarvis/data/candidate_assets.v2.example.json")
    parser.add_argument("reviewed_registry_copy_path", nargs="?", default="jarvis/data/private/candidate_assets.v2.reviewed.local.json")
    parser.add_argument("queue_config_path", nargs="?", default="jarvis/data/multi_candidate_review_queue.example.json")
    parser.add_argument("batch_config_path", nargs="?", default="jarvis/data/global_core_evidence_batch.example.json")
    parser.add_argument("expander_config_path", nargs="?", default="jarvis/data/global_core_source_template_expander.example.json")
    parser.add_argument("planner_config_path", nargs="?", default="jarvis/data/global_core_source_collection_planner.example.json")
    parser.add_argument("source_collection_pack_config_path", nargs="?", default="jarvis/data/ftaw_source_collection_pack.example.json")
    parser.add_argument("public_research_config_path", nargs="?", default="jarvis/data/ftaw_public_source_research_pack.example.json")
    parser.add_argument("verification_config_path", nargs="?", default="jarvis/data/ftaw_draft_evidence_verification_queue.example.json")
    args = parser.parse_args()
    print(
        build_ftaw_draft_evidence_verification_report(
            args.source_registry_path,
            args.reviewed_registry_copy_path,
            args.queue_config_path,
            args.batch_config_path,
            args.expander_config_path,
            args.planner_config_path,
            args.source_collection_pack_config_path,
            args.public_research_config_path,
            args.verification_config_path,
        )
    )


if __name__ == "__main__":
    main()
