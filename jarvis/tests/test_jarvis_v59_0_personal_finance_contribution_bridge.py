from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from jarvis.runtime.personal_finance_contribution_bridge import (
    STATUS_BLOCKED,
    STATUS_REVIEW_REQUIRED,
    build_personal_finance_contribution_bridge_result,
    format_personal_finance_contribution_bridge,
    main as bridge_main,
)


def _write(path: Path, payload: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def _monthly_expenses(path: Path) -> Path:
    return _write(
        path,
        {
            "schema": "JARVIS_MONTHLY_EXPENSES_V1",
            "as_of": "2026-06-17",
            "is_template": False,
            "expenses_confirmed": True,
            "currency": "EUR",
            "minimum_emergency_months": 3,
            "ideal_emergency_months": 6,
            "planned_monthly_contribution_eur": 500,
            "expense_categories": [
                {"category_id": "rent", "monthly_eur": 420, "expense_type": "survival"},
                {"category_id": "utilities", "monthly_eur": 80, "expense_type": "survival"},
                {"category_id": "bills", "monthly_eur": 55, "expense_type": "survival"},
                {"category_id": "food_basic", "monthly_eur": 250, "expense_type": "survival"},
                {"category_id": "transport", "monthly_eur": 0, "expense_type": "survival"},
                {"category_id": "phone_internet", "monthly_eur": 13, "expense_type": "normal"},
                {"category_id": "annual_travel_portugal", "monthly_eur": 100, "expense_type": "normal"},
                {"category_id": "gym", "monthly_eur": 50, "expense_type": "flexible"},
                {"category_id": "restaurants_coffee", "monthly_eur": 50, "expense_type": "flexible"},
                {"category_id": "clothes_personal", "monthly_eur": 30, "expense_type": "flexible"},
            ],
        },
    )


def _snapshot(path: Path) -> Path:
    return _write(
        path,
        {
            "schema": "JARVIS_MANUAL_PORTFOLIO_SNAPSHOT_V1",
            "snapshot_date": "2026-06-17",
            "is_template": False,
            "brokerless_manual_snapshot": True,
            "emergency_fund_reserved_eur": 3600.0,
            "cash_eur": 703.21,
            "holdings": [
                {
                    "instrument_id": "btc_lhv_crypto",
                    "asset_name": "Bitcoin",
                    "symbol": "BTC",
                    "lane": "crypto",
                    "market_value_eur": 20.12,
                },
                {
                    "instrument_id": "legacy_etf_positions",
                    "asset_name": "Legacy ETF/fund positions",
                    "symbol": "LEGACY_ETF",
                    "lane": "stock_fund_etf",
                    "market_value_eur": 1136.18,
                },
            ],
            "totals": {
                "visible_cash_excluding_emergency_eur": 703.21,
                "emergency_fund_reserved_eur": 3600.0,
                "visible_invested_assets_eur": 1156.30,
                "visible_portfolio_excluding_emergency_eur": 1859.51,
                "visible_total_including_emergency_eur": 5459.51,
            },
        },
    )


def _lightyear(path: Path, *, confirmed: bool = True) -> Path:
    return _write(
        path,
        {
            "schema": "JARVIS_LIGHTYEAR_INSTRUMENT_UNIVERSE_V1",
            "is_template": not confirmed,
            "platform": "Lightyear",
            "platform_data_confirmed": confirmed,
            "broker_api_used": False,
            "instruments": [
                {
                    "symbol": "IS3Q",
                    "ticker": "IS3Q:XETRA",
                    "isin": "IE00BP3QZ601",
                    "currency": "EUR",
                    "tradable_confirmed_on_lightyear": confirmed,
                }
            ],
        },
    )


def _crypto_terms(path: Path, *, confirmed: bool = True) -> Path:
    return _write(
        path,
        {
            "schema": "JARVIS_CRYPTO_FACILITY_TERMS_V1",
            "is_template": not confirmed,
            "terms_confirmed": confirmed,
            "manual_only": True,
            "max_crypto_allocation_percent": 20,
            "auto_buy_allowed": False,
            "broker_connection_allowed": False,
            "order_creation_allowed": False,
            "trade_execution_allowed": False,
        },
    )


def _legacy(path: Path, *, confirmed: bool = False) -> Path:
    return _write(
        path,
        {
            "schema": "JARVIS_LEGACY_MIGRATION_REVIEW_V1",
            "is_template": not confirmed,
            "migration_review_confirmed": confirmed,
        },
    )


def _evidence(path: Path, *, crypto: bool = True, etf_fx: bool = True) -> Path:
    items = []
    if crypto:
        items.append(
            {
                "provider_id": "coingecko_free_or_demo",
                "lane": "crypto",
                "data_kind": "simple_price_market_snapshot",
                "status": "PUBLIC_CRYPTO_SOURCE_READY",
                "source_quality": "PUBLIC_CRYPTO_SOURCE_READY",
                "usable_for_research": True,
            }
        )
    if etf_fx:
        items.append(
            {
                "provider_id": "ecb_fx_official",
                "lane": "fx",
                "data_kind": "eur_reference_latest",
                "status": "OFFICIAL_FREE_SOURCE_READY",
                "source_quality": "OFFICIAL_FREE_SOURCE_READY",
                "usable_for_research": True,
            }
        )
    return _write(path, {"evidence_items": items})


class JarvisV590PersonalFinanceContributionBridgeTests(unittest.TestCase):
    def _paths(self, root: Path) -> dict[str, Path]:
        return {
            "expenses": root / "jarvis" / "local" / "monthly_expenses.local.json",
            "snapshot": root / "jarvis" / "local" / "manual_portfolio_snapshot.local.json",
            "lightyear": root / "jarvis" / "local" / "lightyear_instrument_universe.local.json",
            "crypto": root / "jarvis" / "local" / "crypto_facility_terms.local.json",
            "legacy": root / "jarvis" / "local" / "legacy_migration_review.local.json",
            "evidence": root / "outputs" / "free_research_evidence_pack_latest.json",
        }

    def _ready_inputs(self, root: Path) -> dict[str, Path]:
        paths = self._paths(root)
        _monthly_expenses(paths["expenses"])
        _snapshot(paths["snapshot"])
        _lightyear(paths["lightyear"])
        _crypto_terms(paths["crypto"])
        _legacy(paths["legacy"], confirmed=False)
        _evidence(paths["evidence"])
        return paths

    def test_trusted_monthly_contribution_decision_uses_expense_categories_and_emergency_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = self._ready_inputs(Path(tmp))

            result = build_personal_finance_contribution_bridge_result(
                current_date="2026-06-17",
                monthly_expenses_path=paths["expenses"],
                snapshot_path=paths["snapshot"],
                evidence_pack_path=paths["evidence"],
                lightyear_instrument_universe_path=paths["lightyear"],
                crypto_facility_terms_path=paths["crypto"],
                legacy_migration_review_path=paths["legacy"],
            )

            self.assertEqual(result["status"], STATUS_REVIEW_REQUIRED)
            self.assertTrue(result["trusted_monthly_contribution_decision_allowed"])
            self.assertFalse(result["full_allocation_allowed"])
            self.assertEqual(result["monthly_contribution_eur"], 500.0)
            self.assertEqual(result["normal_monthly_expenses_eur"], 1048.0)
            self.assertEqual(result["survival_monthly_expenses_eur"], 805.0)
            self.assertEqual(result["flexible_monthly_expenses_eur"], 130.0)
            self.assertEqual(result["current_emergency_fund_eur"], 3600.0)
            self.assertEqual(result["suggested_monthly_emergency_top_up_eur"], 75.0)
            self.assertEqual(result["suggested_monthly_investment_after_emergency_eur"], 425.0)
            self.assertEqual(result["crypto_amount_eur"], 170.0)
            self.assertEqual(result["stock_fund_etf_amount_eur"], 255.0)
            self.assertEqual(result["individual_stock_amount_eur"], 0.0)
            self.assertEqual(result["blockers"], [])
            self.assertFalse(result["allocation_mutation"])
            self.assertFalse(result["approval_ticket_mutation"])
            self.assertFalse(result["buy_request_created"])
            self.assertTrue(result["final_user_buy_action_required"])

    def test_missing_lightyear_instrument_universe_blocks_trusted_decision(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = self._ready_inputs(Path(tmp))
            _lightyear(paths["lightyear"], confirmed=False)

            result = build_personal_finance_contribution_bridge_result(
                current_date="2026-06-17",
                monthly_expenses_path=paths["expenses"],
                snapshot_path=paths["snapshot"],
                evidence_pack_path=paths["evidence"],
                lightyear_instrument_universe_path=paths["lightyear"],
                crypto_facility_terms_path=paths["crypto"],
                legacy_migration_review_path=paths["legacy"],
            )

            self.assertEqual(result["status"], STATUS_BLOCKED)
            self.assertFalse(result["trusted_monthly_contribution_decision_allowed"])
            self.assertIn("lightyear_instrument_universe_not_confirmed", result["blockers"])
            self.assertTrue(all(not action["allowed_by_decision"] for action in result["manual_actions"]))

    def test_missing_public_evidence_blocks_trusted_decision(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = self._ready_inputs(Path(tmp))
            _evidence(paths["evidence"], crypto=False, etf_fx=True)

            result = build_personal_finance_contribution_bridge_result(
                current_date="2026-06-17",
                monthly_expenses_path=paths["expenses"],
                snapshot_path=paths["snapshot"],
                evidence_pack_path=paths["evidence"],
                lightyear_instrument_universe_path=paths["lightyear"],
                crypto_facility_terms_path=paths["crypto"],
                legacy_migration_review_path=paths["legacy"],
            )

            self.assertEqual(result["status"], STATUS_BLOCKED)
            self.assertIn("crypto_public_evidence_missing", result["blockers"])
            self.assertFalse(result["trusted_monthly_contribution_decision_allowed"])

    def test_format_includes_manual_actions_and_safety_invariants(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = self._ready_inputs(Path(tmp))
            result = build_personal_finance_contribution_bridge_result(
                current_date="2026-06-17",
                monthly_expenses_path=paths["expenses"],
                snapshot_path=paths["snapshot"],
                evidence_pack_path=paths["evidence"],
                lightyear_instrument_universe_path=paths["lightyear"],
                crypto_facility_terms_path=paths["crypto"],
                legacy_migration_review_path=paths["legacy"],
            )

            text = format_personal_finance_contribution_bridge(result)

            self.assertIn("J.A.R.V.I.S. PERSONAL FINANCE CONTRIBUTION DECISION BRIDGE", text)
            self.assertIn("trusted monthly contribution decision allowed: True", text)
            self.assertIn("recommended emergency top-up EUR: 75.0", text)
            self.assertIn("recommended crypto amount EUR: 170.0", text)
            self.assertIn("recommended ETF/fund amount EUR: 255.0", text)
            self.assertIn("- no broker connection", text)
            self.assertIn("- no trades executed", text)

    def test_cli_main_prints_bridge(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = self._ready_inputs(Path(tmp))
            output = io.StringIO()

            with contextlib.redirect_stdout(output):
                code = bridge_main(
                    [
                        "--personal-finance-contribution-bridge",
                        "--current-date",
                        "2026-06-17",
                        "--monthly-expenses-path",
                        str(paths["expenses"]),
                        "--manual-portfolio-snapshot-path",
                        str(paths["snapshot"]),
                        "--evidence-pack-path",
                        str(paths["evidence"]),
                        "--lightyear-instrument-universe-path",
                        str(paths["lightyear"]),
                        "--crypto-facility-terms-path",
                        str(paths["crypto"]),
                        "--legacy-migration-review-path",
                        str(paths["legacy"]),
                    ]
                )

            self.assertEqual(code, 0)
            self.assertIn("trusted monthly contribution decision allowed: True", output.getvalue())
            self.assertIn("recommended investable amount EUR: 425.0", output.getvalue())


if __name__ == "__main__":
    unittest.main()
