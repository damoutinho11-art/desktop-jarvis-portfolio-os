from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from jarvis.jarvis_v47_0_runtime_dependency_slimline_audit import (
    STATUS_BLOCKED,
    STATUS_READY,
    build_runtime_dependency_slimline_audit_result,
    format_runtime_dependency_slimline_audit,
)


ROOT = Path(__file__).resolve().parents[2]


class JarvisV470RuntimeDependencySlimlineAuditTests(unittest.TestCase):
    def test_real_repo_discovers_active_v45_closure(self) -> None:
        result = build_runtime_dependency_slimline_audit_result(
            current_date="2026-06-17",
            root=ROOT,
        )

        self.assertEqual(result.status, STATUS_READY)
        self.assertIn("jarvis.jarvis_v45_0_free_research_cache_evidence_pack_bridge", result.active_modules)
        self.assertGreater(result.total_version_module_count, 0)
        self.assertGreater(result.legacy_candidate_count, 0)
        self.assertTrue(result.audit_only)
        self.assertFalse(result.deletion_performed)

    def test_temp_repo_resolves_relative_imports(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "jarvis").mkdir()
            (root / "jarvis" / "__init__.py").write_text("", encoding="utf-8")
            (root / "jarvis_operator.py").write_text(
                "from jarvis.jarvis_v2_active import main\n",
                encoding="utf-8",
            )
            (root / "jarvis" / "jarvis_v2_active.py").write_text(
                "from .jarvis_v1_base import helper\n"
                "def main():\n"
                "    return helper()\n",
                encoding="utf-8",
            )
            (root / "jarvis" / "jarvis_v1_base.py").write_text(
                "def helper():\n"
                "    return 1\n",
                encoding="utf-8",
            )
            (root / "jarvis" / "jarvis_v0_legacy.py").write_text("x = 1\n", encoding="utf-8")

            result = build_runtime_dependency_slimline_audit_result(
                current_date="2026-06-17",
                root=root,
            )

            self.assertEqual(result.status, STATUS_READY)
            self.assertIn("jarvis.jarvis_v2_active", result.active_version_modules)
            self.assertIn("jarvis.jarvis_v1_base", result.active_version_modules)
            self.assertIn("jarvis.jarvis_v0_legacy", result.legacy_candidate_modules)

    def test_write_report_under_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "jarvis").mkdir()
            (root / "outputs").mkdir()
            (root / "jarvis" / "__init__.py").write_text("", encoding="utf-8")
            (root / "jarvis_operator.py").write_text(
                "from jarvis.jarvis_v1_active import main\n",
                encoding="utf-8",
            )
            (root / "jarvis" / "jarvis_v1_active.py").write_text("def main():\n    return 0\n", encoding="utf-8")

            result = build_runtime_dependency_slimline_audit_result(
                current_date="2026-06-17",
                root=root,
                write_report=True,
            )

            self.assertEqual(result.status, STATUS_READY)
            self.assertTrue(result.report_written)
            payload = json.loads(Path(result.report_path).read_text(encoding="utf-8"))
            self.assertEqual(payload["status"], STATUS_READY)
            self.assertFalse(payload["deletion_performed"])

    def test_report_path_outside_outputs_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "jarvis_operator.py").write_text("x = 1\n", encoding="utf-8")

            result = build_runtime_dependency_slimline_audit_result(
                current_date="2026-06-17",
                root=root,
                report_path="jarvis/local/bad.json",
                write_report=True,
            )

            self.assertEqual(result.status, STATUS_BLOCKED)
            self.assertIn("runtime dependency audit report path must remain under outputs/.", result.blockers)

    def test_missing_entry_file_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = build_runtime_dependency_slimline_audit_result(
                current_date="2026-06-17",
                root=Path(tmp),
                entry_file="missing.py",
            )

            self.assertEqual(result.status, STATUS_BLOCKED)
            self.assertTrue(any("entry file does not exist" in blocker for blocker in result.blockers))

    def test_console_mentions_audit_only_safety(self) -> None:
        result = build_runtime_dependency_slimline_audit_result(
            current_date="2026-06-17",
            root=ROOT,
        )
        output = format_runtime_dependency_slimline_audit(result)

        self.assertIn("Runtime Dependency Slimline Audit", output)
        self.assertIn("audit-only stage", output)
        self.assertIn("no file deletion", output)
        self.assertIn("no broker connection", output)
        self.assertIn("no trades executed", output)


if __name__ == "__main__":
    unittest.main()