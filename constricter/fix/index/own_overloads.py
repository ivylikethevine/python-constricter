"""A checked file's functions defined with `@overload`, or returning the class passed (`type[T]`), for calls.

Their signatures are read as an installed package's are (see `constricter.fix.index.stubs.stubbed`), but
for what each returns: a type the calling file writes as it would any other checked file's.
"""

import ast

from constricter.fix.core.known import SPELLED, Guarded
from constricter.fix.core.signatures import CLASS_BINDS, ReadSignature
from constricter.fix.index import spelling
from constricter.fix.index.modules import Index, Module
from constricter.fix.index.stubs.declared import Signature


def written(module: Module, name: str) -> tuple[Signature, ...]:
    """Find a function's signatures as written: an installed module's, or a checked file's overloads.

    Returns:
      Them.

    """
    return module.signatures[name]


def spelled(
    catalog: Index,
    target: Module,
    defined: tuple[Module, str],
    read: tuple[ReadSignature, ...],
    guarded: dict[str, Guarded] | None,
) -> tuple[ReadSignature, ...]:
    """Write a checked file's overloads' returns as `target` can (see `spelling.spelled_in`).

    Each is the type itself then (`SPELLED`), not a template, but for a type variable alone that a
    parameter binds to the class a call passes (`kind: type[T]) -> T`): a template, the class as the
    call writes it.

    Returns:
      The signatures; none if a return isn't declared, or `target` can't write it (any other type
      variable, a generic class without its arguments, a name it binds otherwise).

    """
    found: list[ReadSignature] = []
    names: dict[str, Guarded] = dict(guarded or {})
    signature: Signature
    each: ReadSignature
    for signature, each in zip(defined[0].overloads[defined[1]], read, strict=True):
        if _class_bound(each):
            found.append(each)
            continue
        text: str | None = (
            None
            if signature.returns is None
            else spelling.spelled_in(
                catalog.modules,
                (target, defined[0]),
                _unquoted(signature.returns),
                names,
            )
        )
        if text is None:
            return ()
        found.append(each._replace(returns=f"{SPELLED}{text}"))
    if guarded is not None:
        guarded.update(names)
    return tuple(found)


def _class_bound(read: ReadSignature) -> bool:
    """Check whether a signature returns a type variable alone that a parameter's `type[...]` binds.

    Returns:
      Whether it does.

    """
    return read.returns is not None and any(
        accepts is not None and accepts.get(CLASS_BINDS) == read.returns for *_, accepts in read.params
    )


def _unquoted(returns: str) -> str:
    """Read a return written in quotes (`-> "Frame"`) as the type it names.

    Returns:
      Its text; any other return as it is.

    """
    node: ast.expr = ast.parse(returns, mode="eval").body
    return node.value if isinstance(node, ast.Constant) and isinstance(node.value, str) else returns
