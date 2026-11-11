"""Count a package's bindings that call into a module it ships as a stub alone (a compiled module's).

  local/.venv/bin/python scratch/lone_stub_reach.py DIR

DIR: an unpacked sdist's package (matplotlib's `lib/matplotlib`), its `.py` and `.pyi` files checked
in a copy under `$TMPDIR` at `suffocate` as `--fix --show-fixes` lists it, in one process. A lone
stub is a `.pyi` with no `.py` beside it. A binding counts when its value is a call (awaited or
not) through a name its file imports from a lone stub's module: `_path.f()` after
`from . import _path`, `f()` after `from ._path import f`, `pkg._path.f()` after `import pkg._path`.
A method called on what such a call gives isn't counted. Prints the lone stubs, the bindings that
count with a fix and with none, and the commonest callees with none. About 100s for matplotlib, 1
worker on 16CPU/60GB.
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

root: Path = Path(sys.argv[1]).resolve()
work: Path = Path(tempfile.mkdtemp(dir=os.environ.get("TMPDIR")))
copy: Path = work / root.name
shutil.copytree(
    root,
    copy,
    ignore=lambda folder, names: [
        name
        for name in names
        if not (Path(folder, name).is_dir() or name.endswith((".py", ".pyi"))) or name == "__pycache__"
    ],
)


def module(path: Path) -> str:
    parts: list[str] = list(path.relative_to(work).with_suffix("").parts)
    return ".".join(parts[:-1] if parts[-1] == "__init__" else parts)


lone: dict[str, Path] = {
    module(stub): stub for stub in sorted(copy.rglob("*.pyi")) if not stub.with_suffix(".py").exists()
}
lone = {name: stub for name, stub in lone.items() if not (stub.with_suffix("") / "__init__.py").exists()}


def names(path: Path, tree: ast.Module) -> dict[str, str]:
    """Map each dotted name `path` binds by an import to the lone module, or its member, it names."""
    package: list[str] = module(path).split(".")
    if path.stem != "__init__":
        package = package[:-1]
    found: dict[str, str] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name in lone:
                    found[alias.asname or alias.name] = alias.name
        elif isinstance(node, ast.ImportFrom):
            base: list[str] = package[: len(package) - node.level + 1] if node.level else []
            source: str = ".".join([*base, *([node.module] if node.module else [])])
            for alias in node.names:
                if f"{source}.{alias.name}" in lone:
                    found[alias.asname or alias.name] = f"{source}.{alias.name}"
                elif source in lone:
                    found[alias.asname or alias.name] = f"{source}:{alias.name}"
    return found


def dotted(node: ast.expr) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute) and (head := dotted(node.value)) is not None:
        return f"{head}.{node.attr}"
    return None


ran = subprocess.run(
    [
        sys.executable,
        "-m",
        "constricter",
        "--fix",
        "--show-fixes",
        "--format=json",
        "--level=suffocate",
        "--jobs=1",
        str(copy),
    ],
    capture_output=True,
    text=True,
    check=False,
    cwd=work,
)
bindings: list[dict[str, object]] = [
    each for each in json.loads(ran.stdout or "[]") if each["code"] == "LVA001"
]
fixed: Counter[str] = Counter()
unfixed: Counter[str] = Counter()
read: dict[str, tuple[ast.Module, dict[str, str]]] = {}
for each in bindings:
    path: Path = Path(str(each["path"]))
    path = path if path.is_absolute() else work / path
    if str(path) not in read:
        tree: ast.Module = ast.parse(path.read_text(encoding="utf-8"))
        read[str(path)] = (tree, names(path, tree))
    tree, imported = read[str(path)]
    if not imported:
        continue
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Assign | ast.AnnAssign)
            and node.lineno == each["line"]
            and node.value is not None
        ):
            value: ast.expr = node.value.value if isinstance(node.value, ast.Await) else node.value
            callee: str | None = dotted(value.func) if isinstance(value, ast.Call) else None
            if callee is not None:
                head, _, member = callee.rpartition(".")
                target: str | None = imported.get(callee) if ":" in imported.get(callee, "") else None
                if target is None and head in imported and ":" not in imported[head]:
                    target = f"{imported[head]}:{member}"
                if target is not None:
                    (fixed if each["fix"] else unfixed)[target] += 1
            break
shutil.rmtree(work)
print(f"{root.name}: {len(lone)} lone stubs: {', '.join(sorted(lone))}")
print(
    f"  {len(bindings)} bindings, {sum(not each['fix'] for each in bindings)} with no fix;"
    f" {fixed.total() + unfixed.total()} call into a lone stub's module:"
    f" {fixed.total()} with a fix, {unfixed.total()} with none",
)
print("  commonest with none:", ", ".join(f"{name} {count}" for name, count in unfixed.most_common(12)))
print("  commonest with a fix:", ", ".join(f"{name} {count}" for name, count in fixed.most_common(12)))
