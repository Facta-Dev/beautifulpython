---
name: python-port
description: >-
  Port code from C, C++, Rust, Go, Java, JavaScript, or TypeScript into idiomatic
  Python that keeps the original behavior: exceptions instead of error codes, None
  and explicit unions instead of sentinels, enums and dataclasses instead of flag
  ints and raw dicts, and tests that prove the port matches. Use this whenever the
  user asks to port, translate, convert, migrate, or rewrite code in Python
  ("rewrite this in Python", "what would this look like in Python", "move this
  module to Python"), even if they don't say "port". Pairs with the
  python-best-practices skill, which covers the target code's style.
---

# Python port

The goal is the Python a Python developer would have written to solve the same
problem, with the same observable behavior. A line-by-line transliteration (C written
in Python syntax, or Rust with `try/except Exception` around every call) runs but
keeps every problem the original had and adds a new set of Python-shaped ones. Port
the behavior, not the structure.

## 1. Understand the original before writing anything

1. **Read the code and its tests**, and anything that calls it, if you have it.
2. **List the observable behavior**: every public function, its inputs, its outputs,
   and every way it can fail. Include the quiet parts, which are where ports go
   wrong: iteration order, how ties break, empty input, whitespace and case handling,
   integer bounds and overflow, encoding, and what counts as an error versus a valid
   edge case.
3. **Note what is incidental**, meaning things the original only does because of its
   language: manual memory management and NOMEM paths, out-parameters, NULL returns,
   fixed-size buffers, header/implementation file splits, a class that exists only to
   group functions, raw flag bitmasks. These don't carry over.
4. If the original has a bug or an ambiguity, keep its behavior, flag it in the
   porting notes, and let the user decide. A port is not the place to silently fix
   things.

## 2. Port the tests first

Translate the original tests into pytest tests before porting the implementation.
Keep one Python test per original test, with a name that maps back to it, so a reader
can check coverage. The tests are the definition of "same behavior". If the original
has no tests, write characterization tests from the behavior list in step 1. Use
`pytest.raises(...)` where the original expects a failure, and parameterize only when
the original's table structure says so.

## 3. Design the Python API, then implement it

Decide the public types and signatures from the behavior list, not from the original's
shape. Then implement against the ported tests.

### From C and C++

| In the original | In Python |
|---|---|
| `malloc`/`free`, `new`/`delete`, create/destroy pairs | Objects with reference counting and `with` for anything needing deterministic cleanup; a `__enter__`/`__exit__` (or `contextlib.closing`) for handles |
| `NULL` meaning "absent" | `None`, and `X | None` in the signature |
| Error codes (`-1`, `ERR_*` defines), `errno` | A specific exception class with the offending value attached; `raise ... from err` when wrapping |
| Out-parameters (`int *err_line`, `long *out`) | Return values: put the data in the result or the exception's attributes |
| Flag bitmasks (`FLAG_A \| FLAG_B`) | Keyword arguments (`trim_values=False`), an `enum.Flag`, or a set of enum members |
| `char *` plus length, `strcmp`, `strcasecmp` | `str`, `==`, `casefold()` (or `lower()` when matching the original's ASCII-only behavior) |
| Pointer plus count, iterator by index | Sequences, iterators, `enumerate` |
| Fixed-size buffers and their truncation | Native `str`/`bytes`/`list`; drop the limit unless the limit is behavior |
| `#define` constants and macros | Module-level constants, functions, enums |
| Global or static mutable state | A class the caller instantiates and owns |
| `strtol`, `sscanf` and friends | `int(value, 10)`, `str.split`, `re` — map parse failures to your exception |

C `long` overflow (`99999999999999999999` failing `strtol` with `ERANGE`) has no
Python equivalent — `int()` accepts it. Decide deliberately and note it: either honor
the original's range check explicitly, or accept big ints and record the difference.

### From Rust

| In the original | In Python |
|---|---|
| `Result<T, E>` | An exception hierarchy (or a result value); `?` becomes implicit — don't wrap every call in `try/except` re-raising the same type |
| `Option<T>` and `unwrap()` | `None` plus explicit unions; `unwrap()` becomes a plain dereference or `.get()` with a real error |
| Enums with data | An `enum.Enum` with fields, separate frozen dataclasses in a union, or `Literal` for string sets |
| Traits | `typing.Protocol` (structural), or shared base/ABC when implementation is shared too |
| `impl Display` / `Debug` | `__str__` / `__repr__` |
| `From`/`TryFrom` conversions | constructors (`@classmethod from_str`), `__init__` validation |
| Iterators and combinators | Generators and comprehensions; don't hand-roll `.map()` object chains |
| Newtypes | `NewType` for IDs at type-check level; frozen dataclasses for value objects |
| `#[non_exhaustive]` | keep enums open by not exhaustively matching in library code (match with `case _:`) |

### From Go, Java, and JavaScript

- Go `(value, error)` returns become exceptions (or a result object); `nil` becomes
  `None`; interfaces become `Protocol`; goroutines and channels become `asyncio` tasks
  and queues, or `ThreadPoolExecutor`/`ProcessPoolExecutor` when the work is
  blocking.
- Java getters/setters and interface-only classes collapse into plain attributes,
  dataclasses, and protocols. Checked exceptions all collapse into runtime exceptions.
- JavaScript `null`/`undefined` become `None` (one absence, not two); thrown errors
  become exceptions raised, not returned; plain objects become dataclasses or
  `TypedDict` at boundaries; numbers: Python ints are unbounded, floats are still
  IEEE 754 — say which one a port chose and why.

## 4. Keep the port proportionate

A port that matches the original on every possible input is usually the wrong goal.
Match it on the inputs it actually receives, and use Python's standard library for the
rest.

- **Don't reimplement the source language's runtime.** Use `str.splitlines`,
  `str.strip`, `int`, `pathlib`, `itertools`, and the `collections` module, not
  hand-written copies of C's `strtol` state machines or Rust's iterator traits. Where
  Python's behavior differs only on exotic input (Unicode digits in `int()`,
  `\r`-handling in `splitlines`, unbounded ints), list the difference in the porting
  notes instead of coding around it. Write a compatibility shim only when the user
  says those inputs occur.
- **Don't grow the API.** Port the public surface the original has, plus the dunder
  conventions Python callers expect (`__repr__`, `__eq__`/`__hash__` on value objects,
  `__len__`/`__iter__` on containers). Skip builders, registries, and plugin systems
  unless the original's callers need them.
- **Keep the algorithm unless it's wrong.** Swap in a different algorithm only to fix
  a real problem, such as quadratic string building on realistic input, and say so in
  the notes.
- **Check the size.** Count code lines, excluding tests, comments, and docstrings. A
  port from C, Rust, or Go usually lands smaller than the original (no memory
  management, no trait impls, no header files). Much larger than the original usually
  means one of the three habits above.

Differential testing against the original is worth doing, but a few dozen realistic
and edge-case inputs answer the question. A property-based fuzzing suite usually just
finds exotic divergences that belong in the notes.

## 5. Verify

Run these and fix everything before reporting:

```bash
ruff check .
mypy .                    # or the project's configured checker
pytest
```

Every ported test must pass. If the original's tests can be run too (a C binary, a
Go test run), run them and compare results on the same inputs.

## 6. Write the porting notes

Alongside the code, write a short `PORTING.md` that a reviewer can check in a few
minutes:

- **API mapping:** a table from each original function or type to its Python
  equivalent.
- **Test mapping:** each original test and the Python test that covers it.
- **Deliberate differences:** anything that now behaves differently and why, such as
  the C `long` overflow bound that no longer applies, a fixed buffer limit that's
  gone, or unbounded ints where the original wrapped.
- **Preserved quirks:** odd behavior kept on purpose, so nobody "fixes" it by
  accident.
- **Verification:** which commands you ran and their result, or a plain statement
  that you couldn't run them.

For the style of the Python itself, follow the `python-best-practices` skill if it is
installed.
