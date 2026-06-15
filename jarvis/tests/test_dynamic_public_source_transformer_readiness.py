import unittest

from jarvis.dynamic_public_source_transformer_readiness import (
    STATUS_READY,
    audit_dynamic_public_source_transformer_readiness,
)


class DynamicPublicSourceTransformerReadinessTests(unittest.TestCase):
    def test_default_candidate_matrix_classifies_without_promoting_sources(self) -> None:
        result = audit_dynamic_public_source_transformer_readiness()

        self.assertEqual(result.status, STATUS_READY)
        self.assertEqual(result.candidate_count, 7)
        self.assertEqual(result.normalizer_ready_count, 3)
        self.assertEqual(result.transformer_required_count, 3)
        self.assertEqual(result.support_only_count, 1)
        self.assertEqual(result.promotion_allowed_count, 0)
        self.assertFalse(result.blockers)

    def test_crypto_rows_require_transformer_before_endpoint_promotion(self) -> None:
        result = audit_dynamic_public_source_transformer_readiness()
        crypto_rows = [row for row in result.rows if row.asset_type == "crypto"]

        self.assertEqual(len(crypto_rows), 3)
        self.assertTrue(
            all(
                row.readiness_classification == "TRANSFORMER_REQUIRED_BEFORE_ENDPOINT_PROMOTION"
                for row in crypto_rows
            )
        )
        self.assertTrue(all(not row.promotion_allowed for row in crypto_rows))

    def test_fx_row_is_support_only_not_approved_endpoint(self) -> None:
        result = audit_dynamic_public_source_transformer_readiness()
        fx_rows = [row for row in result.rows if row.asset_type == "fx_reference_support"]

        self.assertEqual(len(fx_rows), 1)
        self.assertIsNone(fx_rows[0].asset_id)
        self.assertEqual(fx_rows[0].readiness_classification, "SUPPORT_ONLY_TRANSFORMER_REQUIRED")

    def test_safety_flags_remain_non_execution(self) -> None:
        result = audit_dynamic_public_source_transformer_readiness()
        payload = result.to_dict()

        self.assertTrue(payload["manual_review_required"])
        self.assertTrue(payload["fetching_forbidden"])
        self.assertTrue(payload["execution_forbidden"])
        self.assertFalse(payload["creates_buy_request"])
        self.assertFalse(payload["grants_approval"])
        self.assertTrue(payload["no_trades_executed"])


if __name__ == "__main__":
    unittest.main()
