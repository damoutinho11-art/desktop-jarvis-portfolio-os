# J.A.R.V.I.S. v48.0 Stable Runtime Facade

## Purpose

v48 is the first no-behavior-change runtime slimline step.

It creates a stable non-versioned runtime entrypoint:

```text
jarvis.runtime.operator
```

and points the root shortcut to it:

```text
jarvis_operator.py -> jarvis.runtime.operator
```

The stable facade currently delegates to the validated v45 backend:

```text
jarvis.jarvis_v45_0_free_research_cache_evidence_pack_bridge
```

## Why this matters

Before v48, every active root update pointed directly at another staged file like:

```text
jarvis_v45_0_free_research_cache_evidence_pack_bridge.py
```

That kept the root operator tied to stage naming and made cleanup harder.

After v48, future cleanup can move behavior behind the stable facade while keeping the root entrypoint unchanged.

## What v48 does not do

v48 does not:

- delete files
- archive legacy files
- change daily behavior
- change weekly behavior
- change candidate selection
- change approval-ticket behavior
- create broker paths
- create orders
- execute trades

## Validation

The root should point to:

```text
jarvis.runtime.operator
```

The active backend should still be:

```text
jarvis.jarvis_v45_0_free_research_cache_evidence_pack_bridge
```

Daily output should still show:

```text
J.A.R.V.I.S. Free Research Cache Evidence Pack Bridge
```

## Next cleanup stage

The next stage can start moving selected v45/v44/v43 functions behind the stable runtime facade and reduce the active version-module closure, while preserving exact output behavior.