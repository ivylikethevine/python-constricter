# Roadmap

## Done

### Rules

- **LVA001–LVA004**, with `all-scopes` for module and class bodies (LVA004), and `# type:` comments
  counted automatically in modules importing Python 2 `__future__` features.
- **LVA005 and LVA006** (vague, deeply nested), **LVA007** (annotated again the same way, per
  straight-line block), **LVA011** (a tuple longer than `max-length`, 4: measured, annotations list
  5 or more types only 3 times on the corpus).
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
  `rows[0].strip()`, however deep, through `constricter.fix.members`); `cls` in a classmethod as
  `type[C]`, and `type(x)`; computed values (conditionals, arithmetic on builtin scalars and lists,
  comprehensions, `sorted`/`list`/..., `await`), comparisons by `in` and `is`, or of builtin values
  (a `bool`); a union the author would write (`a if c else None`, `a or b` of one type); displays
  that unpack (`[*names, s]`, `{**d, k: v}`), `d.get(k, 0)` and `os.environ["X"]`; a subscript of a
  standard-library class's instance by its `__getitem__` (`proxy["k"]` on a
  `MappingProxyType[str, int]`); standard-library module variables (`sys.path`); chained
  assignments' names, declared before them (`i = j = 0`), and a `:=`'s, before its statement; a
  quoted annotation read as its text (`xs: "list[Node]"`); the `self` a function defined in a method
  reads; a `# type:` signature comment's return, as a declared one; `typing.cast`; `x = None` later
  rebound to one type as `T | None`; loop targets (`enumerate` and `zip` part by part, `map`, a
  generator expression, any mapping's items, an `Iterable[T]`'s `T`) and unpackings, name by name
  (`a, b = x, 1`, `a, b = s.split(",")`, `first, *rest = names`, and the parts that aren't vague of
  a call declaring a `tuple[Row, dict[str, Any]]`), declared before the statement, as a `with`
  statement's target is, by its context manager's `__enter__`; a method a class inherits, from the
  base that defines it, in the module, another checked file or the standard library (`self.id()` in
  a test case); an unannotated generator function's calls, by its `yield`s; a call to a function
  decorated by what gives it back (`functools.cache`, pandas's `@set_module("pandas")`, by its
  declared `Callable[[F], F]`); a call of a value typed `Callable[..., R]`, `type[C]` or a class
  declaring `__call__` (`handler(source)`, `cls()`, `cls.__new__(cls)`); an unpacked named tuple's
  names, by its fields, and a `with` target that unpacks; a `@contextmanager` method's `with`
  target; a module's type alias, declared `TypeAlias` (`alias`: certain where every Python the
  module runs on has it); fixes for LVA003 and LVA007. A tuple longer than `max-length` is
  `tuple[T, ...]`.
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
  (`m.string`). `defaultdict(list)` and `Counter()` stay untyped: their parameters come from later
  use. Generic classes' constructors are read from their `__new__` or `__init__`
  (`collections.deque(names)` is a `collections.deque[str]`, `array.array("i")` an
  `array.array[int]`); at module level, one some Python can't subscript at run time is quoted. What
  only some platforms or versions have is kept (`os.getuid()`).
- **Installed packages**: calls into an installed package that declares its types (`py.typed`, a
  stub package, a lone stub module) are typed by their declared returns as a checked file's are,
  found as the import system would on this Python's path and `VIRTUAL_ENV`'s; types are imported
  from a public module that re-exports them. Functions whose overloads or type variables their
  arguments decide are matched as the tables' are (`constricter.fix.stubbed`), through the package's
  aliases, type variables and protocols, the standard-library classes it names by the `scalars`
  table, and a class argument binding `type[T]`: 83 more fixes on pandas
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
  quoted where a module-level annotation is evaluated.
