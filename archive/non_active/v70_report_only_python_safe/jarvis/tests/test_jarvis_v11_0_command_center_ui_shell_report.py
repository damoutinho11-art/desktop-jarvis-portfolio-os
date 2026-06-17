import unittest

from jarvis.jarvis_v11_0_command_center_ui_shell_report import (
    build_v11_0_command_center_ui_shell_report,
)
from jarvis.tests.test_jarvis_v11_0_command_center_ui_shell import _runtime
from jarvis.jarvis_v11_0_command_center_ui_shell import audit_v11_0_command_center_ui_shell


class JarvisV110CommandCenterUiShellReportTests(unittest.TestCase):
    def test_report_contains_ui_shell_and_safety(self) -> None:
        result = audit_v11_0_command_center_ui_shell(runtime_result=_runtime())
        report = build_v11_0_command_center_ui_shell_report(result)

        self.assertIn("J.A.R.V.I.S. v11.0 Command Center UI Shell", report)
        self.assertIn("status: JARVIS_V11_0_COMMAND_CENTER_UI_SHELL_READY_SAFE", report)
        self.assertIn("ui shell status: COMMAND_CENTER_UI_SHELL_READY", report)
        self.assertIn("recommended next stage: v12_0_voice_operator_interface_boundary", report)
        self.assertIn("section count: 7", report)
        self.assertIn("ready section count: 7", report)
        self.assertIn("voice interface available: False", report)
        self.assertIn("static local HTML only: True", report)
        self.assertIn("web server started: False", report)
        self.assertIn("buy button disabled: True", report)
        self.assertIn("broker connection forbidden: True", report)
        self.assertIn("no trades executed: True", report)


if __name__ == "__main__":
    unittest.main()
