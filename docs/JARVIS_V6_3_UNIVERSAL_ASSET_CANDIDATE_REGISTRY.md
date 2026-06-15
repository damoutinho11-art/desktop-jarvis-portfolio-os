# J.A.R.V.I.S. v6.3 Universal Asset Candidate Registry

## Verdict

v6.3 defines the broad investable candidate registry.

This is the stage where J.A.R.V.I.S. becomes able to represent a wide universe of possible assets without approving or recommending them yet.

## What v6.3 Adds

v6.3 defines candidate coverage for:

- ETFs;
- funds;
- stocks;
- crypto;
- cash-like assets;
- bond ETFs;
- commodity ETFs.

## Candidate States

Supported states:

- DISCOVERED;
- IDENTITY_READY;
- DATA_READY;
- QUALITY_READY;
- POLICY_CANDIDATE;
- APPROVED_POLICY_ASSET;
- WEEKLY_BUY_CANDIDATE;
- BLOCKED;
- AVOID.

In v6.3, candidates must not be promoted to APPROVED_POLICY_ASSET or WEEKLY_BUY_CANDIDATE.

## Why This Stage Exists

v6.1 defined policy intelligence.

v6.2 defined private portfolio state.

v6.3 defines the broad candidate universe J.A.R.V.I.S. may evaluate later.

The system still cannot say what to buy yet because exact asset scoring is deferred to v6.4.

## Registry Rules

Each candidate must include:

- candidate id;
- display name;
- asset type;
- candidate state;
- sleeve routing;
- currency;
- region or network;
- platform options;
- data requirements;
- eligibility checks;
- approval flags;
- execution safety flags.

## Safety

v6.3 is candidate-only.

It does not:

- score exact assets;
- approve assets;
- create policy assets;
- create weekly buy candidates;
- create buy requests;
- mutate policy;
- connect to brokers;
- execute trades.

## Next Stage

The next non-redundant stage is:

v6.4_asset_quality_scoring_gate

Reason:

The registry now exists. Next J.A.R.V.I.S. needs scoring rules for cost, liquidity, diversification, overlap, volatility, drawdown, data quality, platform fit, and crypto risk before it can produce policy-ready assets.
