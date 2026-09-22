# constricter

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

| Option        | CLI                                           | `[tool.constricter]` | flake8 (CLI or config)        | pylint                            |
| ------------- | --------------------------------------------- | -------------------- | ----------------------------- | --------------------------------- |
| level         | `--level`                                     | `level`              | `--constricter-level`         | `constricter-level`               |
| type comments | `--type-comments`                             | `type-comments`      | `--constricter-type-comments` | `constricter-type-comments = yes` |
| all scopes    | `--all-scopes`                                | `all-scopes`         | `--constricter-all-scopes`    | `constricter-all-scopes = yes`    |
| nesting       | `--nesting N`                                 | `nesting`            | `--constricter-nesting`       | `constricter-nesting`             |
| fix           | `--fix`                                       | -                    | -                             | -                                 |
| exclude       | `--exclude GLOB` (repeatable)                 | `exclude`            | flake8's own `exclude`        | pylint's own `ignore-paths`       |
| format        | `--format`: `text`, `json`, `github`, `sarif` | -                    | -                             | -                                 |

The CLI reads `[tool.constricter]` from the nearest `pyproject.toml` above the current directory;
its flags override it, and `--exclude` adds to it. An unknown key or a bad value exits 2.

```toml
[tool.constricter]
level = "constrict" # or 2
exclude = ["tests/fixtures/*"]
type-comments = false
all-scopes = true
nesting = 5
```

`--fix` adds the annotation where the value decides it — a literal (`count = 0` becomes
`count: int = 0`) or a call to a capitalised name (`path = Path(...)`) — for a plain `name = value`
in a function or module body. It never touches class bodies (a dataclass would gain a field) or
unpacking, and it leaves what it can't fix reported.

Tools that run flake8 or pylint (VS Code's extensions, python-lsp-server, prospector, MegaLinter,
Trunk) pick the plugin up once it's installed alongside them.

Without `lint.external`, ruff flags `# noqa: LVA00x` (RUF102) and `--fix` deletes it.

The CLI defaults to `.` and skips hidden dirs, `__pycache__`, `venv`, `site-packages`, `build`,
`dist` and `node_modules`. Exit codes: `0` no errors, `1` errors, `2` an unreadable or unparsable
file, or a bad `pyproject.toml`.

```bash
pip install python-constricter # once the first release is out; until then:
pip install "python-constricter @ git+https://github.com/ivylikethevine/python-constricter@v0.2.0"
```

pre-commit, after ruff's hooks:

```yaml
- repo: https://github.com/ivylikethevine/python-constricter
  rev: v0.2.0
  hooks:
    - id: constricter
```

## Development

With [uv](https://docs.astral.sh/uv/) installed (CI pins 0.12.17):

```bash
export UV_PROJECT_ENVIRONMENT=local/.venv
uv sync --locked --no-install-project # the dev group, hash-checked from uv.lock
uv pip install --python local/.venv --no-deps --no-build-isolation -e .
```

Checks (as CI runs them): `ruff check .` (every rule, preview included), `ruff format --check .`,
`basedpyright` (all), `mypy` (strict), `pylint src tests` (every extension), `flake8 src tests`,
`typos`, `uv lock --check`, `constricter --level=suffocate --all-scopes src tests`, `pytest --cov`
(100% branch coverage). Everything generated goes in `local/`. Python is indented with 2 spaces.

After editing the `dev` group, run `uv lock` (CI fails until you do). Dependabot updates `uv.lock`,
the npm lock and the actions weekly.

Markdown (markdownlint-cli2 and prettier, locked in `.github/package-lock.json`):

```bash
npm ci --prefix .github
git ls-files -z '*.md' | xargs -0 .github/node_modules/.bin/markdownlint-cli2
git ls-files -z '*.md' | xargs -0 .github/node_modules/.bin/prettier --check
```

### Disabled rules

Everything else is on. Some of these may be revisited.

| Tool               | Rule                                                                               | Why                                                                                                               |
| ------------------ | ---------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| ruff               | `docstring-missing-returns`, `docstring-missing-yields` (DOC201/DOC402)            | They require Returns/Yields sections; docstrings here stay one line.                                              |
| ruff               | `missing-trailing-comma` (COM812)                                                  | Conflicts with `ruff format`; ruff says to disable it.                                                            |
| ruff               | `incorrect-blank-line-before-class`, `multi-line-summary-second-line` (D203/D213)  | Each contradicts a rule that stays on (D211/D212); one of each pair has to go.                                    |
| ruff               | `indentation-with-invalid-multiple` and `-comment` (E111/E114)                     | They assume 4-space indents; ruff says to disable them at any other width. flake8's E111/E114 check the 2 spaces. |
| ruff (`tests/`)    | `assert` (S101)                                                                    | pytest works through `assert`.                                                                                    |
| mypy, basedpyright | astroid's untyped calls and missing stubs                                          | astroid (pylint's parser) ships no type information.                                                              |
| typos              | the word `astroid`                                                                 | A real package name.                                                                                              |
| harden-runner      | `egress-policy: audit` on macOS and Windows, and in the release and Scorecard jobs | macOS and Windows reach unpredictable OS hosts; the others haven't run yet, so their hosts aren't known.          |
| vulture            | not run                                                                            | Its only findings were flake8/pylint hook names, which it can't see being called.                                 |

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
- **LVA005, LVA006 and `--fix`.**
- **Python 3.11+**, the oldest version still maintained after 3.10's end of life in October 2026.
  Older Pythons aren't planned: 3.10 would add a runtime dependency (`tomli`) for a month, and
  3.6–3.9 would mean dropping `match` from the checker and keeping a second CI setup with older
  tools. Code written for any Python 3 version can still be checked.
