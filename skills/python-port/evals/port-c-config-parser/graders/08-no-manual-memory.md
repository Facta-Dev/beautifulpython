---
type: llm
focus: trace
weight: 1
---

No manual resource management leaks through: no close() required for correctness on the success path, no fixed 256-byte section name truncation, no C-style NOMEM error paths
