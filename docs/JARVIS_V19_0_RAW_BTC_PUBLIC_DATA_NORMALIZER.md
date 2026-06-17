# J.A.R.V.I.S. v19.0 Raw BTC Public Data Normalizer

## Verdict

v19.0 converts the first real fetched BTC public data file into a normalized local BTC market signal while preserving the no-execution boundary.

## Product role

This stage is the second step in the real public-data pipeline:

1. v18 fetches raw public BTC data safely into ignored local cache.
2. v19 parses and validates the raw BTC JSON into a normalized public signal.
3. A later stage will quality-gate the signal before it can affect scoring or recommendations.

## What v19 does

- Finds the latest raw CoinGecko BTC EUR JSON file under `jarvis/local/public_data/v10_raw`.
- Parses `price_eur`, `market_cap_eur`, `volume_24h_eur`, `change_24h_pct`, and provider timestamp.
- Produces a normalized BTC candidate signal.
- Optionally writes the normalized signal only under ignored `jarvis/local` cache.
- Keeps `recommendation_quality_current_data` false.

## What v19 does not do

- It does not update allocation scores.
- It does not mutate `portfolio_state.json`.
- It does not regenerate approval tickets.
- It does not create buy requests.
- It does not connect to brokers.
- It does not create orders or execute trades.

## Safety boundary

- No broker connection.
- No credentials.
- No private account ingestion.
- No buy request.
- No orders.
- No trades.
- Final real-world buy remains manual outside J.A.R.V.I.S.
