"""Readable report for verified evidence promotion previews."""

from __future__ import annotations

from pathlib import Path

from .verified_evidence_promotion import build_verified_evidence_promotion_pack_from_files


def build_verified_evidence_promotion_report(
    registry_path: str | Path,
    sources_path: str | Path,
    decisions_path: str | Path,
) -> str:
    pack = build_verified_evidence_promotion_pack_from_files(registry_path, sources_path, decisions_path)
    lines = [
        "J.A.R.V.I.S. Verified Evidence Promotion Pack Report",
        "Read-only promotion preview. No files are written by default.",
        f"promotion pack status: {pack.promotion_pack_status}",
        f"total verification tasks: {pack.total_tasks}",
        f"accepted count: {pack.accepted_count}",
        f"rejected count: {pack.rejected_count}",
        f"needs_correction count: {pack.needs_correction_count}",
        f"verified evidence preview count: {pack.verified_evidence_preview_count}",
        "assets ready for real status review:",
    ]
    if pack.assets_ready_for_real_status_review:
        lines.extend(f"- {asset_id}" for asset_id in pack.assets_ready_for_real_status_review)
    else:
        lines.append("- none")
    lines.append("blockers:")
    lines.extend(f"- {blocker}" for blocker in pack.blockers) if pack.blockers else lines.append("- none")
    lines.append("warnings:")
    lines.extend(f"- {warning}" for warning in pack.warnings) if pack.warnings else lines.append("- none")
    lines.extend(
        [
            "no registry mutation: true",
            "no approvals created: true",
            "no buy/sell requests: true",
            "no trades executed: true",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Preview verified evidence promotion without writing files.")
    parser.add_argument("registry_path", nargs="?", default="jarvis/data/candidate_assets.v2.example.json")
    parser.add_argument("sources_path", nargs="?", default="jarvis/data/source_evidence_sources.example.json")
    parser.add_argument("decisions_path", nargs="?", default="jarvis/data/verified_evidence_promotion.example.json")
    args = parser.parse_args()
    print(build_verified_evidence_promotion_report(args.registry_path, args.sources_path, args.decisions_path))


if __name__ == "__main__":
    main()
