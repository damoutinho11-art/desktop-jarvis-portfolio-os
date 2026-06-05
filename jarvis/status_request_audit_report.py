"""Readable status request audit pack report."""

from __future__ import annotations

from pathlib import Path

from .status_request_audit_pack import build_status_request_audit


def build_status_request_audit_report(
    registry_path: str | Path,
    market_data_path: str | Path,
    exposure_path: str | Path,
    policy_path: str | Path,
) -> str:
    result = build_status_request_audit(registry_path, market_data_path, exposure_path, policy_path)
    summary = result.summary
    lines = [
        "J.A.R.V.I.S. Status Request Audit Pack Report",
        "Read-only audit pack. No registry mutation allowed.",
        f"audit pack status: {result.status}",
        f"total requests: {summary.total_status_request_previews}",
        f"audit-ready requests: {summary.audit_ready_count}",
        f"blocked requests: {summary.blocked_count}",
        f"manual approval required: {result.manual_approval_required}",
        f"registry mutation forbidden: {summary.registry_mutation_forbidden}",
        "requested transitions:",
    ]
    if result.audit_packs:
        for pack in result.audit_packs:
            lines.append(f"- {pack.asset_id}: {pack.current_status} -> {pack.requested_status}; audit_ready={pack.audit_ready}")
            if pack.missing_confirmations:
                lines.append(f"  missing confirmations: {', '.join(pack.missing_confirmations)}")
            else:
                lines.append("  missing confirmations: none")
    else:
        lines.append("- none")
    lines.append("warnings:")
    lines.extend(f"- {warning}" for warning in summary.warnings) if summary.warnings else lines.append("- none")
    lines.append("blockers:")
    lines.extend(f"- {blocker}" for blocker in summary.blockers) if summary.blockers else lines.append("- none")
    lines.append("No approvals created.")
    lines.append("No trades executed.")
    return "\n".join(lines)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Build read-only audit packs for generated status request previews.")
    parser.add_argument("registry_path", nargs="?", default="jarvis/data/candidate_assets.example.json")
    parser.add_argument("market_data_path", nargs="?", default="jarvis/data/market_data.example.json")
    parser.add_argument("exposure_path", nargs="?", default="jarvis/data/asset_exposure.example.json")
    parser.add_argument("policy_path", nargs="?", default="jarvis/data/portfolio_policy.example.json")
    args = parser.parse_args()
    print(build_status_request_audit_report(args.registry_path, args.market_data_path, args.exposure_path, args.policy_path))


if __name__ == "__main__":
    main()
