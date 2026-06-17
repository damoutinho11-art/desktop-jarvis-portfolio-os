"""J.A.R.V.I.S. v71.0 remaining Python archive risk audit.

Audit-only. No deletion. No archive movement. No file move.
Purpose: after v70 archived the safest report-only Python files, identify the
remaining non-active Python candidates and separate safe-later candidates from
validation-blocked files.
"""

from __future__ import annotations

import argparse
import ast
import json
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from jarvis.runtime.import_closure_safe_archive_plan import (
    build_import_closure_safe_archive_plan_result,
)
from jarvis.runtime.safety import build_safety_check_console_output

STATUS_READY = "JARVIS_V71_0_REMAINING_PYTHON_ARCHIVE_RISK_AUDIT_READY_SAFE"
AUDIT_READY = "REMAINING_PYTHON_ARCHIVE_RISK_AUDIT_READY"
DEFAULT_OUTPUT_PATH = "outputs/remaining_python_archive_risk_audit_latest.json"

VALIDATION_TEST_PREFIXES = (
    "jarvis/tests/test_jarvis_v5",
    "jarvis/tests/test_jarvis_v60",
    "jarvis/tests/test_jarvis_v61",
    "jarvis/tests/test_jarvis_v62",
    "jarvis/tests/test_jarvis_v63",
    "jarvis/tests/test_jarvis_v64",
    "jarvis/tests/test_jarvis_v65",
    "jarvis/tests/test_jarvis_v66",
    "jarvis/tests/test_jarvis_v67",
    "jarvis/tests/test_jarvis_v68",
    "jarvis/tests/test_jarvis_v69",
    "jarvis/tests/test_jarvis_v70",
    "jarvis/tests/test_jarvis_v71",
)


@dataclass(frozen=True)
class RemainingPythonArchiveRiskAuditResult:
    status: str
    audit_status: str
    current_date: str
    tracked_file_count: int
    active_import_closure_count: int
    active_runtime_module_count: int
    active_versioned_module_count: int
    validation_test_keep_count: int
    validation_imported_module_count: int
    remaining_non_active_versioned_module_count: int
    validation_blocked_module_count: int
    next_safe_module_candidate_count: int
    remaining_non_active_test_count: int
    validation_blocked_test_count: int
    next_safe_test_candidate_count: int
    active_import_closure_paths: list[str]
    validation_test_keep_paths: list[str]
    validation_imported_module_paths: list[str]
    validation_blocked_module_paths: list[str]
    next_safe_module_candidate_paths: list[str]
    validation_blocked_test_paths: list[str]
    next_safe_test_candidate_paths: list[str]
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


def _git_ls_files() -> list[str]:
    return subprocess.check_output(["git", "ls-files"], text=True).splitlines()


def _is_versioned_module(path: str) -> bool:
    return path.startswith("jarvis/jarvis_v") and path.endswith(".py")


def _is_versioned_test(path: str) -> bool:
    return path.startswith("jarvis/tests/test_jarvis_v") and path.endswith(".py")


def _is_validation_test_keep(path: str) -> bool:
    return path.endswith(".py") and any(path.startswith(prefix) for prefix in VALIDATION_TEST_PREFIXES)


def _module_name_to_path(name: str) -> str | None:
    if not name.startswith("jarvis"):
        return None
    return name.replace(".", "/") + ".py"


def _parse_absolute_jarvis_imports(path: str) -> set[str]:
    imports: set[str] = set()
    p = Path(path)
    if not p.exists():
        return imports

    try:
        tree = ast.parse(p.read_text(encoding="utf-8-sig"))
    except SyntaxError:
        return imports

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                module_path = _module_name_to_path(alias.name)
                if module_path:
                    imports.add(module_path)
        elif isinstance(node, ast.ImportFrom):
            if node.level == 0 and node.module:
                module_path = _module_name_to_path(node.module)
                if module_path:
                    imports.add(module_path)

    return imports


