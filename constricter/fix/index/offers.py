"""`--infer-with`: what a hint may name that the file doesn't bind where its annotations run.

A hint is text, and a name in it may not be a type: basedpyright shows a value that is a module by
the module's name, and a generic class without its arguments when it doesn't know them. So a name
is taken only for a class or a type alias the index of checked files and installed packages
defines: `own`, for what the file imports under `if TYPE_CHECKING:`; `vetted`, for what a hint's
edits would import (the standard library's are `hinted`'s to judge, by its tables).
"""

import ast
import re
from collections.abc import Mapping
from pathlib import Path
from typing import Final, NamedTuple, TypeAlias, cast

from constricter.empty import Empty
from constricter.fix.core.known import Guarded, Hints, Offered, Origin
from constricter.fix.index import project
from constricter.fix.index.modules import PACKAGE, module_at
from constricter.fix.index.origins import absolute
from constricter.fix.index.stubs.atoms import private_name
from constricter.fix.libraries import stdlib
from constricter.fix.values.called import ENUM_FACTORIES, TYPING_FACTORIES

_Defined: TypeAlias = tuple[str, str]  # where the index defines a class: its module, and its name there
# The standard library's classes the tables leave out, as they make classes rather than instances.
_UNTABLED: Final = {
    "enum": frozenset(ENUM_FACTORIES),
    "typing": frozenset(TYPING_FACTORIES),
    "typing_extensions": frozenset(TYPING_FACTORIES),
}


class Own(NamedTuple):
    """The classes and aliases a file imports for type checking alone (`guarded`), and the generic ones."""

    # A plain `dict`, not a `MappingProxyType`: the CLI's worker processes are sent it, pickled.
    guarded: Mapping[str, Guarded] = Empty()
    generics: frozenset[str] = frozenset()


def own(catalog: project.Index, path: Path) -> Own:
    """Find the classes the file at `path` imports under a top-level `if` (`if TYPE_CHECKING:`) alone.

    Returns:
      Those the index or the standard library's tables define; none for a file `catalog` doesn't have.

    """
    target: project.Module | None
    if (target := module_at(catalog, path)) is None:
        return Own()
    found: dict[str, Guarded] = {}
    generics: set[str] = set()
    name: str
    origin: Origin
    for name, origin in target.guarded.items():
        generic: bool | None = _class(catalog, origin)
        if generic is not None and name not in target.names:
            found[name] = Guarded(origin, None)
            if generic:
                generics.add(name)
    return Own(found, frozenset(generics))


def vetted(catalog: project.Index, path: Path, hints: tuple[Hints, ...]) -> tuple[Hints, ...]:
    """Drop the edits of the file at `path`'s hints that import what isn't a class, or a generic one bare.

    And those writing a name the file binds that a module it imports whole has a class of too (see
    `_ambiguous`).

    Returns:
      The hints, without them: such a hint is judged by what it shows alone.

    """
    if not any(found.offered for found in hints):
        return hints
    module: tuple[str, bool] = (project.module_name(path), path.stem == PACKAGE)
    target: project.Module | None = catalog.modules.get(module[0])
    checking: Mapping[str, Origin] = Empty() if target is None else target.guarded
    found: dict[str, _Defined | None] = {name: _defined(catalog, origin) for name, origin in checking.items()}
    guarded: dict[str, _Defined] = {name: defined for name, defined in found.items() if defined is not None}
    return tuple(
        _shared(
            catalog,
            module,
            found._replace(
                offered={
                    where: offered
                    for where, offered in found.offered.items()
                    if _sound(catalog, module, offered, found.types.get(where, ""))
                    and not _ambiguous(catalog, target, offered)
                },
            ),
            guarded,
        )
        for found in hints
    )


def _shared(
    catalog: project.Index,
    module: tuple[str, bool],
    found: Hints,
    guarded: Mapping[str, _Defined],
) -> Hints:
    """Import one class by one statement in all of a file's hints' edits, the first's, as it's written once.

    A checker's edits may import a class by any module that re-exports it (`pint`'s `Unit`, then
    `pint.registry`'s): the first made the second's an import of a name taken, and its fix waited
    for a second pass, which reads the name as the file's. A hint whose edits import another class
    by a name the file imports for type checking (`guarded`, each where it's defined) is
    dropped: judged by what it shows, it would be taken for that one. Only a class the index
    defines: it doesn't follow the standard library's re-exports (`typing`'s `Callable`).

    Returns:
      The hints so.

    """
    first: dict[str, tuple[_Defined, str]] = {}  # each name's class, and its statement
    types: dict[tuple[int, int], str] = dict(found.types)
    offered: dict[tuple[int, int], Offered] = {}
    where: tuple[int, int]
    each: Offered
    for where, each in sorted(found.offered.items()):
        statements: list[str] = []
        statement: str
        for statement in each.imports:
            name: str
            origin: Origin
            name, origin = _bound(module, statement)
            defined: _Defined | None
            if (defined := _defined(catalog, origin)) is None:
                statements.append(statement)
                continue
            if name in guarded and guarded[name] != defined:
                break
            was: tuple[_Defined, str] = first.setdefault(name, (defined, statement))
            statements.append(was[1] if was[0] == defined else statement)
        else:
            offered[where] = each._replace(imports=tuple(statements))
            continue
        _ = types.pop(where, None)
    return found._replace(types=types, offered=offered)


