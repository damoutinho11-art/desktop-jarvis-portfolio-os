"""Readable report for real evidence collection checklists."""

from __future__ import annotations

from pathlib import Path

from .evidence_collection_checklist import (
    EvidenceCollectionChecklistResult,
    build_evidence_collection_checklist_from_files,
)


def _top_missing(result: EvidenceCollectionChecklistResult) -> list[tuple[str, int]]:
    counts: dict[str, int] = {}
    for checklist in result.checklists:
        for item in checklist.items:
            if item.current_status == "missing":
                counts[item.evidence_type] = counts.get(item.evidence_type, 0) + 1
    return sorted(counts.items(), key=lambda item: (-item[1], item[0]))


def build_evidence_collection_report(registry_path: str | Path, intake_path: str | Path) -> str:
    result = build_evidence_collection_checklist_from_files(registry_path, intake_path)
    summary = result.summary
    ready = [checklist.asset_id for checklist in result.checklists if checklist.collection_complete]
    missing = _top_missing(result)
    lines = [
        "J.A.R.V.I.S. Evidence Collection Checklist Report",
        "Read-only checklist. Collection complete is not approval, recommendation, or execution.",
        f"checklist status: {result.checklist_status}",
        f"total candidates: {summary.total_candidates}",
        f"complete checklists: {summary.complete_checklists}",
        f"incomplete checklists: {summary.incomplete_checklists}",
        "top missing evidence types:",
    ]
    lines.extend(f"- {evidence_type}: {count}" for evidence_type, count in missing) if missing else lines.append("- none")
    lines.append("candidates ready for real status review evidence collection complete:")
    lines.extend(f"- {asset_id}" for asset_id in ready) if ready else lines.append("- none")
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

    parser = argparse.ArgumentParser(description="Generate real evidence collection checklist without approvals.")
    parser.add_argument("registry_path", nargs="?", default="jarvis/data/candidate_assets.v2.example.json")
    parser.add_argument("intake_path", nargs="?", default="jarvis/data/verified_evidence_intake.example.json")
    args = parser.parse_args()
    print(build_evidence_collection_report(args.registry_path, args.intake_path))


if __name__ == "__main__":
    main()
