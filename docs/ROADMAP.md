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
  or another checked file; fixed-return builtins and `str`/`bytes` methods; members of any typed
  value (`self.index.name`, `rows[0].strip()`, however deep, through `constricter.fix.members`);
  `cls` in a classmethod as `type[C]`; computed values (conditionals, arithmetic on builtin scalars,
  comprehensions, `sorted`/`list`/..., `await`), comparisons by `in` and `is`, or of builtin values
  (a `bool`); standard-library module variables (`sys.path`); chained assignments' names, declared
  before them (`i = j = 0`); `typing.cast`; `x = None` later rebound to one type as `T | None`; loop
  targets (`enumerate` and `zip` part by part) and unpackings, declared before the statement; fixes
  for LVA003 and LVA007. A tuple longer than `max-length` is `tuple[T, ...]`.
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
  file's type the module doesn't import, under `if TYPE_CHECKING:` (no import cycle at run time),
  quoted where a module-level annotation is evaluated.
- **Guesses** apply only with `--unsafe-fixes`: a capitalised call taken to construct its class,
  LVA008's and LVA010's narrowing, an empty container typed by what's added to it, a method typed by
  its `return`s, an instance attribute by its assignments (`assigned`), an unannotated parameter by
  what every call in the checked files passes it (`callers`, builtin types alone: callers' classes
  too would add 10 fixes on the corpora), and what rests on any of these. **Fix levels**: every
  mechanism has a stable id (`--show-fixes`, JSON), and `fix-select`, `fix-ignore` and
  `unsafe-fix-select` choose which apply.
- **Type-checker-backed inference** (`--infer-with basedpyright,ty`): the checkers' inlay hints type
  what `--fix` can't, as guesses, widened, checked and imported; with basedpyright it about doubles
  what `--fix --unsafe-fixes` types on the annotated corpora. A hint naming a class the file doesn't
  bind is a fix too, the class imported under `if TYPE_CHECKING:` by the import the hint's own edits
  carry, or one the module has there: only a class the index of checked files and installed
  packages, or the standard-library tables, define, and no generic one shown without its arguments.
  On pydantic, sqlalchemy and django, basedpyright's hints type 27% more of what `--fix` can't
  (2,253 bindings, now 2,867) and ty's 19% more; after the fix, basedpyright finds 14 new errors on
  pydantic, where it found 21.
