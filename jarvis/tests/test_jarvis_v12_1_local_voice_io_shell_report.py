import unittest

from jarvis.jarvis_v12_1_local_voice_io_shell import audit_v12_1_local_voice_io_shell
from jarvis.jarvis_v12_1_local_voice_io_shell_report import (
    build_v12_1_local_voice_io_shell_report,
)
from jarvis.tests.test_jarvis_v12_1_local_voice_io_shell import _boundary


class JarvisV121LocalVoiceIoShellReportTests(unittest.TestCase):
    def test_report_contains_shell_and_safety(self) -> None:
        result = audit_v12_1_local_voice_io_shell(boundary_result=_boundary())
        report = build_v12_1_local_voice_io_shell_report(result)

        self.assertIn("J.A.R.V.I.S. v12.1 Local Voice I/O Shell", report)
        self.assertIn("status: JARVIS_V12_1_LOCAL_VOICE_IO_SHELL_READY_SAFE", report)
        self.assertIn("shell status: LOCAL_VOICE_IO_SHELL_READY", report)
        self.assertIn("recommended next stage: v13_0_single_command_operator_launcher", report)
        self.assertIn("allowed turn count:", report)
        self.assertIn("blocked turn count:", report)
        self.assertIn("unknown turn count:", report)
        self.assertIn("typed terminal shell only: True", report)
        self.assertIn("microphone available: False", report)
        self.assertIn("speech to text available: False", report)
        self.assertIn("text to speech available: False", report)
        self.assertIn("broker connection forbidden: True", report)
        self.assertIn("no trades executed: True", report)


if __name__ == "__main__":
    unittest.main()
