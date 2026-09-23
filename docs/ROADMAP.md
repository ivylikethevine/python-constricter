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
  functions that declare their return, in the same module or, in the CLI, another checked file;
  fixed-return builtins and `str`/`bytes` methods; copies, subscripts, attributes (annotated,
  `self.x: T`, `@property` returns) and method calls of a known local, and `cls` in a classmethod as
  `type[C]`; computed values (conditionals, arithmetic on builtin scalars, comprehensions,
  `sorted`/`list`/..., `await`); `typing.cast`; standard-library functions with a builtin result,
  resolved through the imports; `x = None` later rebound to one type as `T | None`; loop targets and
  unpackings as declarations before the statement. A tuple longer than `max-length` is
  `tuple[T, ...]` (found on pip's vendored chardet, whose frequency tables had become
  thousand-element annotations).
- **Guesses** apply only with `--unsafe-fixes` (a capitalised call taken to construct its class,
  LVA008's and LVA010's narrowed annotation, an empty container typed by what's added to it, a
  method typed by its `return`s), and a copy of a guess is one too.
- **Unannotated functions' `return`s** type their calls, a few links of a chain deep in one run;
  **classes from other checked files** type their attributes, properties and methods' calls; and the
  checking that needs to repeat for them re-checks only the functions affected, while the
  cross-module index is read in the worker pool: the standard library checks in 9s where it took
  11.5s before.
- **Fix levels**: every mechanism has a stable id, shown by `--show-fixes` and in JSON;
  `fix-select`, `fix-ignore` and `unsafe-fix-select` choose which apply. Never changes a report.
- **More fixed-return builtins, and methods on literals**: `any`, `hex`, `dir`, `range`, `bytearray`
  and the rest with a fixed result, `str`/`bytes` methods on a literal (`", ".join(parts)`) and
  `partition`; and a builtin's name the module rebinds (a parameter named `format`) is no longer
  taken for the builtin. Not `slice` or `memoryview`, generic in recent typeshed.
- **Loop targets from `enumerate` and `zip`, one part at a time**: `for i, x in enumerate(xs)`
  declares `i: int` whatever `xs` is, each part certain or a guess as its own type is, and the
  keywords that don't change what they yield (`start=`, `strict=`, `sorted`'s `key=`) are allowed.
- **Fixes for LVA003** (the loop's `# type:` comment becomes a declaration) and **LVA007** (the
  repeat's annotation is dropped).
- **Type-checker-backed inference** (`--infer-with basedpyright,ty`): the checkers' language
  servers' inlay hints (asked all at once, over several servers for basedpyright) type what `--fix`
  can't, as guesses, widened (`Literal`), checked (nothing vague, nothing the file can't name) and
  imported (`Callable`, `Path`, ...); `--fix` repeats while the checker's view changes. With
  basedpyright it about doubles what the annotated corpora's `--fix --unsafe-fixes` types (rich: 708
  to 1,441) and still converges in one run.
- **Fixes that add an import**: `open(p, "rb")` is an `io.BufferedReader` by its literal mode (and
  `with open(...) as f` declares `f` first), standard-library classes and what returns them
  (`logging.getLogger()`, `datetime.now()`, `uuid4()`) are typed, and LVA012 offers `Final`. The
  name is spelled through an import the module has, or one added after its leading imports (never
  under `if TYPE_CHECKING:`, over a name the module binds, or over a builtin).
