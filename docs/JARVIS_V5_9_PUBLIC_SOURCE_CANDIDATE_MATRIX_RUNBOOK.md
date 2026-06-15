# J.A.R.V.I.S. v5.9 Public Source Candidate Matrix Runbook

## Purpose

v5.9 records candidate public market-data sources for future operator review.

This stage does not create an active endpoint pack. It does not fetch, call APIs, connect to brokers, create buy requests, approve assets, mutate the active registry, or execute trades.

## Why this is a candidate matrix, not an endpoint pack

The current raw-cache normalizer accepts CSV/JSON rows that can be normalized into `date` and `close` values. Some candidate sources may require transformation before they can safely enter that normalizer.

Therefore, v5.9 separates:

- candidate source discovery
- parser compatibility
- manual symbol or coin-ID verification
- cross-check requirement
- future promotion to a local endpoint pack

## Candidate source roles

ETF price candidates:

- Stooq public CSV candidates
- manual symbol verification required
- cross-check required before promotion

Crypto price candidates:

- CoinGecko coin-ID candidates
- transformer required before raw-cache normalization
- exchange/public cross-check required before promotion

FX reference support:

- ECB Data Portal API candidate
- support source only
- not an approved asset endpoint

## Safety invariant

Automated research and local data processing are allowed only after explicit local authorization.

Manual trust and manual approval remain required.

No broker integration, no buy request, no approval grant, no execution, and no trades.
