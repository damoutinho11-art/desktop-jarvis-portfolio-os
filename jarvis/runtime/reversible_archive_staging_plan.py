"""J.A.R.V.I.S. v69.0 reversible archive staging plan.

Audit-only plan. No deletion. No file moves. No archive execution.
Purpose: create a conservative, reversible archive plan for the safest first
cleanup bucket: non-active legacy *_report.py modules and matching tests.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from jarvis.runtime.non_active_archive_candidate_report import (
    build_non_active_archive_candidate_report_result,
)
from jarvis.runtime.safety import build_safety_check_console_output

STATUS_READY = "JARVIS_V69_0_REVERSIBLE_ARCHIVE_STAGING_PLAN_READY_SAFE"
PLAN_READY = "REVERSIBLE_ARCHIVE_STAGING_PLAN_READY"
DEFAULT_OUTPUT_PATH = "outputs/reversible_archive_staging_plan_latest.json"
DEFAULT_ARCHIVE_ROOT = "archive/non_active/v69_report_only_python"


@dataclass(frozen=True)
class ArchivePlanItem:
    source_path: str
    proposed_archive_path: str
    category: str
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ReversibleArchiveStagingPlanResult:
    status: str
    plan_status: str
    current_date: str
    archive_root: str
    active_import_closure_count: int
    validation_test_keep_count: int
    non_active_versioned_module_count: int
    archive_candidate_test_count: int
    non_active_data_config_candidate_count: int
    report_only_module_candidate_count: int
    report_only_test_candidate_count: int
    total_plan_item_count: int
    plan_items: list[dict[str, Any]]
    unresolved_local_import_count: int
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


def _is_report_python(path: str) -> bool:
    return path.endswith("_report.py")


def _archive_path(source_path: str, archive_root: str) -> str:
    return str(Path(archive_root) / source_path).replace("\\", "/")


def _build_plan_items(
    *,
    module_paths: list[str],
    test_paths: list[str],
    archive_root: str,
) -> list[ArchivePlanItem]:
    items: list[ArchivePlanItem] = []

    for path in module_paths:
        if _is_report_python(path):
            items.append(
                ArchivePlanItem(
                    source_path=path,
                    proposed_archive_path=_archive_path(path, archive_root),
                    category="non_active_legacy_report_module",
                    reason="non-active versioned *_report.py module outside current active runtime import closure",
                )
            )

    for path in test_paths:
        if _is_report_python(path):
            items.append(
                ArchivePlanItem(
                    source_path=path,
                    proposed_archive_path=_archive_path(path, archive_root),
                    category="non_active_legacy_report_test",
                    reason="non-active versioned *_report.py test outside current active runtime validation keep set",
                )
            )

    return sorted(items, key=lambda item: item.source_path)


def build_reversible_archive_staging_plan_result(
    *,
    current_date: str = "2026-06-17",
    archive_root: str = DEFAULT_ARCHIVE_ROOT,
    write_report: bool = False,
    output_path: str | Path = DEFAULT_OUTPUT_PATH,
) -> ReversibleArchiveStagingPlanResult:
    report = build_non_active_archive_candidate_report_result(current_date=current_date)

    items = _build_plan_items(
        module_paths=report.non_active_versioned_module_paths,
        test_paths=report.archive_candidate_test_paths,
        archive_root=archive_root,
    )

    active_keep = set(report.active_runtime_keep_paths)
    validation_keep = set(report.validation_test_keep_paths)

    blockers: list[str] = []
    for item in items:
        if item.source_path in active_keep:
            blockers.append(f"planned archive item is active runtime keep path: {item.source_path}")
        if item.source_path in validation_keep:
            blockers.append(f"planned archive item is validation keep path: {item.source_path}")

    source_paths = [item.source_path for item in items]
    if len(source_paths) != len(set(source_paths)):
        blockers.append("duplicate source paths detected in archive plan")

    proposed_paths = [item.proposed_archive_path for item in items]
    if len(proposed_paths) != len(set(proposed_paths)):
        blockers.append("duplicate proposed archive paths detected in archive plan")

    warnings = [
        "plan is advisory only; no deletion or file move is approved by this report",
        "first archive bucket is intentionally conservative: non-active *_report.py Python files only",
        "run full validation before and after any future reversible archive move",
    ]

    result = ReversibleArchiveStagingPlanResult(
        status=STATUS_READY,
        plan_status=PLAN_READY if not blockers else "REVERSIBLE_ARCHIVE_STAGING_PLAN_BLOCKED",
        current_date=current_date,
        archive_root=archive_root,
        active_import_closure_count=report.active_import_closure_count,
        validation_test_keep_count=report.validation_test_keep_count,
        non_active_versioned_module_count=report.non_active_versioned_module_count,
        archive_candidate_test_count=report.archive_candidate_test_count,
        non_active_data_config_candidate_count=report.non_active_data_config_candidate_count,
        report_only_module_candidate_count=sum(
            1 for path in report.non_active_versioned_module_paths if _is_report_python(path)
        ),
        report_only_test_candidate_count=sum(
            1 for path in report.archive_candidate_test_paths if _is_report_python(path)
        ),
        total_plan_item_count=len(items),
        plan_items=[item.to_dict() for item in items],
        unresolved_local_import_count=report.unresolved_local_import_count,
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
        result = ReversibleArchiveStagingPlanResult(**payload)

    return result


def format_reversible_archive_staging_plan(
    result: ReversibleArchiveStagingPlanResult,
    *,
    sample_size: int = 60,
) -> str:
    lines = [
        "J.A.R.V.I.S. REVERSIBLE ARCHIVE STAGING PLAN",
        f"status: {result.status}",
        f"plan status: {result.plan_status}",
        f"current date: {result.current_date}",
        f"archive root: {result.archive_root}",
        f"active import closure count: {result.active_import_closure_count}",
        f"validation test keep count: {result.validation_test_keep_count}",
        f"non-active versioned module count: {result.non_active_versioned_module_count}",
        f"archive candidate test count: {result.archive_candidate_test_count}",
        f"non-active data/config candidate count: {result.non_active_data_config_candidate_count}",
        f"report-only module candidate count: {result.report_only_module_candidate_count}",
        f"report-only test candidate count: {result.report_only_test_candidate_count}",
        f"total plan item count: {result.total_plan_item_count}",
        f"unresolved local import count: {result.unresolved_local_import_count}",
        f"report written: {result.report_written}",
        f"report path: {result.report_path}",
        "",
        "Proposed reversible archive move sample:",
    ]

    for item in result.plan_items[:sample_size]:
        lines.append(f"- {item['source_path']} -> {item['proposed_archive_path']}")

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
    parser = argparse.ArgumentParser(description="Build the v69 reversible archive staging plan.")
    parser.add_argument("--current-date", default="2026-06-17")
    parser.add_argument("--archive-root", default=DEFAULT_ARCHIVE_ROOT)
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--output-path", default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--safety-check", action="store_true")
    args = parser.parse_args(argv)

    if args.safety_check:
        print(build_safety_check_console_output())
        return 0

    result = build_reversible_archive_staging_plan_result(
        current_date=args.current_date,
        archive_root=args.archive_root,
        write_report=args.write_report,
        output_path=args.output_path,
    )
    print(format_reversible_archive_staging_plan(result))
    return 0 if not result.blockers else 1


__all__ = [
    "DEFAULT_ARCHIVE_ROOT",
    "DEFAULT_OUTPUT_PATH",
    "PLAN_READY",
    "STATUS_READY",
    "ArchivePlanItem",
    "ReversibleArchiveStagingPlanResult",
    "build_reversible_archive_staging_plan_result",
    "format_reversible_archive_staging_plan",
    "main",
]


if __name__ == "__main__":
    raise SystemExit(main())
