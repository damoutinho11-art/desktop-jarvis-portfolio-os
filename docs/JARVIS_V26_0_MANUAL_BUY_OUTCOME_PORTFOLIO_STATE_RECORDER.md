# J.A.R.V.I.S. v26.0 Manual Buy Outcome Portfolio-State Recorder

## Purpose

v26 fills the missing local-state step after Diogo performs a real-world buy manually outside J.A.R.V.I.S.

It records an explicit manual-buy confirmation against the current approval ticket, updates local `portfolio_state.json`, and appends an audit record to `outputs/manual_buy_confirmations.jsonl`.

## Scope

Included:

- explicit confirmation phrase
- approval-ticket asset and amount match check
- local `portfolio_state.json` update
- local JSONL confirmation audit
- no-execution safety flags

Excluded:

- buy request creation
- broker connection
- credentials
- private brokerage/account ingestion
- order placement
- trade execution
- automatic selling

## Product rule

J.A.R.V.I.S. may update local state only after Diogo confirms a completed real-world manual buy. It must not assume the buy happened from an approval ticket alone.

## v26.1 idempotency hotfix

A manual buy confirmation must be recorded at most once for the same approval ticket, asset, lane, amount, and execution date. This prevents accidental double-counting if the recorder command is pasted or run twice.

The duplicate guard checks `outputs/manual_buy_confirmations.jsonl` before writing local portfolio state. It does not connect to brokers, does not create orders, and does not execute trades.

