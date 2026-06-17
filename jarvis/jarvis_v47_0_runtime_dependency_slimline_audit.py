"""J.A.R.V.I.S. v47.0 runtime dependency slimline audit.

This is a cleanup-only audit stage.

It scans Python import relationships from the active root operator and produces a
runtime dependency closure. It does not delete, archive, or change runtime
behavior. The goal is to identify which old stage modules are still part of the
active runtime path and which are legacy candidates for a later slimline stage.
"""

from __future__ import annotations

import argparse
import ast
import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Iterable, Mapping

STATUS_READY = "JARVIS_V47_0_RUNTIME_DEPENDENCY_SLIMLINE_AUDIT_READY_SAFE"
STATUS_REVIEW_REQUIRED = "JARVIS_V47_0_RUNTIME_DEPENDENCY_SLIMLINE_AUDIT_REVIEW_REQUIRED_SAFE"
STATUS_BLOCKED = "JARVIS_V47_0_RUNTIME_DEPENDENCY_SLIMLINE_AUDIT_BLOCKED_SAFE"

AUDIT_READY = "RUNTIME_DEPENDENCY_SLIMLINE_AUDIT_READY"
AUDIT_REVIEW_REQUIRED = "RUNTIME_DEPENDENCY_SLIMLINE_AUDIT_REVIEW_REQUIRED"
AUDIT_BLOCKED = "RUNTIME_DEPENDENCY_SLIMLINE_AUDIT_BLOCKED"

NEXT_STAGE = "runtime_dependency_slimline_no_behavior_change"
DEFAULT_ENTRY_FILE = "jarvis_operator.py"
DEFAULT_REPORT_PATH = "outputs/runtime_dependency_slimline_audit_latest.json"


@dataclass(frozen=True)
class RuntimeDependencySlimlineAuditResult:
    status: str
    audit_status: str
    recommended_next_stage: str
    current_date: str
    entry_file: str
    report_path: str
    report_written: bool
    active_module_count: int
    active_version_module_count: int
    total_version_module_count: int
    legacy_candidate_count: int
    active_modules: tuple[str, ...]
    active_version_modules: tuple[str, ...]
    legacy_candidate_modules: tuple[str, ...]
    missing_imports: tuple[str, ...]
    parse_failures: tuple[str, ...]
    audit_only: bool
    runtime_behavior_mutation: bool
    deletion_performed: bool
    broker_connection_forbidden: bool
    order_creation_forbidden: bool
    no_trades_executed: bool
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "audit_status": self.audit_status,
            "recommended_next_stage": self.recommended_next_stage,
            "current_date": self.current_date,
            "entry_file": self.entry_file,
            "report_path": self.report_path,
            "report_written": self.report_written,
            "active_module_count": self.active_module_count,
            "active_version_module_count": self.active_version_module_count,
            "total_version_module_count": self.total_version_module_count,
            "legacy_candidate_count": self.legacy_candidate_count,
            "active_modules": list(self.active_modules),
            "active_version_modules": list(self.active_version_modules),
            "legacy_candidate_modules": list(self.legacy_candidate_modules),
            "missing_imports": list(self.missing_imports),
            "parse_failures": list(self.parse_failures),
            "audit_only": self.audit_only,
            "runtime_behavior_mutation": self.runtime_behavior_mutation,
            "deletion_performed": self.deletion_performed,
            "broker_connection_forbidden": self.broker_connection_forbidden,
            "order_creation_forbidden": self.order_creation_forbidden,
            "no_trades_executed": self.no_trades_executed,
            "blockers": list(self.blockers),
            "warnings": list(self.warnings),
        }


def _today_iso() -> str:
    return date.today().isoformat()


def _resolve_path(path: str | Path, root: str | Path) -> Path:
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    return Path(root) / candidate


def _is_under(path: Path, root: str | Path, child: str) -> bool:
    resolved = path.resolve()
    allowed_root = (Path(root) / child).resolve()
    try:
        resolved.relative_to(allowed_root)
        return True
    except ValueError:
        return False


def _module_name_for_file(path: Path, root: Path) -> str | None:
    try:
        rel = path.resolve().relative_to(root.resolve())
    except ValueError:
        return None
    if rel.suffix != ".py":
        return None
    parts = list(rel.with_suffix("").parts)
    if parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


def _file_for_module(module_name: str, root: Path) -> Path | None:
    if module_name == "jarvis_operator":
        candidate = root / "jarvis_operator.py"
    else:
        candidate = root / Path(*module_name.split(".")).with_suffix(".py")
    if candidate.exists():
        return candidate
    package_init = root / Path(*module_name.split(".")) / "__init__.py"
    if package_init.exists():
        return package_init
    return None


