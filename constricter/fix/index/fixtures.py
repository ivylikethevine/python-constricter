# SPDX-License-Identifier: MIT
"""Pytest fixtures' values, for the tests that take them as parameters.

A test (or a fixture) names the fixtures it wants as its parameters, which no call passes: pytest
finds each in the test's module, then in the `conftest.py` of each package above it, the nearest
first. A fixture's value is what its function returns, or yields: its declared return, or the one
its `return`s give (see `constricter.fix.values.returned`). A parameter so typed is a guess
(`fixture`): a plugin's fixture, or one a `conftest.py` out of the checked files defines, may be
the one pytest takes. A `conftest.py` in a directory that isn't a package is looked in last, if it's
the only checked file of that name and the test's directory, or its top package's, is its own or
under it: a module's name says nothing of where it is, so one of several can't be told apart.
"""

import ast
from pathlib import Path
from typing import Final

from constricter.fix.core.known import Guarded, Passed
from constricter.fix.index import project
from constricter.fix.index.modules import SUFFIX, Index, Module

KIND: Final = "fixture"  # the guessing mechanism (`FIX_KINDS`)
_CONFTEST: Final = "conftest"
_DOT: Final = "."
# What a generator fixture declares it returns: its value is the first argument.
_YIELDING: Final = frozenset({"Iterator", "Generator", "Iterable", "AsyncIterator", "AsyncGenerator"})


def providers(catalog: Index, name: str) -> list[Module]:
    """Find the modules whose fixtures module `name`'s tests can take, the nearest first.

    Returns:
      It, then its packages' `conftest`s, those `catalog` has, then the one outside any package
      (see `_above`).

    """
    parts: list[str] = name.split(_DOT)
    names: list[str] = [
        name,
        *(_DOT.join([*parts[:depth], _CONFTEST]) for depth in range(len(parts) - 1, 0, -1)),
        *([_CONFTEST] if _above(catalog, name) else []),
    ]
    return [catalog.modules[each] for each in dict.fromkeys(names) if each in catalog.modules]


def _above(catalog: Index, name: str) -> bool:
    """Check whether the `conftest.py` outside any package is one module `name`'s tests take fixtures from.

    Returns:
      Whether it's the only checked file named so, in the directory of `name`'s file, or of its top
      package, or in one above it.

    """
    target: Module | None = catalog.modules.get(name)
    flat: Module | None = catalog.modules.get(_CONFTEST)
    if target is None or flat is None or not (target.folder and flat.folder) or _CONFTEST in catalog.repeated:
        return False
    top: Path = Path(target.folder).joinpath(*[".."] * name.count(_DOT)).resolve()
    return Path(flat.folder) in {top, *top.parents}


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
        for fixture in module.fixtures.keys() - found.keys():  # a nearer one of the name is the one taken
            found[fixture] = _typed(catalog, target, module, fixture, guarded)
    return {fixture: typed for fixture, typed in found.items() if typed is not None}


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
