import unittest

from jarvis.dynamic_public_source_transformer_readiness_report import (
    report_dynamic_public_source_transformer_readiness,
)


class DynamicPublicSourceTransformerReadinessReportTests(unittest.TestCase):
    def test_report_contains_classifications_and_safety_boundary(self) -> None:
        report = report_dynamic_public_source_transformer_readiness()

        self.assertIn("status: DYNAMIC_PUBLIC_SOURCE_TRANSFORMER_READINESS_READY_SAFE", report)
        self.assertIn("normalizer ready count: 3", report)
        self.assertIn("transformer required count: 3", report)
        self.assertIn("support only count: 1", report)
        self.assertIn("promotion allowed count: 0", report)
        self.assertIn("TRANSFORMER_REQUIRED_BEFORE_ENDPOINT_PROMOTION", report)
        self.assertIn("SUPPORT_ONLY_TRANSFORMER_REQUIRED", report)
        self.assertIn("- no endpoint promotion", report)
        self.assertIn("- no trades executed", report)


if __name__ == "__main__":
    unittest.main()
