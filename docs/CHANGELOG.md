# Changelog

Notable changes, newest first. Each release's full notes are generated from its merged pull requests
(grouped by `.github/release.yml`) on its
[GitHub release](https://github.com/ivylikethevine/python-constricter/releases).

## Unreleased

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