- **Guesses** apply only with `--unsafe-fixes`: a capitalised call taken to construct its class,
  LVA008's and LVA010's narrowing, an empty container typed by what's added to it (`append`,
  `extend`, `update`, ...), a method typed by its `return`s, an instance attribute by its
  assignments (`assigned`), a plain class's variable by its literal value (`member`: a class under
  plain classes, test cases and builtin exception or value classes, but for a variable a class above
  it declares otherwise), a call to a class the checked files define whatever its name's case, an
  unannotated parameter by what every call in the checked files passes it (`callers`, builtin types
  alone: callers' classes too would add 10 fixes on the corpora), and what rests on any of these.
  **Fix levels**: every mechanism has a stable id (`--show-fixes`, JSON), and `fix-select`,
  `fix-ignore` and `unsafe-fix-select` choose which apply.
- **Type-checker-backed inference** (`--infer-with basedpyright,ty,pyrefly`): the checkers' inlay
  hints type what `--fix` can't, as guesses, widened, checked and imported; with basedpyright it
  about doubles what `--fix --unsafe-fixes` types on the annotated corpora. A hint naming a class
  the file doesn't bind is a fix too, the class imported under `if TYPE_CHECKING:` by the import the
  hint's own edits carry, or one the module has there: only a class the index of checked files and
  installed packages, or the standard-library tables, define, and no generic one shown without its
  arguments: 27% more of basedpyright's hints are fixes on pydantic, sqlalchemy and django, and 19%
  more of ty's. A type alias the index finds (a name annotated `TypeAlias`, or bound to a subscript
  or a union) is taken as a class is, and a module's own composite alias is declared `TypeAlias`,
  imported from `typing` if it must be: on pydantic, 82 more aliases declared and 12 more fixes
  naming `CoreSchema`. ty's spellings are read (`Model@create_model`, `str & ~AlwaysFalsy`; an
  unpacked tuple is kept where the project's oldest Python parses it, `min-python` or
  `requires-python`'s, else written with `Unpack` where the module imports it, else dropped), and a
  hint naming a type variable is a fix only where its function's signature or its class names it.
- **No new type errors**: `corpus_suite.py --types` runs pydantic's, sqlalchemy's and pandas's own
  type checkers after `--fix` (none new) and `--fix --unsafe-fixes`. Where a checker would see a
  value otherwise, the fix is changed, made a guess, or not offered (see
  [FIXES.md](FIXES.md#what-a-type-checker-sees)): a name bound again takes every value (one type the
  file spells two ways, `CoreSchema` and `core_schema.CoreSchema`, counting once), and one first
  bound to no known type is a guess by a later binding's; a read of a union, or of what the function
  tests, is a guess, and one of an `X | None` isn't offered; an ALL_CAPS constant passed to a call
  is `Final`; a read a test around it narrows isn't offered its declared type; `Self` where the
  method says so; no generic class written bare, the standard library's included; no alias its
  module assigns in two branches (a variable, to a checker) written in another file; and a
  constructor guessed only where its callee is a type. The unsafe runs' new errors went from 20, 76
  and 165 (0.2.4) to 2, 5 and 36.
- **Safe by construction**: touches no class body but a plain class's, and that as a guess (no
  decorator, no metaclass, every base plain or a test case), keeps line endings and encodings, edits
  notebooks' cells in place, nothing broken on any corpus, and the corpus packages' own test suites
  pass identically before and after. One pass converges on every corpus, the standard library's
  tests included: a library type a callee's module doesn't import yet is named for its callers by
  the import its own fixes add.
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

### Command and output

- **Formats**: text, `full` (with the source line), JSON, GitHub annotations, SARIF (help text,
  `helpUri`, certain fixes as SARIF fixes, validated against the 2.1.0 schema in the tests), GitLab
  Code Quality, JUnit and rdjson (fixes as suggestions).
- `--diff`, `--show-fixes`, `--statistics`, `--explain`, `--coverage` / `--fail-under`, baselines,
  `--jobs`, standard input, `--exit-zero`, `--output-file`, and `--exclude` globs that also skip
  directory names in a walk.