- **Faster checking**: the standard library's check, profiled (`tests/corpus/corpus_profile.py`, in
  CI's Corpus job on every PR), from 227s to 52s over 0.2.4 and after: one shared walk of each
  module, sorted by node type once, for every pass over all of it (`ast.walk` from 130s to about
  20s), generation by generation over each node class's fields worked out once (`_by_type` 9.9s to
  7.2s profiled, 1.6x unprofiled; not the 2x hoped for: the rest is list building); a function's
  calls found by its span, not walked each round; a guess and what it rests on worked out in one
  walk (13.5s to 7.2s); `:=` looked for only in a module with one (3.4s to 0.4s); value flow's types
  taken from `--fix`'s own inference, not worked out twice; functions checked callees first (the
  module's call graph, a cycle in rounds), so `_returned`'s rounds re-check 1.7% of functions (13.3s
  to 2.0s); and each file parsed once, its tree kept from the cross-file index for the check, in the
  same worker (`rules/parsed.py`; up to 40 MB of source, about 1 GB of trees, shared among the
  workers), so `--jobs=0` on 16 cores went from 7.5s to 6.3s. Every corpus's fixes are unchanged.
- **Safe by construction**: it never touches class bodies, keeps line endings and a file's encoding
  (PEP 263 or a BOM; a fix the encoding can't hold leaves the file, exit 2), edits notebooks' cells
  in place, and converges in one pass on every corpus with nothing broken. `requests`', flask's and
  fastapi's own test suites pass identically before and after `--fix --unsafe-fixes` on their
  source.

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
  pass) on the standard library and pinned packages, in CI's Corpus job;
  **`tests/corpus/corpus_table.py`** records each version's results in [RUNS.md](RUNS.md), with
  totals and percentages, and `--label` for a pseudo-version (`0.2.4-rc.N`). (It measured how much
  `--fix` grows each corpus too, until 0.2.4: 0.5% in bytes, 0.2% in lines, about 10 bytes a fix.)
- **`tests/corpus/corpus_suite.py`** clones a corpus package at its pinned tag, installs its test
  dependencies as its CI does, and runs its test suite as released, after `--fix`, and after
  `--fix --unsafe-fixes`: pydantic, sqlalchemy, django and pandas come out identical (see
  [RUNS.md](RUNS.md)), as flask and fastapi did before they left the corpus. `--types` runs each
  one's own type checker the same way and traces each new error to its fix mechanism.
- **Python 3**: `django` (the 5.2 LTS, for 3.11), `sqlalchemy`, `pydantic` (chosen from 18 measured
  by hand; `requests`, `flask`, `fastapi` and `rich` were dropped as small and alike) and `pandas`
  3.0.6 (1,421 files with its tests; overloads, generics, `TYPE_CHECKING` imports; 30,140 fixed,
  nothing broken, one pass).
