import unittest

from jarvis.jarvis_v13_1_product_mode_closeout_audit import audit_v13_1_product_mode_closeout_audit
from jarvis.jarvis_v13_1_product_mode_closeout_audit_report import (
    build_v13_1_product_mode_closeout_audit_report,
)
from jarvis.tests.test_jarvis_v13_1_product_mode_closeout_audit import _launcher


class JarvisV131ProductModeCloseoutAuditReportTests(unittest.TestCase):
    def test_report_contains_closeout_and_safety(self) -> None:
        result = audit_v13_1_product_mode_closeout_audit(launcher_result=_launcher())
        report = build_v13_1_product_mode_closeout_audit_report(result)

        self.assertIn("J.A.R.V.I.S. v13.1 Product Mode Closeout Audit", report)
        self.assertIn("status: JARVIS_V13_1_PRODUCT_MODE_CLOSEOUT_AUDIT_READY_SAFE", report)
        self.assertIn("closeout status: PRODUCT_MODE_CLOSEOUT_READY", report)
        self.assertIn("recommended next stage: release_tag_product_mode_v13_1", report)
        self.assertIn("blocked buy command verified: True", report)
        self.assertIn("product mode closeout ready: True", report)
        self.assertIn("launcher ready: True", report)
        self.assertIn("runtime ready: True", report)
        self.assertIn("UI shell ready: True", report)
        self.assertIn("voice shell ready: True", report)
        self.assertIn("no feature added: True", report)
        self.assertIn("broker connection forbidden: True", report)
        self.assertIn("no trades executed: True", report)


if __name__ == "__main__":
    unittest.main()
