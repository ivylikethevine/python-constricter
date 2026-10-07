# SPDX-License-Identifier: MIT
"""An attribute of what an installed class's method returns, read off the call: `capsys.readouterr().out`.

The returned class may be one no file can name (pytest's `CaptureResult`, private to `_pytest`), so
the call alone has no type to write; its attribute's is the method's own return, as far as the
receiver's type arguments bind it: a signature of the method's, returning the attribute's type.
"""

import ast
import re
from typing import TYPE_CHECKING, Final

from constricter.fix.index.atoms import parse_text

if TYPE_CHECKING:
    from collections.abc import Mapping

    from constricter.fix.index.declared import Class, Signature
    from constricter.fix.index.modules import Module

_WORD: Final = re.compile(r"\b\w+\b")


def key(method: str, attribute: str) -> str:
    """Name the entry of an attribute of a method's return, beside the method's own.

    Returns:
      It.

    """
    return f"{method}().{attribute}"


def attributes(
    module: "Module",
    klass: "Class",
    method: str,
    wanted: frozenset[str],
) -> dict[str, tuple["Signature", ...]]:
    """Read the attributes (of `wanted`) of what `klass`'s own `method` returns, as signatures of its.

    For a method of one signature returning an instance of a class its own module declares, that
    class's type parameters bound as the return writes them (`CaptureResult[AnyStr]`'s `out`: an
    `AnyStr`, the receiver's).

    Returns:
      Each attribute's, by name: the method's signature, returning the attribute's type.

    """
    written: tuple[Signature, ...] | None = klass.methods.get(method)
    if written is None or len(written) != 1 or written[0].returns is None or module.declared is None:
        return {}
    returned: ast.expr = parse_text(written[0].returns)
    base: ast.expr = returned.value if isinstance(returned, ast.Subscript) else returned
    # By its name there: one defined under an `if` isn't among the module's names.
    result: Class | None = module.declared.classes.get(base.id) if isinstance(base, ast.Name) else None
    given: list[ast.expr] = []
    if isinstance(returned, ast.Subscript):
        given = list(returned.slice.elts) if isinstance(returned.slice, ast.Tuple) else [returned.slice]
    if result is None or len(given) != len(result.params):
        return {}
    bound: Mapping[str, str] = {
        name: ast.unparse(arg) for (name, _), arg in zip(result.params, given, strict=True)
    }
    return {
        name: (written[0]._replace(returns=_WORD.sub(lambda word: bound.get(word[0], word[0]), text)),)
        for name, text in result.attributes.items()
        if name in wanted
    }
