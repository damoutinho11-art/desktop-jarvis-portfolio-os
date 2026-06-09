"""Readable report for FTAW source fact intake."""

from __future__ import annotations

import json
from pathlib import Path

from .ftaw_source_fact_intake import build_ftaw_source_fact_intake_pack_from_files


def build_ftaw_source_fact_intake_report(
    source_registry_path: str | Path,
    reviewed_registry_copy_path: str | Path | None,
    url_fetch_config_path: str | Path,
    fact_intake_config_path: str | Path,
) -> str:
    pack = build_ftaw_source_fact_intake_pack_from_files(
        source_registry_path,
        reviewed_registry_copy_path,
        url_fetch_config_path,
        fact_intake_config_path,
    )
    sample = pack.draft_evidence_records[0] if pack.draft_evidence_records else {}
    lines = [
        "J.A.R.V.I.S. FTAW Source Fact Intake Report",
        "Automated structure. Manual trust.",
        f"FTAW source fact intake status: {pack.intake_status}",
        f"processed fact records count: {pack.processed_fact_records_count}",
        f"draft evidence records count: {len(pack.draft_evidence_records)}",
        f"draft-ready count: {pack.draft_ready_count}",
        f"needs-correction count: {pack.needs_correction_count}",
        "skipped manual evidence types:",
    ]
    lines.extend(f"- {item}" for item in pack.skipped_manual_evidence_types) if pack.skipped_manual_evidence_types else lines.append("- none")
    lines.append("missing facts by evidence type:")
    if pack.missing_facts_by_evidence_type:
        lines.extend(
            f"- {evidence_type}: {', '.join(missing)}"
            for evidence_type, missing in pack.missing_facts_by_evidence_type.items()
        )
    else:
        lines.append("- none")
    lines.extend(
        [
            "sample draft record:",
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

    parser = argparse.ArgumentParser(description="Build FTAW source fact intake report.")
    parser.add_argument("source_registry_path", nargs="?", default="jarvis/data/candidate_assets.v2.example.json")
    parser.add_argument("reviewed_registry_copy_path", nargs="?", default="jarvis/data/private/candidate_assets.v2.reviewed.local.json")
    parser.add_argument("url_fetch_config_path", nargs="?", default="jarvis/data/ftaw_public_url_fetch_adapter.example.json")
    parser.add_argument("fact_intake_config_path", nargs="?", default="jarvis/data/ftaw_source_fact_intake.example.json")
    args = parser.parse_args()
    print(
        build_ftaw_source_fact_intake_report(
            args.source_registry_path,
            args.reviewed_registry_copy_path,
            args.url_fetch_config_path,
            args.fact_intake_config_path,
        )
    )


if __name__ == "__main__":
    main()
