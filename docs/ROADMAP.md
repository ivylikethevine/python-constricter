# Roadmap

## Done

### Rules

- **LVA001–LVA004**, with `all-scopes` for module and class bodies (LVA004), and `# type:` comments
  counted automatically in modules importing Python 2 `__future__` features.
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

### `--fix`

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
  module. None of these is counted on the corpora yet.
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
  `defaultdict(list)` and `Counter()` stay untyped: their parameters come from later use. Generic
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
  found as the import system would on this Python's path and `VIRTUAL_ENV`'s; types are imported
  from a public module that re-exports them. Functions whose overloads or type variables their
  arguments decide are matched as the tables' are (`constricter.fix.index.stubs.stubbed`), through the
  package's aliases, type variables and protocols, the standard-library classes it names by the
  `scalars` table, and a class argument binding `type[T]`: 83 more fixes on pandas
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
  for type checking alone too (`project.definition`, as `_canonical` does), so a class a package's
  `__init__` imports only when it's asked for (pydantic's `TypeAdapter`) has its members, its
  methods' returns and its aliases; a package's re-exports are spelled from both
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
  own `errno`). The unsafe runs' new errors went from 20, 76 and 165 (0.2.4) to 1, 12 and 32.
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

### Command and output

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

### Integrations

- **Plugins** for flake8 and pylint (`C9101`–`C9112`); ruff through `lint.external`.
- **pre-commit** hooks (`constricter-fix` runs as one process, so its cross-module `--fix` sees
  every file) and pre-commit.ci; **tox**, **nox**, **Bazel** and **Pants** notes; **editor**
  settings for VS Code, Zed and Neovim.
- **A GitHub Action**: PR annotations, a per-code summary table, a `sarif-file` output, and a
  `version` input to install a PyPI release with uv; CI runs it on this project.
- **On PyPI** as `python-constricter`.

### Corpus

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
  noted. The timed checks hold every CPU, and run last, one at a time. A suite's tests of one port
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
  On every corpus: 250,958 untyped bindings, 141,733 with no fix at all, 79% of those in functions
  with no annotations. The items under [Next](#next) are sized by it: each count is the bindings
  with no fix an item could reach, not what it would fix. With no fix so far, each an item under
  Next now: `getattr(...)`, a bound method's alias (`append = parts.append`), `dict.get` on a
  `dict[str, Any]`, and a `TypeVar`'s own declaration. Measured and too small to build: an
  unannotated parameter typed by its literal default (76 bindings) or its docstring (325); and
  signatures first, by `pyrefly infer` before `--fix`: 2,254 more certain fixes on the six Python 3
  corpora (19.8% of their untyped bindings fixed, then 20.8%), since it annotates 8% of the
  unannotated parameters, most of the returns it adds are `-> None`, and it left one of pydantic's
  files unparsable; and the same from mypy's daemon (`dmypy suggest`, `scratch/dmypy_suggest.py`,
  500 functions of each corpus but the standard library, which mypy won't check as a project's own):
  it stops on every one of sqlalchemy's and pandas's, takes 30s to 90s a function on 16CPU/60GB with
  14 daemons, and on django, the one with no type comments, brings 19 certain fixes for 415 new
  basedpyright errors, most an `X | None` read without a check; and an unannotated function's
  `return`s of two types, or of one and `None`, joined into a union: 275 more fixes, and 38 new
  basedpyright errors (a union one of whose types is wrong, or that the caller never narrows); and a
  class variable or an attribute first `None`, set in another method (`timeout = None` in a class
  body, `self.conn = None` in `__init__`): of the 894 class-body `name = None`s on the Python 3
  corpora, 402 aren't in a plain class, 275 are never stored by their module (a subclass's to set),
  131 are stored another way or from outside the class, and 82 are assigned no literal, only values
  that are mostly parameters; an attribute's `T | None` types no read its function tests or stores,
  since that isn't offered; and a name a plain class's body binds more than once: of 594 on Django,
  pandas, SQLAlchemy and the standard library, 425 are a method or a class too, 122 are bound in an
  `if`'s or a `try`'s branches, and 14 by two plain assignments.
- **Why `name = self.method()` has no fix** (8,195 bindings, before the inherited methods): the
  method is the class's own (46%), a base's in the file (12%) or in another (10%), a class attribute
  a subclass sets (`self.type2test()`, `self.dumps()`: 28%, left alone), or a library base's (5%).
  Of the 5,479 found, 4,078 have a `return` whose value has no type: a name (1,779: an unannotated
  parameter, or a local with no fix), a call on another value (823), another `self.method()` (408).
- **Other type checkers' servers**, driven through `constricter.cli.lsp.hints` on pydantic, sqlalchemy
  and django (26,716 bindings with no fix): the share of them each one's hints type, as `--fix`
  judges hints now, is 8.2% for ty, 10.7% for basedpyright and 13.7% for pyrefly. Plain Pyright's
  server has no inlay hints (they're Pylance's and basedpyright's), mypy has no server
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
  version. Expected of the 0.3.9-rc.1 mega run: 85 CPU-minutes of implied parts and 58 more, 178
  of the released tests' 200, and sqlalchemy's 9-minute rerun off the critical path; not yet run.

### CI, security and releases

- **CI** (`ci.yml`): every check in [CONTRIBUTING](CONTRIBUTING.md#development), the pre-commit
  hook, Markdown, tests on Linux, macOS and Windows × Python 3.11–3.14 plus PyPy 3.11 and
  free-threaded 3.14 (100% branch coverage), the build and a wheel smoke test, the Action, and the
  corpus. The project's own code passes `--level=suffocate --all-scopes` at 100% annotation
  coverage. A tree CI already passed (the merge to `main` after its pull request, the release tag on
  it) isn't tested again: a `tested-tree` artifact records each passing tree, and the next run on it
  skips every job.
- **The layers, checked**: `import-linter` holds `constricter.fix`'s four layers to importing only
  those before them, the rules and the fixes to importing neither the command nor the plugins, and
  `rules.walked` to nothing of constricter's (`[tool.importlinter]`; `lint-imports` in the Lint
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
  included; rulesets require every check on `main` and protect `v*` tags.
- **Releases** (`release.yml` on `v*` tags): CI, a reusable build workflow that checks the tag
  matches the version and attests the dists (SLSA Build Level 3), PyPI trusted publishing, and a
  GitHub release: the README's badges, each merged pull request's `## Release note` section (which
  `release-note.yml` makes every one write) under "What changed", then GitHub's generated list.
  Verify a download with
  `gh attestation verify FILE --repo ivylikethevine/python-constricter --signer-workflow ivylikethevine/python-constricter/.github/workflows/build.yml`.

### Project

- **Python 3.11+**, the oldest still maintained after 3.10's end of life (October 2026): 3.10 would
  add a runtime dependency (`tomli`) for a month, and 3.6–3.9 would mean dropping `match` from the
  checker. Code for any Python 3 version can still be checked.
- **Layout**: `constricter/` in `rules/`, `fix/`, `cli/` and `plugins/`; `fix/` in four layers, each
  importing only those before it: `core/` (what every part shares), `libraries/` (the standard
  library's and installed packages' types), `values/` (what a value makes its type) and `index/`
  (the cross-file index), its tests laid out the same. Every module is under 800 lines, past which
  the Lint job warns, split along what each grouped (a reader of stubs' signatures out of
  `stubbed.py`, and its names' resolution out of `stubs/signatures.py`; what a file takes of
  another's classes out of `project.py`; loops out of `inference.py`; what a module declares out of
  `rules/annotations.py`; where a module's names come from and its open functions out of
  `fix/index/modules.py`; the hint rounds out of `cli/command.py`; the language server's connection
  out of `cli/lsp/hints.py`; building the scopes out of `rules/checker.py`; the annotation forms out of
  `stdlib_tables/reading.py`; a run report's tables out of `tests/corpus/render.py`), and all of
  `constricter/`'s but five under 750 (`cli/options.py`, `fix/index/project.py`,
  `fix/libraries/overloads.py`, and `rules/late.py` and `scope.py`); the standard-library tables in
  `constricter/fix/tables/`, their generator in `stdlib_tables/`; the language servers' modules
  under `cli/lsp/`, the installed packages' stub readers under `fix/index/stubs/`; docs in `docs/` (changelog,
  contributing, security, integrations, fixes, likely, runs), release notes grouped by
  `.github/release.yml`, issue and PR templates, CODEOWNERS.
- **`Module` and `Outside`, by name**: frozen dataclasses with slots, every field given by keyword
  (they were tuples of 25 to 40 fields built by position). A check is no slower: the standard
  library's 48.3s in one process and 13.0s on 16 CPUs (48.5s and 13.0s before), pandas's 51.6s and
  10.8s (51.0s and 11.0s).
- **Packages weighed and left out.** constricter has no runtime dependency, and installs where only
  pure Python does (PyPy, free-threaded builds). `pygls` or `lsprotocol` for the checkers' servers
  (`cli/lsp/hints.py`): the protocol's types are the small part, and the rest (servers sized by memory,
  a hung one found, restarted and asked again) no library has. `LibCST` for the edits: a native
  parser, for edits already proven on 59 packages. `platformdirs` for one function of ten lines.
  `networkx` or `graphlib` for the files' order: `graphlib` refuses the cycles it's there to find.
  `msgspec` or `orjson` for the index sent to workers: native, and the index is sent more often than
  it needs to be first. `nox` for `tests/ci_local.py`, which reads its steps from CI's own workflow.
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

