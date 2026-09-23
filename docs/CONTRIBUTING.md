# Contributing

Bug reports and rule ideas go in an issue; vulnerabilities go through [SECURITY.md](SECURITY.md).

For a pull request, set up the environment and run the checks under [Development](#development):
every one must pass, coverage stays at 100%, and the project's own code passes
`constricter --level=suffocate --all-scopes`. Keep changes small and docs short, add tests for new
behaviour, and note user-facing changes in [CHANGELOG.md](CHANGELOG.md).

When bumping the version for a release, record it in [RUNS.md](RUNS.md): run
`tests/corpus/corpus_table.py --versions dev --write` (with the `corpus` group installed), which
appends this checkout's results under the new version, and commit it with the bump. Between
releases, `--label 0.2.4-rc.1` records a checkpoint under a pseudo-version instead, without bumping
it.

## Development

With [uv](https://docs.astral.sh/uv/) installed (CI pins 0.12.17):

```bash
export UV_PROJECT_ENVIRONMENT=local/.venv
uv venv --prompt constricter local/.venv # the prompt name; uv sync reuses this venv
uv sync --locked --no-install-project --no-build # the dev group: hash-checked wheels from uv.lock
uv pip install --python local/.venv --no-deps --no-build-isolation -e .
```

Checks (as CI runs them): `ruff check .` (every rule, preview included), `ruff format --check .`,
`basedpyright` (all), `mypy` (strict), `pylint constricter tests` (every extension),
`flake8 constricter tests`, `typos`, `validate-pyproject pyproject.toml`, `uv lock --check`,
`constricter --level=suffocate --all-scopes constricter tests`,
`constricter --coverage --all-scopes --fail-under=100 constricter tests`, `pytest --cov` (100%
branch coverage). Everything generated goes in `local/`, but `constricter/fix/stdlib.json`, the
standard-library tables `--fix` reads: after the pinned basedpyright changes, regenerate it from its
typeshed stubs with `local/.venv/bin/python -m tests.typeshed.stdlib_tables` (CI checks it with
`--check`). Python is indented with 4 spaces.

`local/.venv/bin/python tests/ci_local.py` runs them all at once, as CI does: it reads the Lint,
Docs and Test jobs' steps from `.github/workflows/ci.yml` (so it can't fall behind it), fails a step
by its exit status alone (pylint still rates a run with one finding 10.00/10), and prints each
failing step's output in full. Name jobs to run only those (`tests/ci_local.py lint docs`), and add
`--install-hook` once to run it before every `git push`.

After editing a dependency group, run `uv lock` (CI fails until you do). Dependabot updates
`uv.lock`, the npm lock and the actions weekly.

Fuzzing (`tests/test_fuzz.py`) runs with the tests: hypothesmith generates valid Python, which must
never crash the checker and must stay valid after `--fix`. For a large real codebase, run
`local/.venv/bin/python tests/corpus/corpus.py [PATH]` by hand: it checks PATH (default: this
Python's standard library, about 730 files in a few seconds) at `suffocate` and prints the time, the
offences per code, and any crash. `local/.venv/bin/python tests/corpus/corpus_fix.py [PATH]` runs
`--fix --unsafe-fixes` on a copy of it (in `local/corpus-fix/`) and checks every file still compiles
and a second pass has nothing left to fix.
`local/.venv/bin/python tests/corpus/corpus_profile.py [PATH]` checks it under `cProfile`, in one
process, and prints (as Markdown) constricter's slowest modules and functions, and where the rest of
the time went; the profile is saved to `local/profile/`. CI's Corpus job runs all three against the
standard library and, from the pinned `corpus` dependency group (`django`, `sqlalchemy`, `pydantic`,
`pandas` — a web framework, an ORM, a runtime-validation library and a data library), the same way,
and against pure Python 2 (Twisted 12.3.0) and pip 20.3.4 (2/3-era code whose `# type:` comments sit
in modules with Python 2 `__future__` imports), hash-pinned sdists `tests/corpus/corpus_sources.py`
fetches, since neither installs as a dependency.

`tests/corpus/corpus_suite.py` runs a Python 3 corpus package's own test suite (cloned at its pinned
tag, with its test dependencies as its CI installs them, in `local/corpus-suites/`) as released,
after `--fix`, and after `--fix --unsafe-fixes`, and exits 1 if either differs; with `--types` it
runs the package's own type checker (as its CI does) the same three times instead, traces each new
error to the fix mechanism behind it, and exits 1 if there are any. It needs `git`, `uv`, a C
compiler, Rust and the network.

`tests/corpus/corpus_table.py` measures every corpus with released constricter versions and this
checkout (each isolated in its own environment), at every level, checked and fixed, and records a
section per version in [`docs/RUNS.md`](RUNS.md): offences per code, errors and warnings at each
level, fixes, guesses, anything a fix broke, and the share of bindings typed before and after fixing
(by this checkout's `--coverage`). It needs the `corpus` group
(`uv sync --group dev --group corpus`) and `uv`; see its docstring for the options.

CI also runs the tests on PyPy 3.11 and free-threaded Python 3.14, which install only the `test`
dependency group: every dev tool doesn't have wheels for them, and the tests don't need them all.

Markdown (markdownlint-cli2 and prettier, locked in `.github/package-lock.json`):

```bash
npm ci --prefix .github
git ls-files -z '*.md' | xargs -0 .github/node_modules/.bin/markdownlint-cli2
git ls-files -z '*.md' | xargs -0 .github/node_modules/.bin/prettier --check
```

To apply the rulesets in `.github/rulesets/` (repo admin):

```bash
gh api repos/ivylikethevine/python-constricter/rulesets --method POST --input .github/rulesets/main.json
gh api repos/ivylikethevine/python-constricter/rulesets --method POST --input .github/rulesets/tags.json
```

To publish, add a trusted publisher on PyPI (repository `ivylikethevine/python-constricter`,
workflow `release.yml`, environment `pypi`) and a `pypi` environment in the repo settings, then push
a `v*` tag.

## Disabled rules

Everything else is on. Some of these may be revisited.

| Tool               | Rule                                                                               | Why                                                                                                                   |
| ------------------ | ---------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| ruff               | `incorrect-blank-line-before-class`, `multi-line-summary-second-line` (D203/D213)  | Each contradicts a rule that stays on (D211/D212); one of each pair has to go.                                        |
| ruff (`tests/`)    | `assert` (S101)                                                                    | pytest works through `assert`.                                                                                        |
| mypy, basedpyright | astroid's and fastjsonschema's untyped calls and missing stubs                     | Neither astroid (pylint's parser) nor fastjsonschema (the SARIF test's validator) ships type information.             |
| typos              | the word `astroid`                                                                 | A real package name.                                                                                                  |
| typos              | `constricter/fix/stdlib.json`                                                      | Generated from typeshed: the standard library's own names, which typos takes for misspellings.                        |
| harden-runner      | `egress-policy: audit` on macOS and Windows, and in the weekly external-link check | harden-runner supports only audit on GitHub's macOS and Windows runners; external links can go anywhere.              |
| reuse              | `reuse lint` not run (the files still comply: `REUSE.toml` covers them)            | No recent release ships a wheel for Python 3.11+, so installing it builds from source with an unpinned `poetry-core`. |
| zizmor             | `self-repository` (`.github/zizmor.yml`)                                           | Scorecard reads the `$/` form it wants as an unpinned third-party action, so local actions stay `./`.                 |
