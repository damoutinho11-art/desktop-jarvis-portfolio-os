"""J.A.R.V.I.S. v78.0 final v5 archive execution verification.

This stage verifies the reversible git-mv archive of the final v5 legacy
modules and their direct blocking tests. It does not delete files and does not
change runtime behavior, allocation, approval, broker, order, or trade paths.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from jarvis.runtime.final_v5_archive_execution_plan import (
    DEFAULT_ARCHIVE_ROOT,
    build_final_v5_archive_execution_plan_result,
)
from jarvis.runtime.import_closure_safe_archive_plan import (
    build_import_closure_safe_archive_plan_result,
)
from jarvis.runtime.safety import build_safety_check_console_output

STATUS_READY = "JARVIS_V78_0_FINAL_V5_ARCHIVE_EXECUTION_READY_SAFE"
EXECUTION_READY = "FINAL_V5_ARCHIVE_EXECUTION_READY"
DEFAULT_OUTPUT_PATH = "outputs/final_v5_archive_execution_latest.json"


@dataclass(frozen=True)
class FinalV5ArchiveExecutionResult:
    status: str
    execution_status: str
    current_date: str
    archive_root: str
    execution_verified: bool
    total_plan_item_count: int
    pending_move_count: int
    already_archived_count: int
    missing_item_count: int
    active_import_closure_count: int
    active_runtime_module_count: int
    active_versioned_module_count: int
    unresolved_local_import_count: int
    safety_check_blocked_execution: bool
    archived_items: list[dict[str, Any]]
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


def build_final_v5_archive_execution_result(
    *,
    current_date: str = "2026-06-17",
    write_report: bool = False,
    output_path: str | Path = DEFAULT_OUTPUT_PATH,
) -> FinalV5ArchiveExecutionResult:
    plan = build_final_v5_archive_execution_plan_result(current_date=current_date)
    closure = build_import_closure_safe_archive_plan_result(current_date=current_date)

    safety_output = build_safety_check_console_output()
    safety_blocked = "BLOCKED:" in safety_output and "No execution action was taken" in safety_output

    blockers: list[str] = []

    if plan.blockers:
        blockers.extend(f"v77 plan blocker: {blocker}" for blocker in plan.blockers)

    if plan.total_plan_item_count != 24:
        blockers.append(f"expected 24 final v5 plan items, got {plan.total_plan_item_count}")

    if plan.pending_move_count != 0:
        blockers.append(f"expected 0 pending moves after v78 execution, got {plan.pending_move_count}")

    if plan.already_archived_count != 24:
        blockers.append(f"expected 24 already archived items, got {plan.already_archived_count}")

    if plan.missing_item_count != 0:
        blockers.append(f"expected 0 missing items, got {plan.missing_item_count}")

    if closure.get("unresolved_local_import_count") != 0:
        blockers.append("active import closure has unresolved local imports")

    if not safety_blocked:
        blockers.append("safety-check did not block execution")

    archived_items = [item for item in plan.plan_items if item.get("already_archived")]

    warnings = [
        "final v5 archive was executed as reversible git mv, not deletion",
        "archive movement is intentionally true for this execution verification stage",
        "runtime, allocation, approval, broker, order, and trade behavior remain unchanged",
    ]

    result = FinalV5ArchiveExecutionResult(
        status=STATUS_READY,
        execution_status=EXECUTION_READY if not blockers else "FINAL_V5_ARCHIVE_EXECUTION_BLOCKED",
        current_date=current_date,
        archive_root=DEFAULT_ARCHIVE_ROOT,
        execution_verified=not blockers,
        total_plan_item_count=plan.total_plan_item_count,
        pending_move_count=plan.pending_move_count,
        already_archived_count=plan.already_archived_count,
        missing_item_count=plan.missing_item_count,
        active_import_closure_count=closure.get("active_import_closure_count", 0),
        active_runtime_module_count=closure.get("active_runtime_module_count", 0),
        active_versioned_module_count=closure.get("active_versioned_module_count", 0),
        unresolved_local_import_count=closure.get("unresolved_local_import_count", -1),
        safety_check_blocked_execution=safety_blocked,
        archived_items=archived_items,
        deletion_performed=False,
        archive_performed=True,
        file_move_performed=True,
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
        result = FinalV5ArchiveExecutionResult(**payload)

    return result


def format_final_v5_archive_execution(result: FinalV5ArchiveExecutionResult) -> str:
    lines = [
        "J.A.R.V.I.S. FINAL V5 ARCHIVE EXECUTION",
        f"status: {result.status}",
        f"execution status: {result.execution_status}",
        f"current date: {result.current_date}",
        f"archive root: {result.archive_root}",
        f"execution verified: {result.execution_verified}",
        f"total plan item count: {result.total_plan_item_count}",
        f"pending move count: {result.pending_move_count}",
        f"already archived count: {result.already_archived_count}",
        f"missing item count: {result.missing_item_count}",
        f"active import closure count: {result.active_import_closure_count}",
        f"active runtime module count: {result.active_runtime_module_count}",
        f"active versioned module count: {result.active_versioned_module_count}",
        f"unresolved local import count: {result.unresolved_local_import_count}",
        f"safety-check blocked execution: {result.safety_check_blocked_execution}",
        f"report written: {result.report_written}",
        f"report path: {result.report_path}",
        "",
        "ARCHIVED ITEM SAMPLE:",
    ]

    for item in result.archived_items[:24]:
        lines.append(f"- {item['destination_path']}")

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
    parser = argparse.ArgumentParser(description="Verify the v78 final v5 archive execution.")
    parser.add_argument("--current-date", default="2026-06-17")
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--output-path", default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--safety-check", action="store_true")
    args = parser.parse_args(argv)

    if args.safety_check:
        print(build_safety_check_console_output())
        return 0

    result = build_final_v5_archive_execution_result(
        current_date=args.current_date,
        write_report=args.write_report,
        output_path=args.output_path,
    )
    print(format_final_v5_archive_execution(result))
    return 0 if not result.blockers else 1


__all__ = [
    "DEFAULT_OUTPUT_PATH",
    "EXECUTION_READY",
    "STATUS_READY",
    "FinalV5ArchiveExecutionResult",
    "build_final_v5_archive_execution_result",
    "format_final_v5_archive_execution",
    "main",
]


if __name__ == "__main__":
    raise SystemExit(main())
