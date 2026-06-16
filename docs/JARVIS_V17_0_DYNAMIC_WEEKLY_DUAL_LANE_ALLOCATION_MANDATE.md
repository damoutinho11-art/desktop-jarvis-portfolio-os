# J.A.R.V.I.S. v17.0 Dynamic Weekly Dual-Lane Allocation Mandate

## Verdict

v17.0 changes the active product contract from a single best allocation to a weekly dual-lane mandate:

1. one crypto manual buy recommendation;
2. one stock/fund/ETF manual buy recommendation.

Both lanes remain dynamic, risk-managed, and manual-only. J.A.R.V.I.S. prepares the recommendations; Diogo performs any real-world buys outside the system.

## What changed

- The root allocation engine now tries to allocate the weekly budget across two lanes:
  - crypto lane: BTC/HYPE/TAO candidates, bounded by crypto risk rules and minimum efficient buys;
  - stock/fund/ETF lane: ETF sleeves ranked by the existing ETF scoring engine.
- The weekly approval ticket now includes `weekly_dual_lane_mandate`.
- The active daily readiness output now shows the dual-lane mandate before manual action.
- The current local data produces:
  - crypto lane: `btc EUR 41.54`;
  - stock/fund/ETF lane: `quality_etf EUR 62.31`.

These are current dynamic results, not static allocations.

## Dynamic behavior required

The engine must not hard-code BTC, quality ETF, or any fixed split. It must derive each lane from:

- weekly budget;
- current holdings and target gaps;
- ETF scoring inputs;
- crypto risk caps;
- minimum efficient buys;
- platform readiness;
- executable safety rules;
- freshness/readiness gate.

If one lane is blocked by risk, stale data, platform readiness, or insufficient minimum buy room, J.A.R.V.I.S. may defer that lane and explain why.

## Safety boundary

Unchanged:

- no broker connection;
- no credentials;
- no private brokerage/account ingestion;
- no buy requests;
- no orders;
- no trade execution;
- final real-world buy remains Diogo's manual action outside J.A.R.V.I.S.

