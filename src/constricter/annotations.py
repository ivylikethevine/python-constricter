# SPDX-License-Identifier: MIT
"""What an annotation says: vague parts (LVA005), nesting depth (LVA006), and inferable values (`--fix`)."""

import ast
import re
from collections.abc import Mapping, Sequence
from functools import lru_cache
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
# Builtins whose return type is fixed by the language, whatever their argument: safe to infer, not
# a guess (unlike a capitalised call, which could really be a generic class or a factory function).
_BUILTIN_RETURNS: Final = {
    "bool": "bool",
    "bytes": "bytes",
    "callable": "bool",
    "chr": "str",
    "complex": "complex",
    "float": "float",
    "hasattr": "bool",
    "hash": "int",
    "id": "int",
    "int": "int",
    "isinstance": "bool",
    "issubclass": "bool",
    "len": "int",
    "ord": "int",
    "repr": "str",
    "str": "str",
}
# Modules `_FACTORIES`' names are imported from (so an aliased or re-exported import is still found).
_FACTORY_MODULES: Final = frozenset({"enum", "typing", "typing_extensions"})


def imported_from(tree: ast.Module, modules: frozenset[str]) -> frozenset[str]:
    """Find the top-level names this module imports (`from module import name`) from one of `modules`.

    Only absolute imports are resolved; a relative one (`from . import x`) names no module here.

    Returns:
      Those names, as they're bound here (their alias, if importing gave them one).

    """
    names: set[str] = set()
    stmt: ast.stmt
    module: str
    for stmt in tree.body:
        match stmt:
            case ast.ImportFrom(module=str() as module, level=0) if module in modules:
                names.update(alias.asname or alias.name for alias in stmt.names)
            case _:
                pass
    return frozenset(names)


def factories(tree: ast.Module) -> frozenset[str]:
    """Find names this module imports that are known to build a class or special form.

    Not an instance of what they're named (`Enum`, `NamedTuple`, `TypeVar`, ... from `enum`,
    `typing` or `typing_extensions`), however they're aliased.

    Returns:
      Those names, as they're bound here.

    """
    return imported_from(tree, _FACTORY_MODULES)


def classes(tree: ast.Module) -> dict[str, dict[str, str]]:
    """Map each class defined in the module to its class-level annotated attributes.

    Only a class-body annotation counts (`class C: x: int`); one only assigned in `__init__` or
    elsewhere needs dataflow across methods to see, which is out of scope here. A name that names
    more than one class in the module (however unlikely) gets the last one's attributes.

    Returns:
      Each class's name, mapped to its attributes' names and annotation text.

    """
    found: dict[str, dict[str, str]] = {}
    node: ast.AST
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            found[node.name] = _attributes(node)
    return found


def _attributes(node: ast.ClassDef) -> dict[str, str]:
    attrs: dict[str, str] = {}
    stmt: ast.stmt
    name: str
    annotation: ast.expr
    for stmt in node.body:
        match stmt:
            case ast.AnnAssign(target=ast.Name(id=name), annotation=annotation):
                attrs[name] = ast.unparse(annotation)
            case _:
                pass
    return attrs


@lru_cache(maxsize=256)
def _parsed(annotation: ast.expr) -> ast.expr:
    """Unwrap a string annotation.

    `is_vague` and `depth` both call this on the same annotation; cached so it's parsed once.

    Returns:
      Its parsed expression, or the annotation itself if it isn't a string.

    """
    if isinstance(annotation, ast.Constant) and isinstance(annotation.value, str):
        try:
            return ast.parse(annotation.value, mode="eval").body
        except SyntaxError:
            return annotation
    return annotation


def node_name(node: ast.AST) -> str:
    """Read a `Name`'s or `Attribute`'s simple name.

    Returns:
      It, or `""` if `node` is neither.

    """
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
        name: str = node_name(node)
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
                node_name(func) in _TYPE_VARS
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


def inferred(
    value: ast.expr,
    calls: Mapping[str, str],
    known_factories: frozenset[str],
    declared: Mapping[str, str],
    known_classes: Mapping[str, Mapping[str, str]],
) -> str | None:
    """Return the annotation `value` makes unambiguous, given the module's function `calls`.

    A literal's type (containers too, when their elements agree), a call to a module function that
    declares its return type, a class it constructs, or (`declared`) another local this scope
    already gave a type: a plain copy, a subscript of a known container, or (`known_classes`, see
    `classes`) an attribute of a class defined in this module. `known_factories` (see `factories`)
    are calls that build a class or special form rather than an instance of it, so they're never
    guessed to construct one.

    Returns:
      The annotation as source text, or `None` if the value doesn't decide one.

    """
    if isinstance(value, ast.Name) and value.id in declared:
        return declared[value.id]
    found: str | None
    if (
        isinstance(value, ast.Subscript)
        and isinstance(value.value, ast.Name)
        and value.value.id in declared
        and (found := _subscripted(declared[value.value.id], value)) is not None
    ):
        return found
    if (
        isinstance(value, ast.Attribute)
        and isinstance(value.value, ast.Name)
        and value.value.id in declared
        and (found := known_classes.get(declared[value.value.id], {}).get(value.attr)) is not None
    ):
        return found
    return (
        _scalar(value)
        or _container(value, calls, known_factories, declared, known_classes)
        or _called(value, calls, known_factories)
    )


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
        case ast.UnaryOp(op=ast.Not()):  # `not x` always yields a real `bool`, unlike a comparison
            return "bool"
        case ast.JoinedStr():
            return "str"
        case _:
            return None


