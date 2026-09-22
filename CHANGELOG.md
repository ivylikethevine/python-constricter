# Changelog

Notable changes, newest first. Each release's full notes are generated from its merged pull requests
(grouped by `.github/release.yml`) on its
[GitHub release](https://github.com/ivylikethevine/python-constricter/releases).

## Unreleased

- `--fix` infers method calls on an already-typed local: a method of a class defined in the same
  module (its declared return type; a bare `Self` return is the class itself), and
  `list`/`set`/`dict` methods whose return is the receiver's own element type (`pop`, `setdefault`,
  `get` as `V | None`, `popitem`, `copy`). Both are certain fixes, not `--unsafe-fixes` guesses.
- `--fix` infers more: `not x` (always `bool`), calls to builtins with a fixed return type (`len`,
  `isinstance`, `str`, ...), a plain `x = y` copying `y`'s already-known type (its annotation, an
  earlier fix, or an annotated parameter), a subscript of an already-typed local (`container[key]`,
  its element type; a slice, the same type back), an attribute of one (`obj.attr`, a class-level
  annotated attribute of a class defined in the same module, or a `self.x: T = ...` annotated
  anywhere in one of its methods), a method's own `self` typed as its class, and a call to a
  `str`/`bytes` method whose return type doesn't depend on its arguments (`strip`, `split`,
  `startswith`, `encode`, `decode`, ...) on an already-typed local.
- **LVA007**: a name annotated again with the type it already has, in the same straight-line block
  (an `if`'s two arms, a `try`'s body and its `except`s, ... are compared separately, not against
  each other). A warning at every level, an error at `suffocate`.
- `--exclude` globs also match a directory name during a directory walk (like the built-in skip list
  for `__pycache__`, `venv`, hidden directories, ...), not just a whole path or file name.
- Enum bases and factory calls (`Enum`, `NamedTuple`, `TypeVar`, ...) are recognised by where
  they're imported from, in addition to their bare name, so an aliased or re-exported one is still
  found.
- `project.calls` finds a module/submodule import by name lookup instead of scanning every indexed
  module (`project.index` now returns a `project.Index`, not a plain `dict`).
- `tests/corpus.py` and `tests/corpus_fix.py` (checking and `--fix`-ing a large real codebase) run
  in CI's Corpus job, against the runner's Python standard library and, from a new pinned `corpus`
  dependency group, `requests`, `flask`, `django` and `sqlalchemy`.
- Fix: `--fix` could corrupt a line (and crash) if an offence's fix landed inside a multi-byte
  character; that one offence is now left unfixed instead. Found by the new Corpus job, on the
  Python 3.11 standard library.
- First release, 0.2.0: `LVA001`–`LVA006`, the `relaxed` to `suffocate` levels, a flake8 plugin, a
  pylint plugin and the `constricter` command (with `--fix`, `--diff`, `--explain`, `--select`,
  `--ignore`, `--statistics` and text, JSON, GitHub and SARIF output), configured from
  `[tool.constricter]` in `pyproject.toml`. Python 3.11+. Also baselines (`--write-baseline`,
  `--baseline`), Jupyter notebooks, a GitHub Action, `--jobs`, per-path levels, and JSON with
  comments wherever constricter reads JSON. `--coverage` reports annotation coverage; standard
  input, `gitlab`, `junit` and `rdjson` output, `--unsafe-fixes`, per-file ignores, `--exit-zero`
  and `--output-file`; `--fix` edits notebook cells; releases carry SLSA Build Level 3 provenance
  (GitHub artifact attestations); `--fix` types calls to functions in other checked files.
  `check_source`, `check_tree` and `annotation_coverage` take their options as one `Checks`.
