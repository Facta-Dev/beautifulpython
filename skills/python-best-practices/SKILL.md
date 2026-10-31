---
name: python-best-practices
description: >-
  Write idiomatic, robust, maintainable Python. Use this skill whenever you write,
  review, refactor, debug, or explain Python code: new modules, packages, functions,
  classes, error types, async code, threading, pyproject.toml, tests, or docstrings.
  Trigger on any mention of Python, pip, uv, pyproject, mypy, ruff, pytest, asyncio, or
  .py files, even when the user does not ask for "best practices" or "idiomatic" code.
  Synthesized from PEP 8 and PEP 20, PEP 257, the Google Python Style Guide, Effective
  Python, and the Python typing documentation.
---

# Python best practices

Distilled from five Python style and design sources, with a digest of each in
`references/`. Where they disagree, this file says which to follow and why.

## 1. Mindset

- **Write Python-shaped code.** Don't transliterate C, Java, Go, or Rust constructs.
  Model absence with `None` and `Optional`, errors with exceptions, polymorphism with
  protocols and duck typing, containers with built-in types. Getter/setter pairs, `Impl`
  classes, interfaces with one implementation, and factory factories are smells.
- **EAFP over LBYL.** Prefer try/except around the risky operation to pre-checking that
  can race with reality ("ask forgiveness, not permission"). But don't nest EAFP so deep
  that control flow disappears; when several failures can happen in one block, narrow
  the except clauses instead.
- **Flat is better than nested.** Guard clauses with early returns beat a staircase of
  `if`/`else`. If a function is four levels deep, lift helpers out.
- **Application code is not library code.** Library code (anything with external users)
  follows the API-design rules below strictly. Application code favors simplicity:
  concrete types, explicit errors that the CLI logs, no speculative generality, no
  plugin systems before there is a second plugin.

## 2. Before you hand back code

Run these and fix everything they report:

```bash
ruff check --fix path/          # ruff owns the mechanical lints
ruff format path/               # or: black (they agree on most code)
mypy path/                      # or: pyright, per the project's choice
pytest                          # the tests you wrote first
```

- Fix a lint rather than silencing it. When a rule is genuinely wrong for one line,
  add `# noqa: <code>` **with a reason**, on the narrowest line. A bare `# noqa` is a
  bug waiting to happen; the lints config in the beautifulpython repo (`lints/ruff.toml`)
  forbids it via RUF100.
- Never flip on warnings-as-errors per module with `# ruff: ...` pragmas scattered in
  files. Configure once in `pyproject.toml` (`[tool.ruff]`), enforce strictly in CI.
- Type-check in the same pass you format. A signature that changed shape without mypy
  noticing is not a signature change, it's a future runtime surprise.

## 3. Data modeling

**Use a dataclass (or TypedDict/NamedTuple) before a raw dict or tuple.** A dict with
string keys has no spelling errors caught, no autocomplete, and no docs. Pick the
lightest shape that validates:

| Need | Use |
|---|---|
| Plain record, no behavior | `@dataclass(frozen=True)` or `NamedTuple` |
| Record validated at the boundary | pydantic `BaseModel` (framework code) or a classmethod validating into a frozen dataclass |
| Heterogeneous dict keys, data only | `TypedDict` |
| Closed set of alternatives with data | a dataclass-less `enum.Enum` with fields, or separate frozen dataclasses + a union type |
| Behavior + invariants | a class |

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Money:
    cents: int
    currency: str

    def __post_init__(self) -> None:
        if self.cents < 0:
            raise ValueError(f"negative amount: {self.cents}")
