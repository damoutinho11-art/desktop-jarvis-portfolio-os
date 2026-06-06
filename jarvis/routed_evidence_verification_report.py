"""Readable report for focused routed evidence verification packs."""

from __future__ import annotations

from pathlib import Path

from .routed_evidence_verification_pack import build_routed_evidence_verification_pack_from_files


def build_routed_evidence_verification_report(
    registry_path: str | Path,
    public_sources_path: str | Path,
    config_path: str | Path,
) -> str:
    pack = build_routed_evidence_verification_pack_from_files(registry_path, public_sources_path, config_path)
    lines = [
        "J.A.R.V.I.S. Routed Evidence Verification Pack Report",
        "Automated research. Manual trust.",
        f"verification pack status: {pack.verification_pack_status}",
        f"target asset: {pack.target_asset_id}",
        "required evidence types:",
    ]
    lines.extend(f"- {evidence_type}" for evidence_type in pack.required_evidence_types)
    lines.append(f"pending verification tasks count: {len(pack.pending_tasks)}")
    lines.append("missing evidence types:")
    lines.extend(f"- {evidence_type}" for evidence_type in pack.missing_evidence_types) if pack.missing_evidence_types else lines.append("- none")
    lines.append("selected source per evidence type:")
    if pack.selected_source_by_evidence_type:
        for evidence_type, source_name in pack.selected_source_by_evidence_type.items():
            lines.append(f"- {evidence_type}: {source_name}")
    else:
        lines.append("- none")
    lines.append("recommended decision per evidence type:")
    if pack.recommended_decision_by_evidence_type:
        for evidence_type, decision in pack.recommended_decision_by_evidence_type.items():
            lines.append(f"- {evidence_type}: {decision}")
    else:
        lines.append("- none")
    lines.append(f"accepted preview count: {len(pack.accepted_previews)}")
    lines.append("warnings:")
    lines.extend(f"- {warning}" for warning in pack.warnings) if pack.warnings else lines.append("- none")
    lines.append("blockers:")
    lines.extend(f"- {blocker}" for blocker in pack.blockers) if pack.blockers else lines.append("- none")
    lines.extend(
        [
            "no approvals created: true",
            "no registry mutation: true",
            "no buy/sell requests: true",
            "no trades executed: true",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Build a focused manual verification pack from routed public draft evidence.")
    parser.add_argument("registry_path", nargs="?", default="jarvis/data/candidate_assets.v2.example.json")
    parser.add_argument("public_sources_path", nargs="?", default="jarvis/data/public_source_fetch.example.json")
    parser.add_argument("config_path", nargs="?", default="jarvis/data/routed_evidence_verification_pack.example.json")
    args = parser.parse_args()
    print(build_routed_evidence_verification_report(args.registry_path, args.public_sources_path, args.config_path))


if __name__ == "__main__":
    main()
