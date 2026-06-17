"""J.A.R.V.I.S. v72.0 next-safe Python archive execution plan.

Audit-only. No deletion. No archive movement. No file move.

Purpose:
After v71 identified remaining next-safe module/test candidates, build a
conservative paired archive execution plan:
- include only modules that v71 marks next-safe
- include only matching tests for those modules when v71 marks those tests next-safe
- do not include orphan tests for active modules
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from jarvis.runtime.remaining_python_archive_risk_audit import (
    build_remaining_python_archive_risk_audit_result,
)
from jarvis.runtime.safety import build_safety_check_console_output

STATUS_READY = "JARVIS_V72_0_NEXT_SAFE_PYTHON_ARCHIVE_EXECUTION_PLAN_READY_SAFE"
PLAN_READY = "NEXT_SAFE_PYTHON_ARCHIVE_EXECUTION_PLAN_READY"
DEFAULT_ARCHIVE_ROOT = "archive/non_active/v72_next_safe_python_safe"
DEFAULT_OUTPUT_PATH = "outputs/next_safe_python_archive_execution_plan_latest.json"


@dataclass(frozen=True)
class NextSafeArchivePlanItem:
    source_path: str
    proposed_archive_path: str
    item_type: str
    reason: str


@dataclass(frozen=True)
class NextSafePythonArchiveExecutionPlanResult:
    status: str
    plan_status: str
    current_date: str
    archive_root: str
    next_safe_module_source_count: int
    paired_next_safe_test_count: int
    orphan_next_safe_test_not_moved_count: int
    total_plan_item_count: int
    validation_blocked_module_count: int
    validation_blocked_test_count: int
    active_import_closure_count: int
    active_versioned_module_count: int
    unresolved_local_import_count: int
    plan_items: list[dict[str, str]]
    orphan_next_safe_test_not_moved_paths: list[str]
    active_import_closure_paths: list[str]
    validation_imported_module_paths: list[str]
    validation_test_keep_paths: list[str]
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


def _matching_test_path_for_module(module_path: str) -> str:
    stem = Path(module_path).stem
    return f"jarvis/tests/test_{stem}.py"


def build_next_safe_python_archive_execution_plan_result(
    *,
    current_date: str = "2026-06-17",
    archive_root: str = DEFAULT_ARCHIVE_ROOT,
    write_report: bool = False,
    output_path: str | Path = DEFAULT_OUTPUT_PATH,
) -> NextSafePythonArchiveExecutionPlanResult:
    risk = build_remaining_python_archive_risk_audit_result(current_date=current_date)

    active_paths = set(risk.active_import_closure_paths)
    validation_imported = set(risk.validation_imported_module_paths)
    validation_tests = set(risk.validation_test_keep_paths)
    next_safe_modules = sorted(risk.next_safe_module_candidate_paths)
    next_safe_tests = set(risk.next_safe_test_candidate_paths)

    items: list[NextSafeArchivePlanItem] = []
    paired_tests: set[str] = set()

    for module_path in next_safe_modules:
        items.append(
            NextSafeArchivePlanItem(
                source_path=module_path,
                proposed_archive_path=f"{archive_root}/{module_path}",
                item_type="module",
                reason="v71_next_safe_module_not_active_not_validation_imported",
            )
        )

        matching_test = _matching_test_path_for_module(module_path)
        if matching_test in next_safe_tests:
            paired_tests.add(matching_test)
            items.append(
                NextSafeArchivePlanItem(
                    source_path=matching_test,
                    proposed_archive_path=f"{archive_root}/{matching_test}",
                    item_type="test",
                    reason="matching_test_for_v71_next_safe_module",
                )
            )

    orphan_tests = sorted(next_safe_tests - paired_tests)

    blockers: list[str] = []
    seen_sources: set[str] = set()
    seen_destinations: set[str] = set()

    for item in items:
        if item.source_path in seen_sources:
            blockers.append(f"duplicate source path: {item.source_path}")
        seen_sources.add(item.source_path)

        if item.proposed_archive_path in seen_destinations:
            blockers.append(f"duplicate archive path: {item.proposed_archive_path}")
        seen_destinations.add(item.proposed_archive_path)

        if item.source_path in active_paths:
            blockers.append(f"plan item is active runtime path: {item.source_path}")

        if item.item_type == "module" and item.source_path in validation_imported:
            blockers.append(f"module is still imported by validation tests: {item.source_path}")

        if item.item_type == "test" and item.source_path in validation_tests:
            blockers.append(f"test is current validation keep path: {item.source_path}")

        if not item.source_path.startswith("jarvis/"):
            blockers.append(f"unexpected non-jarvis source path: {item.source_path}")

        if not item.proposed_archive_path.startswith(archive_root + "/"):
            blockers.append(f"archive destination outside archive root: {item.proposed_archive_path}")

    warnings = [
        "plan-only stage; no deletion or archive movement is approved by this report",
        "orphan next-safe tests are intentionally not moved in v72 because their modules are not part of this paired plan",
        "run a dedicated reversible archive execution stage before moving these planned files",
    ]

    result = NextSafePythonArchiveExecutionPlanResult(
        status=STATUS_READY,
        plan_status=PLAN_READY if not blockers else "NEXT_SAFE_PYTHON_ARCHIVE_EXECUTION_PLAN_BLOCKED",
        current_date=current_date,
        archive_root=archive_root,
        next_safe_module_source_count=len(next_safe_modules),
        paired_next_safe_test_count=len(paired_tests),
        orphan_next_safe_test_not_moved_count=len(orphan_tests),
        total_plan_item_count=len(items),
        validation_blocked_module_count=risk.validation_blocked_module_count,
        validation_blocked_test_count=risk.validation_blocked_test_count,
        active_import_closure_count=risk.active_import_closure_count,
        active_versioned_module_count=risk.active_versioned_module_count,
        unresolved_local_import_count=risk.unresolved_local_import_count,
        plan_items=[asdict(item) for item in items],
        orphan_next_safe_test_not_moved_paths=orphan_tests,
        active_import_closure_paths=risk.active_import_closure_paths,
        validation_imported_module_paths=risk.validation_imported_module_paths,
        validation_test_keep_paths=risk.validation_test_keep_paths,
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
        result = NextSafePythonArchiveExecutionPlanResult(**payload)

    return result


def format_next_safe_python_archive_execution_plan(
    result: NextSafePythonArchiveExecutionPlanResult,
    *,
    sample_size: int = 80,
) -> str:
    lines = [
        "J.A.R.V.I.S. NEXT-SAFE PYTHON ARCHIVE EXECUTION PLAN",
        f"status: {result.status}",
        f"plan status: {result.plan_status}",
        f"current date: {result.current_date}",
        f"archive root: {result.archive_root}",
        f"next-safe module source count: {result.next_safe_module_source_count}",
        f"paired next-safe test count: {result.paired_next_safe_test_count}",
        f"orphan next-safe test not moved count: {result.orphan_next_safe_test_not_moved_count}",
        f"total plan item count: {result.total_plan_item_count}",
        f"validation-blocked module count: {result.validation_blocked_module_count}",
        f"validation-blocked test count: {result.validation_blocked_test_count}",
        f"active import closure count: {result.active_import_closure_count}",
        f"active versioned module count: {result.active_versioned_module_count}",
        f"unresolved local import count: {result.unresolved_local_import_count}",
        f"report written: {result.report_written}",
        f"report path: {result.report_path}",
        "",
        "PLANNED MOVE SAMPLE:",
    ]

    for item in result.plan_items[:sample_size]:
        lines.append(f"- {item['source_path']} -> {item['proposed_archive_path']} [{item['item_type']}]")

    lines.extend(["", "ORPHAN NEXT-SAFE TESTS NOT MOVED SAMPLE:"])
    lines.extend(f"- {path}" for path in result.orphan_next_safe_test_not_moved_paths[:sample_size])

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
    parser = argparse.ArgumentParser(description="Build the v72 next-safe Python archive execution plan.")
    parser.add_argument("--current-date", default="2026-06-17")
    parser.add_argument("--archive-root", default=DEFAULT_ARCHIVE_ROOT)
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--output-path", default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--safety-check", action="store_true")
    args = parser.parse_args(argv)

    if args.safety_check:
        print(build_safety_check_console_output())
        return 0

    result = build_next_safe_python_archive_execution_plan_result(
        current_date=args.current_date,
        archive_root=args.archive_root,
        write_report=args.write_report,
        output_path=args.output_path,
    )
    print(format_next_safe_python_archive_execution_plan(result))
    return 0 if not result.blockers else 1


__all__ = [
    "DEFAULT_ARCHIVE_ROOT",
    "DEFAULT_OUTPUT_PATH",
    "PLAN_READY",
    "STATUS_READY",
    "NextSafeArchivePlanItem",
    "NextSafePythonArchiveExecutionPlanResult",
    "build_next_safe_python_archive_execution_plan_result",
    "format_next_safe_python_archive_execution_plan",
    "main",
]


if __name__ == "__main__":
    raise SystemExit(main())
