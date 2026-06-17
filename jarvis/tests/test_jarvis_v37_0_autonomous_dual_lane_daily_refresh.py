from __future__ import annotations

import unittest
from types import SimpleNamespace

from jarvis.jarvis_v37_0_autonomous_dual_lane_daily_refresh import (
    STATUS_BLOCKED,
    STATUS_READY,
    STATUS_REVIEW_REQUIRED,
    _is_legacy_pre_refresh_warning,
    build_autonomous_dual_lane_daily_refresh_result,
    format_autonomous_dual_lane_daily_refresh,
)


def _crypto_result(status: str = "JARVIS_V30_0_EXPANDED_CRYPTO_APPROVAL_TICKET_REFRESH_READY_SAFE") -> SimpleNamespace:
    return SimpleNamespace(
        status=status,
        approval_ticket_written=True,
        selected_crypto_candidate="hype",
        selected_crypto_amount_eur=41.54,
        blockers=(),
        warnings=(),
        to_dict=lambda: {"status": status, "selected_crypto_candidate": "hype"},
    )


def _etf_result(status: str = "JARVIS_V36_0_AUTONOMOUS_DAILY_REFRESH_ACTION_BRIEF_READY_SAFE") -> SimpleNamespace:
    return SimpleNamespace(
        status=status,
        approval_ticket_written=True,
        local_resolution_written=True,
        crypto_candidate="hype",
        crypto_amount_eur=41.54,
        stock_fund_etf_sleeve="quality_etf",
        stock_fund_etf_amount_eur=62.31,
        real_instrument_name="iShares Edge MSCI World Quality Factor UCITS ETF USD (Acc)",
        real_instrument_symbol="IS3Q.DE",
        real_instrument_isin="IE00BP3QZ601",
        real_instrument_source_as_of="2026-06-16",
        real_instrument_public_source_ready=True,
        blockers=(),
        warnings=(),
        to_dict=lambda: {"status": status, "real_instrument_symbol": "IS3Q.DE"},
    )


