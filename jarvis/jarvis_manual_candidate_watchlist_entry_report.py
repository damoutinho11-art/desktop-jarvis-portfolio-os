"""Markdown report for manual candidate watchlist entries."""

from __future__ import annotations

import argparse
from pathlib import Path

from .jarvis_manual_candidate_watchlist_entry import ManualCandidateWatchlistEntryPack, load_watchlist_entry_pack


DEFAULT_INPUT = Path("jarvis/data/jarvis_manual_candidate_watchlist_entry.example.json")


def build_manual_candidate_watchlist_entry_report(pack: ManualCandidateWatchlistEntryPack) -> str:
    lines = [
        f"# {pack.title}",
        "",
        f"version: {pack.version}",
        f"overall status: {pack.overall_status}",
        f"watchlist entry count: {pack.watchlist_entry_count}",
        "",
        "Manual watchlist entry is record-only. READY_FOR_CANDIDATE_INTAKE means ready for v4.49 review only.",
        "",
        "## Entries",
    ]
    for entry in pack.entries:
        lines.extend(
            [
                f"### {entry.watchlist_entry_id}",
                f"- candidate id: {entry.candidate_id}",
                f"- display name: {entry.display_name}",
                f"- status: {entry.entry_status}",
                f"- asset type: {entry.asset_type}",
                f"- symbol or identifier: {entry.symbol_or_identifier}",
                f"- candidate intake preview available: {str(entry.candidate_intake_preview_available).lower()}",
                "- intended route: v4.50 manual watchlist entry -> v4.49 candidate intake -> v4.27-v4.47 Phase 1 real evidence pipeline",
                f"- blocked reasons: {', '.join(entry.blocked_reasons) if entry.blocked_reasons else 'none'}",
                f"- warnings: {', '.join(entry.warnings) if entry.warnings else 'none'}",
            ]
        )
        if entry.candidate_intake_preview is not None:
            preview = entry.candidate_intake_preview
            lines.extend(
                [
                    "- candidate intake preview:",
                    f"  - candidate_id: {preview['candidate_id']}",
                    f"  - display_name: {preview['display_name']}",
                    f"  - asset_type: {preview['asset_type']}",
                    f"  - symbol_or_identifier: {preview['symbol_or_identifier']}",
                    f"  - phase1_route: {preview['phase1_route']}",
                    f"  - approved_asset: {str(preview['approved_asset']).lower()}",
                    f"  - trusted_asset: {str(preview['trusted_asset']).lower()}",
                    f"  - investable: {str(preview['investable']).lower()}",
                    f"  - allocation_recommendation: {str(preview['allocation_recommendation']).lower()}",
                    f"  - buy_signal: {str(preview['buy_signal']).lower()}",
                    f"  - sell_signal: {str(preview['sell_signal']).lower()}",
                    f"  - trade_executed: {str(preview['trade_executed']).lower()}",
                    f"  - registry_mutation: {str(preview['registry_mutation']).lower()}",
                    f"  - executor_created: {str(preview['executor_created']).lower()}",
                ]
            )
    lines.append("")
    lines.append("## Blocked Reasons")
    lines.extend(f"- {reason}" for reason in pack.blocked_reasons) if pack.blocked_reasons else lines.append("- none")
    lines.append("")
    lines.append("## Warnings")
    lines.extend(f"- {warning}" for warning in pack.warnings) if pack.warnings else lines.append("- none")
    lines.extend(
        [
            "",
            "## Safety Statements",
            "no approval",
            "no trusted asset",
            "no investable asset",
            "no evidence verification",
            "no verified evidence promotion",
            "no registry mutation",
            "no registry file written",
            "no allocation recommendation",
            "no portfolio weight",
            "no buy/sell request",
            "no buy signal",
            "no sell signal",
            "no trade",
            "no trade executed",
            "no executor",
            "no broker/authenticated API",
            "no credentials",
            "no private file ingest",
            "no automatic fetching/downloads/extraction",
            "",
            "This report does not claim approval, trust, investability, verification, promotion, allocation, portfolio weight, buy/sell, trade, registry mutation, broker API use, credential use, private ingest, fetching/downloads, or executor authorization.",
        ]
    )
    return "\n".join(lines)


def build_report_from_path(path: str | Path = DEFAULT_INPUT) -> str:
    return build_manual_candidate_watchlist_entry_report(load_watchlist_entry_pack(path))


def main() -> None:
    parser = argparse.ArgumentParser(description="Print the J.A.R.V.I.S. manual candidate watchlist entry report.")
    parser.add_argument("--input", default=str(DEFAULT_INPUT), help="Path to manual watchlist JSON.")
    args = parser.parse_args()
    print(build_report_from_path(args.input))


if __name__ == "__main__":
    main()
