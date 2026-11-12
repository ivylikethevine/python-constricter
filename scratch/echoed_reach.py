"""Count, by syntax alone, what `echoed` could reach: methods returning a parameter as given, and their calls.

  local/.venv/bin/python scratch/echoed_reach.py DIR...

Each DIR's `.py` files are parsed, none checked. A method counts as `returned._echo` takes one;
a binding counts when its value is `self.NAME(...)`, `NAME` such a method of the class the
statement is in, a base's in the file not looked for: fewer than a check would reach by those, and
more by the calls whose argument has no known type. Prints each DIR's classes' such methods, those
with a call bound to a name, and the bindings; then the commonest methods. About a minute for the
mega corpora's checkouts, 1 worker on 16CPU/60GB.
"""

import ast
import sys
import warnings
from collections import Counter
from pathlib import Path

from constricter.fix.values.bodies import plain
from constricter.fix.values.returned import _echo

warnings.simplefilter("ignore", SyntaxWarning)  # the corpora's own escapes
total: Counter[str] = Counter()
commonest: Counter[str] = Counter()
for root in map(Path, sys.argv[1:]):
    found: Counter[str] = Counter()
    for path in root.rglob("*.py"):
        try:
            tree = ast.parse(path.read_bytes())
        except (SyntaxError, ValueError):
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef):
                continue
            echoes = {
                func.name for func in plain(node.body) if _echo(tree, node, func, frozenset()) is not None
            }
            found["methods"] += len(echoes)
            called: set[str] = set()
            for stmt in ast.walk(node):
                value = getattr(stmt, "value", None) if isinstance(stmt, ast.Assign | ast.AnnAssign) else None
                if (
                    isinstance(value, ast.Call)
                    and isinstance(value.func, ast.Attribute)
                    and isinstance(value.func.value, ast.Name)
                    and value.func.value.id == "self"
                    and value.func.attr in echoes
                ):
                    found["bindings"] += 1
                    called.add(value.func.attr)
                    commonest[f"{root.name}: {node.name}.{value.func.attr}"] += 1
            found["called"] += len(called)
    total += found
    if found["methods"]:
        print(
            f"{root.name}: {found['methods']} methods, {found['called']} called and bound, {found['bindings']} bindings"
        )
print(f"in all: {total['methods']} methods, {total['called']} called and bound, {total['bindings']} bindings")
print("commonest:", ", ".join(f"{name} {count}" for name, count in commonest.most_common(12)))
