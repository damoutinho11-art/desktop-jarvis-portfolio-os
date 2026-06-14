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
