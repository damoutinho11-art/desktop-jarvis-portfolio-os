from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from jarvis.runtime.personal_finance_contribution_bridge import build_personal_finance_contribution_bridge_result
from jarvis.tests.test_jarvis_v59_0_personal_finance_contribution_bridge import (
    _crypto_terms,
    _evidence,
    _legacy,
    _lightyear,
    _monthly_expenses,
    _snapshot,
)


class JarvisV600FullAllocationBlockerReconciliationTests(unittest.TestCase):
    def _paths(self, root: Path) -> dict[str, Path]:
        return {
            "expenses": root / "jarvis" / "local" / "monthly_expenses.local.json",
            "snapshot": root / "jarvis" / "local" / "manual_portfolio_snapshot.local.json",
            "lightyear": root / "jarvis" / "local" / "lightyear_instrument_universe.local.json",
            "crypto": root / "jarvis" / "local" / "crypto_facility_terms.local.json",
            "legacy": root / "jarvis" / "local" / "legacy_migration_review.local.json",
            "evidence": root / "outputs" / "free_research_evidence_pack_latest.json",
        }

    def _ready_inputs(self, root: Path, *, legacy_confirmed: bool) -> dict[str, Path]:
        paths = self._paths(root)
        _monthly_expenses(paths["expenses"])
        _snapshot(paths["snapshot"])
        _lightyear(paths["lightyear"], confirmed=True)
        _crypto_terms(paths["crypto"], confirmed=True)
        _legacy(paths["legacy"], confirmed=legacy_confirmed)
        _evidence(paths["evidence"], crypto=True, etf_fx=True)
        return paths

    def test_confirmed_legacy_review_removes_legacy_from_full_allocation_requirements(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = self._ready_inputs(Path(tmp), legacy_confirmed=True)

            result = build_personal_finance_contribution_bridge_result(
                current_date="2026-06-17",
                monthly_expenses_path=paths["expenses"],
                snapshot_path=paths["snapshot"],
                evidence_pack_path=paths["evidence"],
                lightyear_instrument_universe_path=paths["lightyear"],
                crypto_facility_terms_path=paths["crypto"],
                legacy_migration_review_path=paths["legacy"],
                manual_cost_basis_path=Path(tmp) / "jarvis" / "local" / "missing_manual_cost_basis.local.json",
            )

            self.assertTrue(result["trusted_monthly_contribution_decision_allowed"])
            self.assertNotIn("legacy_migration_review", result["full_allocation_still_requires"])
            self.assertEqual(
                result["full_allocation_still_requires"],
                ["correlation_risk_model", "stock_specific_public_evidence", "manual_cost_basis"],
            )
            self.assertFalse(result["full_allocation_allowed"])
            self.assertFalse(result["buy_request_created"])

    def test_unconfirmed_legacy_review_keeps_legacy_full_allocation_requirement(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = self._ready_inputs(Path(tmp), legacy_confirmed=False)

            result = build_personal_finance_contribution_bridge_result(
                current_date="2026-06-17",
                monthly_expenses_path=paths["expenses"],
                snapshot_path=paths["snapshot"],
                evidence_pack_path=paths["evidence"],
                lightyear_instrument_universe_path=paths["lightyear"],
                crypto_facility_terms_path=paths["crypto"],
                legacy_migration_review_path=paths["legacy"],
                manual_cost_basis_path=Path(tmp) / "jarvis" / "local" / "missing_manual_cost_basis.local.json",
            )

            self.assertIn("legacy_migration_review", result["full_allocation_still_requires"])
            self.assertFalse(result["full_allocation_allowed"])
            self.assertFalse(result["allocation_mutation"])
            self.assertFalse(result["approval_ticket_mutation"])


if __name__ == "__main__":
    unittest.main()
