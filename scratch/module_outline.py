# SPDX-License-Identifier: MIT
"""Outline a module for a split: each top-level definition's lines, and the module's names it uses.

  local/.venv/bin/python -m scratch.module_outline PATH [PATH ...]
  local/.venv/bin/python -m scratch.module_outline PATH --group NAME [NAME ...]

For each statement at the module's top level: its first line, its length in lines (decorators and
the comments right above it included), its name, which of the module's other top-level names it
reads, and which read it. With `--group`, the names given and every name they read in turn, their
lines together, and the names outside the group that read one in it: what moves with them, and
what would import them back. Runs in a sandbox; writes nothing.
"""

import ast
import sys
from pathlib import Path


def names_of(node: ast.stmt) -> list[str]:
    """The names a top-level statement binds."""
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        return [node.name]
    if isinstance(node, ast.Assign):
        return [n.id for target in node.targets for n in ast.walk(target) if isinstance(n, ast.Name)]
    if isinstance(node, (ast.AnnAssign, ast.AugAssign)) and isinstance(node.target, ast.Name):
        return [node.target.id]
    if isinstance(node, getattr(ast, "TypeAlias", ())):
        return [node.name.id]
    return []


def outline(path: Path) -> tuple[dict[str, tuple[int, int]], dict[str, set[str]]]:
    """Each top-level name's first line and length, and the module's names it reads."""
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    tree = ast.parse(text)
    body = [node for node in tree.body if names_of(node)]
    spans: dict[str, tuple[int, int]] = {}
    nodes: dict[str, ast.stmt] = {}
    for node in body:
        start = min([node.lineno, *(d.lineno for d in getattr(node, "decorator_list", []))])
        while start > 1 and lines[start - 2].lstrip().startswith("#"):
            start -= 1
        end = node.end_lineno or node.lineno
        for name in names_of(node):
            spans[name] = (start, end - start + 1)
            nodes[name] = node
    reads: dict[str, set[str]] = {}
    for name, node in nodes.items():
        used = {n.id for n in ast.walk(node) if isinstance(n, ast.Name)}
        for each in ast.walk(node):
            if isinstance(each, ast.Constant) and isinstance(each.value, str):
                try:
                    annotation = ast.parse(each.value.strip(), mode="eval")
                except SyntaxError:
                    continue
                used |= {n.id for n in ast.walk(annotation) if isinstance(n, ast.Name)}
        reads[name] = {other for other in used if other in spans and other != name}
    return spans, reads


def main(argv: list[str]) -> int:
    """Print each path's outline, or a group's closure."""
    group = argv[argv.index("--group") + 1 :] if "--group" in argv else []
    paths = [Path(arg) for arg in (argv[: argv.index("--group")] if group else argv)]
    for path in paths:
        spans, reads = outline(path)
        read_by = {name: sorted(other for other, used in reads.items() if name in used) for name in spans}
        if not group:
            print(f"# {path}: {len(path.read_text(encoding='utf-8').splitlines())} lines")
            for name, (start, length) in sorted(spans.items(), key=lambda item: item[1][0]):
                print(f"{start:5} {length:4} {name}  <- {', '.join(sorted(reads[name]))}  -> {', '.join(read_by[name])}")
            continue
        closure: set[str] = set()
        todo = list(group)
        while todo:
            name = todo.pop()
            if name in closure or name not in spans:
                continue
            closure.add(name)
            todo.extend(reads[name])
        total = sum(spans[name][1] for name in closure)
        print(f"# {path}: group of {len(closure)} names, {total} lines")
        for name in sorted(closure, key=lambda n: spans[n][0]):
            outside = [other for other in read_by[name] if other not in closure]
            print(f"{spans[name][0]:5} {spans[name][1]:4} {name}  read from outside by: {', '.join(outside)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
