"""Readable report for evidence freshness and refresh policy."""

from __future__ import annotations

from pathlib import Path

from .evidence_freshness_policy import build_evidence_freshness_pack_from_files


def build_evidence_freshness_report(registry_path: str | Path, intake_path: str | Path, config_path: str | Path) -> str:
    pack = build_evidence_freshness_pack_from_files(registry_path, intake_path, config_path)
    summary = pack.summary
    lines = [
        "J.A.R.V.I.S. Evidence Freshness Report",
        "Automated research. Manual trust.",
        f"freshness report status: {pack.freshness_report_status}",
        "target assets checked:",
    ]
    lines.extend(f"- {asset_id}" for asset_id in summary.target_assets_checked)
    lines.extend(
        [
            f"fresh count: {summary.fresh_count}",
            f"stale count: {summary.stale_count}",
            f"missing count: {summary.missing_count}",
            f"auto-refresh available count: {summary.auto_refresh_available_count}",
            f"manual refresh required count: {summary.manual_refresh_required_count}",
            f"account-specific refresh required count: {summary.account_specific_refresh_required_count}",
            "recommended actions by evidence type:",
        ]
    )
    for key, action in summary.recommended_actions_by_evidence_type.items():
        lines.append(f"- {key}: {action}")
    lines.append("warnings:")
    lines.extend(f"- {warning}" for warning in summary.warnings) if summary.warnings else lines.append("- none")
    lines.append("blockers:")
    lines.extend(f"- {blocker}" for blocker in summary.blockers) if summary.blockers else lines.append("- none")
    lines.extend(
        [
            "no approvals created: true",
            "no registry mutation: true",
            "no buy/sell requests: true",
            "no trades executed: true",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Check verified evidence freshness and refresh policy.")
    parser.add_argument("registry_path", nargs="?", default="jarvis/data/candidate_assets.v2.example.json")
    parser.add_argument("intake_path", nargs="?", default="jarvis/data/private/vwce_verified_evidence_combined.local.json")
    parser.add_argument("config_path", nargs="?", default="jarvis/data/evidence_freshness_policy.example.json")
    args = parser.parse_args()
    print(build_evidence_freshness_report(args.registry_path, args.intake_path, args.config_path))


if __name__ == "__main__":
    main()
