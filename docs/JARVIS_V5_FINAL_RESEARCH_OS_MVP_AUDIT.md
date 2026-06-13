# J.A.R.V.I.S. v5.0 Final Research OS MVP Audit

v5.0 is the final MVP audit and release-readiness seal for J.A.R.V.I.S. as a local-first public research operating system. It is not a new pipeline behavior layer.

J.A.R.V.I.S. now provides:

- public source planning
- public source manifest definition
- fetch dry-run planning
- explicitly authorized local cache controls
- cache integrity and freshness audit
- public asset normalization
- structural public asset classification
- research priority queue preparation
- public evidence pack drafts
- operator research dashboard
- end-to-end public universe workflow audit
- manual trust and manual approval boundaries

J.A.R.V.I.S. is not:

- a trading bot
- a broker integration
- an investment advisor
- a recommendation engine
- an allocation engine
- an automatic evidence verifier
- an automatic approval system
- an executor

The core invariant remains:

Automated research. Manual trust. Manual approval. No execution.

## Write Policy

The audit and report are read-only by default. The default path writes nothing.

An optional local audit snapshot write requires the exact authorization phrase:

`AUTHORIZE_V5_FINAL_RESEARCH_OS_MVP_AUDIT_LOCAL_CACHE_ONLY_NO_VERIFY_NO_TRADE`

Even with this phrase, the write may only target the local v5 final audit cache path and the output remains unverified and unapproved. It does not verify evidence, approve assets, trust assets, mark assets investable, recommend, allocate, buy, sell, trade, mutate the registry, or create an executor.

## How To Run

```powershell
python -m jarvis.jarvis_v5_final_research_os_mvp_audit_report
python -m jarvis.jarvis_v5_final_research_os_mvp_audit_report --input jarvis\data\jarvis_v5_final_research_os_mvp_audit.synthetic_complete.json
python -m unittest jarvis.tests.test_jarvis_v5_final_research_os_mvp_audit jarvis.tests.test_jarvis_v5_final_research_os_mvp_audit_report -v
```

## What Not To Build In v5.0

- no screening inside v5.0
- no research scoring inside v5.0
- no evidence extraction
- no scheduler
- no investment recommendation
- no broker integration
- no registry mutation
- no executor

## Next Efficient Stage

The suggested next phase is v5.1 Real Public Source Fixture Wiring / Operator Runbook, still with no broker integration and no executor.
