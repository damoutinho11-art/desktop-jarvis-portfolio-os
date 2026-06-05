"""Readable report for human evidence collection packs."""

from __future__ import annotations

import json
from pathlib import Path

from .evidence_collection_pack import EvidenceCollectionPack, build_evidence_collection_pack


def _top_counts(counts: dict[str, int], limit: int = 5) -> list[tuple[str, int]]:
    return sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:limit]


def build_evidence_collection_pack_report(registry_path: str | Path, intake_path: str | Path) -> str:
    pack = build_evidence_collection_pack(registry_path, intake_path)
    summary = pack.summary
    first_high = next((task for task in pack.tasks if task.priority == "high"), None)
    lines = [
        "J.A.R.V.I.S. Evidence Collection Pack Report",
        "Human collection instructions only. No external data is fetched.",
        f"collection pack status: {pack.collection_pack_status}",
        f"total tasks: {summary.total_collection_tasks}",
        f"high priority tasks: {summary.high_priority_tasks}",
        "top candidates requiring evidence:",
    ]
    top_assets = _top_counts(summary.tasks_by_asset)
    lines.extend(f"- {asset_id}: {count}" for asset_id, count in top_assets) if top_assets else lines.append("- none")
    lines.append("top missing evidence types:")
    top_types = _top_counts(summary.tasks_by_evidence_type)
    lines.extend(f"- {evidence_type}: {count}" for evidence_type, count in top_types) if top_types else lines.append("- none")
    lines.append("sample intake template for first high-priority task:")
    if first_high:
        lines.append(json.dumps(first_high.intake_record_template, indent=2, sort_keys=True))
    else:
        lines.append("- none")
    lines.extend(
        [
            "no approvals created: true",
            "no registry mutation: true",
            "no buy/sell requests: true",
            "no trades executed: true",
            "Manual approval required for all future actions.",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Generate human evidence collection pack without fetching data.")
    parser.add_argument("registry_path", nargs="?", default="jarvis/data/candidate_assets.v2.example.json")
    parser.add_argument("intake_path", nargs="?", default="jarvis/data/verified_evidence_intake.example.json")
    args = parser.parse_args()
    print(build_evidence_collection_pack_report(args.registry_path, args.intake_path))


if __name__ == "__main__":
    main()
