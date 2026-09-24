# What `--fix` infers

The [README](../README.md#use) has the options (`--fix`, `--diff` to preview, `--unsafe-fixes`,
`--show-fixes`). `--fix` adds the annotation where the value decides it, for a plain `name = value`
in a function or module body:

- a literal: `count = 0` becomes `count: int = 0`;
- a container whose elements agree: `[1, 2]` gives `list[int]`, `{"a": (1, "b")}` gives
  `dict[str, tuple[int, str]]`; a tuple longer than `max-length` (4) is `tuple[T, ...]` if its
  elements agree, and untyped if not (it would be LVA011's);
- a call to a capitalised name (`path = Path(...)` gives `Path`, a guess), if it can be written as a
  type: a name or dotted name whose first name the module binds only by an import or a class
  statement (not `Klass = ...`, `self.api.X()`, `make().X()`); or to a plain function that declares
  its return type (not a decorated, generic, async or redefined one, and not a return of `None`,
  `Any` or one that uses a `TypeVar`), in the same module or, with the CLI, in another file it's
  checking: `from pkg.util import f`, `import pkg.util as u` or `from pkg import util` then `u.f()`,
  relative imports and re-exports all work. A name in the type the file doesn't import is imported
  for type checking alone (see below);
- a builtin with a fixed result: `len(x)` is an `int`, `hex(n)` a `str`, `any(xs)` a `bool`, `dir()`
  a `list[str]`, `range(n)` a `range`, and so on; but not where the module binds the name itself (a
  parameter named `format`, a local `input`, its own `def dir()`), anywhere in it;
- a copy of a local whose type is already known (annotated, a parameter, or fixed earlier in the
  same scope): `y = x`;
- a member of any value whose type is known, a local or anything else here (`self.index`, `f()`,
  `xs[0]`, `", "`), however deep (`self.index.name.upper()`): a subscript (`nums[0]`; a slice, or an
  index typed `slice`, is the container's own type), an attribute (an annotated one, or a
  `@property` declaring its return) or method call of a class defined in the same module or another
  checked file (`p.x`, `p.norm()`), a `str`/`bytes` method with a fixed return (`s.strip()`,
  `", ".join(parts)`, `"k=v".partition("=")` as `tuple[str, str, str]`), or a `list`/`set`/`dict`
  method that returns its own element type (`nums.pop()`, `d.get(k)` as `V | None`); in a
  classmethod, `cls` is `type[C]`, whose class attributes (`limit: int = 3`, `ClassVar[T]`) and
  classmethods' and staticmethods' declared returns type `cls.x` and `cls.m()`. A member of a
  guessed value is a guess too (`Box().name`), and its fix kinds include the value's;
- `typing.cast(T, x)`, however `cast` is imported: `T`;
- the standard library, resolved through the imports (`import m`, `import m as a`,
  `from m import f`), by tables generated from typeshed's stubs (`tests/typeshed/stdlib_tables.py`,
  into `constricter/fix/tables/`, keeping what Linux, macOS and Windows and Python 3.11 to 3.14
  agree on, where they have it: `os.getuid()` is an `int`): a function returning a builtin type
  whatever its arguments (`time.time()` is a `float`, `os.cpu_count()` an `int | None`); a
  non-generic class, or a function or classmethod returning one: `logging.getLogger()` is a
  `logging.Logger`, `datetime.now()` a `datetime.datetime`, `os.stat(p)` an `os.stat_result`; and on
  a value typed as such a class, its attributes and properties, and its methods' returns
  (`parser.prog` is a `str`, `dt.astimezone()` a `datetime.datetime`);
