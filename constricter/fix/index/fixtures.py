# SPDX-License-Identifier: MIT
"""Pytest fixtures' values, for the tests that take them as parameters.

A test (or a fixture) names the fixtures it wants as its parameters, which no call passes: pytest
finds each in the test's module, then in the `conftest.py` of each package above it, the nearest
first. A fixture's value is what its function returns, or yields: its declared return, or the one
its `return`s give (see `constricter.fix.values.returned`). A parameter so typed is a guess
(`fixture`): a plugin's fixture, or one a `conftest.py` out of the checked files defines, may be
the one pytest takes. A `conftest.py` in a directory that isn't a package is looked in next, by
where it is: the test's directory's, or its top package's, then each one's above it. Pytest's own
come last (`capsys`, `monkeypatch`, `caplog`), read from its installed modules where a checked file
imports `pytest`.
"""

import ast
from collections.abc import Mapping
from pathlib import Path
from typing import Final

from constricter.fix.core.known import Guarded, Passed
from constricter.fix.index import project
from constricter.fix.index.modules import CONFTEST, SUFFIX, Index, Module

KIND: Final = "fixture"  # the guessing mechanism (`FIX_KINDS`)
_DOT: Final = "."
_PYTEST: Final = "_pytest"  # the package pytest defines its own fixtures in
# pytest's own fixtures whose value is a standard-library class's instance, each with its class:
# typed without the index, by an import the module has or one added (see `rules.calls`).
STDLIB_OWN: Final = {"tmp_path": "pathlib.Path"}
# What a generator fixture declares it returns: its value is the first argument.
_YIELDING: Final = frozenset({"Iterator", "Generator", "Iterable", "AsyncIterator", "AsyncGenerator"})


def providers(catalog: Index, name: str) -> list[Module]:
    """Find the modules whose fixtures module `name`'s tests can take, the nearest first.

    Returns:
      It, then its packages' `conftest`s, those `catalog` has, then those outside any package (see
      `_above`), then pytest's own modules.

    """
    parts: list[str] = name.split(_DOT)
    names: list[str] = [
        name,
        *(_DOT.join([*parts[:depth], CONFTEST]) for depth in range(len(parts) - 1, 0, -1)),
    ]
    found: list[Module] = [catalog.modules[each] for each in dict.fromkeys(names) if each in catalog.modules]
    target: Module | None = catalog.modules.get(name)
    return [*found, *(each for each in _above(catalog, name) if each is not target), *_own(catalog)]


def _above(catalog: Index, name: str) -> list[Module]:
    """Find the `conftest.py`s outside any package that module `name`'s tests take fixtures from.

    Returns:
      Those in the directory of `name`'s file, or of its top package, and in each one above it, the
      nearest first.

    """
    target: Module | None = catalog.modules.get(name)
    folder: str = "" if target is None else target.folder
    top: Path = Path(folder).joinpath(*[".."] * name.count(_DOT)).resolve()
    folders: list[str] = [str(each) for each in (top, *top.parents)] if folder else []
    flat: Module | None = catalog.modules.get(CONFTEST)
    if flat is not None and CONFTEST not in catalog.repeated:  # the index's: it has what it returns
        return [flat] if flat.folder in folders else []
    return [catalog.conftests[each] for each in folders if each in catalog.conftests]


def _own(catalog: Index) -> list[Module]:
    """Find pytest's modules that define its own fixtures, among the installed ones `catalog` has.

    Returns:
      Them, by name.

    """
    return [
        module
        for name, module in sorted(catalog.modules.items())
        if module.installed and module.fixtures and name.partition(_DOT)[0] == _PYTEST
    ]


def needed(catalog: Index, name: str) -> set[str]:
    """Name the other modules whose fixtures module `name` can take: checked before it, their types are known.

    Returns:
      Them.

    """
    return {module.name for module in providers(catalog, name) if module.fixtures} - {name}


def visible(catalog: Index, path: Path, guarded: dict[str, Guarded]) -> dict[str, Passed]:
    """Type the fixtures the file at `path` can take, as it can write each type (see `project.spelled_in`).

    `guarded` records the names those types need imported for type checking.

    Returns:
      Each typed fixture's value's type, and what it rests on, by its name; nothing for a file
      `catalog` doesn't have.

    """
    target: Module | None
    if path.suffix != SUFFIX or (target := catalog.modules.get(project.module_name(path))) is None:
        return {}
    if target.name in catalog.repeated:  # another file's module, maybe: its `conftest.py`s aren't this one's
        return {}
    found: dict[str, Passed | None] = {}
    module: Module
    for module in providers(catalog, target.name):
        fixture: str
        # A nearer one of the name is the one taken; pytest's of a standard-library class is `STDLIB_OWN`'s.
        skipped: set[str] = found.keys() | (STDLIB_OWN.keys() if module.installed else set())
        for fixture in module.fixtures.keys() - skipped:
            found[fixture] = _typed(catalog, target, module, fixture, guarded)
    return {fixture: typed for fixture, typed in found.items() if typed is not None}


def attributes(seeds: Mapping[str, Passed]) -> frozenset[str]:
    """Name the attributes fixtures' types are written with: `MonkeyPatch`, in `pytest.MonkeyPatch`.

    Returns:
      Them.

    """
    return frozenset(
        node.attr
        for typed, _ in seeds.values()
        for node in ast.walk(ast.parse(typed, mode="eval"))
        if isinstance(node, ast.Attribute)
    )


def _typed(
    catalog: Index,
    target: Module,
    module: Module,
    fixture: str,
    guarded: dict[str, Guarded],
) -> Passed | None:
    """Type one of `module`'s fixtures' value, as `target` can write it.

    Returns:
      The type, and what it rests on; or `None`.

    """
    declared: str | None = module.held[fixture].returns if fixture in module.held else None
    annotation: str | None = declared or module.returned.calls.get(fixture)
    if annotation is not None and module.fixtures[fixture]:
        annotation = _yielded(annotation)
    written: str | None = (
        None if annotation is None else project.spelled_in(catalog, target, module, annotation, guarded)
    )
    if written is None:
        return None
    rests: frozenset[str] = frozenset() if declared else module.returned.guesses.get(fixture, frozenset())
    return written, frozenset({KIND}) | rests


def _yielded(annotation: str) -> str | None:
    """Read what a generator's declared type says it yields: `Frame` of an `Iterator[Frame]`.

    Returns:
      It, or `None` for anything else.

    """
    head: ast.expr
    inner: ast.expr
    match ast.parse(annotation, mode="eval").body:
        case ast.Subscript(value=ast.Name() | ast.Attribute() as head, slice=inner) if (
            ast.unparse(head).rpartition(_DOT)[2] in _YIELDING
        ):
            return ast.unparse(inner.elts[0] if isinstance(inner, ast.Tuple) else inner)
        case _:
            return None
