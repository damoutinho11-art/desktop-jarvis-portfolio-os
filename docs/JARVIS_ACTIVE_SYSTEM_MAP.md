# J.A.R.V.I.S. Active System Map

## Purpose

This file separates the current active runtime surface from legacy stage residue.

The repository has many historical `jarvis_v*.py` files because the system was built as a safety-first staged chain. That history is useful, but the active operator should now be understood through the current root path.

## Current root

```text
jarvis_operator.py
```

Current root target:

```text
jarvis.runtime.operator
```

## Current active command modes

```powershell
python .\jarvis_operator.py --daily --current-date 2026-06-17
python .\jarvis_operator.py --weekly-buy-prep --current-date 2026-06-17
python .\jarvis_operator.py --daily --current-date 2026-06-17 --refresh-free-research-cache
python .\jarvis_operator.py --daily --current-date 2026-06-17 --refresh-free-research-cache --write-evidence-pack
python .\jarvis_operator.py --safety-check
```

## Active late-stage modules

These modules define the current active product surface:

```text
jarvis/jarvis_v43_0_free_research_api_router_weekly_policy.py
jarvis/jarvis_v44_0_free_research_api_fetcher_adapters_local_cache.py
jarvis/jarvis_v45_0_free_research_cache_evidence_pack_bridge.py
```

## Active lane modules

The current late-stage operator still depends on earlier lane modules:

```text
jarvis/jarvis_v42_0_three_lane_daily_action_brief.py
jarvis/jarvis_v41_0_ranked_individual_stock_candidate_ticket_bridge.py
jarvis/jarvis_v40_0_individual_stock_public_universe_bootstrap.py
jarvis/jarvis_v39_0_individual_stock_public_ranker.py
jarvis/jarvis_v38_0_individual_stock_public_universe_engine.py
jarvis/jarvis_v37_0_autonomous_dual_lane_daily_refresh.py
```

## Active safety modules

The current operator still uses earlier safety/voice modules:

```text
jarvis/jarvis_v16_0_real_daily_readiness_gate.py
jarvis/jarvis_v12_1_local_voice_io_shell.py
```

## Active generated files

Generated runtime files must not be committed:

```text
jarvis/local/free_research_api_cache.local.json
outputs/free_research_evidence_pack_latest.json
apply_v*.ps1
```

## Legacy residue

The repo still contains many older stage modules, reports, and docs. They should not be deleted blindly until the runtime dependency chain is collapsed into a smaller stable package.

Recommended future cleanup:

```text
v47 Runtime Dependency Slimline
v48 Legacy Stage Archive/Delete Plan
v49 README/runbook final consolidation
```

## Do not change in hygiene stages

Repository hygiene stages must not:

- change buy logic
- change scoring logic
- change selected assets
- change approval-ticket semantics
- create broker paths
- create execution paths
## Stable runtime facade

As of v48, the root shortcut points to:

```text
jarvis.runtime.operator
```

The facade currently delegates to the validated v45 backend:

```text
jarvis.jarvis_v45_0_free_research_cache_evidence_pack_bridge
```

This is a no-behavior-change cleanup step. Future slimline stages should migrate active behavior behind the stable facade before deleting legacy stage modules.
## Weekly manual buy packet

As of v49, weekly buy-prep mode is user-facing:

```text
python .\jarvis_operator.py --weekly-buy-prep --current-date 2026-06-17 --refresh-free-research-cache --write-evidence-pack
```

The stable runtime facade routes weekly mode to:

```text
jarvis.runtime.weekly_packet
```

Daily mode still delegates to the validated v45 evidence-pack backend.