# J.A.R.V.I.S. v53.0 Portfolio Exposure + Dynamic Emergency Fund Audit

## Purpose

v53 reads the local brokerless manual snapshot and answers whether the emergency fund is good using monthly expenses, not an arbitrary fixed EUR number.

J.A.R.V.I.S. should not say "â‚¬5,000 is enough" unless that is supported by Diogo's actual monthly expenses.

## Command without expenses

```powershell
python .\jarvis_operator.py --portfolio-exposure-audit --current-date 2026-06-17 --monthly-contribution-eur 400
```

Expected behavior:

```text
EXPENSES_REQUIRED_FOR_DYNAMIC_EMERGENCY_POLICY
```

## Command with expenses

```powershell
python .\jarvis_operator.py --portfolio-exposure-audit --current-date 2026-06-17 --monthly-contribution-eur 400 --monthly-expenses-eur 1000 --minimum-emergency-months 3 --ideal-emergency-months 6
```

Policy:

- below 3 months: prioritize emergency fund first
- 3 to 6 months: use a capped maintenance top-up for the emergency fund and invest most of the contribution
- above 6 months: no extra emergency top-up required by expense policy

## Safety

v53 does not:

- mutate allocation
- approve buys
- create buy requests
- connect to brokers
- request credentials
- ingest private broker data automatically
- create orders
- execute trades