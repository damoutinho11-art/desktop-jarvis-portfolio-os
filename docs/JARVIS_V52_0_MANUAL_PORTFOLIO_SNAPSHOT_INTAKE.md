# J.A.R.V.I.S. v52.0 Manual Portfolio Snapshot Intake

## Purpose

v52 makes the missing manual portfolio data from v51 actionable.

It creates and validates a local brokerless snapshot file:

```text
jarvis/local/manual_portfolio_snapshot.local.json
```

This file is ignored by git and must not be committed.

## Template command

```powershell
python .\jarvis_operator.py --write-manual-portfolio-snapshot-template --current-date 2026-06-17
```

## Audit command

```powershell
python .\jarvis_operator.py --manual-portfolio-snapshot-intake --current-date 2026-06-17
```

## Snapshot policy

The snapshot is:

- local JSON only
- manually filled by Diogo
- brokerless
- credential-free
- ignored by git
- used only to improve allocation-audit data coverage

It must not contain:

- passwords
- API keys
- broker tokens
- secrets
- access tokens
- private keys

## Safety

v52 does not:

- connect to brokers
- request credentials
- ingest private broker data automatically
- mutate allocation
- approve buys
- create buy requests
- create orders
- execute trades

## Next stage

After Diogo fills a real snapshot and sets:

```json
"is_template": false
```

the allocation audit can recognize holdings, cash, cost basis, and brokerless manual snapshot policy as covered.
## Template snapshots do not count as coverage

A generated template is only a starting point. The allocation strategy audit must not count it as real holdings, cash, cost-basis, or brokerless snapshot coverage until Diogo fills real values and sets:

```json
"is_template": false
```