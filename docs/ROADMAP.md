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
  comprehensions, `sorted`/`list`/..., `await`); `typing.cast`; `x = None` later rebound to one type
  as `T | None`; loop targets (`enumerate` and `zip` part by part) and unpackings, declared before
  the statement; fixes for LVA003 and LVA007. A tuple longer than `max-length` is `tuple[T, ...]`.
- **The standard library, from typeshed**: tables generated from the stubs basedpyright bundles
  (`tests/typeshed/`, checked in CI), read as Linux, macOS and Windows and Python 3.11 to 3.14 see
  them, into `constricter/fix/tables/` (one JSON file a table, an entry a line; each class's members
  apart from its public ancestors'). Fixed returns, classes and what returns them (`asyncio.Lock()`,
  `logging.getLogger()`), their attributes and methods; and functions and methods whose arguments
  decide their type, by the signature a call matches as a type checker picks among overloads, with
  type variables bound by the arguments (`re.compile("x")` is a `re.Pattern[str]`) and generic
  classes' by the receiver (`pat.match(s)`). A type variable binds to any argument's type where the
  parameter is nothing but it (`copy.copy(obj)`), and to a builtin container's element where it's a
  generic of one (`Iterable[_T]` given `list[str]`), to a scalar's method's return through a generic
  protocol (`math.floor(x)`), and to a function's declared return (`functools.partial(f, x)`);
  generic classes' own attributes are bound by the receiver's (`m.string`). `defaultdict(list)` and
  `Counter()` stay untyped: their parameters come from later use. Generic classes' constructors are
  read from their `__new__` or `__init__` (`collections.deque(names)` is a `collections.deque[str]`,
  `array.array("i")` an `array.array[int]`); at module level, one some Python can't subscript at run
  time is quoted. What only some platforms or versions have is kept (`os.getuid()`).
- **Installed packages**: calls into an installed package that declares its types (`py.typed`, a
  stub package, a lone stub module) are typed by their declared returns as a checked file's are,
  found as the import system would on this Python's path and `VIRTUAL_ENV`'s; types are imported
  from a public module that re-exports them.
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
  what `--fix --unsafe-fixes` types on the annotated corpora.
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
  On every corpus (2026-09-23): 165,019 untyped bindings, 110,480 with no fix at all (111,857 before
  the overload tables and cross-file imports), 72% of those in functions with no annotations. The
  items under [Next](#next) are what reaches the rest. Left alone on purpose: `getattr(...)`, a
  bound method's alias (`append = parts.append`), `dict.get` on a `dict[str, Any]`, `a or b` or a
  conditional whose sides differ (a union, better left to the author), and a `TypeVar`'s own
  declaration.

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
  `tests/typeshed/`; docs in `docs/` (changelog, contributing, security, integrations, fixes, runs),
  release notes grouped by `.github/release.yml`, issue and PR templates, CODEOWNERS.

## Next

By scope (smallest first) and, within each, by value. Each item says what it is, why, how, and when
it's done.

### Medium: a few days

1. **Installed functions' overloads.** Calls into installed packages are typed by declared returns
   alone; their overloads aren't read. On the corpora, 898 untyped numpy calls pass only literals,
   but the commonest (`np.array([1, 2])`) matches an overload returning `NDArray[Any]`, too vague to
   write, and most of the rest need a class argument to bind a type variable
   (`np.empty(n, dtype=np.float64)`: `_DTypeLike[_SCT]` given `np.float64`). Move the stub reading
   in `tests/typeshed/` into the package, read an installed stub's overloads as the tables' are
   (cached with the module), and bind a type variable to a class argument (`type[_SCT]`). Done when
   `np.empty(n, dtype=np.float64)` is an `npt.NDArray[np.float64]` and pandas's `--types` finds no
   new error.

### Large: a week or more

1. **Tables generated at build time.** The standard-library tables could leave git and be generated
   (and compressed) when the package is built, but the pre-commit hooks and the Action install
   straight from a checkout, and `flit_core` has no build hooks: it takes a build backend with one
   (hatchling), the generator out of `tests/`, and typeshed's stubs at build time, pinned with
   basedpyright's. Done when a wheel, an sdist and a git install all carry the same tables, and none
   is tracked.

## Ongoing

- **Restore `reuse lint`** once `reuse` ships a wheel for Python 3.11+ (last checked 2026-09-22:
  6.2.0 still has only a CPython 3.10 one).
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
   `upstream/conda-forge/recipes/python-constricter/`. It builds and passes its tests with
   rattler-build against flit-core 4.0.2, still conda-forge's newest (2026-09-22), while
   `pyproject.toml` asks for `flit_core>=4.1`: either the recipe's host pin or that floor has to
   give until conda-forge has 4.1.
