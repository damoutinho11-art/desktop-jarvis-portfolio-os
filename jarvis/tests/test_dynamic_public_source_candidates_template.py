import json
import unittest
from pathlib import Path


MATRIX = "jarvis/data/dynamic_public_source_candidates.template.json"


def _matrix() -> dict:
    return json.loads(Path(MATRIX).read_text(encoding="utf-8"))


class DynamicPublicSourceCandidatesTemplateTests(unittest.TestCase):
    def test_candidate_matrix_is_not_active_endpoint_pack(self) -> None:
        payload = _matrix()

        self.assertTrue(payload["template_only"])
        self.assertFalse(payload["active_endpoint_pack"])
        self.assertTrue(payload["fetching_forbidden"])
        self.assertTrue(payload["authorization_required_before_fetch"])
        self.assertTrue(payload["manual_review_required"])
        self.assertTrue(payload["execution_forbidden"])
        self.assertFalse(payload["creates_buy_request"])
        self.assertFalse(payload["grants_approval"])
        self.assertTrue(payload["no_trades_executed"])

    def test_candidates_are_public_and_non_broker(self) -> None:
        for candidate in _matrix()["candidates"]:
            self.assertTrue(candidate["public_source_only"])
            self.assertFalse(candidate["requires_authentication"])
            self.assertFalse(candidate["requires_credentials"])
            self.assertFalse(candidate["broker_or_trading_api"])
            self.assertFalse(candidate["contains_private_data"])
            self.assertFalse(candidate["promotion_allowed"])

    def test_crypto_candidates_are_marked_transformer_required(self) -> None:
        crypto_candidates = [
            candidate for candidate in _matrix()["candidates"]
            if candidate.get("asset_type") == "crypto"
        ]

        self.assertEqual(len(crypto_candidates), 3)
        for candidate in crypto_candidates:
            self.assertIn("coin_id", candidate)
            self.assertEqual(
                candidate["parser_compatibility_status"],
                "TRANSFORMER_REQUIRED_NOT_RAW_NORMALIZER_READY",
            )
            self.assertEqual(
                candidate["manual_coin_id_verification_status"],
                "pending_manual_operator_check",
            )

    def test_etf_candidates_require_manual_symbol_verification_and_cross_check(self) -> None:
        etf_candidates = [
            candidate for candidate in _matrix()["candidates"]
            if candidate.get("asset_type") == "ETF"
        ]

        self.assertEqual(len(etf_candidates), 3)
        for candidate in etf_candidates:
            self.assertEqual(
                candidate["parser_compatibility_status"],
                "PARSER_COMPATIBLE_IF_CSV_HAS_DATE_CLOSE_COLUMNS",
            )
            self.assertEqual(
                candidate["manual_symbol_verification_status"],
                "pending_manual_operator_check",
            )
            self.assertTrue(candidate["cross_check_required"])

    def test_fx_candidate_is_support_only_not_asset_endpoint(self) -> None:
        fx_candidates = [
            candidate for candidate in _matrix()["candidates"]
            if candidate.get("asset_type") == "fx_reference_support"
        ]

        self.assertEqual(len(fx_candidates), 1)
        fx = fx_candidates[0]
        self.assertIsNone(fx["asset_id"])
        self.assertEqual(fx["source_role"], "fx_reference_candidate")
        self.assertEqual(
            fx["parser_compatibility_status"],
            "FX_SUPPORT_TRANSFORMER_REQUIRED_NOT_APPROVED_ASSET_ENDPOINT",
        )


if __name__ == "__main__":
    unittest.main()