- **Notebooks** (`.ipynb`), checked and fixed per cell; every JSON file read allows comments and
  trailing commas; every public entry point takes `str` or `bytes`.

### Integrations

- **Plugins** for flake8 and pylint (`C9101`–`C9112`); ruff through `lint.external`.
- **pre-commit** hooks (`constricter-fix` runs as one process, so its cross-module `--fix` sees
  every file) and pre-commit.ci; **tox**, **nox**, **Bazel** and **Pants** notes; **editor**
  settings for VS Code, Zed and Neovim.
- **A GitHub Action**: PR annotations, a per-code summary table, a `sarif-file` output, and a
  `version` input to install a PyPI release with uv; CI runs it on this project.
- **On PyPI** as `python-constricter`.

### Corpus

- **`tests/corpus/corpus.py`** (no crash) and **`tests/corpus/corpus_fix.py`** (nothing broken, one
  pass) on the standard library and pinned packages, in CI's Corpus job (Python 3.14);
  **`tests/corpus/corpus_table.py`** records each version's results in [RUNS.md](RUNS.md), with
  totals and percentages, and `--label` for a pseudo-version (`0.2.4-rc.N`); a release runs in a
  venv of its own with the corpus packages' as its `VIRTUAL_ENV`, so it reads the installed
  packages' types as this checkout does.
- **`tests/corpus/corpus_suite.py`** clones a corpus package at its pinned tag, installs its test
  dependencies as its CI does, and runs its test suite as released, after `--fix`, and after
  `--fix --unsafe-fixes` (see [RUNS.md](RUNS.md)); `--types` runs each one's own type checker the
  same way and traces each new error to its fix mechanism, and `--infer-with CHECKERS` adds a run
  with their hints' fixes.
- **Python 3**: the standard library, `django` (the 5.2 LTS, for 3.11), `sqlalchemy`, `pydantic` and
  `pandas` 3.0.6 (1,421 files with its tests: overloads, generics, `TYPE_CHECKING` imports).
- **Python 2**: Twisted 12.3.0 (pure Python 2, 147 of 819 files unparsable) and pip 20.3.4 (the most
  type comments in `__future__` modules), hash-pinned sdists `tests/corpus/corpus_sources.py`
  fetches.
