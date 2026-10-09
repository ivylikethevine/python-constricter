# SPDX-License-Identifier: MIT
"""Which class an instance's member comes from: its own, or the base that defines it.

A class the module defines takes a member its body doesn't bind from its bases, in method
resolution order, as far as the module sees: its own classes, each defined once and not generic,
then a class another checked file or the standard library's tables define, whose members are
known whole. The order ends there, or before the first base out of sight (an installed package's,
subscripted, computed), which may define anything.
"""

import ast
import builtins
from collections import Counter
from collections.abc import Iterator, Mapping, Sequence
from types import MappingProxyType
from typing import Final, NamedTuple, TypeAlias, cast

from constricter.fix.core.signatures import AWAIT
from constricter.rules.annotations import generic_classes, node_name
from constricter.rules.syntax import FUNCTION_DEFS, child_statements, expressions
from constricter.rules.walked import classes, walk

# Bases that give an instance no member a method call could reach.
_EMPTY: Final = frozenset({"object", "Generic", "Protocol", "ABC"})
# The standard-library class a line of bases ends at (`""`: at none, the line known whole), and the
# names the classes before it bind. Several classes, where two lines each end at one: their paths,
# in order, `SEVERAL` between them.
Beyond: TypeAlias = tuple[str, frozenset[str]]
SEVERAL: Final = ","
# A standard-library class held whole: its members' names, and its own and its ancestors' paths.
Library: TypeAlias = tuple[frozenset[str], frozenset[str]]


class Lineage(NamedTuple):
    """The module's classes' ancestry, as far as it sees.

    `order`: each class's method resolution order after itself, up to the first base out of sight,
    or a class another checked file or the standard library defines (as the module spells it), which
    ends it; `bound`: the names each class's body binds; `selfish`: its methods declared to return a
    bare `Self` (see `self_returns`), which an inheriting class's instance gives as its own class.
    `beyond`: for a base another checked file defines, the standard-library class its own bases end
    at, and the names bound on the way there (see `constricter.fix.index.beyond`); one whose bases
    end at none (a mixin) doesn't end the order, which goes on past it for what it doesn't bind.
    `library`: the standard-library classes held whole that an order goes on past, or that a line
    of bases ends at beside another (see `SEVERAL`), each with its members' names.
    """

    order: Mapping[str, tuple[str, ...]] = MappingProxyType({})
    bound: Mapping[str, frozenset[str]] = MappingProxyType({})
    selfish: Mapping[str, frozenset[str]] = MappingProxyType({})
    beyond: Mapping[str, Beyond] = MappingProxyType({})
    library: Mapping[str, frozenset[str]] = MappingProxyType({})

    def definer(self, receiver: str, name: str) -> str | None:
        """Find the class whose `name` an instance of `receiver` has.

        Returns:
          `receiver` itself if it binds `name`, or isn't one of the module's classes; else the first
          class of its order that does, or that another file defines; `None` if none in sight does.
          For another file's class whose bases end at a standard-library class, that class, where
          nothing on the way binds `name` (see `beyond`).

        """
        found: str | None = (
            receiver
            if receiver not in self.bound or name in self.bound[receiver]
            else next((base for base in self.order[receiver] if self._binds(base, name)), None)
        )
        library: Beyond | None = self.beyond.get(found or "")
        if library is None or name in library[1]:
            return found
        ends: list[str] = library[0].split(SEVERAL)
        # Of several library classes, the first that has the member: the others' is behind it.
        return (
            next((end for end in ends if len(ends) == 1 or name in self.library.get(end, ())), None) or None
        )

    def _binds(self, base: str, name: str) -> bool:
        """Check whether `base`, of a class's order, is where the search for `name` ends.

        Returns:
          Whether it binds it, or may: another file's class, but one known whole that doesn't.

        """
        end: Beyond | None = self.beyond.get(base)
        if end is not None and not end[0]:
            return name in end[1]
        if base in self.library:
            return name in self.library[base]
        return base not in self.bound or name in self.bound[base]

    def selfish_of(self, owner: str) -> frozenset[str]:
        """Name the methods an instance of `owner` has that are declared to return a bare `Self`.

        Returns:
          Its own, and those it takes from its bases in sight.

        """
        return self.selfish.get(owner, frozenset()).union(
            name
            for base in self.order.get(owner, ())
            for name in self.selfish.get(base, ())
            if self.definer(owner, name) == base
        )

    def flattened(self, methods: Mapping[str, Mapping[str, str]]) -> dict[str, dict[str, str]]:
        """Add to each class's `methods` (their return types, by name) those it takes from its bases.

        Returns:
          Each class's own and inherited methods; one declared to return `Self` gives the class itself.

        """
        found: dict[str, dict[str, str]] = {owner: dict(own) for owner, own in methods.items()}
        owner: str
        bases: tuple[str, ...]
        for owner, bases in self.order.items():
            hidden: set[str] = set(self.bound[owner])
            base: str
            for base in bases:
                name: str
                annotation: str
                for name, annotation in methods.get(base, {}).items():
                    if name.removeprefix(AWAIT) not in hidden:
                        selfish: bool = name in self.selfish.get(base, ())
                        found.setdefault(owner, {})[name] = owner if selfish else annotation
                hidden |= self.bound.get(base, frozenset()) | self.beyond.get(base, ("", frozenset()))[1]
                hidden |= self.library.get(base, frozenset())
        return found


