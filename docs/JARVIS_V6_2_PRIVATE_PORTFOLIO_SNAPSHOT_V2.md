# J.A.R.V.I.S. v6.2 Private Portfolio Snapshot v2

## Verdict

v6.2 defines the private portfolio snapshot contract required before J.A.R.V.I.S. can size weekly/day-by-day manual buy recommendations.

This is not a buy planner.

This is not an API connection.

This is not broker integration.

## What v6.2 Adds

v6.2 defines:

- account roles;
- cash buckets;
- protected emergency cash;
- pending bills cash;
- weekly contribution cash;
- extra investable cash;
- holdings;
- asset class;
- sleeve routing;
- platform routing;
- snapshot freshness;
- operator confirmation;
- local-only private data boundary.

## Account Roles

Required account roles:

- daily_bank;
- emergency_fund;
- investment_brokerage;
- crypto_exchange;
- cash_buffer.

## Cash Rules

Cash must be separated into:

- protected cash;
- pending bills cash;
- weekly contribution cash;
- extra investable cash.

Protected cash must never be marked investable.

Emergency cash is not investment cash.

## Snapshot Freshness

A private snapshot must declare:

- as_of_date;
- snapshot_age_hours;
- max_allowed_snapshot_age_hours.

A stale snapshot blocks recommendations.

## Holdings

Each holding must include:

- asset id;
- display name;
- asset class;
- sleeve id;
- account id;
- platform;
- currency;
- quantity;
- market value in EUR;
- manually entered/local source flag;
- freshness flag.

## What v6.2 Does Not Do

v6.2 does not:

- choose assets;
- generate buy tickets;
- approve policies;
- mutate active policy;
- connect to brokers;
- fetch private data automatically;
- execute trades.

## Next Stage

The next non-redundant stage is:

v6.3_universal_asset_candidate_registry

Reason:

J.A.R.V.I.S. now has policy intelligence and a private snapshot contract. Next it needs a broad but quality-gated investable universe before exact asset selection or manual buy tickets.

## Safety

local_private_data_only = true
operator_confirmation_required = true
automatic_import_forbidden_at_this_stage = true
broker_api_forbidden = true
broker_execution_forbidden = true
active_policy_mutated = false
creates_buy_request = false
no_trades_executed = true
