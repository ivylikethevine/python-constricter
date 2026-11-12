"""`--fix` for a call of a method that returns one of its parameters as it's given (see `known.Echo`).

`chosen = self.pick(default)`, where every `return` of `pick` gives its `fallback` parameter: the
call is what it passes for `fallback`. A guess (`KIND`): a subclass may override the method, and
the method's own callers may pass it anything.
"""

import ast
from typing import Final

from constricter.fix.core.known import Echo, Inference, Known
from constricter.fix.values.shapes import Infer

KIND: Final = "echoed"  # the guessing mechanism (`FIX_KINDS`)


def echo(receiver: str, name: str, known: Known) -> tuple[str, Echo] | None:
    """Look up a method of a value typed `receiver` that returns one of its parameters as given.

    The receiver's class's own, or the base's in the module that defines it (see `Lineage`).

    Returns:
      The class that defines it, and the parameter; `None` if it isn't one.

    """
    owner: str | None = known.class_side.lineage.definer(receiver, name)
    found: Echo | None = known.returned.echoes.get(owner or "", {}).get(name)
    return None if owner is None or found is None else (owner, found)


def result(receiver: str, name: str, call: ast.Call, known: Known, infer: Infer) -> Inference | None:
    """Type a call of such a method by the argument it passes for the parameter returned.

    Returns:
      The argument's inference, resting on `KIND` too; `None` for any other call, one that passes
      no such argument (the parameter's default, a `*` or a `**`), or one of no known type.

    """
    defined: tuple[str, Echo] | None
    if (defined := echo(receiver, name, known)) is None:
        return None
    given: ast.expr | None = _argument(call, defined[1])
    typed: Inference | None
    if (typed := None if given is None else infer(given)) is None:
        return None
    reason: str = f"what it passes `{defined[0]}.{name}`, which returns its `{defined[1].name}`"
    return Inference(typed.annotation, reason, typed.kinds | {KIND})


def _argument(call: ast.Call, found: Echo) -> ast.expr | None:
    """Find what a call passes a parameter: by its name, or by its place.

    Returns:
      The argument; `None` where a `*` or a `**` may pass it, or nothing does.

    """
    if any(isinstance(arg, ast.Starred) for arg in call.args) or any(
        keyword.arg is None for keyword in call.keywords
    ):
        return None
    keyword: ast.keyword
    for keyword in call.keywords:
        if keyword.arg == found.name:
            return keyword.value
    if found.position is not None and found.position < len(call.args):
        return call.args[found.position]
    return None
