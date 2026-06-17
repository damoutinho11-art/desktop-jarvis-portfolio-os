# J.A.R.V.I.S. v27.0 Expanded Crypto Universe Data Engine

## Purpose

v27 focuses the project back on finishing crypto before ETF/UI/voice work.

It expands the crypto lane beyond BTC/HYPE/TAO by creating a public-source universe manifest and a data-backed scoring layer that reuses the existing v10 local-cache fetch boundary and v22 public-data quality pipeline.

## Candidate universe

Initial expanded universe:

- BTC
- ETH
- SOL
- LINK
- AVAX
- NEAR
- INJ
- RENDER
- HYPE
- TAO

## Scope

Included:

- expanded crypto candidate universe
- public CoinGecko simple-price source manifest
- local manifest writer under `jarvis/local`
- reuse of v22 source-quality normalization
- market-cap, volume, 24h-change, and platform-readiness scoring

Excluded:

- broker connection
- credentials
- private account data ingestion
- buy request creation
- order placement
- trade execution
- ETF/fund/stock work
- chat/voice interface work

## Safety

v27 only prepares public data sources and scores local public signals. It does not make an allocation mutation, approval-ticket mutation, buy request, order, or trade.
## v27.1 local manifest path-safety hotfix

v27.1 fixes local manifest path validation so absolute temporary test paths are accepted when they are still inside a `jarvis/local` directory segment. Production behavior remains limited to local-cache manifest writes and does not permit broker/order/trade actions.
## v27.2 crypto data coverage gate and missing-source retry manifest

v27.2 prevents the expanded crypto engine from reporting full readiness when any public-data source is missing. Partial coverage now returns review-required status and can write a missing-source manifest to `jarvis/local/public_data_sources.missing.local.json`.

This allows the operator to retry only missing public crypto sources after a provider rate limit or partial fetch failure, while preserving the no-broker, no-order, no-trade boundary.

## v27.2b crypto coverage visibility hotfix

v27.2b exposes `full_public_data_coverage` in the engine result, JSON output, and console report so partial public-data coverage cannot look complete during operator review.

