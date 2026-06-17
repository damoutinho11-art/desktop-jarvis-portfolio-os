from __future__ import annotations

import unittest
from pathlib import Path

from jarvis.runtime.import_closure_safe_archive_plan import (
    build_import_closure_safe_archive_plan_result,
)
from jarvis.runtime.next_safe_python_archive_execution_plan import (
    build_next_safe_python_archive_execution_plan_result,
)

ARCHIVE_ROOT = Path("archive/non_active/v72_next_safe_python_safe")


class JarvisV730NextSafePythonArchiveExecutionTests(unittest.TestCase):
    def test_known_next_safe_files_were_moved_reversibly(self) -> None:
        known_pairs = [
            (
                "jarvis/jarvis_v13_0_single_command_operator_launcher.py",
                "jarvis/tests/test_jarvis_v13_0_single_command_operator_launcher.py",
            ),
            (
                "jarvis/jarvis_v47_0_runtime_dependency_slimline_audit.py",
                "jarvis/tests/test_jarvis_v47_0_runtime_dependency_slimline_audit.py",
            ),
            (
                "jarvis/jarvis_v9_0_public_market_data_enablement_decision_layer.py",
                "jarvis/tests/test_jarvis_v9_0_public_market_data_enablement_decision_layer.py",
            ),
        ]

        for module, test in known_pairs:
            self.assertFalse(Path(module).exists(), module)
            self.assertFalse(Path(test).exists(), test)
            self.assertTrue((ARCHIVE_ROOT / module).exists(), module)
            self.assertTrue((ARCHIVE_ROOT / test).exists(), test)

    def test_active_import_closure_remains_resolved_and_does_not_use_archive(self) -> None:
        result = build_import_closure_safe_archive_plan_result(current_date="2026-06-17")

        self.assertEqual(result["unresolved_local_import_count"], 0)
        self.assertFalse(result["deletion_performed"])
        self.assertFalse(result["archive_performed"])
        self.assertFalse(result["buy_request_created"])

        active_paths = result["active_import_closure_paths"]
        self.assertTrue(active_paths)
        self.assertTrue(all(not path.startswith("archive/") for path in active_paths))

    def test_next_safe_plan_is_empty_after_execution(self) -> None:
        result = build_next_safe_python_archive_execution_plan_result(current_date="2026-06-17")

        self.assertEqual(result.unresolved_local_import_count, 0)
        self.assertEqual(result.next_safe_module_source_count, 0)
        self.assertEqual(result.paired_next_safe_test_count, 0)
        self.assertEqual(result.total_plan_item_count, 0)
        self.assertEqual(result.blockers, [])

    def test_orphan_tests_for_active_modules_remain_in_place(self) -> None:
        self.assertTrue(Path("jarvis/tests/test_jarvis_v10_0_autonomous_public_data_refresh_runtime.py").exists())
        self.assertTrue(Path("jarvis/tests/test_jarvis_v43_0_free_research_api_router_weekly_policy.py").exists())
        self.assertTrue(Path("jarvis/tests/test_jarvis_v45_0_free_research_cache_evidence_pack_bridge.py").exists())


if __name__ == "__main__":
    unittest.main()
