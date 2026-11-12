"""Count a package's bindings with no fix that call a function or method its own stubs declare.

  local/.venv/bin/python scripts/scratch/stub_reach.py DIR

DIR: an unpacked sdist's package (matplotlib's `lib/matplotlib`), checked in a copy under `$TMPDIR`
at `suffocate` as `--fix --show-fixes` lists it. A binding counts when its value is a call (awaited
or not) whose callee's last name a stub in DIR declares a return for, `-> None` aside: by name
alone, so an estimate of what reading the package's `.pyi` files beside its source could reach.
Prints the bindings with no fix, those that count, and the commonest callees.
"""

import ast
import json
import os
import shutil
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

root: Path = Path(sys.argv[1])
declared: set[str] = set()
for stub in root.rglob("*.pyi"):
    for node in ast.walk(ast.parse(stub.read_text(encoding="utf-8"))):
        if (
            isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef)
            and node.returns is not None
            and not (isinstance(node.returns, ast.Constant) and node.returns.value is None)
        ):
            declared.add(node.name)

work: Path = Path(tempfile.mkdtemp(dir=os.environ.get("TMPDIR")))
copy: Path = work / root.name
shutil.copytree(root, copy, ignore=shutil.ignore_patterns("*.pyi"))
ran = subprocess.run(
    [
        sys.executable,
        "-m",
        "constricter",
        "--fix",
        "--show-fixes",
        "--format=json",
        "--level=suffocate",
        str(copy),
    ],
    capture_output=True,
    text=True,
    check=False,
    cwd=work,
)
unfixed: list[dict[str, object]] = [
    each for each in json.loads(ran.stdout or "[]") if each["code"] == "LVA001" and not each["fix"]
]
callees: Counter[str] = Counter()
trees: dict[str, ast.Module] = {}
for each in unfixed:
    path: str = str(each["path"])
    tree: ast.Module = trees.setdefault(path, ast.parse(Path(path).read_text(encoding="utf-8")))
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Assign | ast.AnnAssign)
            and node.lineno == each["line"]
            and node.value is not None
        ):
            value: ast.expr = node.value.value if isinstance(node.value, ast.Await) else node.value
            if isinstance(value, ast.Call):
                func: ast.expr = value.func
                name: str = (
                    func.attr
                    if isinstance(func, ast.Attribute)
                    else func.id
                    if isinstance(func, ast.Name)
                    else ""
                )
                if name in declared:
                    callees[name] += 1
            break
shutil.rmtree(work)
print(
    f"{root.name}: {len(unfixed)} bindings with no fix; {callees.total()} call a function its stubs declare"
)
print("  commonest:", ", ".join(f"{name} {count}" for name, count in callees.most_common(12)))
