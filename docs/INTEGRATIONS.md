# Integrations

Running constricter from pre-commit, CI and build tools. The [README](../README.md#use) has the
options and `[tool.constricter]`; editors are in [editors/](editors/README.md).

## pre-commit

pre-commit, after ruff's hooks (or `constricter-fix`, which runs `--fix` first):

```yaml
- repo: https://github.com/ivylikethevine/python-constricter
  rev: v0.2.3
  hooks:
    - id: constricter
```

`constricter-fix` runs as one process (`require_serial`), so its cross-module `--fix` sees every
file pre-commit passes it. Both hooks are pure Python, so [pre-commit.ci](https://pre-commit.ci)
runs them as they are; it commits `constricter-fix`'s annotations back to the pull request:

```yaml
ci:
  autofix_prs: true # the default: push the hooks' fixes to the pull request
repos:
  - repo: https://github.com/ivylikethevine/python-constricter
    rev: v0.2.3
    hooks:
      - id: constricter-fix
```

## tox and nox

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

## Bazel and Pants

Bazel, through [rules_lint](https://github.com/aspect-build/rules_lint)'s flake8 aspect, with the
plugin in the flake8 binary's dependencies (`tools/lint/BUILD.bazel`, then `linters.bzl` as
rules_lint's own docs have it):

```starlark
load("@rules_python//python/entry_points:py_console_script_binary.bzl", "py_console_script_binary")

py_console_script_binary(
    name = "flake8",
    pkg = "@pip//flake8:pkg",
    deps = ["@pip//python_constricter"],  # the plugin, from your requirements
)
```

Pants, whose flake8 installs from a resolve with the plugin locked in it (`pants.toml`; both
`flake8` and `python-constricter` in that resolve's requirements):

```toml
[python.resolves]
flake8 = "3rdparty/python/flake8.lock"

[flake8]
install_from_resolve = "flake8"
requirements = ["flake8", "python-constricter"]
```

## GitHub Actions

GitHub Actions, as PR annotations, with a table of the offences per code on the run's summary page:

```yaml
- uses: ivylikethevine/python-constricter@v0.2.3
  with:
    args: --format=github src tests # the default is `--format=github` on `.`
    python-version: "3.13" # 3.11 or later
    version: "" # a release to install from PyPI (with uv); empty: the action's own tag
    summary: "true" # "false": no summary table
```

Its `sarif-file` output is the same check as a SARIF log, for code scanning (the job needs
`security-events: write`):

```yaml
- uses: ivylikethevine/python-constricter@v0.2.3
  id: constricter
- if: ${{ !cancelled() }} # upload the findings even when the check failed on them
  uses: github/codeql-action/upload-sarif@1c5b675653bb5c22dbe9b12b556ec555138e09fd # v4.38.1
  with:
    sarif_file: ${{ steps.constricter.outputs.sarif-file }}
    category: constricter
```

For SARIF from the command itself (and SonarQube), see the README's
[SARIF](../README.md#sarif-code-scanning) section.
