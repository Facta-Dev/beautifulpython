---
type: llm
focus: trace
weight: 1
---

Parsing failures raise a dedicated VersionError (or similar) that stores the offending string and does not leak ValueError internals; callers can catch one exception type for any invalid version