def lineage(
    tree: ast.Module,
    selfish: Mapping[str, frozenset[str]],
    imported: frozenset[str],
    beyond: Mapping[str, Beyond] | None = None,
    library: Mapping[str, Library] | None = None,
) -> Lineage:
    """Read the ancestry of the classes the module defines once each.

    `selfish`: its `self_returns`; `imported`: the classes other checked files and the standard
    library define, as it spells them; `beyond`: see `Lineage`; `library`: the standard-library
    classes held whole among them (see `Library`), and those `beyond` ends at beside another. An
    order goes on past one of those to the next base, but one that shares an ancestor with it,
    whose place between them the tables don't say.

    Returns:
      It (see `Lineage`).

    """
    nodes: Sequence[ast.ClassDef] = classes(tree)
    counts: Counter[str] = Counter(node.name for node in nodes)
    generic: frozenset[str] = generic_classes(tree)
    # Each class's bases as written: one out of sight is no key here.
    parents: dict[str, list[str]] = {
        node.name: [ast.unparse(base) for base in node.bases if node_name(base) not in _EMPTY]
        for node in nodes
        if counts[node.name] == 1
    }
    # A class of the module's is seen through; so is another file's known whole (see `Lineage.beyond`).
    seen: frozenset[str] = (frozenset(parents) - (generic - _given(nodes, imported))).union(
        base for base, end in (beyond or {}).items() if not end[0]
    )
    order: dict[str, tuple[str, ...]] = {}
    held: Mapping[str, Library] = library or {}
    passed: set[str] = set()  # the library classes an order goes on past
    name: str
    for name in parents:
        after: list[str] = (_order(name, parents, frozenset()) or [name])[1:]
        order[name] = tuple(after[: _sighted(after, (seen, imported), held, passed)])
    return Lineage(
        order,
        {node.name: frozenset(_bound(node.body)) for node in nodes if node.name in parents},
        selfish,
        MappingProxyType({}) if beyond is None else beyond,
        {base: held[base][0] for base in passed | several(beyond or {}) if base in held},
    )


