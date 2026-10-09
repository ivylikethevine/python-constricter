# Changelog

Notable changes, newest first. Each release's full notes are generated from its merged pull requests
(grouped by `.github/release.yml`) on its
[GitHub release](https://github.com/ivylikethevine/python-constricter/releases).

## Unreleased

- `python -m constricter.trace` records a type for each binding, not each function: what a name
  holds as the statement binding it ends, followed line by line (`sys.monitoring`; `sys.settrace`
  before Python 3.12). `--infer-from` so types a `for` loop's target, a name bound in a loop and one
  bound again, and a local taken from an attribute of `self` that a class with no base stores only
  unannotated parameters in. A parameter the function gives a default (but `None`), binds again,
  tests by a call or matches is no longer taken for untyped: a checker types what's read of it. The
  trace file's format changes (version 2: each file's `bindings`, by line and name): trace again. A
  class defined in another is spelled (`Outer.Inner`), and a generic class's instance has its
  arguments where it was made with them (`Box[int]()`) or is a builtin container of its own type
  variables (`class Stack(list[T])`); no value's own code runs to spell it (a `__getattr__`, a
  property). A pytest process the run starts is recorded too (pytest-xdist's workers:
  `python -m constricter.trace -m pytest -n auto`), by a plugin the run names in `PYTEST_PLUGINS`.
  The recorder is `constricter.recording`. On pandas's `tests/frame/methods`: 148 fixes from 128,
  the traced tests taking 12.8s from 26.8s (9.4s untraced); with their whole suites traced
  (`corpus_suite.py --types --trace`), 1,443 fixes on pandas and 179 on SQLAlchemy.
