# J.A.R.V.I.S. v6 Personal Finance Command Center Audit

## Verdict

J.A.R.V.I.S. v5.11 is a strong safe-research and public-data foundation, but the true final product is now v6:

A personal finance command center that scans a broad investable universe, recommends aggressive-but-bounded portfolio policy candidates, monitors private portfolio state, prepares weekly/day-by-day manual buy actions, and explains risks with professional clarity.

J.A.R.V.I.S. remains manual-execution only.

## v6 Product Boundary

J.A.R.V.I.S. should be able to:

- scan ETFs, funds, stocks, crypto, cash-like options, and later bonds/commodities;
- evaluate source quality, freshness, liquidity, fees, risk, overlap, platform availability, and portfolio fit;
- recommend candidate portfolio policies with flexible bands instead of strict fixed allocations;
- allow weekly crypto buying when risk, cash, and portfolio-state rules permit it;
- prepare manual buy tickets;
- warn about drift, overexposure, stale data, source weakness, and news/risk context;
- support a professional dashboard and later a voice/conversational layer.

J.A.R.V.I.S. must never:

- change active policy automatically;
- approve assets automatically;
- create broker buy requests;
- execute trades;
- connect to broker execution paths;
- silently alter risk rules;
- recommend unverified assets as buy-ready.

## Existing Foundation

The current repo already contains:

- public source candidate matrix;
- source quality gate;
- transformer readiness audit;
- CoinGecko market-chart transformer;
- raw cache normalizer;
- market-data intake validator;
- dynamic coverage audit;
- dynamic allocation optimizer;
- weekly allocation draft plan;
- preflight;
- operator dashboard;
- command-center audit;
- manual approval and non-execution safety boundaries.

## Missing v6 Capabilities

1. Policy intelligence:
   - candidate policy generation;
   - policy scoring;
   - risk-band comparison;
   - manual policy-change ticket.

2. Universal asset candidate registry:
   - ETF, fund, stock, crypto, cash-like, bond, and commodity candidates;
   - eligibility states;
   - source/data quality requirements;
   - platform and currency fit.

3. Private portfolio snapshot v2:
   - account roles;
   - protected cash;
   - investable cash;
   - platform routing;
   - real local operator snapshot path.

4. Manual buy ticket planner:
   - asset;
   - amount;
   - platform;
   - reason;
   - counterargument;
   - risk warning;
   - manual approval status.

5. News/risk context:
   - credible source ranking;
   - risk tags;
   - portfolio impact;
   - daily/weekly brief.

6. Professional dashboard and voice:
   - visual portfolio command center;
   - chat/voice interface grounded in audited backend outputs.

## Recommended Next Stage

The next non-redundant stage is v6.1_policy_intelligence_boundary.

This stage should not build a dashboard, news engine, or universal scanner yet.

It should define how J.A.R.V.I.S. proposes aggressive-but-bounded candidate policies while preserving:

- manual policy approval;
- no automatic policy changes;
- no automatic asset approvals;
- no broker execution;
- no buy request creation;
- no trades.

## Safety

manual_policy_approval_required = true
manual_buy_execution_only = true
automatic_policy_change_forbidden = true
automatic_approval_forbidden = true
broker_execution_forbidden = true
creates_buy_request = false
no_trades_executed = true
