# SPDX-License-Identifier: MIT
"""`--fix` for `with manager as name:`: what the context manager's `__enter__` returns.

`name` is typed as a call to `manager.__enter__()` would be: by the standard-library tables
(`zipfile.ZipFile(path)` gives itself, `tempfile.TemporaryDirectory()` a `str`), a project class's
declared `__enter__`, or an installed package's. A call to one of the module's own functions made a
context manager by `@contextmanager` gives what it declares it yields (`Iterator[T]`'s `T`), as does
one to such a method of its classes, on a receiver whose type is known (`self.defs.entry(key)`).
`open(...)`'s is `constricter.fix.libraries.opened`'s, by its mode.
"""

import ast
from collections import Counter
from collections.abc import Mapping, Sequence
from typing import Final

from constricter.fix.core.known import ImportPlan, Inference, Known
from constricter.fix.libraries import stdlib
from constricter.fix.values.inference import inference
from constricter.rules.annotations import defined_type_vars, is_vague, node_name
from constricter.rules.walked import classes

_ENTER: Final = "__enter__"
_AENTER: Final = "__aenter__"
_NONE: Final = "None"
_MANAGER: Final = ["contextmanager"]  # the one decorator that makes a generator function a manager
# What such a function declares it returns: its first argument is what it yields.
_YIELDING: Final = frozenset({"Iterator", "Generator", "Iterable"})
_CALL: Final = "call"  # the fix kind of a function's declared return
_METHOD: Final = "method"  # and of a method's
_SELF: Final = "Self"  # in a method's declared type: its receiver's class, which a base's isn't
_STDLIB: Final = "stdlib"  # the fix kind of what typeshed declares
# `unittest.mock`'s patchers that make a mock, each with how many arguments come before its `new`.
_PATCHES: Final = {"unittest.mock.patch": 1, "unittest.mock.patch.object": 2}
_REPLACEMENTS: Final = frozenset({"new", "new_callable"})  # the keywords that give the mock's replacement
_MOCKS: Final = ("unittest.mock.MagicMock", "unittest.mock.AsyncMock")


def managers(tree: ast.Module) -> dict[str, str]:
    """Map each function `@contextmanager` makes a context manager to what `with` gives of it.

    A plain `def`, defined once, decorated by `contextmanager` alone (however it's imported), that
    declares an `Iterator[T]`, `Generator[T, ...]` or `Iterable[T]`: `T`, unless it's `None`, vague
    or names one of the module's type variables. At the module's top level, or (as `Class.method`)
    directly in a class it defines once: there, not a `T` naming `Self`.

    Returns:
      Each function's name, and `T` as source text.

    """
    type_vars: frozenset[str] = defined_type_vars(tree)
    found: dict[str, str] = _managers(tree.body, "", type_vars)
    nodes: Sequence[ast.ClassDef] = classes(tree)
    owners: Counter[str] = Counter(node.name for node in nodes)
    node: ast.ClassDef
    for node in nodes:
        if owners[node.name] == 1:
            found.update(_managers(node.body, f"{node.name}.", type_vars | {_SELF}))
    return found


def _managers(body: Sequence[ast.stmt], prefix: str, unusable: frozenset[str]) -> dict[str, str]:
    """Find the functions directly in `body` that `@contextmanager` makes context managers (see `managers`).

    `unusable`: the names a yielded type can't be written with.

    Returns:
      Each one's name after `prefix`, and what it yields as source text.

    """
    counts: Counter[str] = Counter(
        stmt.name for stmt in body if isinstance(stmt, ast.FunctionDef | ast.AsyncFunctionDef)
    )
    found: dict[str, str] = {}
    stmt: ast.stmt
    for stmt in body:
        yielded: ast.expr | None
        if (
            isinstance(stmt, ast.FunctionDef)
            and counts[stmt.name] == 1
            and [node_name(decorator) for decorator in stmt.decorator_list] == _MANAGER
            and (yielded := _yielded(stmt.returns)) is not None
            and not unusable & {node_name(node) for node in ast.walk(yielded)}
        ):
            found[f"{prefix}{stmt.name}"] = ast.unparse(yielded)
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


