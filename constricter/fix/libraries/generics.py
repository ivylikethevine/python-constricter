"""A generic standard-library class's members, bound by the receiver's type arguments."""

import ast
from typing import Final

from constricter.fix.core.known import Inference, Known
from constricter.fix.libraries import stdlib
from constricter.fix.libraries.overloads import write

_KIND: Final = "stdlib"


def generic_member(receiver: str, name: str, call: ast.Call | None, known: Known) -> Inference | None:
    """Type a generic standard-library class's own attribute or property, bound by the receiver's type.

    `m.string` on an `re.Match[str]` is a `str`; a method (`call`) is `method_signatures`' to type.

    Returns:
      The inference, or `None` if the tables don't have it, or a type parameter it names is unbound.

    """
    found: tuple[str, str, dict[str, str]] | None = (
        stdlib.generic_attribute(receiver, name, known) if call is None else None
    )
    if found is None:
        return None
    annotation: str | None = write((found[1], found[2]), known)
    return (
        None
        if annotation is None
        else Inference(annotation, f"`{found[0]}.{name}`'s annotation in typeshed", frozenset({_KIND}))
    )


def library_element(receiver: str, known: Known) -> Inference | None:
    """Type what iterating a standard-library class's instance gives, bound by the receiver's type.

    A `for` loop over an `io.TextIOWrapper` binds a `str`, over an `itertools.chain[int]` an `int`.

    Returns:
      The inference, or `None` if the tables don't have it, or a type parameter it names is unbound.

    """
    found: tuple[str, str, dict[str, str]] | None = stdlib.element(receiver, known)
    annotation: str | None = None if found is None else write((found[1], found[2]), known)
    return (
        None
        if found is None or annotation is None
        else Inference(annotation, f"the elements of a `{found[0]}`", frozenset({_KIND}))
    )