- a standard-library function or method whose arguments decide its type, by the signature they
  match, as a type checker picks among its overloads: `os.listdir(data)` with `data: bytes` is a
  `list[bytes]`, `ast.parse(s, mode="eval")` an `ast.Expression` (by the literal),
  `os.path.join(name, x)` a `str` whatever `x` is (only the `str` signature takes `name`),
  `os.getenv("X", 3)` a `str | int`, `re.compile("x")` a `re.Pattern[str]` (its type variable bound
  by the argument), `parser.parse_args()` an `argparse.Namespace`, and on a `re.Pattern[str]`,
  `pat.match(s)` a `re.Match[str] | None` (the class's type parameter bound by the receiver's type).
  A generic class's constructor is read the same way, from its `__new__` or `__init__`:
  `collections.deque(names)` with `names: list[str]` is a `collections.deque[str]`,
  `itertools.product(a, b)` an `itertools.product[tuple[str, int]]`, `array.array("i")` an
  `array.array[int]`, `weakref.ref(obj)` a `weakref.ReferenceType[Foo]`. Only when that's certain:
  every signature that may be the one (not certainly refusing the arguments, up to the first that
  certainly takes them) gives the same type, on every platform and version, with every type variable
  bound (`collections.deque()` isn't typed). An argument binds a type variable by its type: a
  builtin scalar (`str`, `bytes`, `int`, a literal, `None`, ...) wherever the parameter takes it;
  any other type only where the parameter is nothing but an unbounded type variable
  (`copy.copy(obj)` is a `Foo`); a builtin container (`list[str]`, `dict[str, int]`'s keys,
  `tuple[str, ...]`) or a `str` by its element, where the parameter is a generic class of one
  (`Iterable[_T]`); a scalar by its method's return, where the parameter is a generic protocol
  (`math.floor(x)` is an `int` for a `float`, by `float.__floor__`); and a function by its declared
  return, where the parameter is a `Callable[..., _T]` (`functools.partial(helper, 1)` is a
  `functools.partial[str]`). Two arguments binding one differently leave the call alone
  (`itertools.chain(names, ids)`), as does unpacking `*args` or `**kwargs`. At module level, where
  an annotation is evaluated when the module runs, a class some supported Python can't subscript at
  run time is quoted (`counter: "itertools.count[int]"`), unless the module has
  `from __future__ import annotations`;
- a generic standard-library class's own attribute or property, by the receiver's type arguments:
  `m.string` on an `re.Match[str]` is a `str`, `p.pattern` on an `re.Pattern[bytes]` a `bytes`;
- `open(path, mode)` (or `io.open`), by its literal mode (`r` when there's none): a text mode gives
  an `io.TextIOWrapper`, a binary one an `io.BufferedReader` to read, an `io.BufferedWriter` to
  write, and an `io.BufferedRandom` for both (`+`). Not unbuffered (`buffering`, which gives an
  `io.FileIO`), with an `opener`, or when the module binds `open` itself;
- `x = None`, when every later binding of `x` in the function has one certain type `T` (and nothing
  else writes it, nor reads it from a function or lambda inside, which would see `T | None` where a
  checker otherwise sees what `x` was narrowed to): `T | None`;
- a call to an unannotated function (or method) of the module, when every `return` it has gives one
  type and it can't fall off its end: that type, certain for a function and a guess for a method (a
  subclass may override it); a function whose `return`s are themselves guesses makes its calls
  guesses too. Chains (`f` returns `g()`) are followed, a few links deep. With the CLI, a module
  function in another checked file types its calls the same way, imported as a declared one is (and
  as long as the file can name its type): the files are checked callees first, and files calling
  each other's functions are checked again, up to 3 more times, while that types more;
- with `--unsafe-fixes`, an unannotated instance attribute (`self.x`, or `x` on any value typed as
  its class), when every `self.x = value` in the class's own methods gives one known type (numbers
  widen to the widest: `int`, then `float`): that type. A guess, since a subclass or outside code
  may assign it too; an attribute the class body binds, stored any other way (`+=`, an unpacking,
  `del`, a nested function's `self.x = ...`), or assigned a local bound more than once, is left
  alone;
- an attribute, property or method of a class another checked file defines, its type imported as a
  declared return's is (the CLI only: the plugins see one file at a time);
- with `--unsafe-fixes`, an empty container (`[]`, `{}`, `set()`, `list()`, `dict()`) the function
  then only adds to, every addition typed alike (`append`, `insert`, `add`, `setdefault`,
  `x[k] = v`): `list[T]`, `set[T]` or `dict[K, V]`. A guess, since something else could add to it;
  any use that could (`extend`, `update`, passing it to another function, aliasing it, a nested
  function) leaves it alone;
- a value computed from such: `a if c else b` when both sides agree; arithmetic on builtin scalars
  (`n + 1`, `n / 2`, `"x" * n`, `"%s" % n`; never `**`, whose result can change type); a list, set
  or dict comprehension whose elements are known; `sorted`, `list`, `set`, `frozenset` or `tuple` of
  something whose elements are; and `await` of a call to one of the module's `async def`s.

A loop's target (LVA002) and an unpacking's names (LVA001) are declared instead, on a line of their
own before the statement: `for k, v in ages.items():` with `ages: dict[str, int]` gets `k: str` and
`v: int` above it. The target's type comes from what's iterated: a `range`, `enumerate` and `zip` of
known things, a `dict`'s `.keys()`/`.values()`/`.items()`, or any container whose type is known; an
unpacking splits a tuple type (`a, b = pair`, `pair: tuple[int, str]`) over its names. `enumerate`
and `zip` type each part of the target on its own: `for i, x in enumerate(xs)` declares `i: int`
whatever `xs` is, and a guess about `xs` makes only `x`'s fix one. Keywords that don't change what
they yield are allowed (`enumerate`'s `start=`, `zip`'s `strict=`, `sorted`'s `key=` and
`reverse=`); a starred argument (`zip(*rows)`) isn't.

`with open(path, "rb") as f:` declares `f: io.BufferedReader` before the statement, the file object
being its own context manager.

A type the module can't name yet gets an import. One it already has is reused (with `import io`,
`io.BufferedReader`); otherwise `from io import BufferedReader` is added after the module's
docstring and its leading imports (below a shebang or coding line when it has neither), or
`import io` if `BufferedReader` is a name the module binds. A standard-library type's import never
goes under `if TYPE_CHECKING:`.

