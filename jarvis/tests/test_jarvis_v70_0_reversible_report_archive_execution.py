from __future__ import annotations

import unittest
from pathlib import Path

from jarvis.runtime.import_closure_safe_archive_plan import (
    build_import_closure_safe_archive_plan_result,
)

ARCHIVE_ROOT = Path("archive/non_active/v70_report_only_python_safe")


class JarvisV700ReversibleReportArchiveExecutionTests(unittest.TestCase):
    def test_known_report_only_files_were_moved_reversibly(self) -> None:
        archived_module = ARCHIVE_ROOT / "jarvis/jarvis_v10_0_autonomous_public_data_refresh_runtime_report.py"
        archived_test = ARCHIVE_ROOT / "jarvis/tests/test_jarvis_v10_0_autonomous_public_data_refresh_runtime_report.py"

        self.assertTrue(archived_module.exists())
        self.assertTrue(archived_test.exists())
        self.assertFalse(Path("jarvis/jarvis_v10_0_autonomous_public_data_refresh_runtime_report.py").exists())
        self.assertFalse(Path("jarvis/tests/test_jarvis_v10_0_autonomous_public_data_refresh_runtime_report.py").exists())

    def test_active_import_closure_remains_resolved_and_does_not_use_archive(self) -> None:
        result = build_import_closure_safe_archive_plan_result(current_date="2026-06-17")

        self.assertEqual(result["unresolved_local_import_count"], 0)
        self.assertFalse(result["deletion_performed"])
        self.assertFalse(result["archive_performed"])
        self.assertFalse(result["buy_request_created"])
        # The import-closure audit does not expose order/trade keys directly;
        # execution safety is verified by the safety-check command.

        active_paths = result["active_import_closure_paths"]
        self.assertTrue(active_paths)
        self.assertTrue(all(not path.startswith("archive/") for path in active_paths))

    def test_current_validation_tests_remain_in_place(self) -> None:
        self.assertTrue(Path("jarvis/tests/test_jarvis_v69_0_reversible_archive_staging_plan.py").exists())
        self.assertTrue(Path("jarvis/tests/test_jarvis_v68_0_non_active_archive_candidate_report.py").exists())
        self.assertTrue(Path("jarvis/tests/test_jarvis_v67_0_import_closure_relative_import_precision.py").exists())


if __name__ == "__main__":
    unittest.main()
