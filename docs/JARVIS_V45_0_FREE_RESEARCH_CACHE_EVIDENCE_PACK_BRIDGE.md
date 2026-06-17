# J.A.R.V.I.S. v45.0 Free Research Cache Evidence Pack Bridge

## Purpose

v45 consumes the v44 local free-research cache and turns it into a compact evidence pack.

This is the bridge from raw free-source cache records to usable evidence for later scoring and source-confidence gates.

## Default daily mode

```powershell
python .\jarvis_operator.py --daily --current-date 2026-06-17
```

Default daily mode does not write the evidence pack.

## Write evidence pack from existing cache

```powershell
python .\jarvis_operator.py --daily --current-date 2026-06-17 --write-evidence-pack
```

This reads:

```text
jarvis/local/free_research_api_cache.local.json
```

and writes:

```text
outputs/free_research_evidence_pack_latest.json
```

## Refresh cache and write evidence pack

```powershell
python .\jarvis_operator.py --daily --current-date 2026-06-17 --refresh-free-research-cache --write-evidence-pack
```

## Safety

v45 does not:

- approve buys
- mutate allocation
- create buy requests
- connect to a broker
- request credentials
- ingest private account data
- create orders
- execute trades

Evidence-pack writes are explicit and restricted to `outputs`.
Cache reads/writes are restricted to `jarvis/local`.