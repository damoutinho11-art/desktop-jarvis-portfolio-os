# J.A.R.V.I.S. v28.0 Expanded Crypto Ranking Daily Operator Bridge

## Purpose

v28 connects the completed v27 expanded crypto universe data engine to the active root daily operator.

Before v28, the root operator still pointed to the v24 bridge, which used the older v23 BTC/HYPE/TAO-era crypto-lane selection gate. v28 makes the daily operator consume the v27 10-asset ranked crypto universe while preserving allocation/risk/budget and platform gates.

## What changes

- Adds `jarvis_v28_0_expanded_crypto_ranking_daily_operator_bridge.py`.
- Updates `jarvis_operator.py` to point to v28.
- Keeps v24 and v23 available for history/tests.
- Uses v27 ranking output as the crypto data/ranking source.
- Selects the first ranked crypto candidate that also has executable allocation after risk/budget checks.
- Shows candidates blocked by allocation, source quality, platform route, or ranking engine status.
- Preserves stale-data review warnings from the real daily readiness gate.

## Safety

v28 does not:

- create buy requests
- connect to a broker
- request credentials
- ingest private brokerage/account data
- place orders
- execute trades
- mutate allocation
- mutate approval tickets

The final real-world buy remains manual outside J.A.R.V.I.S.
## v28.1 console formatter test-double compatibility hotfix

v28.1 keeps the real v27 formatter for real expanded-crypto ranking results, but adds a lightweight fallback formatter for unit-test doubles. This preserves production output while allowing bridge tests to validate console safety text without requiring a full v27 result object.
