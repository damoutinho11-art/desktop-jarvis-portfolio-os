# J.A.R.V.I.S. v36.0 Autonomous Daily Refresh Action Brief

## Purpose

v36 makes the daily operator refresh the stock/fund/ETF real-instrument data before showing the manual action brief.

It connects the safe chain:

1. v34 resolves the selected ETF sleeve into a real ETF/fund instrument.
2. v34 fetches fresh public quote data for that real instrument.
3. v35 bridges the selected real instrument into `outputs/approval_ticket_latest.json`.
4. v36 prints a clean manual action brief.

## Meaning of autonomous

Autonomous means the daily command refreshes public data and the local approval ticket when it runs.

It does not mean:

- background execution
- broker connectivity
- credentials
- private account ingestion
- orders
- trades
- real-world buying

The final real-world buy remains manual outside J.A.R.V.I.S.

## Default daily behavior

```powershell
python .\jarvis_operator.py --daily
```

By default, v36:

- writes/refreshes local selected instrument resolution under `jarvis/local/`
- writes/refreshes the approval ticket with the fresh selected real ETF/fund instrument
- prints the clean manual action brief

Use these flags for read-only review mode:

```powershell
python .\jarvis_operator.py --daily --no-write-local-resolution --no-write-ticket
```

## Safety

v36 does not:

- change allocation logic
- create buy requests
- connect to brokers
- request credentials
- ingest private brokerage/account data
- place orders
- execute trades