- A class variable a `unittest` test case declares itself has that type, not its value's:
  `maxDiff = 80` under a test case (or a framework's base, which may be one) is declared
  `int | None`, which a type checker holds it to, and `maxDiff = None` is too, where it had no fix.
  And a plain class's variable is typed by what the standard library gives its value, as the module
  names it (`pattern = re.compile("x")`, `sep = os.sep`, `size = len(NAMES)`): a guess (`member`),
  as one bound to a literal is; another file reading it writes the type by its own imports, or one
  added for type checking. On Django: 40 more variables, and 12 more of what reads them.
- A read of an `X | None` has a fix where nothing in its function narrows it: neither a test nor a
  store of what's read, or of what that's read of. Its declared type, a guess
  (`conn: Connection | None = self.conn`): what a type checker takes it for there. One the function
  tests or stores still has none.
- A loop over `os.walk(top)` is typed by `top`: `root: str`, `dirs: list[str]`, `files: list[str]`
  where it's a `str` or a `pathlib` path, `bytes` where it's a `bytes`. And `iter(xs)` bound to a
  name is an `Iterator` of what a loop over `xs` binds (`it: Iterator[str] = iter(names)`), imported
  from `collections.abc` where the module doesn't name it.
- `--fix` types more of what earlier items left (all in [FIXES.md](FIXES.md)): what's read of a name
  bound to `capsys.readouterr()`, a class's `parametrize` and a fixture's `params`; a `with` target
  of another checked file's `@contextmanager` function (by what it declares or yields) or class, of
  `os.fdopen`, `tokenize.open`, `shelve.open` (from `vague` 0) and `assertLogs`;
  `asyncio.ensure_future`, and `await` of an `async def` declaring no return, by its `return`s; a
  lambda by what its calls pass it, a module's or a plain class's callable alias, and
  `Callable[[A, B], R]` where a function's parameters are positional and every call passes them so;
  a class under a package that declares no types (django's `TestCase`), under two library classes,
  or under a generic library class given its arguments; an empty container by the parameter it's
  passed to, or filled under another file's class; and a checked file's overloads through its
  aliases, protocols and type variables, on its methods, and called through its module. On pydantic:
  one more certain fix, none lost. The standard-library tables change (`assertLogs`'s private
  classes, `ensure_future`'s future-bounded parameter): regenerate them.
- `--fix --show-fixes` lists the fixes it made, after what it left: `fixed 'x': ...` as text, and in
  `--format=json` (where every entry now says whether it's `fixed`) one entry for each, on the line
  it had before any fix. Without `--show-fixes` a `--fix` run's JSON lists what's left, as it did.
- A widening declared on a line of its own (`row: Any  # constricter: auto`, before a loop, an
  unpacking or a `with`) is replaced as an assignment's is: once the statement types the name, and
  nothing binds it again, it's reported as LVA005 with that type as its fix, which drops the mark.
- A module imported for type checking alone spells its types as one imported to run does: a name
  bound to `core_schema.CoreSchema`, then to `CoreSchema`, is one type's, where a second pass of
  `fix-widen`'s `unions` declared it `CoreSchema | core_schema.CoreSchema`.
- `fix-widen`'s two kinds of call, and `vague`, type what a loop, an unpacking or a `with` binds
  too, each name declared on a marked line of its own before the statement
  (`for key, row in obj.rows():`, `a, b = helper()`, `with obj.open() as f:`); and `untyped-calls`
  takes a call of another checked file's function that declares no return (`u.helper()`), which was
  `unknown-calls`'. On pydantic, `--fix` with the calls' kinds marks 519 of 3,956 bindings (13.1%),
  from 325; with every kind and `--unsafe-fixes`, 773 from 507. basedpyright finds two more errors,
  of one loop's target a `TypeIs` then narrows.
- `fix-widen` has two more kinds, for a function's name bound to a call `--fix` has no type for,
  each `Any`, marked: `untyped-calls` (a call of the module's own function or method that declares
  no return, `x = helper()`, `x = self.load()`: what mypy takes it for already) and `unknown-calls`
  (any other: `x = obj.method()`, `x = module.func()`), whatever the name is bound to later. On
  pydantic, `--fix` with both marks 325 of 3,956 bindings (8.2%, all `unknown-calls`); basedpyright
  finds two errors fewer and two more.
- `fix-widen` (`--fix-widen KINDS`) names the wider types `--fix` may write where a value has no
  type it can work out, or none it may write, each a fix kind of its own, off unless listed (`all`:
  every one): `untyped-parameters` (`Any` for what comes of a parameter no annotation types:
  `x = param`, `y = param.read()`), `empty-containers` (`list[Any]` for an empty one nothing fills),
  `mixed-containers` (`list[Any]`, `tuple[Any, ...]`, `dict[str, Any]` for a display of mixed or
  unknown elements), and, as guesses, `unions` (`int | str` for a name bound to two or three types)
  and `vague` (a known type vaguer than `vague` allows, written anyway). Every statement a widening
  writes ends with `# constricter: auto`: LVA005 passes over it, `--coverage` counts it apart
  (`3/4 typed (75.0%), 1 widened`, and `widened` in its JSON), and once its value's type is known
  it's reported as LVA005 with that type as its fix, which drops the mark. On SQLAlchemy all five
  annotate 662 bindings (4.5%); basedpyright finds no error in a file under a rule it hadn't one
  for, and 22 fewer, which the `Any`s hide.
- With `--infer-with`, `ty` and pyrefly get up to four servers, as basedpyright does: a hinted check
  of pandas takes 21s with `ty` (from 36s with one) and 18s with pyrefly (from 69s). Each checker's
  servers are counted by its own memory, where all were by basedpyright's.
- `--fix --unsafe-fixes` no longer types what's read of a name that an arm of an `if`, a `try` or a
  `match` leaves with no known type, whatever another arm binds it to (`levels = index.multi()`,
  `else: levels = ["a"]`, then `for lvl in levels`): it may hold either. And a type alias of a union
  (`Key = Union[int, str]`, the module's or another checked file's) is narrowed as the union it
  names: a copy under a test of it, or of an alias of an `X | None`, has no fix, and one bound again
  to a member of it is that member, certainly (`dtype = cast(ExtensionDtype, dtype)`, of a
  `DtypeObj`). A union bound again to a value of no known type has no type until its branch ends,
  where a copy was declared the whole union (`original_execution_options = execution_options`).
  These were the causes of two of pandas's new type errors after `--fix --unsafe-fixes`, and of
  sqlalchemy's two. On the seven corpora, 44,858 guesses from 44,942, and 64,371 certain fixes from
  64,373.
- `--fix --unsafe-fixes` adds fewer type errors, by what the corpus packages' own checkers found
  after it (pandas's 42 new errors are 7, sqlalchemy's 3 are 2, and pydantic's 9 left are its
  environment's). What an unannotated function's `return`s give, which a checker took for anything,
  has no fix where declaring it makes an error of what its function does with the name: a union of
  which an attribute or an item is taken where no test narrows it (`opt.cb`, of an `Option | None`),
  and a class of the module's of which an attribute it hasn't is taken (`cfg.verbose`, where the
  attributes are set from outside the class). A name of no known type before a branch that binds it
  to a known one (a parameter, in `if flag: x = float(x)`) has none past the branch, where it was a
  guess of the branch's; and a name bound in one arm of an `if`, `try` or `match` to a known type
  and in another to one that isn't has no fix. A union isn't split over several names
  (`for name, length in parts`, of a `list[list[str | int]]`); a display of an attribute narrowed
  where it's written (`[self.offset]` under `isinstance`) has no fix, as one of a name had none; an
  unannotated function returning a class its own body imports or defines types no call (the caller's
  file couldn't name it); and an attribute a class above stores too isn't typed by the subclass's
  assignments. On the seven corpora, 44,942 guesses from 47,918.
- A function called through a module that imports it in turn is typed by its declared return, as one
  imported by name is: `pd.array(...)` after `import pandas as pd`, by the `array` that
  `pandas/__init__.py` imports from `pandas.core.api` (an `ExtensionArray`, imported for type
  checking). On the seven corpora, 64,373 certain fixes from 62,540 (pandas: 16,826 from 16,010).
- A check with `--jobs` keeps its worker processes for all of its rounds, where each round started
  new ones: a file checked again (its callers typing its parameters) is checked by the worker that
  has its tree and how its first check ended, as one process does it. The standard library checks in
  12.9s from 14.4s on 16 CPUs, and a parallel check's findings are now exactly one process's: two of
  pandas's 77,931 differed (a type alias's fix, a guess in one and certain in the other).
- `--fix --unsafe-fixes` guesses wrong less often, by what packages outside the corpora showed: a
  name bound to `TypeAliasType(...)` is a type, as one bound to `TypeVar(...)` is, and has no fix
  (altair: 128 new type errors to 4); an empty container isn't typed by a name its function tests
  where that name is what's added (`xs.append(d)` under `isinstance(d, C)` holds the narrowed type);
  a comprehension that keeps a name only `if x is not None` holds no `None`, so
  `min([v for v in values if v is not None])` is a `str`, not a `str | None`; and a call typed by a
  read that a test around it narrows (`copy.deepcopy(x)` in `if x:`) has no fix, where it was a
  guess of the declared type. A comprehension or a generator that keeps a name only if
  `isinstance(x, C)` holds `C`s (`next(t for t in types if isinstance(t, ObjectType))` is an
  `ObjectType`; several classes, or a variable, leave it untyped). A name bound again to a call on
  itself whose type isn't known (`item = proper(item)`) has no fix: of 37 such guesses on four
  packages 7 were wrong, of the 542 other rebound ones 16. And a later `with` or `for` target of a
  known type holds the first binding's fix to it: `with open(path) as f` then
  `with open(path, "rb") as f` are two types, and `f` has none. A capitalised name another checked
  file binds by assignment (`F = duckdb.FunctionExpression`) is a value: `F(...)` is no longer taken
  to construct an `F` (narwhals: 8 new errors to 1). And a display holding a name narrowed where
  it's written (`studies = [study]` under `isinstance(study, Study)`) has no fix.
- `--infer-with` remembers a file its checker's server hung on, and leaves it without hints from the
  start of the next run, where it waited out the server's silence twice and restarted it each time
  (four minutes of a basedpyright-hinted fix of pandas, 439s to 198s). It's remembered by the file's
  text and the checker's executable, in the cache: a changed file, or a new version of the checker,
  is asked again.
- The command leaves as soon as it has written its output, not by the interpreter's own exit, which
  freed every parsed file and the index an object at a time: 15 of the 67 seconds of a check of
  pandas in one process. With `--jobs=1` on 16 CPUs the standard library checks in 55s, from 74s
  (67s at 0.3.3), and pandas in 60s, from 66s (55s at 0.3.3). The `constricter` script is
  `constricter.__main__:run` now; `constricter.cli.command.main` still returns its status.
- A check is a little faster in one process: whether a fix's type is too vague to write is worked
  out once for each type, not for each binding, and the empty containers a class's attributes start
  as once for the class, not for each of its methods. The same offences and fixes.
- `--fix` no longer writes these, each a type error on a package outside the corpora: `ClassVar[T]`
  or `Final[T]` for a copy of an attribute declared so (it's a `T`; a bare `Final` has no fix);
  `bytes` for `data[0]` (an `int`; an index of unknown type has none); `typing.Self` where the file
  imports `typing_extensions` too, under `if TYPE_CHECKING:` or not (`te.Self`, which older Pythons
  have); a type variable defined under `if TYPE_CHECKING:` (it's found as one now, and never written
  unbound); `V | None` for a `TypedDict`'s `d.get("key")` where the key is required (it's `V`:
  `total=False`, `Required` and `NotRequired` are read now, a base's keys by the base's own); and
  `list[T | None]` for `[a] if a else []`, where `a` is narrowed. A comprehension filtered by
  `isinstance` of its own elements is a guess whatever their type, as one over a union was.
- One `--fix --unsafe-fixes` pass leaves nothing for a second in three more cases: a receiver typed
  by an alias whose import the fix adds (`NDArray`, by `np.array`) has its methods as the file's own
  import names them (`np.typing.NDArray`); a class the package a fix imports re-exports (`ds.Range`,
  by `from pkg import structures as ds`) has its members before any annotation names it; and so has
  one only a quoted annotation names (`study: "optuna.Study"`).
- `--infer-with` no longer crashes on a hint naming a class from a file no import can name
  (`v3.0.0.c.py`): the hint has no fix.
- A check with `--jobs` is faster where files import much. Each worker is sent the index, once, and
  works out what its own files import from the others, which the main process did for every file
  while the workers waited; the index keeps what its modules' classes are named by, their lines of
  bases and their members, which each file asked again; and a file passes over the classes whose
  members it takes none of. On 16 CPUs pandas checks in 11s from 41s (22s at 0.3.3), the standard
  library in 15s from 18.7s, with the same offences and fixes.
- `--fix` adds fewer type errors still: a call of an unannotated function whose `return`s give an
  `X | None` is a guess now (a checker takes it for anything, and what's done with it unchecked for
  `None` is an error only once declared); a name a `# type: ignore` line of its function uses has no
  fix (declared, it leaves the comment nothing to excuse); and a call of another file's overloaded
  function has none where a signature of it returns a type whose import the file can't take
  (`types.ModuleType`, in a file with a local `types`).
- `--fix` adds fewer type errors of its own: `self.__class__` is `type(self)`, a `type[Self]` in a
  method that says `Self` (`c = self.__class__.__new__(self.__class__)` is a `Self`, not the class
  its `return c` then fails as); and a builtin class passed where an installed signature takes a
  bounded `type[T]` (`np.zeros(n, dtype=bool)`) no longer binds `T`, which a numpy scalar alone
  fits: it has no fix, where it was a `np.dtype[bool]` no checker accepts.
- One `--fix --unsafe-fixes` pass leaves a second nothing to change again, on every corpus: a `with`
  target is typed by its manager's `__enter__`'s `return`s the first time, wherever the class is; a
  name bound to `None` then `total += guess` is `T | None` as a guess; a file fixed and checked
  again (its callers typing its parameters, or files calling each other) keeps the imports its first
  check wrote, for itself and for the files reading its types; and a class that binds a name itself
  (a `cached_property`) no longer reads a base's annotation of it.
- `--fix` picks a checked file's overload by the checked files' own classes: a parameter typed as
  nothing but such classes, or as an iterable of them, takes an argument by its class's bases, so
  `concat([df, df])` is a `DataFrame` where another overload takes `Series`.
- `--fix` types an attribute read off an installed method's call whose return no file can name:
  `out = capsys.readouterr().out` is a `str` (pytest's `CaptureResult` is private), by the
  receiver's type arguments. An installed class defined under `if TYPE_CHECKING:` is read too.
- `--fix` types what `with mock.patch(target) as m:` binds (and `patch.object`), given no `new`: a
  `MagicMock | AsyncMock`, as typeshed declares it.
- `--fix` types a lambda bound to a name by its body, where that rests on no name of its own or its
  function's: `first = lambda: 1` is a `Callable[[], int]`.
- `--fix` follows another checked file's class of several bases to the one library class its lines
  reach (`self.id()` under `class Tests(Case)`, `Case(Mixin, unittest.TestCase)` in another file).
- An empty container of `self` is typed by what the module's classes under its own add to it too
  (`self.items = []` in a base, `self.items.append(x)` in a subclass), and read as that on them.
- A check lists a module's functions by the names a file writes, not every function of every module
  it imports; and a file checked a second time, its functions' parameters typed by their callers,
  starts from where its first check ended, checking again only those functions and what their new
  types reach (not with `--fix`, whose text has changed by then).
- `--fix` types a function or a bound method bound to a name in a function as a `Callable[..., R]`,
  by what its call gives whatever it's passed: `dump = json.dumps` is a `Callable[..., str]`,
  `grow = item.grow` a `Callable[..., int]` (a new fix kind, `callable`).
- `--fix` types `await` of a call to a checked file's `async def` method (`await self.fetch()`, its
  class's own or a base's, in the module or another checked file) and to another checked file's
  `async def` function (`await load(url)`, however it's imported).
- `--fix` types a classmethod or staticmethod called on a class under another checked file's
  (`Sub.make()`, `make` its imported base's: a `Sub`, where it returns `Self`).
- An empty container bound to a local is still typed by what's added to it, where every use of that
  local only reads it (`items = self.items`, then `len(items)`).
- `--fix` types `await` of a generic standard-library class's coroutine by its receiver
  (`item = await queue.get()` on an `asyncio.Queue[Item]` is an `Item`).
- `--fix` binds a bound type variable to its argument's type where the function has one signature:
  `contextlib.closing(conn)` is a `contextlib.closing[Conn]`, `dataclasses.replace(point)` a
  `Point`, `ast.copy_location(node, old)` its `node`'s type, and
  `io.BufferedReader(io.FileIO(path))` an `io.BufferedReader[io.FileIO]`. And a `with` target by its
  context manager's base (`with contextlib.closing(sock) as s` declares `s: socket.socket`, by
  `AbstractContextManager[T, None]`).
- With `--unsafe-fixes`, `--fix` types a call of another checked file's unannotated method by its
  `return`s, as it does such a function's: `path = self.mktemp()` under an imported base whose
  `mktemp` returns a string, `tool.name()` on an imported class's instance. A file is checked after
  the modules whose classes' methods it may call so.
- `--fix` looks past another checked file's mixin for a member it doesn't bind: `self.id()` under
  `class Tests(Mixin, unittest.TestCase)` is a `str`, where `Mixin` and its bases, in other files,
  end at no library class.
- `--fix` types a `TypedDict`'s key read by a literal, on a value typed as the class:
  `movie["year"]` by the key's declared type (less `Required`, `NotRequired` or `ReadOnly`),
  `movie.get("year")` as that or `None`, and a loop over `movie["tags"]` by its elements. A class
  under `TypedDict` or under one of its module's, with its bases' keys, in the module, another
  checked file or an installed package that declares its types (`schema["ref"]` on a pydantic-core
  `ModelSchema`): 31 more fixes on pydantic.
- `--fix` types an attribute a class takes from a base: `self.limit` under a class whose base
  declares `limit: int`, by an annotation, a `self.x: T` or a `@property`, through the module's own
  classes and then another checked file's, as an inherited method is found; `cls.limit` too. Not
  where a class before the base binds the name another way, nor past a generic base.
- A type too vague to write (`vague`) is still its name's: `fields = schema.fields()`, declared a
  `dict[str, Any]`, has no fix, and `for name in fields` now declares `name: str`. By a function's,
  a method's or a property's declared return, `typing.cast` and a callable's call; a part of an
  unpacked call too. 13 more fixes on pydantic, and no new basedpyright error with these three.
- `--fix` types more builtin methods: an `int`'s and a `float`'s with one return (`n.bit_length()`,
  `n.to_bytes(2, "big")`, `x.is_integer()`), a `list`'s and a `tuple`'s `count` and `index`, and a
  `set`'s and a `frozenset`'s `issubset`, `issuperset` and `isdisjoint` (a `bool`), `difference` and
  `intersection` (the receiver's own type).
- `--fix` no longer types a standard-library call by a declaration only some supported Pythons have,
  where the others declare it another way: `importlib.metadata.entry_points()`, overloaded before
  3.12 (a `SelectableGroups` then, where the file couldn't name `EntryPoints`),
  `handler.filter(record)` (a `bool` before 3.12, a `bool | LogRecord` since) and
  `zipimporter.get_resource_reader(...)` (a `ZipReader | None` before 3.14) have no fix now.
- `--fix` resolves a function's own imports: with `import os` or `from inspect import signature` in
  its body, `os.getcwd()` is a `str` and `signature(f)` an `inspect.Signature` there, and in the
  functions inside it. Not a name the function binds another way too (`try: import x` /
  `except ImportError: x = None`), nor one two of its imports bind to different things. A type of a
  module only functions import is imported under `if TYPE_CHECKING:`: the module may not be there to
  import when the file is (another platform's `pwd`).
- `--fix` names a type by the import the module has for it under a top-level `if TYPE_CHECKING:`
  (`sig: Signature`, quoted in a module body), where it added `import inspect` and wrote
  `inspect.Signature` before.
- `--fix` types a standard-library class's attribute or property whose type has classes' own
  arguments, and what's read of it: `sig.parameters` on an `inspect.Signature` is a
  `MappingProxyType[str, inspect.Parameter]` (so `list(sig.parameters.values())` a
  `list[inspect.Parameter]`), `for stmt in tree.body` declares `stmt: ast.stmt`, `path.parents` is a
  `Sequence[Path]`; such a module variable too (`sys.modules[name]` is a `ModuleType`), and
  `sys._getframe()` (a `types.FrameType`).
- `--fix` types an operator between a standard-library class's instance and another's or a
  builtin's, by its method's signatures in typeshed: `when - start` of two `datetime`s is a
  `timedelta`, `when + span` a `datetime`, `price * 2` a `Decimal`, `span / span` a `float`. Not
  where the right operand's class is under the left's, or isn't the standard library's. And a
  `dict`'s `.keys()` with a `set` of its key type (`allowed & config.keys()` is a `set[str]`).
- `--fix` types a call of a module's `NewType` (`ref = Ref(name)` is a `Ref`), in the module making
  it and in the checked files importing it.
- The trees a run keeps between indexing and checking are capped by the machine's memory: a quarter
  of it (of a container's limit, where that's lower), and 1 GB at least, which was the cap on every
  machine. Windows, which doesn't say how much it has, keeps 1 GB.
- `--fix` types a standard-library method declared to return a type naming `Self` by its receiver:
  `for child in path.iterdir()` declares `child: Path`, `list(path.glob("*"))` is a `list[Path]`
  (`glob` an `Iterator[Path]`, on every Python), `names.copy()` on a `collections.deque[str]` a
  `collections.deque[str]`.
- `--fix` types `enumerate(xs)`, `zip(xs, ys)`, `map(f, xs)` and `reversed(xs)` bound to a name, by
  what a loop over each binds (`enumerate[str]`, `zip[tuple[str, int]]`, `map[int]`), quoted at
  module level where no Python can subscript the class at run time; and a loop over, or an unpacking
  of, a name holding one.
- `--fix` types `path.open(mode)` on a `pathlib` path as it types `open(path, mode)`, by its literal
  mode, and so a `with path.open() as f:`'s target and `f.read()`.
- `--fix` types a loop over an `X | None` as one over the `X`.
- `--fix` types a loop over a standard-library class's instance by its `__iter__` in typeshed:
  `for line in open(path)` declares `line: str`, a loop over a binary file `bytes`, over an
  `itertools.chain[int]` or a `collections.deque[int]` an `int`, over a `tarfile.TarFile` a
  `tarfile.TarInfo`; and what's built from one (`list(file)`, `[line.strip() for line in file]`).
- `--fix` types what a generic standard-library class inherits with one type: `f.read()` and
  `f.readlines()` on the `io.TextIOWrapper` or `io.BufferedReader` that `open` gives, `f.closed`,
  `task.done()` on an `asyncio.Task`.
- `--fix` types a member of an `X | None` as `X`'s (`m = re.match(...)`, then `m.start()` and
  `m.string`): a type checker has narrowed the value there, or reports the access. Not a member
  `None` has too, nor one of a union of more types.
- `--fix` types `x.__class__` as `type(x)` is typed (`type[C]`), and a class's `__name__`,
  `__qualname__` and `__module__` read of either as a `str`, whatever `x` is (`type(x).__name__`,
  `self.__class__.__name__`).
- `--fix` types what a function reads of the names its module binds once, at its top level: with
  `LIMIT = 10` and `NAMES = ["a"]` there, `n = LIMIT + 1` is an `int` and `for name in NAMES` a loop
  over `str`s, in every function. By the name's annotation (a `Final[T]`'s `T`, a bare `Final`'s
  value's type) or its one value's type, a guess where that is one. Not a name anything in the
  module binds again (a parameter or a local of that name, a `global` statement's).
- `--fix` types more operators on builtin values: an integer's `**` by a literal (`2 ** 32 - 1`), a
  `float`'s by an integer, `<<`, `>>`, `&`, `|` and `^` of integers (`1 << 30`; of two `bool`s, a
  `bool`), an integer times a `str`, `bytes` or `list` (`3 * "ab"`), a tuple's `+` and `*`
  (`pair + (n,)` is a `tuple[int, str, int]`, `(0,) * n` a `tuple[int, ...]`), a `set`'s or
  `frozenset`'s `|`, `&`, `-` and `^` with another of its type, and a `dict`'s `|`.
- `--fix` types a fixed-length tuple's part by a literal index (`pair[0]`, `pair[-1]`), a slice of a
  `tuple[T, ...]`, `a or []` and `a if c else {}` by `a`'s `list` or `dict` (`a if a else []` is
  never `None`), `sorted(xs, key=..., reverse=True)`, `min` and `max` of an `int` and a `float` (a
  `float`), a module's own `__file__` and `__name__` (`os.path.dirname(__file__)` is a `str`),
  `await` of a task or a future held in a name (`done = await task`), and, from `vague` 1,
  `object()`.
- `--fix --unsafe-fixes` types more class variables: a class under `Generic[T]`, `abc.ABC` or a
  plain class's subscript (`class Wide(Box[int])`) is plain, where none of them made one before, nor
  any class above it; and a variable the module stores is typed where every store keeps its type
  (`closed = False` with `self.closed = True`, `count = 0` with `self.count += 1`).
- `--fix` types what a coroutine's call gives the standard library's task and run functions:
  `asyncio.create_task(fetch(url))` is an `asyncio.Task[bytes]` where `fetch` declares `bytes`
  (`loop.create_task` and a task group's too), `asyncio.gather(a(), b())` an
  `asyncio.Future[tuple[A, B]]`, and `asyncio.run(main())` and `loop.run_until_complete(main())`
  what `main` declares. And `await` of a future or a task (`done = await asyncio.gather(a(), b())`)
  and of a coroutine its arguments decide (`asyncio.wait_for`, `asyncio.sleep(1, result)`,
  `asyncio.open_connection`, whose reader and writer an unpacking takes).
- `--fix` types `await` of a standard-library coroutine's call, and an `async with`'s target by a
  standard-library manager's `__aenter__`: `line = await reader.readline()` is a `bytes`,
  `proc = await asyncio.create_subprocess_exec(...)` an `asyncio.subprocess.Process`, and
  `async with asyncio.TaskGroup() as group:` an `asyncio.TaskGroup`. The tables hold what awaiting
  each `async def` with one declared return gives (`awaited`): not a generic class's (`Queue.get`),
  nor one its arguments decide (`asyncio.gather`, `asyncio.wait_for`).
- Faster, with the same output: a value's inferred type is kept until its scope types another name
  (it's asked for again as a guess, and as part of the next value), a module's bound names and class
  tables are read once for the index and the check, an installed package is looked for on disk once
  for all its modules, and its signatures' annotations are parsed once each. About 8% off a check of
  97 of the standard library's test files, and 11% off one of pandas's test directories.
- `--fix` types what a class takes from a standard-library class through another checked file's (or
  a typed installed package's): under a project's own `class Case(unittest.TestCase)`, defined in
  another file, `name = self.id()` is a `str` and `with self.assertRaises(ValueError) as cm:` an
  `_AssertRaisesContext[ValueError]`. Where each class on the way has one base, and none binds the
  name.
- `--fix` types more of the standard library's context managers, and what they construct: a class
  whose `__init__` overloads declare its instance (`subprocess.Popen(cmd, text=True)` is a
  `subprocess.Popen[str]`, `with tempfile.TemporaryDirectory() as d:` a `str`,
  `with warnings.catch_warnings(record=True) as caught:` a `list[warnings.WarningMessage]`), a test
  case's `with self.assertRaises(ValueError) as cm:` (an `_AssertRaisesContext[ValueError]`, and
  `cm.exception` a `ValueError`: a class passed as an argument binds a `type[_E]`, and a class of
  the module's takes a library base's method whose arguments decide it), `assertWarns`,
  `tempfile.NamedTemporaryFile` and `tarfile.open`. The three classes among them that typeshed keeps
  private are written by their private names. 507 more fixes on 97 of the standard library's test
  files (6,109 to 6,616).
- `python -m constricter.trace -m pytest` (or a script) records the types a run binds each
  function's locals to, and `--fix --unsafe-fixes --infer-from FILE` (`infer-from` in
  `[tool.constricter]`) takes them for the bindings `--fix` can't type itself, as a type checker's
  hints are taken: guesses (fix kind `traced`), for a local bound once to a value taken from an
  unannotated parameter, a class the file doesn't name imported under `if TYPE_CHECKING:`. A file is
  matched by its SHA-256, so one edited since the run has none. See
  [FIXES.md](FIXES.md#a-traced-runs-types---infer-from).
- `--fix` types a call on a value whose class the same run imports for type checking: with
  `df = series.to_frame()` typed `DataFrame` by an import the fix adds, `df.shift()` is typed on the
  first pass, not the second. `tests/corpus/corpus_fix.py` lists each fix a second pass still makes.
- `--fix --unsafe-fixes` types a test's parameter named as one of pytest's own fixtures, read from
  pytest as installed where a checked file imports it: `capsys` is a `pytest.CaptureFixture[str]`,
  `monkeypatch` a `pytest.MonkeyPatch`, and `text = caplog.text` a `str`. Each `conftest.py` outside
  a package is looked in by where it is, the nearest first, not only where it's the one checked file
  of that name (a fixture of one of several by its declared return alone). And a fixture's class the
  test file doesn't import has its members: `copy = float_frame.copy()` is typed where only the
  `conftest.py` imports `Frame`. Guesses (fix kind `fixture`).
- `--fix` reads an installed package's private twin through it (`pytest`'s classes, defined in
  `_pytest`), types the members of a class named through a module that re-exports it
  (`pytest.LogCaptureFixture`, `pkg.Row`), and writes a type through such a module where the file
  imports it (`typed.Thing` after `import typed`) before adding an import for type checking.
- Fixed: with an installed package's types read, a module name two checked files share was no longer
  known to be shared, so one's fixtures could type the other's tests.
- `--fix` types a call to a checked file's function defined with `@overload` by the overload its
  arguments match, as an installed package's is: `load(path, raw=True)` is a `bytes` where
  `raw: Literal[True]` returns one. Only where the arguments decide it, and no overload returns a
  type variable or a generic class without its arguments; a parameter typed as a checked file's
  class or alias takes any argument, so it decides nothing.
- `--fix` resolves a standard-library class named through an import for type checking that the same
  run adds: a fixture's `Path`, joined by `/`, is typed on the first pass, not the second.
- `--fix --unsafe-fixes` takes a test's fixtures from a `conftest.py` outside any package too (most
  projects' `tests/conftest.py`), for the tests beside it and under it, where it's the only checked
  file of that name; and pytest's own `tmp_path` is a `Path`. Guesses (fix kind `fixture`).
- `--fix` types a `pathlib` path joined by `/`: `root / "data"` is `root`'s class (`Path`), with a
  `str` or another path on its right.
- `--fix --unsafe-fixes` types an instance attribute bound to an empty container by what its class's
  own methods add to it: `self.items = []` in `__init__` and `self.items.append(row)` in another
  method make `for item in self.items` a loop over `Row`s. Guesses (fix kinds `assigned` and
  `filled`).
- `--fix --unsafe-fixes`: an empty container is still typed by its fills where it's also an operand
  (`parts + more`), unpacked (`[*parts]`, `f(*parts)`), passed to any `join`, or returned in a tuple
  (`return parts, count`).
- `--fix --unsafe-fixes` types what a test computes from the parameters pytest gives it: one named
  as a fixture its module or a `conftest.py` of a package above it defines, by what the fixture
  returns or yields, and one `@pytest.mark.parametrize` gives literals of one type.
  `def test_copy(float_frame)` types `result = float_frame.copy()`. Guesses (fix kind `fixture`). On
  pandas's `tests/frame`, about 60 more fixes of 4,492 bindings with none.
- `--fix --unsafe-fixes` types a list, set or dict display whose elements' types differ as their
  union: `[1, "a"]` is a `list[int | str]`, `{"k": 1, "j": None}` a `dict[str, int | None]`. Up to
  three types, each a plain name; a guess (fix kind `joined`).
- `--infer-with ty`: a hint showing a generic alias (`NDArray[float64]`) is no longer written as
  ty's edit spells it, the alias's class with the alias's arguments (`np.ndarray[np.float64]`, the
  scalar type where the shape goes). A name the file binds to what the hint shows
  (`from things import Thing as T`) is still used.
- `--infer-with`: a hint is no longer a fix for a name bound again later to a value of another type,
  or of none `--fix` knows (the hint is the first value's type alone), nor a union hint
  (`Option | None`) for a name its function never narrows (`is None`, `isinstance`, its truth),
  which the code uses as one member. Nor one with a union inside it (`dict[str, int | bytes]`), one
  whose `Literal` is a class's own argument (`Reader[Literal["frame"]]`, once widened to
  `Reader[str]`), or one for a name returned from a function whose signature says `Self`. On
  pydantic, 70 fewer fixes of 1,863.
- `--fix --unsafe-fixes` annotates a class's variables under a framework's base that reads no
  annotation in a class body, as a plain class's: `per_page = 20` under django's `models.Model`,
  `template_name = "x.html"` under a view, a form, an admin or a command. Django's classes are built
  in, but its `Choices`, enums whose members a type checker won't have annotated; `fix-plain-bases`
  (`--fix-plain-bases BASES`) lists more: a class by its dotted path, or a package for every class
  in it, `!` before one to leave it out. A listed base counts where a checked file defines it too
  (django's own, decorated or under a metaclass). A check of one file alone now resolves a base
  through any import, not the standard library's alone. On django: 563 more guesses (4,632 fixes to
  5,195).
- `--fix` writes a standard-library function's bare generic return with its type parameters'
  defaults, as a type checker reads it: `ET.SubElement(root, "x")` is an `ET.Element[str]`, as is
  `ET.XML(text)`. It was guessed a constructor, `SubElement`, which isn't a type. A capitalised
  standard-library function the tables can't type (`ET.Comment`, `doctest.DocTestSuite`,
  `turtle.Screen`) is no longer guessed to construct a class: a new table, `functions`, lists them.
- `--infer-with`: a server that says nothing for 120s no longer ends the run. It's restarted, and
  each file it hadn't answered is asked about again alone; a file it hangs on again gets no hints,
  named on standard error
  (`constricter: warning: basedpyright hung on FILE twice: no hints for it`). A checker that hangs
  on more than three files still stops the run.
- What makes a type, not a value, isn't reported, nor counted by `--coverage`: `T = TypeVar("T")`, a
  `ParamSpec`, `TypeVarTuple` or `NewType`, and a functional `NamedTuple`, `TypedDict`, `Enum` or
  `collections.namedtuple`. An annotation there would make a type checker take the name for a
  variable. On pydantic: 83 fewer bindings reported.
- `--fix` splits a value typed as an alias of a tuple (`Pair: TypeAlias = tuple[int, str]`) over an
  unpacking's names, as a named tuple's fields are: the module's own, or another checked file's,
  however it's imported. On pydantic: 5 more certain fixes.
- At `vague` 1 and above, `getattr(obj, name)` is an `Any` (`Any | T` with a default of type `T`),
  and a standard-library function declared to return `Any` alone (`json.loads`, `pickle.loads`) an
  `Any`: the tables now hold those 34 functions' returns. On pydantic at 1: 1,241 certain fixes and
  464 guesses, from 1,188 and 466.
- `vague` (`--vague LEVEL`, `[tool.constricter]`, and both plugins' `constricter-vague`): how vague
  an annotation may be before it's LVA005, and how vague a fix may be. -1, the default, allows no
  `Any`, `object` or generic without its parameters; 0, one inside a type that says the rest
  (`tuple[str, Any]`); N from 1, N + 1 of them, or one alone (`Any`). A function's or method's
  declared return with a vague part now types its calls where the level allows, and a type checker's
  hint is taken the same way. At the default, no fix writes a vague type any more: one did where a
  copy or an element of a vague value was typed (59 fixes on pydantic, 37 of them certain, now
  none). On pydantic: 1,017 certain fixes and 429 guesses at -1, 1,120 and 452 at 0, 1,188 and 466
  at 1; no new basedpyright error at any of them.
- `--fix` declares a module's type alias: `Json = dict[str, "Json"]` becomes
  `Json: TypeAlias = dict[str, "Json"]`, a new fix kind, `alias`. Only a value that can be nothing
  but a type made of others: a subscript of what `typing` or `collections.abc` define
  (`Union[A, B]`, `Callable[..., R]`), of a builtin generic or of a generic class the module names,
  or a union of those, of builtin classes, of classes the checked files define and of `None`; or a
  copy of a name the module declares an alias (`Rows = Table`), so one pass converges; never a bare
  class's alias, a name bound twice, or a name the module binds as a value somewhere. `TypeAlias` is
  named as the module's imports can, else imported from `typing`: certain where the module imports
  the name already or `min-python` is 3.10 or later, a guess otherwise. On pydantic (checked under
  this project's `requires-python`, 3.11): 128 more certain fixes.
- `--fix --unsafe-fixes` annotates a class's variables under a builtin exception or value class too
  (`code = "missing"` under `ValueError`, `strip_whitespace = True` under `str`): such a base is one
  a plain class may have. A variable is left alone where a class above it annotates the name as
  another type (`limit: int | None` above makes `limit: int = 3` an incompatible override), or where
  a builtin base has the name itself (`errno` under `OSError`), across the checked files. On
  pydantic: 162 more guesses.
- `--fix` types a call of a value whose type says what calling it gives: a local, an attribute or
  anything else typed `Callable[..., R]` (`schema = handler(source)`), one typed `type[C]` (`cls()`
  in a classmethod, `type(self)()`, and `cls.__new__(cls)`: `Self` where the method's signature says
  so), and an instance of a class declaring `__call__`, another checked file's too. An unpacking's
  names take a named tuple's fields (`globalns, localns = resolver.namespaces`, declared a
  `NamedTuple` class, the module's own or another checked file's), and a `with` statement's target
  that unpacks is split the same way; a `@contextmanager` method types its `with` target on a
  receiver of a known type, as a function does. A call to a class the checked files define
  constructs it whatever its name's case (`_Definitions()`, a guess as a capitalised call is), and a
  name bound again to a guessed value is that value's type from there on
  (`config = config or Config()`). On pydantic: 51 more certain fixes and 34 more guesses.
- Together, on pydantic: 179 more certain fixes (878 to 1,057) and 196 more guesses (255 to 451),
  375 fewer bindings with no fix (2,042 to 1,667); no new basedpyright error after `--fix` or
  `--fix --unsafe-fixes`, nothing broken, and one pass converges.
- A check of many files is faster: the standard library with its tests (1,867 files) in 108s with
  `--jobs=1` (from 185s) and 35s with `--jobs=0` on 8 cores (from 62s), pydantic in 4.2s (from
  6.0s). What a file passes other files' functions is read from the module's one shared walk, only
  the functions that name one walked; a function is walked for a `yield`, a rebound `self` or a
  shadowed import only where the module has one in it; a caller is checked again only where what it
  imports now returns something else; a function's declared return is read once for every class
  table; a value is asked only of what types its kind (a call, a name, a display); and another
  file's function or class member is written for a file only where the file uses it. The results are
  the same, but for what an unused member's type no longer holds back: a name it would have needed
  imported is free for an import a fix adds (`Final`, `Iterator`: 15 more fixes on the standard
  library).
- `--fix` types an unpacked call whose declared return is a tuple with a vague part
  (`schema, metadata = self.common(...)`, declared `tuple[CoreSchema, dict[str, Any]]`): each name
  whose part isn't vague is declared (`schema: CoreSchema`), for a function or a method, the
  module's own or another checked file's; the call whole still has no fix. A classmethod or
  staticmethod types its calls on an instance too (`self.info(stmt)`), and on a class that takes it
  from a base in the same module (`Sub.make()`, a `Sub` where `make` returns `Self`). On pydantic:
  29 more certain fixes (849 to 878) and 1 more guess, 30 fewer bindings with no fix (2,072 to
  2,042); no new basedpyright error, and one pass converges.
- `--fix` types more of what a value's parts decide. An unpacking, name by name: a display of as
  many values gives each name its own value's type (`a, b = x, 1` declares `b: int` whatever `x`
  is), anything else its elements' (`a, b = s.split(",")`, `q, r = divmod(n, 2)`,
  `i, j = range(2)`), and a starred name a `list` of them (`first, *rest = names`). More that's
  iterated: a tuple whose parts agree (`for name in ("a", "b")`), `map(f, xs)` by what `f` returns,
  `iter(xs)`, a generator expression (so `list(...)`, `sorted(...)` and `tuple(...)` of one), and
  any mapping's keys, values and items (`Mapping[K, V]`, `OrderedDict`, `defaultdict`,
  `MappingProxyType`). Builtins their arguments decide: `abs`, `round`, `divmod` and `sum` of
  builtin numbers, `min` and `max` of values of one type or of something's elements, `next` (with a
  default of that type, or `None`), `dict` of a mapping, of pairs or of keywords,
  `dict.fromkeys(keys, value)`, and the builtin classes' classmethods with a fixed return
  (`bytes.fromhex(...)`, `int.from_bytes(...)`); `os.environ.copy()`, a `dict[str, str]`; `-n`, `+n`
  and `~n`; and a `list` added to one of its type, or repeated. A classmethod or staticmethod called
  on its class, by its declared return (`Box.make()`), in the class's own module or another checked
  file's, however the class is imported or re-exported (`MultiIndex.from_arrays(...)`,
  `pd.MultiIndex.from_tuples(...)`); a classmethod, staticmethod or property counts under decorators
  that give it back too (`@classmethod` over `@names_compat`). And a member a class takes from a
  standard-library base, by the tables: `self.id()` in a `unittest.TestCase` is a `str`, `self.name`
  in a `threading.Thread` a `str` (not one that is the base itself, which may be `Self`). On
  pydantic, the one corpus measured: 43 more certain fixes (806 to 849) and 9 more guesses (245 to
  254), 52 fewer bindings with no fix (2,124 to 2,072); no new basedpyright error after `--fix` or
  `--fix --unsafe-fixes`, and one pass converges.
- `min-python` (`--min-python VERSION`, and `[tool.constricter]`): the oldest Python the code runs
  on, whose syntax `--fix` writes. It defaults to the lower bound of the nearest `pyproject.toml`'s
  `requires-python`. At 3.11 or later, a hint's unpacked tuple is written as the checker printed it
  (`tuple[str, *tuple[str, ...]]`): 3 more fixes on pydantic with basedpyright's and ty's hints.
- `--fix` types a subscript of a standard-library class's instance by its `__getitem__` in typeshed:
  `proxy["k"]` on a `MappingProxyType[str, int]` is an `int`, `queue[0]` on a `deque[str]` a `str`,
  `parser["section"]` a `configparser.SectionProxy`. Nothing changes on pydantic.
- A build from a checkout (the Action, a pre-commit hook's install, an editable install) generates
  the standard-library tables in about 12s on 4 cores, from 70s: each of the twelve configurations
  is read in a worker process (in the one process where none can start), and what's asked again and
  again is worked out once. The tables are the same.
- `--fix --unsafe-fixes` annotates a plain class's variables (`limit = 3` in its body becomes
  `limit: int = 3`), by a literal value or a display of them, and types what reads them
  (`self.limit`, `cls.limit`) in the same run: a new fix kind, `member`, always a guess. A plain
  class has no decorator, metaclass or other keyword, and every base is `object`, a `unittest` test
  case or another plain class, across the checked files; and no class that isn't plain inherits from
  it. Every other class body is left alone. On pydantic: 8 more guesses (235 to 243), no new
  basedpyright error, and one pass converges.
- `--fix` takes a class or alias a file spells two ways for one type: `CoreSchema` and
  `core_schema.CoreSchema`, in a file importing the name and its module (the name perhaps for type
  checking alone), as the index of checked files and installed packages resolves them. A name bound
  to one, then the other, keeps its fix. On pydantic: 6 more fixes (5 of them certain), 8 with
  basedpyright's and ty's hints; no new basedpyright error.
- `--fix` types the `self` a function defined in a method reads (one taking and binding none of its
  own; not in a method whose signature says `Self`), and a call to a function whose signature is a
  `# type:` comment, by the comment's return: `names = find()` under `# type: () -> List[str]` is a
  `List[str]`, quoted in a module body where `List` is imported under an `if` on a flag
  (`if MYPY_CHECK_RUNNING:`). Another file's type is written through the module defining it, where
  the file imports that module to run (`core_schema.CoreSchema`, `inspect.Signature`), as a hint's
  is, and no longer by a new import for type checking; not through a name the file binds as a value
  somewhere. With `--infer-with`, ty's spellings are read (`Model@create_model` is `Model`,
  `(str & ~AlwaysFalsy) | None` a `str | None`, and `tuple[str, *tuple[str, ...]]`, Python 3.11's
  syntax, is kept where the project's oldest Python parses it, else written with `Unpack` where the
  module imports it and dropped where it doesn't), and a hint naming a type variable is a fix only
  where its function's signature or its class names it. On pydantic: 4 fewer bindings with no fix
  (2,142 to 2,138), 3 fewer with basedpyright's hints (1,593 to 1,590); basedpyright finds no new
  error after `--fix --unsafe-fixes`. On the seven corpora, since 0.3.1: 53,141 certain fixes (from
  48,645) and 38,622 guesses (from 38,092), 160,085 bindings with no fix (from 165,111); nothing
  broken, and one pass converges.
- Fixed: a type naming an alias its module assigns in two branches a type checker can't decide
  between (`if MYPY: X = A`, `else: X = B`), a variable to it, isn't written in another file, nor
  taken for an alias a hint names; an import a fix needs is added even where its text is on an
  indented line (in a string, in the standard library's `_test_multiprocessing`), which binds
  nothing; a quoted `"Self"` in a signature counts as `Self`; and in a method whose signature says
  `Self`, a `Self` method called on `type(self)`, one the class inherits, and
  `self if inplace else self.copy()` are `Self`, not the class (9 errors on pandas); and what's
  inferred from a name first bound to a value of no known type, then to a typed one, is a guess,
  since it may still hold the first (`levels` bound under an `if` and its `else`, then looped over:
  2 errors on pandas's `style_render.py`; on pydantic, 1 certain fix becomes a guess).
- `--fix` types six more shapes. A union the author would write: `a if c else None` is a `T | None`,
  and `a or b` (or `a and b`) with operands of one type is that type, `or` dropping a `None` before
  its last operand (fix kind `boolean`). A `:=`'s name is declared on a line of its own before its
  statement (before the `if`, for one in an `elif`), typed as an assignment's is:
  `if (m := pattern.match(s)) is not None:` declares `m: re.Match[str] | None`. An empty container
  the function `extend`s or `update`s is typed by that argument's elements (a guess, as `append`'s
  is). A quoted annotation, or a quoted part of one, is read as its text (`xs: "list[Node]"` types
  `xs[0]` and `for x in xs`), and a module body's fix naming what isn't bound yet is quoted. Small
  shapes: `[*names, s]`, `{**d, k: v}`, `type(x)` (a `type[C]`), `d.get(k, 0)` with a default of the
  values' type, and `os.environ["X"]`. With `--infer-with`, `TypeAlias` is imported for a module's
  alias written as a subscript or a union (never a bare class's, which declared one loses the
  class's type parameters), and a hint may name a type alias a checked file or an installed package
  defines (`schema: core_schema.CoreSchema`). On pydantic, the one corpus measured: 59 fewer
  bindings with no fix (2,201 to 2,142; 52 more certain fixes, 7 more guesses), and 127 fewer with
  basedpyright's hints (1,720 to 1,593, 82 of them aliases declared); nothing broken, one pass
  converges.
- Fixed: a fix in a line and a declaration before that line no longer land on each other
  (`x = f(y := 3)`); a fix whose annotation names a parameter or local of its own function, or the
  name it annotates, isn't offered (`text: str` under a parameter `str`); a value typed whatever its
  parts are (`x.kind is None`, an f-string) stays certain when a part is a guess; and an annotation
  that is a string but not an expression (`x: "no way"`) no longer stops the file's check with a
  syntax error.
- `--fix` types a call to a decorated function that declares its return, under decorators that give
  the function back: the standard library's (`functools.cache`, `lru_cache`, `wraps`,
  `abc.abstractmethod`, `typing.final`, `override`, `deprecated`), and a function whose signature
  says so (`F -> F`, or a factory's `Callable[[F], F]`), the module's own or one imported from a
  checked file or an installed package (pandas's `@set_module("pandas")`):
  `idx = date_range("2020", periods=3)` is a `DatetimeIndex`. 2,216 more certain fixes and 249 more
  guesses on pandas, sqlalchemy and pydantic; basedpyright finds 30 new errors on pandas, where a
  name so typed is bound again to another type.
- Fixed: `--fix` left one fix for a second pass where a loop over an `Iterable[T]` binds names used
  in `tup += (name, value)`; a loop's target declared before it is still what the loop gives, and a
  tuple added to isn't taken for the tuple added. A type with a name in quotes inside it
  (`Dict[str, 'Row']`) is no longer written in a file where the name means nothing (4 new errors on
  pydantic). A hint's location that isn't a file's no longer raises, and the tests that build file
  URIs pass on Windows.
- `--fix` types a method a class inherits: `self.size()`, or `x.size()` on a value typed as the
  class, is the base's that defines it, in method resolution order among the module's classes and
  then a class of another checked file. A declared return is certain, a `Self` one the receiver's
  class, and `return`s a guess. An unannotated generator function's calls are a
  `Generator[T, None, None]` by its `yield`s, and a loop over an `Iterable[T]`, `Iterator[T]` or
  `Generator[T, ...]` declares its target `T`. A fix whose type is the same whatever a guessed name
  in it is stays certain (`os.path.join(root, "x")`), and a function whose signature is a `# type:`
  comment is no longer typed by its `return`s. On the standard library, django, sqlalchemy,
  pydantic, pandas and pip, inherited methods add 103 certain fixes and 299 guesses, generators and
  iterables 178 and 122, and 506 guesses become certain; basedpyright finds 5 new errors after them
  (4 on pandas, 1 on sqlalchemy). Joining two `return` types into a union was measured and left out:
  275 more fixes, and 38 new basedpyright errors.
- `--fix` declares a `with` statement's target by what its context manager's `__enter__` returns: a
  standard-library manager by the tables (`with zipfile.ZipFile(p) as z:` is a `zipfile.ZipFile`,
  `with tempfile.TemporaryDirectory() as d:` a `str`), a class's declared `__enter__`, and a
  `@contextmanager` function's `Iterator[T]`. Of the 5,017 `with` targets with no fix on the
  corpora, 494 have a certain one and 356 a guess; basedpyright finds no new error after the
  standard library's 438 certain ones. Not `async with`, nor a target that unpacks.
- `--infer-with pyrefly`: pyrefly is a third checker (`pyrefly lsp`). With all three, hints type
  16.3% of the bindings `--fix` can't on pydantic, sqlalchemy and django (13.2% with basedpyright
  and ty). A request pyrefly cancels is asked again; its hints for a loop's or an unpacking's names,
  which carry no edits, name each class by the file its label says defines it; and a class in an
  installed package's private module is no fix. It infers an unannotated function's return only as
  its configuration says (`infer-return-types = "checked"`).
- `--infer-with` no longer declares another name for a class (`Pair = tuple[int, str]`, hinted
  `type[tuple[int, str]]`) a variable, which annotations then couldn't be written with: a module's
  name, or a function's written as a class's is. `corpus_suite.py --types --infer-with CHECKERS`
  runs a package's own type checker after the hints' fixes too: sqlalchemy's mypy found 321 new
  errors with basedpyright's and ty's hints, and finds 47 without a module's such names.
- `--infer-with` uses a hint that names a class the file doesn't bind where its annotations run: one
  the hint's own edits import (basedpyright, ty and pyrefly send the import an editor would add with
  each hint), written through an import the module has or imported under `if TYPE_CHECKING:`, a
  module body's annotation quoted; and one the module itself imports under `if TYPE_CHECKING:`. Only
  a class a checked file, an installed package that declares its types or the standard-library
  tables define: a module basedpyright shows by its name, an alias, and a class of an unchecked
  package are left. A generic class a hint shows without its arguments (the checker doesn't know
  them) is no longer written, the module's own included, nor a special form alone (`type[Generic]`),
  nor `TypeAlias` in a function. On pydantic, sqlalchemy and django, basedpyright's hints type 614
  more of the 26,716 bindings `--fix` can't (2,253, now 2,867) and ty's 351 more; after
  `--fix --unsafe-fixes --infer-with basedpyright`, basedpyright finds 14 new errors on pydantic (21
  before) and 148 on sqlalchemy (134 before, for 411 more fixes).
- Built with hatchling, and the standard-library tables `--fix` reads are generated from typeshed's
  stubs when the package is built, no longer tracked in git. A release from PyPI installs as before;
  installing from a checkout (the GitHub Action without `version`, the pre-commit hooks,
  `pip install git+...`) downloads the pinned basedpyright as a build dependency and generates them,
  about a minute more.
- `--fix` types an installed class's methods on a receiver typed through a public alias of the class
  (`x.sum()` on an `npt.NDArray[np.float64]` is an `np.float64`): matched as what the alias stands
  for, with `Self` kept as the receiver is written; the alias found through an import under
  `if TYPE_CHECKING:`, one another module re-exports (pandas's `from pandas._typing import npt`), or
  one the file's own fixes add. 8 more fixes on pandas, no new type error.
- An installed module's cached read is keyed by constricter's code as well as its version: a
  development build whose modules had changed shape crashed reading an older entry.
- `--fix` types an installed class's method that declares its `self` by the receiver's type: matched
  against `self`'s annotation, the type variables it binds checked against their bounds by the
  installed classes' ancestors (`a.sum()` on an `np.ndarray[tuple[int], np.dtype[np.float64]]` is an
  `np.float64`: `self: NDArray[ScalarT]`, `ScalarT` bound to `inexact`). A signature whose `self`
  the receiver certainly isn't is passed over. None more on pandas yet, whose arrays are typed bare
  (`np.ndarray`) or through `npt.NDArray`.
- `--fix` types an installed class's methods whose arguments or receiver decide their type, its type
  parameters bound by the receiver's type (`a.astype(np.float32)`, `a.reshape(2, -1)`, a `Self`
  return), inherited ones too; and a builtin container argument by its elements, a bounded type
  variable binding it (`np.empty((n, 2), dtype=np.float64)` is an
  `np.ndarray[tuple[int, int], np.dtype[np.float64]]`). A class alias passed as an argument
  (`np.int32`) binds a `type[T]` as a class does. 52 more fixes on pandas, whose type checkers still
  find no new error after `--fix`.
- `--fix` types a call into an installed package whose overloads its arguments decide by the one
  they match, as it does the standard library's: with numpy 2.5's stubs,
  `np.empty(n, dtype=np.float64)` is an `np.ndarray[tuple[int], np.dtype[np.float64]]`. A stub's
  overloads are read through its aliases (PEP 695's too), type variables' bounds and constraints,
  and protocols; a standard-library class they name, by a new `scalars` table; and a class passed as
  an argument binds a `type[T]`. 83 more fixes on pandas, whose type checkers find no new error
  after `--fix`. An installed class whose subscripted base passes no type variable
  (`class float64(floating[_64Bit])`) is no longer taken for a generic one, and a typed package's
  module re-exports only what the typing rules export (`from m import x as x`, `__all__`), so
  `numpy.NDArray`, which numpy doesn't export, is never written.
- `--fix` types a comparison of builtin values (`n < 3`, `len(xs) == 0`) as a `bool`; a
  standard-library module's variable by its annotation in typeshed (`sys.path`: `list[str]`,
  `os.sep`: `str`, from a new `variables` table); and a chained assignment's names (`i = j = 0`) by
  declarations before it (`i: int`). A parameter or local named like a standard-library import
  (`def f(getpid)`, with `from os import getpid`) is no longer typed as the import: a bug for calls
  too. 1,019 more fixes on the corpora (809 on the standard library), none a type checker rejects; a
  chained name's late fix (`None`, then `str`: `str | None`) is declared too.
- `--fix` types a comparison by `in`, `not in`, `is` and `is not` alone as a `bool`
  (`writing = "w" in mode`), as `not x` is: always a real `bool`, whatever the operands. 234 more
  fixes on the corpora.
- `--fix --unsafe-fixes` types what's computed from an unannotated parameter of a plain top-level
  function when every call in the checked files passes it an argument of one builtin type
  (`callers`, a guess): `def greet(name)` called only as `greet("a")` types `line = name.upper()` as
  `str`. A function used any way but called, or a call that leaves the parameter to its default or
  unpacks its arguments, types nothing. The defining files are checked again knowing the types, then
  the files calling them: 96 more fixes on the corpora (64 on the standard library, 14 on Twisted),
  every corpus still converging in one pass.
- `--fix` types calls into installed packages that declare their types (`py.typed`, a stub package,
  a lone stub module) by their declared returns, as it does another checked file's
  (`pydantic_core.to_json(x)` is a `bytes`): found as the import system would on this Python's path
  and the active virtual environment's, read but never fixed. A type is imported from a public
  module that re-exports it, not a private one, and an installed generic class isn't written bare:
  pandas loses 181 fixes that wrote numpy's generic `np.ndarray` bare, and gains 6; pydantic
  gains 66.
- `--max-fix` (command line only) applies every fix: `--max`, `--fix --unsafe-fixes`, and
  `--infer-with` each of basedpyright and ty that's installed and runs. A checker's executable is
  the first found that runs (`--version`): a version manager's shim that can't run in the directory
  is passed over for the one beside this Python.
- `--infer-with=ty` no longer stops with `ty failed textDocument/inlayHint: content modified`: a
  hint request the server drops while later files open is asked again, up to five times.
- `--max` (command line only) runs the strictest check: `suffocate` for every path, over any
  `per-path-levels`, with `--all-scopes` and the opt-in `LVA012`.
- `--fix` types standard-library generic classes' constructors by what their arguments bind:
  `collections.deque(names)` is a `collections.deque[str]`, `itertools.product(a, b)` an
  `itertools.product[tuple[str, int]]`, `array.array("i")` an `array.array[int]`, `weakref.ref(obj)`
  a `weakref.ReferenceType[Foo]`. A type variable binds to any argument's type where the parameter
  is nothing but it (`copy.copy(obj)` is a `Foo`), to a builtin container's element where it's a
  generic of one (`Iterable[_T]` given a `list[str]`, a `dict`'s keys, a `str`), to a scalar's
  method's return through a generic protocol (`math.floor(x)` is an `int` for a `float`), and to a
  function's declared return where it's a `Callable[..., _T]` (`functools.partial(helper, 1)`); a
  parameter every overload shares is now read for it too. A generic class's own attributes are typed
  by the receiver's type arguments (`m.string` on an `re.Match[str]` is a `str`). 512 more fixes on
  the corpora (387 on the standard library), with no new type-checker error after `--fix`. A read
  the function tests makes a type it binds a guess (`deque([x])` inside `if is_union(x):`, which
  sqlalchemy's `TypeGuard` narrows: 6 of its `--fix --unsafe-fixes` new errors). At module level, a
  class some supported Python can't subscript at run time is quoted (`"itertools.count[int]"`).
- `--fix` converges in one pass on the standard library again (0.2.6 left 911 fixes for a second): a
  call to another checked file's unannotated function returning a library type its module didn't
  import yet (`test.support.import_helper.import_module`, a `types.ModuleType`) is typed on the
  first pass, by the import that module's own fixes add. CI's Corpus job runs on Python 3.14, whose
  standard library showed it.
- Checking is about 10% faster (the standard library, `--jobs=1`: 9.0s to 8.1s), every fix the same:
  whether a fix is a guess is worked out only where there's a fix, a function's body is read once
  for all its empty containers, and a node's children are listed without `ast`'s generators.
- A standard-library return may name one of `typing`'s generic classes, written by its public path
  (`tokenize.generate_tokens(f)` is a `collections.abc.Generator[tokenize.TokenInfo]`).
- Fewer guesses a type checker rejects, again: a read a test around it narrows (inside an
  `isinstance` branch, a `match` case, after an `assert` or an early `return`) isn't offered its
  declared type; and a capitalised call is guessed to construct its class only where the callee is a
  type (not a variable holding a class, `self.api.X()`, or `make().X()`). pandas's
  `--fix --unsafe-fixes` new type errors went from 84 to 36 (sqlalchemy's from 10 to 5).
- The standard-library tables write each class's members apart from its public ancestors
  (`bases.json`), which `--fix` resolves them through: 908 KB to 688 KB, the generator checking
  every class resolves to exactly its full table. `lib2to3.pygram`'s `python_symbols` and
  `pattern_symbols`, instances at run time though typeshed declares them classes, are left out; the
  existence test skips a module a Python was built without (`nis`, `dbm.gnu`), which failed CI's
  3.11 and 3.12 jobs.
- `--fix` types a call to another checked file's function, and its classes' members, whose type
  names something the calling file doesn't import: the name is imported where that file has it from,
  under `if TYPE_CHECKING:` (the module's own block, or a new one), so no import cycle can follow at
  run time; a module-level annotation using it is quoted, unless annotations are postponed. Another
  file's generic class is never written bare.
- `--fix` types a standard-library call whose arguments decide its type, by the signature they match
  among its overloads, as a type checker picks (`os.listdir(data)`, `ast.parse(s, mode="eval")`,
  `os.getenv("X", 3)`), with type variables bound by the arguments (`re.compile("x")` is a
  `re.Pattern[str]`) and generic classes' by the receiver (`pat.match(s)`, a
  `re.Match[str] | None`); and methods decided the same way (`parser.parse_args()`). The tables are
  generated from typeshed's overloads, replacing the hand-picked `AnyStr` and `os.getenv` rules, and
  now keep what only some platforms or Python versions have (`os.getuid()`).
- Fewer guesses a type checker rejects: an ALL_CAPS module constant bound to a literal and passed to
  a call is declared `Final` (which keeps its `Literal` type) rather than `str`; a read of an
  `X | None` (and a filtered comprehension over one) and a bare `None` aren't offered, as code
  nearly always narrows them first; a generic class is never written bare, whoever defines it (the
  standard library's too, unless its type parameters have defaults); and `x = None` then `x = T`
  isn't declared `T | None` where a nested function or lambda reads `x`.
- A function whose `return`s are typed only once its whole body is seen (a container it fills, a
  `None` rebound) types its calls from other files too, though nothing in its own module calls it:
  pip no longer needed a second `--fix` pass once another file could import the type.
- A GitHub release page lists each merged pull request's `## Release note` section under "What
  changed", between the README's badges and GitHub's generated list.
- `constricter.fix.modules` reads the cross-file index (out of `constricter.fix.project`),
  `constricter.rules.late` holds a scope's late fixes (out of `constricter.rules.scope`), and
  `constricter.fix.library` types standard-library calls (out of `constricter.fix.inference`): no
  module is over 750 lines.
- The standard-library tables are one JSON file each, an entry a line, in `constricter/fix/tables/`
  (was `constricter/fix/stdlib.json`); the tests' list of which platforms have what is
  `tests/typeshed/partial.json`, outside the package; a parameter every overload has alike is
  written as `"name kind="`.
- Each module is walked once for the cross-file index and the check (the index's walk was dropped
  before the check could reuse it).

- `--fix` types a call to an unannotated function another checked file defines by its `return`s, as
  it already did within a module (`returned`; a guess where they are): the CLI checks the files
  callees first, each once the modules whose functions it calls are done, and checks files calling
  each other's functions again while that types more. `from pkg import util` then `util.f()` now
  resolves `pkg.util` as `import pkg.util as util` does, for declared returns and classes too. On
  the corpora, 227 more bindings are typed; the standard library's check takes 5% longer with
  `--jobs=1` and 18% with `--jobs=0` on 16 cores.
- `tests/corpus/corpus_fix.py` copies a package into a folder of its own name, so its absolute
  imports resolve across files, as they do in place.
- A name narrowed inside a branch that may not run (`x = None`, then `x = n` under `if`) is no
  longer taken past the branch as the narrowed type: a call to `def late(n, flag)` returning `x` was
  typed a certain `int`, and is now `int | None`. A name rebound in a branch to a type outside its
  earlier one is a guess past it (`rebound`).
- `--fix --unsafe-fixes` types an unannotated instance attribute from its assignments (fix kind
  `assigned`): when every `self.x = value` in the class's own methods gives one known type (or
  numbers, widened to the widest), reads of `self.x`, and of `x` on any value typed as the class,
  are typed as guesses, and chains go on from them (`self.name.upper()`). An attribute the class
  body binds, or that is stored any other way (`+=`, an unpacking, `del`, a nested function), or
  assigned a local bound more than once, is left alone. 456 more guesses on the standard library.
- A GitHub release page starts with the README's badges (their relative links made absolute at the
  release's tag), above the generated notes.
- CI skips a tree it already passed, byte for byte: the push to `main` after a pull request's merge,
  and the release tag on it, reuse the pull request's run instead of running everything again.
- `constricter.rules.binding` binds each statement's names (moved out of
  `constricter.rules.checker`), and `constricter.cli.protocol` holds the language server wire format
  `--infer-with` speaks (out of `constricter.cli.hints`): no module is over 750 lines.
- `tests/corpus/corpus_untyped.py` (`python -m tests.corpus.corpus_untyped`) counts what `--fix`
  still can't type on every corpus, and why, as the tables the roadmap is sized by.
- `tests/corpus/corpus_table.py` also records each corpus's annotation coverage as released, after
  `--fix` and after `--fix --unsafe-fixes`, and how much each raised it; `docs/RUNS.md` keeps only
  the corpora measured today in every version's rows and totals.
- `tests/ci_local.py` runs CI's Lint, Docs and Test checks locally, in parallel, straight from
  `ci.yml`, and `--install-hook` makes it a `pre-push` hook.
- `--fix` types a member of any value whose type it knows, not just of a local: `self.index.name`,
  `t.make().label()`, `rows[0].strip()`, `f().x`, however deep; a member of a guessed value is a
  guess, and its fix kinds include the value's. A call whose type is its callee's alone (a
  fixed-return builtin, a function declaring its return, a method with a fixed or declared return)
  is certain whatever its arguments are: `len(Box())` and `"{}".format(Box())` were guesses. An
  index typed `slice` slices (`items[since]` was typed as an element). `constricter.fix.members`
  holds the member lookup, its sources in `SOURCES`.
- `--fix`'s standard-library tables are generated from the typeshed stubs basedpyright bundles
  (`tests/typeshed/stdlib_tables.py`, checked in CI), in place of the curated ones: 894 functions
  with a builtin result, 38 `AnyStr` ones, 1,478 classes and functions returning one, and 810
  classes' methods and 713's attributes (`dt.astimezone()`, `parser.prog`), for what's the same on
  every platform and Python 3.11 to 3.14. A standard-library class's call (`asyncio.Lock()`,
  `unittest.TestLoader()`) is certain, no longer a guess, and a fixed-return function's keyword
  arguments no longer stop it being typed. On the corpora, 6,050 more fixes are certain and 3,708
  fewer are guesses (most in the standard library itself).
- `--fix` adds no type errors to the corpus packages' own type checks (`corpus_suite.py --types`:
  pydantic's pyright, sqlalchemy's mypy, pandas's mypy and pyright), where it added 18, 61 and 117:
  - a name bound again later takes every value: `x = 1` then `x = None` declares `x: int | None`
    before the first binding, `total = 0` then `total += 0.5` a `float` (fix kind `rebound`);
    another type leaves it untyped, and a later value whose type isn't known makes the fix a guess;
  - after it's bound again, a name is what it was bound to (certain for a member of its declared
    union, a guess otherwise), not its annotation or first binding's type;
  - a copy, attribute or subscript of a union, or of anything the function tests (`isinstance`, a
    `TypeGuard`, `is None`, an `assert`, a `match`), is a guess, as is a comprehension of a union
    with a condition: a checker narrows them where they're read;
  - an ALL_CAPS module-level literal the module passes to a call or a default is a guess: pyright
    keeps its `Literal` type;
  - `self`, and a `Self` method called on `self` or `cls`, in a method whose signature says `Self`,
    is written `Self` as the module imports it (or not at all), not as its class;
  - a generic class the module defines is never written bare (`list[Mapper]`);
  - a declared return naming a type variable imported from another checked file (under
    `if TYPE_CHECKING:` too) or `typing.AnyStr` doesn't type its calls;
  - a type argument with a trailing comma (`list[\n    int,\n]`) is read as the element it is.
- `--fix` types a loop over `enumerate` or `zip` one part at a time: `for i, x in enumerate(xs)`
  declares `i: int` even when `xs`'s elements aren't known, and a guess about one part no longer
  makes the others guesses. `enumerate(xs, start=1)`, `zip(a, b, strict=True)` and
  `sorted(xs, key=f)` are typed too.
- `--fix` types more builtins' calls (`any`, `all`, `ascii`, `bin`, `bytearray`, `dir`, `format`,
  `hex`, `input`, `oct`, `range`), `str`/`bytes` methods on a literal (`", ".join(parts)`), and
  `partition`/`rpartition`. A builtin's name the module binds itself (a parameter named `repr`, a
  local `sorted`) is no longer taken for the builtin: `def f(repr): a = repr(1)` gave `a: str`.
