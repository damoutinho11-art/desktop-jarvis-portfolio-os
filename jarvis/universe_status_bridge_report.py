"""Readable universe review to status request bridge report."""

from __future__ import annotations

from pathlib import Path

from .universe_status_bridge import load_review_and_bridge


def build_universe_status_bridge_report(
    registry_path: str | Path,
    market_data_path: str | Path,
    exposure_path: str | Path,
    policy_path: str | Path,
) -> str:
    result = load_review_and_bridge(registry_path, market_data_path, exposure_path, policy_path)
    lines = [
        "J.A.R.V.I.S. Universe Status Bridge Report",
        "Read-only status request preview. No registry changes written.",
        f"bridge status: {result.status}",
        f"generated status requests count: {len(result.status_requests)}",
        f"manual approval required: {result.manual_approval_required}",
        f"registry mutation forbidden: {result.registry_mutation_forbidden}",
        "generated requests:",
    ]
    if result.status_requests:
        for request in result.status_requests:
            lines.append(f"- {request.asset_id}: {request.current_status} -> {request.requested_status}")
    else:
        lines.append("- none")
    lines.append("blocked candidates:")
    if result.blocked_candidates:
        for candidate in result.blocked_candidates:
            lines.append(f"- {candidate.asset_id}: {', '.join(candidate.blockers)}")
    else:
        lines.append("- none")
    lines.append("warnings:")
    lines.extend(f"- {warning}" for warning in result.warnings) if result.warnings else lines.append("- none")
    lines.append("No approvals created.")
    lines.append("No buy/sell requests created.")
    lines.append("No trades executed.")
    return "\n".join(lines)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Bridge universe review into local status request previews.")
    parser.add_argument("registry_path", nargs="?", default="jarvis/data/candidate_assets.example.json")
    parser.add_argument("market_data_path", nargs="?", default="jarvis/data/market_data.example.json")
    parser.add_argument("exposure_path", nargs="?", default="jarvis/data/asset_exposure.example.json")
    parser.add_argument("policy_path", nargs="?", default="jarvis/data/portfolio_policy.example.json")
    args = parser.parse_args()
    print(build_universe_status_bridge_report(args.registry_path, args.market_data_path, args.exposure_path, args.policy_path))


if __name__ == "__main__":
    main()
