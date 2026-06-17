"""J.A.R.V.I.S. v68.0 non-active archive candidate report.

Audit-only report. No deletion. No archive movement. No runtime behavior mutation.
Purpose: identify files that are not needed by the current active runtime import
closure, while preserving validation tests and safety invariants.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from jarvis.runtime.import_closure_safe_archive_plan import (
    build_import_closure_safe_archive_plan_result,
)
from jarvis.runtime.safety import build_safety_check_console_output

STATUS_READY = "JARVIS_V68_0_NON_ACTIVE_ARCHIVE_CANDIDATE_REPORT_READY_SAFE"
REPORT_READY = "NON_ACTIVE_ARCHIVE_CANDIDATE_REPORT_READY"
DEFAULT_OUTPUT_PATH = "outputs/non_active_archive_candidate_report_latest.json"

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
)


@dataclass(frozen=True)
class NonActiveArchiveCandidateReportResult:
    status: str
    report_status: str
    current_date: str
    tracked_file_count: int
    active_import_closure_count: int
    active_runtime_keep_paths: list[str]
    validation_test_keep_count: int
    validation_test_keep_paths: list[str]
    non_active_versioned_module_count: int
    non_active_versioned_module_paths: list[str]
    archive_candidate_test_count: int
    archive_candidate_test_paths: list[str]
    non_active_data_config_candidate_count: int
    non_active_data_config_candidate_paths: list[str]
    unresolved_local_import_count: int
    deletion_performed: bool
    archive_performed: bool
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


def _is_data_or_config_candidate(path: str) -> bool:
    return (
        path.startswith("jarvis/data/")
        or path.startswith("data/")
        or path.startswith("fixtures/")
        or path.startswith("jarvis/fixtures/")
        or path.startswith("templates/")
        or path.endswith(".json")
        or path.endswith(".csv")
    )


def _is_validation_test_keep(path: str) -> bool:
    return path.endswith(".py") and any(path.startswith(prefix) for prefix in VALIDATION_TEST_PREFIXES)


def build_non_active_archive_candidate_report_result(
    *,
    current_date: str = "2026-06-17",
    write_report: bool = False,
    output_path: str | Path = DEFAULT_OUTPUT_PATH,
) -> NonActiveArchiveCandidateReportResult:
    closure = build_import_closure_safe_archive_plan_result(current_date=current_date)
    tracked = _git_ls_files()

    active = set(closure["active_import_closure_paths"])

    validation_keep = sorted(
        path for path in tracked if _is_versioned_test(path) and _is_validation_test_keep(path)
    )

    non_active_modules = sorted(
        path for path in tracked if _is_versioned_module(path) and path not in active
    )

    archive_candidate_tests = sorted(
        path
        for path in tracked
        if _is_versioned_test(path)
        and path not in active
        and path not in set(validation_keep)
    )

    data_candidates = sorted(
        path
        for path in tracked
        if _is_data_or_config_candidate(path)
        and path not in active
    )

    warnings = [
        "archive candidates are review-only; no deletion or move is approved by this report",
        "validation tests are kept separately even when they are not part of runtime import closure",
        "data/config candidates may include useful examples and should be archived only after review",
    ]

    result = NonActiveArchiveCandidateReportResult(
        status=STATUS_READY,
        report_status=REPORT_READY,
        current_date=current_date,
        tracked_file_count=len(tracked),
        active_import_closure_count=len(active),
        active_runtime_keep_paths=sorted(active),
        validation_test_keep_count=len(validation_keep),
        validation_test_keep_paths=validation_keep,
        non_active_versioned_module_count=len(non_active_modules),
        non_active_versioned_module_paths=non_active_modules,
        archive_candidate_test_count=len(archive_candidate_tests),
        archive_candidate_test_paths=archive_candidate_tests,
        non_active_data_config_candidate_count=len(data_candidates),
        non_active_data_config_candidate_paths=data_candidates,
        unresolved_local_import_count=closure["unresolved_local_import_count"],
        deletion_performed=False,
        archive_performed=False,
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
        blockers=[],
        report_written=False,
        report_path=str(output_path),
    )

    if write_report:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = result.to_dict()
        payload["report_written"] = True
        path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        result = NonActiveArchiveCandidateReportResult(**payload)

    return result


def format_non_active_archive_candidate_report(
    result: NonActiveArchiveCandidateReportResult,
    *,
    sample_size: int = 40,
) -> str:
    lines = [
        "J.A.R.V.I.S. NON-ACTIVE ARCHIVE CANDIDATE REPORT",
        f"status: {result.status}",
        f"report status: {result.report_status}",
        f"current date: {result.current_date}",
        f"tracked files: {result.tracked_file_count}",
        f"active import closure count: {result.active_import_closure_count}",
        f"validation test keep count: {result.validation_test_keep_count}",
        f"non-active versioned module count: {result.non_active_versioned_module_count}",
        f"archive candidate test count: {result.archive_candidate_test_count}",
        f"non-active data/config candidate count: {result.non_active_data_config_candidate_count}",
        f"unresolved local import count: {result.unresolved_local_import_count}",
        f"report written: {result.report_written}",
        f"report path: {result.report_path}",
        "",
        "KEEP — active runtime closure sample:",
    ]

    lines.extend(f"- {path}" for path in result.active_runtime_keep_paths[:sample_size])
    lines.extend(["", "KEEP — validation tests sample:"])
    lines.extend(f"- {path}" for path in result.validation_test_keep_paths[:sample_size])
    lines.extend(["", "REVIEW / ARCHIVE — non-active module sample:"])
    lines.extend(f"- {path}" for path in result.non_active_versioned_module_paths[:sample_size])
    lines.extend(["", "REVIEW / ARCHIVE — non-active test sample:"])
    lines.extend(f"- {path}" for path in result.archive_candidate_test_paths[:sample_size])
    lines.extend(["", "REVIEW / ARCHIVE — data/config sample:"])
    lines.extend(f"- {path}" for path in result.non_active_data_config_candidate_paths[:sample_size])

    lines.extend(
        [
            "",
            "Safety:",
            f"- deletion performed: {result.deletion_performed}",
            f"- archive performed: {result.archive_performed}",
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
    parser = argparse.ArgumentParser(description="Build the v68 non-active archive candidate report.")
    parser.add_argument("--current-date", default="2026-06-17")
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--output-path", default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--safety-check", action="store_true")
    args = parser.parse_args(argv)

    if args.safety_check:
        print(build_safety_check_console_output())
        return 0

    result = build_non_active_archive_candidate_report_result(
        current_date=args.current_date,
        write_report=args.write_report,
        output_path=args.output_path,
    )
    print(format_non_active_archive_candidate_report(result))
    return 0


__all__ = [
    "DEFAULT_OUTPUT_PATH",
    "NonActiveArchiveCandidateReportResult",
    "STATUS_READY",
    "REPORT_READY",
    "build_non_active_archive_candidate_report_result",
    "format_non_active_archive_candidate_report",
    "main",
]


if __name__ == "__main__":
    raise SystemExit(main())
