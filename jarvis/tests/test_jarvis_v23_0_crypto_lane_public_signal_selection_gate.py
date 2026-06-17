from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from jarvis.jarvis_v22_0_multi_crypto_public_data_quality_pipeline import (
    DEFAULT_CANDIDATES,
    build_multi_crypto_public_data_quality_pipeline_result,
)
from jarvis.jarvis_v23_0_crypto_lane_public_signal_selection_gate import (
    DECISION_BLOCKED_BY_PLATFORM,
    DECISION_BLOCKED_BY_SOURCE_QUALITY,
    DECISION_SELECTED,
    STATUS_READY,
    STATUS_REVIEW_REQUIRED,
    build_crypto_lane_public_signal_selection_gate_result,
    format_crypto_lane_public_signal_selection_gate,
)


def _write_raw(root: Path, source_id: str, coingecko_key: str, *, as_of: str = "2026-06-17", price: float = 10.0) -> None:
    raw_dir = root / "jarvis" / "local" / "public_data" / "v10_raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        coingecko_key: {
            "eur": price,
            "eur_market_cap": 1000000.0,
            "eur_24h_vol": 100000.0,
            "eur_24h_change": 1.0,
            "last_updated_at": 1781656726,
        }
    }
    (raw_dir / f"{as_of}_{source_id}.json.raw").write_text(json.dumps(payload), encoding="utf-8")


def _public_signal_result(root: Path):
    for config in DEFAULT_CANDIDATES:
        price = 56000.0 if config.candidate_id == "btc" else 50.0
        _write_raw(root, config.source_id, config.coingecko_key, price=price)
    return build_multi_crypto_public_data_quality_pipeline_result(root=root, current_date="2026-06-17")


def _constitution() -> dict:
    return {
        "asset_routes": {
            "btc": "lhv_crypto",
            "hype": "lhv_crypto",
            "tao": "kraken",
        }
    }


def _portfolio_state() -> dict:
    return {
        "platform_status": {
            "lhv_crypto_ready": True,
            "kraken_ready": False,
        }
    }


def _allocation_result(**amounts: int) -> dict:
    return {
        "ideal_allocations_cents": {
            "btc": amounts.get("btc_ideal", amounts.get("btc", 0)),
            "hype": amounts.get("hype_ideal", amounts.get("hype", 0)),
            "tao": amounts.get("tao_ideal", amounts.get("tao", 0)),
        },
        "executable_allocations_cents": {
            "btc": amounts.get("btc", 0),
            "hype": amounts.get("hype", 0),
            "tao": amounts.get("tao", 0),
        },
    }


class JarvisV230CryptoLanePublicSignalSelectionGateTests(unittest.TestCase):
    def test_selects_highest_executable_data_ready_platform_ready_crypto_without_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = build_crypto_lane_public_signal_selection_gate_result(
                current_date="2026-06-17",
                public_signal_result=_public_signal_result(root),
                allocation_result=_allocation_result(btc=4154, hype=2000, tao=3000),
                constitution=_constitution(),
                portfolio_state=_portfolio_state(),
            )

            self.assertEqual(result.status, STATUS_READY)
            self.assertEqual(result.selected_crypto_candidate, "btc")
            self.assertEqual(result.selected_crypto_amount_eur, 41.54)
            self.assertFalse(result.recommendation_quality_current_data)
            self.assertFalse(result.allocation_mutation)
            self.assertFalse(result.approval_ticket_mutation)
            self.assertFalse(result.buy_request_created)
            self.assertTrue(result.broker_connection_forbidden)
            self.assertTrue(result.credentials_forbidden)
            self.assertTrue(result.private_account_data_ingestion_forbidden)
            self.assertTrue(result.order_creation_forbidden)
            self.assertTrue(result.no_trades_executed)

    def test_tao_data_ready_but_platform_blocked_when_kraken_not_ready(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = build_crypto_lane_public_signal_selection_gate_result(
                current_date="2026-06-17",
                public_signal_result=_public_signal_result(root),
                allocation_result=_allocation_result(tao=5000),
                constitution=_constitution(),
                portfolio_state=_portfolio_state(),
            )

            tao = next(item for item in result.candidate_decisions if item.candidate_id == "tao")
            self.assertEqual(tao.decision_status, DECISION_BLOCKED_BY_PLATFORM)
            self.assertFalse(tao.platform_ready)
            self.assertEqual(result.status, STATUS_REVIEW_REQUIRED)

    def test_blocks_candidate_when_public_signal_quality_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_raw(root, "coingecko_btc_simple_price_eur", "bitcoin", price=56000.0)
            public_signal_result = build_multi_crypto_public_data_quality_pipeline_result(root=root, current_date="2026-06-17")
            result = build_crypto_lane_public_signal_selection_gate_result(
                current_date="2026-06-17",
                public_signal_result=public_signal_result,
                allocation_result=_allocation_result(hype=5000),
                constitution=_constitution(),
                portfolio_state=_portfolio_state(),
            )

            hype = next(item for item in result.candidate_decisions if item.candidate_id == "hype")
            self.assertEqual(hype.decision_status, DECISION_BLOCKED_BY_SOURCE_QUALITY)
            self.assertFalse(hype.source_quality_ready)
            self.assertEqual(result.status, STATUS_REVIEW_REQUIRED)

    def test_console_output_surfaces_selected_crypto_and_safety(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = build_crypto_lane_public_signal_selection_gate_result(
                current_date="2026-06-17",
                public_signal_result=_public_signal_result(root),
                allocation_result=_allocation_result(btc=4154),
                constitution=_constitution(),
                portfolio_state=_portfolio_state(),
            )
            output = format_crypto_lane_public_signal_selection_gate(result)

            self.assertIn("Crypto-Lane Public Signal Selection Gate", output)
            self.assertIn("selected crypto candidate: btc", output)
            self.assertIn("no broker connection", output)
            self.assertIn("no trades executed", output)
            btc = next(item for item in result.candidate_decisions if item.candidate_id == "btc")
            self.assertEqual(btc.decision_status, DECISION_SELECTED)


if __name__ == "__main__":
    unittest.main()