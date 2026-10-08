# SPDX-License-Identifier: MIT
"""Wider types than a value's own, written only where `fix-widen` asks, each line marked (`MARK`).

A marked annotation is `--fix`'s own: it isn't LVA005, `--coverage` counts it apart, and a later
`--fix` replaces it once the value's type is known.
"""

import ast
import re
from collections.abc import Collection, Sequence
from functools import lru_cache
from typing import Final

from constricter.fix.core.known import ImportPlan, Inference
from constricter.fix.values import fills
from constricter.offences import EMPTY_CONTAINERS, MARK, MIXED_CONTAINERS, UNTYPED_PARAMETERS
from constricter.rules.syntax import FunctionDef
from constricter.rules.walked import walk

ANY: Final = "typing.Any"
_RECEIVERS: Final = frozenset({"self", "cls"})
# The mark, ending its line, with the space before it: what a replaced widening's fix deletes.
_MARKED: Final = re.compile(rf"[ \t]*{re.escape(MARK)}(?=[ \t]*[\r\n]*$)")


def marks(lines: Sequence[str]) -> dict[int, tuple[int, int]]:
    """Find the lines a widening marked.

    Returns:
      Each one's number (from 1), and the mark's columns in it (UTF-8 bytes, as `ast` counts).

    """
    found: dict[int, tuple[int, int]] = {}
    number: int
    line: str
    for number, line in enumerate(lines, 1):
        marked: re.Match[str] | None
        if (marked := _MARKED.search(line) if MARK in line else None) is not None:
            start: int = len(line[: marked.start()].encode())
            found[number] = (start, start + len(marked.group().encode()))
    return found


@lru_cache(maxsize=64)  # asked of each of a function's assignments with no fix
def untyped_parameters(function: FunctionDef) -> frozenset[str]:
    """Name a function's parameters nothing types: no annotation, no default, never bound again.

    A checker takes each for anything, wherever it's read. Not `*args` or `**kwargs`, nor a
    method's `self` or `cls`, which is its class's.

    Returns:
      Them.

    """
    args: ast.arguments = function.args
    positional: list[ast.arg] = [*args.posonlyargs, *args.args]
    plain: int = len(positional) - len(args.defaults)
    defaulted: set[str] = {arg.arg for arg in positional[plain:]}
    defaulted.update(
        arg.arg for arg, default in zip(args.kwonlyargs, args.kw_defaults, strict=True) if default
    )
    rebound: set[str] = {
        node.id
        for node in walk(function)
        if isinstance(node, ast.Name) and not isinstance(node.ctx, ast.Load)
    }
    return frozenset(
        arg.arg
        for arg in (*positional, *args.kwonlyargs)
        if arg.annotation is None and arg.arg not in defaulted | rebound | _RECEIVERS
    )


def wider(
    function: FunctionDef | None,
    bound: tuple[ast.Name, ast.expr],
    typed: Collection[str],
    plan: ImportPlan | None,
) -> Inference | None:
    """Type a name `bound` to what comes of an untyped parameter of `function` as `Any`.

    A copy of it (`x = param`), or its method's call (`y = param.read()`), all on the name's line
    (the mark ends it); not one of `typed`, which something gives a type after all. What every
    checker takes it for already.

    Returns:
      The inference, or `None`: also where the module (`plan`) can't name `Any`.

    """
    target: ast.Name
    value: ast.expr
    target, value = bound
    if function is None or plan is None or value.end_lineno != target.lineno:
        return None
    name: str
    match value:
        case ast.Name(id=name) | ast.Call(func=ast.Attribute(value=ast.Name(id=name))) if (
            name in untyped_parameters(function) and name not in typed
        ):
            spelled: str | None = plan.spell(ANY)
            reason: str = f"what comes of `{name}`, a parameter no annotation types"
            return None if spelled is None else Inference(spelled, reason, frozenset({UNTYPED_PARAMETERS}))
        case _:
            return None


def container(value: ast.expr, plan: ImportPlan, kinds: Collection[str]) -> Inference | None:
    """Type a container whose elements aren't known with `Any` for them: `list[Any]`, `dict[str, Any]`.

    An empty one nothing in sight fills (`[]`, `dict()`: kind `empty-containers`), or a display
    whose elements' types differ or aren't known (`[1, "a"]`, `(x, y)`: `mixed-containers`); a dict
    display's keys are `str` where each is a string. Only the kinds among `kinds`.

    Returns:
      The inference, or `None`: for any other value, or where the module (`plan`) can't name `Any`.

    """
    empty: str | None = fills.empty(value)
    kind: str = EMPTY_CONTAINERS if empty is not None else MIXED_CONTAINERS
    spelled: str | None
    if (spelled := plan.spell(ANY) if kind in kinds else None) is None:
        return None
    keys: list[ast.expr | None]
    annotation: str | None
    match value:
        case ast.List(elts=[_, *_]):
            annotation = f"list[{spelled}]"
        case ast.Set():
            annotation = f"set[{spelled}]"
        case ast.Tuple(elts=[_, *_]):
            annotation = f"tuple[{spelled}, ...]"
        case ast.Dict(keys=[_, *_] as keys):
            texts: bool = all(isinstance(key, ast.Constant) and isinstance(key.value, str) for key in keys)
            annotation = f"dict[{'str' if texts else spelled}, {spelled}]"
        case _:
            annotation = {"list": f"list[{spelled}]", "set": f"set[{spelled}]"}.get(
                empty or "",
                f"dict[{spelled}, {spelled}]" if empty else None,
            )
    if annotation is None:
        return None
    reason: str = "an empty container nothing fills" if empty else "a display of mixed or unknown elements"
    return Inference(annotation, reason, frozenset({kind}))