A type another checked file declares (`get_handle() -> IOHandles[str]`) names what that file imports
or defines; a name the calling file doesn't have is imported where the type's file has it from,
under `if TYPE_CHECKING:` (into the module's first top-level one, or a new one after its imports,
with `from typing import TYPE_CHECKING` if it must be), so the import can't make an import cycle at
run time. A name the file already imports, under any name and even for type checking alone, is
reused; a module-level annotation using one imported for type checking alone is quoted
(`top: "IOHandles[str]" = get_handle()`), unless the module has
`from __future__ import annotations`. A generic class another file defines is never written bare.

An added import never binds a name the module binds anywhere, or a builtin's; with no name free,
there's no fix. In a notebook, which has no import block, such a fix is reported but not applied.

LVA012 (opt-in) offers `Final`: around the annotation there (`x: int = 1` becomes
`x: Final[int] = 1`), with LVA001's type for an unannotated name (whose own fix it then replaces),
or bare (`x: Final = f()`) when there's none.

A loop whose target is typed only by `# type: T` (LVA003) gets `name: T` declared before it and the
comment dropped (a type checker would see the name declared twice), when its header is on one line.
A name annotated again with the type it already has (LVA007) loses the repeat: `x: int = 2` becomes
`x = 2` (not a bare `x: int`, and never in a class body).

With `--unsafe-fixes`, LVA008 and LVA010 are fixed too, by rewriting the annotation (`total: float`
only ever given `int`s becomes `total: int`): a guess, since a declared type can be wider on
purpose.

## What a type checker sees

A fix is only as certain as a type checker would find it (`tests/corpus/corpus_suite.py --types`
runs the corpus packages' own checkers after `--fix`), so where a checker sees the value otherwise
than the fix says, the fix is changed, made a guess, or not offered:

- a name bound again later must take every value: `x = 1` then `x = None` declares `x: int | None`
  on a line of its own before the first binding (annotated there, mypy wouldn't narrow it to the
  `int` it's bound to), and `total = 0` then `total += 0.5` declares `total: float` (fix kind
  `rebound`); another type that doesn't fit (`x = 1` then `x = "a"`, a class and its base) leaves it
  untyped. A later value whose type isn't known may be anything, which makes the fix a guess;
- after it's bound again, a name is what it was bound to: certain where that's a member of its
  declared union (`int | None`, then `1`), which every checker narrows it to; a guess otherwise;
- a copy, attribute or subscript of a union, or of anything the function tests (`isinstance(x, C)`,
  `x is None`, `is_c(x)`, an `assert`, a `match`), may be narrowed where it's read: a guess; so is a
  comprehension of a union with a condition (`[c for c in cs if isinstance(c, Column)]`). One of an
  `X | None` (or a filtered comprehension over one) isn't offered at all: code nearly always checks
  it for `None` first, and a checker then takes it for the `X`; nor is a bare `None`; nor is a read
  where a test around it narrows it: in an `if`'s or `while`'s branch, a `match` case, or the rest
  of a block after an `assert` or an `if` that always leaves (`return`, `raise`, ...), for a check
  (`isinstance`, a `TypeGuard`, a `match`) whatever its type, and for a truth test or comparison
  when it's a union;
- an ALL_CAPS module-level name bound to a literal is a constant to pyright, which keeps its
  `Literal` type: `MODE = "r"`'s `str` would widen it. Passed to a call (where a parameter may take
  only some values), it's declared `MODE: Final = "r"`, which keeps the `Literal`: a guess, as
  something may rebind it, and not offered where the module binds it again;
