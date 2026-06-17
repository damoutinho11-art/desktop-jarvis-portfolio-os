# J.A.R.V.I.S. v30.0 Expanded Crypto Approval Ticket Refresh

## Purpose

v30 refreshes the local manual-approval ticket from the v29 expanded crypto allocation eligibility bridge.

v25 built approval tickets from the old v24/v23 crypto selector. v30 builds the ticket from the expanded crypto path so the crypto lane can show the best eligible v27-ranked asset.

## What changes

- Adds `jarvis_v30_0_expanded_crypto_approval_ticket_refresh.py`.
- Updates root `jarvis_operator.py` to v30.
- Reads v29 expanded crypto allocation eligibility.
- Builds a refreshed local approval ticket with the selected expanded crypto candidate.
- Preserves stock/fund/ETF lane from the allocation engine.
- Keeps `as_of` on the allocation-basis date and uses `generated_at` for the ticket generation date.
- Writes only under `outputs/` and only when `--write-ticket` is explicitly passed.

## Safety

v30 does not:

- mutate allocation
- mutate portfolio state
- create buy requests
- connect to brokers
- request credentials
- ingest private brokerage/account data
- place orders
- execute trades

When `--write-ticket` is used, v30 only writes the local manual-approval ticket artifact. The final real-world buy remains manual outside J.A.R.V.I.S.
## v30.1 approval ticket nested selection cleanup

v30.1 removes the full nested v29 source bridge payload from the approval ticket and replaces it with a compact `source_bridge_summary`. This avoids ambiguous nested `selected_crypto_candidate` fields from older upstream bridge layers while preserving the allocation-basis candidate and expanded-crypto selected candidate for audit.
