import copy
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from jarvis.jarvis_public_evidence_pack_draft_generator import (
    ALLOWED_REQUIRED_PUBLIC_EVIDENCE_SECTIONS,
    FALSE_REQUIRED_SAFETY_FIELDS,
    TRUE_REQUIRED_SAFETY_FIELDS,
    build_evidence_pack_draft,
    build_draft_pack_id,
    build_manual_verification_checklist,
    build_missing_information_checklist,
    build_required_public_evidence_sections,
    build_required_public_source_categories,
    choose_next_manual_research_step,
    evaluate_public_evidence_pack_draft_generator,
    execute_authorized_evidence_pack_draft_cache_write,
    load_json,
    validate_draft_generator_config,
    validate_evidence_pack_draft,
    validate_research_queue_item_for_draft,
)


DEFAULT_CONFIG = "jarvis/data/jarvis_public_evidence_pack_draft_generator.example.json"
COMPLETE_CONFIG = "jarvis/data/jarvis_public_evidence_pack_draft_generator.synthetic_complete.json"
PROBLEMATIC_CONFIG = "jarvis/data/jarvis_public_evidence_pack_draft_generator.synthetic_problematic.json"
AUTHORIZED_CONFIG = "jarvis/data/jarvis_public_evidence_pack_draft_generator.synthetic_authorized_write.json"


def _complete_data():
    return load_json(COMPLETE_CONFIG)


def _item(asset_id: str) -> dict:
    return copy.deepcopy(next(item for item in _complete_data()["research_queue_items"] if item["asset_id"] == asset_id))


