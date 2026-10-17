# Bump all versions to 0.4.0

## Context

The user asked to bump every version string from 0.3.9 to 0.4.0, ahead of a release. The package
version is `__version__` in `constricter/__init__.py` (hatch reads it: `[tool.hatch.version]` in
`pyproject.toml`), and the docs pin the release tag in pre-commit and GitHub Action examples. The
previous bump (commit `8aaaffb`, 0.3.8 → 0.3.9) touched exactly these four files; `uv.lock` carries
no version for the editable package, and `docs/CHANGELOG.md` keeps a single `## Unreleased` heading
(release notes come from merged PRs), so neither changes.

## Edits (0.3.9 → 0.4.0, 7 occurrences)

| File | Line | Text |
| --- | --- | --- |
| `constricter/__init__.py` | 28 | `__version__ = "0.3.9"` → `"0.4.0"` |
| `action.yml` | 15 | description's example release `` `0.3.9` `` → `` `0.4.0` `` |
| `README.md` | 260 | pre-commit `rev: v0.3.9` → `rev: v0.4.0` |
| `docs/INTEGRATIONS.md` | 12, 26 | pre-commit `rev: v0.3.9` → `rev: v0.4.0` |
| `docs/INTEGRATIONS.md` | 83, 95 | `uses: ivylikethevine/python-constricter@v0.3.9` → `@v0.4.0` |

Left alone on purpose: run labels like `0.3.9-rc.1` in `docs/CHANGELOG.md`, `docs/ROADMAP.md`,
`docs/RUNS.md`, `docs/LIKELY.md` and `scratch/run_eta.py` (they name past corpus runs, not the
package version); the `0.3.9` match in `.github/package-lock.json` (an npm package's version).

## Verification

- `git grep -nE '\bv?0\.3\.9\b'` shows only the historical run labels above.
- `local/.venv/bin/python -c 'import constricter; print(constricter.__version__)'` prints `0.4.0`
  (editable install reads the file directly).

## Not done here (user's call)

`docs/CONTRIBUTING.md` lines 10-13 say a release bump is recorded in `docs/RUNS.md` by running
`local/.venv/bin/python -m tests.corpus tests/corpus/runs/release.toml` and committing it with the
bump. That is a full corpus run, which the user launches themself; the 0.3.9 bump commit did not
include it either. Nothing is committed or tagged: pushing a `v0.4.0` tag triggers the release.
