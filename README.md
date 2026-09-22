# python-con`strict`er

[![CI](https://github.com/ivylikethevine/python-constricter/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/ivylikethevine/python-constricter/actions/workflows/ci.yml)
[![Security](https://github.com/ivylikethevine/python-constricter/actions/workflows/security.yml/badge.svg?branch=main)](https://github.com/ivylikethevine/python-constricter/actions/workflows/security.yml)
[![OpenSSF Scorecard](https://api.scorecard.dev/projects/github.com/ivylikethevine/python-constricter/badge)](https://scorecard.dev/viewer/?uri=github.com/ivylikethevine/python-constricter)
[![Test coverage: 100%](https://img.shields.io/badge/test_coverage-100%25-brightgreen)](pyproject.toml)
[![Annotations: 100%](https://img.shields.io/badge/annotations-100%25-brightgreen)](#annotation-coverage)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue)](LICENSE.md)

> I want **all** of my python code typed.

```text
            /^\/^\
          _|__|  O|
\/     /~     \_/ \
  \____|__________/  \
        \_______      \
                `\     \                 \
                  |     |                  \
                  /      /                    \
                /     /                       \\
              /      /                         \ \
              /     /                            \  \
            /     /             _----_            \   \
          /     /           _-~      ~-_         |   |
          (      (        _-~    _--_    ~-_     _/   |
          \      ~-____-~    _-~    ~-_    ~-_-~    /
            ~-_           _-~          ~-_       _-~
                ~--______-~                ~-___-~
```

[snake](https://www.asciiart.eu/art/595284d82d1f8d6d)

---

Lint rules: every local variable is typed where it's first bound. Ships as a flake8 plugin, a pylint
plugin and a standalone command (for ruff, which loads no plugins).

```python
def total(items: list[int]) -> int:
    count = 0  # LVA001
    result: int = 0  # ok
    first, *rest = items  # LVA001 twice
    head: int
    tail: list[int]
    head, *tail = items  # ok: declared first
    if (n := len(items)) > 3:  # LVA001
        result = n  # ok: rebinding
    for item in items:  # LVA002
        result += item
    for other in items:  # type: int  # LVA003
        result += other
    value: int
    for value in items:  # ok: declared first
        result += value
    return result
```

## Rules

Checked per function body, including methods and nested functions; with `all-scopes`, module and
class bodies too. Statements are read in source order, and only a name's first binding counts.

| Code     | Reports                                                                | Fix                                            |
| -------- | ---------------------------------------------------------------------- | ---------------------------------------------- |
| `LVA001` | `=`, unpacking, `:=` or `with ... as` in a function without annotation | `name: T = ...`, or `name: T` first            |
| `LVA002` | an untyped `for` target or `match` capture                             | `name: T` first (or a type comment)            |
| `LVA003` | a `for` target typed only by `# type: T`                               | `name: T` first                                |
| `LVA004` | with `all-scopes`: the same as `LVA001`, in a module or class body     | `name: T = ...` (`ClassVar[T]` in a dataclass) |
| `LVA005` | an annotation with `Any`, `object` or a generic without its parameters | name the real type                             |
| `LVA006` | an annotation nested `nesting` deep (5 by default)                     | a `type` alias for a part of it                |
| `LVA007` | a name annotated again with the type it already has, in the same block | drop the second annotation                     |

Exempt: comprehensions, `except ... as`, imports, `def`/`class`, `type` aliases, parameters,
`global`/`nonlocal`, and `_`; in module and class bodies, dunder names (`__all__`, `__slots__`) and
enum members (a base imported from `enum`, however it's aliased, or else whose name ends in `Enum`
or `Flag`).

A `# type:` comment (`x = 1  # type: int`, `with f() as x:  # type: T`) counts as an annotation with
`type-comments`, or automatically in a module written to run on Python 2: one that imports
`print_function`, `unicode_literals`, `absolute_import`, `division`, `with_statement`, `generators`
or `nested_scopes` from `__future__`.

`LVA007` compares a block on its own: an `if`'s body and its `orelse`, a `try`'s body and its
`except`s, and the like, are different blocks, since they don't both run in the same pass.

## Levels

Each level makes one more code an error. The rest are warnings: the CLI prints them (as `::warning`
or SARIF `warning` in those formats) but exits 0; flake8 and pylint report errors only.

| Level             | Errors                           | Warnings                              |
| ----------------- | -------------------------------- | ------------------------------------- |
| `relaxed` / `0`   | none                             | `LVA001`–`LVA004`, `LVA007`           |
| `strict` / `1`    | `LVA001`, `LVA004` (the default) | `LVA002`, `LVA003`, `LVA005`–`LVA007` |
| `constrict` / `2` | `LVA001`, `LVA004`, `LVA002`     | `LVA003`, `LVA005`–`LVA007`           |
| `suffocate` / `3` | all                              | none                                  |

`LVA005` and `LVA006` aren't reported at `relaxed`.

Python 3.11+, no runtime dependencies.

## Use

| Tool   | Setup                                                 | Reports                         | Suppress                                         |
| ------ | ----------------------------------------------------- | ------------------------------- | ------------------------------------------------ |
| CLI    | `constricter [PATH...] [--level L] [--format F] [-q]` | `LVA001`–`LVA007`               | `# noqa: LVA001`                                 |
| flake8 | install it (on by default)                            | `LVA001`–`LVA007`               | `# noqa: LVA001`                                 |
| pylint | `load-plugins = ["constricter.pylint_plugin"]`        | `C9101`–`C9107` (symbols below) | `# noqa: LVA001` or `# pylint: disable=<symbol>` |
| ruff   | run the CLI after ruff; set `lint.external = ["LVA"]` | `LVA001`–`LVA007`               | `# noqa: LVA001`                                 |

pylint symbols: `unannotated-local-variable`, `untyped-for-or-match-variable`,
`comment-typed-for-variable`, `unannotated-module-or-class-variable`, `vague-annotation`,
`deeply-nested-annotation`, `redundant-annotation`.

Options:

| Option           | CLI                                                         | `[tool.constricter]` | flake8 (CLI or config)          | pylint                            |
| ---------------- | ----------------------------------------------------------- | -------------------- | ------------------------------- | --------------------------------- |
| level            | `--level`                                                   | `level`              | `--constricter-level`           | `constricter-level`               |
| type comments    | `--type-comments`                                           | `type-comments`      | `--constricter-type-comments`   | `constricter-type-comments = yes` |
| all scopes       | `--all-scopes`                                              | `all-scopes`         | `--constricter-all-scopes`      | `constricter-all-scopes = yes`    |
| nesting          | `--nesting N`                                               | `nesting`            | `--constricter-nesting`         | `constricter-nesting`             |
| fix              | `--fix` (`--unsafe-fixes` for guesses), `--diff` to preview | -                    | -                               | -                                 |
| select           | `--select CODES` (codes or prefixes)                        | `select`             | flake8's own `select`           | pylint's own `enable`             |
| ignore           | `--ignore CODES`                                            | `ignore`             | flake8's own `extend-ignore`    | pylint's own `disable`            |
| exclude          | `--exclude GLOB` (repeatable)                               | `exclude`            | flake8's own `exclude`          | pylint's own `ignore-paths`       |
| format           | `--format`: `text`, `json`, `github`, `sarif`               | -                    | -                               | -                                 |
| statistics       | `--statistics` (counts per code, text format)               | -                    | -                               | -                                 |
| jobs             | `--jobs N` (`-j`; 0: one per CPU)                           | `jobs`               | flake8's own `--jobs`           | pylint's own `--jobs`             |
| baseline         | `--baseline FILE`; `--write-baseline` records it            | `baseline`           | -                               | -                                 |
| coverage         | `--coverage`, `--fail-under PCT`                            | -                    | -                               | -                                 |
| per-path levels  | -                                                           | `per-path-levels`    | -                               | -                                 |
| per-file ignores | -                                                           | `per-file-ignores`   | flake8's own `per-file-ignores` | -                                 |
| stdin            | `-` as the path, `--stdin-filename PATH`                    | -                    | flake8's own `-`                | -                                 |
| exit status      | `--exit-zero`                                               | -                    | flake8's own `--exit-zero`      | pylint's own `--exit-zero`        |
| output file      | `--output-file FILE`                                        | -                    | flake8's own `--output-file`    | pylint's own `--output`           |

`constricter --explain LVA002` prints a code's rationale, its fix, and the levels that report it.

The CLI reads `[tool.constricter]` from the nearest `pyproject.toml` above the current directory;
its flags override it, and `--exclude` adds to it. An unknown key or a bad value exits 2.

```toml
[tool.constricter]
level = "constrict" # or 2
exclude = ["tests/fixtures/*"]
type-comments = false
all-scopes = true
nesting = 5
jobs = 0
baseline = "constricter-baseline.json" # the default; relative to this pyproject.toml

# The first glob a file matches sets its level; other files get `level`.
[tool.constricter.per-path-levels]
"tests/*" = "strict"

# Codes (or prefixes) to drop for files matching a glob.
[tool.constricter.per-file-ignores]
"tests/fixtures/*" = ["LVA005", "LVA006"]
select = ["LVA00"]
ignore = ["LVA003"]
```

`--fix` adds the annotation where the value decides it, for a plain `name = value` in a function or
module body:

- a literal: `count = 0` becomes `count: int = 0`;
- a container whose elements agree: `[1, 2]` gives `list[int]`, `{"a": (1, "b")}` gives
  `dict[str, tuple[int, str]]`;
- a call to a capitalised name (`path = Path(...)` gives `Path`), or to a plain function that
  declares its return type (not a decorated, generic, async or redefined one, and not a return of
  `None`, `Any` or one that uses a `TypeVar`), in the same module or, with the CLI, in another file
  it's checking: `from pkg.util import f`, `import pkg.util as u` then `u.f()`, relative imports and
  re-exports all work, as long as every name in the type already means the same thing in the file.

It never touches class bodies (a dataclass would gain a field) or unpacking, and it leaves what it
can't fix reported. The standard library and third-party packages are out of reach.

### Baselines

To adopt constricter on a codebase that already has offences, record them, then report only new
ones:

```bash
constricter --write-baseline src # writes constricter-baseline.json next to pyproject.toml
constricter src                  # reports only offences the baseline doesn't cover
```

A baseline counts each file's offences by code and variable name, not line number, so it survives
code moving around; another offence for a name it covers is still reported. Paths in it are relative
to it. It's JSON, and like every JSON file constricter reads it may have `//` and `/* */` comments
and trailing commas. `--baseline FILE` or `baseline` in `[tool.constricter]` names another file; the
default one is used only if it exists.

### Annotation coverage

`constricter --coverage src` prints the share of first bindings that are typed, per file and in
total; the bindings are the ones the rules cover (with `--all-scopes`, module and class bodies too),
and `# noqa` doesn't make one typed. `--fail-under PCT` (which implies `--coverage`) exits 1 below
PCT, so CI can hold a codebase to a share. With `--format=json` it prints
`{"typed", "total", "percent", "files"}`, which a badge can read: publish that JSON somewhere (a
gist, a release asset) and point
[shields.io's dynamic JSON badge](https://shields.io/badges/dynamic-json-badge) at it with the query
`$.percent`. This project keeps its own share at 100% in CI, so its badge is static.

### Notebooks

`.ipynb` files are checked too (directories include them): their code cells are read as one module,
IPython-only lines (`%magic`, `!shell`, `obj?`, `%%cell` magics) are skipped, and each offence is
reported at its cell and line (`analysis.ipynb:cell 3:2:5`). JSON output has a `cell` field; GitHub
and SARIF output point at the file and put the cell in the message. `--fix` and `--diff` edit the
cells, keeping the notebook's formatting.

### Adopting it on an existing codebase

1. See the scale: `constricter --statistics src` counts offences per code.
2. Record them: `constricter --write-baseline src`, and commit `constricter-baseline.json`.
3. Enforce it for new code: add the pre-commit hook or the GitHub Action; the baseline keeps old
   offences quiet, and `--diff` / `--fix` clear the easy ones.
4. Burn it down: fix a file or package at a time, then `--write-baseline` again to shrink the file.
5. Tighten: raise `level` (or `per-path-levels` for the parts that are clean), then turn on
   `all-scopes`.

### Output formats

`--format` is `text` (the default), `json`, `github` (workflow annotations), `sarif` (below),
`gitlab` (Code Climate JSON, for GitLab's merge-request Code Quality widget: pass the file as a
`codequality` report artifact), `junit` (a test suite per file, a failed test case per offence, for
Jenkins, Azure Pipelines, CircleCI or GitLab's test reports) or `rdjson` (for
[reviewdog](https://github.com/reviewdog/reviewdog), with each certain fix as a suggestion).
`--output-file FILE` writes the report there, and `--exit-zero` exits 0 even when there are errors
(not when a file can't be read).

### Editors (standard input)

`constricter - --stdin-filename path/to/file.py` checks standard input, reported as that path (which
also picks its per-path level and baseline entry; a `.ipynb` name reads a notebook). With `--fix` it
prints the fixed source instead of a report, and `--diff` diffs it. That's what editors that lint
unsaved buffers through a command need (none-ls, nvim-lint, flycheck, ALE, efm-langserver, Helix).

### SARIF (code scanning)

`--format=sarif` writes SARIF 2.1.0, with each result's level (`error` or `warning`) set by
`--level`. In GitHub Actions, upload it to code scanning (the job needs `security-events: write`):

```yaml
- run: constricter --format=sarif src > constricter.sarif
- if: ${{ !cancelled() }} # upload the findings even when the step above failed on them
  uses: github/codeql-action/upload-sarif@1c5b675653bb5c22dbe9b12b556ec555138e09fd # v4.38.1
  with:
    sarif_file: constricter.sarif
    category: constricter
```

SonarQube and SonarCloud import it with `sonar.sarifReportPaths=constricter.sarif`; any other tool
that reads SARIF 2.1.0 takes the same file.

Tools that run flake8 or pylint (VS Code's extensions, python-lsp-server, prospector, MegaLinter,
Trunk) pick the plugin up once it's installed alongside them.

Without `lint.external`, ruff flags `# noqa: LVA00x` (RUF102) and `--fix` deletes it.

The CLI defaults to `.`, checks `*.py` and `*.ipynb`, and skips hidden dirs, `__pycache__`, `venv`,
`site-packages`, `build`, `dist` and `node_modules` by directory name; `--exclude` adds more
directory names (or globs) to skip the same way, on top of matching whole paths and file names. Exit
codes: `0` no errors, `1` errors, `2` an unreadable or unparsable file, or a bad `pyproject.toml`.

```bash
pip install python-constricter # once the first release is out; until then:
pip install "python-constricter @ git+https://github.com/ivylikethevine/python-constricter@v0.2.0"
```

pre-commit, after ruff's hooks (or `constricter-fix`, which runs `--fix` first):

```yaml
- repo: https://github.com/ivylikethevine/python-constricter
  rev: v0.2.0
  hooks:
    - id: constricter
```

tox and nox, with it in the environment's dependencies:

```ini
# tox.ini
[testenv:types]
deps = python-constricter
commands = constricter --level=constrict src
```

```python
# noxfile.py
@nox.session
def types(session: nox.Session) -> None:
    session.install("python-constricter")
    session.run("constricter", "--level=constrict", "src")
```

GitHub Actions, as PR annotations (it installs from the action's own tag, not PyPI):

```yaml
- uses: ivylikethevine/python-constricter@v0.2.0
  with:
    args: --format=github src tests # the default is `--format=github` on `.`
    python-version: "3.13" # 3.11 or later
```

## Development

With [uv](https://docs.astral.sh/uv/) installed (CI pins 0.12.17):

```bash
export UV_PROJECT_ENVIRONMENT=local/.venv
uv sync --locked --no-install-project --no-build # the dev group: hash-checked wheels from uv.lock
uv pip install --python local/.venv --no-deps --no-build-isolation -e .
```

Checks (as CI runs them): `ruff check .` (every rule, preview included), `ruff format --check .`,
`basedpyright` (all), `mypy` (strict), `pylint src tests` (every extension), `flake8 src tests`,
`typos`, `validate-pyproject pyproject.toml`, `uv lock --check`,
`constricter --level=suffocate --all-scopes src tests`,
`constricter --coverage --all-scopes --fail-under=100 src tests`, `pytest --cov` (100% branch
coverage). Everything generated goes in `local/`. Python is indented with 4 spaces.

After editing the `dev` group, run `uv lock` (CI fails until you do). Dependabot updates `uv.lock`,
the npm lock and the actions weekly.

Fuzzing (`tests/test_fuzz.py`) runs with the tests: hypothesmith generates valid Python, which must
never crash the checker and must stay valid after `--fix`. For a large real codebase, run
`local/.venv/bin/python tests/corpus.py [PATH]` by hand: it checks PATH (default: this Python's
standard library, about 660 files in two seconds) at `suffocate` and prints the time, the offences
per code, and any crash. `local/.venv/bin/python tests/corpus_fix.py [PATH]` runs
`--fix --unsafe-fixes` on a copy of it (in `local/corpus-fix/`) and checks every file still compiles
and a second pass has nothing left to fix (the standard library: about 3,800 fixes, none breaking).

CI also runs the tests on PyPy 3.11 and free-threaded Python 3.14, which install only the `test`
dependency group: every dev tool doesn't have wheels for them, and the tests don't need them all.

Markdown (markdownlint-cli2 and prettier, locked in `.github/package-lock.json`):

```bash
npm ci --prefix .github
git ls-files -z '*.md' | xargs -0 .github/node_modules/.bin/markdownlint-cli2
git ls-files -z '*.md' | xargs -0 .github/node_modules/.bin/prettier --check
```

### Disabled rules

Everything else is on. Some of these may be revisited.

| Tool               | Rule                                                                                                                             | Why                                                                                                                                        |
| ------------------ | -------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| ruff               | `incorrect-blank-line-before-class`, `multi-line-summary-second-line` (D203/D213)                                                | Each contradicts a rule that stays on (D211/D212); one of each pair has to go.                                                             |
| ruff (`tests/`)    | `assert` (S101)                                                                                                                  | pytest works through `assert`.                                                                                                             |
| mypy, basedpyright | astroid's untyped calls and missing stubs                                                                                        | astroid (pylint's parser) ships no type information.                                                                                       |
| typos              | the word `astroid`                                                                                                               | A real package name.                                                                                                                       |
| harden-runner      | `egress-policy: audit` on macOS and Windows, in the release jobs (release.yml, build.yml), and in the weekly external-link check | harden-runner supports only audit on GitHub's macOS and Windows runners; the release jobs haven't run yet; external links can go anywhere. |
| reuse              | `reuse lint` not run (the files still comply: `REUSE.toml` covers them)                                                          | No recent release ships a wheel for Python 3.11+, so installing it builds from source with an unpinned `poetry-core`.                      |
| zizmor             | `self-repository` on the CI job that runs the repository's root action                                                           | zizmor wants `$/`, and actionlint rejects a bare `$/` (it has no path), so that one line uses `./`.                                        |

To apply the rulesets in `.github/rulesets/` (repo admin):

```bash
gh api repos/ivylikethevine/python-constricter/rulesets --method POST --input .github/rulesets/main.json
gh api repos/ivylikethevine/python-constricter/rulesets --method POST --input .github/rulesets/tags.json
```

To publish, add a trusted publisher on PyPI (repository `ivylikethevine/python-constricter`,
workflow `release.yml`, environment `pypi`) and a `pypi` environment in the repo settings, then push
a `v*` tag.

## Roadmap

Done:

- **ci.yml** runs on pushes and PRs: the checks above and the pre-commit hook (Lint), Markdown
  (Docs), pytest on Linux, macOS and Windows × Python 3.11–3.14 (Test), and the sdist and wheel,
  `twine check` and a wheel smoke test (Build).
- **security.yml** runs on pushes, PRs and weekly: CodeQL (Python and Actions), zizmor (pedantic),
  actionlint (kjanat's fork, which reads the `$/` self-repository syntax the workflows use),
  pip-audit on the lock, and dependency review on PRs.
- **scorecard.yml** runs OpenSSF Scorecard on `main` and weekly. Its pin check misreads the `$/`
  references as unpinned actions, so it flags them.
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
- **Suffocate:** `src/` and `tests/` pass at `--level=suffocate --all-scopes` in CI.
- **More checks:** gitleaks over the whole history (Security), lychee on the Markdown links (offline
  in Docs, external ones weekly), validate-pyproject and check-wheel-contents.
- **SARIF docs**, and `--explain`, `--select` / `--ignore`, `--diff` and `--statistics`.
- **Scorecard** blocks all but the hosts it was seen to use.
- **Project files:** a `constricter-fix` pre-commit hook, a CHANGELOG (release notes grouped by
  `.github/release.yml`), badges, issue and PR templates, CODEOWNERS and CONTRIBUTING.
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

Next:

1. **Restore `reuse lint`** once `reuse` ships a wheel for Python 3.11+ (6.2.0 still has only a
   CPython 3.10 one).
2. Revisit the [disabled rules](#disabled-rules) as tools change (last checked 2026-09-22: COM812,
   one-line DOC201/DOC402 and `max-args` came back on; the rest can't go yet).
3. **A second, more complex corpus** as a permanent, pinned CI target: OpenCV's Python bindings
   turned out to be a poor fit (they're mostly thin C bindings, not hand-annotated Python). By hand
   (`tests/corpus.py`/`corpus_fix.py`, `--unsafe-fixes --all-scopes`), against eighteen real
   packages:

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

   No crashes on any of them, and `--unsafe-fixes` left nothing broken or nothing unfixed on a
   second pass, on any of them. Overall auto-fix rate: 12,104 of 94,523 found (12.8%) — `--fix` only
   adds an annotation it can infer unambiguously, so most real-world `LVA001`/`LVA002` (unpacking,
   `for` targets, non-trivial expressions) still need a human; see the next item for ways to raise
   that. `--nesting`'s default (5) never fires on fourteen of the eighteen; `libcst` (deeply nested
   CST types) is by far the most affected, `sqlalchemy` and `scrapy` are the only other two to hit
   it at all at the default. LVA007 found nothing on any of the eighteen, at any nesting — strong
   evidence it isn't noisy. **`requests`** is the strongest permanent-CI candidate: tiny (19 files,
   so a fast check), extremely stable and widely known, Apache-2 licensed, the canonical "makes
   external API calls" library, and (unlike the dev tools) representative of typical, lightly-typed
   real-world code; `click` or `flask` are reasonable alternatives with more decorator/framework
   patterns. Still needs vendoring or a reproducible pinned checkout to become a permanent CI
   target, and a decision on `--nesting`'s default: keep it at 5 (safe, rarely fires) or tighten it
   (3 already reported 124 times on sqlalchemy, 45 on mypy) to make the rule useful more often.

   Validated `requests` specifically: cloned `v2.34.2` (its source checkout, with its own test
   suite, not just the installed wheel), ran `--fix --unsafe-fixes --all-scopes` on `src/requests/`,
   and ran its own test suite before and after. Identical both times: 617 passed, 15 skipped, 1
   xfailed — the inferred types changed nothing about its runtime behaviour. One found a real, if
   inert, mistake in the "guessed" heuristic: `internetSettings = winreg.OpenKey(...)`
   (Windows-only, guarded by `sys.platform == "win32"`, so untested by this run) got annotated
   `internetSettings: winreg.OpenKey = ...` — `winreg.OpenKey` is a _function_, not a class, but its
   PascalCase name (a Windows API convention, not Python's) fools the capitalised-name "constructs a
   class" heuristic (`annotations._constructs`). Worth keeping in mind for whichever package becomes
   the permanent corpus: run its own test suite before/after `--fix`, not just check that it still
   compiles.

4. **Raise `--fix`'s auto-fix rate further.** The easy, safe wins are done (see Done, above); what's
   left needs the bigger lever: `attribute access` (`x = obj.attr`) and `subscripts`
   (`x = container[key]`) still can't be inferred, nor can a method call on an already-typed local
   (`x = some_str.strip()`) — together the largest remaining category in the original breakdown (a
   sample of ~34,500 unfixed `LVA001`s across the standard library, sqlalchemy and django: 68% of
   "calls" were a method call on some other object). `_Scope.types` (a local's known type, added for
   the copying already done) already has the piece these need, but using it here means parsing a
   container type's element out of its own annotation text (`list[int]` → `int` for `container[0]`)
   and deciding how far to trust a mutated or reassigned local; real design work, not a mechanical
   extension. `BinOp` (`a + b`, ~5% of the sample) would need operand types plus knowing the
   operator isn't overloaded to something else — riskier, lower value, likely skip.
5. **LVA008: a type that could narrow.** A warning at `constrict`, an error at `suffocate`: a
   declared type that every value assigned to the name (across its lifetime, not just its first
   binding) is consistent with a strictly narrower one, e.g. a `str` only ever assigned `"0"` or
   `"1"` (could be `bool`), or a `float` only ever incremented, never divided (could be `int`).
   Needs whole-variable value-flow analysis across every reassignment in a scope, not just a first
   binding, which is a different (and much bigger) kind of check than `LVA001`–`LVA007`; wants its
   own design pass (what counts as "consistent with" a type, how far to follow calls and mutation,
   false-positive risk on a codebase this analysis can't fully see) before it's worth building.
6. **LVA009: a reassignment that changes the type.** An error: `count: int = 0` later reassigned
   `count = "done"` in the same scope. A real, common bug class (mypy already treats this as a type
   error by default), but needs the same value-flow machinery as `LVA008` (infer every
   reassignment's type with `annotations.inferred`, not just the first binding's), plus real
   subtyping awareness to avoid noise `LVA008` doesn't have to worry about: a declared `X | None`
   later assigned a plain `X` is normal Optional narrowing, not a bug, so the check needs to know
   that's consistent rather than comparing annotation text like `LVA007` does; a name reused for
   genuinely unrelated purposes (a sentinel, a generic helper handling more than one type by design)
   is a real, if rarer, source of false positives to design around. Depends on `LVA008`'s design
   work (same value-flow pass could likely serve both checks).

After the first release (these need it on PyPI, or a published tag):

1. **Switch the release jobs to `block`** with the hosts the first release run shows (PyPI upload,
   Sigstore, GitHub releases).
2. **A PyPI badge**, and `pip install python-constricter` as the documented install.
3. **The GitHub Action on the Marketplace**, so `uses: ivylikethevine/python-constricter@v1` is
   listed (it already works from any tag).
4. **Trunk and MegaLinter plugin definitions**, submitted upstream.
5. **A conda-forge recipe.**
