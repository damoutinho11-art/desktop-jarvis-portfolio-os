# J.A.R.V.I.S. v5.11 CoinGecko Raw Fixture Transformer Runbook

## Purpose

v5.11 adds a local-only transformer for CoinGecko-style `market_chart` JSON fixtures.

CoinGecko raw payloads use pair rows:

```json
{"prices": [[timestamp_ms, price], ...]}
```

The existing dynamic market raw cache normalizer expects object rows:

```json
{"prices": [{"date": "YYYY-MM-DD", "close": price}]}
```

This stage bridges that shape mismatch only. It does not change the normalizer, source template, command center, dashboard, registry, optimizer, or endpoint promotion flow.

## What It Does

- Reads one explicit local JSON file.
- Validates the payload is a JSON object.
- Validates `prices` is a non-empty list.
- Validates each row is exactly `[timestamp_ms, price]`.
- Converts timestamps to UTC dates.
- Sorts rows by date.
- Deduplicates same UTC dates deterministically by keeping the last valid value.
- Blocks safely if fewer than 12 normalized price rows remain.
- Optionally writes the normalized payload only when an explicit `output_path` is provided.

## What It Does Not Do

- No fetching.
- No API calls.
- No credentials.
- No broker integration.
- No endpoint promotion.
- No evidence verification.
- No asset approval.
- No buy request.
- No execution.
- No trades.
- No registry mutation.
- No optimizer wiring.
- No dashboard wiring.

## CLI

```powershell
python -m jarvis.dynamic_coingecko_market_chart_transformer_report path\to\coingecko_market_chart.json
```

Optional local output:

```powershell
python -m jarvis.dynamic_coingecko_market_chart_transformer_report path\to\coingecko_market_chart.json --output-path path\to\normalizer_ready.json
```

The CLI never fetches. The optional output is only a local transformed fixture.

## Python API

```python
from jarvis.dynamic_coingecko_market_chart_transformer import (
    transform_coingecko_market_chart_file,
    transform_coingecko_market_chart_payload,
)

result = transform_coingecko_market_chart_payload({"prices": [[1764547200000, 100.0]]})
```

Result status values:

- `DYNAMIC_COINGECKO_MARKET_CHART_TRANSFORMER_READY_SAFE`
- `DYNAMIC_COINGECKO_MARKET_CHART_TRANSFORMER_BLOCKED_SAFE`

## Verification

```powershell
python -m py_compile .\jarvis\dynamic_coingecko_market_chart_transformer.py .\jarvis\dynamic_coingecko_market_chart_transformer_report.py .\jarvis\tests\test_dynamic_coingecko_market_chart_transformer.py .\jarvis\tests\test_dynamic_coingecko_market_chart_transformer_report.py
python -m unittest jarvis.tests.test_dynamic_coingecko_market_chart_transformer jarvis.tests.test_dynamic_coingecko_market_chart_transformer_report -v
python -m unittest discover -v
```

## Safety Boundary

This transformer handles local raw fixture shape only. It is not source truth verification, not endpoint promotion, not approval, not recommendation, not allocation, and not execution.
