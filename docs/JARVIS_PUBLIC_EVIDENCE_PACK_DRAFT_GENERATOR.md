# J.A.R.V.I.S. v4.69 Public Evidence Pack Draft Generator

v4.69 generates draft public evidence packs from public asset universe research
queue items.

The generator answers which public evidence should be collected, which public
source categories are required, which fields need later manual review, what is
missing before manual trust review, and what the next manual research step
should be.

This layer is intentionally narrow:

- It is not evidence extraction.
- It is not evidence verification.
- It is not verified evidence promotion.
- It is not approval, trust, or investability.
- It is not investment recommendation.
- It is not allocation.
- It is not trading.
- It does not fetch, download, scrape, or call APIs.
- It does not use browser automation, subprocesses, schedulers, brokers,
  credentials, or private/account data.
- It does not write by default.

Draft packs remain unverified public-data workflow scaffolding. They are not
evidence, not manual approval, not a buy/sell signal, and not execution.

## Optional Local Cache Write

The default report and evaluation paths never write files.

An optional local-cache write helper exists for tests and future explicit use.
It requires the exact phrase:

```text
AUTHORIZE_PUBLIC_EVIDENCE_PACK_DRAFT_LOCAL_CACHE_ONLY_NO_VERIFY_NO_TRADE
```

Even with that phrase, the helper may only write draft-pack JSON and metadata
under:

```text
jarvis/local/public_asset_universe/evidence_pack_drafts/
```

It must not write to `jarvis/data`, docs, templates, registry files, candidate
files, or the repo root.

## Run

```powershell
python -m jarvis.jarvis_public_evidence_pack_draft_generator_report
python -m jarvis.jarvis_public_evidence_pack_draft_generator_report --input jarvis\data\jarvis_public_evidence_pack_draft_generator.synthetic_complete.json
python -m unittest jarvis.tests.test_jarvis_public_evidence_pack_draft_generator jarvis.tests.test_jarvis_public_evidence_pack_draft_generator_report -v
```

## Do Not Build Inside v4.69

- no evidence extraction
- no evidence verification
- no investment screening
- no research scoring
- no scheduler
- no investment recommendation
- no broker integration
- no registry mutation
- no executor

## Next Efficient Stage

v4.70 Operator Research Dashboard Integration.
