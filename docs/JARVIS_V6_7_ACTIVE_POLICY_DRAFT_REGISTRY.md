# J.A.R.V.I.S. v6.7 Active Policy Draft Registry

## Verdict

v6.7 creates active-policy draft records from manually accepted v6.6 review decisions.

A draft is not an active policy.

A draft is not an approval.

A draft is not a buy ticket.

## What v6.7 Does

v6.7:

- reads v6.6 manual review decisions;
- creates a draft only from ACCEPT_FOR_ACTIVE_POLICY_REVIEW;
- preserves allocation bands;
- preserves selected quality-ready/watchlist assets;
- adds risk constraints;
- adds activation requirements;
- requires later manual approval.

## What v6.7 Does Not Do

v6.7 does not:

- approve the policy;
- activate the policy;
- approve assets;
- create weekly buy tickets;
- create buy requests;
- connect to brokers;
- execute trades.

## Next Stage

The next non-redundant stage is:

v6.8_active_policy_manual_approval_gate

Reason:

The accepted policy now exists as a draft. It still needs an explicit manual approval gate before it can become the active policy used by future weekly planning.
