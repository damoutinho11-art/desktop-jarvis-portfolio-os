"""Readable report for the real status-review request bridge."""

from __future__ import annotations

from pathlib import Path

from .real_status_review_bridge import build_real_status_review_bridge_from_files


def build_real_status_review_report(
    registry_path: str | Path,
    sources_path: str | Path,
    promotion_path: str | Path,
) -> str:
    result = build_real_status_review_bridge_from_files(registry_path, sources_path, promotion_path)
    lines = [
        "J.A.R.V.I.S. Real Status Review Bridge Report",
        "Read-only status request preview. No files are written by default.",
        f"bridge status: {result.bridge_status}",
        f"ready assets count: {result.ready_assets_count}",
        f"generated request preview count: {len(result.status_requests)}",
        f"manual approval required: {result.manual_approval_required}",
        f"registry mutation allowed: {result.registry_mutation_allowed}",
        "requested transitions:",
    ]
    if result.status_requests:
        for request in result.status_requests:
            lines.append(f"- {request.asset_id}: {request.current_status} -> {request.requested_status}")
    else:
        lines.append("- none")

    lines.append("blocked assets:")
    if result.blocked_assets:
        for asset in result.blocked_assets:
            reason = ", ".join(asset.blockers) if asset.blockers else "blocked by validation or audit."
            lines.append(f"- {asset.asset_id}: {reason}")
    else:
        lines.append("- none")

    lines.append("warnings:")
    lines.extend(f"- {warning}" for warning in result.warnings) if result.warnings else lines.append("- none")
    lines.append("blockers:")
    lines.extend(f"- {blocker}" for blocker in result.blockers) if result.blockers else lines.append("- none")
    lines.extend(
        [
            "No approvals created.",
            "No registry mutation.",
            "No buy/sell requests created.",
            "No trades executed.",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Bridge verified evidence readiness into status request previews.")
    parser.add_argument("registry_path", nargs="?", default="jarvis/data/candidate_assets.v2.example.json")
    parser.add_argument("sources_path", nargs="?", default="jarvis/data/source_evidence_sources.example.json")
    parser.add_argument("promotion_path", nargs="?", default="jarvis/data/verified_evidence_promotion.example.json")
    args = parser.parse_args()
    print(build_real_status_review_report(args.registry_path, args.sources_path, args.promotion_path))


if __name__ == "__main__":
    main()