- Faster checking (the standard library's, profiled, 63s to 52s): a module's functions are checked
  callees first, so few are checked again for a callee's return type; each file is parsed once, the
  cross-file index's tree kept for its check in the same worker; and the shared walk reads only each
  node class's fields. The fixes are unchanged.
- `tests/corpus/corpus_suite.py` runs pydantic's, sqlalchemy's, django's and pandas's test suites
  before and after `--fix`, and with `--types` their own type checkers, tracing each new type error
  to the fix mechanism behind it.
- `tests/corpus/corpus_profile.py` profiles a check of a large codebase, printing constricter's
  slowest modules and functions, and where the rest of the time went (`ast.walk`, mostly); CI's
  Corpus job adds it to its summary and keeps the profile.
- `--infer-with basedpyright` (or `ty`, or both, `basedpyright,ty`, the first named preferred;
  `infer-with` in `[tool.constricter]`): `--fix` asks those type checkers' language servers, all at
  once (basedpyright over up to four, as `--jobs` and `--infer-memory` allow, 8 GB by default; each
  behind a guard that kills it if constricter is killed), for their inlay hints, and types what it
  can't type itself from them, as guesses (fix kind `checker`, applied with `--unsafe-fixes`). A
  `Literal` is widened to its values' types; a hint that's vague, isn't an annotation, or names
  something the file can't use is dropped; a class the checker prints bare (`Callable`, `Path`, ...)
  is imported. With `--fix`, a changed file is asked about and fixed again until nothing changes
  (four rounds at most). On `requests`, `flask`, `fastapi`, `rich` and `pydantic` it about doubles
  what `--fix --unsafe-fixes` types.
- `x = None`, later rebound only to a guessed type, is `T | None` as a guess too (it waited for the
  guess to be applied, and a second `--fix`, before).
- `check_source` and `check_tree` take what's known of a file from outside it as one `outside`
  argument (`Outside`: other files' return types and classes, and a type checker's hints), in place
  of `calls` and `classes`.
- `constricter.fix.inference` is split: guesses are judged in `constricter.fix.guesses`, and a type
  split over a loop's or an unpacking's names in `constricter.fix.targets`.
- `--fix` adds the import a type needs: `open(path, mode)` is typed by its literal mode
  (`io.TextIOWrapper`, `io.BufferedReader`, `io.BufferedWriter`, `io.BufferedRandom`; fix kind
  `open`), and `with open(...) as f` declares `f` before the statement; standard-library classes and
  functions returning one (`logging.getLogger()` → `logging.Logger`, `datetime.now()`, `uuid4()`,
  `Path.cwd()`, `argparse.ArgumentParser(...)`) are typed (fix kind `stdlib`); and LVA012 offers
  `Final` (`Final[T]` around its annotation or LVA001's type, a bare `Final` without one; fix kind
  `final`). An existing import is reused (`import io` gives `io.BufferedReader`); otherwise one is
  added after the module's docstring and leading imports, never under `if TYPE_CHECKING:`, over a
  name the module binds, or over a builtin. In a notebook, a fix that needs an import is reported
  but not applied.
- `--fix` types calls to the module's unannotated functions from their `return`s (fix kind
  `returned`; a method's is a guess), uses of classes other checked files define (their attributes,
  properties and methods), and, as a guess, an empty container from what the function then adds to
  it (fix kind `filled`).
