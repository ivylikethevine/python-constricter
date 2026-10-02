# SPDX-License-Identifier: MIT
"""Which class an instance's member comes from: its own, or the base that defines it.

A class the module defines takes a member its body doesn't bind from its bases, in method
resolution order, as far as the module sees: its own classes, each defined once and not generic,
then a class another checked file defines, whose members are known whole. The order ends there, or
before the first base out of sight (an installed package's, subscripted, computed), which may
define anything.
"""

import ast
from collections import Counter
from collections.abc import Iterator, Mapping, Sequence
from types import MappingProxyType
from typing import Final, NamedTuple

from constricter.rules.annotations import generic_classes, node_name
from constricter.rules.syntax import FUNCTION_DEFS, child_statements, expressions
from constricter.rules.walked import classes, walk

# Bases that give an instance no member a method call could reach.
_EMPTY: Final = frozenset({"object", "Generic", "Protocol", "ABC"})


class Lineage(NamedTuple):
    """The module's classes' ancestry, as far as it sees.

    `order`: each class's method resolution order after itself, up to the first base out of sight,
    or a class another checked file defines (as the module spells it), which ends it; `bound`: the
    names each class's body binds; `selfish`: its methods declared to return a bare `Self` (see
    `self_returns`), which an inheriting class's instance gives as its own class.
    """

    order: Mapping[str, tuple[str, ...]] = MappingProxyType({})
    bound: Mapping[str, frozenset[str]] = MappingProxyType({})
    selfish: Mapping[str, frozenset[str]] = MappingProxyType({})

    def definer(self, receiver: str, name: str) -> str | None:
        """Find the class whose `name` an instance of `receiver` has.

        Returns:
          `receiver` itself if it binds `name`, or isn't one of the module's classes; else the first
          class of its order that does, or that another file defines; `None` if none in sight does.

        """
        if receiver not in self.bound or name in self.bound[receiver]:
            return receiver
        return next(
            (base for base in self.order[receiver] if base not in self.bound or name in self.bound[base]),
            None,
        )

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
                    if name not in hidden:
                        selfish: bool = name in self.selfish.get(base, ())
                        found.setdefault(owner, {})[name] = owner if selfish else annotation
                hidden |= self.bound.get(base, frozenset())
        return found


def lineage(
    tree: ast.Module,
    selfish: Mapping[str, frozenset[str]],
    imported: frozenset[str],
) -> Lineage:
    """Read the ancestry of the classes the module defines once each.

    `selfish`: its `self_returns`; `imported`: the classes other checked files define, as it spells
    them.

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
    seen: frozenset[str] = frozenset(parents) - generic
    order: dict[str, tuple[str, ...]] = {}
    name: str
    for name in parents:
        after: list[str] = (_order(name, parents, frozenset()) or [name])[1:]
        hidden: int = next((index for index, base in enumerate(after) if base not in seen), len(after))
        # Another file's class is the last in sight: what it inherits is its own to say.
        last: int = hidden + (hidden < len(after) and after[hidden] in imported)
        order[name] = tuple(after[:last])
    return Lineage(
        order,
        {node.name: frozenset(_bound(node.body)) for node in nodes if node.name in parents},
        selfish,
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
