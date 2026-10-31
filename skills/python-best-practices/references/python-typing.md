# Python typing documentation (digest)

Source: [typing documentation](https://typing.readthedocs.io/en/latest/) and the
specifications it links (PEP 604 unions, PEP 544 protocols, PEP 634 patterns, PEP 695
type parameters). This digest condenses the parts that change day-to-day code.
The typing docs are CC-style; the PEPs are public domain.

## What the checker is for

Annotations are documentation the tools can check. mypy and pyright treat an annotated
function as a contract: anything a caller ships outside that contract is an error, not
an accident. The rules below assume the project runs a checker in CI; annotations
without a checker are just prose with extra steps.

## Syntax, by Python version

- 3.10+: `str | None` unions (PEP 604); built-in generics (`list[int]`,
  `dict[str, int]`) since 3.9. Prefer these everywhere; `List`/`Dict`/`Union` from
  `typing` are legacy spellings.
- `TypeAlias`/`type X = ...` (PEP 695, 3.12) for aliases: `type UserId = NewType(
  "UserId", int)` is wrong — `UserId = NewType("UserId", int)` is the NewType form;
  `type Alias = int | None` is the alias form. Don't mix them up.
- Forward references: quote-strings still work but `TYPE_CHECKING` imports are cleaner:

  ```python
  from typing import TYPE_CHECKING

  if TYPE_CHECKING:
      from mypackage.models import Item

  def render(items: list["Item"]) -> str: ...
  ```

## The core vocabulary

| Construct | Use for |
|---|---|
| `T or None` unions (`Optional[T]`) | a value that can be absent; callers must handle None |
| `Literal["GET", "POST"]` | a closed set of strings, checked statically |
| `TypedDict` | dict-shaped records at boundaries (`json.load` results) |
| `NamedTuple` / frozen dataclass | records with fields and iteration |
| `Protocol` | duck typing with static checks, no inheritance required |
| `Callable[[int], str]` | a function parameter, checked by signature |
| `Iterator[T]` / `Iterable[T]` | streams a function produces or consumes |
| `Generator[Y, S, R]` | a generator with send/return types |
| `Sequence[T]` / `MutableSequence[T]` | read-mostly vs mutable containers |
| `Hashable` / `Sized` / `Reversible` | structural capabilities |
| `AbstractSet[T]`, `Mapping[K, V]` | read-only views, safe in public signatures |
| `NewType("UserId", int)` | distinct IDs that don't mix with raw ints |
| `Final`, `ClassVar` | values that don't rebind / class-level attributes |
| `Any` / `object` | escape hatch vs. "any value at all" |

## Protocols over ABCs

A `Protocol` describes the shape the caller needs. Any class satisfying it works with
no registration:

```python
class Closeable(Protocol):
    def close(self) -> None: ...

def use(c: Closeable) -> None:
    c.close()
```

Rules of thumb: protocols for library/SDK boundaries and the caller side; ABCs when
you also want to share implementation; `isinstance(x, MyProtocol)` works when the
protocol is decorated `@runtime_checkable`.

## Generics and variance

- Functions: `def first[T](items: list[T]) -> T: ...` (PEP 695) or
  `TypeVar("T")` on older Python.
- Classes: `type Box[T]: ...` or `Generic[T]`.
- Covariance (`TypeVar(..., covariant=True)`) only for read-only containers
  (`Sequence[Derived]` accepts `list[Base]`); containers you mutate must stay
  invariant. Getting this wrong is the classic "why won't mypy accept list[Dog] for
  list[Animal]" error.
- `ParamSpec` for decorators that must preserve signatures:

  ```python
  from typing import ParamSpec, TypeVar, Callable

  P = ParamSpec("P")
  R = TypeVar("R")

  def logged(fn: Callable[P, R]) -> Callable[P, R]:
      def inner(*args: P.args, **kwargs: P.kwargs) -> R:
          logger.info("call %s", fn.__name__)
          return fn(*args, **kwargs)
      return inner
  ```

## The pitfalls mypy catches that humans don't

- **Returning None implicitly.** A function that falls off the end returns None; the
  checker reports "missing return statement" when the annotation promised otherwise.
- **dict.get returning Optional.** `config.get("port")` is `int | None`; arithmetic on
  it fails under the checker at the line where the assumption lived, not at runtime.
- **Mutable default arguments are detected** (unless the checker is configured off):
  `def add(x, items: list[Item] = [])` is flagged; use `None` + construct.
- **Unused ignore directives** (`warn_unused_ignores`) catch stale `# type: ignore`s.
- **Untyped defs** (`disallow_untyped_defs`) make every public function's signature an
  explicit contract rather than an assumption.

## strict-mode starter configuration

```toml
[tool.mypy]
python_version = "3.12"
strict = true
warn_unused_ignores = true
```

Strict mode enables `disallow_untyped_defs`, `disallow_any_generics`,
`warn_return_any`, `check_untyped_defs`, and friends. The `lints/mypy.ini` in
beautifulpython carries a ready-made version. Ramp projects up with
`disallow_untyped_defs` first — it delivers most of the value alone.

## When to relax

- Frameworks inject magic (FastAPI's `Depends`, SQLAlchemy's session): use the
  framework's own plugins (`sqlalchemy[mypy]`, fastapi's annotations) instead of
  `type: ignore` sprinkles.
- Third-party untyped packages: `[[tool.mypy.overrides]] module = "pkg"`,
  `ignore_missing_imports = true`, in config — never in code.
- Where a checker cannot understand deliberate behavior, one `# type: ignore[code]
  # reason: ...` — the narrowest line, with the specific error code.