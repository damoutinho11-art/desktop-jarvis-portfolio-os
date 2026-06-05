"""Readable report for the candidate evidence coverage matrix."""

from __future__ import annotations

from pathlib import Path

from .candidate_evidence_matrix import CandidateEvidenceMatrix, build_candidate_evidence_matrix


def _top_missing_categories(matrix: CandidateEvidenceMatrix) -> list[tuple[str, int]]:
    counts: dict[str, int] = {}
    for row in matrix.rows:
        for category in row.missing_evidence:
            counts[category] = counts.get(category, 0) + 1
    return sorted(counts.items(), key=lambda item: (-item[1], item[0]))


def build_candidate_evidence_report(
    registry_path: str | Path,
    market_data_path: str | Path,
    exposure_path: str | Path,
    policy_path: str | Path,
) -> str:
    matrix = build_candidate_evidence_matrix(registry_path, market_data_path, exposure_path, policy_path)
    summary = matrix.summary
    lines = [
        "J.A.R.V.I.S. Candidate Evidence Coverage Matrix",
        "Read-only evidence audit. No approvals, recommendations, registry mutation, or trades created.",
        f"matrix status: {matrix.status}",
        f"total candidates: {summary.total_candidates}",
        f"eligible count: {summary.eligible_for_manual_review_count}",
        f"blocked count: {summary.blocked_count}",
        "top missing evidence categories:",
    ]
    missing = _top_missing_categories(matrix)
    lines.extend(f"- {category}: {count}" for category, count in missing) if missing else lines.append("- none")
    lines.append("candidates by sleeve:")
    lines.extend(f"- {sleeve}: {count}" for sleeve, count in summary.by_sleeve.items())
    lines.append("candidates by asset_type:")
    lines.extend(f"- {asset_type}: {count}" for asset_type, count in summary.by_asset_type.items())
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

    parser = argparse.ArgumentParser(description="Report local candidate evidence coverage without approvals.")
    parser.add_argument("registry_path", nargs="?", default="jarvis/data/candidate_assets.v2.example.json")
    parser.add_argument("market_data_path", nargs="?", default="jarvis/data/market_data.example.json")
    parser.add_argument("exposure_path", nargs="?", default="jarvis/data/asset_exposure.example.json")
    parser.add_argument("policy_path", nargs="?", default="jarvis/data/portfolio_policy.example.json")
    args = parser.parse_args()
    print(build_candidate_evidence_report(args.registry_path, args.market_data_path, args.exposure_path, args.policy_path))


if __name__ == "__main__":
    main()