```

- **Frozen by default.** Mutable records escape by reference into caches, callbacks, and
  closures. Freeze and use `dataclasses.replace` to change.
- **No Boolean params on public functions.** `render(true)` is unreadable at the call
  site. Use an `enum.Enum` (`ReportDetail.SUMMARY`) or two methods.
- **Keyword-only where it matters:** `*,` after positional arguments on functions with
  three or more parameters of the same type; `@dataclass(kw_only=True)` for growing
  records.

## 4. Types

- **Annotate public signatures** — parameters and returns — at minimum. Internal bodies
  can rely on inference, but annotate the tricky ones.
- **Don't lie.** If a function can return `None`, say `-> Item | None` (Python 3.10+;
  use `Optional[Item]` on older runtimes), not `-> Item`. A `dict[str, int]` beats
  `Dict`, `list[Item]` beats `List`, unions written `A | B` beat `Union` (PEP 604).
- **Protocols over inheritance.** Define a small `typing.Protocol` for what the caller
  needs, not an ABC requiring the implementer to inherit yours. Only reach for
  inheritance when you share implementation, not interface.
- **Validation happens once, at the boundary.** Parse config files, network payloads,
  and CLI input into validated dataclasses at the entry point; every inner function
  trusts its inputs. Don't validate a string five layers deep.
- **Be careful with `Any`.** Everything accepts `Any`, which is the same as nothing.
  Use `object` for "any value at all" and narrow with `isinstance`. If an escape hatch
  is unavoidable, name it (`cast(str, value)` with a comment).
- **Literals and aliases:** use `Literal["GET", "POST"]` for a closed set of strings, a
  `NewType` for IDs (`UserId = NewType("UserId", int)`), and a `TypeAlias` for long
  unions. Keep aliases near the types they describe.

## 5. Errors and failures

| Situation | Use |
|---|---|
| Absence is normal (`cache.get`) | return `None` |
| The caller may need to know what failed | a specific exception class |
| A bug or violated invariant inside your code | `assert` (dev-only) or `raise AssertionError` — never for user input |

- **Raise narrow exceptions.** `raise ValueError(f"unknown mode: {mode!r}")`, not bare
  `Exception` or `Error`. Define a module exception hierarchy only when callers
  discriminate; don't invent `FooBaseError` trees up front.
- **Build the message, then raise it.** A string literal or f-string written inline
  in the `raise` is the ruff rule EM101/EM102: assign it first. It keeps messages
  consistent and reusable, and forces the offending value into the message:
  `msg = f"missing key: {key}"` then `raise ConfigError(msg) from err`. Never build
  messages with `+` concatenation.
- **`raise X from err` when you wrap.** Chaining preserves the cause; without `from`,
  the traceback lies about where the exception was born. Inside `except`, always chain:
  `raise ConfigError(f"bad line {n}") from err`.
- **Never swallow.** `except Exception: pass` is the single worst line in a Python
  codebase. When you must absorb, narrow the type, comment why, and log.
- **`finally` and `with`** release resources. Files, locks, sockets, subprocesses,
  database connections — all through `with` (or `contextlib.closing`/`ExitStack` for
  the dynamic cases).
- **Don't signal with special return values.** Returning `-1`/`''`/`None` for three
  different failure modes makes callers guess. Raise, or return a result object.
- **Keep exceptions picklable and testable** if they cross process boundaries.

```python
def parse_record(line: str, line_no: int) -> Record:
    fields = line.split(",")
    if len(fields) != 4:
        msg = f"line {line_no}: expected 4 fields, got {len(fields)}"
        raise ParseError(msg)
    try:
        qty = int(fields[1])
    except ValueError as err:
        msg = f"line {line_no}: bad qty {fields[1]!r}"
        raise ParseError(msg) from err
    return Record(name=fields[0].strip(), qty=qty)
