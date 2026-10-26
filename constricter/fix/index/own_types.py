"""A checked file's classes in its overloads' parameters, and where each class a calling file names is from.

A parameter typed as nothing but checked files' classes (`frame: DataFrame`), or as an iterable of
them (`objs: Iterable[DataFrame] | Mapping[K, DataFrame]`), takes an argument by its class's
lineage: its own path and its bases', through the checked files, as an installed class's is
matched (see `constricter.fix.index.stubs.stubbed`). `concat([df, df])` then picks the overload taking
`DataFrame`s, and not the one taking `Series`.
"""

import ast
from collections.abc import Callable, Iterator, Mapping, Sequence
from pathlib import Path
from types import MappingProxyType
from typing import Final, NamedTuple, TypeAlias

from constricter.fix.core.known import Guarded, Origin
from constricter.fix.core.signatures import OWN, OWN_ELEMENTS, Accepts
from constricter.fix.index import plain, project, spelling
from constricter.fix.index.modules import Index, Memo, Module, classes_under, exported, module_at
from constricter.fix.index.stubs.atoms import BUILTINS_MODULE, CLASS, LITERAL_ATOM, NONE_ATOM, Atom, Scope
from constricter.fix.libraries import stdlib
from constricter.fix.libraries.receivers import UNFOLLOWED
from constricter.fix.values import classvars
from constricter.overrides import override

# Generic classes of one argument whose instance a builtin sequence or set argument is, by its elements.
_ITERABLES: Final = frozenset(
    {"Iterable", "Iterator", "Collection", "Sequence", "MutableSequence", "list", "List"}
    | {"set", "Set", "AbstractSet", "frozenset", "FrozenSet"},
)
# Those a builtin sequence or set isn't: they neither take one nor say what its elements are.
_MAPPINGS: Final = frozenset({"Mapping", "MutableMapping", "dict", "Dict"})
_Atoms: TypeAlias = Callable[[ast.expr, Scope], Iterator[Atom]]
_Lines: TypeAlias = Mapping[str, tuple[str, ...]]  # each class's line of bases, by how a file names it
_NO_LINES: Final[_Lines] = MappingProxyType({})


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
        if atom.kind == NONE_ATOM or (atom.kind == CLASS and name in _MAPPINGS):
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
        elif atom.kind not in {NONE_ATOM, LITERAL_ATOM} and not (
            atom.kind == CLASS and atom.origin[0] == BUILTINS_MODULE and not atom.args
        ):
            return None
    return sorted(found)


def lineages(
    catalog: Index,
    path: Path,
    guarded: Mapping[str, Guarded],
    installed: _Lines = _NO_LINES,
) -> "Lineages":
    """Find where each checked file's class the file at `path` names comes from, by how it names it.

    Its own classes, those it imports (for type checking too, `guarded`), and those of the modules
    it imports; and `installed`, installed packages' classes, which go first.

    Returns:
      Each one's path and its bases', through the checked files, `?` last where a base can't be
      followed (another package's, a computed one); none for a file `catalog` doesn't have.

    """
    target: Module | None
    if (target := module_at(catalog, path)) is None:
        return Lineages(catalog, Named({}, {}, frozenset()), installed)
    own: dict[str, tuple[str, ...]] = {
        name: _lined(catalog, f"{target.name}.{name}") for name in target.bases
    }
    # Those it names for type checking alone, then by its own imports, which the index keeps.
    checking: dict[str, Origin] = {
        name: each.origin for name, each in guarded.items() if name not in target.names
    }
    under: dict[str, str] = {}
    names: Mapping[str, Origin]
    for names in (checking, target.names):
        local: str
        origin: Origin
        for local, origin in spelling.resolved(catalog, names):
            defined: tuple[Module, str] | None
            if origin[1] is None:
                under[local] = origin[0]
                continue
            defined = None if origin[0] == target.name else project.definition(catalog.modules, origin, CLASS)
            if defined is not None and not defined[0].installed:
                own[local] = _lined(catalog, f"{defined[0].name}.{defined[1]}")
    return Lineages(catalog, Named(own, under, target.attributes), installed)


class Named(NamedTuple):
    """The classes a file names itself, by its own or imported name, and where it can name more.

    `under`: each module it imports, by how it names it, a class of whose (or of whose submodules')
    it may name by that (`pkg.m.Row`); `attributes`: the attributes it takes of anything, which a
    class its package re-exports must be one of (`pkg.Row`).
    """

    own: dict[str, tuple[str, ...]]
    under: dict[str, str]
    attributes: frozenset[str]


