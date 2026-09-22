# constricter

Lint rule `LVA001`: every local variable is annotated where it's first bound. Ships as a flake8
plugin, a pylint plugin and a standalone command (for ruff, which loads no plugins).

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
    for item in items:  # ok: no annotated form
        result += item
    return result
```

## Rule

Checked per function body, including methods and nested functions. Module and class bodies are
not checked.

- The first binding by `=`, unpacking, `:=` or `with ... as` must be `name: T = ...`, or follow a
  bare `name: T`.
- Exempt: `for` targets, comprehensions, `except ... as`, `match` captures, imports, `def`/`class`,
  `type` aliases, parameters, `global`/`nonlocal`, and `_`.
- Statements are read in source order.

Python 3.12+, no runtime dependencies.

## Use

| Tool   | Setup                                                  | Reports                        | Suppress                                       |
| ------ | ------------------------------------------------------ | ------------------------------ | ---------------------------------------------- |
| CLI    | `constricter [PATH...] [--exclude GLOB] [-q]`          | `LVA001`                       | `# noqa: LVA001`                               |
| flake8 | install it (on by default)                             | `LVA001`                       | `# noqa: LVA001`                               |
| pylint | `load-plugins = ["constricter.pylint_plugin"]`         | `C9101` / `unannotated-local-variable` | `# pylint: disable=unannotated-local-variable` |
| ruff   | run the CLI after ruff; set `lint.external = ["LVA"]` | `LVA001`                       | `# noqa: LVA001`                               |

Without `lint.external`, ruff flags `# noqa: LVA001` (RUF102) and `--fix` deletes it.

The CLI defaults to `.` and skips hidden dirs, `__pycache__`, `venv`, `site-packages`, `build`,
`dist` and `node_modules`. Exit codes: `0` clean, `1` offences, `2` unreadable/unparseable file.

Not on PyPI yet:

```bash
pip install "python-constricter @ git+https://github.com/ivylikethevine/python-constricter@v0.1.0"
```

pre-commit, after ruff's hooks:

```yaml
- repo: https://github.com/ivylikethevine/python-constricter
  rev: v0.1.0
  hooks:
    - id: constricter
```

## Development

```bash
python -m venv local/.venv
local/.venv/bin/pip install --require-hashes -r requirements-dev.txt
local/.venv/bin/pip install --no-deps --no-build-isolation -e .
```

Checks (as CI runs them): `ruff check .`, `ruff format --check .`, `basedpyright`,
`constricter src tests`, `pytest --cov` (100% branch coverage). Everything generated goes in
`local/`.

After editing the `dev` extra, regenerate the lock:

```bash
uv pip compile pyproject.toml --extra dev --universal --python-version 3.12 --generate-hashes -o requirements-dev.txt
```

## Roadmap

Done:

- **ci.yml** runs on pushes and PRs. Lint job: ruff, basedpyright, the rule on itself, and the
  pre-commit hook. Test job: pytest on Linux, macOS and Windows × Python 3.12–3.14. Build job:
  sdist and wheel, `twine check`, a wheel smoke test, and upload as an artifact.
- **security.yml** runs on pushes, PRs and weekly: CodeQL (Python and Actions), zizmor (pedantic),
  actionlint (kjanat fork) and pip-audit on the lock.
- **release.yml** runs on `v*` tags: CI, a check that the tag matches the version, then build
  provenance attestation.
- **Pinning:** actions are pinned by SHA, Python dependencies by hash, and actionlint by sha256.
  Dependabot updates the first two weekly.

To publish:

1. Add a PyPI trusted publisher and a `pypi` environment, then a `publish` job in release.yml
   (`pypa/gh-action-pypi-publish`, `id-token: write`).
2. Create a GitHub release from the tag, with the dists and attestations attached.
3. Add a ruleset that requires the CI and Security checks on `main` and protects `v*` tags.
4. Once the repo is public: OpenSSF Scorecard and `actions/dependency-review-action`. CodeQL
   uploads and attestations also need a public repo or GitHub Advanced Security.
5. Add a CI check that `requirements-dev.txt` matches `pyproject.toml`.
