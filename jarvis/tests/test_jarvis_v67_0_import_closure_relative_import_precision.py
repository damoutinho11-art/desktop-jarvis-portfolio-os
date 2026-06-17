from __future__ import annotations

import unittest
from pathlib import Path

from jarvis.runtime.import_closure_safe_archive_plan import (
    _parse_local_imports,
    build_import_closure_safe_archive_plan_result,
)


class JarvisV670ImportClosureRelativeImportPrecisionTests(unittest.TestCase):
    def test_parse_local_imports_detects_relative_versioned_imports(self) -> None:
        imports = _parse_local_imports(
            Path("jarvis/jarvis_v45_0_free_research_cache_evidence_pack_bridge.py")
        )

        self.assertIn("jarvis/jarvis_v12_1_local_voice_io_shell.py", imports)

    def test_active_import_closure_remains_resolved_after_relative_import_fix(self) -> None:
        result = build_import_closure_safe_archive_plan_result(current_date="2026-06-17")

        self.assertEqual(result["unresolved_local_import_count"], 0)
        self.assertIn("jarvis/runtime/operator.py", result["active_import_closure_paths"])
        self.assertIn("jarvis/runtime/safety.py", result["active_import_closure_paths"])
        self.assertIn(
            "jarvis/jarvis_v45_0_free_research_cache_evidence_pack_bridge.py",
            result["active_import_closure_paths"],
        )
        self.assertIn(
            "jarvis/jarvis_v12_1_local_voice_io_shell.py",
            result["active_import_closure_paths"],
        )
        self.assertFalse(result["deletion_performed"])
        self.assertFalse(result["archive_performed"])
        self.assertFalse(result["buy_request_created"])


if __name__ == "__main__":
    unittest.main()
