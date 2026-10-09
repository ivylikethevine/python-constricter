# SPDX-License-Identifier: MIT
"""`--fix` for `os.walk(top)`: what a loop over it binds, by `top`'s type.

Its return (`Iterator[tuple[AnyStr, list[AnyStr], list[AnyStr]]]`) nests deeper than the tables hold.
"""

import ast
from collections.abc import Callable
from typing import Final, TypeAlias

from constricter.fix.core.known import Inference, Known
from constricter.fix.libraries import stdlib

_WALK: Final = "os.walk"
_STR: Final = "str"
_BYTES: Final = "bytes"
_KINDS: Final = frozenset({"loop", "stdlib"})
_Infer: TypeAlias = Callable[[ast.expr], Inference | None]


def walked(iterable: ast.expr, known: Known, infer: _Infer) -> Inference | None:
    """Infer what a loop over `os.walk(top)` binds: a directory's path, its directories' names and its files'.

    A `str` and two lists of them, where `top` is a `str` or a `pathlib` path; `bytes`, where it's
    a `bytes`. `infer` types `top`.

    Returns:
      The tuple's annotation and its reason; `None` for any other value, or a `top` of no such type.

    """
    func: ast.expr
    top: ast.expr
    match iterable:
        case ast.Call(func=func, args=[top, *_]) if stdlib.resolved(func, known.names.stdlib) == _WALK:
            found: Inference | None
            if (found := infer(top)) is None:
                return None
            name: str | None = _BYTES if found.annotation == _BYTES else None
            if found.annotation == _STR or stdlib.is_path(found.annotation, known):
                name = _STR
            if name is None:
                return None
            return Inference(
                f"tuple[{name}, list[{name}], list[{name}]]",
                "`os.walk`, which yields a directory's path and its entries' names",
                found.kinds | _KINDS,
            )
        case _:
            return None
