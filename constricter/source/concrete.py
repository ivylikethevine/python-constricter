"""Which names in a class's subscripted base can't be a type variable: whether the class is generic.

`class Dataset(Mapping[Hashable, "DataArray"])` binds every parameter it inherits, so it's written
bare and read as a plain class; `class Box(Base[T])` doesn't. Only the module itself is read: a name
another module binds counts where the module uses it as only a class can be used.
"""

import ast
import builtins
import sys
from collections.abc import Iterator, Sequence
from typing import Final, NamedTuple, TypeAlias, cast
from weakref import WeakKeyDictionary

from constricter.source.annotations import dotted, node_name
from constricter.source.syntax import top_level
from constricter.source.walked import of_type

_Names: TypeAlias = frozenset[str]
_TYPE_VARS: Final = frozenset({"TypeVar", "ParamSpec", "TypeVarTuple"})
# `typing`'s type variables, its private ones too, importable all the same: none is a class.
_TYPING_VARS_ALL: Final = frozenset({"AnyStr", "T", "KT", "VT", "T_co", "V_co", "VT_co", "T_contra", "CT_co"})
_TYPESHED: Final = "_typeshed"
_LITERAL: Final = "Literal"
_UNDERSCORE: Final = "_"
_BUILTINS: Final = frozenset({*dir(builtins), "None"})
_CLASS_CHECKS: Final = frozenset({"isinstance", "issubclass"})
# What a type variable has but a dunder: an attribute read of anything else is of a class or a module.
_TYPE_VAR_ATTRIBUTES: Final = frozenset({"has_default", "evaluate_default", "args", "kwargs"})
_DUNDER: Final = "__"
_CONCRETE: Final[WeakKeyDictionary[ast.Module, "_Concrete"]] = WeakKeyDictionary()
_CLASS_USES: Final[WeakKeyDictionary[ast.Module, _Names]] = WeakKeyDictionary()


def binds_all(subscript: ast.expr, tree: ast.Module, type_vars: frozenset[str]) -> bool:
    """Check whether a class's subscripted base names no type variable (see `_concrete`).

    `type_vars`: the module's own, at its top level (`declarations.defined_type_vars`).

    Returns:
      Whether every name in it, its string forward references' too, is known not to be one.

    """
    return not unbound_names(subscript, tree, type_vars)


def unbound_names(subscript: ast.expr, tree: ast.Module, type_vars: frozenset[str]) -> frozenset[str]:
    """Name what a class's subscripted base names that may be a type variable (see `binds_all`).

    Returns:
      Those names, as written (`T`, `t.T`).

    """
    concrete: _Concrete = _concrete(tree, type_vars)
    named: list[str] = list(_subscript_names(subscript))
    left: frozenset[str] = frozenset(
        name for name in named if not (name in concrete.names or _from_module(name, concrete.modules))
    )
    return left and left - (_class_uses(tree) - concrete.type_vars)


def _subscript_names(node: ast.expr) -> Iterator[str]:
    """Name what a subscript refers to: each name or dotted name, in a string forward reference too.

    A `Literal`'s values are values, not names, and a string that isn't an expression names nothing.

    Yields:
      Each one, as written (`np.float64`).

    """
    name: str | None
    if (name := dotted(node)) is not None:
        yield name
    elif isinstance(node, ast.Constant) and isinstance(node.value, str):
        try:
            yield from _subscript_names(ast.parse(node.value.strip(), mode="eval").body)
        except SyntaxError:
            return
    elif isinstance(node, ast.Subscript) and node_name(node.value) == _LITERAL:
        yield from _subscript_names(node.value)
    else:
        child: ast.AST
        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.expr):
                yield from _subscript_names(child)


def _from_module(name: str, modules: frozenset[str]) -> bool:
    """Check whether a dotted name is a public name of a standard-library module the file imports whole.

    Returns:
      Whether it is (`typing.Any`; not `typing.AnyStr`, nor a private `_T`).

    """
    root: str
    rest: str
    root, _, rest = name.rpartition(".")
    return bool(root) and root in modules and _public_class(rest)


def _public_class(name: str) -> bool:
    """Check whether a standard-library module's name can't be a type variable it defines.

    Returns:
      Whether it can't: public, and none of `typing`'s own (`AnyStr`, `T`, `KT`, ...).

    """
    return not name.startswith(_UNDERSCORE) and name not in _TYPING_VARS_ALL


class _Concrete(NamedTuple):
    """What a module's names can't be a type variable: see `_concrete`."""

    names: frozenset[str]  # names, and dotted names, that are no type variable
    modules: frozenset[str]  # the standard-library modules it imports whole, as it binds them
    type_vars: frozenset[str]  # what it binds to a type variable anywhere, a function's own too


