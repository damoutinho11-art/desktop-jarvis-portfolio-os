# J.A.R.V.I.S. v6.4 Asset Quality Scoring Gate

## Verdict

v6.4 defines the asset quality scoring gate.

It scores candidate assets for readiness before they can enter later policy generation.

This stage does not approve assets, create buy tickets, or execute trades.

## What v6.4 Scores

v6.4 scores candidates across:

- identity confidence;
- data freshness;
- cost and fees;
- liquidity;
- diversification;
- overlap risk;
- volatility and drawdown risk;
- platform fit;
- currency fit;
- fundamental quality for stocks;
- custody/liquidity risk for crypto;
- yield and safety terms for cash-like assets;
- duration risk for bond ETFs;
- role clarity for commodities.

## Output States

Quality statuses:

- QUALITY_READY;
- QUALITY_WATCHLIST;
- QUALITY_NEEDS_MORE_DATA;
- QUALITY_BLOCKED;
- QUALITY_AVOID.

## Safety

v6.4 does not:

- approve assets;
- mutate policy;
- generate weekly buy candidates;
- create buy requests;
- connect to brokers;
- execute trades.

## Next Stage

The next non-redundant stage is:

v6.5_policy_candidate_generator

Reason:

J.A.R.V.I.S. now has policy boundaries, private snapshot boundaries, candidate registry, and quality scoring. The next step is to combine policy intelligence with quality-ready assets into candidate policy portfolios for manual review.
