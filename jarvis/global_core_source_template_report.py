"""Readable report for global core source template expansion."""

from __future__ import annotations

from pathlib import Path

from .global_core_source_template_expander import build_global_core_source_template_expansion_from_files


def build_global_core_source_template_report(
    source_registry_path: str | Path,
    reviewed_registry_copy_path: str | Path | None,
    queue_config_path: str | Path,
    batch_config_path: str | Path,
    expander_config_path: str | Path,
) -> str:
    expansion = build_global_core_source_template_expansion_from_files(
        source_registry_path,
        reviewed_registry_copy_path,
        queue_config_path,
        batch_config_path,
        expander_config_path,
    )
    lines = [
        "J.A.R.V.I.S. Global Core Public Source Template Expansion Report",
        "Read-only source map. Templates are disabled and require manual verification.",
        f"template expansion status: {expansion.expansion_status}",
        f"target candidates count: {len(expansion.target_candidates)}",
        f"generated templates count: {len(expansion.templates)}",
        "templates by candidate:",
    ]
    lines.extend(
        f"- {asset_id}: {count}" for asset_id, count in expansion.templates_by_candidate.items()
    ) if expansion.templates_by_candidate else lines.append("- none")
    lines.append("templates by evidence type:")
    lines.extend(
        f"- {evidence_type}: {count}" for evidence_type, count in expansion.templates_by_evidence_type.items()
    ) if expansion.templates_by_evidence_type else lines.append("- none")
    lines.extend(
        [
            f"disabled templates count: {expansion.disabled_templates_count}",
            f"network fetch enabled count: {expansion.network_fetch_enabled_count}",
            "already reviewed skipped:",
        ]
    )
    lines.extend(f"- {asset_id}" for asset_id in expansion.already_reviewed_skipped) if expansion.already_reviewed_skipped else lines.append("- none")
    lines.append("sample templates:")
    for template in expansion.templates[:8]:
        lines.append(
            f"- {template.source_id}: {template.asset_id} {template.evidence_type}; "
            f"source_type={template.source_type}; enabled={template.enabled}; "
            f"allow_network_fetch={template.allow_network_fetch}; url={template.url_reference}"
        )
    if len(expansion.templates) > 8:
        lines.append(f"- ... {len(expansion.templates) - 8} more templates")
    lines.append("warnings:")
    lines.extend(f"- {warning}" for warning in expansion.warnings) if expansion.warnings else lines.append("- none")
    lines.append("blockers:")
    lines.extend(f"- {blocker}" for blocker in expansion.blockers) if expansion.blockers else lines.append("- none")
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

    parser = argparse.ArgumentParser(description="Build global core source template expansion report.")
    parser.add_argument("source_registry_path", nargs="?", default="jarvis/data/candidate_assets.v2.example.json")
    parser.add_argument("reviewed_registry_copy_path", nargs="?", default="jarvis/data/private/candidate_assets.v2.reviewed.local.json")
    parser.add_argument("queue_config_path", nargs="?", default="jarvis/data/multi_candidate_review_queue.example.json")
    parser.add_argument("batch_config_path", nargs="?", default="jarvis/data/global_core_evidence_batch.example.json")
    parser.add_argument("expander_config_path", nargs="?", default="jarvis/data/global_core_source_template_expander.example.json")
    args = parser.parse_args()
    print(
        build_global_core_source_template_report(
            args.source_registry_path,
            args.reviewed_registry_copy_path,
            args.queue_config_path,
            args.batch_config_path,
            args.expander_config_path,
        )
    )


if __name__ == "__main__":
    main()
