# SPDX-License-Identifier: MIT
"""`--fix` for `open(path, mode)`: the file object it gives, by its literal mode."""

import ast
from typing import Final

from constricter.fix import stdlib
from constricter.fix.known import ImportPlan, Inference, Known

_OPEN: Final = "open"  # the builtin, and the fix kind of what it gives
_IO_OPEN: Final = "io.open"
_ACTIONS: Final = "rwxa"  # exactly one of them in a mode
_MODE_CHARACTERS: Final = "rwxabt+"
_READ: Final = "r"
_BINARY: Final = "b"
_TEXT: Final = "t"
_UPDATE: Final = "+"


def opened(value: ast.expr, known: Known) -> Inference | None:
    """Infer the file object `open(path, mode)` gives, by its mode (a literal, or the default `r`).

    Text modes give an `io.TextIOWrapper`; binary ones an `io.BufferedReader` to read,
    `io.BufferedWriter` to write, and `io.BufferedRandom` for both (`+`). `buffering` or `opener`
    (in a position or by name) decides nothing: unbuffered, it's an `io.FileIO`. Only the builtin
    `open` (or `io.open`), never one the module binds itself.

    Returns:
      The inference (spelled, and imported if it must be, as the module can), or `None`.

    """
    plan: ImportPlan | None = known.names.plan
    func: ast.expr
    args: list[ast.expr]
    keywords: list[ast.keyword]
    match value:
        case ast.Call(func=func, args=[_, *args], keywords=keywords) if plan is not None and (
            (isinstance(func, ast.Name) and func.id == _OPEN and _OPEN not in plan.taken)
            or stdlib.resolved(func, plan.bound) == _IO_OPEN
        ):
            pass
        case _:
            return None
    named: dict[str | None, ast.expr] = {keyword.arg: keyword.value for keyword in keywords}
    mode: ast.expr | None = args[0] if args else named.get("mode")
    text: str | None = (
        "r"
        if mode is None
        else (mode.value if isinstance(mode, ast.Constant) and isinstance(mode.value, str) else None)
    )
    if text is None or len(args) > 1 or {None, "buffering", "opener"} & named.keys():
        return None
    kind: str | None = _file_class(text)
    spelled: str | None = None if kind is None else plan.spell(f"io.{kind}")
    return None if spelled is None else Inference(spelled, f"`open`'s mode `{text}`", frozenset({_OPEN}))


def _file_class(mode: str) -> str | None:
    """Name the `io` class `open` gives for `mode`.

    Returns:
      It, or `None` for a mode that isn't one `open` takes.

    """
    actions: set[str] = set(mode) & set(_ACTIONS)
    if not set(mode) <= set(_MODE_CHARACTERS) or len(actions) != 1 or len(set(mode)) != len(mode):
        return None
    if _BINARY not in mode:
        return "TextIOWrapper"
    if _TEXT in mode:
        return None
    if _UPDATE in mode:
        return "BufferedRandom"
    return "BufferedReader" if _READ in actions else "BufferedWriter"
