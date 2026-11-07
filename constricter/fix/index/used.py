"""What a checked module uses of others: the names it calls and passes, the members it takes.

Read once as the module is indexed (`modules.read`), so a class's members another file can use are known.
"""

import ast
import re
from collections.abc import Iterator, Mapping
from typing import Final, cast

from constricter.fix.core.known import Origin
from constricter.fix.core.signatures import AWAIT
from constricter.fix.values import entered
from constricter.source.annotations import dotted
from constricter.source.keys import key, optional
from constricter.source.walked import of_type

_UNNAMED: Final = frozenset({"__call__", "__enter__"})  # members a statement takes without naming them
_GET: Final = "get"
DOTTED: Final = re.compile(r"[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)+")  # a dotted name, as text writes one


def called(tree: ast.Module, names: Mapping[str, Origin]) -> frozenset[str]:
    """Find what the module calls through its top-level names: `f()`, `u.f()`, `pkg.util.f()`.

    Returns:
      Each callee, as written.

    """
    callees: Iterator[str | None] = (
        dotted(node.func) for node in cast("list[ast.Call]", of_type(tree, ast.Call))
    )
    return frozenset(callee for callee in callees if callee is not None and callee.partition(".")[0] in names)


def passed(tree: ast.Module, names: Mapping[str, Origin]) -> frozenset[str]:
    """Find what the module passes as an argument through its top-level names: `np.float64`, `Row`.

    Returns:
      Each, as written.

    """
    arguments: Iterator[str | None] = (
        dotted(argument)
        for node in cast("list[ast.Call]", of_type(tree, ast.Call))
        for argument in (*node.args, *(keyword.value for keyword in node.keywords))
    )
    return frozenset(name for name in arguments if name is not None and name.partition(".")[0] in names)


def method_calls(tree: ast.Module) -> frozenset[str]:
    """Name the methods the module calls on anything: `astype` in `a.astype(x)`, and a `with`'s `__enter__`.

    Returns:
      Them.

    """
    entering: bool = any(
        item.optional_vars is not None
        for node in cast("list[ast.With]", of_type(tree, ast.With))
        for item in node.items
    )
    return frozenset(
        node.func.attr
        for node in cast("list[ast.Call]", of_type(tree, ast.Call))
        if isinstance(node.func, ast.Attribute)
    ) | (frozenset({entered.ENTER}) if entering else frozenset[str]())


def attributes(tree: ast.Module) -> frozenset[str]:
    """Name the attributes the module takes of anything: `x` in `a.x`, `astype` in `a.astype(x)`.

    And those its statements take without naming them: a call's `__call__`, a `with`'s `__enter__`;
    and the literal keys it reads of anything (`d["x"]`, `d.get("x")`), as a `TypedDict`'s are held
    (see `keys.key`, `keys.optional`), and the methods it awaits a call of, as an `async def`'s are held.

    Returns:
      Them: all of another file's class's members it can use.

    """
    named: frozenset[str] = frozenset(
        node.attr for node in cast("list[ast.Attribute]", of_type(tree, ast.Attribute))
    )
    indexes: list[ast.expr] = [
        node.slice for node in cast("list[ast.Subscript]", of_type(tree, ast.Subscript))
    ]
    indexes.extend(
        node.args[0]
        for node in cast("list[ast.Call]", of_type(tree, ast.Call))
        if node.args and isinstance(node.func, ast.Attribute) and node.func.attr == _GET
    )
    awaited: frozenset[str] = frozenset(
        AWAIT + node.value.func.attr
        for node in cast("list[ast.Await]", of_type(tree, ast.Await))
        if isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Attribute)
    )
    keys: frozenset[str] = frozenset(
        spelled(index.value)
        for index in indexes
        if isinstance(index, ast.Constant) and isinstance(index.value, str)
        for spelled in (key, optional)
    )
    return named | keys | awaited | _quoted(tree) | _UNNAMED


def _quoted(tree: ast.Module) -> frozenset[str]:
    """Name the attributes the module's quoted annotations take: `Study` in `study: "optuna.Study"`.

    Returns:
      Them.

    """
    functions: list[ast.FunctionDef | ast.AsyncFunctionDef] = cast(
        "list[ast.FunctionDef | ast.AsyncFunctionDef]",
        of_type(tree, ast.FunctionDef, ast.AsyncFunctionDef),
    )
    annotations: list[ast.expr | None] = [
        *(node.annotation for node in cast("list[ast.arg]", of_type(tree, ast.arg))),
        *(node.annotation for node in cast("list[ast.AnnAssign]", of_type(tree, ast.AnnAssign))),
        *(node.returns for node in functions),
    ]
    return frozenset(
        part
        for annotation in annotations
        if annotation is not None
        for node in ast.walk(annotation)
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
        for dotted in cast("list[str]", DOTTED.findall(node.value))
        for part in dotted.split(".")[1:]
    )
