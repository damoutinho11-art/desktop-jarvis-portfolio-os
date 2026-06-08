"""Readable report for the FTAW public URL fetch adapter."""

from __future__ import annotations

from pathlib import Path

from .ftaw_public_url_fetch_adapter import build_ftaw_public_url_fetch_pack_from_files


def build_ftaw_public_url_fetch_report(
    source_registry_path: str | Path,
    reviewed_registry_copy_path: str | Path | None,
    auto_draft_config_path: str | Path,
    fetch_config_path: str | Path,
) -> str:
    pack = build_ftaw_public_url_fetch_pack_from_files(
        source_registry_path,
        reviewed_registry_copy_path,
        auto_draft_config_path,
        fetch_config_path,
    )
    lines = [
        "J.A.R.V.I.S. FTAW Public URL Fetch Draft Adapter Report",
        "Automated research. Manual trust.",
        f"FTAW public URL fetch status: {pack.fetch_status}",
        f"global network fetch enabled: {str(pack.global_network_fetch_enabled).lower()}",
        f"processed source count: {pack.processed_source_count}",
        f"local fixture count: {pack.local_fixture_count}",
        f"network fetch attempted count: {pack.network_fetch_attempted_count}",
        f"network fetch blocked count: {pack.network_fetch_blocked_count}",
        f"skipped source count: {pack.skipped_source_count}",
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
            "blocked sources:",
        ]
    )
    lines.extend(f"- {source_id}" for source_id in pack.blocked_sources) if pack.blocked_sources else lines.append("- none")
    lines.append("warnings:")
    lines.extend(f"- {warning}" for warning in pack.warnings) if pack.warnings else lines.append("- none")
    lines.append("manual evidence skipped:")
    lines.extend(f"- {evidence_type}" for evidence_type in pack.manual_evidence_skipped) if pack.manual_evidence_skipped else lines.append("- none")
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

    parser = argparse.ArgumentParser(description="Build FTAW public URL fetch adapter report.")
    parser.add_argument("source_registry_path", nargs="?", default="jarvis/data/candidate_assets.v2.example.json")
    parser.add_argument("reviewed_registry_copy_path", nargs="?", default="jarvis/data/private/candidate_assets.v2.reviewed.local.json")
    parser.add_argument("auto_draft_config_path", nargs="?", default="jarvis/data/ftaw_public_source_auto_draft.example.json")
    parser.add_argument("fetch_config_path", nargs="?", default="jarvis/data/ftaw_public_url_fetch_adapter.example.json")
    args = parser.parse_args()
    print(
        build_ftaw_public_url_fetch_report(
            args.source_registry_path,
            args.reviewed_registry_copy_path,
            args.auto_draft_config_path,
            args.fetch_config_path,
        )
    )


if __name__ == "__main__":
    main()
