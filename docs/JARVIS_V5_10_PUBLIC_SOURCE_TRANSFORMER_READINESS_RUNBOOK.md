# J.A.R.V.I.S. v5.10 Public Source Transformer Readiness Runbook

## Purpose

v5.10 classifies v5.9 public source candidates by transformer readiness.

It does not fetch data, call APIs, connect to brokers, promote endpoint packs, approve assets, create buy requests, mutate registries, or execute trades.

## Classifications

- `NORMALIZER_READY_AFTER_MANUAL_VERIFICATION`
  - Candidate source can potentially be used by the current raw-cache normalizer after manual symbol/source verification.
  - Example: CSV rows that provide `date` and `close` fields.

- `TRANSFORMER_REQUIRED_BEFORE_ENDPOINT_PROMOTION`
  - Candidate source is useful but not directly compatible with the current raw-cache normalizer.
  - Example: CoinGecko market-chart style crypto data requiring timestamp/price pair conversion.

- `SUPPORT_ONLY_TRANSFORMER_REQUIRED`
  - Candidate is a support/reference source, not an approved asset endpoint.
  - Example: FX reference data.

## Operator rule

A source candidate cannot become an endpoint pack until:

1. manual source URL verification is complete,
2. manual symbol or coin-ID verification is complete,
3. parser compatibility is known,
4. required transformer exists if needed,
5. cross-check requirements are satisfied,
6. the operator explicitly promotes a local endpoint file.

## Safety invariant

Automated research/data processing is allowed only after explicit local authorization.

Manual trust and manual approval remain required.

No broker integration, no buy request, no approval grant, no endpoint promotion, no execution, and no trades.
