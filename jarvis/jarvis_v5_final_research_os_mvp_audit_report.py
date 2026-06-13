"""Markdown report for v5.0 Final Research OS MVP Audit."""

from __future__ import annotations

import argparse
from pathlib import Path

from .jarvis_v5_final_research_os_mvp_audit import (
    V5FinalResearchOSMVPAuditResult,
    load_v5_final_research_os_mvp_audit_result,
)


DEFAULT_INPUT = Path("jarvis/data/jarvis_v5_final_research_os_mvp_audit.example.json")


def build_v5_final_research_os_mvp_audit_report(result: V5FinalResearchOSMVPAuditResult) -> str:
    lines = [
        f"# {result.title}",
        "",
        f"version: {result.version}",
        f"overall status: {result.status}",
        f"release candidate label: {result.release_candidate_label}",
        f"final verdict: {result.final_verdict}",
        f"MVP readiness label: {result.mvp_readiness_label}",
        f"product definition: {result.product_definition or 'missing'}",
        "read-only/default-no-write/no-network/no-fetch/no-broker summary: true",
        "",
        "## Required Stage Chain Audit",
        f"- required stage count: {result.required_stage_count}",
        f"- present stage count: {result.present_stage_count}",
        f"- missing stage count: {result.missing_stage_count}",
        f"- duplicate stage count: {result.duplicate_stage_count}",
        f"- out-of-order stage count: {result.out_of_order_stage_count}",
        "stage id | status | ready | blockers | warnings | safety",
        "--- | --- | --- | --- | --- | ---",
    ]
    if result.stage_rows:
        for row in result.stage_rows:
            lines.append(
                f"{row['stage_id']} | {row['status']} | {row['ready']} | "
                f"{row['blocker_count']} | {row['warning_count']} | {row['safety_confirmed']}"
            )
    else:
        lines.append("none | none | false | 0 | 0 | false")
    lines.extend(
        [
            "",
            "## Capability Matrix Audit",
            f"- required present capability count: {result.required_capability_count}",
            f"- present capability count: {result.present_capability_count}",
            f"- forbidden capability violation count: {result.forbidden_capability_violation_count}",
            "capability | required state | present | violation",
            "--- | --- | --- | ---",
        ]
    )
    for row in result.capability_rows:
        lines.append(f"{row['capability_id']} | {row['required_state']} | {row['present']} | {row['violation']}")
    lines.extend(
        [
            "",
            "## Final Audit Area Summary",
            f"- final audit area count: {result.final_audit_area_count}",
            f"- ready area count: {result.ready_area_count}",
            f"- partial area count: {result.partial_area_count}",
            f"- blocked area count: {result.blocked_area_count}",
            "area | status | ready | blockers | warnings | safety",
            "--- | --- | --- | --- | --- | ---",
        ]
    )
    if result.final_audit_area_rows:
        for row in result.final_audit_area_rows:
            lines.append(
                f"{row['area']} | {row['status']} | {row['ready']} | "
                f"{row['blocker_count']} | {row['warning_count']} | {row['safety_confirmed']}"
            )
    else:
        lines.append("none | none | false | 0 | 0 | false")
    lines.extend(
        [
            "",
            "## Public Universe E2E Summary",
            f"- public universe e2e status: {result.public_universe_e2e_status}",
            "",
            "## Manual Trust / Manual Approval / No Execution Summary",
            f"- phase1 safety status: {result.phase1_safety_status}",
            f"- manual trust boundary status: {result.manual_trust_boundary_status}",
            f"- manual approval boundary status: {result.manual_approval_boundary_status}",
            f"- no execution boundary status: {result.no_execution_boundary_status}",
            f"- local-first boundary status: {result.local_first_boundary_status}",
            "",
            "## Blockers / Warnings",
            f"- blocker count: {result.blocker_count}",
            f"- warning count: {result.warning_count}",
            "- blockers: " + (", ".join(result.blockers) if result.blockers else "none"),
            "- warnings: " + (", ".join(result.warnings) if result.warnings else "none"),
            "",
            "## Out Of Scope After v5",
        ]
    )
    lines.extend(f"- {item}" for item in result.out_of_scope_after_v5)
    lines.extend(
        [
            "",
            "## Recommended Next Phase",
            f"- {result.recommended_next_phase or 'v5.1 Real Public Source Fixture Wiring / Operator Runbook'}",
            "",
            "## Do Not Build Next",
        ]
    )
    lines.extend(f"- {item}" for item in result.do_not_build_next)
    lines.extend(
        [
            "",
            "## Where We Are",
            "- J.A.R.V.I.S. v5.0 is a local-first public research OS MVP audit seal.",
            "- the MVP prepares public research artifacts and operator status views.",
            "- manual trust and manual approval remain outside automation.",
            "",
            "## Where We Need To Go",
            "- v5.1 can wire real public source fixtures and an operator runbook without broker execution.",
            "- future work must preserve no verification, no approval, no recommendation, no allocation, and no execution boundaries unless separately and explicitly reviewed.",
            "",
            "## v5.0 Release Statement",
            "- v5.0 release readiness means research OS MVP readiness, not investability or trading readiness.",
            "- no executor exists in v5.0.",
            "",
            "## Safety Statements",
            "no network calls",
            "no fetching",
            "no downloading",
            "no scraping",
            "no API calls",
            "no browser automation",
            "no subprocess execution",
            "no scheduler creation",
            "no broker integration",
            "no Lightyear integration",
            "no LHV integration",
            "no crypto exchange integration",
            "no credentials",
            "no private/account data ingest",
            "no evidence extraction",
            "no evidence verification",
            "no verified evidence promotion",
            "no investment screening",
            "no research scoring based on expected returns",
            "no ranking by investment merit",
            "no recommendation",
            "no approval",
            "no trusted asset",
            "no investable asset",
            "no registry mutation",
            "no candidate registry write",
            "no allocation recommendation",
            "no portfolio weight",
            "no buy/sell signal",
            "no trade",
            "no executor",
            "final real-world purchases remain manual and external",
            "",
            "This report does not claim evidence extraction, evidence verification, recommendation, approval, trust, investability, allocation, buy/sell signal, trade, registry mutation, candidate registry write, broker integration, or executor authorization.",
        ]
    )
    return "\n".join(lines)


def build_report_from_path(path: str | Path = DEFAULT_INPUT) -> str:
    return build_v5_final_research_os_mvp_audit_report(load_v5_final_research_os_mvp_audit_result(path))


def main() -> None:
    parser = argparse.ArgumentParser(description="Print the v5.0 Final Research OS MVP Audit report.")
    parser.add_argument("--input", default=str(DEFAULT_INPUT), help="Path to v5.0 final audit JSON.")
    args = parser.parse_args()
    print(build_report_from_path(args.input))


if __name__ == "__main__":
    main()
