# J.A.R.V.I.S. v32.0 Stock/Fund/ETF Data Freshness Engine

## Purpose

v32 is the first stock/fund/ETF data-quality layer after the expanded crypto lane was connected through the daily approval-ticket brief.

The previous daily operator warning said that the ETF universe had no `as_of` or `updated_at` metadata and was treated as manually maintained local scores. v32 turns that warning into a structured dated-metadata freshness/source-quality gate.

## What changes

- Adds `jarvis_v32_0_stock_fund_etf_data_freshness_engine.py`.
- Updates root `jarvis_operator.py` to v32.
- Reads the refreshed approval ticket.
- Extracts stock/fund/ETF candidate records from the ticket.
- Checks dated source metadata fields such as `as_of`, `updated_at`, `data_as_of`, `source_as_of`, `factsheet_as_of`, and `price_as_of`.
- Marks candidates as fresh, stale, missing, or invalid.
- Preserves the v31 daily manual action brief and no-execution safety checks.

## Safety

v32 does not:

- fetch network data
- refresh or write approval tickets
- mutate allocation
- mutate portfolio state
- create buy requests
- connect to brokers
- request credentials
- ingest private brokerage/account data
- place orders
- execute trades

The final real-world buy remains manual outside J.A.R.V.I.S.
## v32.1 manual-action formatter test-double compatibility hotfix

v32.1 keeps the real v31 daily manual-action formatter for real v31 results, but adds a lightweight fallback formatter for unit-test doubles. This preserves production output while allowing v32 freshness tests to validate ETF metadata and safety text without requiring a full v31 result object.