def _sighted(
    after: Sequence[str],
    known: tuple[frozenset[str], frozenset[str]],
    held: Mapping[str, Library],
    passed: set[str],
) -> int:
    """Count how many of a class's ancestors (`after`, in order) are in sight.

    `known`: the classes seen through, and those another file or the standard library defines.
    One of those is the last in sight, what it inherits its own to say; but a library class
    `held` whole, which the next may follow: each one gone past is added to `passed`.

    Returns:
      How many.

    """
    lines: frozenset[str] = frozenset()  # the library classes so far, and their ancestors
    last: int = 0
    base: str
    for base in after:
        if base in known[0]:
            last += 1
            continue
        last += base in known[1] and not held.get(base, (None, frozenset[str]()))[1] & lines
        if base not in held or held[base][1] & lines or base == after[-1]:
            break
        lines |= held[base][1]
        passed.add(base)
    return last


def several(beyond: Mapping[str, Beyond]) -> frozenset[str]:
    """Name the library classes lines of bases end at beside another (see `SEVERAL`).

    Returns:
      Their paths.

    """
    return frozenset(end for found, _ in beyond.values() if SEVERAL in found for end in found.split(SEVERAL))


def _given(nodes: Sequence[ast.ClassDef], imported: frozenset[str]) -> frozenset[str]:
    """Name the classes that are generic only by a library base given its arguments: not generic at all.

    `class Rows(collections.deque[Row])`: each subscripted base one of `imported`, written with
    builtin types, dotted names and the module's own classes alone (no type variable's name).

    Returns:
      Their names.

    """
    plain: frozenset[str] = frozenset(dir(builtins)) | {node.name for node in nodes}
    return frozenset(
        node.name
        for node in nodes
        if not cast("object", getattr(node, "type_params", ()))  # Python 3.12+'s `class C[T]`
        and all(
            ast.unparse(base) in imported
            and all(part.id in plain for part in ast.walk(base.slice) if isinstance(part, ast.Name))
            for base in node.bases
            if isinstance(base, ast.Subscript)
        )
    )


def _order(name: str, parents: Mapping[str, list[str]], above: frozenset[str]) -> list[str] | None:
    """Linearise a class's ancestry as Python does (C3), a base out of sight standing for itself alone.

    `above`: the classes this one is being ordered for, which it can't be a base of.

    Returns:
      The class, then its ancestors in method resolution order; or `None` if they have no order.

    """
    if name not in parents:
        return [name]
    if name in above:
        return None
    orders: list[list[str]] = []
    base: str
    for base in parents[name]:
        found: list[str] | None
        if (found := _order(base, parents, above | {name})) is None:
            return None
        orders.append(found)
    merged: list[str] | None = _merged([*orders, list(parents[name])])
    return None if merged is None else [name, *merged]


def _merged(orders: list[list[str]]) -> list[str] | None:
    """Merge linearisations, each one's order kept: the first head that no other's tail holds, each time.

    Returns:
      The merged order, or `None` if they disagree.

    """
    left: list[list[str]]
    if not (left := [order for order in orders if order]):
        return []
    head: str | None = next(
        (order[0] for order in left if not any(order[0] in other[1:] for other in left)),
        None,
    )
    if head is None:
        return None
    rest: list[str] | None = _merged([order[1:] if order[0] == head else order for order in left])
    return None if rest is None else [head, *rest]


def _bound(body: Sequence[ast.stmt]) -> Iterator[str]:
    """Name what a class's body binds, through its compound statements: not what its methods do.

    Yields:
      Each function's and nested class's name, and each name an assignment, an import or any
      other statement stores to.

    """
    stmt: ast.stmt
    for stmt in body:
        if isinstance(stmt, (*FUNCTION_DEFS, ast.ClassDef)):
            yield stmt.name
        elif isinstance(stmt, ast.Import | ast.ImportFrom):
            yield from ((alias.asname or alias.name).partition(".")[0] for alias in stmt.names)
        else:
            part: ast.AST
            for part in expressions(stmt):
                yield from (
                    node.id
                    for node in walk(part)
                    if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store)
                )
            yield from _bound(child_statements(stmt))
