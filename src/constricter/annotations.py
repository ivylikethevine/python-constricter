# SPDX-License-Identifier: MIT
"""What an annotation says: vague parts (LVA005), nesting depth (LVA006), and inferable values (`--fix`)."""

import ast
import re
from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING, Final, cast

if TYPE_CHECKING:
    from types import EllipsisType

_VAGUE: Final = frozenset({"Any", "object"})
# Generics that say little without their parameters.
_GENERICS: Final = frozenset(
    {
        "AbstractSet",
        "AsyncGenerator",
        "AsyncIterable",
        "AsyncIterator",
        "Awaitable",
        "Callable",
        "ChainMap",
        "Collection",
        "Container",
        "Coroutine",
        "Counter",
        "DefaultDict",
        "Deque",
        "Dict",
        "FrozenSet",
        "Generator",
        "ItemsView",
        "Iterable",
        "Iterator",
        "KeysView",
        "List",
        "Mapping",
        "Match",
        "MutableMapping",
        "MutableSequence",
        "MutableSet",
        "OrderedDict",
        "Pattern",
        "Reversible",
        "Sequence",
        "Set",
        "Tuple",
        "Type",
        "ValuesView",
        "defaultdict",
        "deque",
        "dict",
        "frozenset",
        "list",
        "set",
        "tuple",
        "type",
    },
)
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
        "TypeVar",
        "TypeVarTuple",
        "TypedDict",
    },
)
_NUMBERS: Final = (int, float, complex)
_TYPE_VARS: Final = frozenset({"TypeVar", "ParamSpec", "TypeVarTuple"})


def _parsed(annotation: ast.expr) -> ast.expr:
    """Unwrap a string annotation.

    Returns:
      Its parsed expression, or the annotation itself if it isn't a string.

    """
    if isinstance(annotation, ast.Constant) and isinstance(annotation.value, str):
        try:
            return ast.parse(annotation.value, mode="eval").body
        except SyntaxError:
            return annotation
    return annotation


def _name(node: ast.AST) -> str:
    name: str
    match node:
        case ast.Name(id=name) | ast.Attribute(attr=name):
            return name
        case _:
            return ""


def is_vague(annotation: ast.expr) -> bool:
    """Check an annotation for vague types.

    Returns:
      Whether it has `Any`, `object` or a generic without its parameters in it.

    """
    root: ast.expr = _parsed(annotation)
    subscripted: set[int] = {id(node.value) for node in ast.walk(root) if isinstance(node, ast.Subscript)}
    node: ast.AST
    for node in ast.walk(root):
        name: str = _name(node)
        if name in _VAGUE or (name in _GENERICS and id(node) not in subscripted):
            return True
    return False


def depth(annotation: ast.expr) -> int:
    """Measure how deeply an annotation's subscripts nest.

    Returns:
      The depth: `dict[str, list[int]]` is 2.

    """
    node: ast.expr = _parsed(annotation)
    inner: ast.expr
    parts: list[ast.expr]
    left: ast.expr
    right: ast.expr
    match node:
        case ast.Subscript(slice=inner):
            return 1 + depth(inner)
        case ast.Tuple(elts=parts) | ast.List(elts=parts):
            return max((depth(part) for part in parts), default=0)
        case ast.BinOp(left=left, right=right):
            return max(depth(left), depth(right))
        case _:
            return 0


def returns(tree: ast.Module) -> dict[str, str]:
    """Return the declared return type of each plain top-level function whose calls `--fix` can annotate.

    Skipped: decorated, generic, async and redefined functions, and returns that are `None`, vague, or
    mention a module-level `TypeVar` (a call's type then depends on its arguments).

    Returns:
      Each such function's name, and its return annotation as source text.

    """
    type_vars: set[str] = set()
    counts: dict[str, int] = {}
    found: dict[str, str] = {}
    stmt: ast.stmt
    name: str
    func: ast.expr
    for stmt in tree.body:
        match stmt:
            case ast.Assign(targets=[ast.Name(id=name)], value=ast.Call(func=func)) if (
                _name(func) in _TYPE_VARS
            ):
                type_vars.add(name)
            case ast.FunctionDef(name=name) | ast.AsyncFunctionDef(name=name):
                counts[name] = counts.get(name, 0) + 1
                if isinstance(stmt, ast.FunctionDef) and _plain(stmt):
                    found[name] = ast.unparse(cast("ast.expr", stmt.returns))
            case _:
                pass
    return {
        name: annotation
        for name, annotation in found.items()
        if counts[name] == 1 and not type_vars & set(_words(annotation))
    }


