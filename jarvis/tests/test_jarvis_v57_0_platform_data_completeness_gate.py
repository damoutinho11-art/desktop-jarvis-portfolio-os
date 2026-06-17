from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from jarvis.runtime import operator as runtime_operator
from jarvis.runtime.platform_data_completeness_gate import (
    GATE_BLOCKED,
    STATUS_BLOCKED,
    build_platform_data_completeness_gate_result,
    build_crypto_facility_terms_template,
    build_legacy_migration_review_template,
    build_lightyear_instrument_universe_template,
    format_platform_data_completeness_gate,
)


def _paths(tmp: str) -> tuple[Path, Path, Path]:
    root = Path(tmp)
    return (
        root / "lightyear_instrument_universe.local.json",
        root / "crypto_facility_terms.local.json",
        root / "legacy_migration_review.local.json",
    )


class JarvisV570PlatformDataCompletenessGateTests(unittest.TestCase):
    def test_missing_intake_blocks_trusted_weekly_action_but_structural_packet_exists(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            lightyear_path, crypto_path, legacy_path = _paths(tmp)
            result = build_platform_data_completeness_gate_result(
                current_date="2026-06-17",
                lightyear_instrument_universe_path=lightyear_path,
                crypto_facility_terms_path=crypto_path,
                legacy_migration_review_path=legacy_path,
            )

        self.assertEqual(result.status, STATUS_BLOCKED)
        self.assertEqual(result.gate_status, GATE_BLOCKED)
        self.assertTrue(result.structural_weekly_packet_available)
        self.assertFalse(result.trusted_weekly_action_allowed)
        self.assertFalse(result.full_allocation_allowed)
        self.assertIn("missing_lightyear_instrument_universe", result.blockers)
        self.assertIn("missing_crypto_facility_terms", result.blockers)
        self.assertIn("legacy_migration_review", result.full_allocation_blockers)
        self.assertIn("correlation_risk_model", result.full_allocation_blockers)
        self.assertIn("stock_specific_public_evidence", result.full_allocation_blockers)

    def test_crypto_candidates_include_lhv_kraken_and_other_without_default_approval(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            lightyear_path, crypto_path, legacy_path = _paths(tmp)
            result = build_platform_data_completeness_gate_result(
                current_date="2026-06-17",
                lightyear_instrument_universe_path=lightyear_path,
                crypto_facility_terms_path=crypto_path,
                legacy_migration_review_path=legacy_path,
            )

        candidates = {item.facility_id: item for item in result.crypto_candidates}
        self.assertIn("lhv", candidates)
        self.assertIn("kraken", candidates)
        self.assertIn("other_manual_facility", candidates)
        self.assertFalse(candidates["lhv"].approved_by_default)
        self.assertFalse(candidates["kraken"].approved_by_default)
        self.assertTrue(candidates["other_manual_facility"].manual_only)

    def test_written_templates_do_not_count_as_confirmed_platform_data(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            lightyear_path, crypto_path, legacy_path = _paths(tmp)
            result = build_platform_data_completeness_gate_result(
                current_date="2026-06-17",
                lightyear_instrument_universe_path=lightyear_path,
                crypto_facility_terms_path=crypto_path,
                legacy_migration_review_path=legacy_path,
                write_platform_data_templates=True,
            )

            self.assertTrue(lightyear_path.exists())
            self.assertTrue(crypto_path.exists())
            self.assertTrue(legacy_path.exists())

        self.assertFalse(result.trusted_weekly_action_allowed)
        self.assertFalse(result.lightyear_instrument_universe_confirmed)
        self.assertFalse(result.crypto_facility_terms_confirmed)
        self.assertIn("lightyear_instrument_universe_not_confirmed", result.blockers)
        self.assertIn("crypto_facility_terms_not_confirmed", result.blockers)
        self.assertEqual(len(result.templates_written), 3)

    def test_credential_like_keys_block_intake_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            lightyear_path, crypto_path, legacy_path = _paths(tmp)
            lightyear = build_lightyear_instrument_universe_template(current_date="2026-06-17")
            lightyear["is_template"] = False
            lightyear["platform_data_confirmed"] = True
            lightyear["api_key"] = "do-not-store-this"
            lightyear["instruments"][0]["tradable_confirmed_on_lightyear"] = True
            lightyear_path.write_text(json.dumps(lightyear), encoding="utf-8")

            crypto = build_crypto_facility_terms_template(current_date="2026-06-17")
            crypto["is_template"] = False
            crypto["terms_confirmed"] = True
            crypto["facilities"][0]["terms_confirmed"] = True
            crypto_path.write_text(json.dumps(crypto), encoding="utf-8")

            legacy_path.write_text(json.dumps(build_legacy_migration_review_template()), encoding="utf-8")

            result = build_platform_data_completeness_gate_result(
                current_date="2026-06-17",
                lightyear_instrument_universe_path=lightyear_path,
                crypto_facility_terms_path=crypto_path,
                legacy_migration_review_path=legacy_path,
            )

        self.assertFalse(result.trusted_weekly_action_allowed)
        self.assertIn("lightyear_instrument_universe contains forbidden credential-like keys", result.blockers)
        lightyear_status = [item for item in result.data_files if item.key == "lightyear_instrument_universe"][0]
        self.assertIn("api_key", lightyear_status.forbidden_credential_keys_found)

    def test_confirmed_platform_intake_allows_trusted_weekly_but_not_full_allocation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            lightyear_path, crypto_path, legacy_path = _paths(tmp)
            lightyear = build_lightyear_instrument_universe_template(current_date="2026-06-17")
            lightyear["is_template"] = False
            lightyear["platform_data_confirmed"] = True
            lightyear["instruments"][0]["tradable_confirmed_on_lightyear"] = True
            lightyear_path.write_text(json.dumps(lightyear), encoding="utf-8")

            crypto = build_crypto_facility_terms_template(current_date="2026-06-17")
            crypto["is_template"] = False
            crypto["terms_confirmed"] = True
            crypto["facilities"][0]["terms_confirmed"] = True
            crypto_path.write_text(json.dumps(crypto), encoding="utf-8")

            legacy_path.write_text(json.dumps(build_legacy_migration_review_template()), encoding="utf-8")

            result = build_platform_data_completeness_gate_result(
                current_date="2026-06-17",
                lightyear_instrument_universe_path=lightyear_path,
                crypto_facility_terms_path=crypto_path,
                legacy_migration_review_path=legacy_path,
            )

        self.assertTrue(result.trusted_weekly_action_allowed)
        self.assertTrue(result.lightyear_instrument_universe_confirmed)
        self.assertTrue(result.crypto_facility_terms_confirmed)
        self.assertFalse(result.full_allocation_allowed)
        self.assertIn("legacy_migration_review", result.full_allocation_blockers)
        self.assertIn("correlation_risk_model", result.full_allocation_blockers)
        self.assertIn("stock_specific_public_evidence", result.full_allocation_blockers)
        self.assertFalse(result.allocation_mutation)
        self.assertFalse(result.approval_ticket_mutation)
        self.assertFalse(result.evidence_pack_mutation)
        self.assertFalse(result.local_cache_mutation)
        self.assertFalse(result.portfolio_state_mutation)
        self.assertFalse(result.buy_request_created)
        self.assertTrue(result.no_trades_executed)

    def test_format_shows_gate_booleans_candidates_blockers_and_safety(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            lightyear_path, crypto_path, legacy_path = _paths(tmp)
            result = build_platform_data_completeness_gate_result(
                current_date="2026-06-17",
                lightyear_instrument_universe_path=lightyear_path,
                crypto_facility_terms_path=crypto_path,
                legacy_migration_review_path=legacy_path,
            )

        output = format_platform_data_completeness_gate(result)
        self.assertIn("PLATFORM DATA COMPLETENESS + INSTRUMENT INTAKE GATE", output)
        self.assertIn("structural weekly packet available: True", output)
        self.assertIn("trusted weekly action allowed: False", output)
        self.assertIn("full allocation allowed: False", output)
        self.assertIn("Kraken (kraken)", output)
        self.assertIn("approved by default=False", output)
        self.assertIn("missing_lightyear_instrument_universe", output)
        self.assertIn("no trades executed", output)

    def test_runtime_facade_routes_gate_and_template_command(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            lightyear_path, crypto_path, legacy_path = _paths(tmp)
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = runtime_operator.main(
                    [
                        "--write-platform-data-templates",
                        "--current-date",
                        "2026-06-17",
                        "--lightyear-instrument-universe-path",
                        str(lightyear_path),
                        "--crypto-facility-terms-path",
                        str(crypto_path),
                        "--legacy-migration-review-path",
                        str(legacy_path),
                    ]
                )

            self.assertEqual(exit_code, 0)
            self.assertTrue(lightyear_path.exists())
            self.assertTrue(crypto_path.exists())
            self.assertTrue(legacy_path.exists())
            self.assertIn("TEMPLATES_WRITTEN", stdout.getvalue())
            self.assertIn("trusted weekly action allowed: False", stdout.getvalue())

    def test_runtime_surface_reports_v57_and_platform_data_gate_module(self) -> None:
        surface = runtime_operator.get_active_runtime_surface()

        active_stage = str(surface["active_runtime_stage"])
        self.assertTrue(active_stage.startswith("v"))
        self.assertGreaterEqual(int(active_stage.split(".")[0].lstrip("v")), 57)
        self.assertEqual(
            surface["active_platform_data_completeness_gate_module"],
            "jarvis.runtime.platform_data_completeness_gate",
        )
        self.assertTrue(surface["execution_forbidden"])
        self.assertTrue(surface["manual_approval_required"])


if __name__ == "__main__":
    unittest.main()
