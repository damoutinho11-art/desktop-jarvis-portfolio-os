from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from jarvis.runtime import operator as runtime_operator
from jarvis.runtime.manual_holdings_update import (
    DEFAULT_MANUAL_HOLDINGS_PATH,
    MANUAL_SOURCE,
    REQUIRED_POSITION_FIELDS,
    STATUS_BLOCKED,
    STATUS_READY,
    STATUS_REVIEW_REQUIRED,
    build_manual_holdings_template,
    build_manual_holdings_update_result,
    format_manual_holdings_update,
    write_manual_holdings_template,
)


def _write(path: Path, payload: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def _confirmed_holdings_payload() -> dict:
    return {
        "schema": "JARVIS_MANUAL_HOLDINGS_V1",
        "as_of": "2026-06-20",
        "is_template": False,
        "manual_only": True,
        "source": MANUAL_SOURCE,
        "holdings_confirmed": True,
        "currency": "EUR",
        "positions": [
            {
                "symbol": "BTC",
                "name": "Bitcoin",
                "lane": "crypto",
                "quantity": 0.01,
                "average_price_eur": 60000.0,
                "cost_basis_eur": 600.0,
                "market_value_eur": 650.0,
                "platform": "Kraken",
                "purchase_date": "2026-06-20",
                "notes": "manual buy outside Jarvis",
            },
            {
                "symbol": "MSFT",
                "name": "Microsoft",
                "lane": "individual_stock",
                "quantity": 1.0,
                "average_price_eur": 420.0,
                "cost_basis_eur": 420.0,
                "market_value_eur": 430.0,
                "platform": "Lightyear",
                "purchase_date": "2026-06-20",
                "notes": "",
            },
        ],
    }


class JarvisV131ManualHoldingsUpdateTests(unittest.TestCase):
    def test_template_contains_required_symbols_fields_and_manual_source(self) -> None:
        template = build_manual_holdings_template(current_date="2026-06-20")

        self.assertEqual(template["schema"], "JARVIS_MANUAL_HOLDINGS_V1")
        self.assertTrue(template["manual_only"])
        self.assertEqual(template["source"], MANUAL_SOURCE)
        self.assertTrue(template["is_template"])
        self.assertFalse(template["holdings_confirmed"])

        symbols = {item["symbol"] for item in template["positions"]}
        self.assertEqual(symbols, {"BTC", "ETH", "VWCE", "IS3Q.DE", "MSFT"})
        for item in template["positions"]:
            for field in REQUIRED_POSITION_FIELDS:
                self.assertIn(field, item)

    def test_missing_file_is_review_required_safe_not_crash(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "manual_holdings.local.json"

            result = build_manual_holdings_update_result(
                current_date="2026-06-20",
                holdings_path=path,
            )

            self.assertEqual(result.status, STATUS_REVIEW_REQUIRED)
            self.assertFalse(result.holdings_ready)
            self.assertFalse(result.file_exists)
            self.assertEqual(result.positions_count, 0)
            self.assertEqual(result.confirmed_positions_count, 0)
            self.assertEqual(result.total_cost_basis_eur, 0.0)
            self.assertIsNone(result.total_market_value_eur)
            self.assertEqual(result.blockers, [])
            self.assertIn("holdings not entered yet", " ".join(result.warnings))
            self.assertFalse(result.safety_flags["buy_request_created"])
            self.assertFalse(result.safety_flags["trade_executed"])

    def test_write_template_creates_blank_review_required_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "manual_holdings.local.json"

            result = build_manual_holdings_update_result(
                current_date="2026-06-20",
                holdings_path=path,
                write_template=True,
            )

            self.assertEqual(result.status, STATUS_REVIEW_REQUIRED)
            self.assertTrue(result.template_written)
            self.assertTrue(result.file_exists)
            self.assertTrue(result.is_template)
            self.assertFalse(result.holdings_ready)
            self.assertEqual(result.confirmed_positions_count, 0)
            payload = json.loads(path.read_text(encoding="utf-8"))
            self.assertTrue(payload["is_template"])
            self.assertFalse(payload["holdings_confirmed"])

    def test_confirmed_manual_holdings_are_ready_and_summarized(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = _write(Path(tmp) / "manual_holdings.local.json", _confirmed_holdings_payload())

            result = build_manual_holdings_update_result(
                current_date="2026-06-20",
                holdings_path=path,
            )

            self.assertEqual(result.status, STATUS_READY)
            self.assertTrue(result.holdings_ready)
            self.assertTrue(result.manual_only)
            self.assertEqual(result.source, MANUAL_SOURCE)
            self.assertEqual(result.positions_count, 2)
            self.assertEqual(result.confirmed_positions_count, 2)
            self.assertEqual(result.total_cost_basis_eur, 1020.0)
            self.assertEqual(result.total_market_value_eur, 1080.0)
            self.assertEqual(result.blockers, [])

    def test_manual_only_and_source_are_validated(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            payload = _confirmed_holdings_payload()
            payload["manual_only"] = False
            payload["source"] = "broker_import"
            path = _write(Path(tmp) / "manual_holdings.local.json", payload)

            result = build_manual_holdings_update_result(
                current_date="2026-06-20",
                holdings_path=path,
            )

            self.assertEqual(result.status, STATUS_BLOCKED)
            self.assertIn("manual_only_must_be_true", result.blockers)
            self.assertIn("source_must_be_diogo_manual_entry", result.blockers)
            self.assertFalse(result.safety_flags["order_created"])
            self.assertFalse(result.safety_flags["trade_executed"])

    def test_format_is_user_facing_and_safe(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = _write(Path(tmp) / "manual_holdings.local.json", _confirmed_holdings_payload())
            result = build_manual_holdings_update_result(current_date="2026-06-20", holdings_path=path)
            text = format_manual_holdings_update(result)

            self.assertIn("J.A.R.V.I.S. MANUAL HOLDINGS", text)
            self.assertIn("holdings ready: True", text)
            self.assertIn("confirmed positions: 2", text)
            self.assertIn("total cost basis EUR: 1020.00", text)
            self.assertIn("total market value EUR: 1080.00", text)
            self.assertIn("broker connection: False", text)
            self.assertIn("trade executed: False", text)
            self.assertIn("Diogo buys manually outside J.A.R.V.I.S.", text)

    def test_runtime_facade_routes_holdings_commands(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "manual_holdings.local.json"
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                code = runtime_operator.main(
                    [
                        "--write-holdings-template",
                        "--holdings-path",
                        str(path),
                        "--current-date",
                        "2026-06-20",
                    ]
                )

            self.assertEqual(code, 0)
            self.assertTrue(path.exists())
            self.assertIn("MANUAL HOLDINGS", output.getvalue())

    def test_runtime_surface_tracks_manual_holdings_module_and_gitignore_entry_exists(self) -> None:
        surface = runtime_operator.get_active_runtime_surface()
        self.assertEqual(surface["active_manual_holdings_update_module"], "jarvis.runtime.manual_holdings_update")
        self.assertEqual(DEFAULT_MANUAL_HOLDINGS_PATH, "jarvis/local/manual_holdings.local.json")

        gitignore = Path(".gitignore").read_text(encoding="utf-8")
        self.assertIn("jarvis/local/manual_holdings.local.json", gitignore)


if __name__ == "__main__":
    unittest.main()