```

## 6. Everyday idioms

- **Comprehensions over hand loops** when the pipeline is short and reads top-down:
  `[f(x) for x in xs if pred(x)]`. Keep an explicit `for` loop when the body is large,
  has side effects beyond building one thing, or needs awkward control flow. Never put
  a long expression in a comprehension's condition; bind it first.
- **`enumerate`, `zip`, `in`, unpacking.** `for i, item in enumerate(items, start=1)`;
  `for name, count in zip(names, counts)`; `first, *rest = row`. Never index with
  `range(len(xs))`.
- **f-strings** for all interpolation — over `%`, `.format`, and `+` chains. Use `=`
  debugging (`f"{value=}"`) in logs during development only.
- **`pathlib.Path`**, not string paths: `Path(__file__).parent / "data" / "out.json"`.
- **Avoid mutable default arguments** (`def add(x, items=[])`): the default is created
  once, shared forever. Use `None` and create inside:

  ```python
  def add(x: Item, items: list[Item] | None = None) -> list[Item]:
      out = items if items is not None else []
      out.append(x)
      return out
  ```

- **Sorting with a key**, not a compare function: `sorted(rows, key=lambda r: (r.rank,
  r.name))` — stable, reads top-down. Reverse only the levels you mean with
  `reverse=` on the level that matters.
- **`else` on loops** exists but almost always hurts readability; skip it.
- **Don't append in a loop to build a string.** Collect parts in a list and `"".join`.

## 7. Imports, modules, and packages

- **One import per line, grouped** stdlib / third-party / local, alphabetical within
  each group (`isort`/ruff does it). No wildcard imports, ever — they pollute the
  namespace and hide renames.
- **Avoid import-time side effects.** Module import must be cheap and safe: parse
  constants, build tables, but don't open files, start threads, touch the network, or
  log. Any work goes in a `main()` guarded by `if __name__ == "__main__":`.
- **Circular imports mean a design problem**, not a `typing.TYPE_CHECKING` puzzle to
  paper over (that one exception aside) — pull the shared types into a lower module.
- **`__init__.py`** declares the package's public API with explicit re-exports
  (`from .client import Client`) and `__all__`. Don't put logic there.
- Keep modules single-purpose and under ~500 lines; a module that needs a table of
  contents is two modules.

## 8. Concurrency and async

- **Threads for I/O-bound, processes for CPU-bound, asyncio for many concurrent
  sockets.** If you cannot say which, threads are wrong half the time. Use
  `concurrent.futures.ThreadPoolExecutor`/`ProcessPoolExecutor` before hand-rolled
  `threading.Thread` management.
- **Every shared mutable resource gets a lock, named near the data** it guards, and
  acquired around the shortest possible region. Prefer queues and messages to shared
  state. Never call user callbacks while holding a lock.
- **`asyncio`: don't block the loop.** No `time.sleep` (use `await asyncio.sleep`), no
  synchronous requests, no CPU-heavy work (move to `loop.run_in_executor` or a process
  pool). Every `Task` you create is stored — otherwise it can be garbage-collected
  mid-flight.
- **Async functions propagate cancellation.** Don't blanket-catch `Exception` inside
  coroutines; `asyncio.CancelledError` must rise (it is a `BaseException` in 3.8+, but
  a bare `except Exception` still catches surrounding error paths incorrectly, so keep
  handlers narrow anyway).
- Library code never assumes a running loop or spawns background tasks on import.

## 9. Packaging, dependencies, tooling

- **`pyproject.toml`** is the single source of truth, with `[project]`, `[tool.ruff]`,
  `[tool.mypy]`, `[tool.pytest.ini_options]`. No `setup.py` for new projects.
- **Pin with ranges**, not `==`, in libraries; commit the lockfile (`uv.lock`,
  `requirements.txt` with hashes) for applications. Never install without hashing in CI.
- **Virtual environments for everything**: never install to the interpreter. `uv venv`
  and `uv sync`, or a `venv` checked into your runbook.
- **One project layout**: `src/mypackage/` layout keeps tests honest about what is
  installed. Tests in `tests/`, never inside the package.
- **Version schemes**: semver for libraries, `0.x` honestly while the API churns;
  deprecate with warnings a release before removing anything public.

## 10. Documentation and docstrings

- A docstring on every public module, class, function. One-line summary in the
  imperative, then detail, in the style the project already uses (PEP 257 style by
  default; Google or NumPy sections for parameter lists — don't mix in one module).
- Don't restate the signature. `"""Returns the name."""` on `get_name()` is noise.
  Document what the signature can't say: raises, side effects, why.
- **Comments explain why, not what.** TODOs get an owner or an issue link.
- Type-annotated signatures carry half the docstring; don't repeat types in prose.

## 11. Tests

- **pytest** by default: plain `assert` with an optional message, `pytest.raises`
  for exceptions, fixtures for shared setup, `parametrize` over a table of cases.
- **Arrange-Act-Assert**, one behavior per test, name the behavior:
  `test_restock_rejects_negative_amount`.
- **Don't test the mock.** Mock at the boundary the code controls (a network client,
  the clock), and keep the real algorithm under test. Patching three layers deep means
  the design needs a seam.
- A bug report becomes a failing test first, then the fix.
- Keep the test suite under 10 seconds where possible; mark network-touching tests and
  skip them in the default run.

## 12. Performance, in order

Measure before optimizing (`cProfile`, `timeit`, or a benchmark in CI). The order that
wins: use the right data structure (`set`/`dict` for membership, `deque` for queue ends,
`Counter` for counting), move invariant work out of loops, let comprehensions and
built-ins (`sum`, `min`, `str.join`) use the C loop, use generators for large streams,
cache pure calls (`functools.lru_cache`) only where the profile says so. Reach for
numpy/polars when the data is tabular; they beat hand loops by an unmeasurable margin.

## Architecture: hexagonal + vertical slicing (when the repo uses it)

Backend repos on the FastAPI/TaskIQ/Dragonfly/Postgres stack follow the facta
backend-python layout. The contracts below are **unbreakable and non-waivable**: the
developers cannot opt out, and neither can you. If an import-linter or banned-import
gate fires, the fix is to re-cut the layout — never to weaken or delete the contract,
and never to silence it with `# noqa`, `# type: ignore`, or a lazy `__getattr__`.
Review treats a broken contract as an automatic Must fix (see `python-review`).

