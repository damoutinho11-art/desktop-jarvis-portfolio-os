"""Readable report for private verified evidence status review bridge."""

from __future__ import annotations

from pathlib import Path

from .private_status_review_bridge import build_private_status_review_bridge_from_files


def build_private_status_review_report(
    registry_path: str | Path,
    intake_path: str | Path,
    freshness_policy_path: str | Path,
    config_path: str | Path,
) -> str:
    result = build_private_status_review_bridge_from_files(registry_path, intake_path, freshness_policy_path, config_path)
    lines = [
        "J.A.R.V.I.S. Private Status Review Bridge Report",
        "Read-only private evidence bridge. Manual approval required.",
        f"private status review bridge status: {result.bridge_status}",
        f"verified eligible assets count: {result.verified_eligible_assets_count}",
        f"freshness-passing assets count: {result.freshness_passing_assets_count}",
        f"generated request previews count: {len(result.request_previews)}",
        "requested transitions:",
    ]
    if result.request_previews:
        for preview in result.request_previews:
            request = preview.status_request
            lines.append(f"- {request.asset_id}: {request.current_status} -> {request.requested_status}")
            lines.append(f"  freshness summary: {preview.freshness_summary}")
    else:
        lines.append("- none")
    lines.append("blocked assets:")
    if result.blocked_assets:
        for blocked in result.blocked_assets:
            lines.append(f"- {blocked.asset_id}: {', '.join(blocked.blockers)}")
    else:
        lines.append("- none")
    lines.append("warnings:")
    lines.extend(f"- {warning}" for warning in result.warnings) if result.warnings else lines.append("- none")
    lines.append("blockers:")
    lines.extend(f"- {blocker}" for blocker in result.blockers) if result.blockers else lines.append("- none")
    lines.extend(
        [
            f"manual approval required: {result.manual_approval_required}",
            "no registry mutation: true",
            "no approvals created: true",
            "no buy/sell requests: true",
            "no trades executed: true",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Generate manual status request previews from private verified evidence.")
    parser.add_argument("registry_path", nargs="?", default="jarvis/data/candidate_assets.v2.example.json")
    parser.add_argument("intake_path", nargs="?", default="jarvis/data/private/vwce_verified_evidence_combined.local.json")
    parser.add_argument("freshness_policy_path", nargs="?", default="jarvis/data/evidence_freshness_policy.example.json")
    parser.add_argument("config_path", nargs="?", default="jarvis/data/private_status_review_bridge.example.json")
    args = parser.parse_args()
    print(build_private_status_review_report(args.registry_path, args.intake_path, args.freshness_policy_path, args.config_path))


if __name__ == "__main__":
    main()
