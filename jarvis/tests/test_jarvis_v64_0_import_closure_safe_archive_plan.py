from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from jarvis.runtime.import_closure_safe_archive_plan import (
    DEFAULT_REPORT_PATH,
    build_import_closure_safe_archive_plan_result,
    format_import_closure_safe_archive_plan,
)


class JarvisV640ImportClosureSafeArchivePlanTests(unittest.TestCase):
    def test_import_closure_audit_is_safe_and_read_only(self) -> None:
        result = build_import_closure_safe_archive_plan_result(
            current_date="2026-06-17",
            repo_root=".",
            write_report=False,
        )

        self.assertEqual(
            result["status"],
            "JARVIS_V64_0_IMPORT_CLOSURE_SAFE_ARCHIVE_PLAN_READY_SAFE",
        )
        self.assertGreaterEqual(result["tracked_file_count"], 1)
        self.assertIn("jarvis/runtime/operator.py", result["active_runtime_roots"])
        self.assertIn("jarvis/runtime/operator.py", result["active_import_closure_paths"])
        self.assertFalse(result["deletion_performed"])
        self.assertFalse(result["archive_performed"])
        self.assertFalse(result["runtime_behavior_mutation"])
        self.assertFalse(result["allocation_mutation"])
        self.assertFalse(result["approval_ticket_mutation"])
        self.assertFalse(result["buy_request_created"])
        self.assertTrue(result["broker_connection_forbidden"])
        self.assertTrue(result["credentials_forbidden"])
        self.assertTrue(result["order_creation_forbidden"])
        self.assertTrue(result["no_trades_executed"])

    def test_report_write_is_generated_and_reversible(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "jarvis" / "runtime").mkdir(parents=True)
            (root / "jarvis" / "__init__.py").write_text("", encoding="utf-8")
            (root / "jarvis" / "runtime" / "__init__.py").write_text("", encoding="utf-8")
            (root / "jarvis_operator.py").write_text("from jarvis.runtime.operator import main\n", encoding="utf-8")
            (root / "jarvis" / "runtime" / "operator.py").write_text("def main():\n    return 0\n", encoding="utf-8")

            result = build_import_closure_safe_archive_plan_result(
                current_date="2026-06-17",
                repo_root=root,
                write_report=True,
                report_path=DEFAULT_REPORT_PATH,
            )

            self.assertTrue(result["report_written"])
            self.assertTrue((root / DEFAULT_REPORT_PATH).exists())
            self.assertFalse(result["deletion_performed"])
            self.assertFalse(result["archive_performed"])

    def test_formatter_states_candidates_are_not_deletions(self) -> None:
        result = build_import_closure_safe_archive_plan_result(
            current_date="2026-06-17",
            repo_root=".",
            write_report=False,
        )
        formatted = format_import_closure_safe_archive_plan(result)

        self.assertIn("IMPORT CLOSURE + SAFE ARCHIVE PLAN", formatted)
        self.assertIn("deletion performed: False", formatted)
        self.assertIn("archive performed: False", formatted)
        self.assertIn("candidates only", formatted.lower())
        self.assertIn("no broker connection", formatted.lower())


if __name__ == "__main__":
    unittest.main()
