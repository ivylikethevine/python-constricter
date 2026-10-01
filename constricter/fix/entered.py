# SPDX-License-Identifier: MIT
"""`--fix` for `with manager as name:`: what the context manager's `__enter__` returns.

`name` is typed as a call to `manager.__enter__()` would be: by the standard-library tables
(`zipfile.ZipFile(path)` gives itself, `tempfile.TemporaryDirectory()` a `str`), a project class's
declared `__enter__`, or an installed package's. A call to one of the module's own functions made a
context manager by `@contextmanager` gives what it declares it yields (`Iterator[T]`'s `T`).
`open(...)`'s is `constricter.fix.opened`'s, by its mode.
"""

import ast
from collections import Counter
from collections.abc import Mapping
from typing import Final

from constricter.fix import stdlib
from constricter.fix.inference import inference
from constricter.fix.known import Inference, Known
from constricter.rules.annotations import defined_type_vars, is_vague, node_name

_ENTER: Final = "__enter__"
_MANAGER: Final = ["contextmanager"]  # the one decorator that makes a generator function a manager
# What such a function declares it returns: its first argument is what it yields.
_YIELDING: Final = frozenset({"Iterator", "Generator", "Iterable"})
_CALL: Final = "call"  # the fix kind of a function's declared return


def managers(tree: ast.Module) -> dict[str, str]:
    """Map each top-level function `@contextmanager` makes a context manager to what `with` gives of it.

    A plain `def`, defined once, decorated by `contextmanager` alone (however it's imported), that
    declares an `Iterator[T]`, `Generator[T, ...]` or `Iterable[T]`: `T`, unless it's `None`, vague
    or names one of the module's type variables.

    Returns:
      Each function's name, and `T` as source text.

    """
    counts: Counter[str] = Counter(
        stmt.name for stmt in tree.body if isinstance(stmt, ast.FunctionDef | ast.AsyncFunctionDef)
    )
    type_vars: frozenset[str] = defined_type_vars(tree)
    found: dict[str, str] = {}
    stmt: ast.stmt
    for stmt in tree.body:
        yielded: ast.expr | None
        if (
            isinstance(stmt, ast.FunctionDef)
            and counts[stmt.name] == 1
            and [node_name(decorator) for decorator in stmt.decorator_list] == _MANAGER
            and (yielded := _yielded(stmt.returns)) is not None
            and not type_vars & {node.id for node in ast.walk(yielded) if isinstance(node, ast.Name)}
        ):
            found[stmt.name] = ast.unparse(yielded)
    return found


def _yielded(returns: ast.expr | None) -> ast.expr | None:
    """Read what a generator function's declared return says it yields.

    Returns:
      `Iterator[T]`'s `T`, or `None` for any other annotation, a `None`, a string or a vague `T`.

    """
    index: ast.expr
    match returns:
        case ast.Subscript(slice=index) if node_name(returns.value) in _YIELDING:
            first: ast.expr = index.elts[0] if isinstance(index, ast.Tuple) and index.elts else index
            return None if isinstance(first, ast.Constant | ast.Tuple) or is_vague(first) else first
        case _:
            return None


def entering(manager: ast.expr) -> ast.Call:
    """Write the call a `with` statement makes of its context manager: `manager.__enter__()`.

    Returns:
      It, placed where `manager` is.

    """
    method: ast.Attribute = ast.copy_location(ast.Attribute(manager, _ENTER, ast.Load()), manager)
    return ast.copy_location(ast.Call(method, [], []), manager)


def entered(
    manager: ast.expr,
    known: Known,
    declared: Mapping[str, str],
    functions: Mapping[str, str],
) -> tuple[Inference, list[ast.expr]] | None:
    """Infer what `with manager as name:` binds `name` to.

    `declared`: the scope's typed names; `functions`: the module's `managers`.

    Returns:
      The inference, and the values it rests on (a guess about one makes it a guess); or `None`.

    """
    name: str
    match manager:
        case ast.Call(func=ast.Name(id=name)) if name in functions and name not in declared:
            yielded: Inference = Inference(
                functions[name],
                f"what `{name}`'s context manager yields",
                frozenset({_CALL}),
            )
            return yielded, []
        case _:
            pass
    # A standard-library manager that returns itself gives its own type, its type arguments included.
    own: Inference | None = inference(manager, known, declared)
    found: Inference | None = (
        own._replace(reason=f"{own.reason}, its own context manager")
        if own is not None and stdlib.enters_itself(own.annotation, known)
        else inference(entering(manager), known, declared)
    )
    return None if found is None else (found, [manager])
