# Contributing

Bug reports and rule ideas go in an issue; vulnerabilities go through [SECURITY.md](SECURITY.md).

For a pull request, set up the environment and run the checks under [Development](#development):
every one must pass, coverage stays at 100%, and the project's own code passes
`constricter --level=suffocate --all-scopes`. Keep changes small and docs short, add tests for new
behaviour, and note user-facing changes in [CHANGELOG.md](CHANGELOG.md).

When bumping the version for a release, record it in [RUNS.md](RUNS.md): run
`local/.venv/bin/python -m tests.corpus tests/corpus/runs/release.toml`, which appends this
checkout's results under the new version, and commit it with the bump. Between releases,
`--label 0.2.4-rc.1` records a checkpoint under a pseudo-version instead, without bumping it.

## Development

With [uv](https://docs.astral.sh/uv/) installed (CI pins 0.12.17):

```bash
export UV_PROJECT_ENVIRONMENT=local/.venv
uv venv --prompt constricter local/.venv # the prompt name; uv sync reuses this venv
uv sync --locked --no-install-project --no-build # the dev group: hash-checked wheels from uv.lock
uv pip install --python local/.venv --no-deps --no-build-isolation -e .
```

Checks (as CI runs them), on `constricter stdlib_tables tests hatch_build.py` where they take paths:
`ruff check .` (every rule, preview included), `ruff format --check .`, `basedpyright` (all), `mypy`
(strict), `pylint` (every extension, and again for a warning on each module past 900 lines, 100
short of the limit it fails one at), `flake8`, `typos`, `validate-pyproject pyproject.toml`,
`lint-imports` (the layers `pyproject.toml` states), `uv lock --check`,
`constricter --level=suffocate --all-scopes`,
`constricter --coverage --all-scopes --fail-under=100`, `pytest --cov` (100% branch coverage; with
`-n auto --dist loadgroup`, on every CPU). Everything generated goes in `local/`, but the
standard-library tables `--fix` reads (`constricter/fix/tables/`) and the tests'
`stdlib_tables/partial.json`, which git ignores: a build (`hatch_build.py`), the editable install
included, generates them from the typeshed stubs of the basedpyright `uv.lock` pins, read with the
`typeshed-client` it pins, in about 12 seconds on 4 cores (30 on one), wherever they're missing or
stale. After changing the generator (`stdlib_tables/`) or either pin, run
`local/.venv/bin/python -m stdlib_tables --if-stale`; `tests/fix/libraries/test_stdlib_tables.py`
fails until then. Python is indented with 4 spaces. An editor running Pyright or basedpyright
(Pylance, Neovim's Mason) needs no setting of its own: `pyrightconfig.json` points both at
`local/.venv` and the code checked, and basedpyright alone reads the stricter `[tool.basedpyright]`
it extends.

`local/.venv/bin/python tests/ci_local.py` runs them all at once, as CI does: it reads the Lint,
Docs and Test jobs' steps from `.github/workflows/ci.yml` (so it can't fall behind it), fails a step
by its exit status alone (pylint still rates a run with one finding 10.00/10), and prints each
failing step's output in full. It also runs the tests on each other Python in the Test job's matrix
(PyPy and free-threaded builds included), each in its own `local/.venv-<python>` that uv creates, so
what only one interpreter breaks fails before CI. Name jobs to run only those
(`tests/ci_local.py lint docs interpreters`), and add `--install-hook` once to run it before every
`git push`.

Three things pass on Python 3.14 and fail on 3.11, CI's oldest, and no linter says so. A quoted
alias (`Record: TypeAlias = "dict[str, object]"`) in a signature's `Record | None` is `str | None`
there, a `TypeError` at import, since only 3.14 leaves annotations unevaluated when a function is
defined. A dataclass field defaulting to `MappingProxyType({})` raises at import, since 3.11's
`dataclasses` takes any unhashable default for a mutable one. And 3.11 forks its worker processes,
so a `ProcessPoolExecutor` first used while another thread runs can hang.

After editing a dependency group, run `uv lock` (CI fails until you do). Nothing bumps a pin for
you: `tool-versions.yml` lists `uv.lock`'s direct dependencies, the npm pins, the actions and the
tools pinned by URL that are behind upstream in one tracking issue, and each bump is a hand edit
(`.github/scripts/check_tool_versions.sh` prints the same report locally).

Fuzzing (`tests/test_fuzz.py`) runs with the tests: hypothesmith generates valid Python, which must
never crash the checker and must stay valid after `--fix`. For a large real codebase, the corpus
runner measures it as a run file says: `local/.venv/bin/python -m tests.corpus RUN.toml`
(`tests/corpus/run_config.py` lists a run file's keys, `tests/corpus/runs/` has some). A run names
its corpora ([`corpora.toml`](../tests/corpus/corpora.toml)'s, or any directory), the constricter
versions (releases, this checkout, or another checkout's by its Python), and its steps: a check at
every level, each fix on a copy (every file still compiling, and nothing left for a second pass),
`--infer-with` each type checker, the census, coverage, a check timed in one process and with every
CPU (by [`hyperfine`](https://github.com/sharkdp/hyperfine) where it's installed, which also counts
each run's instructions, a far steadier measure than its seconds), and one that `py-spy` samples
from outside, with constricter's slowest modules and functions. CI runs the check, the fix and the
profile, each in its own job (the profile's never fails the run), against the standard library and
the clones, at their pinned tags, of `django`, `sqlalchemy`, `pydantic` and `pandas` (a web
framework, an ORM, a runtime-validation library and a data library; their dependencies' types come
from the pinned `corpus` dependency group), and against pure Python 2 (Twisted 12.3.0) and pip
20.3.4 (2/3-era code whose `# type:` comments sit in modules with Python 2 `__future__` imports),
hash-pinned sdists `tests/corpus/corpus_sources.py` fetches, since neither installs as a dependency.

For a corpus with a suite (cloned at its pinned tag, with its test dependencies as its CI installs
them, in `local/corpus-suites/`), three more steps run on its checkout with each fix's patch
applied: `tests`, the package's own tests as released and after each fix; `types`, its own type
checker as its CI runs it, each new error traced to the fix behind it, a certain one, a likely guess
or another guess; and `traced`, its tests under a witness that holds each fixed binding's value to
its annotation, then a fix by their trace (`python -m constricter.trace`, where pytest runs them, or
a script the suite names does in one process: Django's `runtests.py`). A fixed run whose tests
differ is run again, with the released tests: only what it fails both times and no released run did
is the fix's, and a test `corpora.toml` names under the suite's `differs`, with why, is reported
apart. They need `git`, `uv`, a C compiler, Rust (a default toolchain: `rustup default stable`) and
the network, once.

Each execution writes a folder of its own under `local/corpus-runs/`, named by the run's label and
the time: the run file, a record for each corpus, version and step, and `report.json`, `report.md`
and `tables/*.csv` made from them. `--resume FOLDER` carries on a stopped run, and `--only NAME`
keeps one to a corpus. Each step is a process of its own, started once the CPUs it's expected to
keep busy and the memory it's expected to hold are free: what it took in the last run under the same
output, which its record keeps (`tests/corpus/sizing.py`; `cpus` and `memory` in the run file share
out less than the machine has). A step that fails leaves its traceback under `logs/`; the run exits
1 for it, and for anything a fix broke.

A run file with a `[publish]` table records a section per version in [`docs/RUNS.md`](RUNS.md):
offences per code, errors and warnings at each level, fixes, guesses, anything a fix broke, and the
share of bindings typed before and after fixing (by this checkout's `--coverage`). Its `versions`
may name releases too, each installed in an environment of its own. With `section`, it records that
one section of the whole run instead: `tests/corpus/runs/super.toml` and `mega.toml` ask every step
of the seven corpora and of the 40 more packages, and write RUNS.md's `Super corpora` and
`Mega corpora` sections, with the machine they ran on. Run both before a release, outside a sandbox.

On a pull request that touches what `--fix` does, the Corpus coverage workflow comments with
pydantic's share of bindings typed as released, after `--fix`, and after `--fix --unsafe-fixes`,
beside the base branch's (a run of `tests/corpus/runs/coverage.toml`, with both), and edits the
comment on each push.

`local/.venv/bin/python -m tests.corpus.corpus_untyped` counts what `--fix` still can't type on the
same corpora, and why: each untyped binding by the statement that binds it and the shape of its
value, in annotated functions or not, and each call through an import by where it comes from. It
prints the tables [ROADMAP.md](ROADMAP.md) sizes its items by; `--rows FILE` also writes every
binding, as JSON lines.

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
| pylint             | `too-many-instance-attributes` on `Module` and `Outside`                           | Each is a record of one file's tables, a field a table, built by keyword.                                             |
| typos              | the word `astroid`                                                                 | A real package name.                                                                                                  |
| typos              | `constricter/fix/tables/*.json`, `stdlib_tables/partial.json`                      | Generated from typeshed: the standard library's own names, which typos takes for misspellings.                        |
| harden-runner      | `egress-policy: audit` on macOS and Windows, and in the weekly external-link check | harden-runner supports only audit on GitHub's macOS and Windows runners; external links can go anywhere.              |
| reuse              | `reuse lint` not run (the files still comply: `REUSE.toml` covers them)            | No recent release ships a wheel for Python 3.11+, so installing it builds from source with an unpinned `poetry-core`. |
| zizmor             | `self-repository` (`.github/zizmor.yml`)                                           | Scorecard reads the `$/` form it wants as an unpinned third-party action, so local actions stay `./`.                 |
