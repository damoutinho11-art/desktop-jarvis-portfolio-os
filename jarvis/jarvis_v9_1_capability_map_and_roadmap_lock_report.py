"""Report CLI for J.A.R.V.I.S. v9.1 capability map and roadmap lock."""

from __future__ import annotations

import argparse

from .jarvis_v9_1_capability_map_and_roadmap_lock import (
    CapabilityMapAndRoadmapLockResult,
    audit_v9_1_capability_map_and_roadmap_lock,
)


def build_v9_1_capability_map_and_roadmap_lock_report(
    result: CapabilityMapAndRoadmapLockResult,
) -> str:
    lines = [
        "# J.A.R.V.I.S. v9.1 Capability Map and Roadmap Lock",
        "",
        f"status: {result.status}",
        f"roadmap lock status: {result.roadmap_lock_status}",
        f"recommended next stage: {result.recommended_next_stage}",
        f"capability count: {result.capability_count}",
        f"existing capability count: {result.existing_capability_count}",
        f"missing capability count: {result.missing_capability_count}",
        f"stale roadmap reference count: {result.stale_roadmap_reference_count}",
        f"active roadmap reference count: {result.active_roadmap_reference_count}",
        f"redundant stage count: {result.redundant_stage_count}",
        "",
        "## Capability Map",
    ]

    for entry in result.capability_map_entries:
        lines.extend(
            [
                "",
                f"### {entry.capability_id}",
                f"- group: {entry.group}",
                f"- stage or module: {entry.stage_or_module}",
                f"- file path: {entry.file_path}",
                f"- purpose: {entry.purpose}",
                f"- exists: {entry.exists}",
                f"- makes redundant: {', '.join(entry.makes_redundant) if entry.makes_redundant else 'none'}",
            ]
        )

    lines.extend(["", "## Active Roadmap References"])
    for ref in result.active_roadmap_references:
        lines.append(f"- {ref.file_path}: {ref.expected_reference} found={ref.found}")

    lines.extend(["", "## Stale Roadmap References"])
    if result.stale_roadmap_references:
        for ref in result.stale_roadmap_references:
            lines.append(f"- {ref.file_path}: {ref.stale_reference} count={ref.occurrence_count}")
    else:
        lines.append("- none")

    lines.extend(["", "## Redundant Stage Slugs"])
    for slug in result.redundant_stage_slugs:
        lines.append(f"- {slug}")

    lines.extend(["", "## Warnings"])
    lines.extend(f"- {warning}" for warning in result.warnings) if result.warnings else lines.append("- none")

    lines.extend(["", "## Blockers"])
    lines.extend(f"- {blocker}" for blocker in result.blockers) if result.blockers else lines.append("- none")

    lines.extend(
        [
            "",
            "## Safety",
            "",
            f"- capability map ready: {result.capability_map_ready}",
            f"- roadmap lock ready: {result.roadmap_lock_ready}",
            f"- source selection not repeated: {result.source_selection_not_repeated}",
            f"- dry-run planner not rebuilt: {result.dry_run_planner_not_rebuilt}",
            f"- provider registry not rebuilt: {result.provider_registry_not_rebuilt}",
            f"- public data enablement decision preserved: {result.public_data_enablement_decision_preserved}",
            f"- final user buy action required: {result.final_user_buy_action_required}",
            f"- buy request deferred: {result.buy_request_deferred}",
            f"- broker connection forbidden: {result.broker_connection_forbidden}",
            f"- order placement forbidden: {result.order_placement_forbidden}",
            f"- no trades executed: {result.no_trades_executed}",
            f"- live fetch deferred: {result.live_fetch_deferred}",
            f"- network calls deferred: {result.network_calls_deferred}",
            f"- raw response storage deferred: {result.raw_response_storage_deferred}",
            f"- live adapter record emission deferred: {result.live_adapter_record_emission_deferred}",
        ]
    )

    return "\n".join(lines) + "\n"


def report_v9_1_capability_map_and_roadmap_lock() -> str:
    return build_v9_1_capability_map_and_roadmap_lock_report(
        audit_v9_1_capability_map_and_roadmap_lock()
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Report J.A.R.V.I.S. v9.1 capability map and roadmap lock.")
    parser.parse_args()
    print(report_v9_1_capability_map_and_roadmap_lock())


if __name__ == "__main__":
    main()
