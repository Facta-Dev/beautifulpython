---
type: llm
focus: trace
weight: 1
---

REVIEW.md flags the except Exception: pass in load (and the open() without a with statement) and places it in the highest-priority category, because load continues with an undefined text variable after a failed read
