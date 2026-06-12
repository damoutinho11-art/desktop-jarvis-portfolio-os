import unittest
from pathlib import Path

from jarvis.jarvis_manual_candidate_watchlist_entry import (
    INTENDED_ROUTE,
    PHASE1_ROUTE,
    load_watchlist_entry_pack,
    validate_watchlist_entry,
)


DEFAULT_WATCHLIST = "jarvis/data/jarvis_manual_candidate_watchlist_entry.example.json"
SYNTHETIC_MULTI = "jarvis/data/jarvis_manual_candidate_watchlist_entry.synthetic_multi.example.json"


def _entry(**overrides):
    base = {
        "watchlist_entry_id": "watch_test",
        "candidate_id": "synthetic_candidate",
        "display_name": "Synthetic Candidate",
        "asset_type": "etf",
        "symbol_or_identifier": "SYN",
        "issuer_or_provider": "Synthetic issuer",
        "market_or_region": "EU",
        "currency": "EUR",
        "watchlist_reason": "Manual watchlist test.",
        "watchlist_source_context": "synthetic manual entry",
        "manually_entered_by_user": True,
        "manual_entry_timestamp": "2026-06-12T00:00:00Z",
        "intended_route": INTENDED_ROUTE,
        "candidate_intake_required": True,
        "evidence_pipeline_required": True,
        "manual_review_required": True,
        "notes": "No approval.",
    }
    base.update(overrides)
    return base


class ManualCandidateWatchlistEntryTests(unittest.TestCase):
    def test_multiple_asset_types_are_accepted(self) -> None:
        pack = load_watchlist_entry_pack(SYNTHETIC_MULTI)
        asset_types = {entry.asset_type for entry in pack.entries}

        self.assertIn("etf", asset_types)
        self.assertIn("stock", asset_types)
        self.assertIn("crypto", asset_types)
        self.assertIn("other", asset_types)

    def test_unknown_and_other_require_review_and_do_not_approve(self) -> None:
        other = validate_watchlist_entry(_entry(asset_type="other"))
        unknown = validate_watchlist_entry(_entry(asset_type="mystery"))

        self.assertEqual(other.entry_status, "MANUAL_WATCHLIST_ENTRY_PARTIAL_SAFE")
        self.assertEqual(unknown.entry_status, "MANUAL_WATCHLIST_ENTRY_PARTIAL_SAFE")
        self.assertFalse(other.approved_asset)
        self.assertFalse(unknown.trusted_asset)

    def test_vwce_ftaw_are_not_only_allowed_candidates(self) -> None:
        pack = load_watchlist_entry_pack(SYNTHETIC_MULTI)
        ready_ids = {entry.candidate_id for entry in pack.entries if entry.entry_status == "MANUAL_WATCHLIST_ENTRY_READY_FOR_CANDIDATE_INTAKE"}

        self.assertIn("synthetic_stock_candidate", ready_ids)
        self.assertIn("synthetic_crypto_candidate", ready_ids)

    def test_required_fields_are_enforced(self) -> None:
        result = validate_watchlist_entry(
            _entry(watchlist_entry_id="", candidate_id="", display_name="", asset_type="", symbol_or_identifier="", watchlist_reason="")
        )

        self.assertEqual(result.entry_status, "MANUAL_WATCHLIST_ENTRY_BLOCKED_SAFE")
        self.assertGreaterEqual(len(result.blocked_reasons), 6)

    def test_unsafe_claims_are_blocked(self) -> None:
        for field in (
            "approved_asset",
            "trusted_asset",
            "investable",
            "verified_evidence",
            "promoted_verified_evidence",
            "allocation_recommendation",
            "portfolio_weight",
            "buy_signal",
            "sell_signal",
            "trade_executed",
            "registry_mutation",
            "executor_created",
            "broker_api_used",
            "credentials_used",
            "automatic_source_fetching",
            "automatic_download",
            "private_file_ingested",
        ):
            with self.subTest(field=field):
                result = validate_watchlist_entry(_entry(**{field: True}))
                self.assertEqual(result.entry_status, "MANUAL_WATCHLIST_ENTRY_BLOCKED_SAFE")
                self.assertTrue(any(field in reason for reason in result.blocked_reasons))

    def test_complete_entry_reaches_ready_and_produces_preview(self) -> None:
        result = validate_watchlist_entry(_entry())

        self.assertEqual(result.entry_status, "MANUAL_WATCHLIST_ENTRY_READY_FOR_CANDIDATE_INTAKE")
        self.assertTrue(result.candidate_intake_preview_available)
        self.assertIsNotNone(result.candidate_intake_preview)

    def test_partial_and_default_entries_are_safe(self) -> None:
        default_pack = load_watchlist_entry_pack(DEFAULT_WATCHLIST)
        multi_pack = load_watchlist_entry_pack(SYNTHETIC_MULTI)

        self.assertEqual(default_pack.overall_status, "MANUAL_WATCHLIST_ENTRY_BLOCKED_SAFE")
        self.assertEqual(multi_pack.overall_status, "MANUAL_WATCHLIST_ENTRY_PARTIAL_SAFE")
        self.assertTrue(any(entry.entry_status == "MANUAL_WATCHLIST_ENTRY_BLOCKED_SAFE" for entry in multi_pack.entries))

    def test_preview_includes_v4_49_and_phase1_route_and_safety_flags_false(self) -> None:
        result = validate_watchlist_entry(_entry())
        preview = result.candidate_intake_preview

        self.assertIsNotNone(preview)
        self.assertEqual(preview["intake_status"], "candidate_intake_required_pending")
        self.assertTrue(preview["created_by_manual_entry"])
        self.assertTrue(preview["manual_entry_required"])
        self.assertTrue(preview["evidence_pipeline_required"])
        self.assertEqual(preview["phase1_route"], PHASE1_ROUTE)
        self.assertFalse(preview["approved_asset"])
        self.assertFalse(preview["trusted_asset"])
        self.assertFalse(preview["investable"])
        self.assertFalse(preview["allocation_recommendation"])
        self.assertFalse(preview["buy_signal"])
        self.assertFalse(preview["sell_signal"])
        self.assertFalse(preview["trade_executed"])
        self.assertFalse(preview["registry_mutation"])
        self.assertFalse(preview["executor_created"])

    def test_no_registry_candidate_mutation_or_action_flags(self) -> None:
        before = Path(SYNTHETIC_MULTI).read_text(encoding="utf-8")
        pack = load_watchlist_entry_pack(SYNTHETIC_MULTI)

        self.assertEqual(before, Path(SYNTHETIC_MULTI).read_text(encoding="utf-8"))
        self.assertFalse(pack.registry_mutation)
        self.assertFalse(pack.approved_asset)
        self.assertFalse(pack.trusted_asset)
        self.assertFalse(pack.investable)
        self.assertFalse(pack.verified_evidence)
        self.assertFalse(pack.promoted_verified_evidence)
        self.assertFalse(pack.allocation_recommendation)
        self.assertFalse(pack.portfolio_weight)
        self.assertFalse(pack.buy_signal)
        self.assertFalse(pack.sell_signal)
        self.assertFalse(pack.trade_executed)
        self.assertFalse(pack.executor_created)


if __name__ == "__main__":
    unittest.main()
