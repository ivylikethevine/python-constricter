# Completed

What constricter does today and what was measured on the way, by scope. What's next is in
[ROADMAP.md](ROADMAP.md).

## Rules

- **LVA001–LVA004**, with `all-scopes` for module and class bodies (LVA004), and `# type:` comments
  counted automatically in modules importing Python 2 `__future__` features.
- **A type's factory through a re-export**: `_Ts = TypeVarTuple("_Ts")` is a type, not a variable
  to annotate, where `TypeVarTuple` comes through a checked module's re-export too (sqlalchemy's
  `util.typing`, from `typing_extensions`), followed through the index (`across.factories`). On
  sqlalchemy 2.1.4 with `--all-scopes`, LVA004 30 offences fewer (2,471 from 2,501; 17
  `TypeVarTuple`, 13 `TypeVar`), the rest the same.
- **LVA005 and LVA006** (vague past `vague`'s level, deeply nested), with what makes a type
  (`T = TypeVar("T")`, a `NewType`, a functional `NamedTuple`) exempt from LVA001 and LVA004,
  **LVA007** (annotated again the same way, per straight-line block), **LVA011** (a tuple longer
  than `max-length`, 4: measured, annotations list 5 or more types only 3 times on the corpus).
- **Value flow**: **LVA009** (a value that doesn't fit the annotation; 10 findings on the corpus,
  each real), **LVA008** and **LVA010** (an annotation that could narrow, a union member no value
  uses), claimed only for a function's own names with every value known, and a user-defined type
  hierarchy (`narrower`).
- **LVA012, opt-in** (could be `Final`): selected only by its full code, an error only at
  `suffocate`; it fits 45–70% of every corpus's first bindings, so it stays opt-in.
- **Levels**, **per-path levels**, `select` / `ignore` / `extend-select`, per-file ignores, and
  settings from `[tool.constricter]`.

## `--fix`

- **What it infers** (all of it in [FIXES.md](FIXES.md)): literals and containers of them; calls to
  functions that declare their return, or whose `return`s decide it (`returned`), in the same module
  or another checked file, and a classmethod or staticmethod called on its class (`Box.make()`,
  another checked file's `MultiIndex.from_arrays(...)`, or on an instance); fixed-return builtins
  and `str`/`bytes` methods, and builtins their arguments decide (`min`, `max`, `sum`, `abs`,
  `round`, `divmod`, `next`, `dict`); members of any typed value (`self.index.name`,
  `rows[0].strip()`, however deep, through `constricter.fix.values.members`); `cls` in a classmethod
  as `type[C]`, and `type(x)`; computed values (conditionals, arithmetic on builtin scalars and
  lists, a `pathlib` path's `/`, comprehensions, `sorted`/`list`/..., `await`), comparisons by `in`
  and `is`, or of builtin values (a `bool`); a union the author would write (`a if c else None`,
  `a or b` of one type); displays that unpack (`[*names, s]`, `{**d, k: v}`), `d.get(k, 0)` and
  `os.environ["X"]`; a subscript of a standard-library class's instance by its `__getitem__`
  (`proxy["k"]` on a `MappingProxyType[str, int]`); standard-library module variables (`sys.path`);
  chained assignments' names, declared before them (`i = j = 0`), and a `:=`'s, before its
  statement; a quoted annotation read as its text (`xs: "list[Node]"`); the `self` a function
  defined in a method reads; a `# type:` signature comment's return, as a declared one;
  `typing.cast`; `x = None` later rebound to one type as `T | None`; loop targets (`enumerate` and
  `zip` part by part, `map`, a generator expression, any mapping's items, an `Iterable[T]`'s `T`)
  and unpackings, name by name (`a, b = x, 1`, `a, b = s.split(",")`, `first, *rest = names`, and
  the parts that aren't vague of a call declaring a `tuple[Row, dict[str, Any]]`), declared before
  the statement, as a `with` statement's target is, by its context manager's `__enter__`; a method a
  class inherits, from the base that defines it, in the module, another checked file or the standard
  library (`self.id()` in a test case); an unannotated generator function's calls, by its `yield`s;
  a call to a function decorated by what gives it back (`functools.cache`, pandas's
  `@set_module("pandas")`, by its declared `Callable[[F], F]`); a call of a value typed
  `Callable[..., R]`, `type[C]` or a class declaring `__call__` (`handler(source)`, `cls()`,
  `cls.__new__(cls)`); an unpacked named tuple's names, by its fields (a tuple alias's by its
  tuple), and a `with` target that unpacks; a `@contextmanager` method's `with` target; `getattr`
  and the standard library's functions declared to return `Any`, from `vague` 1; a module's type
  alias, declared `TypeAlias` (`alias`: certain where every Python the module runs on has it); fixes
  for LVA003 and LVA007. A tuple longer than `max-length` is `tuple[T, ...]`. A name the module
  binds once, at its top level, as it's typed there, in every function (`n = LIMIT + 1`,
  `for name in NAMES`), and the module's own `__file__` and `__name__`; integers' `**` by a literal,
  shifts and bitwise operators, a tuple's `+` and `*`, a `set`'s operators and a `dict`'s `|`; a
  fixed-length tuple's part by a literal index; `a or []`; `min` and `max` of an `int` and a
  `float`; `await` of a task held in a name. A member of an `X | None`, as `X`'s (`m.start()` on
  what `re.match` gave), and a loop over one; `path.open(mode)`, as `open` is; `enumerate`, `zip`,
  `map` and `reversed` bound to a name; `x.__class__`, and a class's `__name__` read of it or of
  `type(x)`; a loop over a standard-library class's instance, by its `__iter__`
  (`for line in open(path)`, an `itertools.chain[int]`, a `deque[int]`). A function's own imports
  (`import os` in its body); a type named by the module's import for it under `if TYPE_CHECKING:`; a
  call of a module's `NewType`; a `dict`'s `.keys()` under a `set`'s operators. An attribute a class
  takes from a base (`self.limit`, declared in a class above, in the module or another checked
  file); a `TypedDict`'s key read by a literal (`movie["year"]`, `movie.get("year")`), a checked
  file's or an installed package's; and what's read of a name typed too vaguely to write
  (`for name in fields`, `fields` a `dict[str, Any]` by its call's declared return). A call of
  another checked file's unannotated method, by its `return`s (`path = self.mktemp()` under an
  imported base, `tool.name()` on an imported class's instance), as a guess. `await` of a checked
  file's `async def`, a function's in another file or a method's, and of a generic standard-library
  class's (`await queue.get()`), with `asyncio.ensure_future` and an undeclared return left; a
  function or a bound method bound to a name (`Callable[..., R]`); a class-side method a class takes
  from another file's base (`Sub.make()`). What `with mock.patch(...) as m` binds (a
  `MagicMock | AsyncMock`); a lambda bound to a name, by its body; a member behind another file's
  class of several bases, one line reaching a library class; an empty container of `self` filled by
  the module's classes under its own; a checked file's overload picked by the checked files' classes
  (`concat([df, df])`); an attribute read off an installed method's call whose return no file can
  name (`capsys.readouterr().out`), and off a name bound to that call; a class's `parametrize`, and
  a fixture's `params` for its `request.param`. A `with` target of another checked file's manager
  (`@contextmanager`, declared or by its `yield`s; an `__enter__` returning `self`), of `os.fdopen`,
  `tokenize.open`, `shelve.open` and `assertLogs`; `asyncio.ensure_future`, and an `await` of an
  undeclared `async def`; a lambda by what its calls pass it, a module's or a plain class's callable
  alias, and a `Callable`'s parameters where its function's are positional; a base in a package that
  declares no types (django's `TestCase`), behind two library classes, or a generic library one
  given its arguments (`collections.OrderedDict[str, int]`); an empty container by the parameter
  it's passed to, or filled under another file's class; an overload's parameter typed as a checked
  file's alias, protocol or type variable, a method's overloads, and a function called through its
  module. A loop over `os.walk(top)` (a `str` and two lists of them, by its `top`), `iter(xs)` bound
  to a name, `sum` of a class's instances (`T | int`) and `filter(f, xs)` where `f` can't narrow; a
  generic class's operator (`Counter[str] + Counter[str]`), a reflected one (`2 * span`), and a
  checked file's class's under a library base's; `itertools.chain.from_iterable`, and a generic
  class's classmethods (`OrderedDict.fromkeys`). `getattr(obj, "name", default)` as `obj.name` is
  read, joined with the default's type (19 bindings fewer with no fix on the 47 corpora), and
  `pytest.importorskip("mod")` as `import mod` for what's read of it.
- **The standard library, from typeshed**: tables generated from the stubs basedpyright bundles when
  the package is built (`stdlib_tables/`, see [Project](#project)), read as Linux, macOS and Windows
  and Python 3.11 to 3.14 see them, into `constricter/fix/tables/` (one JSON file a table, an entry
  a line; each class's members apart from its public ancestors'). Fixed returns, classes and what
  returns them (`asyncio.Lock()`, `logging.getLogger()`), their attributes and methods; and
  functions and methods whose arguments decide their type, by the signature a call matches as a type
  checker picks among overloads, with type variables bound by the arguments (`re.compile("x")` is a
  `re.Pattern[str]`) and generic classes' by the receiver (`pat.match(s)`). A type variable binds to
  any argument's type where the parameter is nothing but it (`copy.copy(obj)`), and to a builtin
  container's element where it's a generic of one (`Iterable[_T]` given `list[str]`), to a scalar's
  method's return through a generic protocol (`math.floor(x)`), and to a function's declared return
  (`functools.partial(f, x)`); generic classes' own attributes are bound by the receiver's
  (`m.string`), and what one inherits with one type is typed whatever they are (`f.read()` on an
  `io.TextIOWrapper`). A non-generic class's attribute typed with classes' own arguments is held as
  a template too (`sig.parameters`, `tree.body`), as is such a module variable (`sys.modules`), and
  an operator's method with what each signature takes (`when - start` is a `timedelta`).
  `defaultdict(list)` and `Counter()` take their parameters from what's added at their keys, a guess
  (`filled`). Generic
  classes' constructors are read from their `__new__` or `__init__` (`collections.deque(names)` is a
  `collections.deque[str]`, `array.array("i")` an `array.array[int]`), or the instance an `__init__`
  overload's `self` declares (`subprocess.Popen(cmd, text=True)` is a `subprocess.Popen[str]`); at
  module level, one some Python can't subscript at run time is quoted. A generic class returned bare
  is written with its type parameters' defaults (`ET.SubElement(...)` is an `ET.Element[str]`). What
  only some platforms or versions have is kept (`os.getuid()`).
- **The checked files' own overloads**: a call to a function defined with `@overload` is typed by
  the overload its arguments match (`constricter.fix.index.own_overloads`), where builtin,
  standard-library and `Literal` parameters decide it; each return is written as another checked
  file's type is.
- **Installed packages**: calls into an installed package that declares its types (`py.typed`, a
  stub package, a lone stub module) are typed by their declared returns as a checked file's are,
  found as PEP 561 says on `VIRTUAL_ENV`'s path and this Python's (a stub package first); types are
  imported from a public module that re-exports them. Functions whose overloads or type variables
  their arguments decide are matched as the tables' are (`constricter.fix.index.stubs.stubbed`),
  through the package's aliases, type variables and protocols, the standard-library classes it names
  by the `scalars` table, and a class argument binding `type[T]`: 83 more fixes on pandas
  (`np.empty(n, dtype=np.float64)`), no new type error. They're read at run time through the index,
  not by `stdlib_tables/`'s reader, which needs typeshed's standard-library stubs. Their classes'
  methods too, the receiver's type binding the class's type parameters and `Self`, or matched
  against a method's own `self` (`a.sum()`), a receiver typed through a public alias as the class it
  stands for (`npt.NDArray[np.float64]`); a builtin container argument by its elements, binding a
  bounded type variable (numpy's shapes).
- **Fixes that add an import**: `open(p, "rb")` by its literal mode, standard-library classes, and
  `Final`, through an import the module has or one added after its leading imports; another checked
  file's type the module doesn't import, through the module defining it if the file imports that one
  to run (`core_schema.CoreSchema`), else under `if TYPE_CHECKING:` (no import cycle at run time),
  quoted where a module-level annotation is evaluated. A class defined in a class's body is named
  through that class outside it (`names: Group._Names`); a class of a module only some platforms
  have is no fix where a function alone imports it, by a table generated from typeshed (`platform`:
  35 modules).
- **Re-exports, one way**: a name is followed to where it's defined through what a module imports
  for type checking alone too (`project.definition`, as `canonical_origin` does), so a class a
  package's `__init__` imports only when it's asked for (pydantic's `TypeAdapter`) has its members,
  its methods' returns and its aliases; a package's re-exports are spelled from both
  (`modules.exported`). On pydantic's checkout with its tests, 42 fixes more (36 certain, none
  lost), and basedpyright finds no error the fixed copy didn't have; mcp, the standard library and
  pandas are the same.
- **Guesses** apply only with `--unsafe-fixes`: a call taken to construct its class (a capitalised
  name but a standard-library function's, or a variable's bound to one, as `multiprocessing.Value`
  is, which the `functions` table lists, or a class the checked files define whatever its name's
  case), LVA008's and LVA010's narrowing, an empty container typed by what's added to it (`append`,
  `extend`, `update`, ...; an attribute's, `self.items = []`, by what its class's methods add), a
  display whose elements' types differ by their union (`joined`), a method typed by its `return`s,
  an instance attribute by its assignments (`assigned`), a plain class's variable by its literal
  value, what the standard library types it as, or the checked file's class it names (`member`:
  under plain classes, test cases and builtin exception or value classes), an unannotated parameter
  by what every call in the checked files passes it (`callers`, builtin types alone: callers'
  classes too would add 10 fixes on the corpora), a test's by the pytest fixture it names (its
  `conftest.py`s', or pytest's own: `capsys`, `tmp_path`) or its `parametrize` literals (`fixture`),
  and what rests on any of these. **Fix levels**: every mechanism has a stable id (`--show-fixes`,
  JSON), and `fix-select`, `fix-ignore` and `unsafe-fix-select` choose which apply.
- **Likely guesses** (`--likely`, [LIKELY.md](LIKELY.md)): the guesses measured to hold as often as
  a certain fix does, by their whole set of mechanisms (`offences.LIKELY`). Every guess on 42
  packages is held to its package's type checker and to what its traced tests bound: 61 sets pass
  the bars, 36,777 of the 45,922 guesses (80.1%). A file `--fix --likely` wrote a guess in is
  checked again in the same run: what rests on that guess alone is certain once it's declared, so a
  second pass is left nothing. The files a round changed are indexed again
  (`constricter.fix.index.modules.spliced`), and every other file is checked again where what it
  knows from outside changed (`f = defer.fail()` once `defer.py` declares the `Deferred` it
  returns), by the `Outside` each was last checked with: a second pass leaves nothing on the seven
  corpora or the 40 mega corpora, from 605 and 248 lines. Those rounds take `fix-likely` to 1.47 and
  1.84 times `fix-certain`'s seconds there, from 1.05 and 1.13. A fix's tier is decided in one place
  (`Offence.tier`).
- **Type-checker-backed inference** (`--infer-with basedpyright,ty,pyrefly`): the checkers' inlay
  hints type what `--fix` can't, as guesses, widened, checked and imported; with basedpyright it
  about doubles what `--fix --unsafe-fixes` types on the annotated corpora. A hint naming a class
  the file doesn't bind is a fix too, the class imported under `if TYPE_CHECKING:` by the import the
  hint's own edits carry, or one the module has there: only a class the index of checked files and
  installed packages, or the standard-library tables, define, and no generic one shown without its
  arguments: 27% more of basedpyright's hints are fixes on pydantic, sqlalchemy and django, and 19%
  more of ty's. A type alias the index finds (a name annotated `TypeAlias`, or bound to a subscript
  or a union) is taken as a class is (12 more fixes naming `CoreSchema` on pydantic), and a module's
  composite alias `--fix` alone can't vouch for (a union of an unchecked package's classes) is
  declared `TypeAlias` by the checker's hint. ty's spellings are read (`Model@create_model`,
  `str & ~AlwaysFalsy`; an unpacked tuple is kept where the project's oldest Python parses it,
  `min-python` or `requires-python`'s, else written with `Unpack` where the module imports it, else
  dropped), and a hint naming a type variable is a fix only where its function's signature or its
  class names it. A hint is held to what its function does with the name: none for a name bound
  again to another type or to one `--fix` can't type, a union its function never narrows, a union
  inside a container's arguments, a `Literal` in a class's own, a name returned as `Self`, or a
  generic alias ty's edit writes as its class (`np.ndarray[np.bool]` for an `NDArray[bool]`).
  pandas's own type checkers find 84 new errors after the hints' fixes, from 444 (32 without the
  hints).
