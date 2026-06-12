import unittest
from pathlib import Path

from jarvis.jarvis_candidate_intake import (
    EVIDENCE_CHECKLIST_BY_ASSET_TYPE,
    PHASE1_ROUTE,
    build_candidate_intake_pack,
    load_candidate_intake,
    validate_candidate_record,
)


SYNTHETIC_MULTI = "jarvis/data/jarvis_candidate_intake.synthetic_multi.example.json"
DEFAULT_INTAKE = "jarvis/data/jarvis_candidate_intake.example.json"


def _candidate(**overrides):
    base = {
        "candidate_id": "synthetic_candidate",
        "display_name": "Synthetic Candidate",
        "asset_type": "etf",
        "symbol_or_identifier": "SYN",
        "issuer_or_provider": "Synthetic issuer",
        "market_or_region": "EU",
        "currency": "EUR",
        "source_context": "synthetic manual entry",
        "user_rationale": "Test candidate.",
        "intake_status": "draft",
        "created_by_manual_entry": True,
        "manual_entry_required": True,
        "evidence_pipeline_required": True,
        "phase1_route": "v4.27-v4.47-real-evidence-pipeline",
        "notes": "No approval.",
    }
    base.update(overrides)
    return base


class JarvisCandidateIntakeTests(unittest.TestCase):
    def test_multiple_asset_types_are_accepted(self) -> None:
        pack = load_candidate_intake(SYNTHETIC_MULTI)
        asset_types = {candidate.asset_type for candidate in pack.candidates}

        self.assertIn("etf", asset_types)
        self.assertIn("stock", asset_types)
        self.assertIn("crypto", asset_types)
        self.assertIn("other", asset_types)

    def test_unknown_and_other_require_review_and_do_not_approve(self) -> None:
        other = validate_candidate_record(_candidate(asset_type="other"))
        unknown = validate_candidate_record(_candidate(asset_type="mystery"))

        self.assertEqual(other.intake_status, "CANDIDATE_INTAKE_PARTIAL_SAFE")
        self.assertEqual(unknown.intake_status, "CANDIDATE_INTAKE_PARTIAL_SAFE")
        self.assertFalse(other.approved_asset)
        self.assertFalse(unknown.trusted_asset)

    def test_vwce_ftaw_are_not_only_allowed_candidates(self) -> None:
        pack = load_candidate_intake(SYNTHETIC_MULTI)
        ready_ids = {candidate.candidate_id for candidate in pack.candidates if candidate.intake_status == "CANDIDATE_INTAKE_READY_FOR_PHASE1_EVIDENCE_PIPELINE"}

        self.assertIn("synthetic_stock_candidate", ready_ids)
        self.assertIn("synthetic_crypto_candidate", ready_ids)

    def test_required_fields_are_enforced(self) -> None:
        result = validate_candidate_record(_candidate(candidate_id="", display_name="", asset_type="", symbol_or_identifier=""))

        self.assertEqual(result.intake_status, "CANDIDATE_INTAKE_BLOCKED_SAFE")
        self.assertGreaterEqual(len(result.blocked_reasons), 4)

    def test_unsafe_claims_are_blocked(self) -> None:
        for field in (
            "approved_asset",
            "trusted_asset",
            "investable",
            "allocation_recommendation",
            "buy_signal",
            "sell_signal",
            "trade_executed",
            "registry_mutation",
            "executor_created",
        ):
            with self.subTest(field=field):
                result = validate_candidate_record(_candidate(**{field: True}))
                self.assertEqual(result.intake_status, "CANDIDATE_INTAKE_BLOCKED_SAFE")
                self.assertTrue(any(field in reason for reason in result.blocked_reasons))

    def test_complete_candidate_reaches_ready_for_phase1_evidence_pipeline(self) -> None:
        result = validate_candidate_record(_candidate())

        self.assertEqual(result.intake_status, "CANDIDATE_INTAKE_READY_FOR_PHASE1_EVIDENCE_PIPELINE")
        self.assertEqual(result.route_summary, PHASE1_ROUTE)

    def test_partial_and_default_candidates_are_safe(self) -> None:
        default_pack = load_candidate_intake(DEFAULT_INTAKE)
        multi_pack = load_candidate_intake(SYNTHETIC_MULTI)

        self.assertEqual(default_pack.overall_status, "CANDIDATE_INTAKE_BLOCKED_SAFE")
        self.assertEqual(multi_pack.overall_status, "CANDIDATE_INTAKE_PARTIAL_SAFE")
        self.assertTrue(any(candidate.intake_status == "CANDIDATE_INTAKE_BLOCKED_SAFE" for candidate in multi_pack.candidates))

    def test_evidence_mappings_exist_for_supported_types(self) -> None:
        for asset_type in ("etf", "stock", "bond", "fund", "cash_equivalent", "crypto", "commodity", "other"):
            self.assertIn(asset_type, EVIDENCE_CHECKLIST_BY_ASSET_TYPE)
            self.assertTrue(EVIDENCE_CHECKLIST_BY_ASSET_TYPE[asset_type])

    def test_no_registry_candidate_mutation_or_action_flags(self) -> None:
        before = Path(SYNTHETIC_MULTI).read_text(encoding="utf-8")
        pack = load_candidate_intake(SYNTHETIC_MULTI)

        self.assertEqual(before, Path(SYNTHETIC_MULTI).read_text(encoding="utf-8"))
        self.assertFalse(pack.registry_mutation)
        self.assertFalse(pack.approved_asset)
        self.assertFalse(pack.trusted_asset)
        self.assertFalse(pack.investable)
        self.assertFalse(pack.allocation_recommendation)
        self.assertFalse(pack.buy_signal)
        self.assertFalse(pack.sell_signal)
        self.assertFalse(pack.trade_executed)
        self.assertFalse(pack.executor_created)


if __name__ == "__main__":
    unittest.main()
