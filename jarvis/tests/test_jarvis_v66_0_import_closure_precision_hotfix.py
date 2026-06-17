from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from jarvis.runtime.import_closure_safe_archive_plan import (
    _parse_local_imports,
    build_import_closure_safe_archive_plan_result,
)


class JarvisV660ImportClosurePrecisionHotfixTests(unittest.TestCase):
    def test_parse_local_imports_handles_utf8_sig_bom(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bom_module.py"
            path.write_text(
                "\ufefffrom jarvis.runtime.safety import build_safety_check_console_output\n",
                encoding="utf-8",
            )

            imports = _parse_local_imports(path)

            self.assertIn("jarvis/runtime/safety.py", imports)

    def test_active_import_closure_remains_resolved_after_bom_fix(self) -> None:
        result = build_import_closure_safe_archive_plan_result(current_date="2026-06-17")

        self.assertEqual(result["unresolved_local_import_count"], 0)
        self.assertIn("jarvis/runtime/operator.py", result["active_import_closure_paths"])
        self.assertIn("jarvis/runtime/safety.py", result["active_import_closure_paths"])
        self.assertFalse(result["deletion_performed"])
        self.assertFalse(result["archive_performed"])
        self.assertFalse(result["buy_request_created"])


if __name__ == "__main__":
    unittest.main()
