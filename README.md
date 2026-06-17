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
## Stable runtime facade

The root operator now points to the stable runtime facade:

```text
jarvis_operator.py -> jarvis.runtime.operator
```

The facade currently delegates to the validated v45 evidence-pack backend. This keeps future cleanup from forcing the root shortcut to chase every staged `jarvis_v*.py` file.
## Weekly manual buy packet

Weekly buy-prep mode now produces a user-facing manual packet:

```powershell
python .\jarvis_operator.py --weekly-buy-prep --current-date 2026-06-17 --refresh-free-research-cache --write-evidence-pack
```

The packet summarizes the crypto action, ETF/fund action, individual-stock review, evidence, risk notes, and safety state. It remains manual-only: no broker, no buy request, no order, and no trade.
## Manual weekly amount router

Weekly buy-prep mode accepts a budget and proposes manual review amounts:

```powershell
python .\jarvis_operator.py --weekly-buy-prep --current-date 2026-06-17 --weekly-budget-eur 100 --refresh-free-research-cache --write-evidence-pack
```

The router is evidence-aware and manual-only. It does not mutate allocation, approve buys, create buy requests, connect to brokers, create orders, or execute trades.
## Allocation strategy data coverage audit

J.A.R.V.I.S. can audit whether the current data is enough for weekly routing or full allocation:

```powershell
python .\jarvis_operator.py --allocation-strategy-audit --current-date 2026-06-17 --refresh-free-research-cache --write-evidence-pack
```

The current implemented strategy is a weekly manual amount router. Full portfolio allocation remains blocked until required manual portfolio data and risk-policy coverage are complete.
## Manual portfolio snapshot intake

J.A.R.V.I.S. can create a local brokerless snapshot template:

```powershell
python .\jarvis_operator.py --write-manual-portfolio-snapshot-template --current-date 2026-06-17
```

Then audit it:

```powershell
python .\jarvis_operator.py --manual-portfolio-snapshot-intake --current-date 2026-06-17
```

The snapshot is local-only, ignored by git, and must not contain credentials, broker tokens, or API keys.
## Dynamic emergency fund audit

J.A.R.V.I.S. can audit the local manual snapshot and a planned monthly contribution using monthly expenses rather than a fixed arbitrary emergency fund target:

```powershell
python .\jarvis_operator.py --portfolio-exposure-audit --current-date 2026-06-17 --monthly-contribution-eur 400 --monthly-expenses-eur 1000 --minimum-emergency-months 3 --ideal-emergency-months 6
```

Without monthly expenses, J.A.R.V.I.S. refuses to decide how much should go to emergency fund versus investing. Once minimum emergency coverage is met, J.A.R.V.I.S. uses a small capped maintenance top-up rather than overfunding cash.

- v54.0 Dynamic Target Policy Engine: converts the real manual snapshot, expense-based emergency policy, and monthly contribution into a dynamic target policy layer. It remains manual-review-only and does not execute trades.
