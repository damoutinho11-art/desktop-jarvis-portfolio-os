"""Readable universe review workflow report."""

from __future__ import annotations

from pathlib import Path

from .universe_review_workflow import build_universe_review


def _score(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.2f}"


def build_universe_review_report(
    registry_path: str | Path,
    market_data_path: str | Path,
    exposure_path: str | Path,
    policy_path: str | Path,
) -> str:
    result = build_universe_review(registry_path, market_data_path, exposure_path, policy_path)
    summary = result.summary
    lines = [
        "J.A.R.V.I.S. Universe Review Report",
        "Read-only candidate review workflow. No registry changes written.",
        f"total candidates: {summary.total_candidates}",
        f"review_ready count: {summary.review_ready_count}",
        f"blocked count: {summary.blocked_count}",
        f"approved universe count: {summary.approved_universe_count}",
        f"allocation_ready: {summary.allocation_ready}",
        "by sleeve:",
    ]
    lines.extend(f"- {sleeve}: {count}" for sleeve, count in summary.by_sleeve.items()) if summary.by_sleeve else lines.append("- none")
    lines.append("by status:")
    lines.extend(f"- {status}: {count}" for status, count in summary.by_status.items()) if summary.by_status else lines.append("- none")
    lines.append("candidates:")
    for candidate in result.candidates:
        lines.extend(
            [
                f"- {candidate.asset_id}:",
                f"  asset_type: {candidate.asset_type}",
                f"  sleeve: {candidate.sleeve}",
                f"  approval_status: {candidate.approval_status}",
                f"  final_candidate_score: {_score(candidate.final_candidate_score)}",
                f"  review_status: {candidate.review_status}",
                f"  can_submit_for_manual_approval: {candidate.can_submit_for_manual_approval}",
                f"  suggested_next_status: {candidate.suggested_next_status or 'none'}",
                f"  manual_approval_required: {candidate.manual_approval_required}",
            ]
        )
        if candidate.missing_evidence:
            lines.append(f"  missing_evidence: {', '.join(candidate.missing_evidence)}")
        else:
            lines.append("  missing_evidence: none")
    lines.append("warnings:")
    lines.extend(f"- {warning}" for warning in summary.warnings) if summary.warnings else lines.append("- none")
    lines.append("blockers:")
    lines.extend(f"- {blocker}" for blocker in summary.blockers) if summary.blockers else lines.append("- none")
    lines.append("No approvals created.")
    lines.append("No buy/sell requests created.")
    lines.append("No trades executed.")
    return "\n".join(lines)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Run read-only candidate universe review workflow.")
    parser.add_argument("registry_path", nargs="?", default="jarvis/data/candidate_assets.example.json")
    parser.add_argument("market_data_path", nargs="?", default="jarvis/data/market_data.example.json")
    parser.add_argument("exposure_path", nargs="?", default="jarvis/data/asset_exposure.example.json")
    parser.add_argument("policy_path", nargs="?", default="jarvis/data/portfolio_policy.example.json")
    args = parser.parse_args()
    print(build_universe_review_report(args.registry_path, args.market_data_path, args.exposure_path, args.policy_path))


if __name__ == "__main__":
    main()
