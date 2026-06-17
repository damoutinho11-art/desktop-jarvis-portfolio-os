# J.A.R.V.I.S. Repository Hygiene Plan

## Why this exists

The repository has accumulated staged development residue. That is expected because each safety layer was built and tested separately.

The cleanup rule is:

```text
Clean safely first. Collapse dependencies second. Delete legacy code last.
```

## What v46 cleans now

v46 is a hygiene-only stage.

It:

- updates README to match the current v45 reality
- adds this hygiene plan
- adds the active system map
- ignores generated cache/evidence/patch files
- removes stale root portfolio backup JSON files

It does not change runtime behavior.

## Files removed by v46

Root backup files:

```text
portfolio_state_backup_20260604_025103.json
portfolio_state_backup_20260604_025111.json
portfolio_state_backup_20260604_193940.json
portfolio_state_backup_20260604_193940_1.json
```

These were stale local backups, not active portfolio state.

## Files explicitly ignored

```text
apply_v*.ps1
outputs/free_research_evidence_pack_latest.json
outputs/free_research_evidence_pack_*.json
jarvis/local/free_research_api_cache.local.json
jarvis/local/free_research_api_cache.*.json
```

## What not to delete yet

Do not bulk-delete older `jarvis_v*.py` modules yet.

Reason: the current active operator still imports through older safety, lane, and output modules. A safe dependency collapse must happen before removal.

## Next cleanup stage

The next cleanup stage should be:

```text
Runtime Dependency Slimline
```

Goal:

- create a compact active runtime package
- migrate active functions out of long stage chains
- preserve behavior with tests
- then archive/delete legacy modules safely