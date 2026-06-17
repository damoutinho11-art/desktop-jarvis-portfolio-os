"""J.A.R.V.I.S. v75.0 validation-blocked v5 replacement plan.

Audit-only. No deletion. No archive movement. No file move.

Purpose:
v74 proved the final 12 non-active legacy modules are blocked only by direct
v5 validation tests. This plan maps those historical tests/modules to the
active-runtime facade coverage that must replace them before the final v5
legacy archive can be executed.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from jarvis.runtime.safety import build_safety_check_console_output
from jarvis.runtime.validation_blocked_legacy_candidate_decoupling_audit import (
    build_validation_blocked_legacy_candidate_decoupling_audit_result,
)

STATUS_READY = "JARVIS_V75_0_VALIDATION_BLOCKED_V5_REPLACEMENT_PLAN_READY_SAFE"
PLAN_READY = "VALIDATION_BLOCKED_V5_REPLACEMENT_PLAN_READY"
DEFAULT_OUTPUT_PATH = "outputs/validation_blocked_v5_replacement_plan_latest.json"


@dataclass(frozen=True)
class V5ReplacementPlanRecord:
    legacy_module_path: str
    blocking_test_paths: list[str]
    legacy_category: str
    replacement_surface: str
    proposed_active_runtime_coverage: list[str]
    replacement_required_before_archive: bool
    archive_allowed_now: bool
    reason: str


@dataclass(frozen=True)
class ValidationBlockedV5ReplacementPlanResult:
    status: str
    plan_status: str
    current_date: str
    replacement_record_count: int
    validation_blocked_module_count: int
    unique_blocking_test_count: int
    remaining_non_active_versioned_module_count: int
    next_safe_module_candidate_count: int
    active_import_closure_count: int
    active_runtime_module_count: int
    active_versioned_module_count: int
    unresolved_local_import_count: int
    replacement_records: list[dict[str, Any]]
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


def _classify_legacy_module(module_path: str) -> tuple[str, str, list[str]]:
    name = Path(module_path).stem

    if name.endswith("_report"):
        return (
            "historical_v5_report_module",
            "active runtime report-output coverage",
            [
                "assert active audit/report modules write explicit JSON only when --write-report is used",
                "assert generated report outputs remain ignored and are not required for runtime behavior",
                "assert safety fields remain false in active runtime reports",
            ],
        )

    if "fixture_wiring" in name:
        return (
            "historical_public_source_fixture_wiring",
            "platform data completeness gate + evidence intake facade",
            [
                "assert current platform data completeness gate separates public instrument intake from private/local files",
                "assert explicit local templates remain ignored and never count as confirmed data",
                "assert no broker, credential, order, or trade path is introduced",
            ],
        )

    if "fixture_import_dry_run" in name:
        return (
            "historical_real_fixture_import_dry_run",
            "free research cache/evidence bridge facade",
            [
                "assert free research cache/evidence flow is explicit, local-only, and non-mutating by default",
                "assert evidence/report writing requires explicit flags",
                "assert current runtime remains safe with no execution action",
            ],
        )

    if "fixture_review_queue" in name:
        return (
            "historical_operator_fixture_review_queue",
            "manual review and weekly packet facade",
            [
                "assert weekly/manual packet remains review-only",
                "assert manual approval is required outside J.A.R.V.I.S.",
                "assert approval tickets do not become auto-approved or executable",
            ],
        )

    if "research_draft_source_router" in name:
        return (
            "historical_research_draft_source_router",
            "free research API router + source confidence facade",
            [
                "assert current free research routing distinguishes daily read-only from weekly manual prep",
                "assert source confidence and warnings are explicit",
                "assert paid/broker API is not required for current safe research mode",
            ],
        )

    if "public_research_packet_draft_assembler" in name:
        return (
            "historical_public_research_packet_assembler",
            "weekly packet + evidence pack facade",
            [
                "assert weekly manual buy packet uses evidence pack records when available",
                "assert stock-specific evidence gaps are represented honestly",
                "assert packet remains manual action guidance, not execution",
            ],
        )

    if "final_research_os_mvp_audit" in name:
        return (
            "historical_final_research_os_mvp_audit",
            "active runtime import-closure and no-execution safety facade",
            [
                "assert active import closure remains resolved",
                "assert active runtime surface is explicit",
                "assert safety-check blocks buy/order/trade commands",
            ],
        )

    return (
        "historical_v5_unknown",
        "manual review required",
        [
            "inspect historical test intent before replacing",
            "add active-runtime facade coverage before archiving",
        ],
    )


def build_validation_blocked_v5_replacement_plan_result(
    *,
    current_date: str = "2026-06-17",
    write_report: bool = False,
    output_path: str | Path = DEFAULT_OUTPUT_PATH,
) -> ValidationBlockedV5ReplacementPlanResult:
    decoupling = build_validation_blocked_legacy_candidate_decoupling_audit_result(
        current_date=current_date
    )

    records: list[V5ReplacementPlanRecord] = []
    blockers: list[str] = []

    if decoupling.unresolved_local_import_count != 0:
        blockers.append("v74 decoupling audit has unresolved local imports")

    if decoupling.blockers:
        blockers.extend(f"v74 blocker: {blocker}" for blocker in decoupling.blockers)

    for blocked in decoupling.validation_blocked_module_records:
        module_path = blocked["module_path"]
        blocking_tests = list(blocked["blocking_test_paths"])
        category, replacement_surface, coverage = _classify_legacy_module(module_path)

        if not module_path.startswith("jarvis/jarvis_v5"):
            blockers.append(f"unexpected non-v5 validation-blocked module: {module_path}")

        if not blocking_tests:
            blockers.append(f"missing blocking tests for module: {module_path}")

        if category == "historical_v5_unknown":
            blockers.append(f"replacement classification missing for module: {module_path}")

        records.append(
            V5ReplacementPlanRecord(
                legacy_module_path=module_path,
                blocking_test_paths=blocking_tests,
                legacy_category=category,
                replacement_surface=replacement_surface,
                proposed_active_runtime_coverage=coverage,
                replacement_required_before_archive=True,
                archive_allowed_now=False,
                reason=(
                    "direct historical v5 validation coverage must be replaced by "
                    "active-runtime facade coverage before final legacy archive"
                ),
            )
        )

    warnings = [
        "plan-only stage; no deletion or archive movement is approved",
        "archive_allowed_now is intentionally false for every v5 record",
        "next execution stage should add active-runtime replacement tests before moving v5 modules",
    ]

    result = ValidationBlockedV5ReplacementPlanResult(
        status=STATUS_READY,
        plan_status=PLAN_READY if not blockers else "VALIDATION_BLOCKED_V5_REPLACEMENT_PLAN_BLOCKED",
        current_date=current_date,
        replacement_record_count=len(records),
        validation_blocked_module_count=decoupling.validation_blocked_module_count,
        unique_blocking_test_count=decoupling.unique_blocking_test_count,
        remaining_non_active_versioned_module_count=decoupling.remaining_non_active_versioned_module_count,
        next_safe_module_candidate_count=decoupling.next_safe_module_candidate_count,
        active_import_closure_count=decoupling.active_import_closure_count,
        active_runtime_module_count=decoupling.active_runtime_module_count,
        active_versioned_module_count=decoupling.active_versioned_module_count,
        unresolved_local_import_count=decoupling.unresolved_local_import_count,
        replacement_records=[asdict(record) for record in records],
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
        result = ValidationBlockedV5ReplacementPlanResult(**payload)

    return result


def format_validation_blocked_v5_replacement_plan(
    result: ValidationBlockedV5ReplacementPlanResult,
) -> str:
    lines = [
        "J.A.R.V.I.S. VALIDATION-BLOCKED V5 REPLACEMENT PLAN",
        f"status: {result.status}",
        f"plan status: {result.plan_status}",
        f"current date: {result.current_date}",
        f"replacement record count: {result.replacement_record_count}",
        f"validation-blocked module count: {result.validation_blocked_module_count}",
        f"unique blocking test count: {result.unique_blocking_test_count}",
        f"remaining non-active versioned module count: {result.remaining_non_active_versioned_module_count}",
        f"next-safe module candidate count: {result.next_safe_module_candidate_count}",
        f"active import closure count: {result.active_import_closure_count}",
        f"active runtime module count: {result.active_runtime_module_count}",
        f"active versioned module count: {result.active_versioned_module_count}",
        f"unresolved local import count: {result.unresolved_local_import_count}",
        f"report written: {result.report_written}",
        f"report path: {result.report_path}",
        "",
        "REPLACEMENT MAP:",
    ]

    for record in result.replacement_records:
        lines.append(f"- {record['legacy_module_path']}")
        lines.append(f"  category: {record['legacy_category']}")
        lines.append(f"  replacement surface: {record['replacement_surface']}")
        lines.append(f"  archive allowed now: {record['archive_allowed_now']}")
        lines.append("  proposed active-runtime coverage:")
        for coverage in record["proposed_active_runtime_coverage"]:
            lines.append(f"  - {coverage}")

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
    parser = argparse.ArgumentParser(description="Build the v75 validation-blocked v5 replacement plan.")
    parser.add_argument("--current-date", default="2026-06-17")
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--output-path", default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--safety-check", action="store_true")
    args = parser.parse_args(argv)

    if args.safety_check:
        print(build_safety_check_console_output())
        return 0

    result = build_validation_blocked_v5_replacement_plan_result(
        current_date=args.current_date,
        write_report=args.write_report,
        output_path=args.output_path,
    )
    print(format_validation_blocked_v5_replacement_plan(result))
    return 0 if not result.blockers else 1


__all__ = [
    "DEFAULT_OUTPUT_PATH",
    "PLAN_READY",
    "STATUS_READY",
    "V5ReplacementPlanRecord",
    "ValidationBlockedV5ReplacementPlanResult",
    "build_validation_blocked_v5_replacement_plan_result",
    "format_validation_blocked_v5_replacement_plan",
    "main",
]


if __name__ == "__main__":
    raise SystemExit(main())
