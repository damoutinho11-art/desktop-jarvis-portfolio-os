"""Readable report for optional public source draft evidence fetching."""

from __future__ import annotations

from pathlib import Path

from .public_source_fetcher import PublicSourceFetchRunResult, run_public_source_fetcher


def _status(result: PublicSourceFetchRunResult) -> str:
    if any(item.status == "BLOCKED" for item in result.results):
        return "WARNING"
    if any(item.status == "WARNING" for item in result.results):
        return "WARNING"
    return "DRAFTS_CREATED"


def build_public_source_report(registry_path: str | Path, sources_path: str | Path) -> str:
    result = run_public_source_fetcher(registry_path, sources_path)
    drafts = [item for item in result.results if item.draft_evidence_record is not None]
    blocked = [item for item in result.results if item.status == "BLOCKED"]
    warnings = tuple(warning for item in result.results for warning in item.warnings)
    blockers = tuple(blocker for item in result.results for blocker in item.blockers)
    modes: dict[str, int] = {}
    for item in result.results:
        modes[item.mode] = modes.get(item.mode, 0) + 1
    lines = [
        "J.A.R.V.I.S. Public Source Fetch Report",
        "Automated research. Manual trust.",
        f"public fetch status: {_status(result)}",
        f"total source configs: {len(result.results)}",
        f"draft evidence records created: {len(drafts)}",
        f"blocked sources: {len(blocked)}",
        "fetched/fallback mode:",
    ]
    if modes:
        for mode, count in sorted(modes.items()):
            lines.append(f"- {mode}: {count}")
    else:
        lines.append("- none")
    lines.append("warnings:")
    lines.extend(f"- {warning}" for warning in warnings) if warnings else lines.append("- none")
    lines.append("blockers:")
    lines.extend(f"- {blocker}" for blocker in blockers) if blockers else lines.append("- none")
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

    parser = argparse.ArgumentParser(description="Prepare draft evidence from optional public sources.")
    parser.add_argument("registry_path", nargs="?", default="jarvis/data/candidate_assets.v2.example.json")
    parser.add_argument("sources_path", nargs="?", default="jarvis/data/public_source_fetch.example.json")
    args = parser.parse_args()
    print(build_public_source_report(args.registry_path, args.sources_path))


if __name__ == "__main__":
    main()
