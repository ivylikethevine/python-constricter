# `python-constricter`

[![CI](https://github.com/ivylikethevine/python-constricter/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/ivylikethevine/python-constricter/actions/workflows/ci.yml)
[![Security](https://github.com/ivylikethevine/python-constricter/actions/workflows/security.yml/badge.svg?branch=main)](https://github.com/ivylikethevine/python-constricter/actions/workflows/security.yml)
[![OpenSSF Scorecard](https://api.scorecard.dev/projects/github.com/ivylikethevine/python-constricter/badge)](https://scorecard.dev/viewer/?uri=github.com/ivylikethevine/python-constricter)
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

Source: <https://www.asciiart.eu/art/595284d82d1f8d6d>

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

Exempt: comprehensions, `except ... as`, imports, `def`/`class`, `type` aliases, parameters,
`global`/`nonlocal`, and `_`; in module and class bodies, dunder names (`__all__`, `__slots__`) and
enum members (a class whose base's name ends in `Enum` or `Flag`).

A `# type:` comment (`x = 1  # type: int`, `with f() as x:  # type: T`) counts as an annotation with
`type-comments`, or automatically in a module written to run on Python 2: one that imports
`print_function`, `unicode_literals`, `absolute_import`, `division`, `with_statement`, `generators`
or `nested_scopes` from `__future__`.

## Levels

Each level makes one more code an error. The rest are warnings: the CLI prints them (as `::warning`
or SARIF `warning` in those formats) but exits 0; flake8 and pylint report errors only.

| Level             | Errors                           | Warnings                               |
| ----------------- | -------------------------------- | -------------------------------------- |
| `relaxed` / `0`   | none                             | `LVA001`–`LVA004`                      |
| `strict` / `1`    | `LVA001`, `LVA004` (the default) | `LVA002`, `LVA003`, `LVA005`, `LVA006` |
| `constrict` / `2` | `LVA001`, `LVA004`, `LVA002`     | `LVA003`, `LVA005`, `LVA006`           |
| `suffocate` / `3` | all                              | none                                   |

`LVA005` and `LVA006` aren't reported at `relaxed`.

Python 3.11+, no runtime dependencies.

## Use

| Tool   | Setup                                                 | Reports                         | Suppress                                         |
| ------ | ----------------------------------------------------- | ------------------------------- | ------------------------------------------------ |
| CLI    | `constricter [PATH...] [--level L] [--format F] [-q]` | `LVA001`–`LVA006`               | `# noqa: LVA001`                                 |
| flake8 | install it (on by default)                            | `LVA001`–`LVA006`               | `# noqa: LVA001`                                 |
| pylint | `load-plugins = ["constricter.pylint_plugin"]`        | `C9101`–`C9106` (symbols below) | `# noqa: LVA001` or `# pylint: disable=<symbol>` |
| ruff   | run the CLI after ruff; set `lint.external = ["LVA"]` | `LVA001`–`LVA006`               | `# noqa: LVA001`                                 |

pylint symbols: `unannotated-local-variable`, `untyped-for-or-match-variable`,
`comment-typed-for-variable`, `unannotated-module-or-class-variable`, `vague-annotation`,
`deeply-nested-annotation`.

Options:

| Option          | CLI                                              | `[tool.constricter]` | flake8 (CLI or config)        | pylint                            |
| --------------- | ------------------------------------------------ | -------------------- | ----------------------------- | --------------------------------- |
| level           | `--level`                                        | `level`              | `--constricter-level`         | `constricter-level`               |
| type comments   | `--type-comments`                                | `type-comments`      | `--constricter-type-comments` | `constricter-type-comments = yes` |
| all scopes      | `--all-scopes`                                   | `all-scopes`         | `--constricter-all-scopes`    | `constricter-all-scopes = yes`    |
| nesting         | `--nesting N`                                    | `nesting`            | `--constricter-nesting`       | `constricter-nesting`             |
| fix             | `--fix`, or `--diff` to preview                  | -                    | -                             | -                                 |
| select          | `--select CODES` (codes or prefixes)             | `select`             | flake8's own `select`         | pylint's own `enable`             |
| ignore          | `--ignore CODES`                                 | `ignore`             | flake8's own `extend-ignore`  | pylint's own `disable`            |
| exclude         | `--exclude GLOB` (repeatable)                    | `exclude`            | flake8's own `exclude`        | pylint's own `ignore-paths`       |
| format          | `--format`: `text`, `json`, `github`, `sarif`    | -                    | -                             | -                                 |
| statistics      | `--statistics` (counts per code, text format)    | -                    | -                             | -                                 |
| jobs            | `--jobs N` (`-j`; 0: one per CPU)                | `jobs`               | flake8's own `--jobs`         | pylint's own `--jobs`             |
| baseline        | `--baseline FILE`; `--write-baseline` records it | `baseline`           | -                             | -                                 |
| per-path levels | -                                                | `per-path-levels`    | -                             | -                                 |

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
select = ["LVA00"]
ignore = ["LVA003"]
```

`--fix` adds the annotation where the value decides it, for a plain `name = value` in a function or
module body:

- a literal: `count = 0` becomes `count: int = 0`;
- a container whose elements agree: `[1, 2]` gives `list[int]`, `{"a": (1, "b")}` gives
  `dict[str, tuple[int, str]]`;
- a call to a capitalised name (`path = Path(...)` gives `Path`), or to a plain function in the same
  module that declares its return type (not a decorated, generic, async or redefined one, and not a
  return of `None`, `Any` or one that uses a `TypeVar`).

It never touches class bodies (a dataclass would gain a field), unpacking or notebooks, and it
leaves what it can't fix reported.

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
`site-packages`, `build`, `dist` and `node_modules`. Exit codes: `0` no errors, `1` errors, `2` an
unreadable or unparsable file, or a bad `pyproject.toml`.

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
`constricter --level=suffocate --all-scopes src tests`, `pytest --cov` (100% branch coverage).
Everything generated goes in `local/`. Python is indented with 2 spaces.

After editing the `dev` group, run `uv lock` (CI fails until you do). Dependabot updates `uv.lock`,
the npm lock and the actions weekly.

Fuzzing (`tests/test_fuzz.py`) runs with the tests: hypothesmith generates valid Python, which must
never crash the checker and must stay valid after `--fix`. For a large real codebase, run
`local/.venv/bin/python tests/corpus.py [PATH]` by hand: it checks PATH (default: this Python's
standard library, about 660 files in two seconds) at `suffocate` and prints the time, the offences
per code, and any crash.

Markdown (markdownlint-cli2 and prettier, locked in `.github/package-lock.json`):

```bash
npm ci --prefix .github
git ls-files -z '*.md' | xargs -0 .github/node_modules/.bin/markdownlint-cli2
git ls-files -z '*.md' | xargs -0 .github/node_modules/.bin/prettier --check
```

### Disabled rules

Everything else is on. Some of these may be revisited.

| Tool                                         | Rule                                                                                                                                 | Why                                                                                                                             |
| -------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------- |
| ruff                                         | `docstring-missing-returns` and `-yields` (DOC201/DOC402) for one-line docstrings only (`lint.pydoclint.ignore-one-line-docstrings`) | A one-line summary ("Return the …") already says what comes back; a longer docstring gets a `Returns:` or `Yields:` section.    |
| ruff                                         | `missing-trailing-comma` (COM812)                                                                                                    | Conflicts with `ruff format`; ruff says to disable it.                                                                          |
| ruff                                         | `incorrect-blank-line-before-class`, `multi-line-summary-second-line` (D203/D213)                                                    | Each contradicts a rule that stays on (D211/D212); one of each pair has to go.                                                  |
| ruff                                         | `indentation-with-invalid-multiple` and `-comment` (E111/E114)                                                                       | They assume 4-space indents; ruff says to disable them at any other width. flake8's E111/E114 check the 2 spaces.               |
| ruff (`tests/`)                              | `assert` (S101)                                                                                                                      | pytest works through `assert`.                                                                                                  |
| mypy, basedpyright                           | astroid's untyped calls and missing stubs                                                                                            | astroid (pylint's parser) ships no type information.                                                                            |
| typos                                        | the word `astroid`                                                                                                                   | A real package name.                                                                                                            |
| harden-runner                                | `egress-policy: audit` on macOS and Windows, in the release and Scorecard jobs, and in the weekly external-link check                | macOS and Windows reach unpredictable OS hosts; the release and Scorecard jobs haven't run yet; external links can go anywhere. |
| reuse                                        | `reuse lint` not run (the files still comply: `REUSE.toml` covers them)                                                              | No recent release ships a wheel for Python 3.11+, so installing it builds from source with an unpinned `poetry-core`.           |
| zizmor                                       | `self-repository` on the CI job that runs the repository's root action                                                               | zizmor wants `$/`, and actionlint rejects a bare `$/` (it has no path), so that one line uses `./`.                             |
| zizmor, and the sibling repos' SHA-pin check | `unpinned-uses` on release.yml's SLSA job                                                                                            | SLSA's generator must be referenced by its version tag, not a SHA: it verifies its own ref to produce level-3 provenance.       |
| vulture                                      | not run                                                                                                                              | Its only findings were flake8/pylint hook names, which it can't see being called.                                               |

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
- **release.yml** runs on `v*` tags: CI, a check that the tag matches the version, build provenance,
  PyPI (trusted publishing), then a GitHub release with the dists and the provenance bundle.
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
- **Baselines**, a **smarter `--fix`** (containers, same-module return types), **notebooks**, and
  JSON with comments and trailing commas wherever constricter reads JSON.
- **Fuzzing**, a manual **corpus run** (`tests/corpus.py`), an **adoption guide**, **`--fix` for
  notebooks**, and **SLSA level-3 provenance** (slsa-github-generator) on each release, alongside
  the GitHub attestation.
- **Python 3.11+**, the oldest version still maintained after 3.10's end of life in October 2026.
  Older Pythons aren't planned: 3.10 would add a runtime dependency (`tomli`) for a month, and
  3.6–3.9 would mean dropping `match` from the checker and keeping a second CI setup with older
  tools. Code written for any Python 3 version can still be checked.
- **harden-runner** blocks all but the observed hosts in every Linux job that has run, the Linux
  Test jobs included.

Next, smallest first:

1. **A test coverage badge** (coverage is enforced at 100% already; the badge shows it).
2. **An annotation-coverage report**: a `--coverage` option that prints the share of bindings that
   are typed (overall and per file), for users' own badges, and shown for this project.
3. **Restore `reuse lint`** once `reuse` ships a wheel for Python 3.11+.
4. Revisit the [disabled rules](#disabled-rules).

After the first release (these need it on PyPI, or a published tag):

1. **Switch the release jobs to `block`** with the hosts the first release run shows (PyPI upload,
   Sigstore, GitHub releases).
2. **A PyPI badge**, and `pip install python-constricter` as the documented install.
3. **The GitHub Action on the Marketplace**, so `uses: ivylikethevine/python-constricter@v1` is
   listed (it already works from any tag).
4. **Trunk and MegaLinter plugin definitions**, submitted upstream.
5. **A conda-forge recipe.**
