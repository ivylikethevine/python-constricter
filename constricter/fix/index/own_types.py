# SPDX-License-Identifier: MIT
"""A checked file's classes in its overloads' parameters, and where each class a calling file names is from.

A parameter typed as nothing but checked files' classes (`frame: DataFrame`), or as an iterable of
them (`objs: Iterable[DataFrame] | Mapping[K, DataFrame]`), takes an argument by its class's
lineage: its own path and its bases', through the checked files, as an installed class's is
matched (see `constricter.fix.index.stubbed`). `concat([df, df])` then picks the overload taking
`DataFrame`s, and not the one taking `Series`.
"""

import ast
from collections.abc import Callable, Iterator, Mapping, Sequence
from pathlib import Path
from typing import Final, TypeAlias

from constricter.fix.core.known import Guarded, Origin
from constricter.fix.core.signatures import OWN, OWN_ELEMENTS, Accepts
from constricter.fix.index import plain, project
from constricter.fix.index.atoms import BUILTINS_MODULE, CLASS, Atom, Scope
from constricter.fix.index.modules import SUFFIX, Index, Module, module_name
from constricter.fix.libraries import stdlib
from constricter.fix.values import classvars

_NONE_ATOM: Final = "none"
_LITERAL_ATOM: Final = "literal"
_UNFOLLOWED: Final = "?"  # a lineage's base that can't be followed
_DEPTH: Final = 8  # how many classes a line of bases is followed through
# Generic classes of one argument whose instance a builtin sequence or set argument is, by its elements.
_ITERABLES: Final = frozenset(
    {"Iterable", "Iterator", "Collection", "Sequence", "MutableSequence", "list", "List"}
    | {"set", "Set", "AbstractSet", "frozenset", "FrozenSet"},
)
# Those a builtin sequence or set isn't: they neither take one nor say what its elements are.
_MAPPINGS: Final = frozenset({"Mapping", "MutableMapping", "dict", "Dict"})
_Atoms: TypeAlias = Callable[[ast.expr, Scope], Iterator[Atom]]


def accept(modules: Mapping[str, Module], atoms: Sequence[Atom], read: _Atoms, found: Accepts) -> None:
    """Add which checked files' classes a parameter takes to `found`, where it takes nothing else.

    `atoms`: its annotation's members; `read`: what reads a type argument's. `OWN`: the classes
    (each `module.Class`) an argument must be one of, for a parameter whose every member is one,
    `None` or a builtin class; `OWN_ELEMENTS`: those a builtin sequence's or set's elements must
    be, for one whose every member is an iterable of such classes, a mapping or `None`. Neither
    where a member could take anything else.
    """
    direct: list[str] | None
    if direct := _classes(modules, atoms):
        found[OWN] = direct
    elements: list[str] = []
    atom: Atom
    for atom in atoms:
        name: str = atom.origin[1] or ""
        if atom.kind == _NONE_ATOM or (atom.kind == CLASS and name in _MAPPINGS):
            continue
        inner: list[str] | None = (
            _classes(modules, list(read(atom.args[0], atom.scope)))
            if atom.kind == CLASS and name in _ITERABLES and len(atom.args) == 1 and atom.scope is not None
            else None
        )
        if not inner:
            return
        elements.extend(inner)
    if elements:
        found[OWN_ELEMENTS] = sorted(set(elements))


def _classes(modules: Mapping[str, Module], atoms: Sequence[Atom]) -> list[str] | None:
    """Name the checked files' classes a union's members are, where each is one, `None` or a builtin class.

    Returns:
      Their paths, sorted; `None` where a member is anything else (an alias left unread, a type
      variable, another package's class).

    """
    found: set[str] = set()
    atom: Atom
    for atom in atoms:
        module: Module | None = modules.get(atom.origin[0])
        if (
            atom.kind == CLASS
            and module is not None
            and not module.installed
            and atom.origin[1] in module.bases
        ):
            found.add(f"{atom.origin[0]}.{atom.origin[1]}")
        elif atom.kind not in {_NONE_ATOM, _LITERAL_ATOM} and not (
            atom.kind == CLASS and atom.origin[0] == BUILTINS_MODULE and not atom.args
        ):
            return None
    return sorted(found)


def lineages(catalog: Index, path: Path, guarded: Mapping[str, Guarded]) -> dict[str, tuple[str, ...]]:
    """Find where each checked file's class the file at `path` names comes from, by how it names it.

    Its own classes, those it imports (for type checking too, `guarded`), and those of the modules
    it imports.

    Returns:
      Each one's path and its bases', through the checked files, `?` last where a base can't be
      followed (another package's, a computed one); none for a file `catalog` doesn't have.

    """
    target: Module | None
    if path.suffix != SUFFIX or (target := catalog.modules.get(module_name(path))) is None:
        return {}
    modules: dict[str, Module] = catalog.modules
    found: dict[str, tuple[str, ...]] = {
        name: tuple(dict.fromkeys(_line(modules, f"{target.name}.{name}", _DEPTH))) for name in target.bases
    }
    names: dict[str, Origin] = {**{name: each.origin for name, each in guarded.items()}, **target.names}
    key: str
    defined: tuple[Module, str]
    for key, defined in project.spelled_classes(catalog, target, (names, target.attributes), set()):
        if not defined[0].installed:
            found[key] = tuple(dict.fromkeys(_line(modules, f"{defined[0].name}.{defined[1]}", _DEPTH)))
    return found


def _line(modules: Mapping[str, Module], defined: str, depth: int) -> Iterator[str]:
    """Follow a checked file's class (`defined`: its dotted path) up its bases.

    Yields:
      Its path, then its bases' in turn; `?` for a base that isn't a checked file's class or the
      standard library's, or one too deep.

    """
    module: Module | None = modules.get(defined.rpartition(".")[0])
    name: str = defined.rpartition(".")[2]
    if module is None or module.installed or name not in module.bases:
        if stdlib.held_whole(defined) is None and defined.rpartition(".")[0] != BUILTINS_MODULE:
            yield _UNFOLLOWED
        return
    yield defined
    base: str
    for base in module.bases[name]:
        if base == classvars.SPECIAL or not depth:
            yield _UNFOLLOWED
        else:
            yield from _line(modules, plain.resolved(modules, module, base), depth - 1)