def _package_for_module(module_name: str) -> str:
    parts = module_name.split(".")
    if parts[-1] == "__init__":
        parts = parts[:-1]
    if len(parts) <= 1:
        return ""
    return ".".join(parts[:-1])


def _resolve_relative_import(current_module: str, imported_module: str | None, level: int) -> str | None:
    if level <= 0:
        return imported_module
    package_parts = _package_for_module(current_module).split(".") if _package_for_module(current_module) else []
    if level > len(package_parts) + 1:
        return None
    base_parts = package_parts[: len(package_parts) - level + 1]
    imported_parts = imported_module.split(".") if imported_module else []
    return ".".join(part for part in [*base_parts, *imported_parts] if part)


def _iter_internal_imports(tree: ast.AST, current_module: str) -> Iterable[str]:
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                module = alias.name
                if module == "jarvis" or module.startswith("jarvis."):
                    yield module
        elif isinstance(node, ast.ImportFrom):
            module = _resolve_relative_import(current_module, node.module, node.level)
            if not module:
                continue
            if module == "jarvis" or module.startswith("jarvis.") or module == "jarvis_operator":
                yield module


def _dedupe_sorted(items: Iterable[str]) -> tuple[str, ...]:
    return tuple(sorted(dict.fromkeys(str(item) for item in items if str(item))))


def _discover_import_closure(root: Path, entry_file: Path) -> tuple[set[str], tuple[str, ...], tuple[str, ...]]:
    entry_module = _module_name_for_file(entry_file, root)
    if not entry_module:
        return set(), (), (f"could not determine module name for {entry_file}")

    active: set[str] = set()
    missing: list[str] = []
    parse_failures: list[str] = []
    queue: list[str] = [entry_module]

    while queue:
        module_name = queue.pop(0)
        if module_name in active:
            continue
        active.add(module_name)
        path = _file_for_module(module_name, root)
        if path is None:
            missing.append(module_name)
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))
        except (SyntaxError, OSError, UnicodeDecodeError) as exc:
            parse_failures.append(f"{module_name}: {exc}")
            continue
        for imported in _iter_internal_imports(tree, module_name):
            resolved = imported
            if _file_for_module(resolved, root) is not None and resolved not in active and resolved not in queue:
                queue.append(resolved)
            elif _file_for_module(resolved, root) is None:
                missing.append(resolved)

    return active, _dedupe_sorted(missing), _dedupe_sorted(parse_failures)


def _discover_version_modules(root: Path) -> tuple[str, ...]:
    modules: list[str] = []
    jarvis_dir = root / "jarvis"
    for path in sorted(jarvis_dir.glob("jarvis_v*.py")):
        module_name = _module_name_for_file(path, root)
        if module_name:
            modules.append(module_name)
    return tuple(modules)


