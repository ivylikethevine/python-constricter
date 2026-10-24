"""List constricter's `functools` caches whose arguments include a syntax node, which keep it alive.

  local/.venv/bin/python scratch/node_caches.py

An `lru_cache` holds its arguments strongly: one given a module's tree, or any node of it (a node
holds its subtree, though not its parents), keeps up to `maxsize` of them alive after their files are
checked. Prints each such cache: its module and function, its `maxsize`, and the parameter typed as a
node.
"""

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "constricter"
NODES = {
    "Module",
    "AST",
    "FunctionDef",
    "AsyncFunctionDef",
    "ClassDef",
    "stmt",
    "expr",
    "Call",
    "Name",
    "Attribute",
    "arguments",
    "_Def",
}


def cache_of(decorator: ast.expr) -> str | None:
    """Name a `functools` cache decorator's size, or `None` if it isn't one."""
    call = decorator if isinstance(decorator, ast.Call) else None
    target = call.func if call else decorator
    name = (
        target.attr
        if isinstance(target, ast.Attribute)
        else target.id
        if isinstance(target, ast.Name)
        else ""
    )
    if name == "cache":
        return "unbounded"
    if name != "lru_cache":
        return None
    for keyword in call.keywords if call else ():
        if keyword.arg == "maxsize":
            return ast.unparse(keyword.value)
    return ast.unparse(call.args[0]) if call and call.args else "128"


def noded(annotation: ast.expr | None) -> bool:
    """Whether a parameter's annotation names a syntax node class."""
    if annotation is None:
        return False
    return any(
        isinstance(part, (ast.Attribute, ast.Name))
        and (part.attr if isinstance(part, ast.Attribute) else part.id) in NODES
        for part in ast.walk(annotation)
    )


for path in sorted(ROOT.rglob("*.py")):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        sizes = [size for size in map(cache_of, node.decorator_list) if size is not None]
        params = [
            arg.arg
            for arg in (*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs)
            if noded(arg.annotation)
        ]
        if sizes and params:
            print(
                f"{path.relative_to(ROOT.parent)}:{node.lineno} {node.name} maxsize={sizes[0]} nodes={','.join(params)}"
            )
