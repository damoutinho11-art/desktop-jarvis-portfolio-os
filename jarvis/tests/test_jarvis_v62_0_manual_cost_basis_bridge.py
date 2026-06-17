from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from jarvis.runtime.allocation_strategy_audit import build_allocation_strategy_data_coverage_audit_result
from jarvis.runtime.personal_finance_contribution_bridge import build_personal_finance_contribution_bridge_result
from jarvis.tests.test_jarvis_v59_0_personal_finance_contribution_bridge import (
    _crypto_terms,
    _evidence,
    _legacy,
    _lightyear,
    _monthly_expenses,
    _snapshot,
)
from jarvis.tests.test_jarvis_v61_0_manual_cost_basis_intake import _confirmed_cost_basis


class JarvisV620ManualCostBasisBridgeTests(unittest.TestCase):
    def _paths(self, root: Path) -> dict[str, Path]:
        return {
            "expenses": root / "jarvis" / "local" / "monthly_expenses.local.json",
            "snapshot": root / "jarvis" / "local" / "manual_portfolio_snapshot.local.json",
            "lightyear": root / "jarvis" / "local" / "lightyear_instrument_universe.local.json",
            "crypto": root / "jarvis" / "local" / "crypto_facility_terms.local.json",
            "legacy": root / "jarvis" / "local" / "legacy_migration_review.local.json",
            "cost_basis": root / "jarvis" / "local" / "manual_cost_basis.local.json",
            "evidence": root / "outputs" / "free_research_evidence_pack_latest.json",
        }

    def _ready_inputs(self, root: Path, *, cost_basis_confirmed: bool = True) -> dict[str, Path]:
        paths = self._paths(root)
        _monthly_expenses(paths["expenses"])
        _snapshot(paths["snapshot"])
        _lightyear(paths["lightyear"], confirmed=True)
        _crypto_terms(paths["crypto"], confirmed=True)
        _legacy(paths["legacy"], confirmed=True)
        _evidence(paths["evidence"], crypto=True, etf_fx=True)
        if cost_basis_confirmed:
            _confirmed_cost_basis(paths["cost_basis"])
        return paths

    def test_contribution_bridge_removes_manual_cost_basis_when_v61_file_ready(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = self._ready_inputs(Path(tmp), cost_basis_confirmed=True)

            result = build_personal_finance_contribution_bridge_result(
                current_date="2026-06-17",
                monthly_expenses_path=paths["expenses"],
                snapshot_path=paths["snapshot"],
                evidence_pack_path=paths["evidence"],
                lightyear_instrument_universe_path=paths["lightyear"],
                crypto_facility_terms_path=paths["crypto"],
                legacy_migration_review_path=paths["legacy"],
                manual_cost_basis_path=paths["cost_basis"],
            )

            self.assertTrue(result["trusted_monthly_contribution_decision_allowed"])
            self.assertTrue(result["manual_cost_basis_ready"])
            self.assertNotIn("manual_cost_basis", result["full_allocation_still_requires"])
            self.assertEqual(
                result["full_allocation_still_requires"],
                ["correlation_risk_model", "stock_specific_public_evidence"],
            )
            self.assertFalse(result["full_allocation_allowed"])
            self.assertFalse(result["buy_request_created"])

    def test_contribution_bridge_keeps_manual_cost_basis_when_v61_file_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = self._ready_inputs(Path(tmp), cost_basis_confirmed=False)

            result = build_personal_finance_contribution_bridge_result(
                current_date="2026-06-17",
                monthly_expenses_path=paths["expenses"],
                snapshot_path=paths["snapshot"],
                evidence_pack_path=paths["evidence"],
                lightyear_instrument_universe_path=paths["lightyear"],
                crypto_facility_terms_path=paths["crypto"],
                legacy_migration_review_path=paths["legacy"],
                manual_cost_basis_path=paths["cost_basis"],
            )

            self.assertFalse(result["manual_cost_basis_ready"])
            self.assertIn("manual_cost_basis", result["full_allocation_still_requires"])
            self.assertFalse(result["full_allocation_allowed"])

    def test_allocation_audit_marks_manual_cost_basis_covered_from_v61_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = self._ready_inputs(Path(tmp), cost_basis_confirmed=True)
            upstream = SimpleNamespace(
                status="READY",
                blockers=(),
                warnings=(),
                evidence_items=(
                    SimpleNamespace(lane="crypto", usable_for_research=True),
                    SimpleNamespace(lane="fx", usable_for_research=True),
                ),
                source_confidence_score=70,
                source_confidence_grade="MEDIUM_HIGH_FREE_STACK",
                paid_api_required_now=False,
                broker_api_required_now=False,
                free_stack_sufficient_for_weekly_investing=True,
            )

            result = build_allocation_strategy_data_coverage_audit_result(
                current_date="2026-06-17",
                manual_portfolio_snapshot_path=paths["snapshot"],
                manual_cost_basis_path=paths["cost_basis"],
                upstream_result=upstream,
            )

            coverage = {item.key: item for item in result.coverage_items}
            self.assertTrue(coverage["manual_cost_basis"].available)
            self.assertEqual(coverage["manual_cost_basis"].status, "COVERED")
            self.assertNotIn("manual_cost_basis", result.missing_full_allocation_required_keys)
            self.assertEqual(
                set(result.missing_full_allocation_required_keys),
                {"stock_specific_public_evidence", "correlation_risk_model"},
            )
            self.assertFalse(result.full_allocation_allowed)
            self.assertFalse(result.allocation_mutation)
            self.assertFalse(result.buy_request_created)


if __name__ == "__main__":
    unittest.main()
