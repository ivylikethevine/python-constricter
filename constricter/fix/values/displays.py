# SPDX-License-Identifier: MIT
"""A list, set, tuple or dict display's type, from its elements' types.

Where a list's, set's or dict's differ, they're joined into a union (`[1, "a"]` is a
`list[int | str]`): a guess, since a checker joins them too, but not always to the same union (mypy
to their common base).
"""

import ast
import re
from collections.abc import Sequence
from typing import Final

from constricter.fix.core.known import Inference

JOINED: Final = "joined"  # the fix kind (and guessing mechanism) of a display's joined element types
_MOST_JOINED: Final = 3  # the most types a display's elements are joined from
_PLAIN: Final = re.compile(r"[A-Za-z_][\w.]*")  # a type that's a name alone
_UNION_BAR: Final = " | "
_NONE: Final = "None"


def element_type(
    elements: Sequence[ast.expr | None],
    parts: Sequence[Inference | None],
) -> tuple[str | None, bool]:
    """Type a display's `elements` as one: the type they all have (`parts`), or their types joined.

    Returns:
      The type (`None` if there's none to write), and whether it's joined from several.

    """
    uniform: str | None = _uniform(parts)
    return (uniform, False) if uniform is not None else (_joint(elements, parts), True)


def tuple_type(parts: Sequence[Inference | None], max_length: int) -> str | None:
    """Type a tuple display from its elements' types.

    One type per element (`tuple[int, str]`), up to `max_length` of them; a longer one (LVA011's)
    is `tuple[T, ...]` when every element is a `T`, and nothing when they differ: its fields need
    names, not a list of types. One that unpacks (`max_length` below 0) is always the longer kind.

    Returns:
      The annotation, or `None` if an element's type isn't known or a long tuple's differ.

    """
    known_parts: list[Inference] = [part for part in parts if part is not None]
    if len(known_parts) != len(parts):
        return None
    if len(parts) <= max_length:
        return f"tuple[{', '.join(part.annotation for part in known_parts)}]"
    element: str | None = _uniform(parts)
    return None if element is None else f"tuple[{element}, ...]"


def _uniform(parts: Sequence[Inference | None]) -> str | None:
    """Find the one type every element has.

    Returns:
      That type, or `None` if they differ or any is unknown.

    """
    types: set[str | None] = {None if part is None else part.annotation for part in parts}
    return next(iter(types)) if len(types) == 1 else None


def _joint(elements: Sequence[ast.expr | None], parts: Sequence[Inference | None]) -> str | None:
    """Join a display's `elements`' types (`parts`) where they differ: `int | str`, `None` last.

    Up to `_MOST_JOINED` of them, each a plain name (a builtin's, a class's): a union of unions or
    of containers is better left to the author. A literal `None` among them is `None`.

    Returns:
      The union, or `None` if any is unknown, or they're too many or not plain.

    """
    found: list[str | None] = [
        _NONE if isinstance(element, ast.Constant) and element.value is None else part and part.annotation
        for element, part in zip(elements, parts, strict=True)
    ]
    types: list[str] = list(dict.fromkeys(each for each in found if each is not None))
    if None in found or not 1 < len(types) <= _MOST_JOINED:
        return None
    if not all(_PLAIN.fullmatch(each) for each in types):
        return None
    return _UNION_BAR.join(sorted(types, key=lambda each: each == _NONE))
