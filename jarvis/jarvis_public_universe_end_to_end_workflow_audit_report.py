"""Markdown report for v4.71 public universe end-to-end workflow audit."""

from __future__ import annotations

import argparse
from pathlib import Path

from .jarvis_public_universe_end_to_end_workflow_audit import (
    PublicUniverseEndToEndWorkflowAuditResult,
    load_public_universe_end_to_end_workflow_audit_result,
)


DEFAULT_INPUT = Path("jarvis/data/jarvis_public_universe_end_to_end_workflow_audit.example.json")


def build_public_universe_end_to_end_workflow_audit_report(result: PublicUniverseEndToEndWorkflowAuditResult) -> str:
    lines = [
        f"# {result.title}",
        "",
        f"version: {result.version}",
        f"overall status: {result.status}",
        f"audit mode: {result.audit_mode or 'missing'}",
        "read-only/default-no-write/no-network/no-fetch/no-broker summary: true",
        "",
        "## Required Stage Order Audit",
        f"- required stage count: {result.required_stage_count}",
        f"- observed stage count: {result.stage_count}",
        f"- missing stage count: {result.missing_stage_count}",
        f"- duplicate stage count: {result.duplicate_stage_count}",
        f"- out-of-order stage count: {result.out_of_order_stage_count}",
        "",
        "## Stage Safety Audit",
        "stage id | version | status | readiness | input | output | blockers | warnings | safety",
        "--- | --- | --- | --- | --- | --- | --- | --- | ---",
    ]
    if result.stage_rows:
        for row in result.stage_rows:
            lines.append(
                f"{row['stage_id']} | {row['version']} | {row['status']} | {row['readiness']} | "
                f"{row['input_count']} | {row['output_count']} | {row['blocker_count']} | {row['warning_count']} | {row['safety_confirmed']}"
            )
    else:
        lines.append("none | none | none | none | 0 | 0 | 0 | 0 | false")
    lines.extend(
        [
            "",
            "## Handoff Audit",
            "handoff | from | to | status | input | output | blockers | warnings",
            "--- | --- | --- | --- | --- | --- | --- | ---",
        ]
    )
    if result.handoff_rows:
        for row in result.handoff_rows:
            lines.append(
                f"{row['handoff_name']} | {row['from_stage_id']} | {row['to_stage_id']} | {row['handoff_status']} | "
                f"{row['input_count']} | {row['output_count']} | {row['blocker_count']} | {row['warning_count']}"
            )
    else:
        lines.append("none | none | none | none | 0 | 0 | 0 | 0")
    counts = result.workflow_counts
    lines.extend(
        [
            "",
            "## Count Coherence Audit",
            f"- source manifest count: {counts.get('source_manifest_count', 0)}",
            f"- fetch plan count: {counts.get('fetch_plan_count', 0)}",
            f"- local cache entry count: {counts.get('local_cache_entry_count', 0)}",
            f"- cache audit entry count: {counts.get('cache_audit_entry_count', 0)}",
            f"- normalized record count: {counts.get('normalized_record_count', 0)}",
            f"- classified record count: {counts.get('classified_record_count', 0)}",
            f"- research queue item count: {counts.get('research_queue_item_count', 0)}",
            f"- evidence pack draft count: {counts.get('evidence_pack_draft_count', 0)}",
            f"- dashboard stage count: {counts.get('dashboard_stage_count', 0)}",
            "",
            "## Workflow Readiness Label",
            f"- {result.workflow_readiness_label}",
            "",
            "## v5 Final Audit Readiness Label",
            f"- {result.v5_final_audit_readiness_label}",
            "",
            "## Blockers / Warnings",
            f"- blocker count: {result.blocker_count}",
            f"- warning count: {result.warning_count}",
            "- blockers: " + (", ".join(result.blockers) if result.blockers else "none"),
            "- warnings: " + (", ".join(result.warnings) if result.warnings else "none"),
            "",
            "## Next Safe Operator Action",
            f"- {result.next_safe_action or 'missing'}",
            "",
            "## Do Not Build Next",
        ]
    )
    lines.extend(f"- {item}" for item in result.do_not_build_next)
    lines.extend(
        [
            "",
            "## Where We Are",
            "- v4.71 audits the complete v4.61-v4.70 public-universe research workflow.",
            "- this is a workflow readiness audit, not a broker dashboard or portfolio dashboard.",
            "",
            "## Where We Need To Go",
            "- next efficient stage is v5.0 Final Research OS MVP Audit.",
            "- v5.0 remains local-first public research OS MVP, not a trading bot.",
            "",
            "## Redundancy Check",
            "- this is not a new pipeline behavior layer.",
            "- this is not fetching, cache writing, evidence extraction, evidence verification, recommendation, approval, allocation, trading, or execution.",
            "",
            "## Remaining Timeline To v5.0",
            "- v5.0 final research OS MVP audit",
            "- no executor exists in v4.71",
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
            "This report does not claim evidence extraction, evidence verification, recommendation, approval, trust, investability, allocation, buy/sell signal, trade, registry mutation, candidate registry write, private ingest, broker integration, or executor authorization.",
        ]
    )
    return "\n".join(lines)


def build_report_from_path(path: str | Path = DEFAULT_INPUT) -> str:
    return build_public_universe_end_to_end_workflow_audit_report(load_public_universe_end_to_end_workflow_audit_result(path))


def main() -> None:
    parser = argparse.ArgumentParser(description="Print the public universe end-to-end workflow audit report.")
    parser.add_argument("--input", default=str(DEFAULT_INPUT), help="Path to public universe e2e workflow audit JSON.")
    args = parser.parse_args()
    print(build_report_from_path(args.input))


if __name__ == "__main__":
    main()