- The CLI reads the cross-module index in parallel with `--jobs`, so checking is faster.
- `sys.getrefcount` isn't in the standard-library table: it's CPython's only.
- `sys.getswitchinterval()` is typed `float`, not `int`.
- `--fix` types standard-library functions with a builtin result (`time.time()`, `os.getpid()`,
  `textwrap.dedent(...)`, `os.environ.get(k)`, `os.path.join` of `str`s; fix kind `stdlib`),
  resolved through the imports, and `x = None` later rebound to one known type as `T | None` (fix
  kind `optional`).
- `--fix` types a tuple longer than `max-length` as `tuple[T, ...]` when its elements agree, and not
  at all when they differ, instead of listing every element's type.
- `--fix` types a `@property`'s declared return (`obj.prop`), `cls` in a classmethod (`type[C]`:
  `cls.x` from class attributes, `cls.m()` from classmethods and staticmethods), and
  `typing.cast(T, x)` as `T` (fix kind `cast`).
- `--fix` for LVA003 (the loop's `# type:` comment becomes a declaration before it, fix kind
  `comment`) and LVA007 (the repeated annotation is dropped, fix kind `redundant`).
- SARIF and rdjson carry every edit of a fix (LVA003's has two); `Result.replacements` replaces
  `Result.replacement`.
- `annotation_coverage` accepts `bytes` as `check_source` does (it crashed on a `match` with a
  `**rest` capture), and `value_flow` places a `**rest` capture at its name, as `check_source` does.
- **LVA012** (opt-in): a local bound once, by a plain assignment outside any loop, and never rebound
  could be `Final`. Reported only when selected by its full code (`--extend-select LVA012`, new;
  flake8's `extend-select`; pylint's `could-be-final`, `C9112`, off by default), and an error only
  at `suffocate`.
- `--extend-select` (`extend-select`): report more codes without narrowing to them.
- Fix levels: each `--fix` mechanism has a stable id (`literal`, `copy`, `constructor`, ...), shown
  by `--show-fixes` and as `kinds` in `--format=json`; `fix-select` and `fix-ignore` choose which
  fixes are offered, and `unsafe-fix-select` makes a trusted guess (`constructor`, `narrow`)
  certain. The defaults are unchanged. See `docs/FIXES.md`.
- The error for a `--fix` a file's encoding can't hold names the encoding by its canonical name
  (`iso8859-1`), the same on CPython and PyPy.
- A module is read in its PEP 263 declaration's encoding (`# -*- coding: latin-1 -*-`) or its BOM's,
  not always UTF-8, and `--fix` writes it back in the same one (or leaves it, exit 2, when an
  annotation can't be written in it).
- SARIF: each rule has its help text and a `helpUri`, each certain fix is a SARIF `fix`, and columns
  count characters (`columnKind: unicodeCodePoints`), not UTF-8 bytes.
- rdjson: a loop target's or an unpacking's suggestion declares it on a line before the statement
  (it was `for x: T in ...`).
- The GitHub Action: a `version` input (a PyPI release, installed with uv), a per-code summary table
  on the run page (`summary`), and a `sarif-file` output for `upload-sarif`.
- The `constricter-fix` pre-commit hook runs as one process (`require_serial`), so its cross-module
  `--fix` sees every file; a pre-commit.ci snippet in the README.
- `--fix` declares a loop's target (LVA002) or an unpacking's names (`name: T` before the
  statement), infers conditionals, arithmetic on builtin scalars, comprehensions, `sorted`/`list`/
  `set`/`frozenset`/`tuple` of known elements and `await` of the module's `async def`s, and, with
  `--unsafe-fixes`, rewrites the annotation LVA008 or LVA010 would narrow.
- **Breaking** (the API): an `Offence`'s fix is an `edit=Fix(...)` (annotation, reason, guess,
  where); `offence.fix`, `.unsafe` and `.reason` still read as before.
- `--format=full`: each offence with its source line and a caret under the name.
- Editor settings for VS Code, Zed and Neovim (`docs/editors/`), and `uvx`, `pipx`, Bazel and Pants
  notes in the README.
- `tests/corpus_table.py` records each version's corpus results in `docs/RUNS.md`.
- **Breaking**: the pylint plugin is `constricter.plugins.pylint` (was `constricter.pylint_plugin`),
  and the package is reorganised (`constricter.rules`, `constricter.fix`, `constricter.cli`,
  `constricter.plugins`); the `constricter` package's own exports are unchanged.
- **LVA011**: an annotation listing a fixed-length tuple of more than `max-length` types (4 by
  default; `--max-length`, `max-length`, and the plugins' `constricter-max-length`). Reported from
  `strict`, an error at `suffocate`; pylint's `C9111`.
- `[tool.constricter.narrower]` (the plugins' `constricter-narrower`): your own type hierarchy for
  LVA008–LVA010, over the built-in one.
- `--show-fixes` lists each fix and how its value decided it; `--format=json` gains a `fix` object.
- **LVA008** (an annotation every value fits a narrower type of, `total: float` only ever given
  `int`s) and **LVA010** (a union member no value ever is): for a function's own names, reported
  from `constrict`, errors at `suffocate`; pylint's `C9108` and `C9110`.
- **LVA009**: a value, anywhere in a name's lifetime in the scope, whose type doesn't fit its
  annotation (`count: int = 0`, then `count = "done"`). A warning, an error from `constrict`;
  pylint's `C9109` (`mismatched-value-type`).
- `nesting` (LVA006) defaults to 3, not 5: `dict[str, list[int]]` is fine, one level deeper isn't.
- `--fix` infers method calls on an already-typed local: a method of a class defined in the same
  module (its declared return type; a bare `Self` return is the class itself), and
  `list`/`set`/`dict` methods whose return is the receiver's own element type (`pop`, `setdefault`,
  `get` as `V | None`, `popitem`, `copy`). Both are certain fixes, not `--unsafe-fixes` guesses.
- `--fix` infers more: `not x` (always `bool`), calls to builtins with a fixed return type (`len`,
  `isinstance`, `str`, ...), a plain `x = y` copying `y`'s already-known type (its annotation, an
  earlier fix, or an annotated parameter), a subscript of an already-typed local (`container[key]`,
  its element type; a slice, the same type back), an attribute of one (`obj.attr`, a class-level
  annotated attribute of a class defined in the same module, or a `self.x: T = ...` annotated
  anywhere in one of its methods), a method's own `self` typed as its class, and a call to a
  `str`/`bytes` method whose return type doesn't depend on its arguments (`strip`, `split`,
  `startswith`, `encode`, `decode`, ...) on an already-typed local.
