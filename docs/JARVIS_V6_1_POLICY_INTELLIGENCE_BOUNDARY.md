# J.A.R.V.I.S. v6.1 Policy Intelligence Boundary

## Verdict

v6.1 defines the policy intelligence boundary.

J.A.R.V.I.S. may recommend aggressive-but-bounded candidate portfolio policies, but it must not silently activate them.

Diogo must manually approve any policy change.

## What v6.1 Adds

v6.1 defines:

- candidate policies;
- flexible allocation bands;
- equity core and equity satellite sleeves;
- broad ETF/fund/stock evaluation scope;
- BTC and speculative crypto sleeves;
- bounded weekly crypto buying permission;
- policy score breakdowns;
- manual policy-change tickets;
- non-execution safety flags.

## Design Rule

J.A.R.V.I.S. does not use strict allocations.

It uses:

- minimum weight;
- preferred lower band;
- preferred upper band;
- maximum weight;
- weekly buy permission;
- risk notes.

## ETF Rule

The global ETF is the core anchor, not the whole ETF universe.

J.A.R.V.I.S. should also be able to evaluate:

- developed world ETFs;
- S&P 500 ETFs;
- Europe ETFs;
- emerging markets ETFs;
- quality factor ETFs;
- momentum factor ETFs;
- growth ETFs;
- small-cap ETFs;
- sector ETFs;
- single-stock candidates.

Exact asset selection comes later in the universal asset registry and quality-scoring stages.

## Crypto Rule

Weekly crypto buying remains possible when:

- crypto is inside the allowed risk band;
- cash rules allow investing;
- emergency cash is protected;
- portfolio state does not block risk-taking;
- manual approval is preserved.

J.A.R.V.I.S. must not automatically forbid crypto buying just because a fixed target is reached.

J.A.R.V.I.S. must reduce or block crypto buying near upper risk bands.

## Recommended Candidate

The default candidate for manual review is:

balanced_aggressive_flexible_bands

It is not automatically active.

It requires a manual policy-change review ticket.

## Next Stage

The next non-redundant stage is:

v6.2_private_portfolio_snapshot_v2

Reason:

Policy intelligence is now bounded. The next requirement is accurate private portfolio state:

- account roles;
- protected cash;
- investable cash;
- platform routing;
- holdings;
- contribution cash;
- snapshot freshness.

## Safety

active_policy_mutated = false
automatic_policy_change_forbidden = true
automatic_approval_forbidden = true
manual_policy_approval_required = true
broker_execution_forbidden = true
creates_buy_request = false
no_trades_executed = true