class Lineages(Mapping[str, tuple[str, ...]]):
    """Each class a file names, by how it names it, and its line of bases (see `lineages`).

    Those it names itself or imports by name are worked out at once; one of a module it imports
    (`test.support.Foo`, any of a package's) only when it's asked for: a file may name any of
    thousands, and names a few. Two are equal where the file names the same, the index aside.
    """

    def __init__(self, catalog: Index, named: Named, installed: Mapping[str, tuple[str, ...]]) -> None:
        """Keep what `lineages` found, `installed` first, and the index the rest are found in."""
        self.catalog: Index = catalog
        self.named: Named = named
        self.installed: Mapping[str, tuple[str, ...]] = installed
        self.asked: dict[str, tuple[str, ...] | None] = {}

    @override
    def __getitem__(self, key: str) -> tuple[str, ...]:
        """Find a class's line of bases, as `lineages` would have.

        Returns:
          It.

        Raises:
          KeyError: the file names no such class.

        """
        found: tuple[str, ...] | None = self.installed.get(key) or self.named.own.get(key)
        if found is None:
            if key not in self.asked:
                self.asked[key] = self._under(key)
            found = self.asked[key]
        if found is None:
            raise KeyError(key)
        return found

    def _under(self, key: str) -> tuple[str, ...] | None:
        """Find a class `key` names through a module the file imports, a checked file's.

        `local.Row` for one the module defines, `local.m.Row` for one a submodule does, and
        `local.Row` for one it imports from another of its package's, a name the file takes.

        Returns:
          Its line of bases, or `None`.

        """
        parts: list[str] = key.split(".")
        cut: int
        for cut in range(len(parts) - 1, 0, -1):
            package: str | None
            if (package := self.named.under.get(".".join(parts[:cut]))) is None:
                continue
            rest: list[str] = parts[cut:]
            modules: Mapping[str, Module] = self.catalog.modules
            defined: tuple[Module, str] | None = project.definition(
                modules,
                (".".join([package, *rest[:-1]]), rest[-1]),
                CLASS,
                1,
            )
            top: Module | None = modules.get(package)
            where: Origin | None = None if top is None or len(rest) != 1 else exported(top).get(rest[0])
            if defined is None and where is not None and where[1] is not None and where[0] != package:
                defined = (
                    project.definition(modules, where, CLASS) if rest[0] in self.named.attributes else None
                )
            if defined is None or defined[0].installed:
                return None
            return _lined(self.catalog, f"{defined[0].name}.{defined[1]}")
        return None

    @override
    def __iter__(self) -> Iterator[str]:
        """Name every class the file can, its own and installed ones first: each one asked for.

        Yields:
          Each one's name, as the file names it.

        """
        yield from self.installed
        yield from (name for name in self.named.own if name not in self.installed)
        local: str
        package: str
        for local, package in self.named.under.items():
            top: Module | None = self.catalog.modules.get(package)
            spelled: list[str] = [key for key, _ in classes_under(self.catalog, local, package, CLASS)]
            spelled += [
                f"{local}.{name}"
                for name in (() if top is None else exported(top))
                if name in self.named.attributes
            ]
            key: str
            for key in spelled:
                if key not in self.installed and key not in self.named.own and key in self:
                    yield key

    @override
    def __len__(self) -> int:
        """Count the classes the file can name (see `__iter__`).

        Returns:
          How many.

        """
        return sum(1 for _ in self)

    @override
    def __eq__(self, other: object) -> bool:
        """Compare two by what decides them: the classes named at once and the modules the rest are under.

        Returns:
          Whether they're equal.

        """
        if isinstance(other, Lineages):
            return (self.named, dict(self.installed)) == (other.named, dict(other.installed))
        return super().__eq__(other)

    @override
    def __hash__(self) -> int:
        """Hash it by part of what `__eq__` compares: the modules the file names classes under.

        Returns:
          The hash.

        """
        return hash((tuple(self.named.under.items()), self.named.attributes))

    @override
    def __reduce__(self) -> tuple[type[dict[str, tuple[str, ...]]], tuple[dict[str, tuple[str, ...]]]]:
        """Pickle what's worked out so far, as a `dict`: the index stays behind.

        Returns:
          How.

        """
        asked: dict[str, tuple[str, ...]] = {
            key: line for key, line in self.asked.items() if line is not None
        }
        return dict, ({**asked, **self.named.own, **self.installed},)


def _lined(catalog: Index, defined: str) -> tuple[str, ...]:
    """Follow a checked file's class up its bases (see `_line`), once for the index.

    Returns:
      Its path and its bases', each once.

    """
    memo: Memo | None = catalog.memo
    line: tuple[str, ...] | None
    if (line := None if memo is None else memo.lines.get(defined)) is None:
        line = tuple(dict.fromkeys(_line(catalog.modules, defined, project.DEPTH)))
        if memo is not None:
            memo.lines[defined] = line
    return line


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
            yield UNFOLLOWED
        return
    yield defined
    base: str
    for base in module.bases[name]:
        if base == classvars.SPECIAL or not depth:
            yield UNFOLLOWED
        else:
            yield from _line(modules, plain.resolved(modules, module, base), depth - 1)