def _plain(func: ast.FunctionDef) -> bool:
    """Check that `func` declares a return type its calls always have.

    Returns:
      Whether it does: not `None`, and not vague.

    """
    return (
        not func.decorator_list
        and not cast("object", getattr(func, "type_params", ()))  # Python 3.12+'s `def f[T]()`
        and func.returns is not None
        and not (isinstance(func.returns, ast.Constant) and func.returns.value is None)
        and not is_vague(func.returns)
    )


def _words(annotation: str) -> list[str]:
    return [word for word in re.split(r"\W+", annotation) if word]


def inferred(value: ast.expr, calls: Mapping[str, str]) -> str | None:
    """Return the annotation `value` makes unambiguous, given the module's function `calls`.

    A literal's type (containers too, when their elements agree), a call to a module function that
    declares its return type, or a class it constructs.

    Returns:
      The annotation as source text, or `None` if the value doesn't decide one.

    """
    return _scalar(value) or _container(value, calls) or _called(value, calls)


def _scalar(value: ast.expr) -> str | None:
    constant: str | bytes | bool | int | float | complex | EllipsisType | None
    match value:
        case ast.Constant(value=bool() | int() | float() | complex() | str() | bytes() as constant):
            return type(constant).__name__
        case ast.UnaryOp(op=ast.USub() | ast.UAdd(), operand=ast.Constant(value=constant)) if isinstance(
            constant,
            _NUMBERS,
        ) and not isinstance(constant, bool):
            return type(constant).__name__
        case ast.JoinedStr():
            return "str"
        case _:
            return None


def _container(value: ast.expr, calls: Mapping[str, str]) -> str | None:
    elements: list[ast.expr]
    keys: list[ast.expr | None]
    values: list[ast.expr]
    parts: list[str | None]
    match value:
        case ast.List(elts=elements) | ast.Set(elts=elements) if elements:
            element: str | None = _uniform(elements, calls)
            return f"{'list' if isinstance(value, ast.List) else 'set'}[{element}]" if element else None
        case ast.Tuple(elts=elements) if elements:
            parts = [inferred(element, calls) for element in elements]
            return None if None in parts else f"tuple[{', '.join(str(part) for part in parts)}]"
        case ast.Dict(keys=keys, values=values) if keys and None not in keys:
            key: str | None = _uniform([k for k in keys if k is not None], calls)
            item: str | None = _uniform(values, calls)
            return f"dict[{key}, {item}]" if key and item else None
        case _:
            return None


def _uniform(elements: Sequence[ast.expr], calls: Mapping[str, str]) -> str | None:
    """Find the one type every element has.

    Returns:
      That type, or `None` if they differ or any is unknown.

    """
    types: set[str | None] = {inferred(element, calls) for element in elements}
    return next(iter(types)) if len(types) == 1 else None


def _called(value: ast.expr, calls: Mapping[str, str]) -> str | None:
    func: ast.expr
    match value:
        case ast.Call(func=ast.Name() | ast.Attribute() as func) if ast.unparse(func) in calls:
            return calls[ast.unparse(func)]
        case ast.Call(func=ast.Name() | ast.Attribute() as func) if _constructs(_name(func)):
            return ast.unparse(func)
        case _:
            return None


def guessed(value: ast.expr, calls: Mapping[str, str]) -> bool:
    """Whether `inferred`'s annotation for `value` is a guess (`--unsafe-fixes`): it calls a class.

    A capitalised call may construct a generic class (`Box(1)` is really `Box[int]`) or be a factory
    function; literals and calls to module functions with a declared return type are certain.

    Returns:
      Whether any call in `value` is to something other than such a module function.

    """
    return any(isinstance(node, ast.Call) and ast.unparse(node.func) not in calls for node in ast.walk(value))


def _constructs(name: str) -> bool:
    """Check whether a call to `name` constructs a class, by its capitalised name.

    Returns:
      Whether it does, and is worth annotating.

    """
    return name[:1].isupper() and name not in _FACTORIES and name not in _GENERICS
