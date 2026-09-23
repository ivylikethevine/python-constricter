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
- **Members of any typed value**: `self.index.name`, `t.make().label()`, `rows[0].strip()`, however
  deep, through one lookup (`constricter.fix.members.SOURCES`); a member of a guess is a guess, and
  a call whose type is its callee's alone is certain whatever its arguments.
- **Loop targets from `enumerate` and `zip`, one part at a time**: `for i, x in enumerate(xs)`
  declares `i: int` whatever `xs` is, each part certain or a guess as its own type is, and the
  keywords that don't change what they yield (`start=`, `strict=`, `sorted`'s `key=`) are allowed.
- **Instance attributes typed by their assignments** (`assigned`, a guess): an unannotated attribute
  every one of whose `self.x = value`s in its class's own methods gives one known type (numbers
  widened) types its reads and chains (`self.name.upper()`, `box.name`); stored any other way, bound
  in the class body, or assigned a local bound more than once, it's left alone. 456 more guesses on
  the standard library, where most such values are unannotated parameters or `None` first; the check
  takes about 12% longer (30.3s to 34.0s, `--jobs=1`), left for an optimization pass.
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
- **Standard-library tables generated from typeshed** (`tests/typeshed/stdlib_tables.py`, checked in
  CI): the stubs basedpyright bundles, read as Linux, macOS and Windows and Python 3.11 to 3.14 see
  them (re-exports, `__all__`, overloads, method resolution order), keeping what they all agree on,
  replace the curated tables: 894 functions with a builtin result, 38 `AnyStr` ones, 1,478 classes
  and functions or classmethods returning one (`asyncio.Lock()` is certain, no longer a guess), and
  810 classes' methods' returns and 713's attributes (`dt.astimezone()`, `parser.prog`). On the
  corpora, 6,050 more fixes are certain and 3,708 fewer are guesses. `--types` finds one more error
  than before, on sqlalchemy: `time.fromisoformat(v)`, newly typed, is later rebound to `None`, as
  its `datetime` and `date` siblings already were (Medium 1's first-binding case). Left for later:
  an overload that depends on its arguments (`parser.parse_args()`, `subprocess.run`, `os.listdir`),
  a generic class, a class inside a builtin generic (`list[Path]`), and a function only some
  platforms have (`os.getuid`).
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
- **No new type errors**: `corpus_suite.py --types` runs pydantic's, sqlalchemy's and pandas's own
  type checkers after `--fix`, which found 18, 61 and 117 errors they didn't have as released; now
  none (with guesses: 20, 76 and 165, now 11, 41 and 97). A name bound again later is declared with
  a type every value fits, or left untyped; after a rebinding it's what it was bound to; a read of
  what a checker narrows (a union, or anything the function tests) is a guess, as is an ALL_CAPS
  constant's literal passed to a call; `Self` is written where the method says `Self`; a generic
  class isn't written bare; an imported type variable doesn't type a call; and `list[int,]`'s
  element is `int` (see [FIXES.md](FIXES.md#what-a-type-checker-sees)). About a tenth of the certain
  fixes became guesses (the standard library's 22,073 are 19,825), still offered with
  `--unsafe-fixes`.
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
- **What `--fix` still can't type**, counted by **`tests/corpus/corpus_untyped.py`**
  (`python -m tests.corpus.corpus_untyped`; `--rows` writes every binding as JSON lines): each
  untyped binding, classified by the statement that binds it, the shape of its value, its scope,
  whether its function is annotated, and what a call through an import resolves to and where from.
  On every corpus (2026-09-23, after the typeshed tables, members of any receiver and no new type
  errors): 251,848 untyped bindings, 168,727 with no fix at all, 77% of those in functions with no
  annotations. The items under [Next](#next) are what reaches the rest. Left alone on purpose:
  `getattr(...)` (1,268), a bound method's alias (`append = parts.append`), `dict.get` on a
  `dict[str, Any]`, and `a or b` or a conditional whose sides differ (a union, better left to the
  author).

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
  GitHub release. Verify a download with
  `gh attestation verify FILE --repo ivylikethevine/python-constricter --signer-workflow ivylikethevine/python-constricter/.github/workflows/build.yml`.

### Project

- **Python 3.11+**, the oldest still maintained after 3.10's end of life (October 2026): 3.10 would
  add a runtime dependency (`tomli`) for a month, and 3.6–3.9 would mean dropping `match` from the
  checker. Code for any Python 3 version can still be checked.
- **Layout**: a flat `constricter/` in `rules/`, `fix/`, `cli/` and `plugins/`, no module over 750
  lines (`checker.py`'s statement binding moved to `rules/binding.py`, and `hints.py`'s
  language-server wire format to `cli/protocol.py`, with every corpus's report unchanged); docs in
  `docs/` (changelog, contributing, security, integrations, fixes, runs), release notes grouped by
  `.github/release.yml`, issue and PR templates, CODEOWNERS.

## Next

By scope (smallest first) and, within each, by value. Each item says what it is, why, how, and when
it's done.

### Small: a day or less

Nothing queued.

### Medium: a few days

1. **Unannotated functions' returns across files.** Of the 16,529 calls to an imported name with no
   fix, 10,193 go to the corpus's own package, and 1,567 more `module.func()` calls do: mostly to
   functions another checked file defines without a return annotation. Within a module, `returned`
   already types those from their `return` statements (callees first, a guess for a method); the
   CLI's cross-file index (`project.Index`) carries only declared returns. Put the returned types in
   the index too, worked out callees first across the files' import graph (a cycle in rounds, as
   within a module), with each one's guess and what it rests on, so a call through
   `from pkg.util import f` types as a same-file call does. Done when those calls are typed, the
   standard library's check takes no more than 10% longer, and every corpus converges with no new
   `--types` error.
2. **Standard-library calls decided by their arguments.** 8,672 calls through a standard-library
   module still have no fix (and 6,014 to a name imported from one, mostly the standard library's
   own test helpers): `os.path` (1,516; `os.path.join` alone 1,043, `AnyStr` with arguments whose
   types aren't known), `re` (744: generic `Pattern`/`Match`), `os`, `asyncio`, `tempfile`,
   `struct`, `itertools`, `pickle`. The typeshed tables leave out overloads that differ by argument
   (`subprocess.run`, `parser.parse_args()`, `os.listdir`, `math.floor`), generic classes
   (`re.Pattern[str]`), a class inside a builtin generic (`list[Path]`), and functions only some
   platforms have (`os.getuid`). Pick the overload from the arguments' inferred types (and a
   literal's value, as `open` does), and fill a generic's parameters from them. Done when those are
   generated from the stubs like the rest, and every corpus converges with `--types` finding no new
   error.
3. **Fewer guesses a type checker rejects.** `--fix` adds no type errors now, but
   `--fix --unsafe-fixes` still adds 11 (pydantic), 42 (sqlalchemy) and 97 (pandas), mostly from
   `constructor`, `subscript`, `returned` and `copy` guesses on a name bound again later. And "a
   later value whose type isn't known makes the fix a guess" costs 115–133 certain fixes per corpus:
   typing more of those later values (a call to an unannotated function, a subscript) makes them
   certain again. Correct each mechanism with more than a handful of errors, or stop offering it.
   Done when the unsafe runs' new errors are at most half today's.

### Large: a week or more

1. **Types from installed dependencies.** Calls into third-party packages with no fix: 3,421 through
   a module (`numpy` 2,682, `pytest` 463, `pyarrow` 131) and 322 to a name imported from one
   (`zope`, `pydantic_core`, `typing_extensions`, ...). Most calls through an import stay in the
   corpus's own package (10,193 to an imported name, 1,567 through a module, pandas's own `pd.`
   among them): its unannotated functions, whose `return`s type their calls only in their own
   module. The CLI already indexes the checked files' declared returns and classes
   (`project.Index`); do the same for the installed packages they import, from their inline
   annotations (`py.typed`) or stubs (`*-stubs`, typeshed's third-party stubs), resolved in the
   environment the code runs in (an option naming it, else the active one), cached per package
   version. Done when a declared return in an installed typed package types its calls as a checked
   file's does, and the corpora converge with no new `--types` error.
2. **Unannotated code, from its call sites.** 130,558 of the bindings with no fix (77%) are in
   functions with no annotations: nothing anchors an unannotated parameter's type. `--infer-with`
   reaches some of it through a type checker. Without one, type a parameter from its callers when
   every call in the checked files passes the same known type (a guess: the function is public),
   then everything computed from it. Needs the call graph `returned` builds, across modules. Done
   when it measurably types unannotated code on the standard library and Twisted, as guesses, with
   no new `--types` error.

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
