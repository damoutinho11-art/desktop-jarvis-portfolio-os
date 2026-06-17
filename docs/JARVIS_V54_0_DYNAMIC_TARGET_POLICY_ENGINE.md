# J.A.R.V.I.S. v54.0 Dynamic Target Policy Engine

## Verdict

v54.0 adds the dynamic target policy layer.

This stage is policy-only. It does not allocate automatically, approve purchases,
create buy requests, connect to brokers, create orders, or trade.

## Why this exists

v53 made the emergency fund policy dynamic and expense-based. v54 turns that
state into a target policy so the weekly router can later become portfolio-aware
instead of relying only on the simple v50 40/60 route.

## Current Diogo policy baseline

- Emergency fund basis: monthly expenses, not fixed EUR.
- Comfortable monthly expenses: approximately 1200 EUR.
- Minimum emergency target: 3 months.
- Ideal emergency target: 6 months.
- Monthly contribution plan: 500 EUR.
- Maintenance emergency top-up after minimum target: 75 EUR.
- Investable monthly amount after emergency top-up: 425 EUR.

## Target bands

- Cash reserve: measured in months of expenses, not investment percentage.
- Stock/fund/ETF core: 80% to 90% of invested assets.
- Crypto satellite: 5% to 10% of invested assets, contribution-capped because of volatility.
- Individual stocks: review-only until stock-specific public evidence exists.

## Safety

- No allocation mutation.
- No approval-ticket mutation.
- No buy request.
- No broker API.
- No credentials.
- No private account ingestion.
- No orders.
- No trades.