def _patched(manager: ast.expr, known: Known) -> Inference | None:
    """Infer what `with mock.patch(target) as name:` binds: the mock it makes, with no `new` given.

    `unittest.mock.patch` and `patch.object`, however the module names them: a `MagicMock`, or an
    `AsyncMock` for an `async def`, as typeshed declares it.

    Returns:
      The inference, or `None` for any other manager, one given its replacement (`new`,
      `new_callable`, or by position), or a module that can't name both classes.

    """
    func: ast.expr
    args: list[ast.expr]
    keywords: list[ast.keyword]
    match manager:
        case ast.Call(func=func, args=args, keywords=keywords):
            before: int | None = _PATCHES.get(stdlib.resolved(func, known.names.stdlib) or "")
            given: bool = any(isinstance(arg, ast.Starred) for arg in args) or any(
                keyword.arg is None or keyword.arg in _REPLACEMENTS for keyword in keywords
            )
            plan: ImportPlan | None = known.names.plan
            if before is None or len(args) > before or given or plan is None:
                return None
            spelled: list[str | None] = [plan.spell(mock) for mock in _MOCKS]
            return (
                None
                if None in spelled
                else Inference(
                    " | ".join(name for name in spelled if name is not None),
                    "`unittest.mock.patch`'s mock, given no other",
                    frozenset({_STDLIB}),
                )
            )
        case _:
            return None


def entering(manager: ast.expr) -> ast.Call:
    """Write the call a `with` statement makes of its context manager: `manager.__enter__()`.

    Returns:
      It, placed where `manager` is.

    """
    method: ast.Attribute = ast.copy_location(ast.Attribute(manager, _ENTER, ast.Load()), manager)
    return ast.copy_location(ast.Call(method, [], []), manager)


def entered_async(
    manager: ast.expr,
    known: Known,
    declared: Mapping[str, str],
) -> tuple[Inference, list[ast.expr]] | None:
    """Infer what `async with manager as name:` binds `name` to: a standard-library manager's `__aenter__`'s.

    Returns:
      The inference, and the value it rests on; or `None`.

    """
    own: Inference | None = inference(manager, known, declared)
    found: Inference | None = None if own is None else stdlib.awaited_member(own.annotation, _AENTER, known)
    return (
        None if own is None or found is None else (found._replace(kinds=found.kinds | own.kinds), [manager])
    )


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
    receiver: ast.expr
    match manager:
        case ast.Call(func=ast.Name(id=name)) if name in functions and name not in declared:
            yielded: Inference = Inference(
                functions[name],
                f"what `{name}`'s context manager yields",
                frozenset({_CALL}),
            )
            return yielded, []
        case ast.Call(func=ast.Attribute(value=receiver, attr=name)) if any(
            key.endswith(f".{name}") for key in functions
        ):
            owner: Inference | None = inference(receiver, known, declared)
            key: str = (
                "" if owner is None else f"{known.class_side.lineage.definer(owner.annotation, name)}.{name}"
            )
            if owner is not None and key in functions:
                reason: str = f"what `{key}`'s context manager yields"
                return Inference(functions[key], reason, owner.kinds - {"copy"} | {_METHOD}), [receiver]
        case _:
            pass
    patched: Inference | None
    if (patched := _patched(manager, known)) is not None:
        return patched, []
    # A standard-library manager that returns itself gives its own type, its type arguments included.
    own: Inference | None = inference(manager, known, declared)
    found: Inference | None = (
        own._replace(reason=f"{own.reason}, its own context manager")
        if own is not None and stdlib.enters_itself(own.annotation, known)
        else inference(entering(manager), known, declared)
    )
    # What enters as `None` (a `catch_warnings()` that records nothing) binds nothing worth declaring.
    return None if found is None or found.annotation == _NONE else (found, [manager])
