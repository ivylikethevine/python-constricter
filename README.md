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

Lint rules: every local variable is typed where it's first bound. Ships as a flake8 plugin, a
pylint plugin and a standalone command (for ruff, which loads no plugins).

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

Checked per function body, including methods and nested functions. Module and class bodies are
not checked. Statements are read in source order, and only a name's first binding counts.

| Code     | Reports                                                  | Fix                                 |
| -------- | -------------------------------------------------------- | ----------------------------------- |
| `LVA001` | `=`, unpacking, `:=` or `with ... as` without annotation | `name: T = ...`, or `name: T` first |
| `LVA002` | an untyped `for` target or `match` capture               | `name: T` first (or a type comment) |
| `LVA003` | a `for` target typed only by `# type: T`                 | `name: T` first                     |

Exempt: comprehensions, `except ... as`, imports, `def`/`class`, `type` aliases, parameters,
`global`/`nonlocal`, and `_`. Opt-in: a `# type:` comment (`x = 1  # type: int`,
`with f() as x:  # type: T`) counts as an annotation for `LVA001`.

## Levels

Each level makes one more code an error. The rest are warnings: the CLI prints them (as
`::warning` or SARIF `warning` in those formats) but exits 0; flake8 and pylint report errors only.

| Level             | Errors                 | Warnings           |
| ----------------- | ---------------------- | ------------------ |
| `relaxed` / `0`   | none                   | all                |
| `strict` / `1`    | `LVA001` (the default) | `LVA002`, `LVA003` |
| `constrict` / `2` | `LVA001`, `LVA002`     | `LVA003`           |
| `suffocate` / `3` | all                    | none               |

Python 3.12+, no runtime dependencies.

## Use

| Tool   | Setup                                                 | Reports                         | Suppress                     |
| ------ | ----------------------------------------------------- | ------------------------------- | ---------------------------- |
| CLI    | `constricter [PATH...] [--level L] [--format F] [-q]` | `LVA001`–`LVA003`               | `# noqa: LVA001`             |
| flake8 | install it (on by default)                            | `LVA001`–`LVA003`               | `# noqa: LVA001`             |
| pylint | `load-plugins = ["constricter.pylint_plugin"]`        | `C9101`–`C9103` (symbols below) | `# pylint: disable=<symbol>` |
| ruff   | run the CLI after ruff; set `lint.external = ["LVA"]` | `LVA001`–`LVA003`               | `# noqa: LVA001`             |

pylint symbols: `unannotated-local-variable`, `untyped-for-or-match-variable`,
`comment-typed-for-variable`.

Options:

| Option        | CLI                                           | flake8 (CLI or config)                     | pylint                            |
| ------------- | --------------------------------------------- | ------------------------------------------ | --------------------------------- |
| level         | `--level`                                     | `--constricter-level`, `constricter-level` | `constricter-level`               |
| type comments | `--type-comments`                             | `--constricter-type-comments`              | `constricter-type-comments = yes` |
| format        | `--format`: `text`, `json`, `github`, `sarif` | -                                          | -                                 |

Tools that run flake8 or pylint (VS Code's extensions, python-lsp-server, prospector, MegaLinter,
Trunk) pick the plugin up once it's installed alongside them.

Without `lint.external`, ruff flags `# noqa: LVA00x` (RUF102) and `--fix` deletes it.

The CLI defaults to `.` and skips hidden dirs, `__pycache__`, `venv`, `site-packages`, `build`,
`dist` and `node_modules`. Exit codes: `0` no errors, `1` errors, `2` an unreadable or unparsable file.

Not on PyPI yet:

