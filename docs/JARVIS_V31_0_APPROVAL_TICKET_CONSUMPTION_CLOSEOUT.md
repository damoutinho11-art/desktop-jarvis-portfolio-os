# J.A.R.V.I.S. v31.0 Approval Ticket Consumption Closeout

## Purpose

v31 turns the refreshed approval ticket into the daily manual action brief.

v30 writes the approval-ticket artifact. v31 consumes that artifact read-only and prints the clean daily operator output the user needs before manual action.

## What changes

- Adds `jarvis_v31_0_approval_ticket_consumption_closeout.py`.
- Updates root `jarvis_operator.py` to v31.
- Reads `outputs/approval_ticket_latest.json`.
- Compares the saved ticket against the current v30 preview.
- Blocks ambiguous nested `source_bridge_result` payloads.
- Blocks any ticket that contains execution flags.
- Displays a clean manual action brief:
  - crypto lane candidate and amount
  - stock/fund/ETF lane candidate and amount
  - approval status
  - stale-data review requirement
  - no-execution safety

## Safety

v31 does not:

- refresh or write the approval ticket
- mutate allocation
- mutate portfolio state
- create buy requests
- connect to brokers
- request credentials
- ingest private brokerage/account data
- place orders
- execute trades

The final real-world buy remains manual outside J.A.R.V.I.S.