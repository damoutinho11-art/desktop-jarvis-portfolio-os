# J.A.R.V.I.S. v29.0 Expanded Crypto Allocation Eligibility Bridge

## Purpose

v29 connects the completed v27/v28 expanded crypto ranking to the crypto-lane allocation decision.

v28 proved that the daily operator can read the 10-asset crypto ranking, but it also showed that the old allocation basis still assigns the executable crypto-lane amount to BTC. v29 separates the weekly crypto-lane budget amount from the old asset-specific allocation basis, then proposes the best eligible ranked crypto asset for the same manual-buy amount.

## What changes

- Adds `jarvis_v29_0_expanded_crypto_allocation_eligibility_bridge.py`.
- Updates the root `jarvis_operator.py` to v29.
- Keeps v28 as the upstream daily/ranking bridge.
- Uses the v28 executable crypto-lane amount as the weekly crypto budget.
- Reassigns that amount to the highest-ranked eligible v27 candidate when source-quality, ranking, and platform gates pass.
- Surfaces whether the candidate changed from the allocation basis.
- Requires approval-ticket refresh when the candidate changes.

## Why this is safe

v29 is still read-only/product-layer logic. It does not:

- mutate allocation
- mutate approval tickets
- mutate portfolio state
- create buy requests
- connect to brokers
- request credentials
- ingest private brokerage/account data
- place orders
- execute trades

The final real-world buy remains manual outside J.A.R.V.I.S.
## v29.1 upstream formatter test-double compatibility hotfix

v29.1 keeps the real v28 daily-operator formatter for real upstream v28 results, but adds a lightweight fallback formatter for unit-test doubles. This preserves production output while allowing v29 bridge tests to validate reassignment and safety text without requiring a full v28 result object.
