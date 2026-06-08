"""Readable report for FTAW public source auto-draft collection."""

from __future__ import annotations

from pathlib import Path

from .ftaw_public_source_auto_draft import build_ftaw_public_source_auto_draft_pack_from_files


def build_ftaw_public_source_auto_draft_report(
    source_registry_path: str | Path,
    reviewed_registry_copy_path: str | Path | None,
    public_research_config_path: str | Path,
    verification_config_path: str | Path,
    auto_draft_config_path: str | Path,
) -> str:
    pack = build_ftaw_public_source_auto_draft_pack_from_files(
        source_registry_path,
        reviewed_registry_copy_path,
        public_research_config_path,
        verification_config_path,
        auto_draft_config_path,
    )
    lines = [
        "J.A.R.V.I.S. FTAW Public Source Auto-Draft Report",
        "Automated research. Manual trust.",
        f"FTAW public source auto-draft status: {pack.auto_draft_status}",
        f"processed source count: {pack.processed_source_count}",
        f"skipped source count: {pack.skipped_source_count}",
        f"blocked source count: {pack.blocked_source_count}",
        f"draft evidence records count: {len(pack.draft_evidence_records)}",
        "draft records by evidence type:",
    ]
    lines.extend(
        f"- {evidence_type}: {count}" for evidence_type, count in pack.draft_records_by_evidence_type.items()
    ) if pack.draft_records_by_evidence_type else lines.append("- none")
    lines.extend(
        [
            f"draft-ready count: {pack.draft_ready_count}",
            f"needs-correction count: {pack.needs_correction_count}",
            "manual evidence skipped:",
        ]
    )
    lines.extend(f"- {evidence_type}" for evidence_type in pack.manual_evidence_skipped) if pack.manual_evidence_skipped else lines.append("- none")
    lines.extend(
        [
            f"network fetch enabled count: {pack.network_fetch_enabled_count}",
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

    parser = argparse.ArgumentParser(description="Build FTAW public source auto-draft report.")
    parser.add_argument("source_registry_path", nargs="?", default="jarvis/data/candidate_assets.v2.example.json")
    parser.add_argument("reviewed_registry_copy_path", nargs="?", default="jarvis/data/private/candidate_assets.v2.reviewed.local.json")
    parser.add_argument("public_research_config_path", nargs="?", default="jarvis/data/ftaw_public_source_research_pack.example.json")
    parser.add_argument("verification_config_path", nargs="?", default="jarvis/data/ftaw_draft_evidence_verification_queue.example.json")
    parser.add_argument("auto_draft_config_path", nargs="?", default="jarvis/data/ftaw_public_source_auto_draft.example.json")
    args = parser.parse_args()
    print(
        build_ftaw_public_source_auto_draft_report(
            args.source_registry_path,
            args.reviewed_registry_copy_path,
            args.public_research_config_path,
            args.verification_config_path,
            args.auto_draft_config_path,
        )
    )


if __name__ == "__main__":
    main()
