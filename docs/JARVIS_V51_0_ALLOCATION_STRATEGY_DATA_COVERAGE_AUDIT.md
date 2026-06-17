# J.A.R.V.I.S. v51.0 Allocation Strategy + Data Coverage Audit

## Purpose

v51 answers two questions explicitly:

1. What allocation strategy is implemented today?
2. Does J.A.R.V.I.S. have enough data for full portfolio allocation?

The answer is intentionally conservative:

```text
v50 implements a weekly manual amount router, not a full portfolio allocator.
```

## Command

```powershell
python .\jarvis_operator.py --allocation-strategy-audit --current-date 2026-06-17 --refresh-free-research-cache --write-evidence-pack
```

Optional report:

```powershell
python .\jarvis_operator.py --allocation-strategy-audit --current-date 2026-06-17 --write-output
```

Generated report:

```text
outputs/allocation_strategy_data_coverage_audit_latest.json
```

Do not commit generated reports unless a future fixture stage explicitly promotes one.

## Current implemented strategy

The implemented strategy is weekly contribution routing only:

- Diogo provides a weekly budget
- J.A.R.V.I.S. checks refreshed evidence readiness
- crypto can be proposed only when crypto evidence is usable
- crypto is capped at 40 percent
- ETF/fund gets the evidence-weighted remainder
- individual stock stays review-only at 0 EUR
- final buy remains manual outside J.A.R.V.I.S.

## Target strategy

A future full allocator should consider:

- source freshness
- source quality
- diversification benefit
- volatility/risk
- real holdings
- cash balance
- cost basis
- concentration risk
- correlation risk
- instrument fundamentals
- missing-data penalties

## Data coverage gate

Weekly routing can be allowed with public evidence.

Full allocation must stay blocked until required coverage is complete:

- manual holdings snapshot
- manual cash snapshot
- manual cost basis
- individual-stock evidence if stock allocation is considered
- correlation/risk model
- dynamic target policy

## Safety

v51 does not:

- mutate allocation
- approve buys
- create buy requests
- connect to brokers
- request credentials
- ingest private account data
- create orders
- execute trades

Next recommended stage:

```text
manual_portfolio_snapshot_intake
```
## Read-only audit behavior

The allocation strategy audit uses the read-only daily evidence context. It may refresh public cache/evidence when explicitly requested, but it must not report or perform approval-ticket mutation. Weekly ticket preparation remains owned by weekly buy-prep mode.