# SPDX-License-Identifier: MIT
"""Count the plain classes' variables bound to one of the checked files' own classes, and which could be typed.

  local/.venv/bin/python -m scratch.class_names_census                 # django
  local/.venv/bin/python -m scratch.class_names_census pandas pip       # those corpora, one at a time

For each corpus: every plain class's variable bound once, directly in its body, to a bare name
(`form_class = PasswordChangeForm`) that the index resolves to a class a checked file defines (the
module's own, or imported). Of those, the ones no other class above or under it in the checked
files binds the same name in its body (an override a type checker would hold to the same type once
both are declared): what `type[Class]` could be offered for. Prints the counts and a few examples.
Runs in a sandbox (one process, the corpus indexed as a check does).
"""

import argparse
import ast
import warnings
from collections import defaultdict

from constricter.fix.index import decorated, installed, own_types, plain, project
from constricter.fix.index.atoms import CLASS
from constricter.fix.values.classvars import _bound
from tests.corpus import corpus_table


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("corpora", nargs="*", default=["django"])
    args = parser.parse_args()
    warnings.simplefilter("ignore")
    roots = {each.name: each.root for each in corpus_table.corpora()}
    for name in args.corpora:
        paths = sorted(roots[name].rglob("*.py"))
        catalog = plain.settled(
            decorated.passed(installed.with_installed(project.index(paths), installed.search_path())),
            (),
        )
        by_name = {project.module_name(path): path for path in paths}
        trees: dict[str, ast.Module] = {}
        for module, path in by_name.items():
            if module in catalog.modules:
                try:
                    trees[module] = ast.parse(path.read_bytes())
                except (SyntaxError, ValueError):
                    pass
        bound: dict[str, set[str]] = {}  # each class, as `module.Class`: the names its body binds
        bodies: dict[str, ast.ClassDef] = {}
        for module, tree in trees.items():
            for node in tree.body:
                if isinstance(node, ast.ClassDef):
                    bound[f"{module}.{node.name}"] = {each for stmt in node.body for each in _bound(stmt)}
                    bodies[f"{module}.{node.name}"] = node
        lines: dict[str, tuple[str, ...]] = {}
        for module in trees:
            found = own_types.lineages(catalog, by_name[module], {})
            for local in catalog.modules[module].bases:
                lines[f"{module}.{local}"] = found.get(local, ())
        under: dict[str, set[str]] = defaultdict(set)
        for each, line in lines.items():
            for above in line[1:]:
                under[above].add(each)
        candidates = 0
        typed: list[str] = []
        for module, tree in trees.items():
            target = catalog.modules[module]
            for node in tree.body:
                if not isinstance(node, ast.ClassDef) or node.name not in target.plain:
                    continue
                here = f"{module}.{node.name}"
                counts = defaultdict(int)
                for stmt in node.body:
                    for each in _bound(stmt):
                        counts[each] += 1
                for stmt in node.body:
                    match stmt:
                        case ast.Assign(targets=[ast.Name(id=variable)], value=ast.Name(id=value)) if counts[variable] == 1:
                            origin = (module, value) if value in target.classes else target.names.get(value)
                            defined = None if origin is None else project.definition(catalog.modules, origin, CLASS)
                            if defined is None or defined[0].installed:
                                continue
                            candidates += 1
                            others = {*lines.get(here, ())[1:], *under.get(here, ())}
                            if not any(variable in bound.get(other, ()) for other in others):
                                typed.append(f"{module}:{stmt.lineno} {node.name}.{variable} = {value}")
                        case _:
                            pass
        print(f"{name}: {candidates} plain classes' variables bound to a checked file's class; {len(typed)} with no class above or under binding the name")
        for example in typed[:8]:
            print(f"  {example}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
