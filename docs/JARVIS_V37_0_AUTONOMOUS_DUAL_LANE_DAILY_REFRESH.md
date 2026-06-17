# J.A.R.V.I.S. v37.0 Autonomous Dual-Lane Daily Refresh

## Purpose

v37 makes the daily command refresh both active recommendation lanes before printing the manual action brief.

It runs:

1. Crypto public-data/ranking/approval-ticket refresh.
2. Stock/Fund/ETF sleeve-to-real-instrument refresh.
3. Clean combined manual action brief.

## Current active lanes

- Crypto lane: expanded crypto universe, source-quality gate, ranking, allocation eligibility, approval ticket refresh.
- ETF/Fund lane: sleeve-to-real-instrument resolver, fresh public quote fetch, selected real ETF instrument ticket bridge.

## Meaning of autonomous

Autonomous means this happens when the daily command runs:

```powershell
python .\jarvis_operator.py --daily
```

It does not mean background trading or execution.

## Safety

v37 does not:

- connect to brokers
- request credentials
- ingest private brokerage/account data
- create buy requests
- place orders
- execute trades

The final real-world buy remains manual outside J.A.R.V.I.S.

## Next stage

After v37, the next frontier is individual stocks:

```text
individual_stock_public_universe_and_ranker
```