def _container(
    value: ast.expr,
    calls: Mapping[str, str],
    known_factories: frozenset[str],
    declared: Mapping[str, str],
    known_classes: Mapping[str, Mapping[str, str]],
) -> str | None:
    elements: list[ast.expr]
    keys: list[ast.expr | None]
    values: list[ast.expr]
    parts: list[str | None]
    match value:
        case ast.List(elts=elements) | ast.Set(elts=elements) if elements:
            element: str | None = _uniform(elements, calls, known_factories, declared, known_classes)
            return f"{'list' if isinstance(value, ast.List) else 'set'}[{element}]" if element else None
        case ast.Tuple(elts=elements) if elements:
            parts = [
                inferred(element, calls, known_factories, declared, known_classes) for element in elements
            ]
            return None if None in parts else f"tuple[{', '.join(str(part) for part in parts)}]"
        case ast.Dict(keys=keys, values=values) if keys and None not in keys:
            present: list[ast.expr] = [k for k in keys if k is not None]
            key: str | None = _uniform(present, calls, known_factories, declared, known_classes)
            item: str | None = _uniform(values, calls, known_factories, declared, known_classes)
            return f"dict[{key}, {item}]" if key and item else None
        case _:
            return None


def _uniform(
    elements: Sequence[ast.expr],
    calls: Mapping[str, str],
    known_factories: frozenset[str],
    declared: Mapping[str, str],
    known_classes: Mapping[str, Mapping[str, str]],
) -> str | None:
    """Find the one type every element has.

    Returns:
      That type, or `None` if they differ or any is unknown.

    """
    types: set[str | None] = {
        inferred(element, calls, known_factories, declared, known_classes) for element in elements
    }
    return next(iter(types)) if len(types) == 1 else None


def _subscripted(container: str, node: ast.Subscript) -> str | None:
    """Infer `container[...]`'s type, given `container`'s own type as text.

    A slice (`x[1:2]`) of a `list`, `str` or `bytes` is the same type as `container` itself; a plain
    index into one is its element type, as is any index into a `dict` (its value type) or a
    homogeneous `tuple[T, ...]`. A fixed-length `tuple[T1, T2]`'s element only varies with the index,
    which isn't worth resolving.

    Returns:
      The annotation as source text, or `None` if the subscript doesn't decide one.

    """
    # `container` is always `ast.unparse`'s own output (an annotation, or an earlier `inferred`),
    # never user text, so it's always valid Python to parse back.
    root: ast.expr = ast.parse(container, mode="eval").body
    sliced: bool = isinstance(node.slice, ast.Slice)
    element: ast.expr
    last: ast.expr
    match root:
        case ast.Name(id="str" | "bytes"):
            return container
        case ast.Subscript(value=ast.Name(id="list" | "List"), slice=element):
            return container if sliced else ast.unparse(element)
        case ast.Subscript(
            value=ast.Name(id="dict" | "Dict"),
            slice=ast.Tuple(elts=[_, element]),
        ) if not sliced:
            return ast.unparse(element)
        case ast.Subscript(
            value=ast.Name(id="tuple" | "Tuple"),
            slice=ast.Tuple(elts=[element, last]),
        ) if not sliced and isinstance(last, ast.Constant) and last.value is Ellipsis:
            return ast.unparse(element)
        case _:
            return None


def _called(value: ast.expr, calls: Mapping[str, str], known_factories: frozenset[str]) -> str | None:
    func: ast.expr
    name: str
    match value:
        case ast.Call(func=ast.Name() | ast.Attribute() as func) if ast.unparse(func) in calls:
            return calls[ast.unparse(func)]
        case ast.Call(func=ast.Name(id=name)) if name in _BUILTIN_RETURNS:
            return _BUILTIN_RETURNS[name]
        case ast.Call(func=ast.Name() | ast.Attribute() as func) if _constructs(
            node_name(func),
            known_factories,
        ):
            return ast.unparse(func)
        case _:
            return None


def guessed(value: ast.expr, calls: Mapping[str, str], guesses: frozenset[str]) -> bool:
    """Whether `inferred`'s annotation for `value` is a guess (`--unsafe-fixes`): it calls a class.

    A capitalised call may construct a generic class (`Box(1)` is really `Box[int]`) or be a factory
    function; literals, calls to a module function or a fixed-return builtin (`len`, `isinstance`,
    ...), and another local this scope already typed are certain. Copying a local `inferred` itself
    only guessed (`guesses`) is no more certain than the guess it copies.

    Returns:
      Whether any call in `value` is to something other than such a certain callee, or any name in
      it copies such a guess.

    """
    return any(_is_guess(node, calls, guesses) for node in ast.walk(value))


def _is_guess(node: ast.AST, calls: Mapping[str, str], guesses: frozenset[str]) -> bool:
    name: str
    func: ast.expr
    match node:
        case ast.Call(func=ast.Name(id=name)) if name in _BUILTIN_RETURNS:
            return False
        case ast.Call(func=func):
            return ast.unparse(func) not in calls
        case ast.Name(id=name):
            return name in guesses
        case _:
            return False


def _constructs(name: str, known_factories: frozenset[str]) -> bool:
    """Check whether a call to `name` constructs a class, by its capitalised name.

    Returns:
      Whether it does, and is worth annotating: `name` isn't a known factory, by import
      (`known_factories`) or by its bare name (`_FACTORIES`, for one imported some other way).

    """
    return (
        name[:1].isupper()
        and name not in known_factories
        and name not in _FACTORIES
        and name not in _GENERICS
    )