class PublicEvidencePackDraftGeneratorTests(unittest.TestCase):
    def test_default_example_blocks_safely(self) -> None:
        result = evaluate_public_evidence_pack_draft_generator(load_json(DEFAULT_CONFIG))

        self.assertEqual(result.status, "PUBLIC_EVIDENCE_PACK_DRAFT_GENERATOR_BLOCKED_SAFE")
        self.assertEqual(result.draft_pack_count, 0)
        self.assertTrue(result.no_network_called)
        self.assertTrue(result.no_cache_mutated)

    def test_synthetic_complete_returns_ready_safe(self) -> None:
        result = evaluate_public_evidence_pack_draft_generator(_complete_data())

        self.assertEqual(result.status, "PUBLIC_EVIDENCE_PACK_DRAFT_GENERATOR_READY_SAFE")
        self.assertEqual(result.queue_item_count, 6)
        self.assertEqual(result.draft_pack_count, 6)
        self.assertEqual(result.ready_draft_count, 3)

    def test_synthetic_problematic_returns_partial_safe(self) -> None:
        result = evaluate_public_evidence_pack_draft_generator(load_json(PROBLEMATIC_CONFIG))

        self.assertEqual(result.status, "PUBLIC_EVIDENCE_PACK_DRAFT_GENERATOR_PARTIAL_SAFE")
        self.assertEqual(result.draft_pack_count, 1)
        self.assertEqual(result.blocked_item_count, 1)

    def test_synthetic_authorized_write_evaluates_ready_to_write_but_does_not_write(self) -> None:
        result = evaluate_public_evidence_pack_draft_generator(load_json(AUTHORIZED_CONFIG))

        self.assertEqual(result.status, "PUBLIC_EVIDENCE_PACK_DRAFT_GENERATOR_READY_TO_WRITE_SAFE")
        self.assertEqual(result.draft_pack_count, 1)
        self.assertTrue(result.no_cache_mutated)

    def test_high_medium_low_ready_items_generate_collect_public_evidence_drafts(self) -> None:
        for asset_id in ("etf_vwce_xetra", "crypto_btc_public", "unknown_xyz_public"):
            with self.subTest(asset_id=asset_id):
                draft = build_evidence_pack_draft(_item(asset_id), "2026-06-13")
                self.assertEqual(draft["next_manual_research_step"], "collect_public_evidence")

    def test_needs_more_data_item_routes_to_manual_identifier_checklist(self) -> None:
        item = _item("equity_more_data_public")
        draft = build_evidence_pack_draft(item, "2026-06-13")

        self.assertEqual(draft["next_manual_research_step"], "verify_public_identifiers_manually")
        self.assertIn("missing_classification_field::issuer_or_provider", draft["missing_information_checklist"])
        self.assertIn("manual_confirm_asset_identity_and_identifier", draft["manual_verification_checklist"])

    def test_needs_manual_source_review_routes_to_refresh_step(self) -> None:
        draft = build_evidence_pack_draft(_item("etf_stale_public"), "2026-06-13")

        self.assertEqual(draft["next_manual_research_step"], "refresh_public_cache_before_pack")
        self.assertIn("refresh_or_review_public_source_freshness_before_manual_trust_review", draft["missing_information_checklist"])

    def test_blocked_safe_item_is_held_until_safe(self) -> None:
        draft = build_evidence_pack_draft(_item("blocked_missing_public"), "2026-06-13")

        self.assertEqual(draft["next_manual_research_step"], "hold_until_safe")
        self.assertIn("fix_queue_or_classification_inputs_before_public_evidence_pack_work", draft["missing_information_checklist"])

    def test_required_evidence_sections_include_expected_sections(self) -> None:
        sections = set(build_required_public_evidence_sections(_item("etf_vwce_xetra")))

        for section in (
            "identity_and_identifier_check",
            "issuer_or_provider_check",
            "instrument_structure_check",
            "listing_or_venue_check",
            "currency_and_region_check",
            "public_documentation_check",
            "freshness_and_source_date_check",
            "manual_verification_decision",
            "manual_approval_decision",
        ):
            self.assertIn(section, sections)
        self.assertEqual(tuple(ALLOWED_REQUIRED_PUBLIC_EVIDENCE_SECTIONS), build_required_public_evidence_sections(_item("etf_vwce_xetra")))

    def test_source_categories_are_asset_type_aware(self) -> None:
        etf_categories = build_required_public_source_categories(_item("etf_vwce_xetra"))
        crypto_categories = build_required_public_source_categories(_item("crypto_btc_public"))

        self.assertIn("official_fund_factsheet_or_kid_reference", etf_categories)
        self.assertIn("public_protocol_documentation_reference", crypto_categories)
        self.assertIn("manual_verification_reference", etf_categories)

    def test_manual_verification_checklist_never_claims_verified(self) -> None:
        checklist = " ".join(build_manual_verification_checklist(_item("etf_vwce_xetra"))).lower()

        self.assertNotIn("evidence_verified", checklist)
        self.assertNotIn("verified_by_user", checklist)

    def test_draft_pack_preserves_safe_statuses(self) -> None:
        draft = build_evidence_pack_draft(_item("etf_vwce_xetra"), "2026-06-13")

        self.assertEqual(validate_evidence_pack_draft(draft), ())
        self.assertEqual(draft["verification_status"], "NOT_VERIFIED")
        self.assertEqual(draft["approval_status"], "NOT_APPROVED")
        self.assertEqual(draft["investability_status"], "NOT_INVESTABLE")
        self.assertEqual(draft["recommendation_status"], "NO_RECOMMENDATION")
        self.assertEqual(draft["allocation_status"], "NO_ALLOCATION")
        self.assertEqual(draft["execution_status"], "NO_EXECUTION")
        self.assertEqual(draft["trade_status"], "NO_TRADE")

    def test_unsafe_queue_items_are_blocked(self) -> None:
        cases = (
            ("evidence_pack_status", "GENERATED"),
            ("evidence_status", "VERIFIED"),
            ("approval_status", "APPROVED"),
            ("investability_status", "INVESTABLE"),
            ("execution_status", "EXECUTABLE"),
            ("recommendation_status", "BUY"),
            ("allocation_status", "ALLOCATE"),
            ("trade_status", "TRADE"),
            ("required_manual_review", False),
        )
        for field, value in cases:
            with self.subTest(field=field):
                item = _item("etf_vwce_xetra")
                item[field] = value
                reasons = validate_research_queue_item_for_draft(item)
                self.assertTrue(any(field in reason for reason in reasons))

    def test_forbidden_research_steps_are_blocked(self) -> None:
        item = _item("etf_vwce_xetra")
        item["suggested_next_research_step"] = "trade_execution"

        self.assertIn("suggested_next_research_step must not be trade_execution.", validate_research_queue_item_for_draft(item))

    def test_duplicate_draft_pack_id_is_detected(self) -> None:
        config = _complete_data()
        duplicate = copy.deepcopy(config["research_queue_items"][0])
        duplicate["queue_id"] = "research_queue::duplicate_etf_vwce_xetra"
        config["research_queue_items"].append(duplicate)

        result = evaluate_public_evidence_pack_draft_generator(config)

        self.assertEqual(result.status, "PUBLIC_EVIDENCE_PACK_DRAFT_GENERATOR_PARTIAL_SAFE")
        self.assertEqual(result.duplicate_draft_pack_id_count, 1)

    def test_authorized_write_function_writes_only_to_temp_output(self) -> None:
        config = load_json(AUTHORIZED_CONFIG)
        result = evaluate_public_evidence_pack_draft_generator(config)
        with tempfile.TemporaryDirectory() as tmp:
            write_result = execute_authorized_evidence_pack_draft_cache_write(
                config,
                result.draft_packs,
                now=datetime(2026, 6, 13, tzinfo=timezone.utc),
                output_root_override=tmp,
            )
            output_path = Path(write_result["output_path"])
            metadata_path = Path(write_result["metadata_path"])
            payload = json.loads(output_path.read_text(encoding="utf-8"))
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))

        self.assertTrue(write_result["written"])
        self.assertEqual(write_result["status"], "PUBLIC_EVIDENCE_PACK_DRAFT_GENERATOR_WRITTEN_LOCAL_CACHE_SAFE")
        self.assertEqual(payload["draft_packs"][0]["approval_status"], "NOT_APPROVED")
        self.assertEqual(metadata["draft_pack_count"], 1)
        self.assertTrue(metadata["draft_pack_data_unverified"])
        for field in ("evidence_verified", "approved_asset", "trusted_asset", "investable", "allocation_recommendation", "buy_signal", "sell_signal", "trade_executed", "registry_mutation", "executor_created"):
            self.assertFalse(metadata[field])

    def test_wrong_or_missing_phrase_does_not_write(self) -> None:
        config = _complete_data()
        result = evaluate_public_evidence_pack_draft_generator(config)
        with tempfile.TemporaryDirectory() as tmp:
            write_result = execute_authorized_evidence_pack_draft_cache_write(config, result.draft_packs, output_root_override=tmp)
            self.assertFalse(Path(tmp, "public_asset_universe.evidence_pack_drafts.json").exists())

        self.assertFalse(write_result["written"])
        self.assertEqual(write_result["status"], "PUBLIC_EVIDENCE_PACK_DRAFT_GENERATOR_BLOCKED_SAFE")

    def test_write_outside_allowed_roots_is_blocked(self) -> None:
        config = load_json(AUTHORIZED_CONFIG)
        result = evaluate_public_evidence_pack_draft_generator(config)
        for output_root in ("docs", "templates", "jarvis/data"):
            with self.subTest(output_root=output_root):
                write_result = execute_authorized_evidence_pack_draft_cache_write(config, result.draft_packs, output_root_override=output_root)
                self.assertFalse(write_result["written"])
                self.assertIn("evidence pack draft output root", write_result["blockers"][0])

    def test_safety_controls_are_enforced(self) -> None:
        config = _complete_data()
        for field in FALSE_REQUIRED_SAFETY_FIELDS:
            with self.subTest(field=field):
                mutated = copy.deepcopy(config)
                mutated["safety_controls"][field] = True
                self.assertIn(f"safety_controls.{field} must be false.", validate_draft_generator_config(mutated))
        for field in TRUE_REQUIRED_SAFETY_FIELDS:
            with self.subTest(field=field):
                mutated = copy.deepcopy(config)
                mutated["safety_controls"][field] = False
                self.assertIn(f"safety_controls.{field} must be true.", validate_draft_generator_config(mutated))

    def test_next_manual_actions_are_validated(self) -> None:
        config = _complete_data()
        for action in ("review_public_evidence_pack_drafts", "proceed_to_operator_research_dashboard_integration", "fix_research_queue_items", "rerun_research_priority_queue", "no_manual_asset_entry_required"):
            with self.subTest(action=action):
                mutated = copy.deepcopy(config)
                mutated["next_manual_action"] = action
                self.assertFalse([reason for reason in validate_draft_generator_config(mutated) if "next_manual_action" in reason])
        for action in ("evidence_verification", "approval", "registry_mutation", "allocation_recommendation", "trade_execution", "executor_creation"):
            with self.subTest(action=action):
                mutated = copy.deepcopy(config)
                mutated["next_manual_action"] = action
                self.assertTrue([reason for reason in validate_draft_generator_config(mutated) if "next_manual_action" in reason])

    def test_draft_pack_id_is_deterministic(self) -> None:
        self.assertEqual(build_draft_pack_id(_item("etf_vwce_xetra")), "public_evidence_pack_draft::etf_vwce_xetra")

    def test_missing_information_defaults_when_no_missing_fields(self) -> None:
        self.assertIn("no_missing_public_fields_identified_by_queue", build_missing_information_checklist(_item("etf_vwce_xetra")))

    def test_choose_next_manual_research_step_falls_back_to_fix_inputs(self) -> None:
        item = _item("etf_vwce_xetra")
        item["research_priority_bucket"] = "UNEXPECTED"
        self.assertEqual(choose_next_manual_research_step(item), "fix_queue_or_classification_inputs")

    def test_module_import_is_safe(self) -> None:
        import jarvis.jarvis_public_evidence_pack_draft_generator as module

        self.assertTrue(hasattr(module, "evaluate_public_evidence_pack_draft_generator"))


if __name__ == "__main__":
    unittest.main()
