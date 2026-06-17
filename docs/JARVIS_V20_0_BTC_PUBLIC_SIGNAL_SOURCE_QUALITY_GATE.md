# J.A.R.V.I.S. v20.0 BTC Public Signal Source-Quality Gate

## Verdict

v20.0 quality-gates the normalized BTC public signal produced by v19 while preserving the no-execution boundary.

## Product role

This stage is the third step in the real public-data pipeline:

1. v18 fetches raw public BTC data safely into ignored local cache.
2. v19 normalizes the raw BTC JSON into a BTC public signal.
3. v20 checks whether that normalized signal is fresh, structurally complete, and sane enough for a later scoring integration stage.

## What v20 does

- Finds the latest normalized CoinGecko BTC EUR signal under `jarvis/local/public_data/v19_normalized`.
- Checks candidate/source identity.
- Checks `as_of` freshness.
- Checks BTC price, market cap, volume, 24h change, and provider timestamp sanity.
- Returns a source-quality-ready status when the local signal passes the gate.

## What v20 does not do

- It does not update allocation scores.
- It does not mutate `portfolio_state.json`.
- It does not regenerate approval tickets.
- It does not create buy requests.
- It does not connect to brokers.
- It does not create orders or execute trades.
- It does not claim full recommendation quality is current data yet.

## Safety boundary

- No broker connection.
- No credentials.
- No private account ingestion.
- No buy request.
- No orders.
- No trades.
- Final real-world buy remains manual outside J.A.R.V.I.S.