def imported(path: Path, hints: tuple[Hints, ...]) -> dict[str, Guarded]:
    """Find what the file at `path`'s vetted hints' edits import for type checking alone.

    For `linked.same`: a class an edit imports (`DataFrame`, from `pandas.core.frame`) is a spelling
    of it beside the file's own (`pd.DataFrame`) in the pass that writes the import, as in the next.

    Returns:
      Each name one statement binds in every edit, with it.

    """
    module: tuple[str, bool] = (project.module_name(path), path.stem == PACKAGE)
    found: dict[str, Guarded] = {}
    clashing: set[str] = set()
    statement: str
    for statement in {
        statement for each in hints for offered in each.offered.values() for statement in offered.imports
    }:
        name: str
        origin: Origin
        name, origin = _bound(module, statement)
        if name in found:
            clashing.add(name)
        found[name] = Guarded(origin, statement)
    return {name: guarded for name, guarded in found.items() if name not in clashing}


def _bound(module: tuple[str, bool], statement: str) -> tuple[str, Origin]:
    """Read what a `from` import of a hint's edits binds, from the hinted file's `module`.

    Returns:
      The name it binds, and what that is.

    """
    node: ast.ImportFrom = cast("ast.ImportFrom", ast.parse(statement).body[0])
    alias: ast.alias = node.names[0]
    return alias.asname or alias.name, (
        absolute(module[0], node.module, node.level, is_package=module[1]),
        alias.name,
    )


def _defined(catalog: project.Index, origin: Origin) -> _Defined | None:
    """Find where the index defines a class or a type alias, through re-exports.

    Returns:
      Its module and its name there; `None` where it doesn't.

    """
    found: tuple[project.Module, str] | None = project.type_definition(catalog.modules, origin)
    return None if found is None else (found[0].name, found[1])


def _sound(catalog: project.Index, module: tuple[str, bool], offered: Offered, shown: str) -> bool:
    """Check that each import of a hint's edits names a class, and no generic one written bare.

    `module`: the hinted file's module name, and whether it's a package's `__init__`; `shown`: what
    the hint shows, which may write a class bare that its edit's spelling doesn't.

    Returns:
      Whether they do; an `import m`, which names no class, never does, nor an import from an
      installed package's private module (`numpy._core`), which its next release may move.

    """
    statement: str
    for statement in offered.imports:
        try:
            node: ast.stmt = ast.parse(statement).body[0]
        except SyntaxError:  # from a file no import can name (`v3.0.0.c.py`)
            return False
        if not isinstance(node, ast.ImportFrom):
            return False
        alias: ast.alias = node.names[0]
        origin: Origin = (absolute(module[0], node.module, node.level, is_package=module[1]), alias.name)
        if origin[0].partition(".")[0] in project.STDLIB:
            continue
        lone: re.Pattern[str] = re.compile(rf"(?<![\w.]){re.escape(alias.asname or alias.name)}(?![\w\[])")
        generic: bool | None = _class(catalog, origin)
        bare: bool = bool(generic and (lone.search(offered.text) or lone.search(shown)))
        if generic is None or bare or _private(catalog, origin[0]):
            return False
    return True


def _ambiguous(catalog: project.Index, target: project.Module | None, offered: Offered) -> bool:
    """Check whether a hint's edit writes a name the file binds and a module it imports whole has a class of.

    basedpyright shows `enum.Enum` as `Enum`, and its edit writes it so, where the file defines an
    `Enum` of its own (sqlalchemy's `sqltypes.py`, importing `enum`): which the checker meant can't
    be told. A name the edit imports itself is the edit's.

    Returns:
      Whether one is.

    """
    if target is None:
        return False
    try:
        tree: ast.Expression = ast.parse(offered.text, mode="eval")
    except SyntaxError:
        return False
    added: set[str] = set()
    statement: str
    for statement in offered.imports:  # each parses: `vetted` asks `_sound` first
        added.update(
            (alias.asname or alias.name).partition(".")[0]
            for node in ast.parse(statement).body
            if isinstance(node, ast.Import | ast.ImportFrom)
            for alias in node.names
        )
    wholes: list[str] = [origin[0] for origin in target.names.values() if origin[1] is None]
    written: set[str] = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)} - added
    return any(
        name in target.names
        and any(
            (whole, name) != target.names[name]
            and (_class(catalog, (whole, name)) is not None or name in _UNTABLED.get(whole, ()))
            for whole in wholes
        )
        for name in written
    )


def _private(catalog: project.Index, name: str) -> bool:
    """Check whether module `name` is an installed package's private one.

    Returns:
      Whether it is.

    """
    module: project.Module | None = catalog.modules.get(name)
    return module is not None and module.installed and private_name(name)


def _class(catalog: project.Index, origin: Origin) -> bool | None:
    """Find whether `origin` is a class or a type alias: an indexed module's (through re-exports).

    Or a class of the standard library's.

    Returns:
      Whether it's generic, missing its arguments written bare; `None` if it's neither, to anyone's
      knowledge.

    """
    defined: tuple[project.Module, str] | None
    if (defined := project.definition(catalog.modules, origin, project.CLASS)) is not None:
        return defined[1] in defined[0].generics
    if (defined := project.definition(catalog.modules, origin, project.ALIAS)) is not None:
        return defined[0].aliases[defined[1]]
    path: str = f"{origin[0]}.{origin[1]}"
    return stdlib.needs_arguments(path) if stdlib.defines_class(path) else None