## Next

By size (smallest first) and, within each, by value: the bindings with no fix an item could reach,
of the 141,733 on the corpora, or of the 23,271 on pydantic, sqlalchemy and django for an item that
needs `--infer-with`; what only makes a check faster comes last. An item's size is the hours an Opus
5.5 agent would work on it, tests and docs included, apart from what it waits on (a full corpus run,
a package's suite): each ends with that estimate, after what it is, why, how, and when it's done,
and with the coverage it's expected to add: its fixes as a share of the 252,056 offences the last
tagged run (0.3.6) found on the corpora, a guess from the item's reach, not a measurement. An item's
own breakdown may predate the latest fixes: what it cites from the census (`corpus_untyped`) is
current, its finer counts are as first measured. Where an item cites a sample, it's 41 directories
of the standard library, pandas, django and sqlalchemy, each checked alone: 28,931 bindings with no
fix. After the sized items, four groups of avenues read from the 0.3.7-rc.1 census of 47 corpora
(2026-10-16) and the census rows of 2026-10-02 on the seven: what the rules don't see
([Scope](#scope)), gaps in what `--fix` infers ([Inference](#inference)), guess mechanisms the
witness can measure ([Guesses](#guesses)) and what to measure first ([Measurement](#measurement)),
each item sized the same way.

### Small: under 4 hours

1. **The runner's scheduling, measured.** Every corpus's steps now wait for the machine alone, the
   one with the most behind it first, and a running step's hold follows what it uses
   (`tests/corpus/sizing.py`); `check` and `census`, which read one check that the first to start
   runs, are each held for the most either took; a suite's tests run 6 times for 8, its traced tests
   start early, and its type checks beside its tests. Measured on pydantic and pygments alone.
   Since: a suite's tests take a worker for each CPU, up to their `most` and as many as half the
   run's memory holds, starting once half the CPUs they want are free (or half the machine's) with
   as many more as are free then; celery's parts run as many at once as fit, 4.6 GB each; a suite's
   type-check checkout is installed beside its corpus's first steps; and each step's record says
   when it started and how long it waited for its share, the run's `runner.log` each step's end
   (`scratch/run_timeline.py` lays a run out from them). Tested apart, and on pydantic's run alone.
   The last mega run of 40 corpora used 70% of its CPU seconds in 119 minutes, by the sampler's
   count, which misses most of a fork server's workers (a run now counts them by control group), its
   last 15 minutes waiting on `websockets`'s tests, asleep. The first super run of 29 took 87
   minutes, both on 16CPU/60GB: for 25 of them 1 to 3 CPUs were busy, pandas's checkers' steps each
   past `_PATIENCE` and keeping what was free, and fastapi's and black's traced tests waited 68
   minutes to run for 20s and 11s. `scratch/schedule_sim.py` replays it in 85 minutes as it was
   sized, 72 with no wait keeping what's free from steps that fit, whatever the order, and 75 with a
   step whose last run took 5 minutes at most starting beside one kept waiting, as one now does
   (`_BESIDE`). The 18 slow corpora's mega run used 81% of its CPU seconds in 91 minutes, no
   schedule taking it under 77 (its CPU seconds over every CPU). Since, not yet run: a step that
   can't start holds back none after it; a suite step's port and checkouts are taken with its share
   as it starts, none held while it waits; and a suite's tests and type checks are a part per fix,
   each on a checkout of the suite's own once its fix is made (`suite_steps.needs`). The mega run of
   all 47 corpora after them took 155 minutes (the super and the slow corpora's, apart, 87 and 91)
   and used 78% of its CPU seconds before its timed checks, 74% with them: the standard library's
   and pandas's `infer-*` steps held 13 to 17.5 GB each, and what was left of the memory, not of the
   CPUs, kept the rest waiting. Its steps' CPUs, not their memory, cost the time: held to what each
   was given, no schedule of them takes under 147 minutes; to the memory alone, 127. A suite's tests
   kept 5 of 8 CPUs busy (mypy's), and of the 11 CPU hours held and idle, its tests held 3.9, the
   timed checks 2.5. Done, not yet run: a suite's measured tests hold the CPUs they kept busy, a
   margin over, with as many workers as before (141 minutes, replayed). The mega-fast run after it
   (no released or traced tests) took 109 minutes and used 80% of its CPU seconds before its timed
   checks, 73% with them, 13 to 14 CPUs busy until its last half hour; no schedule of its steps
   takes under 93 minutes, or 100 held to what each was given. The basic run of 0.3.8-rc.1, with the
   three suites at new tags and so no record to size their steps by, took 58 minutes and used 66% of
   its CPU seconds (about 72% before its timed checks): django's tests kept 6.5 CPUs busy on the 1
   given, and pandas's `infer-pyrefly` waited 31 minutes for 20 GB. The mega run of 0.3.9-rc.1,
   the first with the suites' tests holding what they kept busy, took 161 minutes (replayed at 141)
   and used 78% of its CPU seconds, 13 to 15 CPUs busy until minute 150: every step but the suites'
   tests had ended by minute 132; the tests (378 steps, 232 step-minutes, 1,336 CPU-minutes) ran two
   at a time on the 8 CPUs each held, keeping 5 to 10 busy, until 150, mypy's traced and type-checked
   tests after waits of 50 minutes and sqlalchemy's 9-minute tests starting at 138; and the 47 timed
   checks took the last 11 minutes alone with 1 to 3 CPUs busy (10 step-minutes). The suites' tests
   are the tail now, and the order they start in the lever: the longest (mypy's, sqlalchemy's,
   pandas's, dask's, optuna's) waited for the fixes and checkers before them. The mega run of
   0.4.0-rc.1, the first with them, took 134 minutes on 16CPU/60GB (replayed at 126) and used 77.5%
   of its CPU seconds: 83.3% over the 123 minutes before its timed checks, with 12 to 15 CPUs busy
   throughout and mypy's, dask's and optuna's suites all ending in the last minute of them; the 47
   timed checks took the last 10.5 minutes with 1.5 CPUs busy. Its steps' CPU seconds over every CPU
   are 113 minutes, and no schedule of them takes under 123: the scheduling is within 10% of its
   floor, and the tail is what's left of the 85%. The 0.4.0-rc.2 run's new `infer-union` steps,
   unmeasured, were held a third of the memory, as any checker's step is (dask's took 18.2 GB), and
   its tests' parts what the tests' whole step had held, which only reads its parts' (1 CPU; mypy's
   kept 5.6 busy). Done, not yet run: an unmeasured part takes its kind's largest measured part
   (the released tests'), and an unmeasured `infer-union` its checkers' steps together, no more
   than twice the largest's memory. Done when a mega run uses 85% of its CPU seconds,
   and one with no earlier run under its output takes within a tenth of one sized by its own. About
   2 hours beside the runs; coverage unchanged.

2. **The timed tail.** The 47 timed checks ran alone over the 0.3.9-rc.1 mega run's last 11 minutes
   with 1.4 of 16 CPUs busy, 2.49 idle CPU-hours, the largest idle hold of any step kind; pandas's
   (136s) and the standard library's (117s) are 41% of it, and 0.4.0-rc.1's tail was the same 10.5
   minutes. Between two runs at the same commit the single-sample seconds differed by a median 0.13%
   in one process and 0.59% with every CPU, instructions by 0.09%; between the two mega runs, a
   version bump apart with the tail alone each time, by a median 0.9% in one process and 1.2% with
   jobs, up to 4%, and instructions by 1% too (`scratch/timing_noise.py`; some corpora moved tag).
   Measured on django, sqlalchemy and twisted, 5 runs a way (`scratch/timed_tail_trial.py`): with no
   warm-up the first run is within 0.8% of the rest, so hyperfine's `--warmup 1` is dropped, which
   halves each timed check; three corpora at once on disjoint 5-CPU sets run 4 to 5% slower in one
   process and 10 to 17% with jobs, with the spread up from under 1% to 2 to 10%, so the timed checks
   stay one at a time. The instructions didn't move side by side (0.04 to 0.15%): the table could
   compare them across runs instead of seconds, which would free the tail to run beside other steps.
   Done when a mega run's tail is under 5 minutes with the timing table's run-to-run noise unchanged:
   the 0.4.0-rc.2 mega run's took 5.3 minutes, from 10.5, and the 0.4.0-rc.3 run's 5.6: 4.4 for 46
   corpora back to back, and pandas's 71s in a resume of its own. Those two runs are a code change
   apart, their instructions a median 7.6% apart in one process (`scratch/timing_noise.py`), so the
   noise wants two runs at one commit. About 1 hour; coverage unchanged.
3. **The compiled wheels, a job each.** `build.yml`'s Compiled job builds one platform's wheels one
   after another, each a full mypyc build: on the 0.4.1 release, about 2 minutes a wheel, 30s of it
   setup and the import test, so macOS took 8 and 15 minutes for 4 wheels and Windows 21 for 8
   (32-bit since dropped), and the Linux jobs over 33. A `python` matrix of cp311 to cp314 beside
   `os`, with `CIBW_BUILD: ${{ matrix.python }}-*`, runs the 20 wheels at once: the same runner
   minutes, free for a public repository, and the release waits on its slowest wheel. Each job's
   artifacts and attestation file are named by both (`compiled-<os>-<python>`), which
   `release.yml`'s `compiled-*` patterns already take; the attestation's file name must change too,
   or `merge-multiple` keeps one per platform. Done when a release's compiled wheels all build in
   under 6 minutes, the same 20 wheels and attestations on PyPI and the GitHub release. About 1
   hour; coverage unchanged.

### Medium: 4 to 8 hours

1. **What a guess breaks, by its cause.** After `--fix --unsafe-fixes` the packages' own type
   checkers find one new error on pandas (from 42), and none on sqlalchemy or pydantic; of the mega
   corpora's 30 on the 0.3.9-rc.1 run (38 before), 17 on mypy, 5 on mcp, 4 on pint (from 10, by the
   augmented assignment below) and one on each of narwhals, nibabel and optuna. mcp's 3 new ones are
   a dict display's guess: `headers = {"a": x}` typed `dict[str, str | None]` by what the function
   adds to it later (`container` with `joined`), then passed where a `Mapping[str, str]` is wanted;
   a display's guess from its later additions should not widen what a call already takes.
   By the fixes' sets of mechanisms ([LIKELY.md](LIKELY.md)), those with `rebound` are blamed for an
   error 0.30 times in each 100 guesses a checker read, a `constructor` 0.06 times; on the mega
   corpora's suites and pydantic alone, 0.70 (6 of 853) and 0.31 (14 of 4,517, each mypy's `lxml`),
   and every error but narwhals's, optuna's and those 14 is a `rebound` guess's. What's left:
   - A name typed by its first values and bound again to what `--fix` can't type (`rebound`):
     `units_overlay: bool`, then a `dict`; `factor: float | None`, then `factor *= other`; a
     `re.Match[str]`, then its `groupdict()`. pint's 10 (3 bindings), mcp's 2, 3 of mypy's
     (`code = error.get("code")`, then `if code is None: code = SYNTAX`). Counted on the basic run
     of 0.3.8-rc.1: the seven corpora's 1,262 `rebound` guesses are blamed for no error and hold
     98.7% of the time (13 of 1,019 told differed), so withholding them all would cost more than it
     saves. Done: a name bound again to a call on itself (`groupdict()`'s case), or a number bound
     again by an augmented assignment with an operand of no known type (`factor *= other`), gets no
     guess; pydantic loses one (`scratch/rebound_census.py` counts them). The 0.4.0-rc.2 mega run
     still had pint's 4 and mypy's 3: the call on itself was only one taking the name, not its
     method (`match = match.groupdict()`) or one behind `or` (`code = codes.get(code) or SYNTAX`).
     Done, not yet run: those, a name bound again to an empty display of another class
     (`units_overlay = {}`, a chained assignment's), and a loop's target bound again past the loop
     to a value of no known type (mcp's `value: str`, then `value = _value_at_path(...)`), get no
     guess either; the last withdraws 25 guesses on the rc.2 run's sources at hand
     (`scratch/rebound_shapes.py`), one blamed for an error. Left as it is: mcp's `name`, a copy of a
     `str | None` parameter filled in `if not name:` by a value the checker sees as `Any` and narrows
     to the declared type; withdrawing that shape would take 23 guesses for that one error. A run of
     `tests/corpus/runs/errors.toml` after them had none of pint's or mypy's left, and mcp's 3 others
     were a display widened by a value narrowed where it's added (`headers[key] = self.session_id`
     in `if self.session_id:`); done since: no fix, 4 of mcp's guesses withdrawn, pydantic's none.
   - A type from a package the suite's own checker can't follow (`etree.Element`, of `lxml`): 14 of
     mypy's. Its environment's; listed, not fixed.
   - A `None`, then only an `Index`, by an unannotated function's `return`s: declared, an argument
     taken from it is checked (`oindex._values`). pandas's one. Nothing its function does with the
     name says so: of pandas's 163 guesses by a method's `return`s, 22 are in code mypy checks.
   - A standard-library call's declared union, written for a name used as one of its members
     (`ibis_type: IbisDataType | None`, "Expected class but received UnionType"): narwhals's one.
   - A display of a base's subclasses, declared their union and passed where a `dict` of the base is
     taken (`dict[str, A | B]` for a `dict[str, Base]`). optuna's one.
   - A method's `bytes`, formatted into text (`magic_number: bytes` in an f-string, mypy's
     `str-bytes-safe`): nibabel's one, a likely `method` guess.

   Done when each package's errors left are its environment's, or under one for each hundred of its
   guesses, on the seven and on the mega corpora's: on the 0.4.0-rc.2 mega run every package was,
   by the guesses blamed for an error in each hundred a checker read (mcp 0.54, pint 0.27, mypy
   0.24, the rest under 0.1). About 6 hours; coverage down by the guesses withdrawn.

2. **A parallel check, past its longest chain.** With every CPU the standard library checks in 12.9s
   and pandas in 11.3s (14.4s and 11.4s before the workers were kept for a run's rounds): 46s and
   50s in one process, 29s in two, 18s in four, 13.7s and 12.9s in eight, so about 10s of each
   doesn't shorten with more (timed before a method's lookups were kept for a run, which took one
   process from 53.7s to 43.0s on the standard library and 61.8s to 53.5s on pandas, 16CPU/60GB:
   time it again first). It isn't the main process (indexing, ordering and telling the workers take
   2 to 3s) but the order: a file waits for those whose unannotated functions it calls, 29 deep in
   the standard library, and pandas's 217 files that call each other go round up to four times
   before the other 1,200 start. Most of those edges are by a method's name alone (`loose.needs`:
   12,704 of the standard library's, to 3,400 by an imported function). Tried, and slower: a worker
   with nothing to do checking files ahead of their turn, each confirmed when its turn came (16.0s
   from 14.4s: most are checked twice, and 25 of pandas's findings then differed). Left to try: an
   edge only where the receiver's class is known to be the other module's; and a file checked again
   from where its first check ended when what it imports returns anew, as it is when its parameters
   are typed. Done when the standard library checks in under 9s with every CPU, its findings the
   same. About 8 hours; coverage unchanged.
3. **What a hint breaks, by its cause.** With `--infer-with` the packages' own type checkers find,
   by the worst of basedpyright's, ty's and pyrefly's hints, 125 new errors on pandas, 49 on
   sqlalchemy, 41 on streamlink, 12 on starlette, 10 on mcp, 9 on sphinx and 1 to 8 on eight more of
   the super corpora; on the slow ones, 215 on litestar, 42 on narwhals, 29 on mypy, 16 on optuna,
   13 on pint and 2 to 8 on four more. Nearly all are traced to a hint's own fix (`checker`).
   litestar's weren't read: its Pyright is set to Python 3.8. Count them by cause, as the guesses'
   are above, and hold a hint to what the cause says. On the 0.4.0-rc.2 mega run the hinted steps'
   868 new errors were 454 blamed on a hint's own fix, 195 on `--fix`'s own guesses beside them and
   219 on no fix, 182 of those litestar's, set off by the hints' `from typing import TypeAlias` on
   its Python 3.8 (`scratch/hint_errors.py` groups them). The hints' by cause: an annotation
   narrower than a later value (95, and 16 a later `None`): the hint is the first value's type, the
   checker knows the later ones' and `--fix` doesn't; ty's `GeneratorType[...]` for a generator
   (44); numpy's `bool[bool]` as ty prints it, read as the builtin (43); another class of the same
   name (43: starlette's own `Match`, pydantic's `ValidationError` for jsonschema's); `TypeAlias` on
   Python 3.8 (23); a module's name for its class (16: `import datetime`, PIL's `Image`); a private
   or stub-only name (13: `np._NBitIntP`, `sys.OptExcInfo`); `Never` (4); a class a function
   defines (4); and 153 others, most of them pandas's `ArrayLike` and `Manager` unions read as one
   member. Done, not yet run: a hint naming a module bare, a well-known class's name the module
   binds to its own class, a builtin given type arguments, a private part of a dotted name or a
   function's class is dropped, ty's `GeneratorType` is written `Generator`, and `TypeAlias` is
   imported from `typing` only from `min-python` 3.10: 165 of the 454, and litestar's 182. Of the
   narrower annotations, 25 were pyrefly's `Self` for a local in a method whose signature doesn't
   say `Self` (`type(self)(...)`, `self[mask]`, `super().drop_duplicates()`), which mypy reads as the
   class there; and 4 a `Never` (`list[Never]`, an empty display's). Done, not yet run: neither is
   a fix, 194 of the 454 in all. Left: a hint narrower than the package's own checker reads the
   same value (`message.get("more_body")`, `bool` to basedpyright and `bool | None` to mypy;
   pyrefly's `bool` for numpy's), the same names imported from elsewhere (`Image`,
   `ValidationError`, which only the checker's definition link can tell apart), and pandas's. Done when a hinted run's new
   errors are under one for each hundred of its hints' fixes on the three corpora type-checked.
   About 8 hours; coverage down by the hints withdrawn.
4. **The witness, past a test's own classes.** The corpora runs hold a fixed binding's value to its
   annotation as its package's traced tests bind it (`tests/corpus/witness`), and a test's own
   stand-in differs (`FakeProcess`, passed where a `ServerProcess` is declared: mcp's one certain
   fix that differed, narwhals's too). On the mega corpora's suites 16 of the 20 `constructor`
   guesses that differed are a class the trace couldn't name, one a function or a test defines again
   at each call (networkx's `StackFrame`, 95 of 100 values; seaborn's `CatScale`, 126 of 132). Done,
   not yet run: a value of a class a test module defines tells nothing of the annotation, as a mock
   doesn't, and a class a function defines again is the annotation's by its module and qualified
   name (`constricter_witness`). In the mega run after it, the certain fixes that differed fell from
   259 to 238 (mcp's none), the likely from 102 to 74 and the guesses from 109 to 96; pandas has 75
   of the certain, sphinx 27, sqlalchemy 19. Most are the package's own declarations, which its
   tests contradict: a numpy scalar where `int` or `bool` is declared (pandas's `iloc`,
   `_has_infs`), `None` where it isn't (sphinx's C++ parser), `round_trip_pickle`'s
   `DataFrame | Series` for any value pickled, pytest's `FSHookProxy` for a `HookRelay`. Two were
   `--fix`'s own: an index of no known type into a list typed as its element (pandas's `ilkey`, a
   slice), since fixed; and a display typed by its elements alone (networkx's `probs = [0]`, then
   `probs.append(d**-r)`, a `float`), as type checkers type it, since widened by what's added (a
   `list[float]`; an `int`'s `**` by an `int` is a `float`). Done, not yet run: the witness tells
   nothing of a `SimpleNamespace` (pdm's stand-ins) or of an annotation naming a test's class
   outside the tests (django's `datetime`, patched to `MockDateTime`), and takes a module's class
   imported anew as the one it names (sphinx's `CitationDomain`). Done when a certain fix that
   differs on the corpora is a declaration its package's tests contradict (pydantic's
   `multiple_of: Decimal | None`, bound to an `int`). About 3 hours; coverage unchanged.
5. **django's traced tests, in more than one process.** The tracer doesn't follow the processes
   `multiprocessing` starts, so django's suite is traced with `--parallel=1`: 812s traced, the
   longest step of a super run, to 79s untraced on its workers (timed before a generator's returns
   were counted: time it again first). celery's parts are traced one after another too. Record in a
   forked child as a pytest-xdist worker records itself, or trace a suite's `parts` side by side, a
   trace file each. Done when django's traced tests take under 300s, the fixes resting on the trace
   the same. About 4 hours; coverage unchanged.
6. **A traced run, sampled.** The tracer follows every line of a recorded function until its
   statements have ended 20 times with nothing new: django's traced tests take 812s, 79s untraced.
   Record in short windows at random times, with `sys.monitoring`'s events off between them, and
   stop reading a large container once new types stop turning up. Done when pydantic's and django's
   traced tests take under twice their untraced time, and the fixes resting on the trace are within
   a hundredth of today's. About 6 hours; coverage unchanged.

7. **The runner's order, from a solver.** No library runs subprocess steps in a graph under CPUs and
   memory as the runner does: Snakemake's scheduler comes nearest, choosing among its ready jobs as
   a knapsack, greedily or by PuLP's solver, but is a workflow engine whole, and Dask's and Ray's
   resources are their workers' Python tasks'. Done, not yet run: where OR-Tools is installed, the
   runner plans its steps with CP-SAT before it starts (`tests/corpus/planning.py`: the CPUs and
   memory each took in the last runs held at once, ports, each step after those it reads), and of
   the steps that could start, starts the one planned first; a step no run has measured keeps the
   rules (the longest chain first, `_PATIENCE`, backfilling). `scratch/schedule_solve.py` plans a
   finished run's steps the same way and proves how short any schedule of them can be. Left:
   OR-Tools in the `corpus` group. The mega run took 154 minutes, the solver's shortest schedule of
   its steps 129 and the least it proves 57; held to what the runner gave each, 147. Done, not yet
   run: the solver holds each step to what the runner will hold for it (`sizing.Plan.wanted`), not
   what it used, so its order is one the runner can keep. Done when a super and a mega run each take
   within a tenth of the solver's shortest schedule of their own steps. About 2 hours beside the
   runs; coverage unchanged.
8. **Signatures from a sampled run.** RightTyper runs a package's tests
   (`python -m righttyper run -m pytest`) and annotates the parameters and returns of the functions
   they called, sampling with `sys.monitoring` at a fraction of a full trace's cost. The traced
   parameters' types as `callers`' seeds brought more errors than fixes (Large 1), so what's new is
   the returns, written before `--fix` as `pyrefly infer`'s signatures were; its sampling is also a
   model for item 6. Measure on pydantic's and django's tests: the time against the `traced` step's,
   the fixes past the trace's, the new errors. Done when measured; a corpus step only if it brings
   more fixes than the trace for no more errors. About 4 hours; coverage unchanged.
9. **CI's tools and security workflows, the shared way.** `security.yml` runs CodeQL and the weekly
   link check in jobs of its own, and every workflow that needs a binary (actionlint, gitleaks,
   lychee, twice) downloads it through `actions/tool` with the URL and sha256 written in the step,
   each a row of `check_tool_versions.local.sh`'s roster. The sibling repositories run the shared
   `codeql.yml` and `link-check.yml` instead, and install tools through the shared `setup-tool` and
   `setup-tools` actions from one roster beside them, `tools.txt` (name, version, archive type, URL
   template and checksum per tool), which `check_tool_versions.sh` reads on its own; the sync
   carries a workflow only where its actions already are, so this repository gets neither until the
   actions do. How: take the `setup-tool` and `setup-tools` actions and `apt/lib.sh` from the sync;
   write `tools.txt` with actionlint, gitleaks and lychee at today's pins; replace each
   `actions/tool` step (`ci.yml`'s offline lychee, `security.yml`'s three) with `setup-tools` and
   delete `actions/tool`; drop the three rows from the local roster, keeping uv's; take `codeql.yml`
   (`language=python`) and `link-check.yml` from the sync and delete the `codeql` and `links` jobs
   from `security.yml`, which keeps zizmor, actionlint, the workflow conventions, pip-audit,
   dependency review and gitleaks; and re-read each job's `allowed-endpoints` from an audit run,
   since the download hosts move. The ruleset needs nothing: CodeQL is a code-scanning tool there,
   not a named check. Done when every workflow has one green run on a pull request, including a
   weekly `link-check.yml` by hand, `tool-versions.yml` reports the same four tools from the new
   roster, and the sync has nothing left to send. About 5 hours; coverage unchanged.
10. **One test run on the union of the fixes.** Of the 0.3.9-rc.1 mega run's 294 fixed test runs (42
    suites by 7 fixes), 259 matched the released tests, 74 of them implied and never run, and none
    found a genuine new failure: 36 suites were clean after every fix and spent 180 runs, 747
    CPU-minutes (mypy 170, optuna 130, dask 91), to learn it. The suites' tests are 79% of the run's
    2,010 CPU-minutes, and the seven fixed parts 946. Build one patch from the seven fixes' records
    and run the tests once on it: equal to released, every part is implied by it; else the per-fix
    parts run as today. The fixes conflict on a few bindings in 37 of 42 suites (1 to 30; pandas 464,
    mypy 73, xarray 71): a priority (unsafe's annotation, then the trace's, then the checkers in a
    fixed order), or the fallback. The same assumption the tiers' implication makes: fewer
    annotations don't fail where more passed. Done: the union is a fix step of its own
    (`infer-union`: `--fix --unsafe-fixes --infer-with` every checker `--infer-from` the trace, so
    the priority is constricter's own, the guesses, then the checkers in the run's order, then the
    trace), and its tests' part runs before every fix's, which stand on it where it was the
    released tests' (`patch: union`) and run as before where it wasn't. On the 0.4.0-rc.1 mega run
    no fix broke a test on any of the 42 suites, whose 178 fixed runs took 812 CPU-minutes. The
    0.4.0-rc.2 mega run, the first with the union, took 91 minutes on 16CPU/60GB (rc.1's 134) and
    1,098 CPU-minutes (1,655), with the same fixes, tests table and no test a fix broke: the union's
    run was the released tests' on 38 suites, and 266 fixed parts stood on it, 22 ran. On django,
    nibabel, black and sphinx it wasn't, by a timing test (django's `test_crafted_xml_performance`)
    and tests no fix's own run failed: flaky under load, so their 28 parts ran. The fixed parts took
    286 CPU-minutes and the union steps 148. Its first run had no record to size the union's steps
    by: its fix step was held 11.7 GB (dask's took 18.2) and waited up to 9 minutes, its tests 1 CPU
    (mypy's kept 5.6 busy), so the next run, sized by this one's, should be quicker still. About 5
    hours; coverage unchanged.
11. **First-round hints cached across runs.** The `infer-*` steps used 290 CPU-minutes and 114
    step-minutes of the 0.3.9-rc.1 mega run (stripe's basedpyright 22.6 minutes, the standard
    library's 21.4 at 12.3 GB), and their memory, not the CPUs, kept the early steps waiting
    (pandas's basedpyright waited 22 minutes for 16 GB; the 0.3.8-rc.1 basic run's pyrefly 31 for
    20 GB). The first round asks the checker about the released text (`cli/lsp/hints.py`), which
    constricter's version doesn't change: keep its hints by file text, checker build and environment,
    as `remembered.py` keeps hung-file markers, and ask only for the later rounds' fixed text. 44 of
    47 tags were unchanged between the mega runs. Done, not yet run: every round is kept whole in
    the cache (`cli/lsp/stored.py`), by the checker's build, the text of every file asked about, the
    workspace's settings files, the environments' installed distributions and the code that asks;
    a round kept starts no server, and `--infer-fresh` asks again. Not a workspace file that isn't
    asked about: walking the tree cost as much as a round. A later round is kept too, for the next
    run with the same fixes. Left: the steps' seconds then measure less of the checker, which the
    report doesn't say yet. Done when a mega run's `infer-*` steps read the first round from the
    store and the hints are the same. About 6 hours; coverage unchanged.

### Large: more than 8 hours

1. **Types observed at run time, past what a parameter gives.** `python -m constricter.trace`
   records what each binding of a function's locals held, and `--infer-from` takes them as hints
   ([Done](#--fix)): only for a local an assignment or a `for` loop binds to a value taken from a
   parameter no checker types. Hints for every local brought 32 new basedpyright errors with 127
   fixes on pydantic (a checker types the value wider than the run saw); under that rule none, and
   one fix there. Measured and not worth building: the parameters' types, which the trace already
   holds, as `callers`' seeds, for `--fix`'s own inference to type what's computed from them: 47
   more fixes on pandas's `tests/frame/methods` and 125 more errors (a parametrized `str` passed
   where pandas declares a `Literal`); a class's alone, 4 and 2. 77% of the bindings with no fix are
   in functions with no annotations (in the 41 sampled directories, 13,992 of 28,931 are a method
   call, an attribute, a subscript or a copy of such a value).
   - [x] **A type per binding**, not per function: what a name holds as the statement binding it
         ends, by `sys.monitoring`'s line events (`sys.settrace`'s before Python 3.12), for a loop's
         target, a name bound in a loop and one bound again.
   - [x] **More values spelled**: a class nested in another (`Outer.Inner`), and a generic one by
         the arguments it was made with (`Box[int]()`) or, a builtin container of its own type
         variables, by its elements.
   - [x] **pytest-xdist's workers**: each pytest process the run starts records itself (the run
         names `constricter.trace` in `PYTEST_PLUGINS`), and the run's trace has theirs.
   - [x] **`self.attr`** where the class declares nothing: a local taken from an attribute a class
         with no base stores only unannotated parameters in.
   - [x] **Counted on the corpora**: a run's `traced` step traces a package's tests before a fixed
         run that reads the trace, and counts its fixes and the new errors. On SQLAlchemy 179 fixes
         and 6 new errors, on pandas 1,443 and one, on pydantic one and none, past what
         `--fix --unsafe-fixes` brings; none at a traced binding, once a parameter the function
         tests, binds again or gives a default isn't taken for untyped (3 of pandas's were).
   - [x] **Django's tests, by their script**: `runtests.py` in one process (`Suite.script`), 20
         minutes traced. 462 fixes rest on the trace, and its tests are the same after; it has no
         type checker.
   - [x] **The four in one run**: the super and the mega run's `traced` steps: 462 fixes rest on
         Django's trace, 178 on SQLAlchemy's, 1,429 on pandas's and one on pydantic's.
   - [ ] **No new error at a traced binding**: after the trace's fixes SQLAlchemy's mypy finds 6 new
         errors and pandas's checkers 3, three of them traced to a traced fix (`fk: ForeignKey`,
         passed where a `ForeignKeyConstraint` is taken; `index: Index`; `loc: int`, then iterated):
         a local whose value a parameter gives, typed narrower than its function uses it. On the
         mega corpora's suites the trace's fixes bring 4 errors past the guesses' own: 3 of pint's
         (`quantity: Quantity`, a traced fix in `numpy_func.py`: "Class definition for "Quantity"
         depends on itself", on its line and two a `builtin` fix shares) and one of altair's, blamed
         on a certain `call` fix (`normalized_engine: str`, `mimebundle.py`) that brings none
         without the trace. Most fixes rest on a trace in networkx (434), dask (339) and botocore
         (299), with no new error and the same tests.

   Done: a traced suite types a loop's target. Left: the three traced fixes above not offered,
   pint's and altair's read, and none like them on the mega corpora's suites. About 10 hours left;
   coverage down by the traced fixes withdrawn.

2. **A method's `return` of an untyped value.** Of the 11,959 `self.method()` bindings with no fix,
   5,617 call a method the class doesn't define itself, and 5,436 one whose `return` gives a value
   `--fix` can't type: a tuple (1,858), a call (1,455), a local or another name (1,396), a subscript
   or attribute (272). Only 137 return an unannotated parameter (26 nothing else), and in none of
   those classes does every `self.method(...)` call pass it a literal: typing a method's parameters
   by its callers, as `callers` types a plain top-level function's (3 fixes on pandas), reaches
   almost none of them. What's left is the values themselves: the tuple's parts, the call, the
   local. Done when a method returning its parameter types its calls. About 14 hours, for about 0.3%
   (some 800 guesses).
3. **Operators and iteration by their classes' methods.** `enumerate`, `zip`, `map` and `reversed`
   bound to a name are typed (`enumerate[str]`, by hand), and `iter` is now; `filter` isn't (its
   predicate narrows): `builtins.pyi`'s generic functions aren't run through the overload matcher
   (`abs`, `min`, `sum` and the like, and the builtin numbers', sequences' and sets' operators, are
   typed by hand, for builtin types alone). A standard-library class's operator is typed by its
   method's signatures, where both operands are a builtin's or a non-generic library class's
   instance (`when - start`, `price * 2`). A loop over a standard-library class's instance is typed
   by its `__iter__` (a file, `itertools.combinations(...)`); one over a method's call whose return
   names `Self` too (`path.iterdir()`, `path.glob(...)`). Counted, among the bindings with no fix,
   before the two done: `iter(...)` bound to a name 155, `zip` 37, `map` 32, `reversed` 19; `max`
   and `min` 168, `sum` 29; a `/` with a string on its right 365 (a fix now where its left is a
   known `pathlib` path), and a tuple added to something 65, of 4,990 binary operations (most
   between two values of no known type); loops over `os.walk(...)` 87 and `itertools`' functions 92.
   A loop over `x.items()` (1,861), `zip` (644) or `enumerate` (611) has no fix for its arguments'
   types, not for this.
   - [x] **A loop over `os.walk(top)`**, whose return nests deeper than the tables hold: a `str` and
         two lists of them, by a `top` that's a `str` or a `pathlib` path; `bytes` by a `bytes`. 4
         more on Django, where most `top`s have no type.
   - [x] **`iter(xs)` bound to a name**: an `Iterator` of what a loop over `xs` binds, imported
         where the module can name it. 2 more on Django.
   - [x] **`max`, `min` and `sum`** of what isn't a builtin number, and `filter`: `min` and `max`
         typed any elements already; `sum` of a class's instances is a `T | int` (`T` from a
         start of it), `filter(f, xs)` a `filter[T]` where `f` can't narrow. Of the standard
         library's bindings of the four with no fix, most take values of no known type
         (`min(count, 8192)`, a parameter); 6 more fixes there.
   - [x] **A generic class's operator** (`Counter[str] + Counter[str]`), a reflected method's
         (`2 * span`), and a checked file's class under a library one: the tables hold the
         reflected methods; a generic operand binds the operand's template by its type arguments;
         a module's class under a library one takes that one's operators where it binds neither.
         Left alone: a template of the class's base (`OrderedDict | OrderedDict`, by `dict`'s),
         which the tables can't tell takes it, and a module's class under a generic library one
         (`class Queue(deque[int])`), which no fix names yet (Large 5).
   - [x] **A loop over the rest of `itertools`**, and a tuple added to something:
         `chain.from_iterable` binds its `_S` by its argument's elements' elements (the tables'
         `ei`), and a generic class's classmethods are held (`OrderedDict.fromkeys`);
         `zip_longest` with no `fillvalue` and `starmap` of a generic function stay typeshed's
         `Any`.

   Done when each of those is a fix: all are, not yet run on the corpora, where the reach of the
   last two is small (some tens of bindings). For about 0.3% (some 800 fixes, of the 1,050 those
   reach).

4. **Narrowed reads.** A read of an `X | None`, or of a union the function tests, has no fix or only
   a guess: a checker narrows it where `--fix` doesn't follow the test
   (`if self.conn is None: return`, then `conn = self.conn`). Counted: of the 13,972 bindings with
   no fix that copy a name or an attribute in a function, 424 follow a test of what they copy in it:
   `is None` (159), `isinstance` (148) or its truth (117); 16 more are guesses now.
   - [x] **A read nothing narrows**: one of an `X | None` whose function neither tests nor stores
         it, nor what it's read of, has its declared type, a guess. 25 on SQLAlchemy, 7 on Django
         and 5 on pydantic; their type checkers, and pandas's, find nothing new.
   - [ ] **The narrowed type**: follow `is None`, `isinstance` and truth tests through a function's
         branches, and offer what every path to the read agrees on.

   Done when `conn = self.conn` after the `return` is a `Connection`. About 11 hours left, for about
   0.2% (some 400 fixes).

5. **The project's own generic classes.** A generic class the checked files define is skipped whole:
   its methods' returns and attributes depend on how it's parameterised (sqlalchemy's `Mapped[T]`,
   `Select[T]`). Bind its type parameters by the receiver's arguments, as a standard-library or
   installed generic class's are. Counted: sqlalchemy defines 101 generic classes (their subclasses
   included), pandas 30, pydantic 11; django, Twisted and pip none. 75 bindings with no fix are a
   member of a name annotated with one, parameterised (74 of them sqlalchemy's), and 246 a member of
   `self` in one's own method (sqlalchemy 136, the standard library 77, pandas 30); a receiver typed
   by inference isn't counted. Done when `rows.first()` on a `Result[Row]` is a `Row | None`. About
   10 hours, for about 0.1% (some 300 fixes).

6. **Annotations held to a run.** The corpora's witness holds each fix to the values its package's
   tests bind (`tests/corpus/witness/constricter_witness.py`): of the certain fixes a test could
   tell of, 99.0% hold on pydantic, 99.8% on mcp and narwhals, and what differs is a declared type
   the tests contradict (`multiple_of: Decimal | None`, bound to an `int`) or a test's stand-in. The
   same check of a project's own annotations, as `python -m constricter.trace --check`: each
   annotated local, parameter and return held to what a run binds, and those a value differs from
   reported as an offence with the type seen. It needs the witness in the package (tested as the
   tracer is), a container's elements held to its arguments, and a protocol's members looked for
   where `isinstance` can't. `typeguard` does the last two, as an optional extra there: the package
   has no dependency. Done when a traced run of this project's own tests reports no annotation of
   its own. About 14 hours; coverage unchanged: it finds wrong annotations, not missing ones.

### Scope

What the rules never see. Both are the largest gaps against every line typed, and neither counts
among the 252,056 offences: each adds offences of its own.

1. **Instance attributes.** `self.x = value` in a method is no binding the rules report:
   `rules/scoping.py` collects the stores only to feed the `assigned` guess for reads of `self.x`.
   Of the 47 corpora's bindings with no fix, 5,999 are a read of `self.x`, 1,660 of them in
   annotated functions, and each traces back to an untyped store the census never counts. A code for
   an attribute first stored in a method, unannotated there and undeclared in the class body, fixed
   as a local is (`self.x: int = 0`, which a type checker takes as the attribute's declaration): by
   the value's type, widened over the class's other stores as `rebound` widens a local's, and
   counted by `--coverage`. Count the stores first: the census sees only name targets. Done when a
   plain class's untyped stores are reported and fixed, the corpus suites the same after and no new
   type error. About 12 hours.
2. **Signatures from the project's own inference.** `returned` decides a function's return where its
   `return`s agree, `callers` an unannotated parameter every call passes one type and `fixture` a
   test's, but each types only the locals bound to them: no edit writes `-> T` on the def or `: T`
   on the parameter (`Edit` has `annotate`, `replace` and `declare`). `pyrefly infer` and
   `dmypy suggest` were measured for signatures ([Done](#corpus)), never constricter's own certain
   returns written back, which turn every caller's `returned` guess in other files into a certain
   fix and give ruff's ANN201 a fix it lacks. An edit kind for the signature; `-> T` where the
   function's `return`s decide one type (a method's a guess: a subclass may return another),
   `-> None` where none returns a value, a parameter's by `callers` and `fixture` as the guesses
   they are; opt-in codes, as LVA012 is, since ruff's ANN reports the offences already. Done when
   the corpora's own type checkers find no new error after the returns alone, and `--fix` on pandas
   gains the callers' fixes the written returns make certain. About 10 hours; coverage unmeasured:
   it moves guesses to certain more than it adds fixes.

### Inference

Gaps the census exposes in what `--fix` infers, smallest first.

1. **`getattr` by a literal name.** 576 of the 1,268 `getattr(...)` bindings with no fix on the
   seven corpora name the attribute as a literal, 521 of them with a default: on a receiver whose
   type is known that's `obj.name`'s type, with a default `T | D`; today an `Any`, or an `Any | T`
   (`fix/values/shapes.py`). Done, not yet run: a literal name that `obj.name` could spell is typed
   as that read is, at any `vague` (`| None` by a `None` default, joined with a default of another
   plain type), its guesses the read's; not an `X | None` read with no `None` default, which a check
   narrows. On pydantic no fix more: its 44 are dunders on receivers of no known type
   (`__module__`, `__set_name__`), or attributes the receiver's class doesn't declare, which is why
   `getattr` is used; the other corpora's count is a run's. Done when
   `getattr(self.conn, "timeout", None)` is typed as `self.conn.timeout` is. About 3 hours; coverage
   up to 0.2%, likely far less.
2. **An assignment's `# type:` comment as its fix.** With `type-comments` off, `x = v  # type: T` is
   LVA001 and its fix is inferred from `v`, the author's `T` ignored (`rules/binding.py` reads the
   comment only to decide whether the name is annotated); a loop's comment (LVA003) is already the
   declaration written, and dropped. The same for an assignment and a `with` target: `T` as the
   annotation, certain, the comment dropped, where `T` parses and names what the module can.
   Unmeasured: the census doesn't see comments. Done when pip's modules without `__future__` imports
   keep their comments' types under `--fix`. About 3 hours; coverage unmeasured.
3. **`pytest.importorskip("mod")` as an import.** 272 bindings on the seven corpora are its `Any`,
   and what's read of them (`pa.array(...)` in pandas's tests) has no fix either. The name is the
   module the literal names: known as `import mod as name` is for what's read of it, the binding
   itself left (an annotation would hide the module from a checker). Done, not yet run: the index
   takes the name as the module where every binding of it in the file is that call, and an import
   a fix adds from it goes under `if TYPE_CHECKING:`. Nothing more on pydantic or pandas's
   `tests/io` in all scopes: the packages pandas skips for (pyarrow, scipy, matplotlib, lxml,
   numba) aren't in the corpora's environment, and sqlalchemy's reads were typed through the
   file's own `TYPE_CHECKING` import already. Its reach is a run's, on corpora whose environment has
   what they skip for. Done when `pa = pytest.importorskip("pyarrow")`, then
   `arr = pa.array(...)`, types `arr`. About 3 hours; coverage unmeasured.
4. **`defaultdict` and `Counter` through `filled`.** 229 `collections.defaultdict(...)` calls have
   no fix on the 47 corpora ([Done](#--fix) states the limitation, with no item): `filled` types an
   empty container by what the function adds to it, so `defaultdict(list)` is a
   `defaultdict[K, list[V]]` by its `d[k].append(v)`, `Counter()` a `Counter[K]` by its `c[k] += 1`
   and `update`. Done when both are fixes, guesses as `filled` is. About 4 hours; coverage under
   0.1%.

### Guesses

Each is measured as every guess is: held to the corpora's type checkers and traced suites
([LIKELY.md](LIKELY.md)), and kept only where it passes the bars.

1. **The text overload.** The overload matcher leaves an argument of unknown type open and needs the
   open signatures to agree, so `os.path.join(dir, name)` fails on `str` against `bytes`: `os.path`
   has 688 calls with no fix on the 47 corpora, `os` 246. A guess for a function overloaded on
   `AnyStr` alone, with no argument known: its `str` signature's return. Done when measured; kept
   where the witness finds `bytes` under one in a hundred. About 4 hours; coverage about 0.3%.
2. **Name consistency.** A parameter or local with no fix whose name is annotated with one type
   everywhere else in the checked files, at least three times and never another
   (`request: HttpRequest`, `df: DataFrame`), takes it. The 2026-10-02 rows show the names
   concentrated (`result` 9,213, `expected` 3,609, `df` 663, `parser` 580), and the agreement bar
   decides the precision: size it from the rows and the index's annotations first. Done when
   measured; a mechanism if it passes the bars. About 8 hours; coverage unmeasured.
3. **A receiver by what's read of it.** 13,077 of the seven corpora's 149,972 bindings with no fix
   are a copy, a member or a method call of an unannotated parameter. The methods and attributes a
   function reads of a parameter often name exactly one class in the index (the checked files, the
   standard-library tables and the installed packages; `loose.needs` already indexes method names
   for the scheduler): where they do, the parameter is that class, a guess, and what's read of it
   follows. Done when measured; kept where the witness agrees. About 14 hours; coverage unmeasured,
   up to 5%.

### Measurement

What to measure before building, smallest first.

1. **A `vague = 0` run.** The runs use the default, no `Any` anywhere, which rejects `NDArray[Any]`,
   `dict[str, Any]`, `pickle.loads` and `json.loads`: `numpy` alone is 4,320 calls with no fix on
   the 47 corpora. One run at `vague = 0` says what the default costs on the scientific corpora
   (xarray, dask, networkx, pandas). Done when the census is read at both. About an hour beside the
   run; coverage unchanged.
2. **Two checkers agreeing, likely.** `checker` is one set to LIKELY.md's bars, by checker; a hint
   basedpyright, ty and pyrefly agree on (two of them, or all three) is a set of its own, measured
   the same way, and `--likely` applies it where one checker's hint alone doesn't pass. Done when
   the mechanisms table counts the agreeing sets. About 3 hours; coverage unchanged (`--likely`
   gains what passes).
3. **Why a call has no fix.** The census classifies the shape of a value with no fix, never why the
   fix failed: a vague return, open overloads that disagree, a receiver of no type, an import it
   can't resolve, an untyped callee. A column for it, read from the check (`--format=json` gains the
   reason a call's fix was refused), so the items above are sized in one run, not from the rows by
   hand. Done when `census.md` has the table by reason. About 4 hours; coverage unchanged.
4. **One type at run time, no fix.** The traced suites already know what each binding held; for each
   binding with no fix, whether the run saw one type is both the upper bound of any inference and a
   bug finder (it would have named `cm` above). A table by shape in the `traced` step: bindings with
   no fix, those the run bound to one type, and the commonest sources. Done when the table is in a
   run's report. About 4 hours; coverage unchanged.
5. **Test results as data.** A suite's tests are read from pytest's and unittest's text (`-rfE`
   lines, the summary), which misread sphinx's captured log lines as failures and spelled 4 suites'
   failure ids two ways between runs. pytest's `--junitxml` or `--report-log` (and unittest's
   verbose output, for django's runner) in `corpus_suite.tested` gives exact test and skip ids,
   skip reasons and per-test durations: sqlalchemy's skip-count flake by name, with no rerun, and
   what test-level sampling or sharding would later need. Done when the records hold each run's
   test ids and durations and the tests table is read from them. About 3 hours; coverage unchanged.
6. **What the records hold and no table shows.** The 0.3.9-rc.1 mega run's records have: likely
   fixes absent from unsafe (networkx 13, pandas 216: the fixes interact, so likely isn't unsafe
   filtered); a fix's `typed` count off by one from coverage plus its fixes on mypy and sphinx (a fix
   that didn't make its binding typed); and `traced` against released, a flakiness sample for free
   (equal on 38 of 42). Tables for the three, from the records alone. Done when `report.md` has
   them. About 2 hours; coverage unchanged.
7. **Tier the runs by what moves.** On the 44 corpora whose tag held between the two mega runs, the
   fix counts moved on 31 to 36 by a median -0.14% (certain), -0.13% (likely) and -0.32% (unsafe),
   the fast sets giving the right sign at about twice the size (`infer-ty` noisier: -1.74% against
   -0.38%), offences not at all, and the whole-set gains came from pydantic's and sqlalchemy's tag
   bumps. For a change's direction, a run of `fast-small`, `fast-large` and one slow-large corpus a
   quadrant; the suites at full breadth, and every size, in the release mega runs alone. Done when
   `runs/` has that file and CONTRIBUTING says when each run is the one. About 1 hour; coverage
   unchanged.

## Ongoing

- **Revisit the [disabled rules](CONTRIBUTING.md#disabled-rules)** as tools change (last checked
  2026-10-15: harden-runner's block policy now works on macOS and Windows, and zizmor's
  `self-repository` can come back once `ossf/scorecard-action` v2.5.0 is taken, both with the other
  repos' shared workflows; astroid 4.3, fastjsonschema 2.22 and reuse 6.2 still can't go). About an
  hour a pass.