- **No new type errors**: `corpus_suite.py --types` runs pydantic's, sqlalchemy's and pandas's own
  type checkers after `--fix` (none new) and `--fix --unsafe-fixes`. Where a checker would see a
  value otherwise, the fix is changed, made a guess, or not offered (see
  [FIXES.md](FIXES.md#what-a-type-checker-sees)): a name bound again takes every value; a read of a
  union, or of what the function tests, is a guess, and one of an `X | None` isn't offered; an
  ALL_CAPS constant passed to a call is `Final`; a read a test around it narrows isn't offered its
  declared type; `Self` where the method says so; no generic class written bare, the standard
  library's included; and a constructor guessed only where its callee is a type. The unsafe runs'
  new errors went from 20, 76 and 165 (0.2.4) to 2, 5 and 36.
- **Safe by construction**: never touches class bodies, keeps line endings and encodings, edits
  notebooks' cells in place, nothing broken on any corpus, and the corpus packages' own test suites
  pass identically before and after. One pass converges on every corpus, the standard library's
  tests included: a library type a callee's module doesn't import yet is named for its callers by
  the import its own fixes add.
- **Fast enough**: the standard library checks in about 8s with `--jobs=1` and 1.5s with `--jobs=0`
  on 16 cores (from 227s profiled at 0.2.4): one shared walk of each module, kept with its tree from
  the cross-file index to the check, and a node's children listed without `ast`'s generators;
  whether a fix is a guess worked out only where there is a fix; each function's body indexed once
  for its empty containers; functions checked callees first; files in `order.plan`'s order, each as
  soon as the modules it calls into are done.

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
  totals and percentages, and `--label` for a pseudo-version (`0.2.4-rc.N`).
- **`tests/corpus/corpus_suite.py`** clones a corpus package at its pinned tag, installs its test
  dependencies as its CI does, and runs its test suite as released, after `--fix`, and after
  `--fix --unsafe-fixes` (see [RUNS.md](RUNS.md)); `--types` runs each one's own type checker the
  same way and traces each new error to its fix mechanism.
- **Python 3**: the standard library, `django` (the 5.2 LTS, for 3.11), `sqlalchemy`, `pydantic` and
  `pandas` 3.0.6 (1,421 files with its tests: overloads, generics, `TYPE_CHECKING` imports).
- **Python 2**: Twisted 12.3.0 (pure Python 2, 147 of 819 files unparsable) and pip 20.3.4 (the most
  type comments in `__future__` modules), hash-pinned sdists `tests/corpus/corpus_sources.py`
  fetches.
- **What `--fix` still can't type**, counted by **`tests/corpus/corpus_untyped.py`**
  (`python -m tests.corpus.corpus_untyped`; `--rows` writes every binding as JSON lines): each
  untyped binding, classified by the statement that binds it, the shape of its value, its scope,
  whether its function is annotated, and what a call through an import resolves to and where from.
  On every corpus (0.3.1): 251,848 untyped bindings, 165,111 with no fix at all, 78% of those in
  functions with no annotations. The items under [Next](#next) are sized by it: each count is the
  bindings with no fix an item could reach, not what it would fix. Left alone on purpose:
  `getattr(...)`, a bound method's alias (`append = parts.append`), `dict.get` on a
  `dict[str, Any]`, and a `TypeVar`'s own declaration. Measured and too small to build: an
  unannotated parameter typed by its literal default (76 bindings) or its docstring (325).
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
- **Layout**: a flat `constricter/` in `rules/`, `fix/`, `cli/` and `plugins/`, no module over 750
  lines; the standard-library tables in `constricter/fix/tables/`, their generator in
  `stdlib_tables/`; docs in `docs/` (changelog, contributing, security, integrations, fixes, runs),
  release notes grouped by `.github/release.yml`, issue and PR templates, CODEOWNERS.
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
  wheel 395 KB). A build from a checkout takes about 75s more here: 75 MB to download (60 MB of it
  Node, which basedpyright depends on and the generator doesn't use), and the generation. The Action
  pays it on every run, and a pre-commit hook once, on install.

## Next

By scope (smallest first) and, within each, by value. Each item says what it is, why, how, and when
it's done.

### Small: a day or less

1. **pyrefly as a third `--infer-with` checker.** Its hints type more of what `--fix` can't than
   basedpyright's or ty's on all three packages measured, and 2 to 7 points more than both together
   (pydantic: 28.0% of the bindings with no fix, 34.9% with pyrefly), as fast as ty. `pyrefly lsp`
   is one server (it works in parallel itself); it cancels a hint request when a later file opens
   (error `-32800`), which `hints.py` must ask again as it does `-32801`. It infers an unannotated
   function's return only as its configuration says (`infer-return-types = "checked"`): say so in
   FIXES.md. Done when `--infer-with pyrefly` types sqlalchemy and its type checker finds no new
   error.
2. **A type alias from a checker's hint.** basedpyright hints an alias's assignment as `TypeAlias`,
   which `--fix` writes only where the module already names it: 782 module-level bindings on the
   three packages have no fix. Import it from `typing` where the value is a type expression of its
   own (`Json = dict[str, "Json"] | str`): declared one, a bare class's alias
   (`memoized_property = generic_fn_descriptor`) loses the class's type parameters, which made 50
   new errors on sqlalchemy. Done when a module's composite aliases are fixed and its checker finds
   no new error.
3. **A hint naming an alias, or an unchecked package's class.** A name a hint's edits import is
   taken only for a class the index or the standard-library tables define (basedpyright shows a
   module-valued name by the module's name, which is no type): a type alias (pydantic's
   `CoreSchema`), a `NewType`, and a class of a package that isn't checked or declares no types are
   dropped, about 60 bindings on pydantic. Index each module's aliases (a name annotated
   `TypeAlias`, or bound to a subscript or a union of classes), and take them too. Done when
   `schema: CoreSchema = ...` is a fix there.
4. **ty's spellings.** `(str & ~AlwaysFalsy) | None` is a `str | None`, `Model@create_model` the
   module's type variable `Model`, and `tuple[str, *tuple[str, ...]]` an annotation as it is: each
   is dropped as not one. Done when all three are fixes.
5. **`:=` declared before its statement.** A walrus's name can't be annotated where it's bound: 366
   bindings with no fix. Declare it on a line before the statement, as a chained assignment's names
   are. Done when `if (m := pattern.match(s)) is not None:` declares `m: re.Match[str] | None`.
6. **A union the author would write.** `x if c else None` (241 bindings) is a `T | None`, and
   `a or b` with both sides of one type is that type; 1,986 conditionals and boolean operations have
   no fix. Sides of two other types stay untyped. Done when both are fixes and the corpus packages'
   type checkers find no new error.
7. **Quoted annotations read through.** With `xs: "list[Node]"`, `xs[0]` and `for x in xs` have no
   fix, and `list["Node"]` gives `'Node'`, whose attributes then have none: a quoted part is in 0.1%
   to 6.5% of the annotated corpora's annotations. Read a string annotation as its text. Done when a
   quoted declaration types what an unquoted one does.
8. **A loop target pyrefly hints.** Its hints for a loop's or an unpacking's names carry no edits,
   only each class's defining file in the label's parts: a class the file doesn't bind is dropped
   there. Name the module from that file, as the project index does. Done when
   `for item in registry().values():` declares `item: Shape`.
9. **Faster table generation.** Every build from a checkout generates the tables in one process: the
   Action on every run, a pre-commit hook's install, and each CI job's editable install, about 75s
   here and more on a runner. The twelve configurations it reads the stubs as are independent: read
   them in parallel, or cache the result by its stamp. Done when a build from a checkout generates
   them in under 20s on 4 cores.

### Medium: a few days

1. **`--infer-with` in `corpus_suite.py --types`.** It runs each package's own checker after `--fix`
   and `--fix --unsafe-fixes`, never with hints, whose fixes are checked by hand: basedpyright,
   unconfigured, finds 14 new errors on pydantic and 148 on sqlalchemy after
   `--fix --unsafe-fixes --infer-with basedpyright` (21 and 134 before hints named classes the file
   doesn't bind), most a name bound again to another type (`stmt = insert(...)`, then
   `stmt = stmt.returning(...)`). Run them with `--infer-with` too, trace each new error to its
   hint, and record the counts in RUNS.md. Done when pydantic's, sqlalchemy's and pandas's are
   there.
2. **Decorated functions that declare their return.** A call to one is never typed, since a
   decorator may change what it returns: about 3,200 calls, 2,715 of them to pandas' functions under
   `@set_module("pandas")` (`date_range`, `array`, `period_range`). Trust the declared return where
   the decorator is declared to give back what it takes (`F -> F`, or a factory's
   `Callable[[F], F]`), and for the standard library's that do (`functools.cache`, `lru_cache`,
   `wraps`, `abstractmethod`). Done when `idx = date_range(...)` is a `DatetimeIndex` on pandas,
   with no new type error.
3. **The project's own overloads.** A function the checked files define with `@overload` (pandas'
   `concat`) is skipped as redefined: 1,689 calls. Match its signatures as the standard library's
   and installed packages' are (`constricter.fix.overloads`). Done when a call the arguments decide
   is typed, and one they don't is left alone.
