"""A function's declared return, as every call of it has it: its own, or the one its overloads agree on."""

import ast
from collections.abc import Sequence
from functools import lru_cache
from typing import Final, cast

from constricter.source.annotations import is_vague, node_name
from constricter.source.quoted import written
from constricter.source.syntax import declared_return

OVERLOADS: Final = frozenset({"overload"})  # an overload's decorator, which its implementation lacks


# By the function alone: each class's body is read for its methods, its properties, its
# classmethods and those held back, and a function's declared return is the same to them all.
@lru_cache(maxsize=4096)
def usable_return(func: ast.FunctionDef | ast.AsyncFunctionDef) -> tuple[str, bool] | None:
    """Read the return type `func` declares, if its calls always have it.

    Returns:
      Its annotation as source text, and whether it has a vague part (`tuple[Row, dict[str, Any]]`,
      `Any`); `None` for a generic function, no return, or `None`.

    """
    declared: ast.expr | None = declared_return(func)
    if (
        cast("object", getattr(func, "type_params", ()))  # Python 3.12+'s `def f[T]()`
        or declared is None
        or (isinstance(declared, ast.Constant) and declared.value is None)
    ):
        return None
    return written(declared), is_vague(declared)


def agreed(defs: Sequence[ast.FunctionDef | ast.AsyncFunctionDef]) -> tuple[str, bool] | None:
    """Read the one return a function's overloads all declare, its implementation the same or none.

    `def from_dict(...)`, each `@overload` of it `-> Self`: whichever a call matches, it's that.

    Returns:
      It, and whether it has a vague part; `None` where they differ, or a definition before the
      last isn't an `@overload` (a redefinition), or the last is.

    """
    overloads: Sequence[ast.FunctionDef | ast.AsyncFunctionDef] = defs[:-1]
    if not all(overloaded(each) for each in overloads) or overloaded(defs[-1]):
        return None
    returns: set[tuple[str, bool] | None] = {usable_return(each) for each in overloads}
    found: tuple[str, bool] | None = returns.pop() if len(returns) == 1 else None
    if found is None or (defs[-1].returns is not None and usable_return(defs[-1]) != found):
        return None
    return found


def overloaded(func: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    """Check whether a function is decorated `@overload` (`typing`'s, however it's spelled).

    Returns:
      Whether it is.

    """
    return any(node_name(decorator) in OVERLOADS for decorator in func.decorator_list)
