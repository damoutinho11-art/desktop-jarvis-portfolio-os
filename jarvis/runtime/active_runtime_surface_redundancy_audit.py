"""J.A.R.V.I.S. v63.0 active runtime surface + redundancy audit.

Audit-only module that maps the currently active runtime surface and separates it
from historical versioned modules/tests. It performs no deletion and no runtime
behavior mutation.

Safety invariant: Automated research. Manual trust. Manual approval. No execution.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from datetime import date
from pathlib import Path
from typing import Any, Mapping

from jarvis.jarvis_v16_0_real_daily_readiness_gate import build_safety_check_console_output

STATUS_READY = "JARVIS_V63_0_ACTIVE_RUNTIME_SURFACE_REDUNDANCY_AUDIT_READY_SAFE"
AUDIT_READY = "ACTIVE_RUNTIME_SURFACE_REDUNDANCY_AUDIT_READY"

DEFAULT_REPORT_PATH = "outputs/active_runtime_surface_redundancy_audit_latest.json"

ACTIVE_DAILY_MONTHLY_COMMANDS = [
    "python .\\jarvis_operator.py --personal-finance-contribution-bridge --current-date YYYY-MM-DD",
    "python .\\jarvis_operator.py --allocation-strategy-audit --current-date YYYY-MM-DD",
    "python .\\jarvis_operator.py --platform-data-completeness-gate --current-date YYYY-MM-DD",
    "python .\\jarvis_operator.py --manual-cost-basis-intake --current-date YYYY-MM-DD",
    "python .\\jarvis_operator.py --active-runtime-surface-redundancy-audit --current-date YYYY-MM-DD",
]

LOCAL_ONLY_FILES = [
    "jarvis/local/monthly_expenses.local.json",
    "jarvis/local/manual_portfolio_snapshot.local.json",
    "jarvis/local/manual_cost_basis.local.json",
    "jarvis/local/lightyear_instrument_universe.local.json",
    "jarvis/local/crypto_facility_terms.local.json",
    "jarvis/local/legacy_migration_review.local.json",
    "jarvis/local/free_research_api_cache.local.json",
]

GENERATED_OUTPUT_FILES = [
    "outputs/free_research_evidence_pack_latest.json",
    "outputs/approval_ticket_latest.json",
    DEFAULT_REPORT_PATH,
]


def _today_iso() -> str:
    return date.today().isoformat()


def _git_ls_files(root: Path) -> list[str]:
    try:
        completed = subprocess.run(
            ["git", "ls-files"],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return []
    return [line.strip().replace("\\", "/") for line in completed.stdout.splitlines() if line.strip()]


def _path_exists(root: Path, item: str) -> bool:
    return (root / item).exists()


def _is_runtime_file(path: str) -> bool:
    return path.startswith("jarvis/runtime/") and path.endswith(".py")


def _is_versioned_runtime_module(path: str) -> bool:
    name = Path(path).name
    return path.startswith("jarvis/") and name.startswith("jarvis_v") and name.endswith(".py")


def _is_versioned_test(path: str) -> bool:
    name = Path(path).name
    return path.startswith("jarvis/tests/") and name.startswith("test_jarvis_v") and name.endswith(".py")


def _is_report_module(path: str) -> bool:
    return path.endswith("_report.py")


def _is_data_fixture(path: str) -> bool:
    return path.startswith("jarvis/data/") and "jarvis_v" in Path(path).name


def _stable_active_runtime_modules(files: list[str]) -> list[str]:
    return sorted(path for path in files if _is_runtime_file(path))


def _candidate_legacy_modules(files: list[str]) -> list[str]:
    active_runtime = set(_stable_active_runtime_modules(files))
    candidates = []
    for path in files:
        if path in active_runtime:
            continue
        if _is_versioned_runtime_module(path):
            candidates.append(path)
    return sorted(candidates)


def build_active_runtime_surface_redundancy_audit_result(
    *,
    current_date: str | None = None,
    repo_root: str | Path = ".",
    write_report: bool = False,
    report_path: str | Path = DEFAULT_REPORT_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    effective_date = current_date or _today_iso()
    files = _git_ls_files(root)

    runtime_modules = _stable_active_runtime_modules(files)
    versioned_modules = sorted(path for path in files if _is_versioned_runtime_module(path))
    versioned_report_modules = sorted(path for path in versioned_modules if _is_report_module(path))
    versioned_non_report_modules = sorted(path for path in versioned_modules if not _is_report_module(path))
    versioned_tests = sorted(path for path in files if _is_versioned_test(path))
    data_fixtures = sorted(path for path in files if _is_data_fixture(path))
    legacy_candidates = _candidate_legacy_modules(files)

    local_file_status = [
        {"path": item, "exists": _path_exists(root, item), "tracked": item in files, "expected_tracked": False}
        for item in LOCAL_ONLY_FILES
    ]
    generated_output_status = [
        {"path": item, "exists": _path_exists(root, item), "tracked": item in files}
        for item in GENERATED_OUTPUT_FILES
    ]

    result = {
        "status": STATUS_READY,
        "audit_status": AUDIT_READY,
        "current_date": effective_date,
        "repo_root": str(root),
        "tracked_file_count": len(files),
        "active_runtime_module_count": len(runtime_modules),
        "active_runtime_modules": runtime_modules,
        "versioned_module_count": len(versioned_modules),
        "versioned_non_report_module_count": len(versioned_non_report_modules),
        "versioned_report_module_count": len(versioned_report_modules),
        "versioned_test_count": len(versioned_tests),
        "data_fixture_count": len(data_fixtures),
        "legacy_candidate_count": len(legacy_candidates),
        "legacy_candidates_sample": legacy_candidates[:25],
        "local_only_files": local_file_status,
        "generated_output_files": generated_output_status,
        "active_commands": ACTIVE_DAILY_MONTHLY_COMMANDS,
        "recommended_next_actions": [
            "Do not delete files in this audit stage.",
            "Keep jarvis/runtime as the active product surface.",
            "Keep jarvis_operator.py as the operator entrypoint.",
            "Treat jarvis/jarvis_v*.py and matching historical tests as legacy candidates until dependency audit confirms no active import path.",
            "Create a later archive/removal plan only after import-closure and test-coverage proof.",
        ],
        "deletion_performed": False,
        "runtime_behavior_mutation": False,
        "allocation_mutation": False,
        "approval_ticket_mutation": False,
        "buy_request_created": False,
        "broker_connection_forbidden": True,
        "credentials_forbidden": True,
        "private_account_data_ingestion_forbidden": True,
        "order_creation_forbidden": True,
        "no_trades_executed": True,
        "blockers": [],
        "warnings": [
            "repository contains many historical versioned modules; cleanup should be staged and audit-backed",
            "do not remove legacy modules until import-closure confirms they are inactive",
        ],
    }

    if write_report:
        resolved_report = root / report_path
        resolved_report.parent.mkdir(parents=True, exist_ok=True)
        resolved_report.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        result["report_written"] = True
        result["report_path"] = str(report_path)
        result["generated_output_files"] = [
            {"path": item, "exists": _path_exists(root, item), "tracked": item in files}
            for item in GENERATED_OUTPUT_FILES
        ]
    else:
        result["report_written"] = False
        result["report_path"] = str(report_path)

    return result


def format_active_runtime_surface_redundancy_audit(result: Mapping[str, Any]) -> str:
    lines = [
        "J.A.R.V.I.S. ACTIVE RUNTIME SURFACE + REDUNDANCY AUDIT",
        f"status: {result['status']}",
        f"audit status: {result['audit_status']}",
        f"current date: {result['current_date']}",
        f"tracked file count: {result['tracked_file_count']}",
        f"active runtime module count: {result['active_runtime_module_count']}",
        f"versioned module count: {result['versioned_module_count']}",
        f"versioned non-report module count: {result['versioned_non_report_module_count']}",
        f"versioned report module count: {result['versioned_report_module_count']}",
        f"versioned test count: {result['versioned_test_count']}",
        f"data fixture count: {result['data_fixture_count']}",
        f"legacy candidate count: {result['legacy_candidate_count']}",
        f"report written: {result['report_written']}",
        f"report path: {result['report_path']}",
        "",
        "Active runtime modules:",
    ]
    lines.extend(f"- {item}" for item in result["active_runtime_modules"])
    lines.extend(["", "Active operator commands:"])
    lines.extend(f"- {item}" for item in result["active_commands"])
    lines.extend(["", "Local-only files:"])
    for item in result["local_only_files"]:
        lines.append(f"- {item['path']}: exists={item['exists']}; tracked={item['tracked']}; expected tracked={item['expected_tracked']}")
    lines.extend(["", "Generated output files:"])
    for item in result["generated_output_files"]:
        lines.append(f"- {item['path']}: exists={item['exists']}; tracked={item['tracked']}")
    lines.extend(["", "Legacy candidate sample:"])
    lines.extend(f"- {item}" for item in result["legacy_candidates_sample"])
    lines.extend([
        "",
        "Recommended next actions:",
    ])
    lines.extend(f"- {item}" for item in result["recommended_next_actions"])
    lines.extend([
        "",
        "Safety:",
        f"- deletion performed: {result['deletion_performed']}",
        f"- runtime behavior mutation: {result['runtime_behavior_mutation']}",
        f"- allocation mutation: {result['allocation_mutation']}",
        f"- approval ticket mutation: {result['approval_ticket_mutation']}",
        f"- buy request created: {result['buy_request_created']}",
        "- no broker connection",
        "- no credentials",
        "- no private account data ingestion",
        "- no orders created",
        "- no trades executed",
    ])
    if result["blockers"]:
        lines.extend(["", "Blockers:"] + [f"- {item}" for item in result["blockers"]])
    else:
        lines.append("blockers: none")
    if result["warnings"]:
        lines.extend(["", "Warnings:"] + [f"- {item}" for item in result["warnings"]])
    else:
        lines.append("warnings: none")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="J.A.R.V.I.S. v63 active runtime surface redundancy audit")
    parser.add_argument("--active-runtime-surface-redundancy-audit", action="store_true")
    parser.add_argument("--write-active-runtime-surface-audit", action="store_true")
    parser.add_argument("--current-date", default=None)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--report-path", default=DEFAULT_REPORT_PATH)
    parser.add_argument("--safety-check", action="store_true")
    args = parser.parse_args(argv)
    if args.safety_check:
        print(build_safety_check_console_output())
        return 0
    result = build_active_runtime_surface_redundancy_audit_result(
        current_date=args.current_date,
        repo_root=args.repo_root,
        write_report=args.write_active_runtime_surface_audit,
        report_path=args.report_path,
    )
    print(format_active_runtime_surface_redundancy_audit(result))
    return 0


__all__ = [
    "AUDIT_READY",
    "DEFAULT_REPORT_PATH",
    "STATUS_READY",
    "build_active_runtime_surface_redundancy_audit_result",
    "format_active_runtime_surface_redundancy_audit",
    "main",
]
