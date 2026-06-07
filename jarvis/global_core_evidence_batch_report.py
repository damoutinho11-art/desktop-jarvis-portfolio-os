"""Readable report for the global core evidence collection batch."""

from __future__ import annotations

from pathlib import Path

from .global_core_evidence_batch import SOURCE_GUIDANCE, build_global_core_evidence_batch_from_files


def build_global_core_evidence_batch_report(
    source_registry_path: str | Path,
    reviewed_registry_copy_path: str | Path | None,
    queue_config_path: str | Path,
    batch_config_path: str | Path,
) -> str:
    batch = build_global_core_evidence_batch_from_files(
        source_registry_path,
        reviewed_registry_copy_path,
        queue_config_path,
        batch_config_path,
    )
    lines = [
        "J.A.R.V.I.S. Global Core Evidence Collection Batch Report",
        "Read-only evidence preparation. No evidence is auto-verified.",
        f"batch status: {batch.batch_status}",
        f"target candidates count: {len(batch.target_candidates)}",
        "target candidates:",
    ]
    lines.extend(f"- {asset_id}" for asset_id in batch.target_candidates) if batch.target_candidates else lines.append("- none")
    lines.append(f"total evidence tasks: {len(batch.tasks)}")
    lines.append("tasks by evidence type:")
    lines.extend(
        f"- {evidence_type}: {count}" for evidence_type, count in batch.tasks_by_evidence_type.items()
    ) if batch.tasks_by_evidence_type else lines.append("- none")
    lines.append("top source guidance:")
    lines.extend(f"- {evidence_type}: {guidance}" for evidence_type, guidance in SOURCE_GUIDANCE.items())
    lines.append("already reviewed skipped:")
    lines.extend(f"- {asset_id}" for asset_id in batch.already_reviewed_skipped) if batch.already_reviewed_skipped else lines.append("- none")
    lines.append("source config templates:")
    lines.extend(
        f"- {template['source_id']}: enabled={template['enabled']}; allow_network_fetch={template['allow_network_fetch']}"
        for template in batch.source_config_templates[:10]
    ) if batch.source_config_templates else lines.append("- none")
    if len(batch.source_config_templates) > 10:
        lines.append(f"- ... {len(batch.source_config_templates) - 10} more templates")
    lines.append("warnings:")
    lines.extend(f"- {warning}" for warning in batch.warnings) if batch.warnings else lines.append("- none")
    lines.append("blockers:")
    lines.extend(f"- {blocker}" for blocker in batch.blockers) if batch.blockers else lines.append("- none")
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

    parser = argparse.ArgumentParser(description="Build a global core ETF evidence collection batch report.")
    parser.add_argument("source_registry_path", nargs="?", default="jarvis/data/candidate_assets.v2.example.json")
    parser.add_argument("reviewed_registry_copy_path", nargs="?", default="jarvis/data/private/candidate_assets.v2.reviewed.local.json")
    parser.add_argument("queue_config_path", nargs="?", default="jarvis/data/multi_candidate_review_queue.example.json")
    parser.add_argument("batch_config_path", nargs="?", default="jarvis/data/global_core_evidence_batch.example.json")
    args = parser.parse_args()
    print(
        build_global_core_evidence_batch_report(
            args.source_registry_path,
            args.reviewed_registry_copy_path,
            args.queue_config_path,
            args.batch_config_path,
        )
    )


if __name__ == "__main__":
    main()
