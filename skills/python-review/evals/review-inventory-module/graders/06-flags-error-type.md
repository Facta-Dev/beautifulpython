---
type: llm
focus: trace
weight: 1
---

REVIEW.md flags that InventoryError is a bare Exception subclass whose only detail is a concatenated string, so callers cannot distinguish invalid numbers from duplicates from parse failures
