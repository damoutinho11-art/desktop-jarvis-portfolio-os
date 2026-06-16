import unittest

from jarvis.jarvis_v12_0_voice_operator_interface_boundary import audit_v12_0_voice_operator_interface_boundary
from jarvis.jarvis_v12_0_voice_operator_interface_boundary_report import (
    build_v12_0_voice_operator_interface_boundary_report,
)
from jarvis.tests.test_jarvis_v12_0_voice_operator_interface_boundary import _ui


class JarvisV120VoiceOperatorInterfaceBoundaryReportTests(unittest.TestCase):
    def test_report_contains_voice_boundary_and_safety(self) -> None:
        result = audit_v12_0_voice_operator_interface_boundary(ui_shell_result=_ui())
        report = build_v12_0_voice_operator_interface_boundary_report(result)

        self.assertIn("J.A.R.V.I.S. v12.0 Voice Operator Interface Boundary", report)
        self.assertIn("status: JARVIS_V12_0_VOICE_OPERATOR_INTERFACE_BOUNDARY_READY_SAFE", report)
        self.assertIn("boundary status: VOICE_OPERATOR_INTERFACE_BOUNDARY_READY", report)
        self.assertIn("recommended next stage: v12_1_local_voice_io_shell", report)
        self.assertIn("allowed command count:", report)
        self.assertIn("blocked command count:", report)
        self.assertIn("voice interface available: False", report)
        self.assertIn("microphone available: False", report)
        self.assertIn("speech to text available: False", report)
        self.assertIn("text to speech available: False", report)
        self.assertIn("execution intents blocked: True", report)
        self.assertIn("broker connection forbidden: True", report)
        self.assertIn("no trades executed: True", report)


if __name__ == "__main__":
    unittest.main()