4. **`with` targets.** Only `open(...)`'s is typed: 5,017 bindings with no fix, 2,533 of them a call
   through an import (`zipfile.ZipFile` 188, `socket.socket` 97, `tarfile.open` 67,
   `tempfile.TemporaryDirectory` 63). Type the target by `__enter__`'s return: the tables' for a
   standard-library class (`Self`, or `str` for a `TemporaryDirectory`), a project class's declared
   one, and a `@contextmanager` function's `Iterator[T]`. Done when each of the three is declared
   before its statement, as `open`'s is.
5. **Builtins and operators by their arguments.** `min(n, 3)`, `max(names)`, `sum(d.values())`,
   `abs(n)`, `round(x)`, `next(iter(xs))`, `divmod(n, 2)`, and `enumerate`, `zip`, `map`, `iter` and
   `reversed` bound to a name have no fix with every argument typed (about 2,600 bindings), nor do
   `-n`, `names + names` and `path / "x"`: `builtins.pyi`'s generic functions and the classes'
   operator methods aren't run through the overload matcher. Nor is a loop over anything but a
   builtin container (`path.iterdir()`, `os.walk(...)`, `itertools.combinations(...)`), whose
   element is its `__iter__`'s. Done when each of those is a fix.
6. **Unpacking by element.** `a, b = s.split(",")` (each a `str`), `first, *rest = names` (a `str`
   and a `list[str]`) and `q, r = divmod(n, 2)` (205) have no fix. Done when each name is declared
   before the statement.
7. **Partly vague hints, opt-in.** The largest group of hints dropped is a type with `Any` in it
   (`dict[str, Any]`, `list[Any]`): 16.4% of the three packages' bindings with no fix for
   basedpyright. It is the value's type, and LVA005 would report it: a fix kind of its own, off by
   default, trades an LVA001 for an LVA005. Done when `fix-select` can turn it on.

### Large: a week or more

1. **Class bodies of plain classes.** `--fix` never touches a class body, where an annotation makes
   a dataclass's or a model's variable a field: 15,336 bindings with no fix, 3,070 of them in a
   class with no base and no decorator (1,421 bound to a literal) and 2,456 under a test case's. As
   a guess, annotate a class variable where every base is `object`, a test case, or a checked file's
   class that is itself plain, and never under a metaclass, a decorator, `Enum`, `NamedTuple`,
   `TypedDict`, `Protocol` or an installed package's base. Done when the corpus packages' test
   suites and type checkers find nothing new after `--fix --unsafe-fixes`.
2. **What an unannotated method returns.** 12,578 `self.method()` calls have no fix: the method
   returns a call (3,488), a name or attribute (2,644), a tuple (2,192) or several kinds (1,093), or
   yields (434), and 37% are defined in another class than the caller's. Follow a method to the base
   class that defines it (a guess), type a generator as an `Iterator[T]`, and join `return`s of two
   types into a union. Done when each is a guess on the corpora with no new type error.

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
