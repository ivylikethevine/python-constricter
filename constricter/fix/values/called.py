"""`--fix` for a call of a value whose type says what calling it gives.

A local, an attribute or anything else typed `Callable[..., R]` gives `R` (`handler(schema)`,
`self.handler(schema)`); one typed `type[C]` constructs a `C` (`cls()` in a classmethod,
`type(self)()`), as does `__new__` given one (`cls.__new__(cls)`, `object.__new__(cls)`); and an
instance of a class that declares `__call__`, what that returns. Not a callable that may be `None`
(a union's call is narrowed first), nor an `R` that is `None`.

And a call typed by its callee's name alone (`typed_call`): a checked file's function's declared
return, a fixed-return builtin's, or a class it's taken to construct, by its capitalised name
(`constructs`).
"""

import ast
from collections.abc import Callable, Mapping
from typing import Final, TypeAlias

from constricter.fix.core.known import ImportPlan, Inference, Known
from constricter.fix.libraries import stdlib
from constricter.fix.values.members import member, parsed
from constricter.fix.values.returns import BUILTIN_RETURNS
from constricter.offences import CONSTRUCTOR
from constricter.rules.annotations import GENERICS, dotted, node_name

_Infer: TypeAlias = Callable[[ast.expr], Inference | None]
_CALLABLE: Final = "Callable"
_TYPE: Final = frozenset({"type", "Type"})
_CALL: Final = "__call__"
NEW: Final = "__new__"  # given a class, makes one of it, whatever it's called on
_KIND: Final = frozenset({"call"})  # the fix kind of a declared return


def result(call: ast.Call, known: Known, declared: Mapping[str, str], infer: _Infer) -> Inference | None:
    """Infer a call of a value whose type is known, by what that type's call gives.

    `declared`: the scope's typed names; `infer` types any other callee (`self.handler`, `type(self)`).

    Returns:
      The inference, what typed a callee that isn't a plain local among its kinds; or `None` for a
      callee of no known type, or a type whose call says nothing.

    """
    func: ast.expr = call.func
    if isinstance(func, ast.Name):
        return None if func.id not in declared else _returned(declared[func.id], func.id, call, known)
    if isinstance(func, ast.Attribute) and func.attr == NEW and call.args:
        return _made(call.args[0], known, infer)
    callee: Inference | None = infer(func)
    found: Inference | None = (
        None if callee is None else _returned(callee.annotation, ast.unparse(func), call, known)
    )
    return None if callee is None or found is None else found._replace(kinds=found.kinds | callee.kinds)


def _made(given: ast.expr, known: Known, infer: _Infer) -> Inference | None:
    """Infer `__new__(given, ...)`: an instance of the class `given` is.

    Returns:
      A `type[C]`'s `C`, or the class `given` names (one the module knows, and binds no other way);
      `None` for anything else.

    """
    spelled: str = ast.unparse(given)
    plan: ImportPlan | None = known.names.plan
    if spelled in known.classes and plan is not None and spelled.partition(".")[0] not in plan.values:
        return Inference(spelled, f"`{NEW}` of `{spelled}`", _KIND)
    found: Inference | None = infer(given)
    made: ast.expr | None = None if found is None else _constructed(parsed(found.annotation))
    if found is None or made is None:
        return None
    reason: str = f"`{NEW}` of `{spelled}`, a `{found.annotation}`"
    return Inference(ast.unparse(made), reason, found.kinds - {"copy"} | _KIND)


def _constructed(callee: ast.expr) -> ast.expr | None:
    """Read the class a `type[C]` constructs.

    Returns:
      `C`, or `None` for any other type, or a `C` in quotes.

    """
    head: ast.expr
    made: ast.expr
    match callee:
        case ast.Subscript(value=head, slice=made) if node_name(head) in _TYPE:
            return None if isinstance(made, ast.Constant) else made
        case _:
            return None


def _returned(callee: str, spelled: str, call: ast.Call, known: Known) -> Inference | None:
    """Infer what calling a value typed `callee` (written `spelled`) gives.

    Returns:
      A `Callable`'s return, a `type[C]`'s `C`, or its class's `__call__`'s return; `None` for a
      `None` or quoted one, or any other type.

    """
    head: ast.expr
    returns: ast.expr
    made: ast.expr | None
    match parsed(callee):
        case ast.Subscript(value=head, slice=ast.Tuple(elts=[_, returns])) if node_name(head) == _CALLABLE:
            if isinstance(returns, ast.Constant):
                return None  # `None`, or a name in quotes
            return Inference(ast.unparse(returns), f"what `{spelled}`, a `{callee}`, returns", _KIND)
        case ast.Subscript(value=head) if node_name(head) in _TYPE:
            made = _constructed(parsed(callee))
            reason: str = f"a call of `{spelled}`, a `{callee}`"
            return None if made is None else Inference(ast.unparse(made), reason, _KIND)
        case _:
            return member(callee, _CALL, call, known)


# Calls that return a class or a special form, not an instance of what they're named.
_FACTORIES: Final = frozenset(
    {
        "Enum",
        "Flag",
        "IntEnum",
        "IntFlag",
        "NamedTuple",
        "NewType",
        "ParamSpec",
        "StrEnum",
        "TypeAliasType",
        "TypeVar",
        "TypeVarTuple",
        "TypedDict",
    },
)


def typed_call(value: ast.expr, known: Known) -> Inference | None:
    """Infer a call by its callee's name alone (see the module docstring).

    Returns:
      The inference, or `None` for a callee typed no such way.

    """
    func: ast.expr
    name: str
    callee: str | None
    match value:
        case ast.Call(func=ast.Name() | ast.Attribute() as func) if (callee := dotted(func)) in known.calls:
            return Inference(
                known.calls[callee or ""],
                f"`{callee}`'s declared return type",
                frozenset({"call"}),
            )
        case ast.Call(func=ast.Name(id=name)) if name in BUILTIN_RETURNS and known.is_builtin(name):
            return Inference(BUILTIN_RETURNS[name], f"`{name}`'s fixed return type", frozenset({"builtin"}))
        case ast.Call(func=ast.Name() | ast.Attribute() as func) if (
            (constructs(node_name(func), known.factories) or dotted(func) in known.classes)
            and _type_expression(func, known)
            and stdlib.resolved(func, known.names.stdlib) not in stdlib.FUNCTIONS
        ):
            return Inference(
                ast.unparse(func),
                f"a call to `{ast.unparse(func)}`, taken to construct one",
                frozenset({CONSTRUCTOR}),
            )
        case _:
            return None


def _type_expression(func: ast.Name | ast.Attribute, known: Known) -> bool:
    """Check that a callee can be written as a type: a (dotted) name starting with a class or module.

    Not a call's attribute (`_tables().Filters`), nor through a name the module binds as a value
    somewhere (`Klass = ...`, `jinja2 = import_optional_dependency("jinja2")`, `self`): a type
    checker rejects a variable in a type.

    Returns:
      Whether it can.

    """
    path: str | None = dotted(func)
    plan: ImportPlan | None = known.names.plan
    return path is not None and (plan is None or path.partition(".")[0] not in plan.values)


def constructs(name: str, known_factories: frozenset[str]) -> bool:
    """Check whether a call to `name` constructs a class, by its capitalised name.

    Returns:
      Whether it does, and is worth annotating: `name` isn't a known factory, by import
      (`known_factories`) or by its bare name (`_FACTORIES`, for one imported some other way).

    """
    return (
        name[:1].isupper() and name not in known_factories and name not in _FACTORIES and name not in GENERICS
    )
