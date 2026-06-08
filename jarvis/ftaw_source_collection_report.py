"""Readable report for the focused FTAW source collection pack."""

from __future__ import annotations

import json
from pathlib import Path

from .ftaw_source_collection_pack import build_ftaw_source_collection_pack_from_files


def build_ftaw_source_collection_report(
    source_registry_path: str | Path,
    reviewed_registry_copy_path: str | Path | None,
    queue_config_path: str | Path,
    batch_config_path: str | Path,
    expander_config_path: str | Path,
    planner_config_path: str | Path,
    pack_config_path: str | Path,
) -> str:
    pack = build_ftaw_source_collection_pack_from_files(
        source_registry_path,
        reviewed_registry_copy_path,
        queue_config_path,
        batch_config_path,
        expander_config_path,
        planner_config_path,
        pack_config_path,
    )
    sample_template = pack.collection_items[0].ready_to_fill_intake_template if pack.collection_items else {}
    lines = [
        "J.A.R.V.I.S. FTAW Source Collection Pack Report",
        "Read-only focused collection pack. Templates are placeholders until manually verified.",
        f"FTAW collection pack status: {pack.pack_status}",
        f"target asset: {pack.target_asset_id}",
        f"total collection items: {len(pack.collection_items)}",
        "collection items by evidence type:",
    ]
    lines.extend(
        f"- {evidence_type}: {count}" for evidence_type, count in pack.items_by_evidence_type.items()
    ) if pack.items_by_evidence_type else lines.append("- none")
    lines.extend(
        [
            f"public research tasks count: {pack.public_research_tasks_count}",
            f"account-specific manual tasks count: {pack.account_specific_manual_tasks_count}",
            f"manual tax review tasks count: {pack.manual_tax_review_tasks_count}",
            "sample intake template:",
            json.dumps(sample_template, indent=2, sort_keys=True),
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

    parser = argparse.ArgumentParser(description="Build focused FTAW source collection pack report.")
    parser.add_argument("source_registry_path", nargs="?", default="jarvis/data/candidate_assets.v2.example.json")
    parser.add_argument("reviewed_registry_copy_path", nargs="?", default="jarvis/data/private/candidate_assets.v2.reviewed.local.json")
    parser.add_argument("queue_config_path", nargs="?", default="jarvis/data/multi_candidate_review_queue.example.json")
    parser.add_argument("batch_config_path", nargs="?", default="jarvis/data/global_core_evidence_batch.example.json")
    parser.add_argument("expander_config_path", nargs="?", default="jarvis/data/global_core_source_template_expander.example.json")
    parser.add_argument("planner_config_path", nargs="?", default="jarvis/data/global_core_source_collection_planner.example.json")
    parser.add_argument("pack_config_path", nargs="?", default="jarvis/data/ftaw_source_collection_pack.example.json")
    args = parser.parse_args()
    print(
        build_ftaw_source_collection_report(
            args.source_registry_path,
            args.reviewed_registry_copy_path,
            args.queue_config_path,
            args.batch_config_path,
            args.expander_config_path,
            args.planner_config_path,
            args.pack_config_path,
        )
    )


if __name__ == "__main__":
    main()
