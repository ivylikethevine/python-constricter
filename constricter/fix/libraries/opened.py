# SPDX-License-Identifier: MIT
"""`--fix` for `open(path, mode)` and `path.open(mode)`: the file object it gives, by its literal mode."""

import ast
from typing import Final

from constricter.fix.core.known import ImportPlan, Inference, Known
from constricter.fix.libraries import stdlib

_OPEN: Final = "open"  # the builtin, and the fix kind of what it gives
# The standard library's functions that open a file as the builtin does, by the mode after their
# first argument.
_OPENERS: Final = frozenset({"io.open", "_io.open", "os.fdopen"})
_READERS: Final = frozenset({"tokenize.open"})  # those that open one as text, whatever they're given
# Those that give an `io.TextIOWrapper` for a text mode alone (the tables have their other modes).
_COMPRESSED: Final = frozenset({"gzip.open", "bz2.open", "lzma.open"})
_SHELF: Final = "shelve.open"  # typeshed's `Shelf[Any]`: written where `vague` lets it be
_ACTIONS: Final = "rwxa"  # exactly one of them in a mode
_MODE_CHARACTERS: Final = "rwxabt+"
_READ: Final = "r"
_BINARY: Final = "b"
_TEXT: Final = "t"
_UPDATE: Final = "+"
_WRAPPER: Final = "io.TextIOWrapper"


def opened(value: ast.expr, known: Known) -> Inference | None:
    """Infer the file object `open(path, mode)` gives, by its mode (a literal, or the default `r`).

    Text modes give an `io.TextIOWrapper`; binary ones an `io.BufferedReader` to read,
    `io.BufferedWriter` to write, and `io.BufferedRandom` for both (`+`). `buffering` or `opener`
    (in a position or by name) decides nothing: unbuffered, it's an `io.FileIO`. The builtin `open`,
    never one the module binds itself, and the standard library's own that open as it does
    (`io.open`, `os.fdopen`); `tokenize.open`, always text; `gzip.open`, `bz2.open` and `lzma.open`
    given a text mode; and `shelve.open`, a `shelve.Shelf[Any]`.

    Returns:
      The inference (spelled, and imported if it must be, as the module can), or `None`.

    """
    plan: ImportPlan | None = known.names.plan
    func: ast.expr
    args: list[ast.expr]
    keywords: list[ast.keyword]
    match value:
        case ast.Call(func=func, args=[_, *args], keywords=keywords) if plan is not None:
            pass
        case _:
            return None
    if isinstance(func, ast.Name) and func.id == _OPEN and _OPEN not in plan.taken:
        return _by_mode(args, keywords, plan)
    origin: str | None
    if (origin := stdlib.resolved(func, known.names.stdlib)) in _OPENERS:
        return _by_mode(args, keywords, plan)
    return None if origin is None else _by_opener(origin, _mode(args, keywords), plan)


def _by_opener(origin: str, mode: str | None, plan: ImportPlan) -> Inference | None:
    """Infer what a standard-library function that opens a file its own way gives (see `opened`).

    `mode`: its literal mode, as `_mode` reads it.

    Returns:
      The inference, or `None` for any other function, or a mode that isn't a text one.

    """
    spelled: str | None = None
    if origin == _SHELF:
        parts: tuple[str | None, str | None] = (plan.spell("shelve.Shelf"), plan.spell("typing.Any"))
        spelled = None if None in parts else f"{parts[0]}[{parts[1]}]"
    elif origin in _READERS or (
        origin in _COMPRESSED and mode is not None and _TEXT in mode and _file_class(mode) is not None
    ):
        spelled = plan.spell(_WRAPPER)
    reason: str = f"`{origin}`'s return type in typeshed"
    return None if spelled is None else Inference(spelled, reason, frozenset({"stdlib"}))


def opened_path(receiver: str, value: ast.Call, known: Known) -> Inference | None:
    """Infer the file object `path.open(mode)` gives on a `pathlib` path, as `open(path, mode)`'s is.

    `receiver`: the path's type, as the module spells it.

    Returns:
      The inference, or `None` for any other call or receiver.

    """
    plan: ImportPlan | None = known.names.plan
    attr: str
    args: list[ast.expr]
    keywords: list[ast.keyword]
    match value:
        case ast.Call(func=ast.Attribute(attr=attr), args=args, keywords=keywords) if (
            attr == _OPEN and plan is not None and stdlib.is_path(receiver, known)
        ):
            return _by_mode(args, keywords, plan)
        case _:
            return None


def _mode(args: list[ast.expr], keywords: list[ast.keyword]) -> str | None:
    """Read a call's literal mode from the arguments after its path: the first, or the one named `mode`.

    Returns:
      It (`r`, with none given), or `None` if it isn't a string literal.

    """
    named: dict[str | None, ast.expr] = {keyword.arg: keyword.value for keyword in keywords}
    mode: ast.expr | None
    if (mode := args[0] if args else named.get("mode")) is None:
        return _READ
    return mode.value if isinstance(mode, ast.Constant) and isinstance(mode.value, str) else None


def _by_mode(args: list[ast.expr], keywords: list[ast.keyword], plan: ImportPlan) -> Inference | None:
    """Infer a file object by the arguments after its path: its mode, first or by name.

    Returns:
      The inference, or `None` (see `opened`).

    """
    text: str | None = _mode(args, keywords)
    if text is None or len(args) > 1 or {None, "buffering", "opener"} & {k.arg for k in keywords}:
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
