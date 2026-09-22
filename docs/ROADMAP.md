# Roadmap

## Done

- **ci.yml** runs on pushes and PRs: the checks in [CONTRIBUTING](CONTRIBUTING.md#development) and
  the pre-commit hook (Lint), Markdown (Docs), pytest on Linux, macOS and Windows × Python 3.11–3.14
  (Test), and the sdist and wheel, `twine check` and a wheel smoke test (Build).
- **security.yml** runs on pushes, PRs and weekly: CodeQL (Python and Actions), zizmor (pedantic),
  actionlint, pip-audit on the lock, and dependency review on PRs.
- **scorecard.yml** runs OpenSSF Scorecard on `main` and weekly.
- **release.yml** runs on `v*` tags: CI, then **build.yml** (a reusable workflow) builds the dists,
  checks the tag matches the version, and attests their provenance (SLSA v1 Build Level 3, as the
  build and attestation run in a reusable workflow), then PyPI (trusted publishing), then a GitHub
  release with the dists and the attestation bundle. Verify a download with
  `gh attestation verify FILE --repo ivylikethevine/python-constricter --signer-workflow ivylikethevine/python-constricter/.github/workflows/build.yml`.
- **Pinning:** actions by SHA, Python dependencies by hash (`uv.lock`), npm by lockfile, actionlint
  and uv by version. Dependabot updates all but the last two; `uv lock --check` fails CI on drift.
- **harden-runner** blocks all but the observed hosts in every Linux job that has run.
- **Rulesets:** `.github/rulesets/` requires every check on `main` and protects `v*` tags.
- **Settings** from `[tool.constricter]` in `pyproject.toml`.
- **Python 2 code:** type comments count automatically in modules that import Python 2 `__future__`
  features.
- **All scopes:** `all-scopes` checks module and class bodies (`LVA004`).
- **Suffocate:** `constricter/` and `tests/` pass at `--level=suffocate --all-scopes` in CI.
- **More checks:** gitleaks over the whole history (Security), lychee on the Markdown links (offline
  in Docs, external ones weekly), validate-pyproject and check-wheel-contents.
- **SARIF docs**, and `--explain`, `--select` / `--ignore`, `--diff` and `--statistics`.
- **Scorecard** blocks all but the hosts it was seen to use.
- **Project files:** a `constricter-fix` pre-commit hook, a changelog (`docs/`, release notes
  grouped by `.github/release.yml`), badges, issue and PR templates, CODEOWNERS, and contributing
  and security policies in `docs/`.
- **Per-path levels**, **`--jobs`** for parallel checking, and a **GitHub Action** (`action.yml`)
  that CI runs on the project itself.
- **LVA005, LVA006 and `--fix`.**
- **`--coverage`** (and `--fail-under`) for annotation coverage, with test- and annotation-coverage
  badges this project's CI keeps true.
- **Baselines**, a **smarter `--fix`** (containers, same-module return types), **notebooks**, and
  JSON with comments and trailing commas wherever constricter reads JSON.
- **Fuzzing**, a **corpus run** (`tests/corpus.py`), an **adoption guide**, **`--fix` for
  notebooks**, and **SLSA Build Level 3 provenance** (GitHub's artifact attestations, from a
  reusable build workflow) on each release.
- **Python 3.11+**, the oldest version still maintained after 3.10's end of life in October 2026.
  Older Pythons aren't planned: 3.10 would add a runtime dependency (`tomli`) for a month, and
  3.6–3.9 would mean dropping `match` from the checker and keeping a second CI setup with older
  tools. Code written for any Python 3 version can still be checked.
- **harden-runner** blocks all but the observed hosts in every Linux job that has run, the Linux
  Test jobs and Scorecard included.
- **Stdin**, **`gitlab`, `junit` and `rdjson` output**, **safe and `--unsafe-fixes`**, **per-file
  ignores**, **`--exit-zero`** and **`--output-file`**, **tox and nox** snippets, **PyPy 3.11 and
  free-threaded 3.14** in CI, and a **`--fix` corpus run** (`tests/corpus_fix.py`).
- **Cross-module `--fix`** in the CLI (the flake8 and pylint plugins see one file at a time).
- **CI's Corpus job** runs `tests/corpus.py` and `tests/corpus_fix.py` against the runner's Python
  standard library on every push and PR.
- **`project.Index`** sorts modules by name so `calls` finds a module/submodule import by prefix
  (`bisect`) instead of scanning every indexed module.
- **Enum bases and factory calls resolve by import origin** (`annotations.factories`,
  `checker._is_enum`'s `imported_from` check), so an aliased or re-exported `Enum`/`NamedTuple`/...
  is still recognised; the bare-name lists remain a fallback for one imported some other way.
- **A general path-exclusion mechanism**: `--exclude` globs also match a directory name during a
  directory walk, folding the built-in skip list (`__pycache__`, `node_modules`, hidden dirs, ...)
  into the same mechanism instead of a separate hardcoded check.
- **`_FileRun` split** into `_CheckRun`, `_BaselineRun` and `_CoverageRun` (one per mode-group,
  instead of one struct with fields only some modes populate), and `_check_path` and
  `_baseline_path` share a `_read_checked` read-and-report-errors wrapper.
- **LVA007: duplicate/redundant typing.** A name annotated again with the type it already has, in
  the same straight-line block; a warning at every level, an error at `suffocate`.
- **`--fix` infers more**: `not x` (always a real `bool`, unlike a comparison, which sqlalchemy's
  own corpus data proves isn't safe to assume — it overloads `<`/`==` to build query expressions); a
  table of builtins with a fixed, un-overloadable return type (`len`→`int`,
  `isinstance`/`hasattr`/`callable`/`issubclass`→`bool`, `str`/`repr`/`chr`→`str`, `int`/`float`
  →themselves, ...); and copying an already-known local's type for a plain `x = y` (from its own
  annotation, an earlier fix in the same scope, or an annotated parameter) — a guessed source's type
  copies too, marked just as guessed, so a chain of copies still converges in one `--fix` pass
  instead of needing a second. Verified on the eighteen-codebase corpus below: fixed rose from
  12,104 to 13,608 of the same 94,523 found (12.8% → 14.4%), no crashes, nothing left to fix on a
  second pass anywhere, and `requests`' own test suite (not just its compile check) passed
  identically — 617 passed, 15 skipped, 1 xfailed — before and after `--fix --unsafe-fixes` on its
  source.
- **`--fix` infers subscripts and attributes** of an already-typed local: `container[key]` (its
  element type from a `list`, `dict` or homogeneous `tuple[T, ...]`; the same `list`/`str`/`bytes`
  type back for a slice; nothing for a fixed-length heterogeneous tuple, since the element varies
  with the index) and `obj.attr` (a class-level annotated attribute of a class defined in the same
  module — not one only assigned in `__init__`, which would need dataflow across methods to see).
  Both build on `_Scope.types`, so a guessed source's uncertainty carries through automatically, the
  same as a plain copy. Re-verified on the corpus: no crashes, still converges in one `--fix` pass,
  `requests`' test suite still passes identically, and fixed rose further (e.g. standard library
  4,431 → 4,450, mypy 1,939 → 1,996, django 2,408 → 2,414, sqlalchemy 830 → 848, pydantic 434 →
  447).
- **A permanent, pinned corpus.** By hand (`tests/corpus.py`/`corpus_fix.py`,
  `--unsafe-fixes --all-scopes`), against eighteen real packages, to choose it — OpenCV's Python
  bindings (the original idea) turned out to be a poor fit, since they're mostly thin C bindings,
  not hand-annotated Python:

  | Codebase         | Version | Files | Left un-typed |      Fixed | LVA006 @5 | LVA007 |
  | ---------------- | ------- | ----: | ------------: | ---------: | --------: | -----: |
  | standard library | 3.11.16 |   732 |        24,173 |      3,828 |         0 |      0 |
  | mypy             | 2.3.1   |   195 |         9,853 |      1,777 |         0 |      0 |
  | pylint           | 4.0.8   |   178 |         3,609 |        486 |         0 |      0 |
  | libcst           | 1.9.0   |   297 |         3,407 |      1,042 |       201 |      0 |
  | uiautomator2     | 3.7.0   |    32 |           888 |         86 |         0 |      0 |
  | requests         | 2.34.2  |    19 |           372 |         45 |         0 |      0 |
  | flask            | 3.1.3   |    24 |           410 |         29 |         0 |      0 |
  | click            | 8.5.0   |    17 |           567 |         86 |         0 |      0 |
  | praw             | 8.0.3   |    89 |           602 |        114 |         0 |      0 |
  | boto3            | 1.43.99 |    39 |           483 |         93 |         0 |      0 |
  | django           | 6.1.1   |   907 |        15,648 |      2,248 |         0 |      0 |
  | pydantic         | 2.13.5  |   105 |         2,998 |        367 |         0 |      0 |
  | attrs            | 26.1.0  |    13 |           336 |         60 |         0 |      0 |
  | aiohttp          | 3.14.3  |    55 |         1,590 |        217 |         0 |      0 |
  | paramiko         | 5.0.0   |    41 |         1,272 |        241 |         0 |      0 |
  | scrapy           | 2.19.0  |   179 |         1,814 |        389 |         1 |      0 |
  | sqlalchemy       | 2.0.54  |   257 |        12,556 |        643 |         7 |      0 |
  | rich             | 15.0.0  |   100 |         1,841 |        353 |         0 |      0 |
  | **Total**        |         |       |    **82,419** | **12,104** |           |        |

  No crashes on any of them, and `--unsafe-fixes` left nothing broken or nothing unfixed on a second
  pass, on any of them; `--nesting`'s default then (5) never fires on fourteen of the eighteen, and
  LVA007 found nothing on any of them, at any nesting — strong evidence it isn't noisy
  (`--nesting`'s default is still worth revisiting some day: `libcst`, deeply nested CST types, is
  by far the most affected, `sqlalchemy` and `scrapy` are the only other two to hit it at all at the
  default, and 3 already reported 124 times on sqlalchemy, 45 on mypy). Chose four to run
  permanently in CI (see the Corpus job): **`requests`** (tiny, so a fast check; extremely stable
  and widely known; the canonical "makes external API calls" library; unlike the dev tools,
  representative of typical, lightly-typed real-world code), **`flask`** and **`django`** (two web
  frameworks, more decorator/class-heavy than `requests`; `django` pinned to the 5.2 LTS, since 6.x
  needs Python 3.12+) and **`sqlalchemy`** (an ORM, and the corpus most likely to exercise
  `LVA006`). Each runs as its own Corpus (`package`) matrix job, from a new `corpus` dependency
  group.

  Also validated `requests` specifically: cloned `v2.34.2` (its source checkout, with its own test
  suite, not just the installed wheel), ran `--fix --unsafe-fixes --all-scopes` on `src/requests/`,
  and ran its own test suite before and after. Identical both times: 617 passed, 15 skipped, 1
  xfailed — the inferred types changed nothing about its runtime behaviour. One found a real, if
  inert, mistake in the "guessed" heuristic: `internetSettings = winreg.OpenKey(...)` (Windows-only,
  guarded by `sys.platform == "win32"`, so untested by this run) got annotated
  `internetSettings: winreg.OpenKey = ...` — `winreg.OpenKey` is a _function_, not a class, but its
  PascalCase name (a Windows API convention, not Python's) fools the capitalised-name "constructs a
  class" heuristic (`annotations._constructs`).

- **`--fix` infers `self.attr` and `str`/`bytes` method calls.** `classes` (used for `obj.attr`) now
  also collects `self.x: T = ...` from anywhere in a method's body, not just class-level
  annotations; a method whose first parameter is literally named `self` has it typed as its class
  (`_owners`, by the method's `id()`, not by name — a same-named method on an unrelated class isn't
  confused with it), so `self.attr` resolves the same way `obj.attr` already did. Separately, a
  fixed table of `str`/`bytes` methods whose return type doesn't depend on their arguments (`strip`,
  `split`, `startswith`, `encode`, `decode`, ...) makes `some_str.strip()` on an already-typed local
  as certain as a builtin function call — not a guess, unlike an arbitrary method call, which stays
  guessed. Re-verified on the corpus: no crashes, still converges in one `--fix` pass on all six
  re-checked (standard library, mypy, `requests`, `flask`, `django`, `sqlalchemy`), and fixed rose
  further still (e.g. mypy 1,996 → 2,074, sqlalchemy 848 → 1,039, `requests` 52 → 57).

- **`--fix` infers method calls** on an already-typed local, as certain fixes: a method of a class
  defined in the same module (`method_returns`, the same rules as a module function's: plain, not
  decorated or redefined, not `None`, vague or a `TypeVar`, and never on a generic class; a bare
  `Self` return is the class itself), and `list`/`set`/`dict` methods whose return is the receiver's
  own element type (`copy`, `pop`, `setdefault`, `get` as `V | None`, `popitem`; any other argument
  shape, like `pop(key, default)` or a keyword, decides nothing). `BinOp` (`a + b`) stays skipped:
  it needs both operands' types and proof the operator isn't overloaded, for little gain.
  Re-verified with `tests/corpus_fix.py` on Python 3.14's standard library and the four pinned
  corpus packages: no crashes, nothing stops compiling, still converges in one pass, and fixed rose
  on four of the five (standard library 23,575 → 23,645, sqlalchemy 1,039 → 1,123, flask 35 → 44,
  `requests` 57 → 66; django unchanged at 2,324).

- **Release jobs block egress**: the build, PyPI and GitHub release jobs run harden-runner in
  `block` with the hosts the v0.2.2 and v0.2.3 release runs used.
- **On PyPI**: `pip install python-constricter` is the documented install, with PyPI version and
  Python version badges (the classifiers now name 3.11–3.14, CPython and PyPy).

- **LVA009: a value that doesn't fit the annotation**, over the name's whole lifetime in the scope
  (see [Rules](../README.md#rules)): a warning, an error from `constrict`, pylint's `C9109`
  (`mismatched-value-type`). Built on the value-flow engine (`constricter.rules.flow`); across
  Python 3.14's standard library and the four corpus packages it finds 10, each a real mismatch.

- **LVA008: an annotation that could narrow**, and **LVA010: a union member no value uses** (see
  [Rules](../README.md#rules)): reported from `constrict`, errors at `suffocate`; pylint's `C9108`
  (`narrowable-annotation`) and `C9110` (`unused-union-member`). Claimed only for a function's own
  names with every value known: measured on instadroid's app (47 files), their first two findings
  were module-level settings rebound elsewhere (a documented `None` default, a
  `globals().update(...)`), which is why module and class variables are left out; on the corpus, as
  expected of code this full of imported types, they find nothing.

- **`--show-fixes`**: each `--fix` annotation with how its value decided it (a literal, a copy of a
  local, a function's declared return type, a guessed constructor, ...), after the report; JSON
  output carries the same `fix` object on every result.
- **A user-defined type hierarchy** for LVA008–LVA010: `[tool.constricter.narrower]` (and the
  plugins' `narrower` option), overriding the defaults and the module's classes per type, and making
  the types it names comparable.
- **LVA011: a fixed-length tuple longer than `max-length`** (4 by default, measured: across the
  corpus, variable annotations list 2 types 140 times, 3 and 4 about 20 times each, and 5 or more 3
  times). Reported from `strict`, an error at `suffocate`; pylint's `C9111`.
- **Reorganised**: a flat `constricter/` (no `src/`) in `rules/`, `fix/`, `cli/` and `plugins/`,
  with no module over 750 lines; `docs/` holds the changelog and contributing and security policies.

- **Editor setup, install notes, `--format=full` and corpus runs**: settings for VS Code, Zed and
  Neovim in `docs/editors/`; `uvx`/`pipx`, Bazel and Pants notes; `--format=full`, each offence with
  its source line and a caret under the name; and `tests/corpus_table.py`, recording each version's
  results on the corpus in `docs/RUNS.md`.

- **`--fix` does more**: declarations before a loop (LVA002) or an unpacking; computed values
  (conditionals, arithmetic on builtin scalars, comprehensions, `sorted`/`list`/`set`/`tuple` of
  known elements, `await`); and, with `--unsafe-fixes`, LVA008's and LVA010's narrowed annotation.
  On the corpus, with nothing broken and still one pass: the standard library 23,645 → 28,393 fixed,
  django 2,324 → 2,648, sqlalchemy 1,123 → 1,409, flask 44 → 67, `requests` 66 → 79.

- **pre-commit fixes**: `constricter-fix` runs as one process (`require_serial`), so its
  cross-module `--fix` sees every file pre-commit passes it (a split run misses what one run fixes:
  `tests/test_project.py`), and a pre-commit.ci snippet.
- **SARIF `helpUri`, help text and `fixes`**: each certain fix is a SARIF fix (an insertion,
  declaration or rewrite), columns count characters (`columnKind`), and the output validates against
  SchemaStore's SARIF 2.1.0 schema in the tests (fetched at a pinned commit and SHA-256 into
  `local/`, not distributed). The same text edits fix rdjson's suggestion for a loop target or
  unpacking, which was `for x: T in ...`.
- **GitHub Action**: a `version` input (a PyPI release, installed with uv), a per-code summary table
  on the run page (`summary`), and a `sarif-file` output; CI's Action job uses each.
- **fastapi, pydantic and rich in the pinned corpus** (the `corpus` group and CI's Corpus matrix):
  architectures the first four lack — dependency injection and annotations as runtime behaviour
  (fastapi 0.141.1), a validation library whose own models are annotated classes over a compiled
  core (pydantic 2.13.5), and many small composed renderables and protocols (rich 15.0.0). On each:
  no crashes, nothing broken by `--fix --unsafe-fixes`, one pass (fixed: fastapi 141, pydantic 695,
  rich 625). Their own test suites weren't run before and after `--fix`, as `requests`' was.
  `tests/corpus_table.py --label` records this checkout under a pseudo-version (`0.2.4-rc.1` in
  `docs/RUNS.md`).
- **Python 2 corpora**: `sentry-sdk` 1.45.1 (2/3-era code: 547 `# type:` lines in modules with a
  Python 2 `__future__` import, the type-comment path) in the `corpus` group, and Twisted 12.3.0
  (pure Python 2: 147 of its 819 files don't parse under Python 3 — print and `exec` statements,
  tuple parameters, `raise E, msg`, `0777`, `10L`), a hash-pinned sdist `tests/corpus_sources.py`
  fetches, since it can't be installed on Python 3. Both are in CI's Corpus matrix: unparsable files
  reported, never a crash, nothing broken by `--fix`, one pass. Chosen from 15 measured candidates
  (CPython 2.7's `Lib/`, pip 20.3, Mercurial, ansible, Trac, hypothesis 4, ...).
- **Fix levels**: each `--fix` mechanism has a stable id (`literal`, `copy`, `constructor`, ...,
  seventeen in all; see `docs/FIXES.md`), covering every part a fix was built from, shown by
  `--show-fixes` and in JSON. `fix-select` and `fix-ignore` choose which fixes are offered;
  `unsafe-fix-select` trusts a guessing mechanism (`constructor`, `narrow`), and a copy of a trusted
  guess with it. The rules' own value flow never sees the policy, so it changes no report, and the
  defaults fix exactly what they did (the standard library: 28,395 before and after).
- **LVA012, opt-in**: a local bound once, by a plain assignment outside any loop (a loop's body
  rebinds it each pass, and type checkers reject `Final` there), and never rebound could be `Final`.
  Reported only when selected by its full code (the CLI's new `--extend-select`, flake8's
  `extend-select`, pylint's `could-be-final`), an error only at `suffocate`, with no `--fix` (it
  would have to import `Final`). Measured as the roadmap asked, it fits 45–70% of every corpus's
  first bindings (the standard library 54%, django 45%, sqlalchemy 52%, Twisted 71%, this repository
  47%), which settles it: opt-in, nothing more.
- **Every entry point takes bytes**: `annotation_coverage` accepts `str | bytes`, as `check_source`
  and `value_flow` do, and each reads the source's lines as text (`jsonc.as_text`); given bytes it
  used to crash on a `match` with a `**rest` capture. `value_flow` now gets those lines too, so it
  places a `**rest` capture at its name, as `check_source` does.
- **The README split up**: `docs/INTEGRATIONS.md` (pre-commit, CI and build tools), `docs/FIXES.md`
  (what `--fix` infers), this roadmap, and the development notes and disabled rules in
  `docs/CONTRIBUTING.md`; the README links them by absolute URL, so they work on PyPI too.
- **Non-UTF-8 source**: a module is read in its PEP 263 declaration's encoding (or a BOM's), and
  `--fix` writes it back in the same one, or leaves the file as it was, exit 2, when an annotation
  can't be written in it. Such files are rare: 3 of the standard library's 2,273 (all in its own
  tests), none in the four corpus packages; the standard library's `--fix` corpus run now covers
  them (1,867 files, 28,395 fixed, nothing broken, one pass).

## Next

By scope (smallest first) and, within each, by value. Each item says what it is, why, how, and when
it's done.

### Small: a day or less

Nothing queued.

### Medium: a few days

Nothing queued.

### Large: a week or more

1. **Type-checker-backed inference**, opt-in (`--infer-with=ty|basedpyright`): start that checker's
   language server, ask for the inlay hints over each file, and turn a hint on an unannotated first
   binding into a fix, always a guess (`--unsafe-fixes`), since a hint can be too wide, a `Literal`,
   or name something the file doesn't import.

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
