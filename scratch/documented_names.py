"""Count what the docstring `Returns` entries of a corpus's plain unannotated functions name.

    local/.venv/bin/python -m scratch.documented_names ROOT [ROOT ...] [--top N] [--show KIND]

For each `def` directly in a module or a class body, undecorated (or `@staticmethod`), with no
return annotation, reads the return its docstring names with `constricter.fix.values.documented`
and sorts it: `typed` (with the annotation), `none` (no docstring or no section), `several` (a
numpydoc section of several entries that isn't a tuple every `return` displays) or `other`. A name
counts as a class where the module binds its first part at its top level, by an import or a class
of its own: an upper bound, since the check itself knows which imported names are classes and which
are generic. Prints each count per root, then the `--top` entry texts left untyped, with how many
functions name each and how many calls to a function of that name the root has (by name alone: a
rough reach). AST only, one process.
"""

import argparse
import ast
from collections import Counter
from collections.abc import Callable
from pathlib import Path

from constricter.fix.values import documented as doc

_SKIPPED_DECORATORS = frozenset({"staticmethod"})


def _functions(tree: ast.Module) -> list[ast.FunctionDef]:
    """List the plain functions `documented` may type: in the module's or a class's body, undecorated.

    Returns:
      Them.

    """
    bodies: list[list[ast.stmt]] = [
        tree.body,
        *(node.body for node in tree.body if isinstance(node, ast.ClassDef)),
    ]
    return [
        func
        for body in bodies
        for func in body
        if isinstance(func, ast.FunctionDef)
        and func.returns is None
        and all(isinstance(d, ast.Name) and d.id in _SKIPPED_DECORATORS for d in func.decorator_list)
    ]


def _bound(tree: ast.Module) -> Callable[[str], bool]:
    """Tell whether a dotted name's first part is bound at the module's top level by an import or a class.

    Returns:
      Whether it is.

    """
    names: set[str] = set()
    statements: list[ast.stmt] = [*tree.body]
    for node in tree.body:
        if isinstance(node, ast.If | ast.Try):
            statements.extend((*node.body, *node.orelse))
    for node in statements:
        if isinstance(node, ast.Import | ast.ImportFrom):
            names.update((alias.asname or alias.name).partition(".")[0] for alias in node.names)
        elif isinstance(node, ast.ClassDef):
            names.add(node.name)
    return lambda name: name.partition(".")[0] in names


def _entry(docstring: str) -> str | None:
    """Read a docstring's named return's text, as `documented` finds the section.

    Returns:
      It, or `None` for no section.

    """
    found = doc._NUMPYDOC.search(docstring)
    if found is not None:
        return " ".join(found.group("body").strip().splitlines()[:1]) or None
    found = doc._GOOGLE.search(docstring) or doc._SPHINX.search(docstring)
    return None if found is None else found.group("type")


def _calls(tree: ast.Module) -> Counter[str]:
    """Count each call's callee name (`f()`, `x.f()`).

    Returns:
      The counts.

    """
    counted: Counter[str] = Counter()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                counted[node.func.id] += 1
            elif isinstance(node.func, ast.Attribute):
                counted[node.func.attr] += 1
    return counted


def _kind(func: ast.FunctionDef, tree: ast.Module, classes: Callable[[str], bool]) -> tuple[str, str | None]:
    """Sort one function: (`typed` | `none` | `several` | `other`, the annotation or the entry text).

    Returns:
      Its kind and text.

    """
    docstring = ast.get_docstring(func)
    entry = None if docstring is None else _entry(docstring)
    if docstring is None or entry is None:
        return "none", None
    annotation = doc.documented(func, [None], numpy=doc.imports_numpy(tree), classes=classes)
    if annotation is not None:
        return "typed", annotation
    found = doc._NUMPYDOC.search(docstring)
    entries = None if found is None else doc._numpydoc(found.group("body"), found.group("indent"))
    return ("several", entry) if entries and len(entries) > 1 else ("other", " ".join(entry.split()))


def main() -> None:
    """Print the counts for each root."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("roots", nargs="+", type=Path)
    parser.add_argument("--top", type=int, default=40)
    parser.add_argument("--show", help="list each function of this kind (typed, none, several, other)")
    args = parser.parse_args()
    for root in args.roots:
        kinds: Counter[str] = Counter()
        texts: Counter[str] = Counter()
        names_by_text: dict[str, set[str]] = {}
        calls: Counter[str] = Counter()
        typed: Counter[str] = Counter()
        for path in sorted(root.rglob("*.py")):
            try:
                tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
            except (SyntaxError, ValueError):
                continue
            calls.update(_calls(tree))
            classes = doc.writable(tree, (_bound(tree),))
            for func in _functions(tree):
                kind, text = _kind(func, tree, classes)
                kinds[kind] += 1
                if kind == "typed" and text is not None:
                    typed[text] += 1
                elif kind == "other" and text is not None:
                    texts[text] += 1
                    names_by_text.setdefault(text, set()).add(func.name)
                if args.show == kind:
                    print(f"  {path.relative_to(root)}:{func.lineno} {func.name}: {text}")
        total = sum(kinds.values())
        print(f"{root.name}  functions {total}  " + "  ".join(f"{k} {v}" for k, v in kinds.most_common()))
        print("  typed: " + ", ".join(f"{a} {n}" for a, n in typed.most_common()))
        print(f"  {'functions':>9}  {'calls':>6}  entry")
        for words, count in texts.most_common(args.top):
            reach = sum(calls[name] for name in names_by_text[words])
            print(f"  {count:>9}  {reach:>6}  {words}")
        print("-" * 60)


if __name__ == "__main__":
    main()
