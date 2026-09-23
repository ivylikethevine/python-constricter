# Changelog

Notable changes, newest first. Each release's full notes are generated from its merged pull requests
(grouped by `.github/release.yml`) on its
[GitHub release](https://github.com/ivylikethevine/python-constricter/releases).

## Unreleased

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
