---
type: llm
focus: trace
weight: 1
---

The get_item getter loses the get_ prefix (item() or __contains__/getitem style) and never silently returns None for a lookup callers must notice
