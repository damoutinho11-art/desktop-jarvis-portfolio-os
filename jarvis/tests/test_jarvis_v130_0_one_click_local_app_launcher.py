from pathlib import Path
import unittest

from jarvis.runtime.operator import ACTIVE_RUNTIME_STAGE, CURRENT_OPERATOR_SURFACE


class TestJarvisV130OneClickLocalAppLauncher(unittest.TestCase):
    def test_operator_surface_is_v130_launcher(self):
        self.assertEqual(ACTIVE_RUNTIME_STAGE, "v130.0")
        self.assertEqual(CURRENT_OPERATOR_SURFACE, "one_click_local_app_launcher")

    def test_batch_launcher_exists_and_runs_daily_operator(self):
        path = Path("Start Jarvis.bat")
        self.assertTrue(path.exists())

        text = path.read_text(encoding="utf-8")
        self.assertIn("jarvis_operator.py", text)
        self.assertIn("--daily-operator", text)
        self.assertIn("--max-targets 10", text)
        self.assertIn("outputs\\dashboard_latest.html", text)
        self.assertIn("No broker, credential, order, trade, or auto-approval", text)

    def test_powershell_launcher_exists_and_runs_daily_operator(self):
        path = Path("Start-Jarvis.ps1")
        self.assertTrue(path.exists())

        text = path.read_text(encoding="utf-8")
        self.assertIn("jarvis_operator.py", text)
        self.assertIn("--daily-operator", text)
        self.assertIn("--max-targets 10", text)
        self.assertIn("outputs\\dashboard_latest.html", text)
        self.assertIn("No broker, credential, order, trade, or auto-approval", text)


if __name__ == "__main__":
    unittest.main()
