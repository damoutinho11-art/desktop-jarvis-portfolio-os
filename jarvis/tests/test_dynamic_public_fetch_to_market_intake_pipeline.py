import json
import tempfile
import unittest
from pathlib import Path
from typing import Any

from jarvis.dynamic_market_data_intake_validator import STATUS_READY as INTAKE_READY
from jarvis.dynamic_market_data_intake_validator import validate_dynamic_market_data_intake
from jarvis.dynamic_market_raw_cache_normalizer import (
    STATUS_READY as NORMALIZER_READY,
    normalize_dynamic_market_raw_cache,
)
from jarvis.dynamic_public_data_fetcher_adapter import build_dynamic_public_data_fetcher_adapter
from jarvis.jarvis_public_data_fetcher import AUTHORIZATION_PHRASE, fetch_public_sources


REGISTRY = "jarvis/data/dynamic_approved_universe.example.json"
BINDINGS = "jarvis/data/dynamic_market_source_bindings.example.json"
ENDPOINTS = "jarvis/data/dynamic_public_data_fetcher_endpoints.example.json"


def _prices(start: float) -> list[dict[str, Any]]:
    return [
        {"date": f"2026-{month:02d}-01", "close": start + month}
        for month in range(1, 13)
    ]


def _csv_payload(start: float) -> bytes:
    lines = ["date,close"]
    for row in _prices(start):
        lines.append(f"{row['date']},{row['close']}")
    return ("\n".join(lines) + "\n").encode("utf-8")


def _json_payload(start: float) -> bytes:
    return json.dumps({"prices": _prices(start)}).encode("utf-8")


class DynamicPublicFetchToMarketIntakePipelineTests(unittest.TestCase):
    def test_fake_authorized_fetch_normalizes_and_passes_intake(self) -> None:
        adapter = build_dynamic_public_data_fetcher_adapter(REGISTRY, BINDINGS, ENDPOINTS)
        self.assertEqual(adapter.status, "DYNAMIC_PUBLIC_DATA_FETCHER_ADAPTER_READY_SAFE")

        config = dict(adapter.public_fetcher_config)
        config["dry_run_only"] = False
        config["execute_fetch"] = True
        config["write_local_cache"] = True
        config["authorization_phrase"] = AUTHORIZATION_PHRASE
        config["fetch_date"] = "2026-06-15"
        config["output_directory"] = "jarvis/local/test_dynamic_public_fetch"

        url_payloads: dict[str, bytes] = {}
        for index, source in enumerate(config["sources"]):
            expected = str(source.get("expected_content_type", "")).lower()
            source_url = str(source["source_url"])
            start = 100.0 + (index * 10.0)

            if "json" in expected:
                url_payloads[source_url] = _json_payload(start)
            else:
                url_payloads[source_url] = _csv_payload(start)

        def fake_fetch(url: str) -> bytes:
            return url_payloads[url]

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fetch_result = fetch_public_sources(config, None, root=root, fetch_func=fake_fetch)

            self.assertEqual(
                fetch_result.overall_status,
                "PUBLIC_DATA_FETCHER_FETCH_COMPLETED_LOCAL_CACHE_ONLY_SAFE",
            )
            self.assertEqual(len(fetch_result.fetched_files), 6)
            self.assertTrue(all(Path(path).exists() for path in fetch_result.fetched_files))
            self.assertTrue(
                all(
                    str(Path(path)).endswith((".csv.raw", ".json.raw"))
                    for path in fetch_result.fetched_files
                )
            )

            normalizer = normalize_dynamic_market_raw_cache(
                REGISTRY,
                BINDINGS,
                ENDPOINTS,
                tuple(fetch_result.fetched_files),
            )

            self.assertEqual(normalizer.status, NORMALIZER_READY)
            self.assertEqual(normalizer.normalized_series_count, 6)
            self.assertEqual(normalizer.normalized_market_data["base_currency"], "EUR")

            normalized_path = root / "jarvis" / "local" / "test_dynamic_market_data.normalized.json"
            normalized_path.parent.mkdir(parents=True, exist_ok=True)
            normalized_path.write_text(
                json.dumps(normalizer.normalized_market_data, indent=2),
                encoding="utf-8",
            )

            intake = validate_dynamic_market_data_intake(REGISTRY, BINDINGS, normalized_path)

            self.assertEqual(intake.status, INTAKE_READY)
            self.assertEqual(intake.ready_series_count, 6)
            self.assertFalse(intake.blockers)
            self.assertTrue(normalizer.fetching_forbidden)
            self.assertTrue(normalizer.raw_data_unverified)
            self.assertTrue(normalizer.manual_approval_required)
            self.assertTrue(normalizer.execution_forbidden)
            self.assertFalse(normalizer.to_dict()["creates_buy_request"])
            self.assertTrue(normalizer.to_dict()["no_trades_executed"])


if __name__ == "__main__":
    unittest.main()
