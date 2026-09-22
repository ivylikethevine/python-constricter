# constricter

A lint rule no mainstream linter has: **every local variable is annotated where it's first bound.**
It ships as a flake8 plugin, a pylint plugin and a standalone command, all running the same check,
so it fits a flake8, pylint or ruff setup (ruff loads no plugins, so there it runs as the command
beside ruff).

ruff's and flake8-annotations' `ANN` rules stop at function signatures, and type checkers only
complain about a local whose type they can't infer. This rule makes the type of every local explicit.

```python
def total(items: list[int]) -> int:
    count = 0  # LVA001 local variable 'count' is not annotated where it's first bound
    result: int = 0  # ok
    first, *rest = items  # LVA001 twice: 'first' and 'rest'
    head: int
    tail: list[int]
    head, *tail = items  # ok: declared first
    if (n := len(items)) > 3:  # LVA001 'n'
        result = n  # ok: a later rebinding needs nothing more
    for item in items:  # ok: `for` targets have no annotated form
        result += item
    return result
```

## Contents

- [The rule](#the-rule)
- [Install](#install)
- [Standalone command](#standalone-command)
- [flake8](#flake8)
- [pylint](#pylint)
- [With ruff](#with-ruff)
- [Suppressing a line](#suppressing-a-line)
- [Development](#development)

## The rule

Per function body. Nested functions and lambdas are their own scopes, and module and class bodies are
left to the type checker's inference.

- The first binding of a name by `=`, tuple unpacking, `:=` or `with ... as` must be an annotated
  assignment (`name: T = ...`), or come after a bare declaration (`name: T`) in the same function.
- A later rebinding needs nothing more.
- Exempt, because Python has no annotated form for them or they're typed elsewhere: `for` targets,
  comprehension variables, `except ... as`, `match` captures, imports, `def`/`class` names, `type`
  aliases, parameters, and `global`/`nonlocal` names.
- Statements are read in source order: a name first bound in an `if` branch counts as bound in the
  `else` below it.

Every function is checked, methods and functions nested in classes or inside `if`/`try` blocks
included.

| Tool   | Code / symbol                        |
| ------ | ------------------------------------ |
| CLI    | `LVA001`                             |
| flake8 | `LVA001` (plugin prefix `LVA`)       |
| pylint | `C9101` / `unannotated-local-variable` |

Requires Python 3.12+. No runtime dependencies. The `flake8` and `pylint` extras pull in those tools.

## Install

It isn't on PyPI. Install it from its repository, or from a local checkout:

```bash
pip install "python-constricter @ git+https://github.com/<you>/python-constricter@v0.1.0"
pip install -e ../python-constricter                      # a local checkout
pip install "python-constricter[flake8] @ git+https://…"  # plus flake8 (or [pylint])
```

Pinned with hashes (`pip-compile --generate-hashes`, `pip install --require-hashes`)? pip can't hash
a VCS URL, so pin a built wheel instead: a release asset URL with its `--hash=sha256:…`, or a PyPI
release.

## Standalone command

```bash
constricter                                  # every *.py under the current directory
constricter src tests                        # files and directories
constricter --exclude 'tests/fixtures/*' src # skip matching paths (repeatable)
constricter -q src                           # no summary line
python -m constricter src                    # the same, without the console script
```

```text
src/app.py:12:5: LVA001 local variable 'count' is not annotated where it's first bound
Found 1 unannotated local(s) in 14 file(s).
```

When walking a directory it skips hidden directories, `__pycache__`, `venv`, `site-packages`, `build`,
`dist` and `node_modules`. A file you name explicitly is always checked. Exit status: `0` clean, `1`
offences found, `2` a file couldn't be read or parsed.

## flake8

Installing the package into the environment flake8 runs from is all it takes: the plugin registers
through its `flake8.extension` entry point under the `LVA` prefix, and flake8 selects it by default.
`flake8 --version` lists it as `constricter`.

```bash
flake8 src tests                # LVA001 alongside everything else flake8 reports
flake8 --select=LVA src tests   # this rule only
```

flake8 doesn't read `pyproject.toml`. Configure it in `.flake8`, `setup.cfg` or `tox.ini`:

```ini
[flake8]
# Only if you already set `select`: that replaces the default, so add LVA to it.
# select = E,F,W,LVA
# Run flake8 for this rule only (the usual setup next to ruff):
# select = LVA
per-file-ignores =
    tests/fixtures/*: LVA001
```

## pylint

Load it as a plugin, in `pyproject.toml`:

```toml
[tool.pylint.main]
load-plugins = ["constricter.pylint_plugin"]

# Optional: skip it for some files.
# [tool.pylint.main]
# ignore-paths = ["tests/fixtures/.*"]
```

Or in `.pylintrc` (`[MAIN]` / `load-plugins=constricter.pylint_plugin`), or on the command line:

```bash
pylint --load-plugins=constricter.pylint_plugin src
# This rule only:
pylint --load-plugins=constricter.pylint_plugin --disable=all --enable=unannotated-local-variable src
```

The plugin runs the same `ast` check as the command and flake8 (not a walk over astroid's tree), so all
three report the same lines.

## With ruff

ruff can't load third-party plugins, so the rule runs as its own step next to ruff. It only reads
files, so it can run before or after ruff; either order gives the same result.

- **After ruff** (recommended): a `ruff check --fix` or `ruff format` that rewrites a file runs first,
  so the reported line numbers match the code you'll open.
- **Before ruff**: fails faster when the annotation rule is what's broken, since it's quicker than a full
  ruff run on a large tree.

### 1. Tell ruff about the code

Ruff flags `# noqa: LVA001` as an unknown code (RUF102), and `ruff check --fix` deletes it, unless
the code is declared external:

```toml
[tool.ruff.lint]
external = ["LVA"]
```

### 2. Run it alongside

**pre-commit.** Hooks run in the order they're listed. This one goes after ruff's, and the ruff hooks
stay unchanged:

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.16.8
    hooks:
      - id: ruff-check
        args: [--fix]
      - id: ruff-format
  - repo: https://github.com/<you>/python-constricter
    rev: v0.1.0
    hooks:
      - id: constricter # move this repo entry above ruff's to run it first
```

Until the repository is published, use a local hook with the package installed in your dev
environment:

```yaml
  - repo: local
    hooks:
      - id: constricter
        name: constricter
        entry: constricter --quiet
        language: system
        types: [python]
```

**A script, Makefile or justfile.** Chain it onto the ruff commands. `&&` stops at the first failure,
so swap the order to run it first:

```bash
ruff check . && ruff format --check . && constricter src tests
```

```make
lint:
	ruff check .
	ruff format --check .
	constricter src tests
```

**CI** (GitHub Actions), as a step after ruff's:

```yaml
- run: ruff check . && ruff format --check .
- run: constricter src tests
```

**flake8 for this rule only.** If you'd rather have flake8's `--per-file-ignores` and output formats,
run flake8 with `select = LVA` (see [flake8](#flake8)) as the step after ruff. ruff keeps every other
rule.

## Suppressing a line

| Where           | Comment                                          |
| --------------- | ------------------------------------------------ |
| CLI, flake8     | `# noqa: LVA001` (or a bare `# noqa`)            |
| pylint          | `# pylint: disable=unannotated-local-variable`   |
| ruff's `--fix`  | keeps `# noqa: LVA001` only with `lint.external = ["LVA"]` |

The comment goes on the line the offence is reported on: the line with the name, in a statement that
spans several lines.

## Development

```bash
python -m venv .venv && .venv/bin/pip install -e '.[dev]'
.venv/bin/python -m pytest --cov            # 100% at the time of writing; the floor is 95
.venv/bin/ruff check . && .venv/bin/ruff format --check .
.venv/bin/basedpyright                      # strict
.venv/bin/constricter src tests       # the rule, on itself
```

`tests/test_plugins.py` runs real flake8 and pylint, both as subprocesses and in-process.
