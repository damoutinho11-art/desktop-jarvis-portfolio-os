from __future__ import annotations

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

    def test_import_closure_no_longer_depends_on_v16_safety_gate(self) -> None:
        result = build_import_closure_safe_archive_plan_result(current_date="2026-06-17")

        self.assertEqual(result["unresolved_local_import_count"], 0)
        self.assertNotIn(
            "jarvis/jarvis_v16_0_real_daily_readiness_gate.py",
            result["active_import_closure_paths"],
        )
        self.assertNotIn(
            "jarvis/jarvis_v16_0_real_daily_readiness_gate.py",
            result["active_versioned_modules"],
        )
        self.assertIn("jarvis/runtime/safety.py", result["active_import_closure_paths"])
        self.assertFalse(result["deletion_performed"])
        self.assertFalse(result["archive_performed"])
        self.assertFalse(result["buy_request_created"])

    def test_remaining_active_versioned_modules_are_expected_bridges_only(self) -> None:
        result = build_import_closure_safe_archive_plan_result(current_date="2026-06-17")

        self.assertEqual(
            set(result["active_versioned_modules"]),
            {
                "jarvis/jarvis_v38_0_individual_stock_public_universe_engine.py",
                "jarvis/jarvis_v39_0_individual_stock_public_ranker.py",
                "jarvis/jarvis_v41_0_ranked_individual_stock_candidate_ticket_bridge.py",
                "jarvis/jarvis_v43_0_free_research_api_router_weekly_policy.py",
                "jarvis/jarvis_v44_0_free_research_api_fetcher_adapters_local_cache.py",
                "jarvis/jarvis_v45_0_free_research_cache_evidence_pack_bridge.py",
            },
        )


if __name__ == "__main__":
    unittest.main()
