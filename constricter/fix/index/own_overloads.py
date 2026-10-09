# SPDX-License-Identifier: MIT
"""A checked file's functions defined with `@overload`, for the calls their arguments decide.

Their signatures are read as an installed package's are (see `constricter.fix.index.stubbed`), but
for what each returns: a type the calling file writes as it would any other checked file's.
"""

import ast

from constricter.fix.core.known import SPELLED, Guarded
from constricter.fix.core.signatures import ReadSignature
from constricter.fix.index import project
from constricter.fix.index.declared import Signature
from constricter.fix.index.modules import Index, Module


def written(module: Module, name: str) -> tuple[Signature, ...]:
    """Find a function's signatures as written: an installed module's, or a checked file's overloads.

    Returns:
      Them.

    """
    return module.overloads[name] if module.declared is None else module.declared.signatures[name]


def spelled(
    catalog: Index,
    target: Module,
    defined: tuple[Module, str],
    read: tuple[ReadSignature, ...],
    guarded: dict[str, Guarded] | None,
) -> tuple[ReadSignature, ...]:
    """Write a checked file's overloads' returns as `target` can (see `project.spelled_in`).

    Each is the type itself then (`SPELLED`), not a template: no overload of a checked file's binds
    a type variable.

    Returns:
      The signatures; none if a return isn't declared, or `target` can't write it (a type
      variable, a generic class without its arguments, a name it binds otherwise).

    """
    found: list[ReadSignature] = []
    names: dict[str, Guarded] = dict(guarded or {})
    signature: Signature
    each: ReadSignature
    for signature, each in zip(defined[0].overloads[defined[1]], read, strict=True):
        text: str | None = (
            None
            if signature.returns is None
            else project.spelled_in(catalog, target, defined[0], _unquoted(signature.returns), names)
        )
        if text is None:
            return ()
        found.append(each._replace(returns=f"{SPELLED}{text}"))
    if guarded is not None:
        guarded.update(names)
    return tuple(found)


def _unquoted(returns: str) -> str:
    """Read a return written in quotes (`-> "Frame"`) as the type it names.

    Returns:
      Its text; any other return as it is.

    """
    node: ast.expr = ast.parse(returns, mode="eval").body
    return node.value if isinstance(node, ast.Constant) and isinstance(node.value, str) else returns
