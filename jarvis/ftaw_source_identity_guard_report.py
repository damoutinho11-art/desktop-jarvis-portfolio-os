"""Readable report for FTAW source identity guard."""

from __future__ import annotations

from pathlib import Path

from .ftaw_source_identity_guard import build_ftaw_source_identity_guard_from_files


def build_ftaw_source_identity_guard_report(
    source_registry_path: str | Path,
    reviewed_registry_copy_path: str | Path | None,
    fact_intake_config_path: str | Path,
    guard_config_path: str | Path,
) -> str:
    result = build_ftaw_source_identity_guard_from_files(
        source_registry_path,
        reviewed_registry_copy_path,
        fact_intake_config_path,
        guard_config_path,
    )
    lines = [
        "J.A.R.V.I.S. FTAW Source Identity Guard Report",
        "Do not trust facts unless they belong to the exact asset.",
        f"FTAW source identity guard status: {result.identity_guard_status}",
        f"target asset: {result.asset_id}",
        "checked identity fields:",
    ]
    lines.extend(f"- {field}" for field in result.checked_fields) if result.checked_fields else lines.append("- none")
    lines.append("matched fields:")
    lines.extend(f"- {field}" for field in result.matched_fields) if result.matched_fields else lines.append("- none")
    lines.append("missing identity fields:")
    lines.extend(f"- {field}" for field in result.missing_identity_fields) if result.missing_identity_fields else lines.append("- none")
    lines.append("placeholder identity fields:")
    lines.extend(f"- {field}" for field in result.placeholder_identity_fields) if result.placeholder_identity_fields else lines.append("- none")
    lines.append("mismatched fields:")
    lines.extend(f"- {field}" for field in result.mismatched_fields) if result.mismatched_fields else lines.append("- none")
    lines.append("skipped manual evidence types:")
    lines.extend(f"- {field}" for field in result.skipped_evidence_types) if result.skipped_evidence_types else lines.append("- none")
    lines.append("blockers:")
    lines.extend(f"- {blocker}" for blocker in result.blockers) if result.blockers else lines.append("- none")
    lines.append("warnings:")
    lines.extend(f"- {warning}" for warning in result.warnings) if result.warnings else lines.append("- none")
    lines.extend(
        [
            f"identity guard passed: {str(result.identity_guard_passed).lower()}",
            "manual verification still required: true",
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

    parser = argparse.ArgumentParser(description="Build FTAW source identity guard report.")
    parser.add_argument("source_registry_path", nargs="?", default="jarvis/data/candidate_assets.v2.example.json")
    parser.add_argument("reviewed_registry_copy_path", nargs="?", default="jarvis/data/private/candidate_assets.v2.reviewed.local.json")
    parser.add_argument("fact_intake_config_path", nargs="?", default="jarvis/data/ftaw_source_fact_intake.example.json")
    parser.add_argument("guard_config_path", nargs="?", default="jarvis/data/ftaw_source_identity_guard.example.json")
    args = parser.parse_args()
    print(
        build_ftaw_source_identity_guard_report(
            args.source_registry_path,
            args.reviewed_registry_copy_path,
            args.fact_intake_config_path,
            args.guard_config_path,
        )
    )


if __name__ == "__main__":
    main()