- **What `--fix` still can't type**, counted by **`tests/corpus/corpus_untyped.py`**
  (`python -m tests.corpus.corpus_untyped`; `--rows` writes every binding as JSON lines): each
  untyped binding, classified by the statement that binds it, the shape of its value, its scope,
  whether its function is annotated, and what a call through an import resolves to and where from.
  On every corpus: 251,848 untyped bindings, 160,085 with no fix at all, 77% of those in functions
  with no annotations. The items under [Next](#next) are sized by it: each count is the bindings
  with no fix an item could reach, not what it would fix. Left alone on purpose: `getattr(...)`, a
  bound method's alias (`append = parts.append`), `dict.get` on a `dict[str, Any]`, and a
  `TypeVar`'s own declaration. Measured and too small to build: an unannotated parameter typed by
  its literal default (76 bindings) or its docstring (325); and signatures first, by `pyrefly infer`
  before `--fix`: 2,254 more certain fixes on the six Python 3 corpora (19.8% of their untyped
  bindings fixed, then 20.8%), since it annotates 8% of the unannotated parameters, most of the
  returns it adds are `-> None`, and it left one of pydantic's files unparsable; and an unannotated
  function's `return`s of two types, or of one and `None`, joined into a union: 275 more fixes, and
  38 new basedpyright errors (a union one of whose types is wrong, or that the caller never
  narrows).
- **Why `name = self.method()` has no fix** (8,195 bindings, before the inherited methods): the
  method is the class's own (46%), a base's in the file (12%) or in another (10%), a class attribute
  a subclass sets (`self.type2test()`, `self.dumps()`: 28%, left alone), or a library base's (5%).
  Of the 5,479 found, 4,078 have a `return` whose value has no type: a name (1,779: an unannotated
  parameter, or a local with no fix), a call on another value (823), another `self.method()` (408).
- **Other type checkers' servers**, driven through `constricter.cli.hints` on pydantic, sqlalchemy
  and django (26,716 bindings with no fix): the share of them each one's hints type, as `--fix`
  judges hints now, is 8.2% for ty, 10.7% for basedpyright and 13.7% for pyrefly. Plain Pyright's
  server has no inlay hints (they're Pylance's and basedpyright's), mypy has no server
  (`dmypy inspect` answers one location at a time), and pytype is discontinued.

### CI, security and releases

- **CI** (`ci.yml`): every check in [CONTRIBUTING](CONTRIBUTING.md#development), the pre-commit
  hook, Markdown, tests on Linux, macOS and Windows × Python 3.11–3.14 plus PyPy 3.11 and
  free-threaded 3.14 (100% branch coverage), the build and a wheel smoke test, the Action, and the
  corpus. The project's own code passes `--level=suffocate --all-scopes` at 100% annotation
  coverage. A tree CI already passed (the merge to `main` after its pull request, the release tag on
  it) isn't tested again: a `tested-tree` artifact records each passing tree, and the next run on it
  skips every job.
- **Security** (`security.yml`, weekly too): CodeQL, zizmor (pedantic), actionlint, pip-audit,
  dependency review, and gitleaks over the whole history; OpenSSF Scorecard; lychee on links.
- **Pinning**: actions by SHA, Python dependencies by hash (`uv.lock`, checked in CI), npm by
  lockfile, uv and actionlint by version; Dependabot updates them weekly.
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
- **Layout**: a flat `constricter/` in `rules/`, `fix/`, `cli/` and `plugins/`, all but seven
  modules under 750 lines (`fix/stubbed.py`, `overloads.py`, `inference.py` and `project.py`, and
  `rules/annotations.py`, `checker.py` and `scope.py`); the standard-library tables in
  `constricter/fix/tables/`, their generator in `stdlib_tables/`; docs in `docs/` (changelog,
  contributing, security, integrations, fixes, runs), release notes grouped by
  `.github/release.yml`, issue and PR templates, CODEOWNERS.
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

## Next

By scope (smallest first) and, within each, by value: the bindings with no fix an item could reach,
of the 160,085 on the corpora, or of the 26,365 on pydantic, sqlalchemy and django for an item that
needs `--infer-with`. Each item says what it is, why, how, and when it's done. The counts predate
the fixes for type aliases, class variables under builtin bases, calls of typed callables and named
tuples (measured on pydantic alone: 2,042 bindings with no fix to 1,667): they need recounting.

### Small: a day or less

Nothing open.

### Medium: a few days

1. **`--infer-with` in `corpus_suite.py --types`: pandas.** pydantic's and sqlalchemy's are in
   [RUNS.md](RUNS.md): 26 and 47 new errors after basedpyright's and ty's hints' fixes, most traced
   to a hint (a name bound again to another type, a class less exact than the package's checker
   sees). pandas's hasn't been run. Done when it's recorded, and a released line's error an inserted
   line moves is no longer counted as new.
2. **More context managers.** 4,167 `with` targets had no fix (before a target that unpacks was
   split, and a `@contextmanager` method typed): `self.assertRaises(...)` and its kin (typeshed's
   class for them is private), `tarfile.open`, `tempfile.TemporaryDirectory()` and `shelve.open`
   (generic classes whose arguments the call doesn't say), `warnings.catch_warnings`,
   `contextlib.closing`, `test.support`'s (not in typeshed), and an `async with`'s by `__aenter__`.
   All but `test.support`'s are the tables' to hold (`stdlib_tables/`): a constructor whose
   `__init__` overloads declare `self`, a private class's public path, `__aenter__` beside
   `__enter__`. Count each first. Done when the three largest are fixes.
3. **Operators and iteration by their classes' methods.** `enumerate`, `zip`, `map`, `iter` and
   `reversed` bound to a name have no fix (`enumerate[str]`: at module level, a builtin some Python
   can't subscript at run time needs quoting), nor do `path / "x"`, `min(n, 1.5)` (two number types)
   and a `tuple` added to another: `builtins.pyi`'s generic functions and the classes' operator
   methods aren't run through the overload matcher (`abs`, `min`, `sum` and the like are typed by
   hand, for builtin types alone). Nor is a loop over anything but a builtin container or a mapping
   (`path.iterdir()`, `os.walk(...)`, `itertools.combinations(...)`), whose element is its
   `__iter__`'s. Count each first. Done when each of those is a fix.
4. **The project's own overloads.** A function the checked files define with `@overload` (pandas'
   `concat`) is skipped as redefined: 1,689 calls. Match its signatures as the standard library's
   and installed packages' are (`constricter.fix.overloads`). Done when a call the arguments decide
   is typed, and one they don't is left alone.
5. **Partly vague hints, opt-in.** The largest group of hints dropped is a type with `Any` in it
   (`dict[str, Any]`, `list[Any]`): 4,393 of the three packages' bindings with no fix for
   basedpyright, 16.4% of them. It is the value's type, and LVA005 would report it: a fix kind of
   its own, off by default, trades an LVA001 for an LVA005. Done when `fix-select` can turn it on.
6. **An unannotated method's type, in another file.** A module's functions' `return`s type their
   calls in the files importing them; its classes' methods' don't: 132 `self.method()` bindings
   whose base is another file's and whose `return`s give one type (Twisted's `self.mktemp()`), and
   every such call on an imported class's instance. Carry them with the functions', as guesses. Done
   when `path = self.mktemp()` is a `str` under a base class of another file.
7. **A library base out of sight.** A class under a standard-library class gets the methods it
   inherits from it (`self.id()` in a `unittest.TestCase`), but not behind another checked file's
   class (django's `TestCase`, itself under `unittest.TestCase`: a module's index entry holds its
   own classes' methods alone), under an installed package's class, or a generic one
   (`collections.OrderedDict`), nor a method its arguments decide. A class-side method a class takes
   from another file's base (`Sub.make()`, `make` its imported base's) has no fix either. Done when
   `name = self.id()` in a class under another file's test case is a `str`.
8. **Awaited calls.** `await` types only a call to one of the module's own `async def`s: not a
   method's (`await self.fetch()`), another checked file's, nor the standard library's
   (`await asyncio.open_connection(...)`, `await reader.readline()`), which the tables don't hold.
   In 41 directories sampled across the standard library, pandas, django and sqlalchemy, 382
   bindings with no fix are an `await`, 355 of them in `asyncio` and its tests. Done when
   `line = await reader.readline()` is a `bytes`.
9. **A tuple alias, unpacked.** A named tuple's fields type an unpacking's names; a declared alias
   of a tuple (`Pair: TypeAlias = tuple[int, str]`, or a union of them) doesn't. Count them first.
   Done when `a, b = pair()` under `-> Pair` declares each.

10. **The main process, in a parallel check.** With `--jobs`, what each file knows from outside it
    (`schedule.outside`) is still worked out one file at a time in the main process, which the
    workers wait on: about a third of a parallel check of the standard library. Most of it lists
    every function and class of every module a file imports (`project.spellings`, 1.3 million on the
    standard library) to find the few it uses: look up the names the file writes instead, or work it
    out in the workers. Done when the main process's share is under a tenth.
11. **A file checked again, whole.** A file whose functions' parameters every call types is parsed
    and checked again from the start (227 of the standard library's files, a fifth of a
    single-process check), as is each file of a cycle. Check again only the functions the new types
    reach, with the tree kept. Done when the second round costs under a tenth of the first.

### Large: a week or more

1. **A method's `return` of an untyped value.** Of the 11,959 `self.method()` bindings with no fix,
   5,617 call a method the class doesn't define itself, and 5,436 one whose `return` gives a value
   `--fix` can't type: a tuple (1,858), a call (1,455), a local or another name (1,396), a subscript
   or attribute (272). Only 137 return an unannotated parameter (26 nothing else), and in none of
   those classes does every `self.method(...)` call pass it a literal: typing a method's parameters
   by its callers, as `callers` types a plain top-level function's (3 fixes on pandas), reaches
   almost none of them. What's left is the values themselves: the tuple's parts, the call, the
   local. Done when a method returning its parameter types its calls.
2. **Class bodies of plain classes, past literals.** An annotation in a class body makes a
   dataclass's or a model's variable a field, so `--fix` annotates only a plain class's variable
   bound to a literal or a display of them (`member`, a guess). Counted without it: 15,336 bindings
   with no fix, 3,070 of them in a class with no base and no decorator (1,421 bound to a literal)
   and 2,456 under a test case's. A class under a builtin exception or value class is plain too now
   (162 more guesses on pydantic, no new basedpyright error there). Left: a value that names
   something (a call, a copy, an attribute), a name the body binds more than once, and a variable a
   test case's own class declares otherwise (`maxDiff = 80` under `unittest.TestCase`, typeshed's
   `int | None`, is still typed `int`: the tables' attributes would say). Done when the corpus
   packages' test suites and type checkers find nothing new after `--fix --unsafe-fixes`, `member`
   included.

## Ongoing

- **zuban as an `--infer-with` checker** once its server holds a project (last checked 2026-09-30:
  0.10.0 overflows its stack with pydantic's or django's files open and says nothing for two minutes
  on sqlalchemy's; a server per file types 15.3% of pydantic's bindings with no fix, below the
  others). It refuses a hint range ending past the last line, and is AGPL-3.0.
- **The Type Server Protocol** once a second checker serves it and it reaches 1.0 (last checked
  2026-09-30: 0.4.1, `pyrefly tsp` alone). `typeServer/getComputedType` gives a type as a structure
  with each class's declaring file, where an inlay hint's is text to parse.
- **Restore `reuse lint`** once `reuse` ships a wheel for Python 3.11+ (last checked 2026-09-22:
  6.2.0 still has only a CPython 3.10 one).
- **Test on PyPy 8** once hypothesis ships wheels for its ABI (`pp80`): CI's PyPy entry is pinned to
  7.3 (`pypy: v7.3.x`), since hypothesis has no pure-Python wheel (last checked 2026-09-30: 6.168.3
  has `pp73` wheels alone).
- **Revisit the [disabled rules](CONTRIBUTING.md#disabled-rules)** as tools change (last checked
  2026-09-22: COM812, one-line DOC201/DOC402 and `max-args` came back on; the rest can't go yet).

## Waiting on a step outside this repository

1. **The GitHub Action on the Marketplace.** It already works from any tag, and `action.yml` has the
   name, description and branding a listing needs: tick "Publish this Action to the GitHub
   Marketplace" when publishing a release.
2. **Trunk and MegaLinter plugin definitions**, submitted upstream. MegaLinter's is
   `mega-linter-plugin-constricter/constricter.megalinter-descriptor.yml` (usable now through
   `PLUGINS`); what's left is a pull request adding it to `.automation/plugins.yml` in
   oxsecurity/megalinter. Trunk's is drafted in `upstream/trunk/linters/constricter/`, for a pull
   request to trunk-io/plugins with the snapshot its test harness generates.
3. **A conda-forge recipe**, submitted to conda-forge/staged-recipes: drafted in
   `upstream/conda-forge/recipes/python-constricter/`, built from the sdist, which carries the
   tables. It built and passed its tests with rattler-build against flit-core; the build backend is
   hatchling now (`>=1.27`), which its host requirements name, not yet rebuilt.
