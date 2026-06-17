"""J.A.R.V.I.S. v74.0 validation-blocked legacy candidate decoupling audit.

Audit-only. No deletion. No archive movement. No file move.

Purpose:
After v73 archived the next-safe non-active Python bucket, the remaining
legacy module archive candidates are blocked by validation tests. This audit
maps each validation-blocked legacy module to the tests that still import it,
so future stages can decouple or retire those tests deliberately.
"""

from __future__ import annotations

import argparse
import ast
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from jarvis.runtime.remaining_python_archive_risk_audit import (
    build_remaining_python_archive_risk_audit_result,
)
from jarvis.runtime.safety import build_safety_check_console_output

STATUS_READY = "JARVIS_V74_0_VALIDATION_BLOCKED_LEGACY_CANDIDATE_DECOUPLING_AUDIT_READY_SAFE"
AUDIT_READY = "VALIDATION_BLOCKED_LEGACY_CANDIDATE_DECOUPLING_AUDIT_READY"
DEFAULT_OUTPUT_PATH = "outputs/validation_blocked_legacy_candidate_decoupling_audit_latest.json"


@dataclass(frozen=True)
class ValidationBlockedLegacyModuleRecord:
    module_path: str
    blocking_test_count: int
    blocking_test_paths: list[str]
    decoupling_reason: str
    recommended_next_action: str


@dataclass(frozen=True)
class ValidationBlockedLegacyCandidateDecouplingAuditResult:
    status: str
    audit_status: str
    current_date: str
    validation_blocked_module_count: int
    unique_blocking_test_count: int
    total_blocking_test_reference_count: int
    next_safe_module_candidate_count: int
    remaining_non_active_versioned_module_count: int
    validation_blocked_test_count: int
    next_safe_test_candidate_count: int
    active_import_closure_count: int
    active_runtime_module_count: int
    active_versioned_module_count: int
    unresolved_local_import_count: int
    validation_blocked_module_records: list[dict[str, Any]]
    unique_blocking_test_paths: list[str]
    active_import_closure_paths: list[str]
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


def _module_name_to_path(module_name: str) -> str | None:
    if not module_name.startswith("jarvis"):
        return None
    return module_name.replace(".", "/") + ".py"


def _parse_direct_jarvis_imports(path: str) -> set[str]:
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
            if node.level != 0:
                continue

            module = node.module or ""
            module_path = _module_name_to_path(module)
            if module_path:
                imports.add(module_path)

            if module == "jarvis":
                for alias in node.names:
                    if alias.name.startswith("jarvis_v"):
                        imports.add(f"jarvis/{alias.name}.py")

    return imports


