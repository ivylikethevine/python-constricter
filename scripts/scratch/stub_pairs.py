"""Count a package's own stubs: each `.pyi` beside a `.py`, or alone (a compiled module's).

  python3 -I scripts/scratch/stub_pairs.py DIR

DIR: an unpacked sdist's source directory (matplotlib's `lib`). Prints its modules (tests aside),
its stubs beside a module and alone, and for the modules with a stub, their functions, how many
declare a return, and how many more a function of the same name in the stub declares (by name
alone, so an estimate).
"""

import ast
import sys
from pathlib import Path

root = Path(sys.argv[1])
modules = [path for path in root.rglob("*.py") if "tests" not in path.parts]
stubs = list(root.rglob("*.pyi"))
paired = [stub for stub in stubs if stub.with_suffix(".py").exists()]
functions = declared = by_stub = 0
for stub in paired:
    named = {
        node.name
        for node in ast.walk(ast.parse(stub.read_text(encoding="utf-8")))
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef) and node.returns
    }
    for node in ast.walk(ast.parse(stub.with_suffix(".py").read_text(encoding="utf-8"))):
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            functions += 1
            declared += node.returns is not None
            by_stub += node.returns is None and node.name in named
print(
    f"{len(modules)} modules (tests aside); {len(paired)} stubs beside one, {len(stubs) - len(paired)} alone"
)
print(f"their {functions} functions: {declared} declare a return, about {by_stub} more by their stubs")
