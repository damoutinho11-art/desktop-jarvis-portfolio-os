# J.A.R.V.I.S. v33.0 Stock/Fund/ETF Public Source Fetcher

## Purpose

v33 adds the first strict public data intake bridge for the stock/fund/ETF lane.

The ETF candidates currently exist as abstract sleeves such as `quality_etf`, `growth_nasdaq_etf`, and `global_core_etf`. v33 does not invent real tickers for those sleeves. It requires a local public source manifest under `jarvis/local/` and fetches current public quote data only when a real provider/symbol is configured.

## Supported providers

- `yahoo_chart`
- `stooq_csv`

Both are public quote-data routes and require no broker/private account connection. They are used only for read-only source freshness.

## Local manifest

Default path:

```text
jarvis/local/stock_fund_etf_public_sources.local.json
```

This file is local/operator-managed and should not be committed.

Example shape:

```json
{
  "version": 1,
  "sources": {
    "quality_etf": {
      "provider": "yahoo_chart",
      "symbol": "REAL_SYMBOL_HERE",
      "currency": "EUR"
    }
  }
}
```

v33 can generate a local template with:

```powershell
python .\jarvis_operator.py --daily --current-date 2026-06-17 --write-local-manifest-template
```

The template does not count as data. Candidates remain `REVIEW_REQUIRED_SAFE` until real provider/symbol entries fetch fresh public data.

## Safety

v33 does not:

- invent ETF tickers
- use static market data
- promote stale fixtures
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