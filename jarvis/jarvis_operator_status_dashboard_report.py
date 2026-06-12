"""Markdown report for the v4.59 J.A.R.V.I.S. operator status dashboard."""

from __future__ import annotations

import argparse
from pathlib import Path

from .jarvis_operator_status_dashboard import OperatorStatusDashboardResult, load_operator_dashboard_result


DEFAULT_INPUT = Path("jarvis/data/jarvis_operator_status_dashboard.example.json")


def _join(values: tuple[str, ...]) -> str:
    return ", ".join(values) if values else "none"


def build_operator_status_dashboard_report(result: OperatorStatusDashboardResult) -> str:
    completed = [
        key for key in (
            "phase1_complete",
            "candidate_intake_chain_complete",
            "manual_workspace_ready",
            "public_fetch_control_ready",
            "freshness_monitor_ready",
            "dashboard_ready",
        )
        if result.v5_progress.get(key) is True
    ]
    remaining = result.v5_progress.get("remaining_before_v5", [])
    remaining_items = tuple(str(item) for item in remaining) if isinstance(remaining, list) else ()
    lines = [
        f"# {result.title}",
        "",
        f"version: {result.version}",
        f"overall status: {result.overall_status}",
        f"dashboard mode: {result.dashboard_mode or 'missing'}",
        f"report only: {str(result.report_only).lower()}",
        f"no network: {str(result.no_network).lower()}",
        f"no writes: {str(result.no_writes).lower()}",
        f"no private file auto ingest: {str(result.no_private_file_auto_ingest).lower()}",
        f"current project phase: {result.current_project_phase or 'missing'}",
        f"current head note: {result.current_head_note or 'missing'}",
        f"next recommended manual action: {result.next_manual_action or 'missing'}",
        "",
        "This dashboard is not a gate, not a command contract, and not a review layer.",
        "It reads explicit dashboard config only and does not run subprocesses or call other reports automatically.",
        "",
        "## Component Status",
        "component | stage/version | latest known status | capability | blockers | next safe action",
        "--- | --- | --- | --- | --- | ---",
    ]
    for component in result.components:
        lines.append(
            f"{component.component_name} | {component.stage_range_or_version} | {component.latest_known_status} | "
            f"{component.capability_summary} | {_join(component.current_blockers)} | {component.next_safe_action}"
        )
    if not result.components:
        lines.append("none | none | none | none | missing component summaries | run_status_dashboard")
    lines.extend(
        [
            "",
            "## Where We Are",
            "- Phase 1 real evidence/manual review chain is summarized from explicit dashboard input.",
            "- Phase 2 candidate intake chain is summarized from explicit dashboard input.",
            "- Manual candidate workspace, public fetch control, and freshness monitoring are summarized without executing them.",
            "",
            "## Where We Need To Go",
            f"- next manual action: {result.next_manual_action or 'missing'}",
            "- use local/private manual candidate data entry for real candidates.",
            "- configure local public source manifests before any optional explicit public fetch.",
            "- treat stale/missing freshness only as a reason to consider v4.57 explicit local-cache fetch.",
            "",
            "## Do Not Build Next",
            "- do not build another gate without a new capability boundary.",
            "- do not build review-of-review loops.",
            "- do not build an executor, allocation engine, broker integration, or automatic trust/investability.",
            "",
            "## Redundancy Check",
            "- no more candidate-intake gates",
            "- no more fetch gates unless new capability requires it",
            "- no review-of-review loops",
            "",
            "## v5.0 Progress",
            f"- completed capabilities: {', '.join(completed) if completed else 'none'}",
            "- remaining capabilities:",
        ]
    )
    lines.extend(f"  - {item}" for item in remaining_items) if remaining_items else lines.append("  - none")
    lines.extend(["", "## Blockers"])
    lines.extend(f"- {blocker}" for blocker in result.blockers) if result.blockers else lines.append("- none")
    lines.extend(["", "## Validation Blocked Reasons"])
    lines.extend(f"- {reason}" for reason in result.blocked_reasons) if result.blocked_reasons else lines.append("- none")
    lines.extend(
        [
            "",
            "## Route",
            "manual candidate workspace -> public fetch control plane -> freshness monitor -> candidate intake chain -> Phase 1 real evidence/manual review pipeline -> future dashboard/operator MVP",
            "",
            "## Safety Statements",
            "no network calls",
            "no fetching",
            "no downloading",
            "no writes",
            "no evidence extraction",
            "no evidence verification",
            "no verified evidence promotion",
            "no approval",
            "no trusted asset",
            "no investable asset",
            "no registry mutation",
            "no registry file written",
            "no candidate registry write",
            "no candidate intake file written",
            "no allocation recommendation",
            "no portfolio weight",
            "no buy/sell request",
            "no trade",
            "no executor",
            "no broker/authenticated API",
            "no credentials",
            "no private file ingest",
            "no automatic private data ingest",
            "no fetched data committed",
            "",
            "This report does not claim evidence verification, approval, trust, investability, allocation, buy/sell, trade, registry mutation, candidate registry write, broker API use, credential use, private ingest, automatic evidence extraction, or executor authorization.",
        ]
    )
    return "\n".join(lines)


def build_report_from_path(path: str | Path = DEFAULT_INPUT) -> str:
    return build_operator_status_dashboard_report(load_operator_dashboard_result(path))


def main() -> None:
    parser = argparse.ArgumentParser(description="Print the J.A.R.V.I.S. operator status dashboard report.")
    parser.add_argument("--input", default=str(DEFAULT_INPUT), help="Path to dashboard JSON.")
    args = parser.parse_args()
    print(build_report_from_path(args.input))


if __name__ == "__main__":
    main()
