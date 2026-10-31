"""Why a run's class-body bindings with no fix sit in a class that isn't plain, for choosing what to widen.

    local/.venv/bin/python -m scratch.class_plain corpus-runs/FOLDER NAME=ROOT [NAME=ROOT ...] [--top N]

For each corpus named, reads the census rows (`records/NAME/*/census.rows.jsonl`) of class-scope
bindings `--fix` offers nothing for, opens the file under ROOT (the directory the run checked for
NAME), finds the innermost class holding the line, and counts what keeps that class from being plain
(`constricter.fix.values.classvars`), followed up its bases through every class ROOT defines (by
name alone, the first definition found): a metaclass (by name), another keyword, a decorator (by
name), a base that isn't a name, or a base ROOT doesn't define, by its origin through the module's
imports (a builtin, `object`, a test case and `PASSED_OVER` left out). A class may count under
several; one with none is `plain by its text` (a store or a binding's count decides). Runs nothing.
"""

import argparse
import ast
import json
from collections import Counter, defaultdict
from collections.abc import Mapping
from pathlib import Path

from constricter.fix.values.classvars import allowed, imported
from constricter.source.annotations import dotted

_Own = tuple[list[str], list[str]]  # a class's own causes, and the names of its bases ROOT may define


def _own(node: ast.ClassDef, origins: Mapping[str, str]) -> _Own:
    causes: list[str] = []
    bases: list[str] = []
    for keyword in node.keywords:
        named = dotted(keyword.value)
        causes.append(f"metaclass: {named}" if keyword.arg == "metaclass" else f"keyword: {keyword.arg}")
    for decorator in node.decorator_list:
        target = decorator.func if isinstance(decorator, ast.Call) else decorator
        causes.append(f"decorator: {dotted(target)}")
    for base in node.bases:
        value = base.value if isinstance(base, ast.Subscript) else base
        name = dotted(value)
        if name is None:
            causes.append("base: not a name")
            continue
        first, _, rest = name.partition(".")
        origin = origins.get(first, first)
        whole = f"{origin}.{rest}" if rest else origin
        if name != "object" and not allowed(whole):
            bases.append(whole)
    return causes, bases


def _roots(name: str, defined: Mapping[str, _Own], seen: frozenset[str]) -> set[str]:
    causes, bases = defined[name]
    found = set(causes)
    for base in bases:
        last = base.rpartition(".")[2]
        if last in defined and last not in seen:
            found |= _roots(last, defined, seen | {last})
        elif last not in defined:
            found.add(f"base: {base}")
    return found


def _holder(tree: ast.Module, line: int) -> ast.ClassDef | None:
    best: ast.ClassDef | None = None
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.lineno <= line <= (node.end_lineno or node.lineno):
            if best is None or node.lineno > best.lineno:
                best = node
    return best


def _defined(root: Path) -> tuple[dict[str, _Own], dict[str, ast.Module]]:
    defined: dict[str, _Own] = {}
    trees: dict[str, ast.Module] = {}
    for path in sorted(root.rglob("*.py")):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except (OSError, SyntaxError, UnicodeDecodeError, ValueError):
            continue
        trees[str(path.relative_to(root))] = tree
        origins = imported(tree)
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                defined.setdefault(node.name, _own(node, origins))
    return defined, trees


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("folder", type=Path)
    parser.add_argument("roots", nargs="+")
    parser.add_argument("--top", type=int, default=40)
    args = parser.parse_args()
    counts: Counter[str] = Counter()
    samples: dict[str, list[str]] = defaultdict(list)
    total = 0
    for pair in args.roots:
        name, _, root = pair.partition("=")
        defined, trees = _defined(Path(root))
        for rows in args.folder.glob(f"records/{name}/*/census.rows.jsonl"):
            for line in rows.read_text(encoding="utf-8").splitlines():
                row = json.loads(line)
                tree = trees.get(row["path"])
                if row["fixed"] or row["scope"] != "class" or tree is None:
                    continue
                if (node := _holder(tree, row["line"])) is None or node.name not in defined:
                    continue
                total += 1
                for cause in _roots(node.name, defined, frozenset({node.name})) or {"plain by its text"}:
                    counts[cause] += 1
                    if len(samples[cause]) < 2:
                        samples[cause].append(f"{name}:{row['path']}:{row['line']} {node.name}")
    print(f"{total:,} class-body bindings with no fix")
    for cause, count in counts.most_common(args.top):
        print(f"{count:7,}  {cause}  ({'; '.join(samples[cause])})")


if __name__ == "__main__":
    main()
