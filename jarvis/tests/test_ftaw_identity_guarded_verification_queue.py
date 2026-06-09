import unittest
from pathlib import Path

from jarvis.ftaw_identity_guarded_verification_queue import (
    FTAWIdentityGuardedVerificationQueueConfig,
    build_ftaw_identity_guarded_verification_queue,
    build_ftaw_identity_guarded_verification_queue_from_files,
)
from jarvis.ftaw_source_fact_intake import FTAWSourceFactIntakeConfig, FTAWSourceFactRecord
from jarvis.ftaw_source_identity_guard import FTAWSourceIdentityGuardConfig


SOURCE_REGISTRY = "jarvis/data/candidate_assets.v2.example.json"
URL_FETCH_CONFIG = "jarvis/data/ftaw_public_url_fetch_adapter.example.json"
INTAKE_CONFIG = "jarvis/data/ftaw_source_fact_intake.example.json"
GUARD_CONFIG = "jarvis/data/ftaw_source_identity_guard.example.json"
QUEUE_CONFIG = "jarvis/data/ftaw_identity_guarded_verification_queue.example.json"
TARGET = "ftaw_global_core_candidate"


def _fund_record(**overrides):
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


def _run(records, guard=None):
    return build_ftaw_identity_guarded_verification_queue(
        SOURCE_REGISTRY,
        None,
        URL_FETCH_CONFIG,
        FTAWSourceFactIntakeConfig(records=tuple(records)),
        guard or _guard(),
        FTAWIdentityGuardedVerificationQueueConfig(target_asset_id=TARGET),
    )


class FTAWIdentityGuardedVerificationQueueTests(unittest.TestCase):
    def test_placeholder_identity_does_not_become_eligible(self) -> None:
        guard = _guard(expected_provider="<expected_provider_to_confirm>")
        queue = _run([_fund_record()], guard)

        self.assertEqual(queue.needs_identity_confirmation_count, 1)
        self.assertEqual(queue.eligible_for_manual_verification_count, 0)
        self.assertEqual(queue.items[0].queue_status, "needs_identity_confirmation")

    def test_missing_source_facts_do_not_become_eligible(self) -> None:
        facts = dict(_fund_record().extracted_facts)
        facts["replication_method"] = "<replication_method_to_capture>"
        queue = _run([_fund_record(extracted_facts=facts)])

        self.assertEqual(queue.needs_source_facts_count, 1)
        self.assertEqual(queue.eligible_for_manual_verification_count, 0)
        self.assertEqual(queue.items[0].queue_status, "needs_source_facts")

    def test_provider_mismatch_blocks(self) -> None:
        facts = {**_fund_record().extracted_facts, "provider": "Wrong Provider"}
        queue = _run([_fund_record(extracted_facts=facts)])

        self.assertEqual(queue.blocked_source_identity_mismatch_count, 1)
        self.assertEqual(queue.items[0].queue_status, "blocked_source_identity_mismatch")

    def test_ticker_mismatch_blocks(self) -> None:
        facts = {**_fund_record().extracted_facts, "ticker": "WRONG"}
        queue = _run([_fund_record(extracted_facts=facts)])

        self.assertEqual(queue.blocked_source_identity_mismatch_count, 1)
        self.assertEqual(queue.items[0].queue_status, "blocked_source_identity_mismatch")

    def test_isin_or_symbol_mismatch_blocks(self) -> None:
        facts = {**_fund_record().extracted_facts, "isin_or_symbol": "WRONGISIN"}
        queue = _run([_fund_record(extracted_facts=facts)])

        self.assertEqual(queue.blocked_source_identity_mismatch_count, 1)
        self.assertEqual(queue.items[0].queue_status, "blocked_source_identity_mismatch")

    def test_source_name_mismatch_blocks(self) -> None:
        queue = _run([_fund_record(source_name="Wrong source")])

        self.assertEqual(queue.blocked_source_identity_mismatch_count, 1)
        self.assertEqual(queue.items[0].queue_status, "blocked_source_identity_mismatch")

    def test_url_domain_mismatch_blocks(self) -> None:
        queue = _run([_fund_record(url_reference="https://wrong.example/fund")])

        self.assertEqual(queue.blocked_source_identity_mismatch_count, 1)
        self.assertEqual(queue.items[0].queue_status, "blocked_source_identity_mismatch")

    def test_matching_synthetic_identity_becomes_eligible(self) -> None:
        queue = _run([_fund_record()])

        self.assertEqual(queue.queue_status, "READY_FOR_MANUAL_VERIFICATION")
        self.assertEqual(queue.eligible_for_manual_verification_count, 1)
        self.assertEqual(queue.items[0].queue_status, "eligible_for_manual_verification")

    def test_manual_only_evidence_types_are_skipped(self) -> None:
        queue = _run([
            _fund_record(evidence_type="platform_availability"),
            _fund_record(evidence_type="tax_route"),
            _fund_record(),
        ])

        statuses = {item.evidence_type: item.queue_status for item in queue.items}
        self.assertEqual(statuses["platform_availability"], "manual_only_skipped")
        self.assertEqual(statuses["tax_route"], "manual_only_skipped")
        self.assertEqual(queue.manual_only_skipped_count, 2)

    def test_eligible_items_remain_unverified(self) -> None:
        queue = _run([_fund_record()])

        self.assertFalse(queue.items[0].verified_by_user)

    def test_no_approval_status_changes_or_registry_mutation(self) -> None:
        before = Path(SOURCE_REGISTRY).read_text(encoding="utf-8")

        queue = _run([_fund_record()])

        self.assertEqual(before, Path(SOURCE_REGISTRY).read_text(encoding="utf-8"))
        self.assertFalse(queue.registry_mutation_performed)
        self.assertFalse(queue.approvals_created)

    def test_no_buy_sell_requests_or_trades(self) -> None:
        queue = _run([_fund_record()])

        self.assertFalse(queue.buy_sell_requests_created)
        self.assertFalse(queue.allocation_recommendation_created)
        self.assertFalse(queue.trades_executed)

    def test_default_example_placeholder_identity_is_not_ready(self) -> None:
        queue = build_ftaw_identity_guarded_verification_queue_from_files(
            SOURCE_REGISTRY,
            None,
            URL_FETCH_CONFIG,
            INTAKE_CONFIG,
            GUARD_CONFIG,
            QUEUE_CONFIG,
        )

        self.assertEqual(queue.total_input_items, 5)
        self.assertEqual(queue.eligible_for_manual_verification_count, 0)
        self.assertEqual(queue.needs_source_facts_count, 5)


if __name__ == "__main__":
    unittest.main()
