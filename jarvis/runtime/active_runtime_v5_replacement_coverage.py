"""J.A.R.V.I.S. v76.0 active-runtime v5 replacement coverage pack.

Audit-only. No deletion. No archive movement. No file move.

Purpose:
v75 mapped the final validation-blocked v5 modules to replacement coverage.
v76 proves that active-runtime facade coverage exists for those replacement
areas before any final v5 legacy archive is considered.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from jarvis.runtime.import_closure_safe_archive_plan import (
    build_import_closure_safe_archive_plan_result,
)
from jarvis.runtime.safety import build_safety_check_console_output
from jarvis.runtime.validation_blocked_v5_replacement_plan import (
    build_validation_blocked_v5_replacement_plan_result,
)

STATUS_READY = "JARVIS_V76_0_ACTIVE_RUNTIME_V5_REPLACEMENT_COVERAGE_READY_SAFE"
COVERAGE_READY = "ACTIVE_RUNTIME_V5_REPLACEMENT_COVERAGE_READY"
DEFAULT_OUTPUT_PATH = "outputs/active_runtime_v5_replacement_coverage_latest.json"


@dataclass(frozen=True)
class ActiveRuntimeV5ReplacementCoverageRecord:
    coverage_area: str
    replaces_legacy_categories: list[str]
    active_runtime_evidence: list[str]
    covered: bool
    archive_unlocked: bool
    reason: str


@dataclass(frozen=True)
class ActiveRuntimeV5ReplacementCoverageResult:
    status: str
    coverage_status: str
    current_date: str
    replacement_record_count: int
    coverage_record_count: int
    covered_record_count: int
    archive_unlocked_record_count: int
    validation_blocked_module_count: int
    remaining_non_active_versioned_module_count: int
    active_import_closure_count: int
    active_runtime_module_count: int
    active_versioned_module_count: int
    unresolved_local_import_count: int
    safety_check_blocked_execution: bool
    coverage_records: list[dict[str, Any]]
    deletion_performed: bool
    archive_performed: bool
    file_move_performed: bool
    runtime_behavior_mutation: bool
    allocation_mutation: bool
    approval_ticket_mutation: bool
    buy_request_created: bool
    broker_connection: bool
    credentials_used: bool
    private_account_data_ingestion: bool
    order_created: bool
    trade_executed: bool
    warnings: list[str]
    blockers: list[str]
    report_written: bool
    report_path: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _path_present(paths: set[str], suffix: str) -> bool:
    return any(path.endswith(suffix) for path in paths)


def _gitignore_contains(line: str) -> bool:
    path = Path(".gitignore")
    if not path.exists():
        return False
    return line in path.read_text(encoding="utf-8", errors="replace").splitlines()


def build_active_runtime_v5_replacement_coverage_result(
    *,
    current_date: str = "2026-06-17",
    write_report: bool = False,
    output_path: str | Path = DEFAULT_OUTPUT_PATH,
) -> ActiveRuntimeV5ReplacementCoverageResult:
    replacement = build_validation_blocked_v5_replacement_plan_result(current_date=current_date)
    closure = build_import_closure_safe_archive_plan_result(current_date=current_date)

    active_paths = set(closure.get("active_import_closure_paths", []))
    safety_output = build_safety_check_console_output()
    safety_blocked = "BLOCKED:" in safety_output and "No execution action was taken" in safety_output

    records: list[ActiveRuntimeV5ReplacementCoverageRecord] = []

    platform_coverage = (
        _path_present(active_paths, "jarvis/runtime/platform_data_completeness_gate.py")
        and _path_present(active_paths, "jarvis/runtime/platform_lane_policy.py")
    )
    records.append(
        ActiveRuntimeV5ReplacementCoverageRecord(
            coverage_area="public_source_and_platform_intake_boundary",
            replaces_legacy_categories=["historical_public_source_fixture_wiring"],
            active_runtime_evidence=[
                "platform_data_completeness_gate is in active import closure",
                "platform_lane_policy is in active import closure",
                "local/private templates remain separated from active runtime execution",
            ],
            covered=platform_coverage,
            archive_unlocked=False,
            reason="covers v5 fixture wiring intent through active platform intake boundary",
        )
    )

    evidence_coverage = (
        _path_present(active_paths, "jarvis/jarvis_v43_0_free_research_api_router_weekly_policy.py")
        and _path_present(active_paths, "jarvis/jarvis_v44_0_free_research_api_fetcher_adapters_local_cache.py")
        and _path_present(active_paths, "jarvis/jarvis_v45_0_free_research_cache_evidence_pack_bridge.py")
    )
    records.append(
        ActiveRuntimeV5ReplacementCoverageRecord(
            coverage_area="free_research_cache_and_evidence_bridge",
            replaces_legacy_categories=[
                "historical_real_fixture_import_dry_run",
                "historical_research_draft_source_router",
                "historical_public_research_packet_assembler",
            ],
            active_runtime_evidence=[
                "v43 free research API router remains in active closure",
                "v44 free research cache adapter remains in active closure",
                "v45 evidence pack bridge remains in active closure",
            ],
            covered=evidence_coverage,
            archive_unlocked=False,
            reason="covers v5 research/source packet intent through current evidence bridge",
        )
    )

    weekly_manual_coverage = (
        _path_present(active_paths, "jarvis/runtime/weekly_packet.py")
        and _path_present(active_paths, "jarvis/runtime/platform_weekly_action_packet.py")
        and _path_present(active_paths, "jarvis/runtime/personal_finance_contribution_bridge.py")
    )
    records.append(
        ActiveRuntimeV5ReplacementCoverageRecord(
            coverage_area="manual_review_weekly_packet_and_no_auto_approval",
            replaces_legacy_categories=["historical_operator_fixture_review_queue"],
            active_runtime_evidence=[
                "weekly_packet is in active import closure",
                "platform_weekly_action_packet is in active import closure",
                "personal_finance_contribution_bridge is in active import closure",
            ],
            covered=weekly_manual_coverage,
            archive_unlocked=False,
            reason="covers v5 manual review queue intent through current weekly/manual packet facade",
        )
    )

    report_output_coverage = (
        _gitignore_contains("outputs/validation_blocked_v5_replacement_plan_latest.json")
        and _gitignore_contains("outputs/validation_blocked_legacy_candidate_decoupling_audit_latest.json")
        and _gitignore_contains("outputs/next_safe_python_archive_execution_plan_latest.json")
    )
    records.append(
        ActiveRuntimeV5ReplacementCoverageRecord(
            coverage_area="explicit_report_output_and_ignored_generated_files",
            replaces_legacy_categories=["historical_v5_report_module"],
            active_runtime_evidence=[
                "v75 generated report output is ignored",
                "v74 generated report output is ignored",
                "v72 generated report output is ignored",
            ],
            covered=report_output_coverage,
            archive_unlocked=False,
            reason="covers v5 report-module intent through explicit active report outputs",
        )
    )

    final_audit_coverage = (
        closure.get("unresolved_local_import_count") == 0
        and safety_blocked
        and _path_present(active_paths, "jarvis/runtime/import_closure_safe_archive_plan.py")
        and _path_present(active_paths, "jarvis/runtime/safety.py")
    )
    records.append(
        ActiveRuntimeV5ReplacementCoverageRecord(
            coverage_area="import_closure_and_execution_safety_facade",
            replaces_legacy_categories=["historical_final_research_os_mvp_audit"],
            active_runtime_evidence=[
                "active import closure has zero unresolved local imports",
                "stable runtime safety facade blocks execution commands",
                "import_closure_safe_archive_plan remains in active import closure",
            ],
            covered=final_audit_coverage,
            archive_unlocked=False,
            reason="covers v5 final MVP audit intent through active closure and safety facade",
        )
    )

    blockers: list[str] = []
    if replacement.blockers:
        blockers.extend(f"v75 replacement blocker: {blocker}" for blocker in replacement.blockers)
    if closure.get("unresolved_local_import_count") != 0:
        blockers.append("active import closure has unresolved imports")
    if not safety_blocked:
        blockers.append("safety-check did not block execution")
    for record in records:
        if not record.covered:
            blockers.append(f"missing active-runtime replacement coverage: {record.coverage_area}")

    warnings = [
        "coverage-only stage; no deletion or archive movement is approved",
        "archive_unlocked remains false even when replacement coverage is present",
        "final v5 archive still requires a dedicated reversible archive plan and execution stage",
    ]

    result = ActiveRuntimeV5ReplacementCoverageResult(
        status=STATUS_READY,
        coverage_status=COVERAGE_READY if not blockers else "ACTIVE_RUNTIME_V5_REPLACEMENT_COVERAGE_BLOCKED",
        current_date=current_date,
        replacement_record_count=replacement.replacement_record_count,
        coverage_record_count=len(records),
        covered_record_count=sum(1 for record in records if record.covered),
        archive_unlocked_record_count=sum(1 for record in records if record.archive_unlocked),
        validation_blocked_module_count=replacement.validation_blocked_module_count,
        remaining_non_active_versioned_module_count=replacement.remaining_non_active_versioned_module_count,
        active_import_closure_count=closure.get("active_import_closure_count", 0),
        active_runtime_module_count=closure.get("active_runtime_module_count", 0),
        active_versioned_module_count=closure.get("active_versioned_module_count", 0),
        unresolved_local_import_count=closure.get("unresolved_local_import_count", -1),
        safety_check_blocked_execution=safety_blocked,
        coverage_records=[asdict(record) for record in records],
        deletion_performed=False,
        archive_performed=False,
        file_move_performed=False,
        runtime_behavior_mutation=False,
        allocation_mutation=False,
        approval_ticket_mutation=False,
        buy_request_created=False,
        broker_connection=False,
        credentials_used=False,
        private_account_data_ingestion=False,
        order_created=False,
        trade_executed=False,
        warnings=warnings,
        blockers=blockers,
        report_written=False,
        report_path=str(output_path),
    )

    if write_report:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = result.to_dict()
        payload["report_written"] = True
        path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        result = ActiveRuntimeV5ReplacementCoverageResult(**payload)

    return result


def format_active_runtime_v5_replacement_coverage(
    result: ActiveRuntimeV5ReplacementCoverageResult,
) -> str:
    lines = [
        "J.A.R.V.I.S. ACTIVE RUNTIME V5 REPLACEMENT COVERAGE PACK",
        f"status: {result.status}",
        f"coverage status: {result.coverage_status}",
        f"current date: {result.current_date}",
        f"replacement record count: {result.replacement_record_count}",
        f"coverage record count: {result.coverage_record_count}",
        f"covered record count: {result.covered_record_count}",
        f"archive unlocked record count: {result.archive_unlocked_record_count}",
        f"validation-blocked module count: {result.validation_blocked_module_count}",
        f"remaining non-active versioned module count: {result.remaining_non_active_versioned_module_count}",
        f"active import closure count: {result.active_import_closure_count}",
        f"active runtime module count: {result.active_runtime_module_count}",
        f"active versioned module count: {result.active_versioned_module_count}",
        f"unresolved local import count: {result.unresolved_local_import_count}",
        f"safety-check blocked execution: {result.safety_check_blocked_execution}",
        f"report written: {result.report_written}",
        f"report path: {result.report_path}",
        "",
        "COVERAGE RECORDS:",
    ]

    for record in result.coverage_records:
        lines.append(f"- {record['coverage_area']}")
        lines.append(f"  covered: {record['covered']}")
        lines.append(f"  archive unlocked: {record['archive_unlocked']}")
        lines.append("  replaces:")
        for category in record["replaces_legacy_categories"]:
            lines.append(f"  - {category}")
        lines.append("  evidence:")
        for evidence in record["active_runtime_evidence"]:
            lines.append(f"  - {evidence}")

    lines.extend(
        [
            "",
            "Safety:",
            f"- deletion performed: {result.deletion_performed}",
            f"- archive performed: {result.archive_performed}",
            f"- file move performed: {result.file_move_performed}",
            f"- runtime behavior mutation: {result.runtime_behavior_mutation}",
            f"- allocation mutation: {result.allocation_mutation}",
            f"- approval ticket mutation: {result.approval_ticket_mutation}",
            f"- buy request created: {result.buy_request_created}",
            f"- broker connection: {result.broker_connection}",
            f"- credentials used: {result.credentials_used}",
            f"- private account data ingestion: {result.private_account_data_ingestion}",
            f"- order created: {result.order_created}",
            f"- trade executed: {result.trade_executed}",
            "warnings:",
        ]
    )
    lines.extend(f"- {warning}" for warning in result.warnings)
    lines.extend(["blockers:"] + [f"- {blocker}" for blocker in result.blockers or ["none"]])

    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build the v76 active-runtime v5 replacement coverage pack.")
    parser.add_argument("--current-date", default="2026-06-17")
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--output-path", default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--safety-check", action="store_true")
    args = parser.parse_args(argv)

    if args.safety_check:
        print(build_safety_check_console_output())
        return 0

    result = build_active_runtime_v5_replacement_coverage_result(
        current_date=args.current_date,
        write_report=args.write_report,
        output_path=args.output_path,
    )
    print(format_active_runtime_v5_replacement_coverage(result))
    return 0 if not result.blockers else 1


__all__ = [
    "COVERAGE_READY",
    "DEFAULT_OUTPUT_PATH",
    "STATUS_READY",
    "ActiveRuntimeV5ReplacementCoverageRecord",
    "ActiveRuntimeV5ReplacementCoverageResult",
    "build_active_runtime_v5_replacement_coverage_result",
    "format_active_runtime_v5_replacement_coverage",
    "main",
]


if __name__ == "__main__":
    raise SystemExit(main())
