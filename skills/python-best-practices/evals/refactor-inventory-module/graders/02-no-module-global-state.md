---
type: llm
focus: trace
weight: 1
---

Storage no longer depends on a module-level mutable registry; each Inventory owns its items, and no public function mutates hidden global state
