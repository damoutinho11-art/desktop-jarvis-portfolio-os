import unittest
from types import SimpleNamespace

from jarvis.jarvis_v21_0_crypto_public_signal_daily_readiness_bridge import (
    STATUS_BLOCKED,
    STATUS_REVIEW_REQUIRED,
    build_crypto_public_signal_daily_readiness_bridge,
    build_crypto_public_signal_daily_readiness_console_output,
)


class FakeNested:
    def to_dict(self):
        return {}


def fake_readiness(status="JARVIS_V16_0_REAL_DAILY_READINESS_GATE_REVIEW_REQUIRED_SAFE", warnings=("portfolio stale",), blockers=()):
    return SimpleNamespace(
        status=status,
        readiness_status="STALE_REVIEW_REQUIRED",
        stale_data_review_required="REVIEW_REQUIRED" in status,
        blockers=tuple(blockers),
        warnings=tuple(warnings),
        to_dict=lambda: {"status": status, "blockers": list(blockers), "warnings": list(warnings)},
    )


def fake_btc_signal(ready=True, blockers=(), warnings=()):
    return SimpleNamespace(
        quality_status="BTC_PUBLIC_SIGNAL_SOURCE_QUALITY_READY" if ready else "BTC_PUBLIC_SIGNAL_SOURCE_QUALITY_BLOCKED",
        source_quality_ready=ready,
        signal_age_days=0 if ready else None,
        candidate_id="btc",
        source_id="coingecko_btc_simple_price_eur",
        as_of="2026-06-17" if ready else "",
        price_eur=56545.0 if ready else None,
        market_cap_eur=1133363561099.58 if ready else None,
        volume_24h_eur=22234807893.14 if ready else None,
        change_24h_pct=-1.2204 if ready else None,
        provider_last_updated_utc="2026-06-17T00:10:53+00:00" if ready else "",
        blockers=tuple(blockers),
        warnings=tuple(warnings),
        to_dict=lambda: {"source_quality_ready": ready, "blockers": list(blockers), "warnings": list(warnings)},
    )


class JarvisV210CryptoPublicSignalDailyReadinessBridgeTests(unittest.TestCase):
    def test_integrates_quality_gated_btc_signal_without_mutation(self):
        result = build_crypto_public_signal_daily_readiness_bridge(
            daily_readiness_result=fake_readiness(),
            btc_public_signal_result=fake_btc_signal(),
        )

        self.assertEqual(result.status, STATUS_REVIEW_REQUIRED)
        self.assertTrue(result.crypto_public_signal_ready)
        self.assertTrue(result.crypto_public_signal_used_for_evidence)
        self.assertFalse(result.recommendation_quality_current_data)
        self.assertFalse(result.allocation_mutation)
        self.assertFalse(result.approval_ticket_mutation)
        self.assertFalse(result.buy_request_created)
        self.assertTrue(result.broker_connection_forbidden)
        self.assertTrue(result.no_trades_executed)

    def test_blocks_when_btc_signal_quality_gate_blocks(self):
        result = build_crypto_public_signal_daily_readiness_bridge(
            daily_readiness_result=fake_readiness(status="JARVIS_V16_0_REAL_DAILY_READINESS_GATE_READY_SAFE", warnings=()),
            btc_public_signal_result=fake_btc_signal(ready=False, blockers=("missing signal",)),
        )

        self.assertEqual(result.status, STATUS_BLOCKED)
        self.assertFalse(result.crypto_public_signal_ready)
        self.assertIn("missing signal", result.blockers)

    def test_console_output_surfaces_crypto_public_signal(self):
        result = build_crypto_public_signal_daily_readiness_bridge(
            daily_readiness_result=fake_readiness(),
            btc_public_signal_result=fake_btc_signal(),
        )
        output = build_crypto_public_signal_daily_readiness_console_output(result)

        self.assertIn("Crypto public signal:", output)
        self.assertIn("BTC signal: BTC_PUBLIC_SIGNAL_SOURCE_QUALITY_READY", output)
        self.assertIn("allocation/scoring/ticket unchanged", output)
        self.assertIn("no broker connection", output)
        self.assertIn("no trades executed", output)

    def test_invalid_current_date_blocks(self):
        result = build_crypto_public_signal_daily_readiness_bridge(
            current_date="17-06-2026",
            daily_readiness_result=fake_readiness(status="JARVIS_V16_0_REAL_DAILY_READINESS_GATE_READY_SAFE", warnings=()),
            btc_public_signal_result=fake_btc_signal(),
        )

        self.assertEqual(result.status, STATUS_BLOCKED)
        self.assertIn("current_date must use YYYY-MM-DD format when provided.", result.blockers)


if __name__ == "__main__":
    unittest.main()