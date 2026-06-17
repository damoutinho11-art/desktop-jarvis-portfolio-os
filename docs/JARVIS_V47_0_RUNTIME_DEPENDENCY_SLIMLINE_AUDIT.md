# J.A.R.V.I.S. v47.0 Runtime Dependency Slimline Audit

## Purpose

v47 is an audit-only cleanup stage.

It scans the active Python import dependency closure starting from:

```text
jarvis_operator.py
```

The goal is to identify:

- active modules still imported by the current runtime
- active `jarvis_v*.py` stage modules
- legacy `jarvis_v*.py` candidate modules not in the active runtime closure
- missing imports
- parse failures

## What v47 does not do

v47 does not:

- delete files
- archive files
- change runtime behavior
- change investing logic
- change selected assets
- connect to brokers
- create buy requests
- create orders
- execute trades

## Command

```powershell
python -m jarvis.jarvis_v47_0_runtime_dependency_slimline_audit --current-date 2026-06-17
```

Optional report:

```powershell
python -m jarvis.jarvis_v47_0_runtime_dependency_slimline_audit --current-date 2026-06-17 --write-report
```

Generated report path:

```text
outputs/runtime_dependency_slimline_audit_latest.json
```

Do not commit generated audit reports unless a future fixture stage explicitly promotes one.

## Next stage

The next cleanup stage should use this audit to build a no-behavior-change runtime slimline package.

Do not bulk-delete older stage files until the active dependency closure has been collapsed and validated.