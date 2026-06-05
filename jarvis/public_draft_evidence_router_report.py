"""Readable report for routed public draft evidence."""

from __future__ import annotations

from pathlib import Path

from .public_draft_evidence_router import build_public_draft_evidence_router_pack


def build_public_draft_evidence_router_report(registry_path: str | Path, public_sources_path: str | Path) -> str:
    pack = build_public_draft_evidence_router_pack(registry_path, public_sources_path)
    summary = pack.summary
    lines = [
        "J.A.R.V.I.S. Public Draft Evidence Router Report",
        "Automated research. Manual trust.",
        f"router status: {pack.router_status}",
        f"total public source results: {summary.total_public_source_results}",
        f"routed draft evidence count: {summary.routed_draft_records_count}",
        "routed evidence by asset:",
    ]
    if summary.routed_records_by_asset:
        for asset_id, count in summary.routed_records_by_asset.items():
            lines.append(f"- {asset_id}: {count}")
    else:
        lines.append("- none")
    lines.append("routed evidence by evidence type:")
    if summary.routed_records_by_evidence_type:
        for evidence_type, count in summary.routed_records_by_evidence_type.items():
            lines.append(f"- {evidence_type}: {count}")
    else:
        lines.append("- none")
    lines.append(f"missing routes: {summary.missing_routes_count}")
    lines.append("warnings:")
    lines.extend(f"- {warning}" for warning in summary.warnings) if summary.warnings else lines.append("- none")
    lines.append("blockers:")
    lines.extend(f"- {blocker}" for blocker in summary.blockers) if summary.blockers else lines.append("- none")
    lines.extend(
        [
            "user verification required: true",
            "no approvals created: true",
            "no registry mutation: true",
            "no buy/sell requests: true",
            "no trades executed: true",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Route public draft evidence into manual verification categories.")
    parser.add_argument("registry_path", nargs="?", default="jarvis/data/candidate_assets.v2.example.json")
    parser.add_argument("public_sources_path", nargs="?", default="jarvis/data/public_source_fetch.example.json")
    args = parser.parse_args()
    print(build_public_draft_evidence_router_report(args.registry_path, args.public_sources_path))


if __name__ == "__main__":
    main()
