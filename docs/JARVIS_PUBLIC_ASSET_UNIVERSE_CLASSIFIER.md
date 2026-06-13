# J.A.R.V.I.S. v4.67 Public Asset Universe Classifier

The public asset universe classifier takes normalized public asset records from v4.66 and adds deterministic structural classification tags.

It can classify fields such as asset class, instrument type, region bucket, currency bucket, venue bucket, identifier quality, data completeness, freshness, and evidence-readiness bucket.

It is intentionally narrow:

- it is not screening
- it is not research scoring
- it is not ranking
- it is not evidence extraction
- it is not evidence verification
- it is not approval, trust, or investability
- it is not investment advice
- it does not fetch, scrape, download, call APIs, or use browser automation
- it does not write by default
- it does not allocate, emit buy/sell signals, trade, or create an executor
- it does not integrate with brokers, Lightyear, LHV, crypto exchanges, wallets, credentials, or private/account data

The optional local classified-cache write helper requires the exact authorization phrase:

`AUTHORIZE_PUBLIC_ASSET_UNIVERSE_CLASSIFY_LOCAL_CACHE_ONLY_NO_VERIFY_NO_TRADE`

Even when explicitly authorized, classified output remains unverified and unapproved. It is local-cache-only and must not be committed.

Run the report:

```powershell
python -m jarvis.jarvis_public_asset_universe_classifier_report
python -m jarvis.jarvis_public_asset_universe_classifier_report --input jarvis\data\jarvis_public_asset_universe_classifier.synthetic_complete.json
```

Run focused tests:

```powershell
python -m unittest jarvis.tests.test_jarvis_public_asset_universe_classifier jarvis.tests.test_jarvis_public_asset_universe_classifier_report -v
```

Do not build next inside v4.67:

- no screening
- no research scoring
- no evidence extraction
- no scheduler
- no investment recommendation
- no broker integration
- no registry mutation
- no executor

Next efficient stage: v4.68 Public Asset Universe Research Priority Queue.
