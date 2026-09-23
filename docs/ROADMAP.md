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
  LVA008's and LVA010's narrowed annotation), and a copy of a guess is one too.
- **Fix levels**: every mechanism has a stable id, shown by `--show-fixes` and in JSON;
  `fix-select`, `fix-ignore` and `unsafe-fix-select` choose which apply. Never changes a report.
- **Fixes for LVA003** (the loop's `# type:` comment becomes a declaration) and **LVA007** (the
  repeat's annotation is dropped).
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
  totals and percentages, how much `--fix` grows each corpus (0.4% in bytes and 0.2% in lines, about
  9 bytes per fix; 0.9% with guesses), and `--label` for a pseudo-version (`0.2.4-rc.N`).
- **`tests/corpus/corpus_suite.py`** clones a corpus package at its pinned tag, installs its locked
  test dependencies, and runs its test suite as released, after `--fix`, and after
  `--fix --unsafe-fixes`; flask (490 tests) and fastapi (3,341) come out identical.
- **Python 3**: `requests`, `flask`, `django` (the 5.2 LTS, for 3.11), `sqlalchemy`, `fastapi`,
  `pydantic`, `rich` (chosen from 18 measured by hand) and `pandas` 3.0.6 (1,421 files with its
  tests; overloads, generics, `TYPE_CHECKING` imports; 30,140 fixed, nothing broken, one pass).
- **Python 2**: `sentry-sdk` 1.45.1 (2/3-era `# type:` comments, installed), and Twisted 12.3.0
  (pure Python 2, 147 of 819 files unparsable) and pip 20.3.4 (the most type comments in
  `__future__` modules), hash-pinned sdists `tests/corpus/corpus_sources.py` fetches; chosen from 15
  measured.
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

1. **† Classes from other checked modules.** `project.Index` holds only functions; add each class's
   annotated attributes, `@property` returns, and methods' and classmethods' declared returns, and
   resolve a receiver typed as an imported class through them, under the name rules `project.calls`
   follows. Up to ~900 bindings in the annotated corpora (`param.method()`, `local.x`,
   `Table.grid(...)`), the largest gain found. Done when a class's attribute, property, method and
   classmethod type their uses from another checked file, the same way they do in their own.
2. **† Fixes that add an import.** Many inferred types need a name the file doesn't import:
   `with open(p, "rb") as f` is an `io.BufferedReader` (938 `open` calls), `logging.getLogger()` a
   `logging.Logger`, and LVA012's fix would be `Final`. Add or extend an import safely (after
   `from __future__`, not inside `TYPE_CHECKING`, never over a name already taken), then type
   `open()` by its literal mode and give LVA012 a fix. Done when those fixes add a correct import
   and a second `--fix` pass is a no-op.
3. **† Empty containers filled later**: `x = []` then only `x.append(v)` in the same scope, every
   `v` typed and agreeing, gives `list[T]` (`{}` with `x[k] = v`, `set()` with `.add(v)`), a guess,
   since other code may add to it. At least 558 on the corpus. Done when those are guessed and a
   container passed elsewhere, extended or filled with differing types is left alone.
4. **† Return types of unannotated functions**, from their `return` statements when every one is
   typed and they agree and the function can't fall off its end: certain for a module function, a
   guess for a method (a subclass may override it). Needs the callee's scope checked before its
   callers'. At least 656 calls on the corpus, mostly in unannotated code. Done when such a call is
   typed and a function with a bare `return`, a fall-through or a `yield` isn't.
5. **Run the remaining corpora's test suites, and their type checkers, after `--fix`.**
   `tests/corpus/corpus_suite.py` runs flask's and fastapi's suites (and `requests`' was run by
   hand) before and after `--fix` and `--fix --unsafe-fixes`, identically. Add pydantic, rich,
   sqlalchemy, django and pandas (whose 27% guesses make it the most telling). A local's annotation
   is never evaluated at runtime, so a test suite catches a fix that breaks the code, not a wrong
   type: also run each project's own type checker (mypy or pyright, as its CI does) before and
   after, and count the new errors per fix mechanism. Done when every Python 3 corpus's suite passes
   the same, and each new type error is traced to a mechanism and that mechanism corrected or made a
   guess.

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
