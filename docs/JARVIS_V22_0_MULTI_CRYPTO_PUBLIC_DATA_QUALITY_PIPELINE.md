# J.A.R.V.I.S. v22.0 Multi-Crypto Public Data Quality Pipeline

## Purpose

v22 generalizes the BTC-only public-data spine to the crypto-lane candidate set.

It reads raw public market data already fetched through the guarded v10 boundary, normalizes BTC/HYPE/TAO candidate signals, and applies a source-quality gate to each signal.

## Scope

Included:

- BTC raw CoinGecko price JSON
- HYPE raw CoinGecko price JSON
- TAO raw CoinGecko price JSON
- local normalized multi-crypto public signal files
- freshness checks
- price, market cap, volume, provider timestamp, and 24h-change sanity checks
- safety flags proving no allocation, ticket, broker, order, or trade mutation

Excluded:

- allocation scoring mutation
- approval ticket regeneration
- automatic buy requests
- broker connections
- credentials
- private account ingestion
- order placement
- trade execution

## Safety boundary

v22 remains local-cache-only and evidence-only. Even when all crypto public signals are quality-ready, recommendation_quality_current_data remains false until a later integration gate explicitly wires quality-gated signals into the crypto-lane scoring/risk layer.