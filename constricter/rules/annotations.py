# SPDX-License-Identifier: MIT
"""What an annotation says (LVA005, LVA006, LVA011), and what a module declares.

An annotation's vague parts, nesting depth and longest fixed-length tuple; a module's functions' and
methods' return types, its classes' attributes, and the factories it imports.
"""

import ast
import re
from collections.abc import Iterator, Sequence
from functools import lru_cache
from typing import Final, cast

_VAGUE: Final = frozenset({"Any", "object"})
# Generics that say little without their parameters.
GENERICS: Final = frozenset(
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
_TUPLES: Final = frozenset({"tuple", "Tuple"})  # the annotations that list one type per element
_TYPE_VARS: Final = frozenset({"TypeVar", "ParamSpec", "TypeVarTuple"})
# Modules `_FACTORIES`' names are imported from (so an aliased or re-exported import is still found).
_FACTORY_MODULES: Final = frozenset({"enum", "typing", "typing_extensions"})
# A method returning `Self` returns its receiver's own class.
_SELF: Final = "Self"


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
    """Map each class defined in the module to its annotated attributes.

    A class-body annotation (`class C: x: int`) and a `self.x: int = ...` annotated assignment
    anywhere in one of its methods both count; a name that names more than one class in the module
    (however unlikely) gets the last one's attributes.

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
            case ast.FunctionDef() | ast.AsyncFunctionDef():
                attrs.update(_self_attributes(stmt))
            case _:
                pass
    return attrs


def _self_attributes(func: ast.FunctionDef | ast.AsyncFunctionDef) -> Iterator[tuple[str, str]]:
    """Find `self.attr: T = ...` annotated assignments anywhere in a method's body.

    Yields:
      Each attribute's name and annotation text.

    """
    node: ast.AST
    name: str
    annotation: ast.expr
    for node in ast.walk(func):
        match node:
            case ast.AnnAssign(
                target=ast.Attribute(value=ast.Name(id="self"), attr=name),
                annotation=annotation,
            ):
                yield name, ast.unparse(annotation)
            case _:
                pass


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
        if name in _VAGUE or (name in GENERICS and id(node) not in subscripted):
            return True
    return False


def length(annotation: ast.expr) -> int:
    """Measure the longest fixed-length tuple an annotation lists, one type per element.

    `tuple[int, str]` is 2; `tuple[int, ...]` (any length) and anything but a tuple are 0.

    Returns:
      The most elements any `tuple[...]` or `Tuple[...]` in it lists.

    """
    node: ast.AST
    head: ast.expr
    elements: list[ast.expr]
    lengths: list[int] = [0]
    for node in ast.walk(_parsed(annotation)):
        match node:
            case ast.Subscript(value=head, slice=ast.Tuple(elts=elements)) if node_name(head) in _TUPLES:
                lengths.append(0 if _variadic(elements) else len(elements))
            case ast.Subscript(value=head) if node_name(head) in _TUPLES:
                lengths.append(1)
            case _:
                pass
    return max(lengths)


def _variadic(elements: list[ast.expr]) -> bool:
    """Check whether a tuple annotation's elements end in `...` (`tuple[int, ...]`: any length).

    Returns:
      Whether they do.

    """
    return isinstance(elements[-1], ast.Constant) and elements[-1].value is Ellipsis


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
    return _declared_returns(tree.body, _type_vars(tree))


def method_returns(tree: ast.Module) -> dict[str, dict[str, str]]:
    """Map each non-generic class defined in the module to its methods' declared return types.

    For `--fix` to type `obj.method()` on a local already typed as that class. A method counts under
    the same rules as `returns`' functions: a plain `def` directly in the class body, not decorated
    (so no `staticmethod`, `classmethod` or `property`) or redefined, whose return isn't `None`,
    vague, or a `TypeVar`. A generic class (`class C[T]`, or any subscripted base like `Generic[T]`)
    is skipped whole: its methods' returns depend on how it's parameterised. A bare `Self` return is
    the class itself; one that only mentions `Self` (`list[Self]`) is skipped.

    Returns:
      Each class's name, mapped to its methods' names and return annotation text.

    """
    type_vars: frozenset[str] = _type_vars(tree)
    found: dict[str, dict[str, str]] = {}
    node: ast.AST
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.ClassDef)
            and not cast("object", getattr(node, "type_params", ()))  # Python 3.12+'s `class C[T]`
            and not any(isinstance(base, ast.Subscript) for base in node.bases)
        ):
            found[node.name] = {
                name: node.name if _is_self(annotation) else annotation
                for name, annotation in _declared_returns(node.body, type_vars).items()
                if _is_self(annotation) or _SELF not in _words(annotation)
            }
    return found


def _is_self(annotation: str) -> bool:
    """Check whether an annotation is exactly `Self` (bare, or `typing.Self` and the like).

    Returns:
      Whether it is.

    """
    # `annotation` is always `ast.unparse`'s own output, so it's always valid Python to parse back.
    return node_name(ast.parse(annotation, mode="eval").body) == _SELF


def _type_vars(tree: ast.Module) -> frozenset[str]:
    """Find the module-level names bound to a `TypeVar`, `ParamSpec` or `TypeVarTuple`.

    Returns:
      Those names.

    """
    names: set[str] = set()
    stmt: ast.stmt
    name: str
    func: ast.expr
    for stmt in tree.body:
        match stmt:
            case ast.Assign(targets=[ast.Name(id=name)], value=ast.Call(func=func)) if (
                node_name(func) in _TYPE_VARS
            ):
                names.add(name)
            case _:
                pass
    return frozenset(names)


def _declared_returns(body: Sequence[ast.stmt], type_vars: frozenset[str]) -> dict[str, str]:
    """Find the plain functions defined directly in `body` whose calls `--fix` can annotate.

    Returns:
      Each such function's name, and its return annotation as source text.

    """
    counts: dict[str, int] = {}
    found: dict[str, str] = {}
    stmt: ast.stmt
    name: str
    for stmt in body:
        match stmt:
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