- **harden-runner** blocks all but the observed hosts in every Linux job that has run, the Linux
  Test jobs included.

Next, smallest first:

1. Switch the release jobs and Scorecard to `block` once they've run and their hosts are known.
2. **gitleaks:** scan the history for committed secrets (as the sibling repos do).
3. **lychee:** check the Markdown files' links, offline in CI and weekly for external ones.
4. **`reuse lint`:** check every file's licence header (the SPDX headers are already there).
5. **validate-pyproject and check-wheel-contents:** catch packaging mistakes before a release.
6. **A `constricter-fix` pre-commit hook**, running `--fix`.
7. **SARIF upload docs:** examples for GitHub code scanning, SonarQube and Codacy.
8. **CHANGELOG**, with generated release notes.
9. **Badges:** CI, PyPI, Scorecard and licence.
10. **Issue and PR templates, and CODEOWNERS.**
11. **CONTRIBUTING**, kept short.
12. **`--explain LVA00x`:** print a rule's rationale and examples, as `ruff rule` does.
13. **`--select` / `--ignore`:** choose codes without changing the level.
14. **`--diff`:** preview what `--fix` would change.
15. **`--statistics`:** counts per code, to track progress on a large codebase.
16. **Per-path levels** in `[tool.constricter]`, e.g. `strict` for `tests/` and `suffocate`
    elsewhere.
17. **Parallel checking** for large repositories.
18. **A GitHub Action** (`uses: ivylikethevine/python-constricter@v1`) that runs `--format=github`
    for PR annotations.
19. **Fuzzing:** hypothesis with hypothesmith generates valid Python; the checker must never crash
    on it.
20. **A weekly run over a large real codebase** (CPython's standard library) to catch crashes and
    slowdowns.
21. **Mutation testing (mutmut)**, weekly, to check the tests catch bugs rather than just cover
    lines. It's slow, so not on every push.
22. **An adoption guide** for existing codebases: start at `relaxed`, baseline, then raise the
    level.
23. **`# lva-ignore: LVA00x`:** a suppression that, unlike `# noqa` (which every front end honours),
    still reports the offence as a warning at `suffocate`.
24. **Trunk and MegaLinter plugin definitions**, submitted upstream once it's on PyPI.
25. **A conda-forge recipe**, once it's on PyPI.
26. **A baseline file (`--baseline`):** record existing offences so a large codebase can adopt the
    tool and fail only on new ones.
27. **A smarter `--fix`:** uniform list and dict literals (`[1, 2]` becomes `list[int]`), and calls
    to same-module functions that declare their return type.
28. **Jupyter notebooks:** check `.ipynb` code cells, as ruff does.
29. **SLSA level-3 provenance** (slsa-github-generator), a stronger guarantee than today's
    attestation.
30. Revisit the [disabled rules](#disabled-rules).