- **LVA007**: a name annotated again with the type it already has, in the same straight-line block
  (an `if`'s two arms, a `try`'s body and its `except`s, ... are compared separately, not against
  each other). A warning at every level, an error at `suffocate`.
- `--exclude` globs also match a directory name during a directory walk (like the built-in skip list
  for `__pycache__`, `venv`, hidden directories, ...), not just a whole path or file name.
- Enum bases and factory calls (`Enum`, `NamedTuple`, `TypeVar`, ...) are recognised by where
  they're imported from, in addition to their bare name, so an aliased or re-exported one is still
  found.
- `project.calls` finds a module/submodule import by name lookup instead of scanning every indexed
  module (`project.index` now returns a `project.Index`, not a plain `dict`).
- `tests/corpus.py` and `tests/corpus_fix.py` (checking and `--fix`-ing a large real codebase) run
  in CI's Corpus job, against the runner's Python standard library and, from a new pinned `corpus`
  dependency group, `requests`, `flask`, `django` and `sqlalchemy`.
- Fix: `--fix` could corrupt a line (and crash) if an offence's fix landed inside a multi-byte
  character; that one offence is now left unfixed instead. Found by the new Corpus job, on the
  Python 3.11 standard library.
- First release, 0.2.0: `LVA001`–`LVA006`, the `relaxed` to `suffocate` levels, a flake8 plugin, a
  pylint plugin and the `constricter` command (with `--fix`, `--diff`, `--explain`, `--select`,
  `--ignore`, `--statistics` and text, JSON, GitHub and SARIF output), configured from
  `[tool.constricter]` in `pyproject.toml`. Python 3.11+. Also baselines (`--write-baseline`,
  `--baseline`), Jupyter notebooks, a GitHub Action, `--jobs`, per-path levels, and JSON with
  comments wherever constricter reads JSON. `--coverage` reports annotation coverage; standard
  input, `gitlab`, `junit` and `rdjson` output, `--unsafe-fixes`, per-file ignores, `--exit-zero`
  and `--output-file`; `--fix` edits notebook cells; releases carry SLSA Build Level 3 provenance
  (GitHub artifact attestations); `--fix` types calls to functions in other checked files.
  `check_source`, `check_tree` and `annotation_coverage` take their options as one `Checks`.
