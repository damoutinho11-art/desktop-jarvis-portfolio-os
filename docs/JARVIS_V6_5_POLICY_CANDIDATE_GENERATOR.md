# J.A.R.V.I.S. v6.5 Policy Candidate Generator

## Verdict

v6.5 generates manual-review portfolio policy candidates.

It combines:

- private portfolio snapshot boundaries;
- protected cash vs investable cash;
- quality-ready and watchlist assets;
- flexible allocation bands;
- crypto ceilings;
- defensive cash/bond floors.

## What v6.5 Produces

v6.5 produces policy candidates such as:

- balanced aggressive manual-review policy;
- ETF-heavy policy with bounded crypto allowance;
- core ETF + BTC accumulation policy;
- defensive cash/bond-aware policy.

## What v6.5 Does Not Do

v6.5 does not:

- approve a policy;
- activate a policy;
- approve any asset;
- create weekly buy tickets;
- create buy requests;
- connect to brokers;
- execute trades.

## Safety

All policies are manual-review candidates only.

Speculative crypto candidates such as HYPE and TAO remain excluded until quality improves.

Weekly crypto buying remains possible only in later stages, bounded by policy, private snapshot state, risk rules, and manual approval.

## Next Stage

The next non-redundant stage is:

v6.6_manual_policy_review_queue

Reason:

Policy candidates now exist, but they still require explicit manual accept/defer/reject/needs-correction review before any active policy or weekly buy planning can be derived.
