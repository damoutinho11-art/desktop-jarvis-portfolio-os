import json
import tempfile
import unittest
from pathlib import Path

from jarvis.ftaw_source_fact_intake import FTAWSourceFactIntakeConfig, FTAWSourceFactRecord
from jarvis.ftaw_source_identity_guard import (
    FTAWSourceIdentityGuardConfig,
    build_ftaw_source_identity_guard,
    build_ftaw_source_identity_guard_from_files,
)


SOURCE_REGISTRY = "jarvis/data/candidate_assets.v2.example.json"
REVIEWED_REGISTRY = "jarvis/data/private/candidate_assets.v2.reviewed.local.json"
INTAKE_CONFIG = "jarvis/data/ftaw_source_fact_intake.example.json"
GUARD_CONFIG = "jarvis/data/ftaw_source_identity_guard.example.json"
TARGET = "ftaw_global_core_candidate"


def _record(**overrides):
    data = {
        "asset_id": TARGET,
        "evidence_type": "fund_metadata",
        "source_name": "Synthetic provider page",
        "source_quality": "provider_factsheet",
        "url_reference": "https://provider.example/fund",
        "file_reference": None,
        "as_of": "2026-06-09",
        "extracted_facts": {
            "name": "Synthetic FTAW Fund",
            "ticker": "FTAW",
            "isin_or_symbol": "SYNTHETICISIN",
            "provider": "Synthetic Provider",
            "index_tracked": "Synthetic Index",
            "replication_method": "physical",
        },
        "user_notes": "Synthetic test facts.",
    }
    data.update(overrides)
    return FTAWSourceFactRecord(**data)


def _guard(**overrides):
    data = {
        "asset_id": TARGET,
        "expected_name": "Synthetic FTAW Fund",
        "expected_ticker": "FTAW",
        "expected_isin_or_symbol": "SYNTHETICISIN",
        "expected_provider": "Synthetic Provider",
        "expected_index_tracked": "Synthetic Index",
        "allowed_source_names": ("Synthetic provider page",),
        "allowed_url_domains": ("provider.example",),
    }
    data.update(overrides)
    return FTAWSourceIdentityGuardConfig(**data)


def _run(record=None, guard=None):
    return build_ftaw_source_identity_guard(
        SOURCE_REGISTRY,
        REVIEWED_REGISTRY,
        FTAWSourceFactIntakeConfig(records=(record or _record(),)),
        guard or _guard(),
    )


class FTAWSourceIdentityGuardTests(unittest.TestCase):
    def test_only_ftaw_is_processed(self) -> None:
        other = _record(asset_id="webn_global_core_candidate")
        result = build_ftaw_source_identity_guard(
            SOURCE_REGISTRY,
            REVIEWED_REGISTRY,
            FTAWSourceFactIntakeConfig(records=(_record(), other)),
            _guard(),
        )

        self.assertTrue(result.identity_guard_passed)
        self.assertEqual(result.asset_id, TARGET)

    def test_platform_and_tax_route_are_skipped(self) -> None:
        platform = _record(evidence_type="platform_availability")
        tax = _record(evidence_type="tax_route")
        result = build_ftaw_source_identity_guard(
            SOURCE_REGISTRY,
            REVIEWED_REGISTRY,
            FTAWSourceFactIntakeConfig(records=(_record(), platform, tax)),
            _guard(),
        )

        self.assertEqual(result.skipped_evidence_types, ("platform_availability", "tax_route"))

    def test_missing_canonical_identity_causes_confirmation_needed(self) -> None:
        result = _run(guard=_guard(expected_provider=None))

        self.assertEqual(result.identity_guard_status, "needs_identity_confirmation")
        self.assertIn("expected_provider", result.missing_identity_fields)
        self.assertFalse(result.identity_guard_passed)

    def test_placeholder_identity_fields_do_not_pass(self) -> None:
        result = build_ftaw_source_identity_guard_from_files(SOURCE_REGISTRY, REVIEWED_REGISTRY, INTAKE_CONFIG, GUARD_CONFIG)

        self.assertEqual(result.identity_guard_status, "needs_identity_confirmation")
        self.assertFalse(result.identity_guard_passed)
        self.assertTrue(result.placeholder_identity_fields)

    def test_matching_synthetic_identity_passes_guard(self) -> None:
        result = _run()

        self.assertEqual(result.identity_guard_status, "identity_guard_passed")
        self.assertTrue(result.identity_guard_passed)
        self.assertEqual(set(result.matched_fields), {"name", "ticker", "isin_or_symbol", "provider", "index_tracked"})

    def test_provider_mismatch_blocks(self) -> None:
        result = _run(record=_record(extracted_facts={**_record().extracted_facts, "provider": "Wrong Provider"}))

        self.assertEqual(result.identity_guard_status, "BLOCKED")
        self.assertIn("provider", result.mismatched_fields)

    def test_ticker_mismatch_blocks(self) -> None:
        result = _run(record=_record(extracted_facts={**_record().extracted_facts, "ticker": "WRONG"}))

        self.assertEqual(result.identity_guard_status, "BLOCKED")
        self.assertIn("ticker", result.mismatched_fields)

    def test_isin_mismatch_blocks(self) -> None:
        result = _run(record=_record(extracted_facts={**_record().extracted_facts, "isin_or_symbol": "WRONGISIN"}))

        self.assertEqual(result.identity_guard_status, "BLOCKED")
        self.assertIn("isin_or_symbol", result.mismatched_fields)

    def test_source_name_mismatch_blocks(self) -> None:
        result = _run(record=_record(source_name="Wrong source"))

        self.assertEqual(result.identity_guard_status, "BLOCKED")
        self.assertIn("source_name", result.mismatched_fields)

    def test_url_domain_mismatch_blocks_when_configured(self) -> None:
        result = _run(record=_record(url_reference="https://wrong.example/fund"))

        self.assertEqual(result.identity_guard_status, "BLOCKED")
        self.assertIn("url_domain", result.mismatched_fields)

    def test_passing_identity_does_not_set_verified_by_user_true(self) -> None:
        result = _run()

        self.assertTrue(result.identity_guard_passed)
        self.assertFalse(result.approvals_created)

    def test_no_approval_status_changes_or_registry_mutation(self) -> None:
        before = Path(SOURCE_REGISTRY).read_text(encoding="utf-8")

        result = _run()

        self.assertEqual(before, Path(SOURCE_REGISTRY).read_text(encoding="utf-8"))
        self.assertFalse(result.registry_mutation_performed)
        self.assertFalse(result.approvals_created)

    def test_no_buy_sell_requests(self) -> None:
        result = _run()

        self.assertFalse(result.buy_sell_requests_created)
        self.assertFalse(result.allocation_recommendation_created)
        self.assertFalse(result.trades_executed)


if __name__ == "__main__":
    unittest.main()
