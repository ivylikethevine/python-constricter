# python-con`strict`er

> EXPERIMENTAL UNTIL v1.0.0

**I want all of my python code typed.**

[![CI](https://github.com/ivylikethevine/python-constricter/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/ivylikethevine/python-constricter/actions/workflows/ci.yml)
[![Security](https://github.com/ivylikethevine/python-constricter/actions/workflows/security.yml/badge.svg?branch=main)](https://github.com/ivylikethevine/python-constricter/actions/workflows/security.yml)
[![PyPI](https://img.shields.io/pypi/v/python-constricter)](https://pypi.org/project/python-constricter/)
[![Python](https://img.shields.io/pypi/pyversions/python-constricter)](https://pypi.org/project/python-constricter/)
[![OpenSSF Scorecard](https://api.scorecard.dev/projects/github.com/ivylikethevine/python-constricter/badge)](https://scorecard.dev/viewer/?uri=github.com/ivylikethevine/python-constricter)
[![Test coverage: 100%](https://img.shields.io/badge/test_coverage-100%25-brightgreen)](pyproject.toml)
[![Annotations: 100%](https://img.shields.io/badge/annotations-100%25-brightgreen)](#annotation-coverage)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue)](LICENSE.md)

Lint rules: every local variable is typed where it's first bound. Ships as a flake8 plugin, a pylint
plugin and a standalone command (for ruff, which loads no plugins).

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

---

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
class bodies too. Statements are read in source order, and only a name's first binding counts
(`LVA008`–`LVA010` aside, which read every one).

| Code     | Reports                                                                                   | Fix                                            |
| -------- | ----------------------------------------------------------------------------------------- | ---------------------------------------------- |
| `LVA001` | `=`, unpacking, `:=` or `with ... as` in a function without annotation                    | `name: T = ...`, or `name: T` first            |
| `LVA002` | an untyped `for` target or `match` capture                                                | `name: T` first (or a type comment)            |
| `LVA003` | a `for` target typed only by `# type: T`                                                  | `name: T` first                                |
| `LVA004` | with `all-scopes`: the same as `LVA001`, in a module or class body                        | `name: T = ...` (`ClassVar[T]` in a dataclass) |
| `LVA005` | an annotation with `Any`, `object` or a generic without its parameters                    | name the real type                             |
| `LVA006` | an annotation nested `nesting` deep (3 by default)                                        | a `type` alias for a part of it                |
| `LVA007` | a name annotated again with the type it already has, in the same block                    | drop the second annotation                     |
| `LVA008` | with every value the name ever holds known: an annotation that could narrow to them       | narrow it (`total: int`)                       |
| `LVA009` | a value, anywhere in the name's lifetime, whose type doesn't fit its annotation           | fix the value, or widen the annotation         |
| `LVA010` | with every value known: a union member no value is                                        | drop the member                                |
| `LVA011` | an annotation listing a fixed-length tuple of more than `max-length` types (4 by default) | name the fields (a `NamedTuple`, a dataclass)  |
| `LVA012` | opt-in: a local bound once, outside any loop, and never rebound                           | `name: Final = ...`                            |

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

`LVA009` checks every binding of an annotated name (or parameter) in the scope, wherever and in
whatever order they run, but only one whose value's type `--fix` would infer with certainty, and
only against types whose every subclass is known: builtins, and classes the module defines on such
bases. An imported class, a protocol or an alias is never compared, builtin containers are compared
by the container alone (`flags: tuple[str, ...] = ("-q",)` fits), a copy of a union-typed name is
skipped (an `is None` check may have narrowed it), and so is a name annotated only under
`if TYPE_CHECKING:`. It has no `--fix`.

`LVA008` and `LVA010` also need every binding's value known (one unknown call, loop target or
unpacking and the name could hold anything), and are only claimed for a function's own names: a
module or class variable is state other code rebinds out of sight (`mod.X = ...`, `self.x = ...`,
`monkeypatch`), and a `nonlocal` write from a nested function counts as unknown too. Neither has a
`--fix`: `--fix` adds annotations, it doesn't rewrite them.

## Levels

Each level makes one more code an error. The rest are warnings: the CLI prints them (as `::warning`
or SARIF `warning` in those formats) but exits 0; flake8 and pylint report errors only.

| Level             | Errors                                 | Warnings                                                  |
| ----------------- | -------------------------------------- | --------------------------------------------------------- |
| `relaxed` / `0`   | none                                   | `LVA001`–`LVA004`, `LVA007`, `LVA009`                     |
| `strict` / `1`    | `LVA001`, `LVA004` (the default)       | `LVA002`, `LVA003`, `LVA005`–`LVA007`, `LVA009`, `LVA011` |
| `constrict` / `2` | `LVA001`, `LVA004`, `LVA002`, `LVA009` | `LVA003`, `LVA005`–`LVA008`, `LVA010`, `LVA011`           |
| `suffocate` / `3` | all                                    | none                                                      |

`LVA005`, `LVA006` and `LVA011` aren't reported at `relaxed`; `LVA008` and `LVA010` only from
`constrict`. `LVA012` is opt-in, reported only when selected by its full code
(`--extend-select LVA012`, flake8's `extend-select = LVA012`, pylint's `enable = could-be-final`),
at every level, and an error only at `suffocate`: on the corpus, 45–70% of every codebase's first
bindings qualify, so it suits a codebase that wants `Final` everywhere it can go, not a default.

Python 3.11+, no runtime dependencies.

## Use

| Tool   | Setup                                                 | Reports                         | Suppress                                         |
| ------ | ----------------------------------------------------- | ------------------------------- | ------------------------------------------------ |
| CLI    | `constricter [PATH...] [--level L] [--format F] [-q]` | `LVA001`–`LVA012`               | `# noqa: LVA001`                                 |
| flake8 | install it (on by default)                            | `LVA001`–`LVA012`               | `# noqa: LVA001`                                 |
| pylint | `load-plugins = ["constricter.plugins.pylint"]`       | `C9101`–`C9112` (symbols below) | `# noqa: LVA001` or `# pylint: disable=<symbol>` |
| ruff   | run the CLI after ruff; set `lint.external = ["LVA"]` | `LVA001`–`LVA012`               | `# noqa: LVA001`                                 |

pylint symbols: `unannotated-local-variable`, `untyped-for-or-match-variable`,
`comment-typed-for-variable`, `unannotated-module-or-class-variable`, `vague-annotation`,
`deeply-nested-annotation`, `redundant-annotation`, `narrowable-annotation`,
`mismatched-value-type`, `unused-union-member`, `long-tuple-annotation`, `could-be-final` (off until
enabled).

Options:

| Option           | CLI                                                                                                                                                                          | `[tool.constricter]`                            | flake8 (CLI or config)          | pylint                            |
| ---------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------- | ------------------------------- | --------------------------------- |
| level            | `--level`                                                                                                                                                                    | `level`                                         | `--constricter-level`           | `constricter-level`               |
| type comments    | `--type-comments`                                                                                                                                                            | `type-comments`                                 | `--constricter-type-comments`   | `constricter-type-comments = yes` |
| all scopes       | `--all-scopes`                                                                                                                                                               | `all-scopes`                                    | `--constricter-all-scopes`      | `constricter-all-scopes = yes`    |
| nesting          | `--nesting N`                                                                                                                                                                | `nesting`                                       | `--constricter-nesting`         | `constricter-nesting`             |
| max length       | `--max-length N` (LVA011)                                                                                                                                                    | `max-length`                                    | `--constricter-max-length`      | `constricter-max-length`          |
| type hierarchy   | -                                                                                                                                                                            | `narrower` (a table)                            | `--constricter-narrower`        | `constricter-narrower`            |
| fix              | `--fix` (`--unsafe-fixes` for guesses), `--diff` to preview                                                                                                                  | -                                               | -                               | -                                 |
| infer with       | `--infer-with CHECKERS` (`basedpyright`, `ty`, both: inferred types, as guesses)                                                                                             | `infer-with`                                    | -                               | -                                 |
| show fixes       | `--show-fixes` (each fix and how it was decided, text)                                                                                                                       | -                                               | -                               | -                                 |
| fix levels       | `--fix-select`, `--fix-ignore`, `--unsafe-fix-select` (mechanisms: [docs/FIXES.md](https://github.com/ivylikethevine/python-constricter/blob/main/docs/FIXES.md#fix-levels)) | `fix-select`, `fix-ignore`, `unsafe-fix-select` | -                               | -                                 |
| select           | `--select CODES` (codes or prefixes)                                                                                                                                         | `select`                                        | flake8's own `select`           | pylint's own `enable`             |
| extend select    | `--extend-select CODES` (also report these; an opt-in code by its full code)                                                                                                 | `extend-select`                                 | flake8's own `extend-select`    | pylint's own `enable`             |
| ignore           | `--ignore CODES`                                                                                                                                                             | `ignore`                                        | flake8's own `extend-ignore`    | pylint's own `disable`            |
| exclude          | `--exclude GLOB` (repeatable)                                                                                                                                                | `exclude`                                       | flake8's own `exclude`          | pylint's own `ignore-paths`       |
| format           | `--format`: `text`, `full` (with source), `json`, `github`, `sarif`, `gitlab`, `junit`, `rdjson`                                                                             | -                                               | -                               | -                                 |
| statistics       | `--statistics` (counts per code, text format)                                                                                                                                | -                                               | -                               | -                                 |
| jobs             | `--jobs N` (`-j`; 0: one per CPU)                                                                                                                                            | `jobs`                                          | flake8's own `--jobs`           | pylint's own `--jobs`             |
| baseline         | `--baseline FILE`; `--write-baseline` records it                                                                                                                             | `baseline`                                      | -                               | -                                 |
| coverage         | `--coverage`, `--fail-under PCT`                                                                                                                                             | -                                               | -                               | -                                 |
| per-path levels  | -                                                                                                                                                                            | `per-path-levels`                               | -                               | -                                 |
| per-file ignores | -                                                                                                                                                                            | `per-file-ignores`                              | flake8's own `per-file-ignores` | -                                 |
| stdin            | `-` as the path, `--stdin-filename PATH`                                                                                                                                     | -                                               | flake8's own `-`                | -                                 |
| exit status      | `--exit-zero`                                                                                                                                                                | -                                               | flake8's own `--exit-zero`      | pylint's own `--exit-zero`        |
| output file      | `--output-file FILE`                                                                                                                                                         | -                                               | flake8's own `--output-file`    | pylint's own `--output`           |

`constricter --explain LVA002` prints a code's rationale, its fix, and the levels that report it.

The CLI reads `[tool.constricter]` from the nearest `pyproject.toml` above the current directory;
its flags override it, and `--exclude` adds to it. An unknown key or a bad value exits 2.

```toml
[tool.constricter]
level = "constrict" # or 2
exclude = ["tests/fixtures/*"]
type-comments = false
all-scopes = true
nesting = 3
max-length = 4
jobs = 0
baseline = "constricter-baseline.json" # the default; relative to this pyproject.toml

# The first glob a file matches sets its level; other files get `level`.
[tool.constricter.per-path-levels]
"tests/*" = "strict"

# Codes (or prefixes) to drop for files matching a glob.
[tool.constricter.per-file-ignores]
"tests/fixtures/*" = ["LVA005", "LVA006"]

# Your own type hierarchy for LVA008–LVA010: each type, and the types it's narrower than.
[tool.constricter.narrower]
UserId = ["str"]  # an imported NewType the rules then compare
int = []          # an `int` no longer fits `float`
select = ["LVA00"]
ignore = ["LVA003"]
```

`--fix` adds the annotation where the value decides it: a literal (`count = 0` becomes
`count: int = 0`), a container whose elements agree, a constructor or a function that declares its
return type or whose `return`s agree (in another checked file too), a copy, subscript, attribute or
method call of a local whose type is known, and values computed from those; a loop's target or an
unpacking's names get a declaration on the line before. `--unsafe-fixes` adds guesses, and
`--show-fixes` lists each fix and how its value decided it. `--infer-with basedpyright` (or `ty`, or
`basedpyright,ty`, installed alongside) asks those type checkers for what `--fix` can't type itself,
as guesses. The full list is in
[docs/FIXES.md](https://github.com/ivylikethevine/python-constricter/blob/main/docs/FIXES.md).

### Installing and running

```bash
pip install python-constricter           # into the project's environment
uvx --from python-constricter constricter # or run it without installing: uv's tool runner
pipx run --spec python-constricter constricter  # or pipx's
```

Tools that run flake8 or pylint (VS Code's extensions, python-lsp-server, prospector, MegaLinter,
Trunk) pick the plugin up once it's installed alongside them.

Without `lint.external`, ruff flags `# noqa: LVA00x` (RUF102) and `--fix` deletes it.

The CLI defaults to `.`, checks `*.py` and `*.ipynb`, and skips hidden dirs, `__pycache__`, `venv`,
`site-packages`, `build`, `dist` and `node_modules` by directory name; `--exclude` adds more
directory names (or globs) to skip the same way, on top of matching whole paths and file names. Exit
codes: `0` no errors, `1` errors, `2` an unreadable or unparsable file, a `--fix` its encoding can't
hold, or a bad `pyproject.toml`. A module is read in its PEP 263 declaration's encoding.

pre-commit, after ruff's hooks (or `constricter-fix`, which runs `--fix` first):

```yaml
- repo: https://github.com/ivylikethevine/python-constricter
  rev: v0.2.6
  hooks:
    - id: constricter
```

pre-commit.ci, tox, nox, Bazel, Pants and the GitHub Action (PR annotations, a summary table and a
SARIF log) are in
[docs/INTEGRATIONS.md](https://github.com/ivylikethevine/python-constricter/blob/main/docs/INTEGRATIONS.md);
settings for VS Code, Zed and Neovim are in
[docs/editors/](https://github.com/ivylikethevine/python-constricter/blob/main/docs/editors/README.md).

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
`--level`. Each rule has its help text and a link to [Rules](#rules), and each certain fix is a
SARIF fix (columns count characters: `columnKind` is `unicodeCodePoints`). In GitHub Actions, upload
it to code scanning (the job needs `security-events: write`; the
[GitHub Action](https://github.com/ivylikethevine/python-constricter/blob/main/docs/INTEGRATIONS.md#github-actions)'s
`sarif-file` output does the same):

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

## Development

Setting up, the checks CI runs, the corpus runs and the rules this project's own linters leave off
are in
[docs/CONTRIBUTING.md](https://github.com/ivylikethevine/python-constricter/blob/main/docs/CONTRIBUTING.md).

## Roadmap

What's done and what's next, by scope:
[docs/ROADMAP.md](https://github.com/ivylikethevine/python-constricter/blob/main/docs/ROADMAP.md).

## AI usage

Heavily inspired by
[Dictionarry/Profilarr's AI Transparency Statement](https://v2.dictionarry.dev/ai-transparency).

I have used generative AI to write large parts of this code. All of the code here is my
_responsibility_ regardless: AI is a tool, not an owner of a project. I have personally understood,
reviewed, and approved all of the AI-generated code in this repository, and **mainline releases**
carry the same accountability to me as anything I write and publish myself.
