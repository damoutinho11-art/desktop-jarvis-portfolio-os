"""J.A.R.V.I.S. v64.0 import closure + safe archive plan.

Audit-only module. It maps the active import closure from the current operator
surface and separates actively imported files from legacy archive candidates.

Safety invariant: Automated research. Manual trust. Manual approval. No execution.
"""

from __future__ import annotations

import argparse
import ast
import json
import subprocess
from datetime import date
from pathlib import Path
from typing import Any, Mapping

from jarvis.jarvis_v16_0_real_daily_readiness_gate import build_safety_check_console_output

STATUS_READY = "JARVIS_V64_0_IMPORT_CLOSURE_SAFE_ARCHIVE_PLAN_READY_SAFE"
AUDIT_READY = "IMPORT_CLOSURE_SAFE_ARCHIVE_PLAN_READY"

DEFAULT_REPORT_PATH = "outputs/import_closure_safe_archive_plan_latest.json"

ROOT_IMPORT_PATHS = [
    "jarvis_operator.py",
    "jarvis/runtime/operator.py",
]

ACTIVE_RUNTIME_DIR = "jarvis/runtime"

CURRENT_VALIDATION_COMMANDS = [
    "python -m unittest discover -s .\\jarvis\\tests -p \"test_jarvis_v5*.py\"",
    "python -m unittest discover -s .\\jarvis\\tests -p \"test_jarvis_v60*.py\"",
    "python -m unittest discover -s .\\jarvis\\tests -p \"test_jarvis_v61*.py\"",
    "python -m unittest discover -s .\\jarvis\\tests -p \"test_jarvis_v62*.py\"",
    "python -m unittest discover -s .\\jarvis\\tests -p \"test_jarvis_v63*.py\"",
    "python -m unittest discover -s .\\jarvis\\tests -p \"test_jarvis_v64*.py\"",
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


def _tracked_python_files(files: list[str]) -> list[str]:
    return sorted(path for path in files if path.endswith(".py"))


def _module_to_path(module_name: str) -> str | None:
    if not module_name.startswith("jarvis"):
        return None
    parts = module_name.split(".")
    if parts == ["jarvis"]:
        return "jarvis/__init__.py"
    return "/".join(parts) + ".py"


def _is_versioned_module(path: str) -> bool:
    name = Path(path).name
    return path.startswith("jarvis/") and name.startswith("jarvis_v") and name.endswith(".py")


def _is_runtime_module(path: str) -> bool:
    return path.startswith("jarvis/runtime/") and path.endswith(".py")


def _is_versioned_test(path: str) -> bool:
    name = Path(path).name
    return path.startswith("jarvis/tests/") and name.startswith("test_jarvis_v") and name.endswith(".py")


def _is_data_fixture(path: str) -> bool:
    return path.startswith("jarvis/data/") and "jarvis_v" in Path(path).name


def _parse_local_imports(path: Path) -> set[str]:
    if not path.exists() or not path.is_file():
        return set()
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (SyntaxError, UnicodeDecodeError, OSError):
        return set()

    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                candidate = _module_to_path(alias.name)
                if candidate:
                    imports.add(candidate)
        elif isinstance(node, ast.ImportFrom):
            if not node.module:
                continue
            candidate = _module_to_path(node.module)
            if candidate:
                imports.add(candidate)
    return imports


def _active_runtime_roots(files: list[str]) -> list[str]:
    roots = set(ROOT_IMPORT_PATHS)
    roots.update(path for path in files if _is_runtime_module(path))
    return sorted(path for path in roots if path in files)


def _resolve_import_closure(root: Path, files: list[str], roots: list[str]) -> tuple[list[str], list[dict[str, Any]]]:
    tracked = set(files)
    closure: set[str] = set()
    unresolved: list[dict[str, Any]] = []
    queue = list(roots)

    while queue:
        current = queue.pop(0).replace("\\", "/")
        if current in closure:
            continue
        if current not in tracked:
            unresolved.append({"from": None, "import_path": current, "reason": "not tracked"})
            continue

        closure.add(current)
        imported_paths = _parse_local_imports(root / current)
        for imported in sorted(imported_paths):
            if imported in tracked and imported not in closure:
                queue.append(imported)
            elif imported not in tracked:
                # Try package __init__.py fallback for imports such as jarvis.runtime
                if imported.endswith(".py"):
                    package_init = imported[:-3] + "/__init__.py"
                    if package_init in tracked and package_init not in closure:
                        queue.append(package_init)
                    elif imported.startswith("jarvis/"):
                        unresolved.append({"from": current, "import_path": imported, "reason": "local import not tracked"})
    return sorted(closure), unresolved


def _test_stem_for_versioned_module(module_path: str) -> str:
    stem = Path(module_path).stem
    return "test_" + stem


def _active_versioned_test_candidates(active_versioned_modules: list[str], versioned_tests: list[str]) -> list[str]:
    active_test_stems = {_test_stem_for_versioned_module(path) for path in active_versioned_modules}
    return sorted(path for path in versioned_tests if Path(path).stem in active_test_stems)


def build_import_closure_safe_archive_plan_result(
    *,
    current_date: str | None = None,
    repo_root: str | Path = ".",
    write_report: bool = False,
    report_path: str | Path = DEFAULT_REPORT_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    effective_date = current_date or _today_iso()
    files = _git_ls_files(root)

    python_files = _tracked_python_files(files)
    runtime_roots = _active_runtime_roots(files)
    closure_paths, unresolved_imports = _resolve_import_closure(root, files, runtime_roots)

    runtime_modules = sorted(path for path in files if _is_runtime_module(path))
    versioned_modules = sorted(path for path in files if _is_versioned_module(path))
    versioned_tests = sorted(path for path in files if _is_versioned_test(path))
    data_fixtures = sorted(path for path in files if _is_data_fixture(path))

    active_versioned_modules = sorted(path for path in closure_paths if _is_versioned_module(path))
    active_versioned_tests = _active_versioned_test_candidates(active_versioned_modules, versioned_tests)

    legacy_module_archive_candidates = sorted(path for path in versioned_modules if path not in closure_paths)
    legacy_test_archive_candidates = sorted(path for path in versioned_tests if path not in active_versioned_tests)
    data_fixture_archive_candidates = sorted(data_fixtures)

    result = {
        "status": STATUS_READY,
        "audit_status": AUDIT_READY,
        "current_date": effective_date,
        "repo_root": str(root),
        "tracked_file_count": len(files),
        "tracked_python_file_count": len(python_files),
        "active_runtime_root_count": len(runtime_roots),
        "active_runtime_roots": runtime_roots,
        "active_import_closure_count": len(closure_paths),
        "active_import_closure_paths": closure_paths,
        "active_runtime_module_count": len(runtime_modules),
        "active_runtime_modules": runtime_modules,
        "active_versioned_module_count": len(active_versioned_modules),
        "active_versioned_modules": active_versioned_modules,
        "active_versioned_test_count": len(active_versioned_tests),
        "active_versioned_tests": active_versioned_tests,
        "versioned_module_count": len(versioned_modules),
        "versioned_test_count": len(versioned_tests),
        "data_fixture_count": len(data_fixtures),
        "legacy_module_archive_candidate_count": len(legacy_module_archive_candidates),
        "legacy_module_archive_candidates_sample": legacy_module_archive_candidates[:40],
        "legacy_test_archive_candidate_count": len(legacy_test_archive_candidates),
        "legacy_test_archive_candidates_sample": legacy_test_archive_candidates[:40],
        "data_fixture_archive_candidate_count": len(data_fixture_archive_candidates),
        "data_fixture_archive_candidates_sample": data_fixture_archive_candidates[:25],
        "unresolved_local_import_count": len(unresolved_imports),
        "unresolved_local_imports_sample": unresolved_imports[:25],
        "current_validation_commands": CURRENT_VALIDATION_COMMANDS,
        "safe_archive_plan": [
            "Do not delete or move files in v64.",
            "Keep jarvis_operator.py and jarvis/runtime/* as the active product surface.",
            "Keep every path in active_import_closure_paths.",
            "Do not remove active_versioned_modules; they are still imported by active runtime.",
            "Treat legacy_module_archive_candidates as candidates only, not as approved deletions.",
            "Before any v65 archive/removal, run full regression and create a reversible branch/commit.",
            "Archive tests only after equivalent active-runtime tests exist.",
        ],
        "deletion_performed": False,
        "archive_performed": False,
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
            "archive candidates are advisory only; no deletion is approved by this audit",
            "active versioned modules must remain until active runtime is fully decoupled",
        ],
        "report_written": False,
        "report_path": str(report_path),
    }

    if write_report:
        resolved_report = root / report_path
        resolved_report.parent.mkdir(parents=True, exist_ok=True)
        resolved_report.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        result["report_written"] = True

    return result


def format_import_closure_safe_archive_plan(result: Mapping[str, Any]) -> str:
    lines = [
        "J.A.R.V.I.S. IMPORT CLOSURE + SAFE ARCHIVE PLAN",
        f"status: {result['status']}",
        f"audit status: {result['audit_status']}",
        f"current date: {result['current_date']}",
        f"tracked file count: {result['tracked_file_count']}",
        f"tracked python file count: {result['tracked_python_file_count']}",
        f"active runtime root count: {result['active_runtime_root_count']}",
        f"active import closure count: {result['active_import_closure_count']}",
        f"active runtime module count: {result['active_runtime_module_count']}",
        f"active versioned module count: {result['active_versioned_module_count']}",
        f"active versioned test count: {result['active_versioned_test_count']}",
        f"versioned module count: {result['versioned_module_count']}",
        f"versioned test count: {result['versioned_test_count']}",
        f"data fixture count: {result['data_fixture_count']}",
        f"legacy module archive candidate count: {result['legacy_module_archive_candidate_count']}",
        f"legacy test archive candidate count: {result['legacy_test_archive_candidate_count']}",
        f"data fixture archive candidate count: {result['data_fixture_archive_candidate_count']}",
        f"unresolved local import count: {result['unresolved_local_import_count']}",
        f"report written: {result['report_written']}",
        f"report path: {result['report_path']}",
        "",
        "Active runtime roots:",
    ]
    lines.extend(f"- {item}" for item in result["active_runtime_roots"])
    lines.extend(["", "Active versioned modules still imported:"])
    if result["active_versioned_modules"]:
        lines.extend(f"- {item}" for item in result["active_versioned_modules"])
    else:
        lines.append("- none")
    lines.extend(["", "Legacy module archive candidate sample:"])
    lines.extend(f"- {item}" for item in result["legacy_module_archive_candidates_sample"])
    lines.extend(["", "Legacy test archive candidate sample:"])
    lines.extend(f"- {item}" for item in result["legacy_test_archive_candidates_sample"])
    lines.extend(["", "Current validation commands:"])
    lines.extend(f"- {item}" for item in result["current_validation_commands"])
    lines.extend(["", "Safe archive plan:"])
    lines.extend(f"- {item}" for item in result["safe_archive_plan"])
    lines.extend([
        "",
        "Safety:",
        f"- deletion performed: {result['deletion_performed']}",
        f"- archive performed: {result['archive_performed']}",
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
    parser = argparse.ArgumentParser(description="J.A.R.V.I.S. v64 import closure safe archive plan")
    parser.add_argument("--import-closure-safe-archive-plan", action="store_true")
    parser.add_argument("--write-import-closure-safe-archive-plan", action="store_true")
    parser.add_argument("--current-date", default=None)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--report-path", default=DEFAULT_REPORT_PATH)
    parser.add_argument("--safety-check", action="store_true")
    args = parser.parse_args(argv)
    if args.safety_check:
        print(build_safety_check_console_output())
        return 0
    result = build_import_closure_safe_archive_plan_result(
        current_date=args.current_date,
        repo_root=args.repo_root,
        write_report=args.write_import_closure_safe_archive_plan,
        report_path=args.report_path,
    )
    print(format_import_closure_safe_archive_plan(result))
    return 0


__all__ = [
    "AUDIT_READY",
    "DEFAULT_REPORT_PATH",
    "STATUS_READY",
    "build_import_closure_safe_archive_plan_result",
    "format_import_closure_safe_archive_plan",
    "main",
]
