# J.A.R.V.I.S. v34.0 Stock/Fund/ETF Sleeve-to-Instrument Resolver

## Purpose

v34 fixes the ETF/fund abstraction problem.

`quality_etf`, `growth_nasdaq_etf`, and `global_core_etf` are strategy sleeves, not buyable instruments. v34 keeps those sleeves as the portfolio brain, but requires the selected sleeve to resolve into a real ETF/fund instrument before the ETF/fund lane can become actionable.

## What changes

- Adds `jarvis_v34_0_stock_fund_etf_sleeve_to_instrument_resolver.py`.
- Updates root `jarvis_operator.py` to v34.
- Reads the refreshed approval ticket to identify the selected ETF/fund sleeve.
- Reads a local sleeve-to-instrument universe under `jarvis/local/`.
- Requires real instrument metadata:
  - instrument id
  - name
  - ISIN
  - ticker
  - exchange
  - currency
  - public provider/symbol
  - optional factsheet URL
  - optional expense ratio
  - optional priority score
- Fetches fresh public quote data before selecting an instrument.
- Selects only real instruments with fresh public source data.
- Can write a local template and local resolution, both under `jarvis/local/`.

## Local instrument universe

Default path:

```text
jarvis/local/stock_fund_etf_instrument_universe.local.json
```

This file is operator-managed and should not be committed.

v34 can create a blank template:

```powershell
python .\jarvis_operator.py --daily --current-date 2026-06-17 --write-local-instrument-template
```

Blank entries never count as real data.

## Safety

v34 does not:

- invent instruments
- invent tickers
- use static market data
- select stale public-source instruments
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