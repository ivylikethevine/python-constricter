# SPDX-License-Identifier: MIT
"""The order the CLI checks files in: each after those whose unannotated functions it calls.

So their `return`s are known when it's checked (see `project.returned`); files calling each other's
functions (a cycle in the graph `project.needs` gives) form one component.
"""

from collections.abc import Iterator, Mapping, Sequence
from pathlib import Path
from typing import Final, NamedTuple, TypeAlias

from constricter.fix import project
from constricter.fix.project import Index

_SUFFIX: Final = ".py"
_Visit: TypeAlias = tuple[str, Iterator[str]]  # a module in the graph, and its callees still to visit


class Plan(NamedTuple):
    """The order to check files in (see `plan`), and the module each one's `returned` goes to."""

    components: list[list[int]]  # files importing each other, by their index in the paths; callees first
    after: list[frozenset[int]]  # the components each one's files import unannotated functions from
    names: dict[int, str]  # each file's module name, if it's the only file with it


def plan(catalog: Index, paths: Sequence[Path]) -> Plan:
    """Order the files in `paths` for checking: each after the files whose unannotated functions it calls.

    Those it imports and calls (through re-exports, or an imported module), so their `return`s are known
    when it's checked (see `returned`); files calling each other's (a cycle) are one component. A
    file `catalog` doesn't have, or one of several with the same module name, is one on its own.

    Returns:
      The components, callees first, and what each comes after; and each file's module.

    """
    names: list[str | None] = [
        project.module_name(path) if path.suffix == _SUFFIX else None for path in paths
    ]
    counts: dict[str | None, int] = {}
    name: str | None
    for name in names:
        counts[name] = counts.get(name, 0) + 1
    unique: dict[str, int] = {
        name: at
        for at, name in enumerate(names)
        if name is not None and counts[name] == 1 and name in catalog.modules
    }
    graph: dict[str, list[str]] = {
        name: sorted(project.needs(catalog, catalog.modules[name]) & unique.keys()) for name in sorted(unique)
    }
    components: list[list[int]] = []
    after: list[frozenset[int]] = []
    component: dict[str, int] = {}
    members: frozenset[str]
    for members in _Components(graph):  # callees' components first
        member: str
        for member in members:
            component[member] = len(components)
        after.append(
            frozenset(
                component[callee] for member in members for callee in graph[member] if callee not in members
            ),
        )
        components.append(sorted(unique[member] for member in members))
    at: int
    for at in sorted(set(range(len(paths))) - set(unique.values())):
        components.append([at])
        after.append(frozenset())
    return Plan(components, after, {at: name for name, at in unique.items()})


class _Components:
    """A graph's strongly connected components (Tarjan's, with a stack of its own: chains can be long)."""

    def __init__(self, graph: Mapping[str, Sequence[str]]) -> None:
        """Start on `graph`: each node's successors."""
        self.graph: Mapping[str, Sequence[str]] = graph
        self.order: dict[str, int] = {}  # each node visited, and when
        self.low: dict[str, int] = {}  # the earliest node on the stack each node reaches
        self.stack: list[str] = []
        self.on_stack: set[str] = set()

    def __iter__(self) -> Iterator[frozenset[str]]:
        """Find the components.

        Yields:
          Each component, after every component it reaches.

        """
        start: str
        for start in self.graph:
            yield from self.reached(start)

    def reached(self, start: str) -> Iterator[frozenset[str]]:
        """Visit what `start` reaches that isn't visited yet (nothing, if it's been visited itself).

        Yields:
          Each component it completes.

        """
        if start in self.order:
            return
        # Each entry: a node, and its successors still to visit; `None` at the bottom ends it.
        waiting: list[_Visit | None] = [None, self._visit(start)]
        entry: _Visit
        for entry in iter(waiting.pop, None):
            node: str = entry[0]
            successor: str | None
            if (successor := next(entry[1], None)) is not None:
                waiting.append(entry)
                if successor not in self.order:
                    waiting.append(self._visit(successor))
                elif successor in self.on_stack:
                    self.low[node] = min(self.low[node], self.order[successor])
                continue
            parent: _Visit | None
            if (parent := waiting[-1]) is not None:
                self.low[parent[0]] = min(self.low[parent[0]], self.low[node])
            if self.low[node] == self.order[node]:
                yield self._popped(node)

    def _visit(self, node: str) -> _Visit:
        """Put `node` on the stack.

        Returns:
          It, and its successors to visit.

        """
        self.order[node] = self.low[node] = len(self.order)
        self.stack.append(node)
        self.on_stack.add(node)
        return node, iter(self.graph[node])

    def _popped(self, node: str) -> frozenset[str]:
        """Take `node`'s component off the stack: `node` and what's above it.

        Returns:
          The component.

        """
        members: list[str] = [*iter(self.stack.pop, node), node]
        self.on_stack.difference_update(members)
        return frozenset(members)
