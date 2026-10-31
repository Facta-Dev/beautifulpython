---
type: llm
focus: trace
weight: 1
---

config_get_int's behavior is preserved: a value that overflows C long (99999999999999999999) is NOT_NUMBER in the C, so the port states what it does for huge ints and its tests cover it; a partially numeric value (12x) and an empty value are also NOT_NUMBER