- `self`, and a method declared to return `Self` called on `self` or `cls`, is `Self`, not its class
  (in a subclass, the class isn't `Self`): written as the module already imports `Self`
  (`typing.Self` is Python 3.11's, so no import is added), and not offered without one; a `Self`
  later bound to anything else isn't offered either;
- a generic class is never written bare (`list[Box]`, as `[self]` in `Box` would be; `Box()` guessed
  to construct one): the module's own, another checked file's, or the standard library's
  (`logging.StreamHandler()`), unless every type parameter it has has a default
  (`io.BufferedReader`);
- a declared return that names a type variable, the module's own, one it imports from another
  checked file (`from ._typing import T`, under `if TYPE_CHECKING:` too) or `typing.AnyStr`, depends
  on the arguments: its calls aren't typed;
- a one-parameter generic written with a trailing comma (`list[int,]`, as a formatter splits a long
  one) has the element it would without.

## A type checker's types (`--infer-with`)

`--infer-with basedpyright` (or `ty`, or both: `basedpyright,ty`) asks that type checker what it
infers, for the bindings `--fix` can't type itself. It starts the checker's language server
(`basedpyright-langserver`, or `ty server`, on `PATH` or beside the Python running constricter),
asks it for the inlay hints over each file, and turns a variable's hint into a fix. Every such fix
is a guess (fix kind `checker`), applied with `--unsafe-fixes`: a hint is the type of the value
where the name is bound, which a later binding can widen, and the checker can be wrong about what
the code means. Its guesses feed the rest of the scope as `--fix`'s own do (a copy of a hinted local
is typed too, as a guess).

A hint is used only as an annotation the file can hold:

- `Literal[...]` is widened to its values' types (`Literal[1] | None` is `int | None`,
  `Literal[Color.RED]` is `Color`), and `LiteralString` to `str`;
- anything vague (`Any`, `list[Unknown]`), not an annotation (`Module("os")`, a signature), as deep
  as LVA006 reports or as long a tuple as LVA011 does, or a bare `None`, is dropped;
- every name in it must be a builtin, a name the module binds at its top level (before the binding,
  in a module body), or a class the checker prints bare that `--fix` can import
  (`collections.abc`'s, `Path`, `deque`, `Decimal`, `UUID`, ...: one is added as other fixes add
  theirs). Otherwise nothing says what the name means, and the hint is dropped.

With several checkers, each name takes the first checker's hint, in the order they're named, that
passes the checks above: one checker's `Unknown` falls back to the next's type. They're asked at the
same time, each over its own servers. A checker that works one file at a time (basedpyright) gets up
to four servers (more only repeat each other's work: SQLAlchemy's hints took 20s with one, 11s with
four, 18s with sixteen), as `--jobs` allows, one per 32 files; one that works in parallel itself
(`ty`) gets one. Free servers take the files a few at a time, the biggest first, each always with
its next few asked before its last few are answered. Each server holds its own copy of the program
it checks: about 1.2 GB for SQLAlchemy, 3.4 GB for pandas. `--infer-memory GB` (`infer-memory`) caps
what a checker's servers use together: by default 8 GB, or half the memory available if that's less;
set, never more than is available. One server a checker always gets.

