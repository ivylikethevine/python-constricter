# SPDX-License-Identifier: MIT
"""What iterating a class's instance gives, read from its `__iter__`: the `elements` table's entries."""

import ast
import re
from typing import Final

from stdlib_tables.overloads import Overloads
from stdlib_tables.reading import ClassRef, readable, substituted
from stdlib_tables.stubs import Binding, Found, Function
from stdlib_tables.templates import TYPING

_ITER: Final = "__iter__"
_NEXT: Final = "__next__"
_SELF: Final = "Self"
# What `__iter__` returns that yields its first type argument.
_YIELDING: Final = frozenset({"Iterator", "Iterable", "Generator"})
_NAME: Final = re.compile(r"\w+")


def element(overloads: Overloads, klass: ClassRef) -> str | None:
    """Read what iterating a class's instance gives: its `__iter__`'s `Iterator[T]`'s `T`.

    Where `__iter__` returns `Self`, what `__next__` returns. The class's own, or the nearest
    base's that defines it, that base's type parameters written as the class passes them
    (`deque[_T]`'s is `Sequence[_T]`'s).

    Returns:
      It, as a template its type arguments bind; or `None` if it has none that can be written.

    """
    found: tuple[ast.expr, ClassRef] | None
    if (found := _returned(overloads, klass, _ITER)) is None:
        return None
    yielding: ast.expr
    owner: ClassRef
    yielding, owner = found
    head: Found | None = overloads.reading.ref(
        yielding.value if isinstance(yielding, ast.Subscript) else yielding,
        owner.module,
    )
    if head is None or head.module not in TYPING:
        return None
    if isinstance(yielding, ast.Subscript) and head.name in _YIELDING:
        index: ast.expr = yielding.slice
        found = (index.elts[0] if isinstance(index, ast.Tuple) else index, owner)
    elif head.name == _SELF and (found := _returned(overloads, klass, _NEXT)) is not None:
        owner = found[1]
    else:
        return None
    template: str | None = overloads.template(found[0], owner.module)
    params: list[str] = [param.rstrip("=") for param in overloads.type_parameters(owner) or []]
    if template is None or owner == klass or not set(params).intersection(_NAME.findall(template)):
        return template
    passed: list[str] | None = overloads.base_arguments(klass, owner)
    if passed is None or len(passed) != len(params):
        return None
    return substituted(template, dict(zip(params, passed, strict=True)))


def _returned(overloads: Overloads, klass: ClassRef, name: str) -> tuple[ast.expr, ClassRef] | None:
    """Find what a class's method `name` is declared to return, in the nearest class defining it.

    Returns:
      The annotation and that class; `None` if nothing defines it, or not as one plain method.

    """
    owner: ClassRef
    for owner in overloads.reading.trusted(klass)[0]:
        binding: Binding | None
        if (binding := overloads.reading.body(owner).get(name)) is None:
            continue
        if isinstance(binding, Function) and len(binding.defs) == 1 and readable(binding.defs[0]):
            returns: ast.expr | None = binding.defs[0].returns
            return None if returns is None else (returns, owner)
        return None
    return None