class JarvisV370AutonomousDualLaneDailyRefreshTests(unittest.TestCase):
    def test_runs_crypto_then_etf_refresh_and_clean_brief(self) -> None:
        calls: list[str] = []

        def crypto_builder(**kwargs):
            calls.append("crypto")
            self.assertTrue(kwargs["write_ticket"])
            self.assertTrue(kwargs["write_local_signals"])
            return _crypto_result()

        def etf_builder(**kwargs):
            calls.append("etf")
            self.assertTrue(kwargs["write_ticket"])
            self.assertTrue(kwargs["write_local_resolution"])
            return _etf_result()

        result = build_autonomous_dual_lane_daily_refresh_result(
            current_date="2026-06-17",
            crypto_refresh_builder=crypto_builder,
            etf_daily_builder=etf_builder,
        )

        self.assertEqual(calls, ["crypto", "etf"])
        self.assertEqual(result.status, STATUS_READY)
        self.assertTrue(result.crypto_refresh_ran)
        self.assertTrue(result.crypto_ticket_written)
        self.assertTrue(result.etf_refresh_ran)
        self.assertTrue(result.etf_ticket_written)
        self.assertEqual(result.crypto_candidate, "hype")
        self.assertEqual(result.real_instrument_symbol, "IS3Q.DE")
        self.assertFalse(result.buy_request_created)
        self.assertTrue(result.broker_connection_forbidden)
        self.assertTrue(result.no_trades_executed)

    def test_crypto_review_warning_is_not_legacy_cleanup(self) -> None:
        self.assertFalse(_is_legacy_pre_refresh_warning("crypto daily public-data refresh requires review"))
        self.assertFalse(_is_legacy_pre_refresh_warning("crypto daily public-data refresh requires review."))
    def test_crypto_legacy_only_review_allows_ready_after_ticket_write(self) -> None:
        result = build_autonomous_dual_lane_daily_refresh_result(
            current_date="2026-06-17",
            crypto_refresh_builder=lambda **kwargs: SimpleNamespace(
                status="JARVIS_V30_0_EXPANDED_CRYPTO_APPROVAL_TICKET_REFRESH_REVIEW_REQUIRED_SAFE",
                approval_ticket_written=True,
                selected_crypto_candidate="hype",
                selected_crypto_amount_eur=41.54,
                blockers=(),
                warnings=(
                    "approval_ticket_latest is 13 days old; refresh required before manual action.",
                    "Crypto-lane candidate changed from allocation basis btc to hype; approval ticket refresh is required before manual action.",
                ),
                to_dict=lambda: {},
            ),
            etf_daily_builder=lambda **kwargs: _etf_result(),
        )

        self.assertEqual(result.status, STATUS_READY)
        self.assertEqual(result.warnings, ())
    def test_crypto_review_required_makes_daily_review_but_still_runs_etf(self) -> None:
        result = build_autonomous_dual_lane_daily_refresh_result(
            current_date="2026-06-17",
            crypto_refresh_builder=lambda **kwargs: _crypto_result("JARVIS_V30_0_EXPANDED_CRYPTO_APPROVAL_TICKET_REFRESH_REVIEW_REQUIRED_SAFE"),
            etf_daily_builder=lambda **kwargs: _etf_result(),
        )

        self.assertEqual(result.status, STATUS_REVIEW_REQUIRED)
        self.assertTrue(result.etf_refresh_ran)
        self.assertIn("crypto daily public-data refresh requires review", result.warnings)

    def test_crypto_blocked_stops_before_etf(self) -> None:
        result = build_autonomous_dual_lane_daily_refresh_result(
            current_date="2026-06-17",
            crypto_refresh_builder=lambda **kwargs: SimpleNamespace(
                status="JARVIS_V30_0_EXPANDED_CRYPTO_APPROVAL_TICKET_REFRESH_BLOCKED_SAFE",
                approval_ticket_written=False,
                blockers=("crypto blocker",),
                warnings=(),
                to_dict=lambda: {},
            ),
            etf_daily_builder=lambda **kwargs: _etf_result(),
        )

        self.assertEqual(result.status, STATUS_BLOCKED)
        self.assertTrue(result.crypto_refresh_ran)
        self.assertFalse(result.etf_refresh_ran)
        self.assertIn("crypto blocker", result.blockers)

    def test_no_write_flags_are_passed_down(self) -> None:
        seen: dict[str, bool] = {}

        def crypto_builder(**kwargs):
            seen["crypto_write_ticket"] = kwargs["write_ticket"]
            seen["crypto_write_local_signals"] = kwargs["write_local_signals"]
            return _crypto_result()

        def etf_builder(**kwargs):
            seen["etf_write_ticket"] = kwargs["write_ticket"]
            seen["etf_write_local_resolution"] = kwargs["write_local_resolution"]
            return _etf_result()

        build_autonomous_dual_lane_daily_refresh_result(
            current_date="2026-06-17",
            write_ticket=False,
            write_local_signals=False,
            write_local_resolution=False,
            crypto_refresh_builder=crypto_builder,
            etf_daily_builder=etf_builder,
        )

        self.assertFalse(seen["crypto_write_ticket"])
        self.assertFalse(seen["crypto_write_local_signals"])
        self.assertFalse(seen["etf_write_ticket"])
        self.assertFalse(seen["etf_write_local_resolution"])

    def test_successful_dual_refresh_filters_legacy_pre_refresh_warnings(self) -> None:
        result = build_autonomous_dual_lane_daily_refresh_result(
            current_date="2026-06-17",
            crypto_refresh_builder=lambda **kwargs: SimpleNamespace(
                status="JARVIS_V30_0_EXPANDED_CRYPTO_APPROVAL_TICKET_REFRESH_REVIEW_REQUIRED_SAFE",
                approval_ticket_written=True,
                selected_crypto_candidate="hype",
                selected_crypto_amount_eur=41.54,
                blockers=(),
                warnings=(
                    "ETF universe has no as_of/updated_at metadata; scoring inputs are treated as manually maintained local scores.",
                    "approval_ticket_latest is 13 days old; refresh required before manual action.",
                    "Crypto-lane candidate changed from allocation basis btc to hype; approval ticket refresh is required before manual action.",
                ),
                to_dict=lambda: {},
            ),
            etf_daily_builder=lambda **kwargs: _etf_result(),
        )

        self.assertEqual(result.status, STATUS_READY)
        self.assertEqual(result.warnings, ())
    def test_console_mentions_both_lanes_and_safety(self) -> None:
        result = build_autonomous_dual_lane_daily_refresh_result(
            current_date="2026-06-17",
            crypto_refresh_builder=lambda **kwargs: _crypto_result(),
            etf_daily_builder=lambda **kwargs: _etf_result(),
        )

        output = format_autonomous_dual_lane_daily_refresh(result)

        self.assertIn("Autonomous Dual-Lane Daily Refresh", output)
        self.assertIn("Crypto lane:", output)
        self.assertIn("Candidate: hype", output)
        self.assertIn("Stock/Fund/ETF lane:", output)
        self.assertIn("IS3Q.DE", output)
        self.assertIn("no broker connection", output)
        self.assertIn("no trades executed", output)


if __name__ == "__main__":
    unittest.main()