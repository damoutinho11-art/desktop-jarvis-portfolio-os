"""J.A.R.V.I.S. v77.0 final v5 archive execution plan.

Plan-only. No deletion. No archive movement. No file move.

Purpose:
v76 proved active-runtime replacement coverage exists for the final v5 legacy
modules. v77 builds the exact reversible git-mv plan for the final 12 v5
modules and their 12 direct blocking tests, but does not execute it.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path, PurePosixPath
from typing import Any

from jarvis.runtime.active_runtime_v5_replacement_coverage import (
    COVERAGE_READY,
    build_active_runtime_v5_replacement_coverage_result,
)
from jarvis.runtime.import_closure_safe_archive_plan import (
    build_import_closure_safe_archive_plan_result,
)
from jarvis.runtime.safety import build_safety_check_console_output
from jarvis.runtime.validation_blocked_v5_replacement_plan import (
    build_validation_blocked_v5_replacement_plan_result,
)

STATUS_READY = "JARVIS_V77_0_FINAL_V5_ARCHIVE_EXECUTION_PLAN_READY_SAFE"
PLAN_READY = "FINAL_V5_ARCHIVE_EXECUTION_PLAN_READY"
DEFAULT_ARCHIVE_ROOT = "archive/non_active/v77_final_v5_python_safe"
DEFAULT_OUTPUT_PATH = "outputs/final_v5_archive_execution_plan_latest.json"


@dataclass(frozen=True)
class FinalV5ArchivePlanItem:
    item_type: str
    source_path: str
    destination_path: str
    source_exists: bool
    destination_exists: bool
    already_archived: bool
    pending_move: bool
    recommended_command: str


@dataclass(frozen=True)
class FinalV5ArchiveExecutionPlanResult:
    status: str
    plan_status: str
    current_date: str
    archive_root: str
    plan_unlocked: bool
    execution_performed: bool
    module_source_count: int
    blocking_test_source_count: int
    total_plan_item_count: int
    pending_move_count: int
    already_archived_count: int
    missing_item_count: int
    replacement_record_count: int
    coverage_record_count: int
    covered_record_count: int
    archive_unlocked_record_count: int
    active_import_closure_count: int
    active_runtime_module_count: int
    active_versioned_module_count: int
    unresolved_local_import_count: int
    safety_check_blocked_execution: bool
    plan_items: list[dict[str, Any]]
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


def _archive_destination(source_path: str, archive_root: str) -> str:
    return str(PurePosixPath(archive_root) / PurePosixPath(source_path))


def _build_plan_item(item_type: str, source_path: str, archive_root: str) -> FinalV5ArchivePlanItem:
    destination_path = _archive_destination(source_path, archive_root)
    source_exists = Path(source_path).exists()
    destination_exists = Path(destination_path).exists()
    already_archived = (not source_exists) and destination_exists
    pending_move = source_exists and not destination_exists

    command = f'git mv "{source_path}" "{destination_path}"' if pending_move else "no-op"

    return FinalV5ArchivePlanItem(
        item_type=item_type,
        source_path=source_path,
        destination_path=destination_path,
        source_exists=source_exists,
        destination_exists=destination_exists,
        already_archived=already_archived,
        pending_move=pending_move,
        recommended_command=command,
    )


def build_final_v5_archive_execution_plan_result(
    *,
    current_date: str = "2026-06-17",
    archive_root: str = DEFAULT_ARCHIVE_ROOT,
    write_report: bool = False,
    output_path: str | Path = DEFAULT_OUTPUT_PATH,
) -> FinalV5ArchiveExecutionPlanResult:
    replacement = build_validation_blocked_v5_replacement_plan_result(current_date=current_date)
    coverage = build_active_runtime_v5_replacement_coverage_result(current_date=current_date)
    closure = build_import_closure_safe_archive_plan_result(current_date=current_date)

    active_paths = set(closure.get("active_import_closure_paths", []))

    module_paths: list[str] = []
    blocking_test_paths: list[str] = []

    for record in replacement.replacement_records:
        module_path = record["legacy_module_path"]
        module_paths.append(module_path)
        blocking_test_paths.extend(record["blocking_test_paths"])

    module_paths = sorted(set(module_paths))
    blocking_test_paths = sorted(set(blocking_test_paths))

    items: list[FinalV5ArchivePlanItem] = []
    items.extend(_build_plan_item("legacy_v5_module", path, archive_root) for path in module_paths)
    items.extend(_build_plan_item("legacy_v5_blocking_test", path, archive_root) for path in blocking_test_paths)

    blockers: list[str] = []

    if replacement.blockers:
        blockers.extend(f"v75 replacement blocker: {blocker}" for blocker in replacement.blockers)

    if coverage.blockers:
        blockers.extend(f"v76 coverage blocker: {blocker}" for blocker in coverage.blockers)

    if coverage.coverage_status != COVERAGE_READY:
        blockers.append("v76 coverage is not ready")

    if coverage.covered_record_count != coverage.coverage_record_count:
        blockers.append("not every v76 replacement coverage record is covered")

    if coverage.unresolved_local_import_count != 0:
        blockers.append("v76 coverage has unresolved local imports")

    if not coverage.safety_check_blocked_execution:
        blockers.append("v76 safety-check did not block execution")

    if closure.get("unresolved_local_import_count") != 0:
        blockers.append("active import closure has unresolved local imports")

    for path in module_paths:
        if not path.startswith("jarvis/jarvis_v5"):
            blockers.append(f"unexpected non-v5 module in final archive plan: {path}")

    for item in items:
        if item.source_path in active_paths:
            blockers.append(f"planned source is active runtime path: {item.source_path}")
        if not item.source_exists and not item.destination_exists:
            blockers.append(f"planned item is missing from source and archive destination: {item.source_path}")

    pending = sum(1 for item in items if item.pending_move)
    already_archived = sum(1 for item in items if item.already_archived)
    missing = sum(1 for item in items if (not item.source_exists and not item.destination_exists))

    plan_unlocked = not blockers and bool(items)

    warnings = [
        "plan-only stage; no deletion or archive movement is performed",
        "execute only in a later dedicated reversible git-mv stage",
        "final v5 archive must preserve rollback through Git history",
        "approval ticket drift and generated reports must be restored or ignored before commit",
    ]

    result = FinalV5ArchiveExecutionPlanResult(
        status=STATUS_READY,
        plan_status=PLAN_READY if not blockers else "FINAL_V5_ARCHIVE_EXECUTION_PLAN_BLOCKED",
        current_date=current_date,
        archive_root=archive_root,
        plan_unlocked=plan_unlocked,
        execution_performed=False,
        module_source_count=len(module_paths),
        blocking_test_source_count=len(blocking_test_paths),
        total_plan_item_count=len(items),
        pending_move_count=pending,
        already_archived_count=already_archived,
        missing_item_count=missing,
        replacement_record_count=replacement.replacement_record_count,
        coverage_record_count=coverage.coverage_record_count,
        covered_record_count=coverage.covered_record_count,
        archive_unlocked_record_count=coverage.archive_unlocked_record_count,
        active_import_closure_count=closure.get("active_import_closure_count", 0),
        active_runtime_module_count=closure.get("active_runtime_module_count", 0),
        active_versioned_module_count=closure.get("active_versioned_module_count", 0),
        unresolved_local_import_count=closure.get("unresolved_local_import_count", -1),
        safety_check_blocked_execution=coverage.safety_check_blocked_execution,
        plan_items=[asdict(item) for item in items],
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
        result = FinalV5ArchiveExecutionPlanResult(**payload)

    return result


def format_final_v5_archive_execution_plan(result: FinalV5ArchiveExecutionPlanResult) -> str:
    lines = [
        "J.A.R.V.I.S. FINAL V5 ARCHIVE EXECUTION PLAN",
        f"status: {result.status}",
        f"plan status: {result.plan_status}",
        f"current date: {result.current_date}",
        f"archive root: {result.archive_root}",
        f"plan unlocked: {result.plan_unlocked}",
        f"execution performed: {result.execution_performed}",
        f"module source count: {result.module_source_count}",
        f"blocking test source count: {result.blocking_test_source_count}",
        f"total plan item count: {result.total_plan_item_count}",
        f"pending move count: {result.pending_move_count}",
        f"already archived count: {result.already_archived_count}",
        f"missing item count: {result.missing_item_count}",
        f"replacement record count: {result.replacement_record_count}",
        f"coverage record count: {result.coverage_record_count}",
        f"covered record count: {result.covered_record_count}",
        f"archive unlocked record count: {result.archive_unlocked_record_count}",
        f"active import closure count: {result.active_import_closure_count}",
        f"active runtime module count: {result.active_runtime_module_count}",
        f"active versioned module count: {result.active_versioned_module_count}",
        f"unresolved local import count: {result.unresolved_local_import_count}",
        f"safety-check blocked execution: {result.safety_check_blocked_execution}",
        f"report written: {result.report_written}",
        f"report path: {result.report_path}",
        "",
        "PLAN ITEMS:",
    ]

    for item in result.plan_items:
        lines.append(f"- {item['source_path']}")
        lines.append(f"  type: {item['item_type']}")
        lines.append(f"  destination: {item['destination_path']}")
        lines.append(f"  pending move: {item['pending_move']}")
        lines.append(f"  already archived: {item['already_archived']}")

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
    parser = argparse.ArgumentParser(description="Build the v77 final v5 archive execution plan.")
    parser.add_argument("--current-date", default="2026-06-17")
    parser.add_argument("--archive-root", default=DEFAULT_ARCHIVE_ROOT)
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--output-path", default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--safety-check", action="store_true")
    args = parser.parse_args(argv)

    if args.safety_check:
        print(build_safety_check_console_output())
        return 0

    result = build_final_v5_archive_execution_plan_result(
        current_date=args.current_date,
        archive_root=args.archive_root,
        write_report=args.write_report,
        output_path=args.output_path,
    )
    print(format_final_v5_archive_execution_plan(result))
    return 0 if not result.blockers else 1


__all__ = [
    "DEFAULT_ARCHIVE_ROOT",
    "DEFAULT_OUTPUT_PATH",
    "PLAN_READY",
    "STATUS_READY",
    "FinalV5ArchiveExecutionPlanResult",
    "FinalV5ArchivePlanItem",
    "build_final_v5_archive_execution_plan_result",
    "format_final_v5_archive_execution_plan",
    "main",
]


if __name__ == "__main__":
    raise SystemExit(main())
