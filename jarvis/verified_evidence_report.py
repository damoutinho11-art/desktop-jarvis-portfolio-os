"""Readable report for manual verified evidence intake packs."""

from __future__ import annotations

from pathlib import Path

from .verified_evidence_intake import build_verified_evidence_pack_from_files


def build_verified_evidence_report(registry_path: str | Path, intake_path: str | Path) -> str:
    pack = build_verified_evidence_pack_from_files(registry_path, intake_path)
    summary = pack.summary
    lines = [
        "J.A.R.V.I.S. Verified Evidence Intake Report",
        "Read-only manual evidence intake. No approvals, recommendations, registry mutation, or trades created.",
        f"intake status: {pack.intake_status}",
        f"total records: {summary.total_intake_records}",
        f"valid records: {summary.valid_records}",
        f"invalid records: {summary.invalid_records}",
        f"verified records: {summary.verified_records}",
        f"unverified records: {summary.unverified_records}",
        "assets with real_status_promotion_allowed:",
    ]
    if pack.assets_with_real_status_promotion_allowed:
        lines.extend(f"- {asset_id}" for asset_id in pack.assets_with_real_status_promotion_allowed)
    else:
        lines.append("- none")
    lines.append("blockers:")
    lines.extend(f"- {blocker}" for blocker in summary.blockers) if summary.blockers else lines.append("- none")
    lines.append("warnings:")
    lines.extend(f"- {warning}" for warning in summary.warnings) if summary.warnings else lines.append("- none")
    lines.extend(
        [
            "no registry mutation: true",
            "no approvals created: true",
            "no buy/sell requests: true",
            "no trades executed: true",
            "Manual approval required for all future actions.",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Audit verified evidence intake without approvals.")
    parser.add_argument("registry_path", nargs="?", default="jarvis/data/candidate_assets.v2.example.json")
    parser.add_argument("intake_path", nargs="?", default="jarvis/data/verified_evidence_intake.example.json")
    args = parser.parse_args()
    print(build_verified_evidence_report(args.registry_path, args.intake_path))


if __name__ == "__main__":
    main()
