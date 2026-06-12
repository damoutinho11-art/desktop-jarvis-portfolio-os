# J.A.R.V.I.S. v4.61 Public Asset Universe Discovery Plan

v4.61 is a read-only plan/schema/report layer for the next J.A.R.V.I.S. direction:
public asset universe discovery as the primary research path.

This is a strategic pivot away from manual one-by-one candidate entry as the main
workflow. Manual watchlists remain useful for forced or user-specific research
ideas, but the main path should discover broad public universes for ETFs,
equities, funds/ETPs, crypto assets, and market reference data.

## Purpose

J.A.R.V.I.S. should eventually fetch all public research data it needs through
explicit, local-cache-controlled stages. The user should not manually enter every
ETF, stock, fund, or crypto asset.

The user's manual role remains:

- explicit human review and approval decisions
- final real-world purchase/action outside J.A.R.V.I.S.

This stage does not fetch or build the universe. It defines:

- target asset universes
- public source categories
- required universe fields
- future local cache layout
- freshness requirements
- classification plan
- research screening plan
- evidence readiness route
- future build sequence toward a local-first Research OS MVP

## External Manual Venues

Lightyear, LHV, and crypto platforms may be mentioned only as external manual
venues where the user may choose to act outside J.A.R.V.I.S. They are not
integrations. v4.61 does not log in to brokers, call broker APIs, store
credentials, or execute trades.

## Safety Boundaries

v4.61 does not:

- make network calls
- fetch, download, scrape, or call APIs
- write files or create cache directories
- create schedulers or subprocess execution paths
- ingest private/account data
- parse sources as evidence
- extract, verify, or promote evidence
- mutate candidate registries
- approve, trust, or mark assets investable
- recommend allocation or portfolio weights
- emit buy/sell signals
- execute trades or create an executor

## Future Build Sequence

The efficient next sequence is:

1. v4.62 Public Asset Universe Source Manifest Schema
2. v4.63 Public Asset Universe Fetch Dry-Run Planner
3. v4.64 Public Asset Universe Local Cache Builder
4. v4.65 Public Asset Universe Normalizer
5. v4.66 Public Asset Universe Classifier
6. v4.67 Research Priority Queue Dashboard
7. v4.68 Evidence Pack Generator Dry-Run
8. v5.0 Research OS MVP Audit

The v5.0 target is a local-first public research OS, not a trading bot.

## Run

```powershell
python -m jarvis.jarvis_public_asset_universe_discovery_plan_report
python -m jarvis.jarvis_public_asset_universe_discovery_plan_report --input jarvis\data\jarvis_public_asset_universe_discovery_plan.synthetic_complete.example.json
python -m unittest jarvis.tests.test_jarvis_public_asset_universe_discovery_plan jarvis.tests.test_jarvis_public_asset_universe_discovery_plan_report -v
```

The report is deterministic and read-only. It is not approval, trust,
investability, allocation advice, a buy/sell request, trade execution, evidence
verification, registry mutation, broker integration, or executor authorization.
