# Effective Python (digest)

Source: *Effective Python*, 3rd edition, by Brett Slatkin (Addison-Wesley, 2024).
Ninety items on writing Python well. License of the source: copyright, all rights
reserved; this digest paraphrases the advice in condensed form and links back.

The items below are grouped the way the book's chapters are. Item numbers refer to the
third edition.

## Pythonic thinking (Items 1-10)

1. **Know which Python you're writing.** Match the project's minimum runtime; don't
   use 3.12-only syntax in a 3.10-supporting library.
2. **Follow PEP 8.** Formatting is a solved problem; consistency is the win.
3. **Know the differences between `bytes` and `str`.** `str` for text (Unicode), `bytes`
   for raw data; decode/encode explicitly at the boundaries (`open(..., encoding=)`).
4. **Interpolate with f-strings**, not `%` or `.format`; lazy `%s` args for logging.
5. **Use helper classes over bookkeeping** — instead of a tuple-returning function whose
   callers unpack and re-pack, return a small class or NamedTuple; call sites stay
   readable when requirements grow.
6. **Unpack, don't index.** `first, *rest = items`; `enumerate`; multiple assignment.
   Star unpacking makes `range(len(xs))` obsolete.
7. **None-aware expressions**: `value = default if value is None else value`;
   `value or default` is wrong when falsy-but-valid values exist (0, "", []).
8. **Walrus operator `:=`** in comprehensions and loop conditions to avoid computing a
   value twice (`while chunk := f.read(8192):`).
9. **`raise`/`return` in one place** — a function that returns a value OR raises a
   special-exception sentinel (like returning `None` as a code for three failures)
   forces callers to test types; exceptions or explicit unions are clearer.
10. **Avoid surprising positional syntax**: when a function has many same-typed
    parameters, require keywords (`*,`) so call sites self-document.

## Comprehensions and functions (Items 11-20+)

- Use comprehensions over `map`/`filter` with lambdas — clearer for simple cases.
- Don't use more than two control sub-expressions in one comprehension; a `for` loop is
  clearer at that point.
- `any`/`all`/`sum`/`max` with generator expressions instead of manual loops.
- **Generators** for sequences too big to materialize; a generator function returns an
  iterator lazily and composes with everything else.
- **Nested closures over stateful decorators**; a class with `__call__` beats a
  closure when state must survive calls (`functools.lru_cache` covers caching; don't
  hand-roll it).
- `functools.wraps` on any decorator, so tracebacks and introspection stay honest.
- **Positional or keyword only where it matters**: `def safe_division_c(numerator,
  denominator, *, ignore_overflow=False)` — the `*` makes intent part of the API.
- Annotate public functions; the annotation is also the tool's contract.

## Classes and inheritance (Items 26-40+)

- **Prefer dataclasses over `__init__` boilerplate**; `frozen=True` for values; default
  fields must be immutable or `field(default_factory=...)`.
- **Compose private helper classes over extending built-ins** — subclassing `dict` or
  `list` to add behavior breaks under methods that bypass your override; `collections`
  or composition is robust.
- **`@classmethod` polymorphism** (alternative constructors) beats metaclass tricks.
- **Use super() with cooperative multiple inheritance**; know the MRO.
- **Mix-in classes**: small, single-behavior classes that assume nothing; they don't
  define `__init__`.
- **`__getattr__`/`__getattribute__`** lazily; they're slow and surprising. Prefer
  explicit methods or descriptors.
- **Descriptor classes** to factor repeated property logic.
- **`__slots__`** to cut per-instance memory when instances are numerous; note it
  freezes the attribute set.
- **`__init_subclass__`** over metaclasses for plugin registration.
- Attributes: keep them simple; promote to `@property` when behavior grows (and keep
  the property body free of side effects).

## Concurrency and parallelism (Items 67-80+)

- Threads for blocking I/O (a thread blocks per socket); `ThreadPoolExecutor` over raw
  threads.
- Processes for CPU-bound work — the GIL stops bytecode-level parallelism;
  `ProcessPoolExecutor` sidesteps it.
- **asyncio** for ten thousand concurrent operations, not ten; coroutines, tasks, and
  event loops each have their own failure mode: forget to `await`, or drop a task
  reference, and work silently never happens.
- Never block the event loop with `time.sleep` or synchronous I/O.
- `queue.Queue` and futures before locks; when locking, name the lock after the data
  it protects.
- Beware of re-entrancy: a `Lock` is not an `RLock`; nested acquisition deadlocks.

## Robustness and performance (Items 81-90+)

- `contextlib.contextmanager` (or `ExitStack`) over hand-written `try/finally` stacks.
- Copy dependencies explicitly (`copy.copy` vs `deepcopy` and when either lies to you).
- **Don't mutate during iteration** — add or remove keys from a dict while looping, and
  the loop skips or repeats entries; iterate a copy or collect first.
- `functools.lru_cache` only for pure, cheap-keyed functions; measure.
- **Profile before optimizing** (`cProfile`, `timeit`); the built-in data structures
  (`set`, `deque`, `dict`, `heapq`) beat hand-rolled ones by orders of magnitude.
- `bisect` for sorted-list insertion; `heapq` for priority behavior.
- Testing: `pytest.raises(MyError)` around the exact call, not the whole test body.
- Debug: `repr`, `%`-style formatting with all the flags, and `breakpoint()`; don't
  leave `print` debugging committed.

## The habits the book hammers

1. Make every failure either an exception or an explicit result value — never a magic
   sentinel that the caller must remember to type-check.
2. Make every shared resource's ownership explicit: who closes the file, who owns the
   lock, who cancels the task.
3. Prefer "one obvious way" (Zen): when two constructs in the stdlib do it, pick the
   one Python developers reach for first.