def build_remaining_python_archive_risk_audit_result(
    *,
    current_date: str = "2026-06-17",
    write_report: bool = False,
    output_path: str | Path = DEFAULT_OUTPUT_PATH,
) -> RemainingPythonArchiveRiskAuditResult:
    closure = build_import_closure_safe_archive_plan_result(current_date=current_date)
    tracked = _git_ls_files()

    active_paths = set(closure["active_import_closure_paths"])

    validation_tests = sorted(
        path for path in tracked if _is_versioned_test(path) and _is_validation_test_keep(path)
    )

    validation_imports: set[str] = set()
    for test_path in validation_tests:
        validation_imports |= _parse_absolute_jarvis_imports(test_path)

    remaining_non_active_modules = sorted(
        path for path in tracked if _is_versioned_module(path) and path not in active_paths
    )

    validation_blocked_modules = sorted(
        path for path in remaining_non_active_modules if path in validation_imports
    )

    next_safe_modules = sorted(
        path for path in remaining_non_active_modules if path not in validation_imports
    )

    remaining_non_active_tests = sorted(
        path for path in tracked if _is_versioned_test(path) and path not in active_paths
    )

    validation_blocked_tests = sorted(
        path for path in remaining_non_active_tests if path in set(validation_tests)
    )

    next_safe_tests = sorted(
        path for path in remaining_non_active_tests if path not in set(validation_tests)
    )

    blockers: list[str] = []
    for path in next_safe_modules:
        if path in active_paths:
            blockers.append(f"safe module candidate is active runtime path: {path}")
        if path in validation_imports:
            blockers.append(f"safe module candidate is imported by validation tests: {path}")

    for path in next_safe_tests:
        if path in active_paths:
            blockers.append(f"safe test candidate is active runtime path: {path}")
        if path in set(validation_tests):
            blockers.append(f"safe test candidate is current validation keep path: {path}")

    warnings = [
        "audit-only; no deletion or archive movement is approved by this report",
        "validation-blocked modules must remain until their tests are refactored or retired",
        "next-safe candidates still require a dedicated reversible archive execution stage",
    ]

    result = RemainingPythonArchiveRiskAuditResult(
        status=STATUS_READY,
        audit_status=AUDIT_READY if not blockers else "REMAINING_PYTHON_ARCHIVE_RISK_AUDIT_BLOCKED",
        current_date=current_date,
        tracked_file_count=closure["tracked_file_count"],
        active_import_closure_count=closure["active_import_closure_count"],
        active_runtime_module_count=closure["active_runtime_module_count"],
        active_versioned_module_count=closure["active_versioned_module_count"],
        validation_test_keep_count=len(validation_tests),
        validation_imported_module_count=len(validation_imports),
        remaining_non_active_versioned_module_count=len(remaining_non_active_modules),
        validation_blocked_module_count=len(validation_blocked_modules),
        next_safe_module_candidate_count=len(next_safe_modules),
        remaining_non_active_test_count=len(remaining_non_active_tests),
        validation_blocked_test_count=len(validation_blocked_tests),
        next_safe_test_candidate_count=len(next_safe_tests),
        active_import_closure_paths=sorted(active_paths),
        validation_test_keep_paths=validation_tests,
        validation_imported_module_paths=sorted(validation_imports),
        validation_blocked_module_paths=validation_blocked_modules,
        next_safe_module_candidate_paths=next_safe_modules,
        validation_blocked_test_paths=validation_blocked_tests,
        next_safe_test_candidate_paths=next_safe_tests,
        unresolved_local_import_count=closure["unresolved_local_import_count"],
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
        result = RemainingPythonArchiveRiskAuditResult(**payload)

    return result


def format_remaining_python_archive_risk_audit(
    result: RemainingPythonArchiveRiskAuditResult,
    *,
    sample_size: int = 50,
) -> str:
    lines = [
        "J.A.R.V.I.S. REMAINING PYTHON ARCHIVE RISK AUDIT",
        f"status: {result.status}",
        f"audit status: {result.audit_status}",
        f"current date: {result.current_date}",
        f"tracked files: {result.tracked_file_count}",
        f"active import closure count: {result.active_import_closure_count}",
        f"active runtime module count: {result.active_runtime_module_count}",
        f"active versioned module count: {result.active_versioned_module_count}",
        f"validation test keep count: {result.validation_test_keep_count}",
        f"validation imported module count: {result.validation_imported_module_count}",
        f"remaining non-active versioned module count: {result.remaining_non_active_versioned_module_count}",
        f"validation-blocked module count: {result.validation_blocked_module_count}",
        f"next-safe module candidate count: {result.next_safe_module_candidate_count}",
        f"remaining non-active test count: {result.remaining_non_active_test_count}",
        f"validation-blocked test count: {result.validation_blocked_test_count}",
        f"next-safe test candidate count: {result.next_safe_test_candidate_count}",
        f"unresolved local import count: {result.unresolved_local_import_count}",
        f"report written: {result.report_written}",
        f"report path: {result.report_path}",
        "",
        "VALIDATION-BLOCKED MODULE SAMPLE:",
    ]

    lines.extend(f"- {path}" for path in result.validation_blocked_module_paths[:sample_size])
    lines.extend(["", "NEXT-SAFE MODULE CANDIDATE SAMPLE:"])
    lines.extend(f"- {path}" for path in result.next_safe_module_candidate_paths[:sample_size])
    lines.extend(["", "VALIDATION-BLOCKED TEST SAMPLE:"])
    lines.extend(f"- {path}" for path in result.validation_blocked_test_paths[:sample_size])
    lines.extend(["", "NEXT-SAFE TEST CANDIDATE SAMPLE:"])
    lines.extend(f"- {path}" for path in result.next_safe_test_candidate_paths[:sample_size])

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
    parser = argparse.ArgumentParser(description="Build the v71 remaining Python archive risk audit.")
    parser.add_argument("--current-date", default="2026-06-17")
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--output-path", default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--safety-check", action="store_true")
    args = parser.parse_args(argv)

    if args.safety_check:
        print(build_safety_check_console_output())
        return 0

    result = build_remaining_python_archive_risk_audit_result(
        current_date=args.current_date,
        write_report=args.write_report,
        output_path=args.output_path,
    )
    print(format_remaining_python_archive_risk_audit(result))
    return 0 if not result.blockers else 1


__all__ = [
    "AUDIT_READY",
    "DEFAULT_OUTPUT_PATH",
    "STATUS_READY",
    "RemainingPythonArchiveRiskAuditResult",
    "build_remaining_python_archive_risk_audit_result",
    "format_remaining_python_archive_risk_audit",
    "main",
]


if __name__ == "__main__":
    raise SystemExit(main())
