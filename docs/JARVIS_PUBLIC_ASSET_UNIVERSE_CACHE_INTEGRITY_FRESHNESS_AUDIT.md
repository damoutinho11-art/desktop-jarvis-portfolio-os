# J.A.R.V.I.S. v4.65 Public Asset Universe Cache Integrity + Freshness Audit

v4.65 audits local public asset universe cache integrity and freshness after the v4.64 local cache builder.

This layer is read-only. It does not fetch, download, scrape, call APIs, write files, mutate cache, repair cache, normalize data, classify assets, screen investments, extract evidence, verify evidence, approve assets, recommend allocation, create buy/sell requests, trade, or create an executor.

The audit reads only explicit input JSON. In file-backed mode it reads only explicitly listed raw and metadata paths under the configured public cache root, normally `jarvis/local/public_asset_universe/`. It never scans local directories automatically.

## What It Checks

- missing raw cache files or inline raw content
- missing metadata sidecars or inline metadata
- raw SHA256 versus metadata `content_sha256`
- metadata `content_length` versus raw byte length
- metadata `source_id` consistency
- freshness by update frequency
- expected source coverage
- invalid cache paths
- unsafe metadata claims

Hash consistency is not evidence verification. Freshness is not approval. Cache presence is not trust, investability, allocation advice, a buy/sell signal, trade authorization, or executor authorization.

## Freshness Rules

- `daily`: fresh within 1 calendar day
- `weekly`: fresh within 7 calendar days
- `monthly`: fresh within 31 calendar days
- `manual`: not automatically stale; manual review required

## Commands

Default report:

```powershell
python -m jarvis.jarvis_public_asset_universe_cache_integrity_freshness_audit_report
```

Synthetic complete report:

```powershell
python -m jarvis.jarvis_public_asset_universe_cache_integrity_freshness_audit_report --input jarvis\data\jarvis_public_asset_universe_cache_integrity_freshness_audit.synthetic_complete.json
```

Synthetic problematic report:

```powershell
python -m jarvis.jarvis_public_asset_universe_cache_integrity_freshness_audit_report --input jarvis\data\jarvis_public_asset_universe_cache_integrity_freshness_audit.synthetic_problematic.json
```

Focused tests:

```powershell
python -m unittest jarvis.tests.test_jarvis_public_asset_universe_cache_integrity_freshness_audit jarvis.tests.test_jarvis_public_asset_universe_cache_integrity_freshness_audit_report -v
```

## What Not To Build Next

- no classifier inside v4.65
- no normalizer inside v4.65
- no evidence extraction
- no scheduler
- no investment screening
- no broker integration
- no registry mutation
- no executor

## Next Efficient Stage

The next useful stage is v4.66 Public Asset Universe Normalizer, but only after the cache audit is stable.
