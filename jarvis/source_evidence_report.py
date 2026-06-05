"""Readable report for offline source evidence draft generation."""

from __future__ import annotations

from pathlib import Path

from .source_evidence_fetcher import SourceEvidenceRunResult, run_source_evidence_fetcher


def _status(result: SourceEvidenceRunResult) -> str:
    if any(item.status == "BLOCKED" for item in result.results):
        return "WARNING"
    if any(item.status == "WARNING" for item in result.results):
        return "WARNING"
    return "DRAFTS_CREATED"


def build_source_evidence_report(registry_path: str | Path, sources_path: str | Path) -> str:
    result = run_source_evidence_fetcher(registry_path, sources_path)
    drafts = [item for item in result.results if item.draft_evidence_record is not None]
    blocked = [item for item in result.results if item.status == "BLOCKED"]
    warnings = tuple(warning for item in result.results for warning in item.warnings)
    blockers = tuple(blocker for item in result.results for blocker in item.blockers)
    fact_counts: dict[str, int] = {}
    for item in result.results:
        for key in item.extracted_facts:
            fact_counts[key] = fact_counts.get(key, 0) + 1
    lines = [
        "J.A.R.V.I.S. Source Evidence Draft Report",
        "Automated research, manual trust. No network calls are made in default mode.",
        f"source evidence status: {_status(result)}",
        f"total source configs: {len(result.results)}",
        f"draft evidence records created: {len(drafts)}",
        f"blocked sources: {len(blocked)}",
        "warnings:",
    ]
    lines.extend(f"- {warning}" for warning in warnings) if warnings else lines.append("- none")
    lines.append("blockers:")
    lines.extend(f"- {blocker}" for blocker in blockers) if blockers else lines.append("- none")
    lines.append("extracted fact summary:")
    if fact_counts:
        for key, count in sorted(fact_counts.items()):
            lines.append(f"- {key}: {count}")
    else:
        lines.append("- none")
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

    parser = argparse.ArgumentParser(description="Prepare draft evidence from safe local/static sources only.")
    parser.add_argument("registry_path", nargs="?", default="jarvis/data/candidate_assets.v2.example.json")
    parser.add_argument("sources_path", nargs="?", default="jarvis/data/source_evidence_sources.example.json")
    args = parser.parse_args()
    print(build_source_evidence_report(args.registry_path, args.sources_path))


if __name__ == "__main__":
    main()
