# J.A.R.V.I.S. Dynamic Portfolio Preflight Runbook

Main command:
python -m jarvis.dynamic_portfolio_preflight_report

READY statuses:
DYNAMIC_PORTFOLIO_PREFLIGHT_READY_SAFE
DYNAMIC_BOUND_MARKET_COVERAGE_READY_SAFE
DYNAMIC_MARKET_SOURCE_BINDING_READY_SAFE
DYNAMIC_MARKET_COVERAGE_READY_SAFE
DYNAMIC_WEEKLY_PLAN_READY_SAFE
DYNAMIC_POLICY_READY_SAFE
manual approval required: True
execution forbidden: True

Blocked status:
DYNAMIC_PORTFOLIO_PREFLIGHT_BLOCKED_SAFE

Safety boundary:
No execution
J.A.R.V.I.S. must not execute.
J.A.R.V.I.S. must not:
fetch market data
connect to a broker
place orders
create buy requests
approve assets
mutate the registry
execute trades

## Dynamic Public Market Data Ingestion Path

This section documents the accepted dynamic public market-data path as of the final operator acceptance run.

Purpose:

- connect the approved dynamic portfolio universe to public market data
- keep public data raw and unverified until reviewed
- normalize local raw cache files into the existing market-data shape
- feed the existing market-data intake validator, coverage checks, optimizer, weekly plan, dashboard, and command-center audit
- never create trust, approval, buy requests, broker actions, execution, or trades

Accepted sequence:

1. Dynamic approved universe
2. Dynamic market source bindings
3. Dynamic market import plan
4. Dynamic public data fetcher adapter
5. Existing public data fetcher local raw cache path
6. Dynamic market raw cache normalizer
7. Dynamic market data intake validator
8. Dynamic bound market coverage
9. Dynamic market coverage audit
10. Dynamic allocation optimizer
11. Dynamic weekly draft plan
12. Dynamic portfolio preflight
13. Dynamic operator dashboard
14. Dynamic command-center audit

Operator commands:

- python -m jarvis.dynamic_market_source_binding_report
- python -m jarvis.dynamic_market_import_plan_report
- python -m jarvis.dynamic_public_data_fetcher_adapter_report
- python -m jarvis.dynamic_market_raw_cache_normalizer_report
- python -m jarvis.dynamic_market_data_intake_validator_report
- python -m jarvis.dynamic_bound_market_coverage_report
- python -m jarvis.dynamic_market_coverage_audit_report
- python -m jarvis.dynamic_allocation_optimizer_report
- python -m jarvis.dynamic_allocation_weekly_plan_report
- python -m jarvis.dynamic_portfolio_preflight_report
- python -m jarvis.dynamic_operator_status_dashboard_report
- python -m jarvis.dynamic_command_center_audit_report

Current readiness interpretation:

- required command count: 11
- ready status count: 10
- raw cache normalizer is expected to be blocked until real local raw cache files exist
- dashboard and command-center audit remain ready when fixture-backed market data is present

Public data safety:

- adapter defaults to dry-run only
- adapter does not fetch, download, scrape, call APIs, or write cache files
- real public fetching must go through the existing public data fetcher
- real public fetching requires the exact authorization phrase
- raw files must remain local-cache-only
- raw data remains unverified
- normalized market data is not approval
- manual approval remains required
- no registry mutation is performed
- no buy request is created
- no broker integration is used
- no execution or trades occur

Acceptance proof:

The integration test `test_dynamic_public_fetch_to_market_intake_pipeline.py` proves the technical path with a fake fetch function only:

- existing public fetcher
- typed `.csv.raw` / `.json.raw` local cache files
- dynamic market raw cache normalizer
- normalized market-data JSON
- dynamic market data intake validator READY

The test does not call the internet and does not write production market data.

Final accepted safety invariant:

Automated research and data processing are allowed. Manual trust and manual approval remain required. Broker integration, buy requests, approvals, execution, and trades are forbidden.
