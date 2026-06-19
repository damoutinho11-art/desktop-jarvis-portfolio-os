from __future__ import annotations

from pathlib import Path
import unittest

from jarvis.runtime import operator
from jarvis.runtime.full_system_audit import build_full_system_audit_result
from jarvis.runtime.news_coverage_readiness import (
    REQUIRED_CATEGORIES,
    STATUS_READY,
    build_news_coverage_readiness_result,
)
from jarvis.runtime.product_api import build_product_api_result


class JarvisV980AuditWarningResolutionNewsCoverageTests(unittest.TestCase):
    def test_news_coverage_lane_is_first_class_and_ready(self) -> None:
        result = build_news_coverage_readiness_result(current_date="2026-06-18")

        self.assertEqual(result.status, STATUS_READY)
        self.assertTrue(result.news_coverage_ready)
        self.assertFalse(result.live_news_fetch_enabled)
        self.assertTrue(result.manual_review_required)
        self.assertEqual(result.missing_categories, [])
        self.assertEqual(set(result.covered_categories), set(REQUIRED_CATEGORIES))
        self.assertEqual(result.blockers, [])

    def test_product_api_exposes_news_coverage(self) -> None:
        result = build_product_api_result(current_date="2026-06-18")

        self.assertTrue(result.api_ready)
        self.assertTrue(result.news_coverage["news_coverage_ready"])
        self.assertFalse(result.news_coverage["live_news_fetch_enabled"])
        self.assertIn("macro", result.news_coverage["covered_categories"])
        self.assertIn("individual_stock", result.news_coverage["covered_categories"])
        self.assertEqual(result.blockers, [])

    def test_full_system_audit_uses_news_lane(self) -> None:
        result = build_full_system_audit_result(
            current_date="2026-06-18",
            speed_warning_seconds=120.0,
        )

        self.assertTrue(result.news_coverage_ready)
        self.assertTrue(result.news_checks["news_coverage_ready"])
        self.assertFalse(result.news_checks["live_news_fetch_enabled"])
        self.assertEqual(result.news_checks["missing_categories"], [])
        self.assertNotIn("news_coverage_not_ready", result.blockers)

    def test_unresolved_import_warning_is_non_blocking_and_explained(self) -> None:
        product = build_product_api_result(current_date="2026-06-18")
        audit = build_full_system_audit_result(
            current_date="2026-06-18",
            speed_warning_seconds=120.0,
        )

        all_warnings = "\n".join(product.warnings + audit.warnings)
        all_blockers = "\n".join(product.blockers + audit.blockers)

        self.assertEqual(product.blockers, [])
        self.assertEqual(audit.blockers, [])
        self.assertNotIn("unresolved local imports", all_blockers)

        if "unresolved local imports" in all_warnings:
            self.assertIn("product-mode audit warning: unresolved local imports", all_warnings)

    def test_operator_routes_v98_surface(self) -> None:
        self.assertEqual(operator.ACTIVE_RUNTIME_STAGE, "v98.0")
        self.assertEqual(operator.CURRENT_OPERATOR_SURFACE, "audit_warning_resolution_news_coverage")

        source = Path("jarvis/runtime/operator.py").read_text(encoding="utf-8")
        self.assertIn("--news-coverage-readiness", source)
        self.assertIn("_news_coverage_readiness_main", source)


if __name__ == "__main__":
    unittest.main()
