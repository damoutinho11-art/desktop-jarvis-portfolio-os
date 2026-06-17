# J.A.R.V.I.S. Portfolio OS

J.A.R.V.I.S. Portfolio OS is a local, safety-first portfolio research and manual-buy preparation system.

The current active operator is the v45 free-research cache evidence-pack bridge. It supports a daily read-only check-in flow and a weekly manual-buy preparation flow. It can refresh public/free research data into a local cache and write an evidence pack when explicitly requested.

## Current operating model

J.A.R.V.I.S. is not an auto-trader.

It can:

- prepare research data
- refresh public/free source cache records
- build evidence packs
- select or display candidates across crypto, ETF/fund, and individual-stock lanes
- prepare manual review tickets and weekly manual-buy packets in later stages
- summarize risk/source status

It cannot and must not:

- connect to brokers
- request or store broker credentials
- ingest private account data automatically
- create buy requests
- create orders
- execute trades
- approve a real-world purchase automatically

The final real-world buy remains manual outside J.A.R.V.I.S.

## Daily mode

Daily mode is for read-only check-ins, source quality, drift/risk review, and finance analysis.

```powershell
python .\jarvis_operator.py --daily --current-date 2026-06-17
```

Default daily mode should not mutate the approval ticket, portfolio state, evidence pack, or local cache.

## Weekly buy-prep mode

Weekly mode is for manual buy preparation. It may refresh/write the manual review ticket, but still cannot create a buy request, broker order, or trade.

```powershell
python .\jarvis_operator.py --weekly-buy-prep --current-date 2026-06-17
```

## Explicit free research cache refresh

Public/free research data refresh is explicit.

```powershell
python .\jarvis_operator.py --daily --current-date 2026-06-17 --refresh-free-research-cache
```

The local cache path is:

```text
jarvis/local/free_research_api_cache.local.json
```

Do not commit generated local cache files.

## Explicit evidence-pack write

Evidence-pack writing is explicit.

```powershell
python .\jarvis_operator.py --daily --current-date 2026-06-17 --refresh-free-research-cache --write-evidence-pack
```

The generated evidence-pack path is:

```text
outputs/free_research_evidence_pack_latest.json
```

Do not commit generated evidence-pack files unless a future stage deliberately promotes a fixture.

## Optional public research APIs

The system is free-first and no-key-first where possible.

Supported/declared public research sources include:

- CoinGecko free/demo for crypto
- ECB official FX reference
- Yahoo chart public fallback for public quotes
- SEC EDGAR official validation when explicitly requested
- FMP optional research API when `JARVIS_FMP_API_KEY` exists

Optional public research keys are allowed only for research. Broker/API execution keys remain outside scope.

## Current active lanes

Current active lane output comes through the v45 operator chain:

- Crypto lane
- ETF/fund lane
- Individual stock review lane
- Free-source router
- Free-source cache
- Evidence-pack bridge

See:

```text
docs/JARVIS_ACTIVE_SYSTEM_MAP.md
docs/JARVIS_REPOSITORY_HYGIENE_PLAN.md
```

## Safety check

```powershell
python .\jarvis_operator.py --safety-check
```

Expected behavior: execution commands are blocked.

## Tests

Run focused current checks:

```powershell
python -m unittest jarvis.tests.test_jarvis_v45_0_free_research_cache_evidence_pack_bridge jarvis.tests.test_jarvis_operator_v45_0_root_bridge jarvis.tests.test_jarvis_v46_0_repository_hygiene_active_surface_map -v
```

Older stage tests remain in the repository for historical coverage while the runtime dependency chain is being slimmed. Do not delete older `jarvis_v*.py` files blindly; the current operator still imports through earlier safety/source modules.