def _write_report(result: RuntimeDependencySlimlineAuditResult, root: Path, report_path: Path) -> None:
    if not _is_under(report_path, root, "outputs"):
        raise ValueError("runtime dependency audit report path must remain under outputs/.")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(result.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_runtime_dependency_slimline_audit_result(
    *,
    current_date: str | None = None,
    root: str | Path = ".",
    entry_file: str | Path = DEFAULT_ENTRY_FILE,
    report_path: str | Path = DEFAULT_REPORT_PATH,
    write_report: bool = False,
) -> RuntimeDependencySlimlineAuditResult:
    root_path = Path(root)
    current_date_text = current_date or _today_iso()
    resolved_entry = _resolve_path(entry_file, root_path)
    resolved_report = _resolve_path(report_path, root_path)
    blockers: list[str] = []
    warnings: list[str] = []

    if not resolved_entry.exists():
        blockers.append(f"entry file does not exist: {entry_file}")
    if write_report and not _is_under(resolved_report, root_path, "outputs"):
        blockers.append("runtime dependency audit report path must remain under outputs/.")

    active_modules: set[str] = set()
    missing_imports: tuple[str, ...] = ()
    parse_failures: tuple[str, ...] = ()
    if not blockers:
        active_modules, missing_imports, parse_failures = _discover_import_closure(root_path, resolved_entry)

    all_version_modules = _discover_version_modules(root_path)
    active_version_modules = tuple(module for module in all_version_modules if module in active_modules)
    legacy_candidate_modules = tuple(module for module in all_version_modules if module not in active_modules)

    if missing_imports:
        warnings.append(f"{len(missing_imports)} internal import(s) could not be resolved.")
    if parse_failures:
        warnings.append(f"{len(parse_failures)} file(s) could not be parsed.")
    if not active_version_modules and not blockers:
        warnings.append("no active jarvis_v*.py modules were discovered from entry file.")

    report_written = False

    preliminary_blockers = _dedupe_sorted(blockers)
    preliminary_warnings = _dedupe_sorted(warnings)
    status = STATUS_BLOCKED if preliminary_blockers else STATUS_REVIEW_REQUIRED if preliminary_warnings else STATUS_READY
    audit_status = AUDIT_BLOCKED if preliminary_blockers else AUDIT_REVIEW_REQUIRED if preliminary_warnings else AUDIT_READY

    result = RuntimeDependencySlimlineAuditResult(
        status=status,
        audit_status=audit_status,
        recommended_next_stage=NEXT_STAGE,
        current_date=current_date_text,
        entry_file=str(resolved_entry),
        report_path=str(resolved_report),
        report_written=False,
        active_module_count=len(active_modules),
        active_version_module_count=len(active_version_modules),
        total_version_module_count=len(all_version_modules),
        legacy_candidate_count=len(legacy_candidate_modules),
        active_modules=_dedupe_sorted(active_modules),
        active_version_modules=tuple(active_version_modules),
        legacy_candidate_modules=tuple(legacy_candidate_modules),
        missing_imports=missing_imports,
        parse_failures=parse_failures,
        audit_only=True,
        runtime_behavior_mutation=False,
        deletion_performed=False,
        broker_connection_forbidden=True,
        order_creation_forbidden=True,
        no_trades_executed=True,
        blockers=preliminary_blockers,
        warnings=preliminary_warnings,
    )

    if write_report and not preliminary_blockers:
        _write_report(result, root_path, resolved_report)
        report_written = True
        result = RuntimeDependencySlimlineAuditResult(
            **{**result.to_dict(), "report_written": report_written}
        )

    return result


def format_runtime_dependency_slimline_audit(result: RuntimeDependencySlimlineAuditResult) -> str:
    lines = [
        "J.A.R.V.I.S. Runtime Dependency Slimline Audit",
        f"status: {result.status}",
        f"audit status: {result.audit_status}",
        f"current date: {result.current_date}",
        f"entry file: {result.entry_file}",
        f"report path: {result.report_path}",
        f"report written: {result.report_written}",
        f"active module count: {result.active_module_count}",
        f"active version module count: {result.active_version_module_count}",
        f"total version module count: {result.total_version_module_count}",
        f"legacy candidate count: {result.legacy_candidate_count}",
        "",
        "Audit policy:",
        "- audit-only stage",
        "- no runtime behavior change",
        "- no file deletion",
        "- no broker path",
        "- no order path",
        "- no trades",
        "",
        "Active version modules:",
    ]

    if result.active_version_modules:
        lines.extend(f"- {module}" for module in result.active_version_modules[:40])
        if len(result.active_version_modules) > 40:
            lines.append(f"- ... {len(result.active_version_modules) - 40} more")
    else:
        lines.append("- none")

    lines.extend(["", "Legacy candidate modules not in active runtime closure:"])
    if result.legacy_candidate_modules:
        lines.extend(f"- {module}" for module in result.legacy_candidate_modules[:40])
        if len(result.legacy_candidate_modules) > 40:
            lines.append(f"- ... {len(result.legacy_candidate_modules) - 40} more")
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "Safety:",
            f"- audit only: {result.audit_only}",
            f"- runtime behavior mutation: {result.runtime_behavior_mutation}",
            f"- deletion performed: {result.deletion_performed}",
            "- no broker connection",
            "- no orders created",
            "- no trades executed",
        ]
    )

    if result.blockers:
        lines.extend(["", "Blockers:"])
        lines.extend(f"- {blocker}" for blocker in result.blockers)
    else:
        lines.append("blockers: none")

    if result.warnings:
        lines.extend(["", "Warnings:"])
        lines.extend(f"- {warning}" for warning in result.warnings)
    else:
        lines.append("warnings: none")

    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit active J.A.R.V.I.S. runtime dependency closure.")
    parser.add_argument("--current-date", default=None)
    parser.add_argument("--entry-file", default=DEFAULT_ENTRY_FILE)
    parser.add_argument("--report-path", default=DEFAULT_REPORT_PATH)
    parser.add_argument("--write-report", action="store_true")
    args = parser.parse_args(argv)

    result = build_runtime_dependency_slimline_audit_result(
        current_date=args.current_date,
        entry_file=args.entry_file,
        report_path=args.report_path,
        write_report=args.write_report,
    )
    print(format_runtime_dependency_slimline_audit(result))
    return 0 if result.status != STATUS_BLOCKED else 1


if __name__ == "__main__":
    raise SystemExit(main())