Each server runs behind a small guard process, which passes its input and output through and kills
it (and anything it started: a venv's `basedpyright-langserver` starts `node`) once constricter has
gone, however it went (interrupted, terminated, or killed outright): no server outlives the run,
even one stuck waiting on constricter.

`--fix` repeats with `--infer-with`: a file a round changed is sent to the checker again and fixed
again, as its new annotations change what the checker infers, until a round changes nothing (four at
most). `--diff` shows the first round. A checker that isn't installed, fails, or says nothing at all
for two minutes (it reports its progress as it works: pandas' first answer took basedpyright seven
minutes) stops the run with an error; a notebook, standard input and a file that can't be decoded
aren't sent to it. The checker's own configuration (its `[tool.basedpyright]` or `ty.toml`, its
environment) decides what it infers.

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

## Fix levels

Each fix names the mechanisms that decided it, parts included (`[1, 2]` is a `container` of
`literal`s), by a stable id: `--show-fixes` prints them after the reason (`[container, literal]`),
and `--format=json`'s `fix` object has them as `kinds`.

| Id              | Decided by                                                                          |
| --------------- | ----------------------------------------------------------------------------------- |
| `literal`       | a literal, an f-string, or `not x`                                                  |
| `container`     | a list, set, tuple or dict display whose elements' types agree                      |
| `copy`          | a copy of a local whose type is known                                               |
| `subscript`     | a subscript of a container whose type is known                                      |
| `attribute`     | an attribute of a class the module (or another checked file) defines                |
| `method`        | a method with a fixed or declared return type, on a value whose type is known       |
| `builtin`       | a builtin with a fixed return type (`len`, `str`, ...)                              |
| `call`          | a function that declares its return type (this module's, or another checked file's) |
| `constructor`   | a call to a capitalised name, taken to construct one (a guess)                      |
| `conditional`   | both sides of `a if c else b`                                                       |
| `arithmetic`    | arithmetic on builtin scalars                                                       |
| `comprehension` | a list, set or dict comprehension's elements                                        |
| `builder`       | `sorted`, `list`, `set`, `frozenset` or `tuple` of known elements                   |
| `await`         | `await` of the module's `async def`                                                 |
| `loop`          | what a loop (or `sorted`, `list`, ...) iterates over                                |
| `unpack`        | an unpacking, split over its names                                                  |
| `narrow`        | LVA008's or LVA010's narrower annotation (a guess)                                  |
| `cast`          | `typing.cast(T, x)`: its `T`                                                        |
| `comment`       | LVA003: the loop's own `# type:` comment, as a declaration                          |
| `redundant`     | LVA007: the repeated annotation, dropped                                            |
| `stdlib`        | the standard library's functions, classes and members, from typeshed (`uuid4`)      |
| `open`          | `open(path, mode)`'s file object, by its literal mode (`io.TextIOWrapper`, ...)     |
| `final`         | LVA012's `Final`: around its annotation, or with LVA001's type (`Final[int]`)       |
| `checker`       | a type checker's inferred type, from its inlay hints (`--infer-with`; a guess)      |
| `rebound`       | a name later bound to a wider type: the type every value fits (`int`, then `float`) |
| `optional`      | `x = None`, then only ever a value of one known type `T`: `T \| None`               |
| `filled`        | an empty container, then only what the function adds to it (a guess)                |
| `returned`      | an unannotated function's own `return`s (a method's: a guess)                       |
| `assigned`      | an unannotated instance attribute's every `self.x = value` in its class (a guess)   |

A project chooses which apply, in `[tool.constricter]` or on the command line:

- `fix-select` (`--fix-select KINDS`): offer only fixes every one of whose mechanisms is listed
  (default: all);
- `fix-ignore` (`--fix-ignore KINDS`): never offer a fix any listed mechanism decided;
- `unsafe-fix-select` (`--unsafe-fix-select KINDS`): treat guesses from the listed guessing
  mechanisms (`constructor`, `narrow`) as certain, so plain `--fix` applies them, as ruff's
  `extend-safe-fixes` does. A copy of such a guess is trusted with it.

```toml
[tool.constricter]
fix-ignore = ["arithmetic"]          # never annotate from arithmetic
unsafe-fix-select = ["constructor"]  # this codebase's capitalised calls construct what they name
```

None of them changes what's reported: an offence whose fix isn't offered is still reported, without
a fix. The defaults (every mechanism, nothing trusted) are the plain certain/guess split.
