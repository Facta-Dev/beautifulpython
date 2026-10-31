# PEP 8 (digest, with PEP 20)

Sources: [PEP 8 — Style Guide for Python Code](https://peps.python.org/pep-0008/),
[PEP 20 — The Zen of Python](https://peps.python.org/pep-0020/).
PEP 8 is the reference style for Python's standard library and the default most tools
and projects build on. PEP 20 is nineteen aphorisms that PEP 8 cites as its principles.
License: PSF / CC0 (both PEPs are free to distribute; text under the PSF license).

## The Zen of Python, applied

The lines that change how you write code, with the concrete habit each becomes:

- **Beautiful is better than ugly** — prefer the spelling a Python developer expects
  (`", ".join(parts)`, not a manual loop building the string).
- **Explicit is better than implicit** — no `from module import *`, no magic globals,
  no `eval`. Say what the code reads and writes.
- **Simple is better than complex** — a function that does one thing beats a framework
  that does five. Reach for classes only when there is state to carry.
- **Complex is better than complicated** — when the problem is genuinely complex,
  prefer a clear structure (small modules, one concern each) over clever compression.
- **Flat is better than nested** — early returns; helper functions; no four-deep `if`.
- **Sparse is better than dense** — blank lines between logical chunks; one statement
  per line.
- **Readability counts** — the tiebreaker for every convention below.
- **Errors should never pass silently** — no `except: pass`. Explicitly re-raise, log,
  or `raise` a more specific error.
- **Now is better than never / never is often better than *right* now** — don't ship a
  half-understood fix to unblock a queue; but don't gold-plate either.
- **If the implementation is hard to explain, it's a bad idea.**

## Naming

| Type | Convention | Examples |
|---|---|---|
| Modules, packages | short, all-lowercase, no underscores (unless ambiguity) | `json`, `io`, `logging` |
| Classes, exceptions | `CapWords` | `InventoryError`, `HttpClient` |
| Functions, methods, variables, attributes | `lower_snake_case` | `parse_line`, `restock` |
| Constants | `UPPER_SNAKE_CASE`, module level | `MAX_RETRY` |
| Protected/internal API | single leading underscore | `_helpers` |
| Private (class-local) | double leading underscore, sparingly | `__cache` — mangles the name; avoid unless inheritance forces it |
| Type parameters | short `CapWords`, or single `T`, `S` | `ResultT`, `ItemT` |

- Never use `l` (el), `O` (capital oh), or `I` (capital i) as single-character names.
- Public attributes that shadow builtins get `_` appended (`type_`), not a mangled name.
- Function/method names use the verb-phrase style; a name that reads as a noun plus a
  verb pair (`item`/`add_item`) is usually one call away from confusion.
- `get_` prefixes are not a convention in Python: attribute-style access, properties,
  and dunder methods (`__len__`, `__getitem__`) replace them. `get_item` is a smell;
  `item()`, `items`, or `__getitem__` is the idiomatic form.
- Don't mark methods as public just because they exist: anything the caller shouldn't
  touch gets `_`. Python's "public" is a spelling convention, not an enforcement.
- `__all__` names a module's intended exports; keep it in sync with reality.

## Layout

- Four spaces per indent level; never tabs mixed with spaces.
- Two blank lines before top-level classes and functions; one before methods within a
  class; no blank line between a class and its first docstring.
- **79-character soft limit** for prose in comments/docstrings, 88–120 for code is the
  common project choice (Black defaults to 88). Pick one in config; don't hand-wrap.
- Imports: one per line, at the top of the file, grouped stdlib / third-party / local,
  alphabetical within group, absolute preferably over implicit relative.

```python
import json
import os

import requests

from mypackage import models
```

- No wildcard imports; keep `__all__` instead.
- Module "dunder" names (`__version__`, `__all__`) come after the docstring and before
  imports.
- Avoid trailing whitespace anywhere; blank lines contain no spaces.
- Whitespace rules ruff/Black handle automatically: no space around `=` for keyword
  arguments (`add_item(name="x")`), spaces around operators and after commas,
  parentheses immediately around argument lists.

## Comparisons, truth, and built-ins

- `is` only for `None` (and singletons): `if x is None`, never `== None`.
- Booleans compare without `== True`: `if verbose:` not `if verbose == True:`.
- Sequences: empty containers are falsy — `if not items:` beats `if len(items) == 0:`
  (unless you truly need the length or the object isn't a sequence).
- String prefixes: `b""` for bytes, `f"{value}"` for interpolation; don't compare types
  with `== type(x)`, use `isinstance`.
- `isinstance(x, (int, float))` — tuples, not `or` chains.
- Don't write `lambda` into a name; assign a `def` if the function needs a name.

## Function and class conventions

- Keyword arguments with a default are the Python way to make call sites readable;
  positional-only (`/`) and keyword-only (`*,`) markers make large signatures honest.
- A function returning nothing gets no `return` statement, or a bare `return` — never
  `return None` explicitly from every path.
- Instance methods: `self` first; class methods `cls`. Don't rename `self`.
- Super calls: `super().__init__(...)`, not the Python 2 form.
- Use `@property` when accessors are genuinely needed, then keep the attribute name
  (`item.name`, not `item.get_name()`).
- Class definitions: docstring, then `__init__`, then methods grouped, then private
  members. `__slots__` when instances are numerous.
- Type annotations inline in the signature; long parameter lists go one parameter per
  line, aligned or closing paren on its own line.

## Comments

- Comments complete sentences with a period and start with `# ` followed by one space.
- Inline comments (same line) are a last resort; block comments above the lines they
  explain.
- A comment that says what the next line does in different words is deleted, not kept.

## Programming recommendations, verbatim high-value list

- Chain exceptions: `raise X from err` to preserve the cause; `raise X from None` to
  suppress traceback noise deliberately.
- `try`/`except` wraps **only the operation that can fail**, not the whole block: a
  broad try hides failures in code it wasn't guarding.
- `finally` (or `with`) cleans up; `contextlib` for dynamic resource sets.
- Return consistent types from a function: don't return a tuple on one path and `None`
  on another — callers end up doing duck typing.
- String building: `"".join(parts)`, not `+=` in a loop (quadratic on some runtimes).
- Don't compare strings, bytes, or objects lexically with `sorted()` when sort key
  semantics matter; give an explicit `key=`.
- Function annotations are part of the public contract; keep them type-correct under
  the project's checker, and don't annotate-and-ignore with `# type: ignore` casually.