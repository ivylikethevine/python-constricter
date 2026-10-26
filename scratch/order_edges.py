"""Count the check order's edges by a method's name alone, and what an edge only by the class named would leave.

`order.plan` makes a file wait for a module whose classes it names when any class there has an
unannotated method of a name it calls (`loose.needs`, by the module's `loose`). This builds the
graph as `order.plan` does (the index as `rounds.checked_all` makes it), then again with that edge
only where a class the file names, or one of its bases in the same module, has such a method, and
without those edges at all. For each it prints the edges, the components (the largest), and the
longest chain of components, in files and in source bytes (a check's time is about its bytes).

    VIRTUAL_ENV=... local/.venv/bin/python -m scratch.order_edges CORPUS
"""

import ast
import sys
from collections.abc import Callable, Mapping
from pathlib import Path

from constricter.cli.paths import python_files
from constricter.fix.index import awaits, crossed, decorated, fixtures, linked, loose, managed, order, plain, project
from constricter.fix.index.modules import Index, Module
from constricter.fix.index.stubs import installed
from constricter.fix.values.returned import unannotated
from constricter.fix.core.signatures import AWAIT
from constricter.offences import PLAIN_BASES

_Needs = Callable[[Index, Module], set[str]]


def class_loose(paths: list[Path]) -> dict[str, dict[str, frozenset[str]]]:
    """Each module's classes' unannotated methods, with those of their bases in the module, by class name."""
    found: dict[str, dict[str, frozenset[str]]] = {}
    for path in paths:
        try:
            tree = ast.parse(path.read_bytes())
        except (SyntaxError, ValueError):
            continue
        own: dict[str, frozenset[str]] = {}
        bases: dict[str, list[str]] = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                methods = unannotated(node.body) | {
                    f"{AWAIT}{stmt.name}"
                    for stmt in node.body
                    if isinstance(stmt, ast.AsyncFunctionDef) and stmt.returns is None
                }
                own[node.name] = own.get(node.name, frozenset()) | methods
                bases.setdefault(node.name, []).extend(b.id for b in node.bases if isinstance(b, ast.Name))
        lined: dict[str, frozenset[str]] = {}
        for name in own:
            seen: set[str] = set()
            todo = [name]
            union: set[str] = set()
            while todo:
                each = todo.pop()
                if each in seen or each not in own:
                    continue
                seen.add(each)
                union |= own[each]
                todo.extend(bases.get(each, ()))
            lined[name] = frozenset(union)
        found[project.module_name(path)] = lined
    return found


def per_class(lined: Mapping[str, Mapping[str, frozenset[str]]]) -> _Needs:
    """`loose.needs`, but by the class named: a module's class with no such method makes no edge."""

    def needs(catalog: Index, target: Module) -> set[str]:
        called = loose._called(target)
        found: set[str] = set()
        named = (target.names, target.attributes)
        for _, defined in crossed.spelled_classes(catalog, target, named, set()):
            module, name = defined[0], defined[1]
            if module.name == target.name or module.loose.isdisjoint(called):
                continue
            methods = lined.get(module.name, {}).get(name)
            if methods is None or not methods.isdisjoint(called):  # not found: kept, as `loose` has it
                found.add(module.name)
        return found

    return needs


def graph(catalog: Index, unique: Mapping[str, int], by_method: _Needs | None) -> dict[str, list[str]]:
    """The graph `order.plan` builds, its `loose.needs` swapped for `by_method` (`None`: none)."""
    return {
        name: sorted(
            (
                linked.needs(catalog, catalog.modules[name])
                | (set() if by_method is None else by_method(catalog, catalog.modules[name]))
                | managed.needs(catalog, catalog.modules[name])
                | awaits.needs(catalog, catalog.modules[name])
                | fixtures.needed(catalog, name)
            )
            & unique.keys(),
        )
        for name in sorted(unique)
    }


def report(title: str, edges: dict[str, list[str]], sizes: Mapping[str, int]) -> None:
    """Print a graph's edges, components and longest chain."""
    components = list(order._Components(edges))
    of: dict[str, int] = {}
    for at, members in enumerate(components):
        for member in members:
            of[member] = at
    files: list[int] = []
    weight: list[int] = []
    for at, members in enumerate(components):  # callees first: each one's predecessors are done
        after = {of[c] for m in members for c in edges[m] if of[c] != at}
        files.append(len(members) + max((files[a] for a in after), default=0))
        weight.append(sum(sizes[m] for m in members) + max((weight[a] for a in after), default=0))
    count = sum(len(v) for v in edges.values())
    largest = max(len(c) for c in components)
    total = sum(sizes.values())
    print(
        f"{title}: {count} edges, {len(components)} components (largest {largest}), longest chain"
        f" {max(files)} files, {max(weight) / 1e6:.2f} MB of {total / 1e6:.2f} MB ({max(weight) / total:.0%})"
    )


def main() -> None:
    paths = [p for p in python_files([Path(sys.argv[1])]) if p.suffix == ".py"]
    catalog = plain.settled(
        decorated.passed(installed.with_installed(project.index(paths), installed.search_path())),
        PLAIN_BASES,
    )
    names = [project.module_name(p) for p in paths]
    counts: dict[str, int] = {}
    for name in names:
        counts[name] = counts.get(name, 0) + 1
    unique = {n: at for at, n in enumerate(names) if counts[n] == 1 and n in catalog.modules}
    sizes = {n: paths[at].stat().st_size for n, at in unique.items()}
    lined = class_loose([paths[at] for at in unique.values()])
    full = graph(catalog, unique, loose.needs)
    by_class = graph(catalog, unique, per_class(lined))
    none = graph(catalog, unique, None)
    loose_only = sum(len(set(full[n]) - set(none[n])) for n in full)
    kept = sum(len(set(by_class[n]) - set(none[n])) for n in full)
    print(f"{len(unique)} modules; edges by a method's name alone: {loose_only}, by the class named: {kept}")
    report("as checked", full, sizes)
    report("by the class named", by_class, sizes)
    report("no method edges", none, sizes)


if __name__ == "__main__":
    main()