def _concrete(tree: ast.Module, type_vars: frozenset[str]) -> _Concrete:
    """Find the names the module binds that can't be a type variable, without reading another module.

    A builtin; a class, function or variable the module defines at its top level, but for its type
    variables (`type_vars`, and a function's own); a public name imported from the standard library
    but for `typing`'s type variables and `_typeshed`'s, whose names are type variables as often as
    classes.

    Returns:
      Them, and the standard-library modules the module imports whole.

    """
    found: _Concrete | None
    if (found := _CONCRETE.get(tree)) is None:
        found = _CONCRETE[tree] = _read_concrete(tree, type_vars)
    return found


def _read_concrete(tree: ast.Module, defined: frozenset[str]) -> _Concrete:
    names: set[str] = set(_BUILTINS)
    modules: set[str] = set()
    typing_vars: set[str] = set()  # `from typing import T`
    value: ast.expr | None
    stmt: ast.stmt
    module: str
    targets: list[ast.expr]
    name: str
    for stmt in top_level(tree.body):  # under an `if TYPE_CHECKING:` too
        match stmt:
            case ast.ClassDef() | ast.FunctionDef() | ast.AsyncFunctionDef():
                names.add(stmt.name)
            case ast.Assign(targets=targets, value=value) if not _aliased(value):
                names.update(target.id for target in targets if isinstance(target, ast.Name))
            case ast.AnnAssign(target=ast.Name(id=name), value=value) if value is None or not _aliased(value):
                names.add(name)
            case ast.ImportFrom(module=str() as module, level=0) if _standard(module):
                names.update(alias.asname or alias.name for alias in stmt.names if _public_class(alias.name))
                typing_vars.update(
                    alias.asname or alias.name for alias in stmt.names if alias.name in _TYPING_VARS_ALL
                )
            case ast.Import():
                modules.update(
                    alias.asname or alias.name.partition(".")[0]
                    for alias in stmt.names
                    if _standard(alias.name)
                )
            case _:
                pass
    assigned: Sequence[ast.Assign | ast.AnnAssign] = cast(
        "Sequence[ast.Assign | ast.AnnAssign]",
        of_type(tree, ast.Assign, ast.AnnAssign),
    )
    local: set[str] = set()  # a function's own `T = TypeVar("T")` too
    node: ast.Assign | ast.AnnAssign
    for node in assigned:
        if isinstance(node.value, ast.Call) and node_name(node.value.func) in _TYPE_VARS:
            stored: list[ast.expr] = node.targets if isinstance(node, ast.Assign) else [node.target]
            local.update(target.id for target in stored if isinstance(target, ast.Name))
    type_vars: frozenset[str] = defined | typing_vars | local
    return _Concrete(frozenset(names) - type_vars, frozenset(modules), type_vars)


def _aliased(value: ast.expr) -> bool:
    """Check whether a top-level variable's value is another name (`K = T`), which may be a type variable.

    Returns:
      Whether it is, or a call of a type variable's class (`T: TypeVar = TypeVar("T")`).

    """
    return dotted(value) is not None or (isinstance(value, ast.Call) and node_name(value.func) in _TYPE_VARS)


def _standard(module: str) -> bool:
    """Check whether a module is the standard library's, other than `_typeshed`.

    Returns:
      Whether it is.

    """
    return module.partition(".")[0] in sys.stdlib_module_names and module != _TYPESHED


def _class_uses(tree: ast.Module) -> frozenset[str]:
    """Find the names, and dotted names, the module uses as only a class (or a module) can be used.

    Called, subclassed, subscripted, given to `isinstance` or `issubclass`, caught, or read an attribute
    of that isn't a dunder nor a type variable's own (`has_default`): a `TypeVar` allows none of them.

    Returns:
      Them, as written.

    """
    found: frozenset[str] | None
    if (found := _CLASS_USES.get(tree)) is None:
        found = _CLASS_USES[tree] = _read_class_uses(tree)
    return found


def _read_class_uses(tree: ast.Module) -> frozenset[str]:
    used: set[str | None] = set()
    node: ast.AST
    func: ast.expr
    checked: ast.expr
    bases: list[ast.expr]
    caught: ast.expr
    value: ast.expr
    attr: str
    for node in of_type(tree, ast.Call, ast.Subscript, ast.ClassDef, ast.ExceptHandler, ast.Attribute):
        match node:
            case ast.Call(func=func, args=[_, checked]) if node_name(func) in _CLASS_CHECKS:
                used.update(
                    dotted(each) for each in (checked.elts if isinstance(checked, ast.Tuple) else [checked])
                )
                used.add(dotted(func))
            case ast.Call(func=func) | ast.Subscript(value=func):
                used.add(dotted(func))
            case ast.ClassDef(bases=bases):
                used.update(dotted(base.value if isinstance(base, ast.Subscript) else base) for base in bases)
            case ast.ExceptHandler(type=ast.expr() as caught):
                used.update(
                    dotted(each) for each in (caught.elts if isinstance(caught, ast.Tuple) else [caught])
                )
            case ast.Attribute(value=value, attr=attr) if not (
                attr.startswith(_DUNDER) or attr in _TYPE_VAR_ATTRIBUTES
            ):
                used.add(dotted(value))
            case _:
                pass
    return frozenset(name for name in used if name is not None)
