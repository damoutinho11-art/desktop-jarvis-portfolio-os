# J.A.R.V.I.S. v24.0 Crypto-Lane Selection Daily Operator Bridge

## Purpose

v24 replaces the BTC-only v21 daily crypto evidence bridge with the v23 crypto-lane public signal selection gate.

The active root daily command now surfaces:

- selected crypto candidate
- selected crypto amount
- BTC/HYPE/TAO selection gate result
- stale portfolio/approval-ticket warnings
- no-execution safety boundary

## Scope

Included:

- active root `jarvis_operator.py` wiring to v24
- daily operator output with v23 crypto-lane selection
- safety-check and voice/demo command preservation
- focused tests proving no scoring/ticket/order mutation

Excluded:

- allocation score mutation
- approval ticket mutation
- buy request creation
- broker connection
- credentials
- private account ingestion
- order placement
- trade execution

## Why this matters

v21 still showed BTC-only evidence. v24 makes the active daily product consume the multi-crypto selection gate, so the public-data pipeline is no longer detached from the main operator command.