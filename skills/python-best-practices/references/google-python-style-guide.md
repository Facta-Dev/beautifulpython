# Google Python Style Guide (digest)

Source: [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html).
Google's internal guide, widely adopted outside Google. It defers to PEP 8 and adds
rules of its own where PEP 8 is silent. License: CC BY 3.0.

## Background and goals

Style rules exist to make code readable and reviewable at scale. The guide's opening
note applies to everything here: "you should not blindly follow [the rules] — a
judgment call is expected." Consistency within a project beats any single rule.

## Modules and imports

- **Import modules, not symbols.** Google allows `from x import y` where y is a
  package or module path, and warns against arbitrary cross-module class imports
  because of shadowing: two different `utils.something` names in one file are a
  classic bug.

  ```python
  from google.maps import search  # good: search is a module
  search.by_address(...)
  ```

- Use the full module path in code (`search.by_address`), not aliased shortcuts.
- Each import on its own line; no `import x, y`.
- Wildcard imports, even from a module you own, are forbidden — they pollute the
  namespace and defeat both readers and checkers.
- Long `from ... import (...)` lists are alphabetical.
- Put `if __name__ == '__main__':` at the bottom: `main()` function first, then the
  guard, with `sys.exit(main())`.

## Exceptions

The section with the most opinionated rules:

- **Raise specific, meaningful exceptions.** Include what was wrong and, where useful,
  what was received: `raise DownloadError(f"missing module {name}")`.
- Modules should define their own exception base class **only** if callers discriminate
  on it; subclass the closest built-in: `class FooError(ValueError)`.
- Never catch-and-reraise silently: catch only what you can handle, and when wrapping,
  `raise NewError(...) from original`.
- Minimize the `try` body: wrap only the line that raises, so the traceback names the
  real culprit.
- `assert` is **not** a runtime guard. It disappears under `-O`; use it for internal
  invariants and tests only, never for validating user input.
- `finally` for cleanup; never `return`/`break` inside `finally` (it swallows the
  in-flight exception).

## Classes

- Prefer composition to multiple inheritance; when multiple inheritance is used, know
  the MRO and call `super().__init__(...)` in every class — never the Python 2
  `Parent.__init__` form.
- `@property` for simple accessor-like behavior; functions for anything heavier. A
  property that could surprise (`item.weight` doing a network call) should be a
  method. Side effects don't belong in property bodies.
- Use `@dataclass` (or pydantic models at validated boundaries) over hand-written
  `__init__`/`__repr__`/`__eq__` where the class is a record.
- Avoid `_` and `__` name mangling unless subclassing forces it.
- Don't use class-level mutable state shared between instances as a poor-man's
  singleton; make sharing explicit.

## Functions

- **Docstrings are mandatory** for public functions; the Google template is: summary
  line, blank line, then `Args:` / `Returns:` / `Raises:` / `Yields:` sections.
- **"Never use mutable objects as default values"**: `def f(a, b=[])` binds one list
  to the function object forever. Use `None` and construct inside.
- Prefer keyword arguments with defaults over positional flags; a caller reading
  `render(shape, verbose=True)` knows what the bool does.
- Decorators: use `functools.wraps` so name, docstring, and signature survive; avoid
  decorators that change the return type invisibly.

## Type annotations

- **Annotate public module, class, and function signatures.** Google enforces typing
  with pytype internally; the principle transfers to mypy/pyright.
- Use modern syntax: `str | None` (3.10+) or `Optional[str]` per project baseline.
- Avoid `Any` in public APIs — it disables checking for every caller. `object` plus
  narrowing is the honest form.
- `type: ignore` needs a reason; `cast` only at the narrowest point.

## Strings, files, and processes

- f-strings for interpolation; for logging prefer lazy `%s` args (`log.info("%s", x)`)
  so formatting is skipped when the level is off.
- `"".join(parts)` to build strings; never `+=` in a loop over many parts.
- `str` everywhere internally; encode/decode at the edges, with `encoding=` passed
  explicitly to file reads.
- Files, sockets, and temp files open with `with` (`tempfile` for temporary paths);
  never rely on refcounting to close.
- `subprocess.run(["cmd", "arg"])` with an argument list, not `shell=True`.

## Testing

- Test names verb-style (`test_foo_does_bar`); one behavior per test; arrange-act-assert.
- Tests are code under the same style rules, except trivial asserts are allowed.
- Assertion failures get messages where the mismatch isn't obvious.
- Mock at the boundary the code controls; don't patch three layers deep.

## Rules worth flagging as Google-specific

- `TODO(username)` or `TODO(issue-link)` format — bare TODOs get deleted in review.
- Lint runs in CI with the pinned pylint-equivalent ruleset (transfers to ruff; see
  `lints/ruff.toml`).
- The Google docstring template (`Args:`/`Returns:`/`Raises:`) is binding; don't mix
  NumPy style into the same project.

## What the guide leaves to PEP 8

Formatting, naming, line length, import grouping — PEP 8 owns these and the guide
defers to it explicitly. When this digest and `pep8.md` disagree about something
formatting-shaped, follow PEP 8; when they disagree about error policy or typing
strictness, this guide is the stricter source.
