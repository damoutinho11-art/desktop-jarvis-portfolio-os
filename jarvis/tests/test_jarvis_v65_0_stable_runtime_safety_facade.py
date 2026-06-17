from __future__ import annotations

from pathlib import Path
import unittest

from jarvis.runtime.import_closure_safe_archive_plan import build_import_closure_safe_archive_plan_result
from jarvis.runtime.safety import (
    BLOCKED_EXECUTION_COMMAND,
    BLOCKED_EXECUTION_MESSAGE,
    build_safety_check_console_output,
)


class JarvisV650StableRuntimeSafetyFacadeTests(unittest.TestCase):
    def test_safety_output_is_stable_and_blocks_execution(self) -> None:
        output = build_safety_check_console_output()

        self.assertIn(BLOCKED_EXECUTION_COMMAND, output)
        self.assertIn(BLOCKED_EXECUTION_MESSAGE, output)
        self.assertIn("BLOCKED", output)
        self.assertIn("No execution action was taken", output)
        self.assertIn("Diogo must perform the final real-world buy outside the system", output)


    def test_runtime_safety_facade_is_active_and_direct_v16_import_is_removed(self) -> None:
        result = build_import_closure_safe_archive_plan_result(current_date="2026-06-17")

        self.assertEqual(result["unresolved_local_import_count"], 0)
        self.assertIn("jarvis/runtime/safety.py", result["active_import_closure_paths"])

        direct_v16_runtime_imports = []
        for runtime_path in sorted(Path("jarvis/runtime").glob("*.py")):
            runtime_text = runtime_path.read_text(encoding="utf-8-sig")
            if "jarvis.jarvis_v16_0_real_daily_readiness_gate" in runtime_text:
                direct_v16_runtime_imports.append(str(runtime_path).replace("\\", "/"))

        self.assertEqual(direct_v16_runtime_imports, [])
        self.assertFalse(result["deletion_performed"])
        self.assertFalse(result["archive_performed"])
        self.assertFalse(result["buy_request_created"])



    def test_expected_bridge_modules_remain_active_after_precision_expansion(self) -> None:
        result = build_import_closure_safe_archive_plan_result(current_date="2026-06-17")
        active = set(result["active_versioned_modules"])

        expected_bridges = {
            "jarvis/jarvis_v38_0_individual_stock_public_universe_engine.py",
            "jarvis/jarvis_v39_0_individual_stock_public_ranker.py",
            "jarvis/jarvis_v41_0_ranked_individual_stock_candidate_ticket_bridge.py",
            "jarvis/jarvis_v43_0_free_research_api_router_weekly_policy.py",
            "jarvis/jarvis_v44_0_free_research_api_fetcher_adapters_local_cache.py",
            "jarvis/jarvis_v45_0_free_research_cache_evidence_pack_bridge.py",
        }

        self.assertTrue(expected_bridges.issubset(active))
        self.assertGreaterEqual(result["active_versioned_module_count"], len(expected_bridges))
        self.assertEqual(result["unresolved_local_import_count"], 0)


if __name__ == "__main__":
    unittest.main()
