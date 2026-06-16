import unittest

from jarvis.jarvis_v13_0_single_command_operator_launcher import (
    run_v13_0_single_command_operator_launcher,
)
from jarvis.jarvis_v13_0_single_command_operator_launcher_report import (
    build_v13_0_single_command_operator_launcher_report,
)
from jarvis.tests.test_jarvis_v13_0_single_command_operator_launcher import _runtime, _ui, _voice


class JarvisV130SingleCommandOperatorLauncherReportTests(unittest.TestCase):
    def test_report_contains_launcher_and_safety(self) -> None:
        result = run_v13_0_single_command_operator_launcher(
            runtime_result=_runtime(),
            ui_shell_result=_ui(),
            voice_shell_result=_voice(),
            voice_command_text="Jarvis, buy BTC now.",
        )
        report = build_v13_0_single_command_operator_launcher_report(result)

        self.assertIn("J.A.R.V.I.S. v13.0 Single Command Operator Launcher", report)
        self.assertIn("status: JARVIS_V13_0_SINGLE_COMMAND_OPERATOR_LAUNCHER_READY_SAFE", report)
        self.assertIn("launcher status: SINGLE_COMMAND_OPERATOR_LAUNCHER_READY", report)
        self.assertIn("recommended next stage: v13_1_product_mode_closeout_audit", report)
        self.assertIn("voice command processed: True", report)
        self.assertIn("blocked: True", report)
        self.assertIn("No execution action was taken", report)
        self.assertIn("no web server started: True", report)
        self.assertIn("no microphone: True", report)
        self.assertIn("broker connection forbidden: True", report)
        self.assertIn("no trades executed: True", report)


if __name__ == "__main__":
    unittest.main()
