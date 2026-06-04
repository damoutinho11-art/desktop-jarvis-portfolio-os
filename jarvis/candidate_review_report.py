"""Readable candidate review pack report."""

from __future__ import annotations

from pathlib import Path

from .candidate_review_engine import build_candidate_review_packs
from .candidate_review_pack import CandidateReviewPack


def _fmt(value: object) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.4f}"
    return str(value)


def build_candidate_review_report(
    registry_path: str | Path,
    market_data_path: str | Path | None = None,
    exposure_path: str | Path | None = None,
) -> str:
    packs = build_candidate_review_packs(registry_path, market_data_path, exposure_path)
    lines = [
        "J.A.R.V.I.S. Candidate Review Pack Report",
        "Read-only evidence pack. No recommendations generated.",
        f"total candidates: {len(packs)}",
    ]
    for pack in packs:
        lines.extend(
            [
                "",
                f"asset_id: {pack.asset_id}",
                f"asset_type: {pack.asset_type}",
                f"sleeve: {pack.sleeve}",
                f"approval_status: {pack.approval_status}",
                f"approved_for_allocation: {pack.approved_for_allocation}",
                f"final_candidate_score: {_fmt(pack.final_candidate_score)}",
                f"review_status: {pack.review_status}",
                f"can_submit_for_manual_approval: {pack.can_submit_for_manual_approval}",
                f"manual_approval_required: {pack.manual_approval_required}",
            ]
        )
        if pack.market_metrics_summary:
            lines.append(f"market_latest_price: {_fmt(pack.market_metrics_summary.get('latest_price'))}")
        else:
            lines.append("market_latest_price: n/a")
        if pack.exposure_summary:
            lines.append(f"exposure_holding_count: {pack.exposure_summary.get('holding_count')}")
        else:
            lines.append("exposure_holding_count: n/a")
        lines.append("warnings:")
        lines.extend(f"- {warning}" for warning in pack.warnings) if pack.warnings else lines.append("- none")
        lines.append("blockers:")
        lines.extend(f"- {blocker}" for blocker in pack.blockers) if pack.blockers else lines.append("- none")
    lines.append("")
    lines.append("No trades executed.")
    return "\n".join(lines)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Build read-only candidate review packs from local evidence.")
    parser.add_argument("registry_path", nargs="?", default="jarvis/data/candidate_assets.example.json")
    parser.add_argument("market_data_path", nargs="?", default="jarvis/data/market_data.example.json")
    parser.add_argument("exposure_path", nargs="?", default="jarvis/data/asset_exposure.example.json")
    args = parser.parse_args()
    print(build_candidate_review_report(args.registry_path, args.market_data_path, args.exposure_path))


if __name__ == "__main__":
    main()