```bash
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

```bash
python -m venv local/.venv
local/.venv/bin/pip install --require-hashes -r requirements-dev.txt
local/.venv/bin/pip install --no-deps --no-build-isolation -e .
```

Checks (as CI runs them): `ruff check .` (every rule, preview included), `ruff format --check .`,
`basedpyright` (all), `mypy` (strict), `pylint src tests` (every extension), `flake8 src tests`,
`typos`, `constricter --level=suffocate src tests`, `pytest --cov` (100% branch coverage).
Everything generated goes in `local/`. Python is indented with 2 spaces.

Markdown (markdownlint-cli2 and prettier, locked in `.github/package-lock.json`):

```bash
npm ci --prefix .github
git ls-files -z '*.md' | xargs -0 .github/node_modules/.bin/markdownlint-cli2
git ls-files -z '*.md' | xargs -0 .github/node_modules/.bin/prettier --check
```

After editing the `dev` extra, regenerate the lock (CI fails until you do):

```bash
local/.venv/bin/uv pip compile pyproject.toml --extra dev --universal --python-version 3.12 --generate-hashes -o requirements-dev.txt
```

### Disabled rules

Everything else is on. Some of these may be revisited.

| Tool               | Rule                                                                              | Why                                                                                                               |
| ------------------ | --------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| ruff               | `docstring-missing-returns`, `docstring-missing-yields` (DOC201/DOC402)           | They require Returns/Yields sections; docstrings here stay one line.                                              |
| ruff               | `missing-trailing-comma` (COM812)                                                 | Conflicts with `ruff format`; ruff says to disable it.                                                            |
| ruff               | `incorrect-blank-line-before-class`, `multi-line-summary-second-line` (D203/D213) | Each contradicts a rule that stays on (D211/D212); one of each pair has to go.                                    |
| ruff               | `indentation-with-invalid-multiple` and `-comment` (E111/E114)                    | They assume 4-space indents; ruff says to disable them at any other width. flake8's E111/E114 check the 2 spaces. |
| ruff (`tests/`)    | `assert` (S101)                                                                   | pytest works through `assert`.                                                                                    |
| mypy, basedpyright | astroid's untyped calls and missing stubs                                         | astroid (pylint's parser) ships no type information.                                                              |
| pylint             | the `while_used` extension                                                        | It bans `while` outright; the checker's work queues need it.                                                      |
| typos              | the word `astroid`                                                                | A real package name.                                                                                              |
| markdownlint       | line length (MD013)                                                               | Prose is hand-wrapped; tables and code can't wrap.                                                                |
| harden-runner      | `egress-policy: audit`, not `block`                                               | `block` needs each job's allowed hosts, known only after CI has run.                                              |
| vulture            | not run                                                                           | Its only findings were flake8/pylint hook names, which it can't see being called.                                 |

To apply the rulesets in `.github/rulesets/` (repo admin):

```bash
gh api repos/ivylikethevine/python-constricter/rulesets --method POST --input .github/rulesets/main.json
gh api repos/ivylikethevine/python-constricter/rulesets --method POST --input .github/rulesets/tags.json
```

## Roadmap

Done:

- **ci.yml** runs on pushes and PRs. Lint job: the checks above and the pre-commit hook. Test job: pytest on Linux, macOS and Windows × Python 3.12–3.14. Build job:
  sdist and wheel, `twine check`, a wheel smoke test, and upload as an artifact.
- **security.yml** runs on pushes, PRs and weekly: CodeQL (Python and Actions), zizmor (pedantic),
  actionlint (kjanat fork) and pip-audit on the lock.
- **release.yml** runs on `v*` tags: CI, a check that the tag matches the version, then build
  provenance attestation.
- **Pinning:** actions are pinned by SHA, Python dependencies by hash, and actionlint (kjanat's
  fork, which reads the `$/` self-repository syntax the workflows use) by sha256. Dependabot updates
  the first two weekly; actionlint is bumped by hand.
- **Lock check:** CI fails when `requirements-dev.txt` doesn't match `pyproject.toml`.
- **Docs:** CI lints and formats every Markdown file; `SECURITY.md` says how to report a
  vulnerability.
- **Releases:** each tag also gets a GitHub release with the dists and the provenance bundle.
- **Rulesets:** `.github/rulesets/` requires every check on `main` and protects `v*` tags (apply
  them as above).
- **Suffocate:** `src/` and `tests/` pass at `--level=suffocate` in CI.

Next, smallest first:

1. Read `[tool.constricter]` (`level`, `exclude`, `type-comments`) from `pyproject.toml` in the CLI.
2. After the first CI runs: fix what fails on GitHub, and switch harden-runner from `audit` to
   `block` with each job's allowed hosts.
3. Publish to PyPI: a trusted publisher, a `pypi` environment, and a `publish` job in release.yml
   (`pypa/gh-action-pypi-publish`, `id-token: write`).
4. Once the repo is public: OpenSSF Scorecard (its pin check misreads the workflows' `$/` references as
   unpinned actions, so it will flag them) and `actions/dependency-review-action`. CodeQL
   uploads and attestations also need a public repo or GitHub Advanced Security.
5. **Python 2 code.** Turn on type comments automatically when a file looks like Python 2 (its
   only annotation form). Parsing Python 2 syntax itself needs a separate parser.
6. Optionally check module and class bodies (a fifth level, or an opt-in).
7. Keep 100% of the project's own Python at `suffocate`, including any new scripts, and extend it to
   module and class bodies once they're checked.
8. Revisit the [disabled rules](#disabled-rules).
9. **Python 3.6+.** Code written for any Python 3 version can already be checked, since this runs on
   3.12+ and newer parsers read older syntax. _Running_ on 3.6–3.11 would mean dropping `match`,
   `StrEnum`, `typing.override` and `X | Y` unions from the source. 3.8+ is cheap to reach. 3.6 and 3.7
   also need CI on old runner images and older pytest/ruff/pylint, all of which dropped them.