def build_validation_blocked_legacy_candidate_decoupling_audit_result(
    *,
    current_date: str = "2026-06-17",
    write_report: bool = False,
    output_path: str | Path = DEFAULT_OUTPUT_PATH,
) -> ValidationBlockedLegacyCandidateDecouplingAuditResult:
    risk = build_remaining_python_archive_risk_audit_result(current_date=current_date)

    blocked_modules = sorted(risk.validation_blocked_module_paths)
    validation_tests = sorted(risk.validation_test_keep_paths)
    active_paths = set(risk.active_import_closure_paths)

    module_to_tests: dict[str, list[str]] = {module: [] for module in blocked_modules}

    for test_path in validation_tests:
        imports = _parse_direct_jarvis_imports(test_path)
        for module in blocked_modules:
            if module in imports:
                module_to_tests[module].append(test_path)

    records: list[ValidationBlockedLegacyModuleRecord] = []
    blockers: list[str] = []

    for module in blocked_modules:
        tests = sorted(module_to_tests[module])
        if module in active_paths:
            blockers.append(f"validation-blocked module is unexpectedly active runtime path: {module}")
        if not tests:
            blockers.append(f"validation-blocked module has no mapped blocking test: {module}")

        records.append(
            ValidationBlockedLegacyModuleRecord(
                module_path=module,
                blocking_test_count=len(tests),
                blocking_test_paths=tests,
                decoupling_reason="module is non-active but still imported by validation tests",
                recommended_next_action=(
                    "keep module until equivalent active-runtime coverage exists, then "
                    "refactor or retire the blocking validation tests before archive"
                ),
            )
        )

    unique_tests = sorted({test for tests in module_to_tests.values() for test in tests})
    total_refs = sum(len(tests) for tests in module_to_tests.values())

    warnings = [
        "audit-only; no deletion or archive movement is approved by this report",
        "remaining legacy module candidates are validation-blocked and must not be moved yet",
        "future decoupling should replace direct historical module tests with active-runtime facade tests",
    ]

    result = ValidationBlockedLegacyCandidateDecouplingAuditResult(
        status=STATUS_READY,
        audit_status=AUDIT_READY if not blockers else "VALIDATION_BLOCKED_LEGACY_CANDIDATE_DECOUPLING_AUDIT_BLOCKED",
        current_date=current_date,
        validation_blocked_module_count=len(blocked_modules),
        unique_blocking_test_count=len(unique_tests),
        total_blocking_test_reference_count=total_refs,
        next_safe_module_candidate_count=risk.next_safe_module_candidate_count,
        remaining_non_active_versioned_module_count=risk.remaining_non_active_versioned_module_count,
        validation_blocked_test_count=risk.validation_blocked_test_count,
        next_safe_test_candidate_count=risk.next_safe_test_candidate_count,
        active_import_closure_count=risk.active_import_closure_count,
        active_runtime_module_count=risk.active_runtime_module_count,
        active_versioned_module_count=risk.active_versioned_module_count,
        unresolved_local_import_count=risk.unresolved_local_import_count,
        validation_blocked_module_records=[asdict(record) for record in records],
        unique_blocking_test_paths=unique_tests,
        active_import_closure_paths=risk.active_import_closure_paths,
        validation_test_keep_paths=validation_tests,
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
        result = ValidationBlockedLegacyCandidateDecouplingAuditResult(**payload)

    return result


def format_validation_blocked_legacy_candidate_decoupling_audit(
    result: ValidationBlockedLegacyCandidateDecouplingAuditResult,
    *,
    sample_size: int = 50,
) -> str:
    lines = [
        "J.A.R.V.I.S. VALIDATION-BLOCKED LEGACY CANDIDATE DECOUPLING AUDIT",
        f"status: {result.status}",
        f"audit status: {result.audit_status}",
        f"current date: {result.current_date}",
        f"validation-blocked module count: {result.validation_blocked_module_count}",
        f"unique blocking test count: {result.unique_blocking_test_count}",
        f"total blocking test reference count: {result.total_blocking_test_reference_count}",
        f"next-safe module candidate count: {result.next_safe_module_candidate_count}",
        f"remaining non-active versioned module count: {result.remaining_non_active_versioned_module_count}",
        f"validation-blocked test count: {result.validation_blocked_test_count}",
        f"next-safe test candidate count: {result.next_safe_test_candidate_count}",
        f"active import closure count: {result.active_import_closure_count}",
        f"active runtime module count: {result.active_runtime_module_count}",
        f"active versioned module count: {result.active_versioned_module_count}",
        f"unresolved local import count: {result.unresolved_local_import_count}",
        f"report written: {result.report_written}",
        f"report path: {result.report_path}",
        "",
        "VALIDATION-BLOCKED MODULE MAP:",
    ]

    for record in result.validation_blocked_module_records[:sample_size]:
        lines.append(f"- {record['module_path']}")
        lines.append(f"  blocking tests: {record['blocking_test_count']}")
        for test_path in record["blocking_test_paths"][:10]:
            lines.append(f"  - {test_path}")

    lines.extend(["", "UNIQUE BLOCKING TEST SAMPLE:"])
    lines.extend(f"- {path}" for path in result.unique_blocking_test_paths[:sample_size])

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
    parser = argparse.ArgumentParser(
        description="Build the v74 validation-blocked legacy candidate decoupling audit."
    )
    parser.add_argument("--current-date", default="2026-06-17")
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--output-path", default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--safety-check", action="store_true")
    args = parser.parse_args(argv)

    if args.safety_check:
        print(build_safety_check_console_output())
        return 0

    result = build_validation_blocked_legacy_candidate_decoupling_audit_result(
        current_date=args.current_date,
        write_report=args.write_report,
        output_path=args.output_path,
    )
    print(format_validation_blocked_legacy_candidate_decoupling_audit(result))
    return 0 if not result.blockers else 1


__all__ = [
    "AUDIT_READY",
    "DEFAULT_OUTPUT_PATH",
    "STATUS_READY",
    "ValidationBlockedLegacyCandidateDecouplingAuditResult",
    "ValidationBlockedLegacyModuleRecord",
    "build_validation_blocked_legacy_candidate_decoupling_audit_result",
    "format_validation_blocked_legacy_candidate_decoupling_audit",
    "main",
]


if __name__ == "__main__":
    raise SystemExit(main())
