# What `--fix` infers

The [README](../README.md#use) has the options (`--fix`, `--diff` to preview, `--unsafe-fixes`,
`--show-fixes`). `--fix` adds the annotation where the value decides it, for a plain `name = value`
in a function or module body:

- a literal: `count = 0` becomes `count: int = 0`;
- a container whose elements agree: `[1, 2]` gives `list[int]`, `{"a": (1, "b")}` gives
  `dict[str, tuple[int, str]]`;
- a call to a capitalised name (`path = Path(...)` gives `Path`), or to a plain function that
  declares its return type (not a decorated, generic, async or redefined one, and not a return of
  `None`, `Any` or one that uses a `TypeVar`), in the same module or, with the CLI, in another file
  it's checking: `from pkg.util import f`, `import pkg.util as u` then `u.f()`, relative imports and
  re-exports all work, as long as every name in the type already means the same thing in the file;
- a local whose type is already known (annotated, a parameter, or fixed earlier in the same scope):
  a plain copy (`y = x`), a subscript (`nums[0]`), an attribute or method call of a class defined in
  the same module (`p.x`, `p.norm()`), a `str`/`bytes` method with a fixed return (`s.strip()`), or
  a `list`/`set`/`dict` method that returns its own element type (`nums.pop()`, `d.get(k)` as
  `V | None`);
- a value computed from such: `a if c else b` when both sides agree; arithmetic on builtin scalars
  (`n + 1`, `n / 2`, `"x" * n`, `"%s" % n`; never `**`, whose result can change type); a list, set
  or dict comprehension whose elements are known; `sorted`, `list`, `set`, `frozenset` or `tuple` of
  something whose elements are; and `await` of a call to one of the module's `async def`s.

A loop's target (LVA002) and an unpacking's names (LVA001) are declared instead, on a line of their
own before the statement: `for k, v in ages.items():` with `ages: dict[str, int]` gets `k: str` and
`v: int` above it. The target's type comes from what's iterated: a `range`, `enumerate` and `zip` of
known things, a `dict`'s `.keys()`/`.values()`/`.items()`, or any container whose type is known; an
unpacking splits a tuple type (`a, b = pair`, `pair: tuple[int, str]`) over its names.

With `--unsafe-fixes`, LVA008 and LVA010 are fixed too, by rewriting the annotation (`total: float`
only ever given `int`s becomes `total: int`): a guess, since a declared type can be wider on
purpose.

It never touches class bodies (a dataclass would gain a field), and it leaves what it can't fix
reported. The standard library and third-party packages are out of reach.

`--show-fixes` lists, after the report, each fix and how its value decided it (for `b = s.strip()`:
`str`, from `str.strip`'s fixed return type), marking the guesses `--unsafe-fixes` would add;
`--format=json` always carries the same as a `fix` object (`annotation`, `reason`, `unsafe`) on each
result.

The type hierarchy LVA008–LVA010 compare through is the numeric tower (`bool` < `int` < `float` <
`complex`) plus the classes a module defines, under the bases they name.
`[tool.constricter.narrower]` (or the plugins' `narrower` option, as `B=A, int=`) replaces what
those say for each type it names, and vouches for the types it names: an imported type the rules
would never compare otherwise is compared.
