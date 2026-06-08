"""Readable report for the FTAW public source research pack."""

from __future__ import annotations

import json
from pathlib import Path

from .ftaw_public_source_research_pack import build_ftaw_public_source_research_pack_from_files


def build_ftaw_public_source_research_report(
    source_registry_path: str | Path,
    reviewed_registry_copy_path: str | Path | None,
    queue_config_path: str | Path,
    batch_config_path: str | Path,
    expander_config_path: str | Path,
    planner_config_path: str | Path,
    source_collection_pack_config_path: str | Path,
    public_research_config_path: str | Path,
) -> str:
    pack = build_ftaw_public_source_research_pack_from_files(
        source_registry_path,
        reviewed_registry_copy_path,
        queue_config_path,
        batch_config_path,
        expander_config_path,
        planner_config_path,
        source_collection_pack_config_path,
        public_research_config_path,
    )
    sample = pack.draft_evidence_records[0] if pack.draft_evidence_records else {}
    lines = [
        "J.A.R.V.I.S. FTAW Public Source Research Pack Report",
        "Read-only draft evidence preparation. Manual verification is required before any evidence can be trusted.",
        f"FTAW public research pack status: {pack.pack_status}",
        f"target asset: {pack.target_asset_id}",
        f"public research tasks count: {pack.public_research_tasks_count}",
        f"draft evidence records count: {len(pack.draft_evidence_records)}",
        "skipped manual evidence types:",
    ]
    lines.extend(f"- {item}" for item in pack.skipped_manual_evidence_types) if pack.skipped_manual_evidence_types else lines.append("- none")
    lines.append("draft records by evidence type:")
    lines.extend(
        f"- {evidence_type}: {count}" for evidence_type, count in pack.draft_records_by_evidence_type.items()
    ) if pack.draft_records_by_evidence_type else lines.append("- none")
    lines.extend(
        [
            "sample draft evidence record:",
            json.dumps(sample, indent=2, sort_keys=True),
            "warnings:",
        ]
    )
    lines.extend(f"- {warning}" for warning in pack.warnings) if pack.warnings else lines.append("- none")
    lines.append("blockers:")
    lines.extend(f"- {blocker}" for blocker in pack.blockers) if pack.blockers else lines.append("- none")
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

    parser = argparse.ArgumentParser(description="Build focused FTAW public source research pack report.")
    parser.add_argument("source_registry_path", nargs="?", default="jarvis/data/candidate_assets.v2.example.json")
    parser.add_argument("reviewed_registry_copy_path", nargs="?", default="jarvis/data/private/candidate_assets.v2.reviewed.local.json")
    parser.add_argument("queue_config_path", nargs="?", default="jarvis/data/multi_candidate_review_queue.example.json")
    parser.add_argument("batch_config_path", nargs="?", default="jarvis/data/global_core_evidence_batch.example.json")
    parser.add_argument("expander_config_path", nargs="?", default="jarvis/data/global_core_source_template_expander.example.json")
    parser.add_argument("planner_config_path", nargs="?", default="jarvis/data/global_core_source_collection_planner.example.json")
    parser.add_argument("source_collection_pack_config_path", nargs="?", default="jarvis/data/ftaw_source_collection_pack.example.json")
    parser.add_argument("public_research_config_path", nargs="?", default="jarvis/data/ftaw_public_source_research_pack.example.json")
    args = parser.parse_args()
    print(
        build_ftaw_public_source_research_report(
            args.source_registry_path,
            args.reviewed_registry_copy_path,
            args.queue_config_path,
            args.batch_config_path,
            args.expander_config_path,
            args.planner_config_path,
            args.source_collection_pack_config_path,
            args.public_research_config_path,
        )
    )


if __name__ == "__main__":
    main()
