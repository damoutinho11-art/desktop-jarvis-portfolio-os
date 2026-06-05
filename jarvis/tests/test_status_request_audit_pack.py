import json
import tempfile
import unittest
from pathlib import Path

from jarvis.asset_status_workflow import (
    ETF_INVESTABLE_CONFIRMATIONS,
    INVESTABLE_BASE_CONFIRMATIONS,
    WATCHLIST_CONFIRMATIONS,
    AssetStatusChangeRequest,
)
from jarvis.status_request_audit_pack import audit_status_bridge_result, audit_status_request
from jarvis.universe_status_bridge import UniverseStatusBridgeResult


def _request(
    current_status: str = "candidate_unreviewed",
    requested_status: str = "candidate_reviewed",
    confirmations: tuple[str, ...] = ("manual_review_completed",),
    manual_approval_required: bool = True,
    auto_execute: bool = False,
    asset_type: str = "ETF",
) -> AssetStatusChangeRequest:
    return AssetStatusChangeRequest(
        request_id=f"status_req_{current_status}_{requested_status}",
        created_at="2026-06-04T10:00:00+00:00",
        asset_id="quality_etf_candidate",
        asset_type=asset_type,
        current_status=current_status,
        requested_status=requested_status,
        rationale="Fixture-only status change.",
        evidence_summary="Synthetic evidence reviewed for a local audit pack.",
        required_confirmations=confirmations,
        manual_approval_required=manual_approval_required,
        auto_execute=auto_execute,
    )


def _registry_payload() -> dict[str, object]:
    return {
        "assets": [
            {
                "asset_id": "quality_etf_candidate",
                "name": "Quality ETF manual candidate",
                "asset_type": "ETF",
                "sleeve": "quality_etf",
                "ticker": "UNKNOWN",
                "isin_or_symbol": "UNKNOWN",
                "platforms": ["Lightyear"],
                "currency": "EUR",
                "domicile": "Ireland",
                "distribution_policy": "accumulating",
                "ter_or_fee": 0.0,
                "data_source": "manual_placeholder",
                "approval_status": "candidate_unreviewed",
                "risk_level": "medium",
                "provider": "unknown",
                "index_tracked": "unknown",
                "replication_method": "unknown",
            }
        ]
    }


class StatusRequestAuditPackTests(unittest.TestCase):
    def test_valid_candidate_unreviewed_to_candidate_reviewed_is_audit_ready(self) -> None:
        pack = audit_status_request(_request())

        self.assertTrue(pack.audit_ready)
        self.assertEqual(pack.validation_status, "valid")
        self.assertFalse(pack.registry_mutation_allowed)

    def test_candidate_reviewed_to_approved_watchlist_ready_with_confirmations(self) -> None:
        pack = audit_status_request(
            _request(
                current_status="candidate_reviewed",
                requested_status="approved_watchlist",
                confirmations=tuple(sorted(WATCHLIST_CONFIRMATIONS)),
            )
        )

        self.assertTrue(pack.audit_ready)

    def test_approved_watchlist_to_investable_requires_investable_confirmations(self) -> None:
        blocked = audit_status_request(
            _request(
                current_status="approved_watchlist",
                requested_status="approved_investable",
                confirmations=tuple(sorted(INVESTABLE_BASE_CONFIRMATIONS)),
            )
        )
        ready = audit_status_request(
            _request(
                current_status="approved_watchlist",
                requested_status="approved_investable",
                confirmations=tuple(sorted(set(INVESTABLE_BASE_CONFIRMATIONS) | set(ETF_INVESTABLE_CONFIRMATIONS))),
            )
        )

        self.assertFalse(blocked.audit_ready)
        self.assertIn("expense_ratio_reviewed", blocked.missing_confirmations)
        self.assertTrue(ready.audit_ready)

    def test_candidate_unreviewed_to_investable_is_blocked(self) -> None:
        pack = audit_status_request(
            _request(
                current_status="candidate_unreviewed",
                requested_status="approved_investable",
                confirmations=tuple(sorted(set(INVESTABLE_BASE_CONFIRMATIONS) | set(ETF_INVESTABLE_CONFIRMATIONS))),
            )
        )

        self.assertFalse(pack.audit_ready)
        self.assertIn("direct candidate_unreviewed -> approved_investable is forbidden.", pack.blockers)

    def test_test_position_to_investable_is_blocked(self) -> None:
        pack = audit_status_request(
            _request(
                current_status="test_position",
                requested_status="approved_investable",
                confirmations=tuple(sorted(set(INVESTABLE_BASE_CONFIRMATIONS) | set(ETF_INVESTABLE_CONFIRMATIONS))),
            )
        )

        self.assertFalse(pack.audit_ready)
        self.assertIn("direct test_position -> approved_investable is forbidden.", pack.blockers)

    def test_rejected_to_investable_is_blocked(self) -> None:
        pack = audit_status_request(
            _request(
                current_status="rejected",
                requested_status="approved_investable",
                confirmations=tuple(sorted(set(INVESTABLE_BASE_CONFIRMATIONS) | set(ETF_INVESTABLE_CONFIRMATIONS))),
            )
        )

        self.assertFalse(pack.audit_ready)
        self.assertIn("direct rejected -> approved_investable is forbidden.", pack.blockers)

    def test_missing_confirmations_blocks_audit_ready(self) -> None:
        pack = audit_status_request(
            _request(current_status="candidate_reviewed", requested_status="approved_watchlist", confirmations=())
        )

        self.assertFalse(pack.audit_ready)
        self.assertEqual(pack.validation_status, "blocked")
        self.assertIn("candidate_review_pack_present", pack.missing_confirmations)

    def test_auto_execute_true_blocks_audit_ready(self) -> None:
        pack = audit_status_request(_request(auto_execute=True))

        self.assertFalse(pack.audit_ready)
        self.assertTrue(pack.auto_execute)
        self.assertIn("auto_execute must always be false.", pack.blockers)

    def test_manual_approval_required_false_blocks_audit_ready(self) -> None:
        pack = audit_status_request(_request(manual_approval_required=False))

        self.assertFalse(pack.audit_ready)
        self.assertFalse(pack.manual_approval_required)
        self.assertIn("manual_approval_required must always be true.", pack.blockers)

    def test_audit_bridge_result_does_not_mutate_registry_or_create_approvals(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            registry_path = Path(temp_dir) / "registry.json"
            registry_path.write_text(json.dumps(_registry_payload(), indent=2), encoding="utf-8")
            before = registry_path.read_text(encoding="utf-8")
            bridge_result = UniverseStatusBridgeResult(
                status="PREVIEW_READY",
                status_requests=(_request(),),
                blocked_candidates=(),
                warnings=(),
                blockers=(),
                manual_approval_required=True,
                registry_mutation_forbidden=True,
            )

            result = audit_status_bridge_result(bridge_result, registry_path)

            self.assertEqual(before, registry_path.read_text(encoding="utf-8"))
            self.assertFalse(result.audit_packs[0].registry_mutation_allowed)
            self.assertTrue(result.summary.registry_mutation_forbidden)
            self.assertFalse(hasattr(result, "approval_requests"))


if __name__ == "__main__":
    unittest.main()