- **Python 2**: Twisted 12.3.0 (pure Python 2, 147 of 819 files unparsable) and pip 20.3.4 (the most
  type comments in `__future__` modules), hash-pinned sdists `tests/corpus/corpus_sources.py`
  fetches; chosen from 15 measured (`sentry-sdk` 1.45.1's 2/3-era type comments were dropped as
  pip's alike).
- **What `--fix` still can't type** is measured in [NEXT-UP.md](NEXT-UP.md).

### CI, security and releases

- **CI** (`ci.yml`): every check in [CONTRIBUTING](CONTRIBUTING.md#development), the pre-commit
  hook, Markdown, tests on Linux, macOS and Windows × Python 3.11–3.14 plus PyPy 3.11 and
  free-threaded 3.14 (100% branch coverage), the build and a wheel smoke test, the Action, and the
  corpus. The project's own code passes `--level=suffocate --all-scopes` at 100% annotation
  coverage.
- **Security** (`security.yml`, weekly too): CodeQL, zizmor (pedantic), actionlint, pip-audit,
  dependency review, and gitleaks over the whole history; OpenSSF Scorecard; lychee on links.
- **Pinning**: actions by SHA, Python dependencies by hash (`uv.lock`, checked in CI), npm by
  lockfile, uv and actionlint by version; Dependabot updates them weekly.
- **harden-runner** blocks egress to all but the observed hosts in every Linux job, the release jobs
  included; rulesets require every check on `main` and protect `v*` tags.
- **Releases** (`release.yml` on `v*` tags): CI, a reusable build workflow that checks the tag
  matches the version and attests the dists (SLSA Build Level 3), PyPI trusted publishing, and a
  GitHub release. Verify a download with
  `gh attestation verify FILE --repo ivylikethevine/python-constricter --signer-workflow ivylikethevine/python-constricter/.github/workflows/build.yml`.

### Project

- **Python 3.11+**, the oldest still maintained after 3.10's end of life (October 2026): 3.10 would
  add a runtime dependency (`tomli`) for a month, and 3.6–3.9 would mean dropping `match` from the
  checker. Code for any Python 3 version can still be checked.
- **Layout**: a flat `constricter/` in `rules/`, `fix/`, `cli/` and `plugins/`, no module over 750
  lines; docs in `docs/` (changelog, contributing, security, integrations, fixes, runs), release
  notes grouped by `.github/release.yml`, issue and PR templates, CODEOWNERS.

## Next

By scope (smallest first) and, within each, by value. Each item says what it is, why, how, and when
it's done.

### Small: a day or less

Nothing queued.

### Medium: a few days

1. **Make `--fix` add no type errors to the corpora.** `tests/corpus/corpus_suite.py` runs
   pydantic's, sqlalchemy's, django's and pandas's suites, which pass the same after `--fix` and
   `--fix --unsafe-fixes` (see [RUNS.md](RUNS.md)), and with `--types` their own type checkers
   (django has none), tracing each new error to its fix's mechanism: 195 after `--fix` and 260 with
   guesses. Correct the mechanisms, or make their fixes guesses, most first: a first binding's type
   when the name is later bound to another (`None`, the other `cast` of an `if`/`else`: `cast`,
   `literal`, `call`, `method`, `builtin`, `stdlib`, `arithmetic`); a declared `Optional` attribute
   or name copied where it's narrowed (`attribute`, `copy`); a method returning `Self`, or a copy of
   `self`, written as the class (`method`, `copy`), bare where it's generic; an imported `TypeVar`
   left unbound (`call`); a module constant's literal widened to `str` (`literal`, `LVA004`); and an
   element type taken from a subscript with a trailing comma, `list[\n int,\n]`, written as the
   tuple `(int,)` (`loop`). Done when `--types` finds no new error after `--fix` on any corpus.
2. **Standard-library tables generated from typeshed.** `stdlib.RETURNS` and `CLASSES` are curated
   by hand: small, and not always right (`sys.getswitchinterval` was `int`). Generate them from the
   typeshed stubs basedpyright bundles, with a script checked in and its output committed: every
   function whose return names no `TypeVar` and no `Any` and doesn't depend on its overload (1,426
   with a builtin result, 3,928 functions or classes with a standard-library class), spelled by the
   public path the call goes through (`unittest.TestLoader`, not where it's defined), without
   `typing`'s factories (`TypeVar`, `NewType`). Measured: 2,593 more bindings (2,410 certain, mostly
   the standard library's own code), and about 760 of today's constructor guesses become certain
   (`asyncio.Lock()`, `unittest.TestLoader()`). Then, from the same stubs, the methods and
   attributes of those classes on a typed local (`parser.parse_args()`, `dt.astimezone()`): about
   530 more, certain. Left for later: generic classes, `TypeVar` returns (`os.path.dirname`) and
   overloads that differ (`subprocess.run`), which need the arguments' types. Done when the tables
   are generated, the curated ones gone, and every corpus converges with `--types` finding no new
   error they cause.
3. **Methods, attributes and subscripts on any typed receiver.** `_from_local` types `x.m()` only
   when `x` is a local name; `self.index._getitem_slice(...)` and `a.b.c` aren't. Infer the
   receiver's type as any other value's, and look the member up on it. A fixed-return method's
   arguments can't change its type, so `guesses._deciding` should skip them (as it does for `open`
   and `library_class`): 234 of its 629 guesses are guesses only for a call among the arguments.
   Measured: 2,077 bindings (1,448 certain, 384 in annotated code), overlapping the Small item on
   literal receivers. Done when chained receivers are typed, and a fixed-return method's arguments
   don't make its call a guess.

### Large: a week or more

Nothing queued.

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
