# J.A.R.V.I.S. v38.0 Individual Stock Public Universe Engine

## Purpose

v38 starts the individual-stock lane safely.

It keeps the v37 crypto + ETF/fund daily refresh intact, then checks a local individual-stock public universe.

A stock is considered data-ready only if it has:

- real stock id
- real ticker/symbol
- supported public provider
- fresh public quote
- no stale or failed source status

## Local files

Universe template:

```text
jarvis/local/individual_stock_public_universe.local.json
```

Signals output:

```text
jarvis/local/individual_stock_public_signals.local.json
```

Both files are local/operator-managed and should not be committed.

## Commands

Create a local stock universe template:

```powershell
python .\jarvis_operator.py --daily --current-date 2026-06-17 --write-stock-template
```

Refresh local stock public signals:

```powershell
python .\jarvis_operator.py --daily --current-date 2026-06-17 --write-stock-signals
```

## Safety

v38 does not:

- promote a stock pick
- mutate allocation
- write an approval ticket for stocks
- create a buy request
- connect to brokers
- request credentials
- ingest private brokerage/account data
- place orders
- execute trades

The final real-world buy remains manual outside J.A.R.V.I.S.