- **Dependencies point inward, only**: composition root -> slices (use-cases) ->
  `ports` (Protocols) -> `domain`. Never the reverse.
- **`domain` is I/O-free.** It MUST NOT import `fastapi`, `sqlalchemy`, `taskiq`,
  `httpx`, or Dragonfly/Redis clients — not even for one helper.
- **Slices don't import each other.** A new feature is a new slice; shared behavior
  moves down into `ports`/`domain`, never sideways.
- **Ports are `Protocol`s; use-cases depend on the Protocol, not the concrete
  adapter.** The composition root (lifespan/startup) picks the real adapter and
  wires it. No service locator, no import-time wiring.
- **SQL, vector metrics, and broker code live in adapters.** Routers only translate:
  request models in, domain calls, and one exception handler maps domain errors to
  HTTP statuses.
- **Anything that must survive a restart dispatches through TaskIQ.** `BackgroundTasks`
  is for best-effort only, and the difference is stated at the call site.
- Every feature change starts by identifying its slice; if you can't say which slice
  a file belongs to, stop and re-cut the layout.

```python
# <app>-domain/pricing.py — pure: zero framework imports
def apply_discount(price: int, pct: int) -> int:
    if pct < 0:
        raise ValueError("discount pct must be >= 0")
    return price - price * pct // 100


# <app>-ports/pricing.py — adapters implement this Protocol
class TaxPort(Protocol):
    def current_tax(self, sku: str) -> int: ...


# The composition root wires TaxPort's postgres adapter; the router maps
# domain errors to HTTP statuses in one exception handler.
```

## FastAPI, TaskIQ, and the backend stack

When the code imports `fastapi`, `taskiq`, `sqlalchemy`, or touches Dragonfly/Redis or
Postgres, read `references/fastapi-taskiq.md` first: some general rules above (hand-rolled
DI, validating what the framework validates) do not apply there, and the stack has its
own set of quiet failure modes that pass every lint in this config.

## Final checklist

Before returning Python code, confirm:

- `ruff` and the project's type checker are clean; tests pass.
- No mutable default arguments; no bare `except:` or `except Exception: pass`.
- Every `raise` is a specific exception with an f-string message, chained with `from`
  when re-raising inside `except`.
- Files opened through `with`; loops through `enumerate`/`zip`, not `range(len(...))`.
- Public functions annotated, including the union with `None` where absence is real.
- No `print()` in library code (logging or the caller's return value instead).
- No import-time side effects; `__main__` blocks guard executable modules.
- No `# noqa` without a reason.
- Data records are frozen dataclasses or named tuples, not raw dicts between layers.

## References

Read these when you need the reasoning behind a rule or a complete checklist for a task.
Each is a condensed digest of one source.

- `references/pep8.md` (https://peps.python.org/pep-0008/): naming, layout, imports,
  whitespace, and the Zen of Python (PEP 20) applied to everyday code.
- `references/pep257.md` (https://peps.python.org/pep-0257/): docstrings, DRY, and
  consistency rules for docstring conventions.
- `references/google-python-style-guide.md`
  (https://google.github.io/styleguide/pyguide.html): modules, imports, error policy,
  tests, typing rules from the Google guide.
- `references/effective-python.md` (https://www.effectivepython.com): item-by-item
  advice from the third edition, condensed.
- `references/python-typing.md` (https://typing.readthedocs.io): the typing
  documentation digest — unions, protocols, generics, variance, mypy pitfalls.
- `references/fastapi-taskiq.md` (the FastAPI + TaskIQ + Dragonfly + Postgres stack):
  read first when the code imports fastapi or taskiq.