- **Types observed at run time** (`python -m constricter.trace -m pytest`, then
  `--infer-from FILE`): the run's lines are followed (`sys.monitoring`; `sys.settrace` before Python
  3.12), and the type of each name a statement of a function under the root binds is noted as the
  statement ends (builtin containers by their first elements, a class by its module and name),
  written by each file's SHA-256, each binding by its line; a pytest process the run starts
  (pytest-xdist's workers) records itself. `--fix` takes them as a checker's hints are taken, as
  guesses of kind `traced`, for a local an assignment or a `for` loop binds to a value taken from a
  parameter no checker types, or from an attribute of `self` its class stores only such parameters
  in (what no checker types wider than the run saw), bound again or in a loop too, a class the file
  doesn't name imported under `if TYPE_CHECKING:`. With their suites traced: 1,443 fixes on pandas,
  462 on Django and 179 on SQLAlchemy, none bringing an error where the traced name is bound, and
  Django's tests the same after; pandas's traced tests take 99s on 14 workers, as they do untraced,
  Django's 20 minutes in one process.
- **Wider types, chosen** (`fix-widen`, [FIXES.md](FIXES.md#wider-types-fix-widen)): each a fix kind
  of its own, off unless listed (`all`: every one). A statement one writes ends with
  `# constricter: auto`: LVA005 passes over it, `--coverage` counts it apart (typed, widened), it
  types nothing read of its name (so one pass still leaves a second nothing), and once its value's
  type is known `--fix` writes that over it and drops the mark, as it never does an author's
  annotation. Not `object` at any level: it hides no error, and nearly every use of the value then
  is one. Five kinds: `untyped-parameters` (`Any` for `x = param` and `y = param.method()`, the
  parameter with no annotation and no default, which a checker types by it), `empty-containers`
  (`list[Any]` for an empty one nothing fills) and `mixed-containers` (`list[Any]`,
  `tuple[Any, ...]`, `dict[str, Any]` for a display of mixed or unknown elements), certain; `unions`
  (two or three known types' union, not for a name changed in place nor with a `Self`) and `vague`
  (a known type vaguer than `vague` allows), guesses. On sqlalchemy, with `--unsafe-fixes`: 175,
  196, 98, 9 and 184 bindings, 662 together (4.5%); basedpyright finds no error in a file under a
  rule it hadn't one for, and 22 fewer, which the `Any`s hide (13 by `mixed-containers`). The first
  unions, of guessed values or changed by `+=`, brought 3 errors with 15 fixes. And two for a
  function's name bound to a call of no known type, `Any`, certain, whatever the name is bound to
  later: `untyped-calls` (the module's own function, a method of the class or its bases in the
  module on `self`, or another checked file's function, that declares no return: what mypy takes it
  for) and `unknown-calls` (any other). Both, and `vague`, type what a loop, an unpacking or a
  `with` binds too, declared before the statement. On pydantic, with `--unsafe-fixes` and every
  kind: 773 bindings widened from 187, 81.0% typed or widened from 66.2%, 514 by `unknown-calls`
  (its functions all declare their returns); basedpyright finds two errors fewer and four more (a
  name declared `str | None`, assigned an explicit `Any`, keeps that type; a loop's target declared
  `Any`, which a `TypeIs` narrows otherwise than the `type` it was). On the seven corpora, with
  `--unsafe-fixes` and every kind, a check offers a widening for 79,791 of the 250,958 offences
  (31.8%), the bindings with no fix going from 139,714 to 59,923, and a fix leaves 76.7% of the
  bindings typed or widened (45.6% typed, from 2.2%), no file broken: `unknown-calls` 56,419,
  `untyped-calls` 12,187, `empty-containers` 3,812, `untyped-parameters` 3,173, `mixed-containers`
  2,543, `vague` 1,186, `unions` 471. With `untyped-calls` beside the guesses, sqlalchemy's mypy
  finds nothing new (299 such fixes) and pandas's checkers the one error they find without it (812);
  pydantic has no such call. A union of a guessed value's type is a guess, resting on it; a class a
  package re-exports is the one its module defines (`pd.DataFrame`), and the members of one an
  overloaded method's return imports type what's read of it in the same pass: with every kind, a
  second `--fix --unsafe-fixes` pass leaves nothing on the seven corpora, from 12 bindings (pandas
  9, the standard library 2, pydantic 1), and pandas gets 25 fixes more without widening, pydantic
  none (`scratch/widen_pass.py`, 4 workers on 16CPU/60GB).
- **Each checker's servers, by its own measure**: every checker gets up to four, and a server's
  memory is its checker's (`Server.fitting`). basedpyright's each hold the whole program (0.6 GB and
  130 bytes for each byte of the files); `ty`'s and pyrefly's each hold their share, so the files
  count once among them (0.4 GB a server and 38 bytes a byte; 0.47 GB and 120). A hinted check of
  pandas: `ty` 36s with one server, 25s with two, 21s with four (1.2 GB, 1.7, 2.5); pyrefly 132s,
  58s and 32s (2.8 GB, 3.2, 4.2). Measured, and left out: asking for the hints while the files are
  indexed gained nothing with every CPU (a hinted check of pandas 118s, from 117s: the workers index
  in a second or two), and a worker forked while the servers' threads ran hung on Python 3.11.
- **A hung server is restarted**: one silent for 120s is restarted and each file it hadn't answered
  asked about alone; a file it hangs on again has no hints, named on standard error. The hang is
  remembered by the checker's installed version and, for an hour, by the file's path
  (`remembered._RECENT`), so the second pass over the text it fixed leaves the file out from the
  start: pandas's `infer-basedpyright`, which hangs on `tests/apply/test_series_apply.py`, took
  380s, from 746s, the file's 89 fixes the same and the rest within what two runs differ by.
- **Hints kept between runs**: `--infer-with` keeps every round whole (`cli/lsp/stored.py`), by the
  checker's build, the text of every file asked about, the workspace's settings files, the
  environments' installed distributions and the code that asks; a round kept starts no server,
  `--infer-fresh` asks again, an entry unread for 14 days goes, and a run's report notes a step that
  read one. The 0.4.3-rc.1 mega-fast run, at the mega run's commit, read every round of its 141
  `infer-*` steps from the store, each patch byte for byte the mega run's: 56 minutes on
  16CPU/60GB, the mega run 95.
- **What a hint breaks, under one in a hundred**: on the 0.4.3-rc.1 mega run the hinted steps
  brought 381 new errors in the packages' own checkers (458 on 0.4.0-rc.3, 868 on rc.2): pyrefly's
  128, basedpyright's 110, ty's 107 and the trace's 36. For each hundred hint fixes past
  `--fix --unsafe-fixes`, every hinted step's together: pandas 0.54 (106 for 19,610), sqlalchemy
  0.57 (12 for 2,092), pydantic 0.53 (3 for 564), from 0.9, 1.2 and 0.5 (`scratch/hint_errors.py`).
  No fix: a hint naming a module bare, a well-known class's name the module binds to its own class,
  a builtin given type arguments, a private part of a dotted name, a function's class, `Never`,
  pyrefly's `Self` where the method's signature doesn't say `Self`, and a standard-library module's
  attribute the module hasn't at run time (`sys.OptExcInfo`); an alias of a union is the union, for
  the narrowing rule and inside a container (pandas's `Scalar`); a name the function compares with
  `None` takes `None`; and a file checked again within a round has its hints moved past the lines
  its earlier checks added (`runs.shifted`), where they sat on the wrong name. Left, by rc.2's
  causes: an annotation narrower than a later value (the hint is the first value's type), a hint
  narrower than the package's own checker reads the value (`message.get("more_body")`, `bool` to
  basedpyright and `bool | None` to mypy), the same name imported from elsewhere (`Image`,
  `ValidationError`), which only the checker's definition link tells apart.
- **No new type errors**: a corpus run's `types` step runs pydantic's, sqlalchemy's and pandas's own
  type checkers after `--fix` (none new but released errors in a new place) and
  `--fix --unsafe-fixes`. Where a checker would see a value otherwise, the fix is changed, made a
  guess, or not offered (see [FIXES.md](FIXES.md#what-a-type-checker-sees)): a name bound again
  takes every value (one type the file spells two ways, `CoreSchema` and `core_schema.CoreSchema`,
  counting once), and one first bound to no known type is a guess by a later binding's; a read of a
  union, or of what the function tests, is a guess, and one of an `X | None` it tests or stores
  isn't offered; an ALL_CAPS constant passed to a call is `Final`; a read a test around it narrows
  isn't offered its declared type; `Self` where the method says so; no generic class written bare,
  the standard library's included; no alias its module assigns in two branches (a variable, to a
  checker) written in another file; a constructor guessed only where its callee is a type; and a
  class's variable held to what a class above it declares (`limit: int | None`, or a builtin base's
  own `errno`). The unsafe runs' new errors went from 20, 76 and 165 (0.2.4) to 1, 12 and 32. No
  guess for a name bound again to a call on itself (`match = match.groupdict()`, behind `or` too),
  to an empty display of another class, or past a loop to a value of no known type, nor for a
  display widened by a value a test narrows where it's added. On the 0.4.0-rc.3 mega run, after
  `--fix --unsafe-fixes`, the packages' own checkers find 22 new errors, 14 of them mypy's over
  `lxml` (an `etree.Element` its environment can't follow), and 20 of the 33,448 guesses a checker
  read are blamed for one: under one in each hundred on every package (`scratch/guess_report.py`).
- **Safe by construction**: touches no class body but a plain class's, and that as a guess (no
  decorator, no metaclass, every base plain, a test case or a builtin exception or value class),
  keeps line endings and encodings, edits notebooks' cells in place, nothing broken on any corpus,
  and the corpus packages' own test suites pass identically before and after. One pass converges on
  every corpus, the standard library's tests included: a library type a callee's module doesn't
  import yet is named for its callers by the import its own fixes add, and a file checked again
  after its text is fixed keeps what its first check wrote.
- **Fast enough**: the standard library checks in about 8s with `--jobs=1` and 1.5s with `--jobs=0`
  on 16 cores (from 227s profiled at 0.2.4): one shared walk of each module, kept with its tree from
  the cross-file index to the check, and a node's children listed without `ast`'s generators;
  whether a fix is a guess worked out only where there is a fix; each function's body indexed once
  for its empty containers; functions checked callees first; files in `order.plan`'s order, each as
  soon as the modules it calls into are done. Profiled again at 0.3.1, with the cross-file fixes
  since: the standard library with its tests (1,867 files) checks in 108s with `--jobs=1` and 35s
  with `--jobs=0` on 8 cores (from 185s and 62s), each function walked only for what the module has
  in it (a `yield`, a shadowed import, a call to another file's function), and another file's
  functions and members written for a file only where it uses them. A build from a checkout
  generates the standard-library tables in about 12s on 4 cores (from 70s): each configuration read
  in a worker process, and what a class takes, a name's definition and a class's members worked out
  once.
- **Workers that start loaded, told once**: a fork server imports `constricter.cli.command`, its
  tables read, before it forks a worker (`workers._preload`; 38 MB): one worker starts in 9 ms, 8 in
  14 ms, the server itself in 74 ms once a run (`scratch/worker_start.py --alone`). The index is
  pickled once and written once, to a file in a directory the `Workers` own, which each worker maps
  (`Workers.tell`): a pool pickled it again down each worker's pipe. Telling 16 workers the standard
  library's 8.3 MB index takes 0.28s, from 0.33s (0.18s for one), and the parent holds nothing more
  as it tells, from up to 37 MB on pandas (`scratch/index_sent.py`); what's left is each worker's
  own `pickle.loads`, 0.06s alone and 0.17s with 16 at once on 16 CPUs.
- **A file checked again, by what's new**: a file whose functions' parameters every call types is
  checked again from where its first check ended (`checker._resumed`), and only the scopes that
  round checks anew are finished again (their late fixes), not those its first check finished. The
  second round costs, of the first, 5% on the standard library in one process, 3% on django, 7% on
  pip and about none on pandas (`scratch/second_round.py`), from 6%, 4%, 11% and none; the findings
  and fixes are the same with one worker and with four.
- **Only the classes a file uses**: a class spelled through a module a file imports
  (`test.test_x.C`, any of a package's) has its line of bases worked out when the check asks for it,
  and kept (`own_types.Lineages`); one whose members the file takes none of is known as a class only
  where the file writes it. What a check knows of a file from outside it is 8 MiB over the standard
  library's 1,869 files, from 54 MiB: a test file importing `test.support`, 77 KiB from 1,164
  (`scratch/outside_size.py`), with the same fixes there and on pandas and pydantic, widened or not.

- **A compiled wheel**: mypyc compiles the `rules` and `fix` packages, all 93 of their modules, as
  they're annotated, into a wheel for each 64-bit platform and CPython 3.11 to 3.14 beside the pure
  one (`[tool.hatch.build.targets.wheel.hooks.mypyc]`, off by default; `build.yml`, by
  cibuildwheel), with no runtime dependency. On pydantic it gives the same findings and the same
  `--fix` as the pure build, 1.27 times as fast in one process (5.0s from 6.4s) and 1.15 times with
  every CPU on 8. Compiled code runs as its annotations say, so where Python and typeshed differ the
  code is written another way (CONTRIBUTING lists the kinds), and the two frozen dataclasses the
  workers are sent pickle by their fields. The whole suite runs on it in CI (Compiled), but for the
  six tests that patch a compiled module's globals (`interpreted`). On every corpus
  (`tests/corpus/runs/compiled.toml`, the pure and the compiled wheel each beside the same packages,
  `scratch/compiled_venv.py`) the findings and the fixes are the same, the check 1.37 times as fast
  in one process and 1.26 times with 4 workers (the medians of 47 corpora, on 16CPU/60GB). A wheel
  beside other packages fixes by their types too: against `dev`'s venv, which has the dev group's,
  five corpora differed (docutils's types for sphinx, click's for uvicorn).
- **Installed stubs, as PEP 561 orders them.** Built in `44c05d5`: `installed.search_path()` reads
  the checked code's environment (`VIRTUAL_ENV`) before constricter's own, `locate()` takes a
  `-stubs` package first in any directory, a partial one leaving a module it lacks to the package,
  and a namespace package's typed subpackage (`google/auth/py.typed`). On the corpus runs
  `local/.venv`'s untyped `docutils`, `pandas`, `pygments`, `yaml`, `dateutil` and `six` shadowed
  the corpus environments' `docutils-stubs`, `pygments-stubs` (sphinx), `pandas-stubs` (altair,
  narwhals, seaborn), `yaml-stubs` and `dateutil-stubs`: sphinx's 102 `docutils.nodes.*` calls with
  no fix were `imported`. About 145 direct calls and the chains they start (sphinx 491, seaborn 383
  `receiver`/`member` calls; a few hundred, estimated: [type sources](research/type-sources.md)). On
  the 0.4.3-rc.5 mega run (`9892f71`, 16CPU/60GB, 82 minutes), against rc.1's (`264d149`): certain
  fixes sphinx 3,228 from 3,128, seaborn 650 from 639, altair 378 and narwhals 980 from 982, no new
  type error (narwhals's certain tier 19 from 23): the chains estimated didn't come. Done when a
  super run gives sphinx, seaborn, altair and narwhals the stubs' fixes, no new type error. Coverage
  up to 0.2%. The 0.4.3-rc.2 super run already ran on `44c05d5`: sphinx's certain fixes 3,128 to
  3,230 (+102) against the 0.4.3-rc.1 mega run (`264d149`), unsafe 3,949 to 4,130, rc.3 the same
  again; seaborn, altair and narwhals are mega corpora, so not yet measured. One new type error in
  every tier: `sub_node_copy = node.copy()` (`sphinx/environment/adapters/toctree.py:552`) is fixed
  `Node`, the parameter's declared type, where the stubs' `copy() -> Self` meets a receiver an
  `isinstance` narrowed to `nodes.reference | nodes.title`, and mypy then rejects `[sub_node_copy]`
  as a `list[Element]`. A method returning its receiver's type on a receiver an `isinstance` narrows
  is no fix since (`Scope._takes_narrowed`, `narrowed.checked_to`): on the 0.4.3-rc.4 super run
  (`46bdc27`) no patch types `sub_node_copy`, and sphinx has one type error fewer in every tier than
  rc.3 (certain 4 from 5, basedpyright 8 from 9), its certain fixes 3,228.
- **Returns the trace records** (`traced`, a guess): the tracer records what each function returned
  at the line it returned from (`<return>`, `sys.monitoring`'s `PY_RETURN`; a function binding no
  name too, its lines not followed; not a generator's), and `--infer-from` gives LVA014 a function's
  return where its own `return`s decide nothing (`traced.hints`, `Hints.returns`): only where the
  run took every way out of the function (each `return` with a value, and its end where it can fall
  off it), up to three types' union, not a typing form (`Union` from an `__or__`). A value a
  function returns was the largest pool of the 0.4.3-rc.1 mega run's 103,514 calls with no fix
  (`member` 20,975, `untyped` 7,919, `local` 6,324). On pydantic, which annotates its returns, 2
  returns and 1 binding; on django, 10 of its test labels (4,994 of its 17,578 tests, one process on
  16CPU/60GB), `--fix --unsafe-fixes --extend-select LVA014` typed 5,912 bindings from 5,445 (+8.6%)
  and wrote 625 signatures from the trace. On the mega run of 2026-10-27 (`mega-10-27-2026-0131`, 91
  minutes on 16CPU/60GB, django's whole suite traced) the `infer-trace` step typed 134,844 bindings
  of 292,568 (+979 on rc.8), its new type errors 29 outside sqlalchemy's `typing_extensions` cascade
  (rc.8's 32), 2 of them blamed on `traced`: clean.
- **Declared types of installed packages with no `py.typed`, as guesses** (`declared`,
  `installed.as_untyped`): such a package's modules join the index with their functions' and
  methods' declared returns as `returned` guesses resting on `declared`, followed through its
  re-exports (`pd.date_range`), as pyright reads one with `useLibraryCodeForTypes`; its classes'
  attributes, classmethods and overloads aren't offered. pandas/core declares 73% of its functions'
  returns, wheel 86%, setuptools 54%. On dask (its pandas 3.0.6 untyped; one process on
  16CPU/60GB), `--fix --unsafe-fixes` 5,788 fixes from 5,700 (+0.36% of its offences). The modules
  whose classes are typing forms, typed by typeshed (`typing_extensions`, `_typeshed`), are never
  read so (`installed._FORMS`): on the mega run of 2026-10-27, sqlalchemy's `typing_extensions`
  4.16.0, installed as source, made `_T: TypeVar = TypeVar("_T")` guesses and 5,516 new type
  errors. `mypy_extensions` is read for its classes alone (`u8`, `i64`; `_CLASSES_ALONE`), its
  typing forms being no class: listed on mypy's checkout (`--unsafe-fixes --show-fixes`, one
  process), 6,337 fixes from 6,314, the 23 `tag: u8` the guard had cost. On the mega runs of
  2026-10-27 and 10-28 (`mega-10-27-2026-0131`, `mega-10-28-2026-0057`, 16CPU/60GB) the whole sets
  `declared+returned` (350 guesses, 179 told, 100% held, none of 211 checked blamed),
  `declared+returned+unpack` (128, 121, 98.3%, none of 121) and `constructor+declared+returned`
  (57, 44, 100%, none of 47) passed [LIKELY.md](LIKELY.md)'s bars and are in `offences.LIKELY`
  since. `reads`, which passed as a mechanism (57 guesses, 26 told, 96.2%, none of 19 blamed),
  passes as no whole set: its 12 sets have 14 guesses at most. On the mega run of 2026-10-28 on
  `6b0ab18` (`mega-10-28-2026-0826`, 69 minutes on 16CPU/60GB), with both: new type errors 428, as
  on `b6ac32b`, none blamed on the three sets; `--likely` 211,064 bindings typed from 210,500, and
  mypy's 23 `tag: u8` back in every tier.
- **A class under a base that binds its parameters**: a subscripted base makes a checked file's
  class generic only where its subscript may pass a type variable (`concrete.binds_all`,
  [FIXES.md](FIXES.md)); one naming another module's names is settled through the index, bare where
  each is a class, a type alias or a type variable with a default (`modules.concrete_in`,
  `project.defaulted`). xarray's 1,244 `Dataset()` calls were `declined` before. On the mega run of
  2026-10-29 (`mega-10-29-2026-1139` on `f7d53b2`, 89 minutes on 16CPU/60GB) xarray's bindings with
  no fix 11,247 from 14,326 and sqlalchemy's 9,662 from 10,140, as measured alone.
- **A `dict`'s `get` and `pop` given a default**: `d.get(k, [])` on a `dict[str, list[int]]` is a
  `list[int]` and `d.pop(k, None)` a `V | None`, as a checker picks typeshed's overload
  (`returns._defaulted`); 199 such calls on the 47 corpora. No new type error on the mega run of
  2026-10-29.
- **Names a chain of star imports re-exports**, followed `HOPS` deep for a call's return and a
  class's members (`project.starred_origin`, `starred_names`), a class spelt two ways one class
  where `reads` asks (`reads._merge_spellings`); a module's `__all__` isn't read. On the mega run of
  2026-10-29 networkx's bindings with no fix 16,022 from 16,046, dask's 18,248 from 18,356.
- **A text's operator with a value of no known type** (`operand`, a guess): `"pre-" + x`,
  `x + ".pyc"` and `" " * n` take the text's type (`inference._with_text`), a guess only where the
  value's type rests on it (`guesses._rests_on_operands`). On the mega run of 2026-10-29: 324
  guesses, 193 told, 100% held, none of 163 read blamed, and its set `literal+operand` 127 with 64
  told: it passes [LIKELY.md](LIKELY.md)'s bars.
- **A standard-library base's single-underscore members**: the tables hold a class's `_private`
  methods too, not a dunder but `__enter__`, `__aenter__` and `__getitem__`, nor a mangled `__x`
  (`stdlib_tables/reading._read`), so `self._expand_help(action)` in a `HelpFormatter` subclass is a
  `str`: 129 more methods in `methods.json`. Measured alone (one process on 16CPU/60GB): pdm +6
  fixes, pip +3, the standard library +15, none lost.
- **Overloads that agree on their return**: a checked file's overloads all declaring one return,
  and the implementation that one or none, are read as its declared return (`usable.agreed`), so
  `DataTree.from_dict(groups)` is typed with `groups` of no known type (276 such calls on xarray).
  None of the mega run of 2026-10-29's new type errors is from it.
- **The members of a class imported for type checking alone**: a file's own `if TYPE_CHECKING:`
  imports are taken as its run-time ones are (`crossed.imported`), so `info.size()` on an
  `info: Info` imported that way is typed. pydantic 1,131 fixes to 1,141 and xarray 9,067 to 9,122,
  measured alone (one process on 16CPU/60GB); the mega runs of 2026-10-29 covered its census.
  Through it guesses copy sqlalchemy's own bare `_InternalEntityType`, a generic alias, into other
  files ([ROADMAP.md](ROADMAP.md), Small).
- **A generic class whose every parameter has a default**, written bare as a type checker reads it
  with them: each module records its type variables with a default and what its generic classes'
  bases name, and the index drops from `generics` those whose every such name resolves to one
  (`modules.settled`, `defaulted_in`), installed modules' too; a `Generic[...]` or `Protocol[...]`
  listing another module's type variable gives the class its parameters (`declarations._params`).
  sqlalchemy 2,091 fixes to 2,263, measured alone. No `constructor` guess writes one bare where its
  call passes `self` of a class binding type variables, or a parameter annotated with one
  (`doubts.binds_defaults`, `Module.defaulted_generics`): mcp's 60 and strawberry-graphql's 18 new
  type errors on the mega run of 2026-10-29 at 11:39 (`f7d53b2`) were those, none at 19:20
  (`e793bc6`).
- **`return`s of one type and of `None`** give `T | None`, a guess, as a type checker infers the
  return: each recorded `return` matched to the function's own in source order, `return None` and a
  bare `return` typed `None` (`returned._returned_types`, `_or_none`). django's bindings with no fix
  11,709 from 11,712, measured alone; the mega runs check no types for django or pip.
- **A class variable across its line, and classes under inert marks**: a plain class's variable is
  joined across its line (`classvars.joined`, `plain._joined`: the widest number, `| None`,
  `tuple[T, ...]`), values fitting no one type keeping each class's own; a decorator or metaclass
  reading no annotations leaves a class plain (`source/inert.py`, `project.INERT`), none of its
  variables typed where a class in its line defines the name or the join fails
  (`classvars.unshadowed`). All `member` guesses, `--unsafe-fixes` only. On the mega runs of
  2026-10-29, bindings with no fix: pygments 2,313 from 6,695, the standard library 62,138 from
  63,071, django 11,609 from 11,747. Its type errors as measured alone (pygments 10 new and 6 gone,
  django 17 new and 43 gone, one process on 16CPU/60GB): the runs check no types for either.
- **A generic alias whose type variable is quoted**: sqlalchemy's
  `_InternalEntityType = Union["Mapper[_T]", "AliasedInsp[_T]"]` is generic by the names in its
  forward references (`modules._alias_names_any`), and a module's generic aliases are among its
  `generics`, so neither a hint's edit nor a fix writes one bare: the mega run of 2026-10-29 at
  22:41 (`d160aa8`) has no `_InternalEntityType` error, from 3.

## Command and output

- **Formats**: text, `full` (with the source line), JSON, GitHub annotations, SARIF (help text,
  `helpUri`, certain fixes as SARIF fixes, validated against the 2.1.0 schema in the tests), GitLab
  Code Quality, JUnit and rdjson (fixes as suggestions).
- `--diff`, `--show-fixes`, `--statistics`, `--explain`, `--coverage` / `--fail-under`, baselines,
  `--jobs`, standard input, `--exit-zero`, `--output-file`, and `--exclude` globs that also skip
  directory names in a walk.
- **A fix that says what it fixed**: `--fix --show-fixes` lists each fix it made after what it left,
  as text (`fixed 'x'`) or in `--format=json` (`fixed` on every entry), a later round's too, each on
  the line it had before any fix. `corpus_suite.compared` so runs constricter once for each fixed
  run it type-checks, where it ran it twice: on pydantic the one run lists the 1,084 certain fixes
  and the 1,569 with guesses that a check listed before it.
- **Notebooks** (`.ipynb`), checked and fixed per cell; every JSON file read allows comments and
  trailing commas; every public entry point takes `str` or `bytes`.

- **A walk that asks git**: a directory is walked once, entering no directory it skips (a project's
  `.venv` and `node_modules` aren't listed). In a git checkout only what git tracks there or would
  is checked (`git ls-files`), so nothing a `.gitignore` names; a path named on the command line is
  checked regardless, a directory git ignores included, and `--no-gitignore` (`gitignore = false`)
  walks whole.

## Integrations

- **Plugins** for flake8 and pylint (`C9101`–`C9112`); ruff through `lint.external`.
- **pre-commit** hooks (`constricter-fix` runs as one process, so its cross-module `--fix` sees
  every file) and pre-commit.ci; **tox**, **nox**, **Bazel** and **Pants** notes; **editor**
  settings for VS Code, Zed and Neovim.
- **A GitHub Action**: PR annotations, a per-code summary table, a `sarif-file` output, and a
  `version` input to install a PyPI release with uv; CI runs it on this project.
- **On PyPI** as `python-constricter`.

## Corpus

- **One corpus runner**: `python -m tests.corpus RUN.toml` reads a run file (the corpora, the
  constricter versions, the steps, the formats) and writes a folder of that execution's own
  (`<output>/<label>-<month>-<day>-<year>-<time>/`): a record for each corpus, version and step, and
  `report.json`, `report.md` and `tables/*.csv`, each made from the records alone. The corpora,
  their sdists and their suites are `corpora.toml`'s. Every step starts constricter one way
  (`launch.run`), on one tree a corpus (`trees.Tree`): a suite's checkout at its pinned tag, with
  its settings and environment, where a corpus has one. No other script starts constricter on a
  corpus: CI's Corpus and Profile jobs are run files, and so are a release's section of
  [RUNS.md](RUNS.md) (`runs/release.toml`, with `--label` for a pseudo-version, `0.2.4-rc.N`).
- **Its steps**: a check at every level, each fix on a copy (no crash, nothing broken, one pass),
  `--infer-with` each type checker's hints, coverage, the census of what has no fix, a timed and a
  profiled check; and on a suite's checkout with each fix's patch applied, `tests` (as released and
  after each fix), `types` (the package's own checkers, each new error traced to its fix mechanism:
  of a file's alike errors, the one on a line a fix wrote) and `traced` (each fix held to what the
  traced tests bind, then a fix by the trace). Each checker reads the checkout's own settings:
  basedpyright's server and pyrefly read pandas's, pydantic's and sqlalchemy's, but this project's,
  above it, for a checkout with none (django's), which is given empty ones (`pyrightconfig.json`,
  `pyrefly.toml`); ty reads nothing above its workspace.
- **Sized by the machine** (`tests/corpus/sizing.py`): each step is a process of its own, started
  once the CPUs it's expected to keep busy and the memory it's expected to hold are free: what its
  process tree took in the last run under the same output, which its record keeps (`used`: its
  seconds, CPU seconds and the most memory held at once), a quarter over. Where a user's systemd
  runs, a step starts in a scope of its own (`systemd-run --user --scope`) and the kernel counts
  every process in it (`memory.peak`, `cpu.stat`; `by: scope`): on pydantic, with every worker on
  16CPU/60GB, a fix step's 11 to 13 CPU seconds and 0.8 to 0.9 GB, where `psutil`'s readings, which
  count the rest, saw 1 and 0.1 to 0.2. An unmeasured traced step is sized by its suite's `tests`
  step; a step that wants all the memory runs alone, and one that held over 8 GB beside others is
  noted. The timed checks hold every CPU, and run last, one at a time, or beside the other steps
  (`timing-beside`, below). A suite's tests of one port
  run one suite at a time, and its tests are stopped after `suite-seconds`. A stopped run resumes
  under its own label, keeping its start and adding each execution's minutes, and a run exits
  non-zero on anything a fix broke or a step that failed, whose traceback its log keeps. Every
  corpus's steps wait for the machine alone (`at-once` bounds the corpora cloned and
  installed side by side): the step with the most seconds still behind it first, its own and its
  suite's steps' after it, and what's free kept for one that waited five minutes. A running step's
  hold follows what it's using: an unmeasured one gives back what it isn't a minute in, and any one
  takes what it uses over its share from the next to start; a step too short to be read is counted
  by the system's own total, its CPU seconds and its largest process's most memory. A step is sized
  by a run of its own label before any other's (a probe's steps size only what no run of the label
  measured), and `check` and `census`, which read one check that the first to start runs, by the
  most either took.
- **Class bodies' fixes, held to the suites**: a plain class's variable typed past a literal (a test
  case's own, a value the standard library types, a checked file's class it names) brings no new
  type error and no test that differs on any corpus package's suite after `--fix --unsafe-fixes`.
  One fix lost: a class's members reserve the names their types need imported (`multiprocessing`'s
  `Process`), so asyncio's `proc: Process` has none.
- **The standard library, pinned**: the standard-library corpus is CPython 3.14.7's source release's
  `Lib` (`corpora.toml`, fetched and hash-checked as Twisted's sdist is), not the running Python's
  own, which a prebuilt Python ships without its `test` package (1,205 of the 1,867 files): CI's
  check of it on uv's prebuilt 3.14.7, which has none, counts all 1,867. Any Python 3.14 runs the
  corpora: uv's prebuilt 3.14.7 checks pandas in 55.3s in one process and 9.3s with every CPU, a
  source build with profile-guided and link-time optimization and no shared library 57.9s and 9.5s,
  and pyenv's `python-build` (`-O3 --enable-shared` alone) 68.5s and 11.7s.
- **The witness, past a container's class**: a builtin container is held to its annotation's
  arguments, not its class alone: a list's, a deque's or a tuple's first 100 elements, a set's every
  one, a dict's keys and values, a tuple's parts one by one. Only a value of the builtin class
  itself (a subclass may run its own code as it's read), and what can't be told of an element can't
  be told of its container. Five more of sqlalchemy's certain fixes differ so (20 of 1,026, from
  15), each a declaration of its own its tests contradict (`tables: set[TableClause]`, holding a
  `Subquery`); none more of pydantic's 482. `typeguard` and `beartype` were weighed for it
  (`scratch/witness_checkers.py`): of the 50,957 fixes pydantic's, pandas's, sqlalchemy's and
  django's suites judge, 3,333 are containers their tests bind, and 315 of those hold an element the
  annotation doesn't name outright. `beartype` checks one element, chosen at random, and calls a
  container's own `__len__`; `typeguard` checks them all, and is kept for annotations held to a run
  (below).
- **Fewer runs for the same counts**: a suite's traced tests start once `fix-unsafe` has ended and
  the other steps have their copies, and its type checks run beside its tests, on a checkout of
  their own. Its tests run after every guess first: the same as released, they stand for the tiers
  under it (`implied`), and a run file's `tests-hinted = false` leaves out the runs after each
  checker's hints and the trace's fix. One check at `suffocate` gives every level's counts (a level
  chooses the codes it reports and which are errors, no more) and the census; CI's run file checks
  at each (`every-level`). A traced run has `constricter` alone on its path, not this checkout's
  `tests`. A run's `mechanisms` table counts each fix's fixes by their whole set of mechanisms,
  which a guess is likely by, and by tier.
- **A suite's own differences, told apart**: a fixed run whose tests differ is run again, with the
  released tests, the trace's fix as any other: a failure is the fix's only if both fixed runs have
  it and no released run does (nibabel's and litestar's come and go: litestar's
  `test_request_body_logging_middleware` failed one of two runs after `--fix --unsafe-fixes`, and
  `test_websocket_stream_applies_guards` the other). `corpora.toml` names the tests a fix may
  change, each with why (`differs`: black's `test_piping`, which asserts its own source is as black
  formats it); a run reports them apart, and one whose only differences are named exits 0.
- **celery's suite, part by part** (`parts`): in one process its tests held 25 GB (28 GB traced),
  whatever pytest captures or logs; a directory of `t/unit` at a time, each a process, 4.6 GB at
  most (`t/unit/concurrency`; 5.8 GB traced), the same 3,521 passed and 3 failed, in 107s from 131s.
  The parts' traces are joined (`recording.merged`).
- **A traced suite's time, by its parts**: a run's `traced` table has each suite's traced tests'
  seconds beside its released tests' untraced, and `scratch/traced_share.py` times them under the
  tracer alone. pygments's 5,346 tests take 9s untraced, 12s under `constricter.trace` and 17s under
  the witness told its 960 fixes, from 121s and 184s: its lexers are generators, whose returns
  weren't counted, so none was ever followed no more. A function is now, whatever it is, once 20
  returns or 50,000 lines add nothing, and a line costs less (its number as given, its function
  looked up once, a class's name kept). The trace then has a little less: 87 fixes rest on
  pygments's for 89, and 567 of pydantic's fixes are told of for 572.
- **Workers for the suites that take them**: tox's tests (82s in one process, 18s on 8 workers) and
  narwhals's (74s, 19s), the same three times over. Not anyio's (8 tests of a main module fail in a
  worker), joblib's (the workers collect different tests) or websockets's (`unittest`), as
  `corpora.toml` says.
- **A suite's fixed runs, side by side**: each is a part of its own on one of the suite's `at-once`
  checkouts, started once its fix is made. In the mega run anyio's took 103s to 127s each and pint's
  28s to 41s, beside released runs of 111s and 32s; their whole tests took 586s and 219s, one after
  another, in the mega run before.
- **`tests/corpus/runs/super.toml`** asks every step of the `super` corpora (the seven and every
  fast one) and writes [RUNS.md](RUNS.md)'s `Super corpora` section from the run's folder, with the
  machine it ran on; **`mega.toml`** the same of every corpus, the seven and 40 more packages
  `corpora.toml` pins (38 with a suite read from their own CI): typed applications, `asyncio` code,
  pytest-heavy test trees, scientific packages on numpy's types, `TypedDict`s and overloads of their
  own, and untyped ones. The scripts they replace took 23 and 54 minutes on 16 CPUs (74 with every
  traceable suite's tests traced): their first runs found a crash, four packages a second pass still
  changed and 17 type errors after `--fix`, each fixed since: after `--fix` no corpus's or package's
  own checker finds a new error but one of werkzeug's (`winreg`, another platform's: pydantic's 9
  were Pyright reading this project's settings, not its own); django's suite is the same after
  `fix-plain-bases`' guesses, and one `--fix --unsafe-fixes` pass leaves a second nothing on any of
  the seven. Measured, with no gain: the fixed copies on a `tmpfs`.
- **The timed checks beside the other steps** (`timing-beside`, a run file's `[steps]` key, set in
  `super.toml` and `mega.toml`): the timed checks once ran last, alone and one at a time, since
  three corpora at once on disjoint 5-CPU sets ran 4 to 5% slower in one process and 10 to 17% with
  jobs (`scratch/timed_tail_trial.py`); that tail took 5.3 to 6.2 minutes of a mega run. But their
  instructions didn't move side by side (0.04 to 0.15%, 0.00% with jobs across runs at one commit,
  `scratch/timing_noise.py`), so the timing table compares instructions across runs (its
  `beside other steps` column, RUNS.md's intro) and the checks run sized as measured, not held to
  the end (`sizing.held_last`). Replayed on the super run of 2026-10-26
  (`scratch/schedule_sim.py --timing-beside`): 42.0 minutes from 43.5. On the mega runs of
  2026-10-26 and 2026-10-27 (16CPU/60GB) the 47 timed steps ran beside the suites and ended an hour
  before the run. The profile on the way (`py-spy`, `scratch/profile_diff.py`, 2026-10-23) took the
  standard library's check from 50.9s to 40.6s and pandas's from 57.5s to 46.9s in one process:
  `reads.members` walked every method each check, a function's body was walked again for each
  parameter, and `overloads._agreed` was hot.
- **RightTyper, measured and declined** (`scratch/righttyper_measure.py`): a sampled run's
  signatures as a corpus step. On pydantic (2026-10-24, `--ignore-annotations`, its tests in
  25.9s) the 23 parameters and 22 returns it added brought 3 more certain fixes and 45 pyright
  errors, the sampled types narrower than the functions take (`**kwargs: None`, `Self` in a
  metaclass). On django (2026-10-26, its whole suite in 336s, RightTyper 0.1.0 patched three
  ways in the script's copy: a test-local class's name, a nonzero exit before its post-processing,
  a lazy object's class read through `__getattribute__`; `--all-files`): 10,149 parameters and
  6,842 returns in 405 files, `--fix` then 4,293 certain fixes from 2,622, but basedpyright 12,879
  errors from 4,007 (`bool | dict[Never, Never]` for a setting, `type[AppConfig] | None` for a
  class). Not a corpus step: the project's own tracer's returns are held to every way out of a
  function and bring none of this.
- **Profiles and timings that can be trusted**: **`tests/corpus/corpus_profile.py`** runs the check
  under `py-spy`, which samples it from outside, its workers too (`--jobs N`), and prints each
  module's and function's own and whole time; the runner's **`timing`** step checks each version of
  a corpus at `--jobs` 1 and the run's `jobs`, under `hyperfine` where it's installed (one run to
  warm up, the exit status ignored) and in a loop of its own otherwise, keeping each run's seconds
  and, by `hyperfine`, the instructions it took, its workers' included. Their relative deviation, 10
  runs each way in one process and with every worker (`scratch/timing_trial.py`): on pandas, 12
  workers on 16CPU/60GB, the seconds' 3.52% and 3.58% by the loop, 3.66% and 1.10% by `hyperfine`
  and 2.58% and 1.02% by `pyperf command`, the instructions' 0.08% and 0.04%; on the standard
  library, 8 workers on 8CPU/60GB, 0.53% and 0.89%, 0.27% and 0.60%, 0.50% and 0.51%, and 0.06% and
  0.02%. Both on CPUs `pyperf system tune` had set. `pyperf` counts no instructions, warms up in
  every process, and stops at a nonzero exit. And the Corpus coverage workflow's comment on a pull
  request says how long a check of pydantic takes with it and with its base, the median of 5 runs
  each on the same runner: kept with the run, not per commit (`pytest-benchmark` and `asv` keep a
  history a runner's noise would fill).
- **Python 3**: the standard library, `django` (the 5.2 LTS, for 3.11), `sqlalchemy`, `pydantic` and
  `pandas` 3.0.6 (1,421 files with its tests: overloads, generics, `TYPE_CHECKING` imports).
- **Python 2**: Twisted 12.3.0 (pure Python 2, 147 of 819 files unparsable) and pip 20.3.4 (the most
  type comments in `__future__` modules), hash-pinned sdists `tests/corpus/corpus_sources.py`
  fetches.
- **What `--fix` still can't type**, counted by **`tests/corpus/corpus_untyped.py`**
  (`python -m tests.corpus.corpus_untyped`; `--rows` writes every binding as JSON lines): each
  untyped binding, classified by the statement that binds it, the shape of its value, its scope,
  whether its function is annotated, and what a call through an import resolves to and where from.
  On the seven corpora at 0.4.0: 251,517 untyped bindings, 140,562 with no fix at all, 79.0% of
  those in functions with no annotations. The items under [the roadmap](ROADMAP.md#next) are sized
  by it: each count is the bindings with no fix an item could reach, not what it would fix. Measured
  and too small to build: an unannotated parameter typed by its literal default (76 bindings) or its
  docstring (325); and signatures first, by `pyrefly infer` before `--fix`: 2,254 more certain fixes
  on the six Python 3 corpora (19.8% of their untyped bindings fixed, then 20.8%), since it
  annotates 8% of the unannotated parameters, most of the returns it adds are `-> None`, and it left
  one of pydantic's files unparsable; and the same from mypy's daemon (`dmypy suggest`,
  `scratch/dmypy_suggest.py`, 500 functions of each corpus but the standard library, which mypy
  won't check as a project's own): it stops on every one of sqlalchemy's and pandas's, takes 30s to
  90s a function on 16CPU/60GB with 14 daemons, and on django, the one with no type comments, brings
  19 certain fixes for 415 new basedpyright errors, most an `X | None` read without a check; and an
  unannotated function's `return`s of two types, or of one and `None`, joined into a union: 275 more
  fixes, and 38 new basedpyright errors (a union one of whose types is wrong, or that the caller
  never narrows); and a class variable or an attribute first `None`, set in another method
  (`timeout = None` in a class body, `self.conn = None` in `__init__`): of the 894 class-body
  `name = None`s on the Python 3 corpora, 402 aren't in a plain class, 275 are never stored by their
  module (a subclass's to set), 131 are stored another way or from outside the class, and 82 are
  assigned no literal, only values that are mostly parameters; an attribute's `T | None` types no
  read its function tests or stores, since that isn't offered; and a name a plain class's body binds
  more than once: of 594 on Django, pandas, SQLAlchemy and the standard library, 425 are a method or
  a class too, 122 are bound in an `if`'s or a `try`'s branches, and 14 by two plain assignments.
- **Why a call has no fix, counted**: `--format=json` gives a call bound with no fix the reason it
  has none (`unfixed`, `fix/values/refused.py`), and the census keeps it on each row and counts the
  calls by it (`census.md`'s "Calls with no fix, by why", the record's `reasons`). On the 0.4.3-rc.1
  mega run, 103,514 calls on the 47 corpora: `receiver` 28,934, `member` 20,975, `imported` 18,601,
  `library` 11,562, `untyped` 7,919, `local` 6,324, `declined` 5,597, `vague` 2,392, `other` 1,210.
- **Why `name = self.method()` has no fix** (8,195 bindings, before the inherited methods): the
  method is the class's own (46%), a base's in the file (12%) or in another (10%), a class attribute
  a subclass sets (`self.type2test()`, `self.dumps()`: 28%, left alone), or a library base's (5%).
  Of the 5,479 found, 4,078 have a `return` whose value has no type: a name (1,779: an unannotated
  parameter, or a local with no fix), a call on another value (823), another `self.method()` (408).
- **Other type checkers' servers**, driven through `constricter.cli.lsp.hints` on pydantic,
  sqlalchemy and django (26,716 bindings with no fix): the share of them each one's hints type, as
  `--fix` judges hints now, is 8.2% for ty, 10.7% for basedpyright and 13.7% for pyrefly. Plain
  Pyright's server has no inlay hints (they're Pylance's and basedpyright's), mypy has no server
  (`dmypy inspect` answers one location at a time), and pytype is discontinued.

- **Fewer of a suite's test runs for the same answer**: a part after a fix whose patch another
  fix's part ran is that part's (`implied`, `patch: same`), and one whose patch a clean run's holds
  is that run's (`within`): `infer-trace`'s patch was `fix-unsafe`'s on 22 of the 0.3.9-rc.1 mega
  run's 42 suites, and held it on 41. The `tests` step runs one fixed run again for each outcome
  with a failure new or gone, weighed against every released run (this run's, the traced tests',
  earlier runs' on the same checkout), and the released tests only where no other run of theirs is
  there; a fixed run whose failures are the released tests' doesn't run again, whatever its other
  counts (`calm` says whether they're some released run's). A `mega` run takes the tests as
  released from the latest earlier run on the same checkout where the traced tests' outcome equals
  them (`from`, `confirmed`), running them where it doesn't; a record is taken only with the same
  tag, checkout environment (`environment`: a hash of its Python and packages) and parser
  (`parser`: a hash of what reads a run's output), which `facts.toml` names with each checker's
  version.
- **One test run on the union of the fixes**: `infer-union` is a fix step of its own
  (`--fix --unsafe-fixes --infer-with` every checker `--infer-from` the trace, so where fixes
  conflict constricter's own come first, then the guesses, the checkers in the run's order and the
  trace), and its tests' part runs before every fix's, which stand on it where it was the released
  tests' (`patch: union`) and run as before where it wasn't. It assumes what the tiers' implication
  does: fewer annotations don't fail where more passed. The 0.4.0-rc.2 mega run, the first with it,
  took 91 minutes on 16CPU/60GB (rc.1's 134) and 1,098 CPU-minutes (1,655), with the same fixes and
  tests table and no test a fix broke: the union's run was the released tests' on 38 of 42 suites,
  and 266 fixed parts stood on it. On django, nibabel, black and sphinx it wasn't, by a timing test
  (django's `test_crafted_xml_performance`) and tests no fix's own run failed, flaky under load.
- **A run for a change's direction** (`tests/corpus/runs/direction.toml`): every fast corpus,
  pydantic and sqlalchemy, each fix tier and coverage, no suite steps. On the 44 corpora whose tag
  held between two mega runs the fix counts moved on 31 to 36 by a median -0.14% (certain), -0.13%
  (likely) and -0.32% (unsafe), and the fast sets gave each the right sign at about twice the size
  (`infer-ty` noisier: -1.74% against -0.38%); offences didn't move. CONTRIBUTING says when each run
  file is the one: the suites at full breadth, and every size, in a release's super and mega runs.
- **What the records hold, tabled**: `unshared`, the likely fixes the unsafe fixes leave out or
  write otherwise (the fixes interact: on the 0.4.0-rc.3 mega run pandas's 216, networkx's 52 and
  dask's 2 are absent from unsafe); `uncounted`, a fix step whose bindings typed after aren't those
  typed before and those fixed (mypy's and sphinx's one each); and `resampled`, a suite's traced
  tests beside its released tests, a flakiness sample for free (the same failures on all but 6).
  The first two are listed only where they differ, from the fix steps' `.fixes.jsonl` and records.
- **A traced run under twice its untraced time, unsampled**: on the 0.4.3-rc.2 super run
  (`44c05d5`, 16CPU/60GB) pydantic's and django's traced tests took 1.04 and 1.10 times their
  untraced (55.6s against 53.7s, 52.8s against 48.2s), pandas's, the slowest, 1.37 (135.1s against
  98.5s). Sampling in short windows (`sys.monitoring`'s events off between them) is left for a
  corpus whose traced tests grow past twice.
- **A suite's traced tests, in more than one process.** django's are traced on its workers: a
  process the traced run forks records on and writes its trace as it ends (`trace.forked`), and a
  suite run by `python -c` is traced by its own command (`corpus_suite._traceable`). On the
  0.4.3-rc.2 super run (`44c05d5`, 16CPU/60GB) django's `traced` step took 65.1s, from 643s on the
  0.4.0-rc.3 mega run, its tests 52.8s against 48.2s untraced, 482 fixes resting on the trace.
  celery's 13 parts are now traced side by side too, as its tests run (`corpus_suite.traced`), each
  writing a trace of its own, merged in the parts' order. On the 0.4.3-rc.5 mega run (`9892f71`,
  16CPU/60GB, 82 minutes) celery's `traced` took 85s, from 163s and 182s on rc.1's two, its released
  tests 59s there. Done when a mega run's celery `traced` step takes about its `tests` step's time,
  the fixes resting on the trace the same. Coverage unchanged.
- **sqlalchemy's tests in a fixed order.** A part stands for another only where its counts equal the
  released tests' exactly (`_tests_part`, `standing`). On the 0.4.3-rc.4 super run (`46bdc27`)
  sqlalchemy's traced tests skipped 971, so rc.3's released record (975) wasn't confirmed and the
  released tests ran again (973), and `infer-union`'s skipped 975, two of `ReturningTest`'s
  `test_imv_returning_datatypes[...LargeBinary1/2]` skipped where they passed: so it stood for none,
  and six fixed trees ran the suite apart, 83 to 111s on 7 to 15 CPUs each, 6,229 CPU seconds more
  than rc.3, on one checkout one after another, while 22 steps wanting 8 CPUs waited up to 15
  minutes: the `tests` stage 20.5 minutes from 12 (`scratch/stage_compare.py`). The flake is
  sqlalchemy's test harness: a `testing.combinations` case's own requirement (`uuid_data_type`) is
  added at call time to the compound exclusion the test function already carries
  (`exclusions.compound.__call__` extends `fn._sa_exclusion_extend` in place), so once a UUID case
  of `test_imv_returning_datatypes` runs, every later case in that process skips (alone, its
  LargeBinary cases pass 8 of 8; after the UUID ones, 2 pass and 26 skip), and xdist's `load`
  distribution changes, run to run and by worker count, which cases follow one on a worker.
  `--dist loadscope` isn't enough: the three drivers' classes share the suite's functions, and
  `ReturningTest` alone gave 91 passed with 2 workers and 93 with 8. sqlalchemy's tests run
  `--dist loadfile` since (`corpora.toml`), a file's tests on one worker in order:
  `test/dialect/test_suite.py`, the one file running the shared suite on SQLite, gave the same
  outcome for each of its 3,259 tests with 2 workers and with 8, 2,971 passed and 288 skipped, in
  6.3s and 6.9s; the whole suite (`test/`, 30,448 tests on 16CPU/60GB) the same outcome for each
  test with 13 workers and with 4, 29,457 passed and 991 skipped, in 88s and 112s (the released
  tests' 90s on 13 under `load`). On the 0.4.3-rc.5 mega run (`9892f71`, 16CPU/60GB, 82 minutes) the
  released tests ran again (114s) and the union's part (112s) stood for every fixed tree
  (`tests-fix-likely` 0s, implied). Done when a run's `infer-union` part stands for sqlalchemy's
  fixed trees again and its `tests` stage takes about rc.3's 12 minutes. Coverage unchanged.
- **One type at run time, no fix**: the `traced` step keeps the types the trace saw each of the
  package's bindings hold (`traced.seen.jsonl`), and the report holds the census's bindings with
  neither a fix nor a guess to them, by shape (`one-type.csv`, its commonest source of each; the
  Markdown leaves the sources out). On the 0.4.3-rc.7 mega run (`5674049`, 16CPU/60GB, 68
  minutes), of 162,001 such bindings the traced tests reached 79,623 and saw 60,259 hold one type:
  the upper bound of any inference there, and where a binding bound otherwise is worth a look.
- **The hinted steps' servers, sized by the memory free**: memory, not CPUs, kept the 0.4.3-rc.2
  super run's steps waiting (pandas's `infer-union`, all three checkers' servers at once, held
  28.5 GB for 10.5 minutes). The runner's `infer-union` asks its checkers in turn
  (`--infer-in-turn`, each one's servers shut down before the next's start), sized by its largest
  checker's step until measured. A hinted step starts with as few CPUs as hold one server of each
  of its checkers for the corpus (`Plan._hinted`) and takes more as they free, its servers given
  that share of the 8 GB default rounded up to whole servers (`Wanted.hinted`, `Wanted.server`);
  only one whose last run took 300s at most starts short (`sizing._BRIEF`), as a short start keeps
  its CPUs for the whole step. On the 0.4.3-rc.6 mega run (`c7f4db0`, 16CPU/60GB, 65 minutes)
  pandas's `infer-union` held 14.3 GB, and the run used 77% of its CPU seconds (rc.7 75%).
- **basedpyright's heap, capped**: Node 24's own cap was 4.2 GB whatever a server's share, and
  basedpyright empties its caches near it. Each server's heap is capped at nine tenths of its share
  of the memory (`NODE_OPTIONS=--max-old-space-size`, `Checker.share`), and a capped server that
  exits is restarted and asked about its files alone, as a hung one is (`ExitedError`), a file it
  exits on again left without hints and not remembered. A file a server hung on in an earlier run
  gets no hints rather than none of its answers (`Session.hints`), and a fix or census step whose
  constricter ends at an exception fails (`pipeline._crashed`). On the 0.4.3-rc.4 super run
  (`46bdc27`, 16CPU/60GB) every stage exited 0 and no hinted process crashed; its
  `infer-basedpyright` checker fixes are rc.2's (`44c05d5`) on all five corpora, 8,630 in both,
  pandas's 6 more and sqlalchemy's 1 fewer (`type_: TypeEngine[_T]`).

- **The witness, past a test's own classes**: a value of a class a test module defines, a mock or
  a `mock.sentinel` object, or a `SimpleNamespace` tells nothing of the annotation, nor does an
  annotation naming a test's class outside the tests; a class a function defines again at each
  call is the annotation's by its module and qualified name; a descriptor class an attribute is
  annotated with is read through an instance as its `__get__` declares (`declarations.descriptors`).
  A verdict tells of its first 3 differing values, each the value's class and the annotation
  evaluated (`differed`), so a misjudgment can be read from the run. Read through on the
  0.4.3-rc.8 mega run (`7a075e4`) and the super run of 2026-10-25 (`722e868`): of rc.8's 10 new
  differing certain fixes, 7 are declarations the tests contradict (pandas's numpy scalars,
  types-docutils' stubs, sqlalchemy's untold value); pdm's `dep: str` was given tomlkit
  `InlineTable`s (pdm's own `deps: list[str]` contradicted), and its `url` and strawberry's `node`
  didn't differ again; strawberry's other differing fixes are its own `cast("Edge[NodeType]", ...)`
  of a class and declarations of instances given classes. The one misjudgment, pdm's
  `mock.sentinel` values, is fixed.
- **The runner's schedule, held to the solver's shortest**: every corpus's steps wait for the
  machine alone, the one with the most seconds behind it first, and a running step's hold follows
  what it uses (`tests/corpus/sizing.py`): a step that can't start holds back none after it, a
  suite's measured tests hold the CPUs they kept busy with a margin over, an unmeasured part takes
  its kind's largest measured part, and an unmeasured `infer-union`, its checkers asked in turn, the
  largest checker's step's memory. Where OR-Tools is installed (the `corpus` and `dev` groups, and
  CI's corpus setup), the runner plans its steps with CP-SAT before it starts
  (`tests/corpus/planning.py`: each step held to what the runner will hold for it,
  `sizing.Plan.wanted`, ports, each step after those it reads) and, of the steps that could start,
  starts the one planned first; a step no run has measured keeps the rules (the longest chain first,
  `_PATIENCE`, backfilling), and a stage plans its own steps alone (`planning.ranks`'s `chosen`).
  `scratch/run_timeline.py` lays a run out from its records, `scratch/schedule_sim.py` replays it,
  and `scratch/schedule_solve.py` plans a finished run's steps the same way and proves how short any
  schedule of them can be. Read against the solver with 16 CPUs and 36 GB: the 0.4.3-rc.1 mega run
  95.2 minutes against a shortest 85.2 (11.7% over), rc.5 81.3 against 66.0 (23%), rc.6 64.3 against
  55.6 (16%), rc.7 67.7 against 57.9 (17%), rc.8 69.6 against 58.9 (18%), and the 0.4.3-rc.1
  mega-fast run 56.2 against 45.6 (23%); the 0.4.3-rc.2 super run, in one sitting, 47.6 against a
  shortest 47.7, its pandas `infer-union` of 630s the floor; the super run of 2026-10-26 (`b5f720c`,
  42.1 minutes on 16CPU/60GB, in one sitting) at the shortest the solver finds (43.2 in 60 seconds,
  42.6 in 300, proved at least 19.7), its waits memory's (3,791 minutes in all, the hinted steps
  holding 11 to 15 GB each); and the mega run of 2026-10-26 (`mega-10-26-2026-2120`, 98 minutes on
  16CPU/60GB, with `timing-beside`) 96.0 against 93.5 in 300 seconds (proved at least 56.0), within
  a tenth. In stages, the barriers cost most, not the order: replayed on 2026-10-24 with 16 CPUs and
  29 GB, the runner's order replays the 0.4.3-rc.4 super run in 38.5 minutes against its 51.8 in
  stages, and rc.3 and rc.4 took 47.7 and 51.8 against a shortest 30.5 and 35.7 with no stages. A
  run's share of its CPU seconds isn't the measure (85% was the target before): memory and the timed
  tail bound it whatever the order, and the 0.4.0-rc.1 mega run, within a tenth of its floor, used
  77.5%; the timed tail, a super run's last 2.5 minutes at under one CPU, went with `timing-beside`.
  Weighed and left: ordering by most CPU seconds with `_PATIENCE` 600s and `_BESIDE` 60s replays
  three super runs in 87.6 minutes summed against the rules' (300s, 300s) 102, but the rules order
  only the steps no run has measured; and no library runs subprocess steps in a graph under CPUs and
  memory as the runner does (Snakemake's scheduler comes nearest, a workflow engine whole; Dask's
  and Ray's resources are their workers' Python tasks').
- **Test results as data**: a suite's tests were read from pytest's and unittest's text alone, which
  misread sphinx's captured log lines as failures and spelled 4 suites' failure ids two ways between
  runs. Each part pytest runs writes a JUnit report (`--junitxml`, the `xunit1` family), read into
  `records/<corpus>/<version>/tests-<run>.tests.jsonl`, a line a test with its id (from the class
  name: pytest's cached rewritten modules keep the `file` of where a checkout was before), outcome,
  seconds and skip reason; the failed tests are the reports' where every part wrote one, the counts
  stay the summary's (the reports don't tell an unexpected pass from a pass), and a suite unittest
  runs (django, mkdocs, twisted) is read as text still. Each fixed run's record names the tests it
  skipped where the tests as released ran them, and the reverse (`skipped anew`, `skipped no more`;
  `suite_steps._skips`), and the tests table counts them (`report_tables._tests`): the union's own
  run is a row of its own (`infer-union`), an implied part shows the skips of the run that stands
  for it, and the released tests are read from the earlier run's folder they were taken from
  (`from`) where this one's doesn't hold them. On the 0.4.3-rc.7 and rc.8 mega runs no test's skip
  moved. The released tests are found in the earlier run's folder under whichever version label it
  kept them (`report_tables._released`): the mega run of 2026-10-27 took sqlalchemy's from a super
  run's `super+dev`, and its columns were blank until then; written again from its records, none of
  sqlalchemy's skips moved.
- **What stub packages add to the corpora, measured** (`scratch/stubs_measure.py`, 2026-10-28, one
  process on 16CPU/60GB): pandas-stubs 3.0.5.260914, scipy-stubs 1.18.1.1, pyarrow-stubs
  20.0.0.20260819 and types-PyYAML 6.0.12.20260906, each put on `PYTHONPATH` alone, then together,
  against each environment as installed and against pyrefly's `stubgen` stubs of the same package.
  Fixes listed by `--unsafe-fixes --show-fixes`; bindings no checker's error was read for.
  pandas-stubs moves fixes to certain but adds none: on dask 5,811 from 5,815 (certain 3,216 from
  3,120, likely 1,736 from 1,769, guesses 859 from 926), on xarray 6,937 from 7,018 (certain 3,662
  from 3,557, guesses 259 from 384). What it loses is chiefly dask's 133 `pd.Series(...)`
  constructor guesses: its `Series` is generic, and a generic class written without its arguments is
  no fix. pyrefly's stubs of pandas give dask 5,848 and xarray 6,999, fewer certain gains (3,134,
  3,641) and fewer losses. pyarrow-stubs: dask 3 more (its pyarrow is 26, the stubs 20), pandas,
  where pyarrow isn't installed, 5 fewer (`pa.Scalar` generic there too); types-PyYAML nothing on
  dask or xarray; networkx nothing under any set, pandas-stubs or scipy-stubs, its scipy calls
  inside functions and their returns arrays `vague` refuses.
- **A new error blamed on the fix it names**: `corpus_suite._blamed` takes, of the fixes in an
  error's line, one whose annotation holds a type the message quotes before the nearest one before
  it: optuna's `params: dict[str, int | float]` error is the `copy+filled` guess's, not `name: str`'s
  in the same line. A second pass's `left` counts its added lines alone (`corpus_table.added`), no
  `+++` header among them: the standard library's one line left 1, from 2. Both on the mega run of
  2026-10-29 at 22:41 (`d160aa8`).

## CI, security and releases

- **CI** (`ci.yml`): every check in [CONTRIBUTING](CONTRIBUTING.md#development), the pre-commit
  hook, Markdown, tests on Linux, macOS and Windows × Python 3.11–3.14 plus PyPy 3.11 and
  free-threaded 3.14 (100% branch coverage), the build and a wheel smoke test, the Action, and the
  corpus. The project's own code passes `--level=suffocate --all-scopes` at 100% annotation
  coverage. A tree CI already passed (the merge to `main` after its pull request, the release tag on
  it) isn't tested again: a `tested-tree` artifact records each passing tree, and the next run on it
  skips every job.
- **The layers, checked**: `import-linter` holds `constricter.fix`'s four layers to importing only
  those before them, the rules and the fixes to importing neither the command nor the plugins, and
  `source.walked` to nothing of constricter's (`[tool.importlinter]`; `lint-imports` in the Lint
  job).
- **ty, a fourth type checker**, beside basedpyright, mypy and pyrefly on the project's own code
  (`ty check`, `[tool.ty]`): it found a quoted alias it couldn't join with `| None`, a method read
  off a `Callable`, and a comment it took for a `type: ignore`; a warning fails it, but for
  `redundant-cast`, the casts being the other checkers'.
- **The public API, wholly typed**: `basedpyright --verifytypes constricter`, in the Lint job with
  the other checks (a release's build is no place to learn of a symbol), fails under a 100%
  completeness score (it exits 0 whatever the score) and names each symbol that isn't. It reads the
  package as the `python` first on PATH has it installed, ignoring `--pythonpath` and a venv
  config: the dev venv's editable install. It found three: a
  discarded `signal` handler; the pylint plugin's `msgs`, inferred from the base class; and its
  `process_module`'s parameter, astroid's `Module`, which astroid (no `py.typed`) leaves unknown
  under Python 3.11's semantics where `--ignoreexternal` excuses it under 3.14's: now a Protocol of
  the two members the checker reads.
- **Dependencies and docstrings, checked**: deptry holds the package's imports to its dependencies
  and extras, and the rest's to what some group declares (`[tool.deptry]`, two runs in the Lint job:
  deptry takes every group for a dev one). pydoclint, as a flake8 plugin, holds a docstring's
  `Returns:`, `Yields:` and `Raises:` to its function; no docstring lists its arguments, and the
  annotations give the types (`.flake8`).
- **The tests, in parallel**: `pytest -n auto --dist loadgroup` (pytest-xdist, as
  `tests/ci_local.py` runs them) takes 16s with coverage on 16 CPUs, from 50s in one process; the
  eight that start `--jobs` workers of their own share a worker. The floor is the fuzz test, 11s in
  one process: its 150 examples split over workers were each smaller, so they aren't.
- **Security** (`security.yml`, weekly too): CodeQL, zizmor (pedantic), actionlint, pip-audit,
  dependency review, and gitleaks over the whole history; OpenSSF Scorecard; lychee on links.
- **Pinning**: actions by SHA, Python dependencies by hash (`uv.lock`, checked in CI), npm by
  lockfile, uv and actionlint by version. `tool-versions.yml` keeps one issue open while any of them
  is behind a release at least a week old; Dependabot opens no version-update pull request.
- **harden-runner** blocks egress to all but the observed hosts in every Linux job, the release jobs
  included. The rulesets hold `main` to pull requests and signed commits, with no required status
  check, and protect `v*` tags.
- **Releases** (`release.yml` on `v*` tags): CI, a reusable build workflow that checks the tag
  matches the version and attests the dists (SLSA Build Level 3), PyPI trusted publishing, and a
  GitHub release: the README's badges, each merged pull request's `## Release note` section (which
  `release-note.yml` makes every one write) under "What changed", then GitHub's generated list.
  Verify a download with
  `gh attestation verify FILE --repo ivylikethevine/python-constricter --signer-workflow ivylikethevine/python-constricter/.github/workflows/build.yml`.
- **The compiled wheels, a job each**: a `python` matrix of cp311 to cp314 beside `os` in
  `build.yml` (`CIBW_BUILD` set from it) builds the 20 wheels at once, each job's artifacts and
  attestation named by both (`compiled-<os>-<python>`, which `release.yml`'s `compiled-*` patterns
  take): 2 to 5 minutes a job, from 0.4.2's 10 to 20 a platform. 0.4.3's 20 are on PyPI and the
  GitHub release (2026-10-25). A job can lose its start to a transient refusal as harden-runner
  engages (an artifact download's `ECONNREFUSED`, an image pull's `unexpected EOF`), which a rerun
  of the failed jobs clears.
- **Ubuntu 26.04 runners, named**: every Linux job runs on `ubuntu-26.04` rather than
  `ubuntu-latest`, so an image change is a commit, not the label moving under a release
  (`.github/actionlint.yaml` names the label, which actionlint 1.7.12 doesn't know); the ARM wheels
  stay on `ubuntu-24.04-arm`, there being no 26.04 ARM image. CI, Security, CodeQL and the 0.4.3
  release passed on it, harden-runner's allowlists unchanged.

## Project

- **Python 3.11+**, the oldest still maintained after 3.10's end of life (October 2026): 3.10 would
  add a runtime dependency (`tomli`) for a month, and 3.6–3.9 would mean dropping `match` from the
  checker. Code for any Python 3 version can still be checked.
- **Layout**: `constricter/` in `rules/`, `fix/`, `source/` (what a module's source says: its walks,
  annotations and declarations, which the rules and the fixes both read and which reads neither),
  `cli/` and `plugins/`; `fix/` in four layers, each importing only those before it: `core/` (what
  every part shares), `libraries/` (the standard library's and installed packages' types), `values/`
  (what a value makes its type) and `index/` (the cross-file index), its tests laid out the same.
  Modules are split along what each grouped as they near pylint's 1,000 lines (a reader of stubs'
  signatures out of `stubbed.py`, and its names' resolution out of `stubs/signatures.py`; what a
  file takes of another's classes out of `project.py`, and how a file spells another's types and
  calls (`spelling.py`); loops out of `inference.py`; what a module declares out of
  `source/annotations.py`; where a module's names come from and its open functions out of
  `fix/index/modules.py`; the hint rounds out of `cli/command.py`; the language server's connection
  out of `cli/lsp/hints.py`; building the scopes out of `rules/checker.py`; how a function binds a
  name again out of `rules/late.py` (`rebound.py`); operators out of `fix/libraries/overloads.py`
  (`operators.py`); the annotation forms out of `stdlib_tables/reading.py`; a run report's tables
  out of `tests/corpus/render.py`; a run's facts and resuming out of the corpus runner's
  `__main__.py` (`resume.py`); a suite's checkouts and type checks out of
  `tests/corpus/suite_steps.py` (`suite_checkouts.py`)); the Lint job warns past 800 lines, where
  `fix/values/hinted.py`, `rules/scope.py`, `source/declarations.py`, `fix/libraries/overloads.py`
  and `cli/options.py` are; the standard-library tables in `constricter/fix/tables/`, their
  generator in `stdlib_tables/`; the language servers' modules under `cli/lsp/`, the installed
  packages' stub readers under `fix/index/stubs/`; docs in `docs/` (changelog, contributing,
  security, integrations, fixes, likely, runs), release notes grouped by `.github/release.yml`,
  issue and PR templates, CODEOWNERS.
- **`Module` and `Outside`, by name**: frozen dataclasses with slots, every field given by keyword
  (they were tuples of 25 to 40 fields built by position). A check is no slower: the standard
  library's 48.3s in one process and 13.0s on 16 CPUs (48.5s and 13.0s before), pandas's 51.6s and
  10.8s (51.0s and 11.0s).
- **Faults a review of the package found**, each with a test: `fix-widen`'s method lookup through
  bases that cycle (`class A(B)`, `class B(A)`) no longer hangs; a relative import climbing past
  the top package names no module, as Python refuses it (`origins.absolute`); a guarded name's
  clash no longer drops the generic classes other files declare (`Outside.usable`); an import in
  a top-level `try`'s `finally:` counts as the module's; `infer-with` in `pyproject.toml` names each
  checker once; the hint store's key covers the code that writes what it keeps (`edits.py`);
  workers start only inside `kept()`, which stops them; the pylint plugin reads a module by its
  PEP 263 declaration or BOM, as the CLI does (a latin-1 module crashed it).
- **Simplified**, behavior kept and the compiled build's tests passing: helpers shared where a
  shape was written several times (a checked module's lookup, `syntax.own_returns`, the
  `Outside()` defaults for a module no other file informs, one framing of a language server's
  messages, one probe per checker), `Counter` for hand counts, dead names removed and names used
  in one module made private; the corpus runner's facts and resuming in `tests/corpus/resume.py`
  (its `__main__.py` was at pylint's 1,000 lines), its step names, paths and constants named once.
- **Structure**: what a module's source says (its walks, annotations and declarations) in
  `constricter/source/`, which import-linter holds below the rules and the fixes, so the two no
  longer import each other; one table per code in `offences.CODES` (its message and the levels it's
  reported and an error from), and one table of the plugins' options (`plugins/options.py`). The
  corpus runner reads its flags with argparse (`run_config.read_command`): an argument it doesn't
  take is an error, with its usage. It writes `facts.toml` with tomli-w and holds a corpus's shared
  check with filelock, both declared in the `test` group. What reads a suite's tests' output
  changed (`corpus_suite.parser`: `3aeda7010fee`), so a run after it doesn't reuse an earlier run's
  released-tests records.
- **Packages weighed and left out.** constricter has no runtime dependency, and installs where only
  pure Python does (PyPy, free-threaded builds). `pygls` or `lsprotocol` for the checkers' servers
  (`cli/lsp/hints.py`): the protocol's types are the small part, and the rest (servers sized by
  memory, a hung one found, restarted and asked again) no library has. `LibCST` for the edits: a
  native parser, for edits already proven on 59 packages. `platformdirs` for one function of ten
  lines. `networkx` or `graphlib` for the files' order: `graphlib` refuses the cycles it's there to
  find. `msgspec` or `orjson` for the index sent to workers: native, and the index is sent more
  often than it needs to be first. `nox` for `tests/ci_local.py`, which reads its steps from CI's
  own workflow.
- **Pyright and basedpyright in editors**: `pyrightconfig.json`, which both read first, holds the
  shared settings (`local/.venv`, and the code checked alone) and extends `pyproject.toml`, where
  only basedpyright finds a section (`typeCheckingMode = "all"`). Plain Pyright resolves the dev
  dependencies with no config warning, and `basedpyright` checks the same files in about the same
  time (9.6s, from 9.0s).
- **Tables generated at build time**: built with hatchling, whose hook (`hatch_build.py`) generates
  `constricter/fix/tables/` wherever they're missing or stale, from the typeshed stubs of the
  basedpyright `uv.lock` pins, a build dependency only then. They're stale when `source.json`'s
  stamp differs: that version, and a digest of the generator's code (`stdlib_tables/`) and the
  modules of `constricter` it imports. An sdist carries them, so a wheel built from it needs
  nothing; a wheel, an sdist and a build from a checkout carry the same tables, byte for byte the
  ones git tracked before. Not compressed: a wheel is a zip already (the tables are 1 MB, the whole
  wheel 395 KB). A build from a checkout downloads 75 MB (60 MB of it Node, which basedpyright
  depends on and the generator doesn't use) and generates them, about 12s on 4 cores. The Action
  pays it on every run, and a pre-commit hook once, on install.
- **The stubs, read by `typeshed-client`** (`stdlib_tables/shed.py`), a build dependency `uv.lock`
  pins beside basedpyright, both in the tables' stamp: it decides each stub's `sys.platform` and
  `sys.version_info` blocks, lists what a body binds and resolves its imports, and
  `stdlib_tables/stubs.py` binds what it lists in the stub's own order. The tables came out byte for
  byte the same. Two things stay the generator's: whether a submodule exists in a Python version
  (`typeshed-client` reads `VERSIONS` for the top-level module alone), and an `__all__` assigned
  twice, where the last assignment stands.
- **The installed modules' cache, swept** (`installed.swept`): each version and reading code has its
  own part of the cache, and a run that writes to it sweeps, a day apart at most: entries of no
  build's part go, another build's part unswept for a month, and its own entries unread for a month
  or, the longest unread first, over 256 MB.

- **No per-file license headers.** `REUSE.toml` licenses every file (`path = "**"`, MIT; the code
  of conduct CC-BY-4.0, as the Contributor Covenant's text), and Scorecard's License check reads
  only `LICENSE.md`, so no file carries a header of its own; ruff's `missing-copyright-notice` is
  off, and `git grep` finds the identifier in `REUSE.toml` alone. The synced CI files lose theirs
  in their source, which the sync carries.
