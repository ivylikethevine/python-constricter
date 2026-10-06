# SPDX-License-Identifier: MIT
"""Types split over what a loop or an unpacking binds: a container's elements, a tuple's parts."""

import ast
from collections import Counter
from collections.abc import Mapping, Sequence
from types import MappingProxyType
from typing import Final, cast

from constricter.fix.core.imports import rebound_names
from constricter.fix.core.known import Inference
from constricter.rules.annotations import defined_type_vars, node_name
from constricter.rules.quoted import written
from constricter.rules.syntax import top_level
from constricter.rules.walked import classes

# Builtins that iterate over their (first) argument's elements, one to one.
SAME_ELEMENTS: Final = frozenset({"reversed", "sorted"})
DICT_VIEWS: Final = frozenset({"keys", "values", "items"})
# What iterating each builtin that takes no type argument gives.
_ELEMENTS: Final = {"str": "str", "bytes": "int", "bytearray": "int", "range": "int"}
# Containers whose one type parameter is their elements'.
# And the builtin iterators', what they yield (`zip[tuple[str, int]]`); `enumerate[T]` counts its `T`s.
_ONE_ELEMENT_TYPE: Final = frozenset(
    {"list", "List", "set", "Set", "frozenset", "FrozenSet", "zip", "map", "reversed"},
)
# What yields its first type parameter, however it's named (`Iterator[T]`, `abc.Generator[T, None, None]`).
_YIELDING: Final = frozenset({"Iterable", "Iterator", "Generator"})
# Mappings of keys to values, however they're named (`dict[K, V]`, `abc.Mapping[K, V]`).
_MAPPINGS: Final = frozenset(
    {
        "dict",
        "Dict",
        "Mapping",
        "MutableMapping",
        "OrderedDict",
        "defaultdict",
        "DefaultDict",
        "MappingProxyType",
        "ChainMap",
    },
)
RANGE: Final = "range"
ENUMERATE: Final = "enumerate"
ZIP: Final = "zip"
MAP: Final = "map"  # yields what its function returns, whatever it's mapped over
ITER: Final = "iter"  # yields its one argument's elements (with a sentinel, what its callable returns)
ITERATORS: Final = frozenset({RANGE, ENUMERATE, ZIP, MAP, ITER, *SAME_ELEMENTS})
# The keywords each of `ITERATORS` takes that don't change what it yields (`sorted`'s only its order).
_ITERATOR_KEYWORDS: Final = {
    ENUMERATE: frozenset({"start"}),
    ZIP: frozenset({"strict"}),
    "sorted": frozenset({"key", "reverse"}),
}
# `tuple[T, ...]`'s two parts: the element type and the ellipsis.
_ANY_LENGTH: Final = 2
_NAMED_TUPLE: Final = ["NamedTuple"]  # the one base of a class whose annotated variables are its fields
_TUPLES: Final = frozenset({"tuple", "Tuple"})
_TYPE_ALIAS: Final = "TypeAlias"
_NO_TUPLES: Final[Mapping[str, str]] = MappingProxyType({})


def named_tuples(tree: ast.Module) -> dict[str, str]:
    """Map each tuple type the module names to the tuple unpacking one gives.

    A class defined once, directly under `NamedTuple` alone, with two fields or more: its fields'
    types. A type alias of a tuple (`Pair: TypeAlias = tuple[int, str]`, `Pair = tuple[int, str]`,
    `type Pair = tuple[int, str]`) at the module's top level, bound once there and naming none of
    its type variables: the tuple.

    Returns:
      Each one's name, and the tuple's type as text.

    """
    found: dict[str, str] = _aliased_tuples(tree)
    nodes: Sequence[ast.ClassDef] = classes(tree)
    counts: Counter[str] = Counter(node.name for node in nodes)
    node: ast.ClassDef
    for node in nodes:
        if counts[node.name] == 1 and [node_name(base) for base in node.bases] == _NAMED_TUPLE:
            fields: list[str] = [
                written(stmt.annotation)
                for stmt in node.body
                if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name)
            ]
            if len(fields) > 1:
                found[node.name] = f"tuple[{', '.join(fields)}]"
    return found


def _aliased_tuples(tree: ast.Module) -> dict[str, str]:
    """Find the module's type aliases of a tuple (see `named_tuples`).

    Returns:
      Each one's name, and the tuple's type as text.

    """
    rebound: frozenset[str] = frozenset(rebound_names(tree))
    type_vars: frozenset[str] = defined_type_vars(tree)
    found: dict[str, str] = {}
    stmt: ast.stmt
    for stmt in top_level(tree.body):
        aliased: tuple[str, ast.expr] | None = _alias(stmt)
        if (
            aliased is not None
            and aliased[0] not in rebound
            and isinstance(aliased[1], ast.Subscript)
            and node_name(aliased[1].value) in _TUPLES
            and not type_vars & {node.id for node in ast.walk(aliased[1]) if isinstance(node, ast.Name)}
        ):
            found[aliased[0]] = written(aliased[1])
    return found


def _alias(stmt: ast.stmt) -> tuple[str, ast.expr] | None:
    """Read the name and value a statement binds as a type alias, if it may be one.

    Returns:
      Them: an assignment's to one name (annotated `TypeAlias`, or not at all), or a `type`
      statement's; `None` for any other statement.

    """
    name: str
    value: ast.expr
    annotation: ast.expr
    match stmt:
        case ast.AnnAssign(target=ast.Name(id=name), annotation=annotation, value=ast.expr() as value) if (
            node_name(annotation) == _TYPE_ALIAS
        ):
            return name, value
        case ast.Assign(targets=[ast.Name(id=name)], value=value):
            return name, value
        case _ if type(stmt).__name__ == _TYPE_ALIAS:  # Python 3.12+'s `type X = ...`
            return cast("ast.Name", getattr(stmt, "name", None)).id, cast(
                "ast.expr",
                getattr(stmt, "value", None),
            )
        case _:
            return None


def sole(argument: ast.expr) -> ast.expr:
    """Read a one-parameter generic's type argument, written with a trailing comma or not.

    `list[int,]` (as a formatter writes a long one split over lines) subscripts `list` with the
    tuple `(int,)`; its element is still `int`.

    Returns:
      The type argument.

    """
    element: ast.expr
    match argument:
        case ast.Tuple(elts=[element]):
            return element
        case _:
            return argument


def element_type(container: str, reason: str, kinds: frozenset[str]) -> Inference | None:
    """Infer the elements of a value typed `container`.

    Returns:
      Them, or `None` for a type whose elements aren't known from it alone.

    """
    # `container` is always `ast.unparse`'s own output, so it's always valid Python to parse back.
    root: ast.expr = ast.parse(container, mode="eval").body
    name: str
    head: ast.expr
    item: ast.expr
    key: ast.expr
    others: list[ast.expr]
    match root:
        case ast.Name(id=name) if name in _ELEMENTS:
            return Inference(_ELEMENTS[name], reason, kinds)
        case ast.Subscript(value=ast.Name(id=name), slice=item) if (
            name in _ONE_ELEMENT_TYPE or name == ENUMERATE
        ):
            text: str = ast.unparse(sole(item))
            return Inference(f"tuple[int, {text}]" if name == ENUMERATE else text, reason, kinds)
        case ast.Subscript(value=head, slice=ast.Tuple(elts=[item, *_]) | item) if (
            node_name(head) in _YIELDING
        ):
            return Inference(ast.unparse(item), reason, kinds)
        case ast.Subscript(value=head, slice=ast.Tuple(elts=[key, _])) if node_name(head) in _MAPPINGS:
            return Inference(ast.unparse(key), reason, kinds)
        case ast.Subscript(value=ast.Name(id="tuple" | "Tuple"), slice=ast.Tuple(elts=[item, *others])) if (
            # `tuple[T, ...]`, or one whose parts agree (`("a", "b")`): whichever it is, a `T`.
            all(_is_ellipsis(other) or ast.unparse(other) == ast.unparse(item) for other in others)
        ):
            return Inference(ast.unparse(item), reason, kinds)
        case _:
            return None


def dict_parts(annotation: str) -> tuple[str, str] | None:
    """Read a `dict[K, V]`'s key and value types, or another mapping's (`Mapping[K, V]`).

    Returns:
      Them, as text, or `None` for any other annotation.

    """
    # `annotation` is always `ast.unparse`'s own output, so it's always valid Python to parse back.
    head: ast.expr
    key: ast.expr
    value: ast.expr
    match ast.parse(annotation, mode="eval").body:
        case ast.Subscript(value=head, slice=ast.Tuple(elts=[key, value])) if node_name(head) in _MAPPINGS:
            return ast.unparse(key), ast.unparse(value)
        case _:
            return None


def counted(name: str, args: list[ast.expr]) -> list[ast.expr]:
    """Pick the arguments whose elements one of `ITERATORS` yields: `enumerate`'s first, others' all.

    Returns:
      Them.

    """
    return args[:1] if name == ENUMERATE else args


def _is_ellipsis(node: ast.expr) -> bool:
    return isinstance(node, ast.Constant) and node.value is Ellipsis


def unpacked(
    target: ast.expr,
    annotation: str | None,
    tuples: Mapping[str, str] = _NO_TUPLES,
) -> list[tuple[ast.Name, str | None]]:
    """Match an unpacking target's names with the parts of a value typed `annotation`.

    A plain name takes the whole type; a tuple or list of targets takes a `tuple[A, B, ...]` of the
    same length part by part, or each an element of anything else whose elements are known (a
    `tuple[T, ...]`'s or `list[T]`'s `T`, a `str`'s `str`). A starred name takes a `list` of what's
    left for it, if that's of one type. A shape that doesn't match gets `None`. `tuples`: the named
    tuples the module names (see `named_tuples`), each split as its fields' tuple.

    Returns:
      Each name the target binds, with its type as text (or `None`).

    """
    elements: list[ast.expr]
    value: ast.expr
    match target:
        case ast.Name():
            return [(target, annotation)]
        case ast.Tuple(elts=elements) | ast.List(elts=elements):
            parts: list[str | None] = _parts(tuples.get(annotation or "", annotation), elements)
            return [
                pair
                for element, part in zip(elements, parts, strict=True)
                for pair in unpacked(element, part, tuples)
            ]
        case ast.Starred(value=value):
            return unpacked(value, annotation, tuples)
        case _:
            return []


def _parts(annotation: str | None, targets: Sequence[ast.expr]) -> list[str | None]:
    """Split a value's type over the targets it's unpacked into.

    Returns:
      Each target's type as text, a starred one's a `list`; all `None` if `annotation` isn't a tuple
      of that many, nor anything whose elements are known.

    """
    unknown: list[str | None] = [None] * len(targets)
    if annotation is None:
        return unknown
    star: int | None = next(
        (at for at, target in enumerate(targets) if isinstance(target, ast.Starred)),
        None,
    )
    elements: list[ast.expr]
    match ast.parse(annotation, mode="eval").body:
        case ast.Subscript(value=ast.Name(id="tuple" | "Tuple"), slice=ast.Tuple(elts=elements)) if not (
            len(elements) == _ANY_LENGTH and _is_ellipsis(elements[-1])
        ):
            return _fixed([ast.unparse(element) for element in elements], len(targets), star) or unknown
        case _:
            found: Inference | None
            if (found := element_type(annotation, "", frozenset())) is None:
                return unknown
            each: list[str | None] = [found.annotation] * len(targets)
            if star is not None:
                each[star] = f"list[{found.annotation}]"
            return each


def _fixed(parts: list[str], count: int, star: int | None) -> list[str | None] | None:
    """Split a fixed-length tuple's `parts` over `count` targets, the one at `star` starred (if any).

    Returns:
      Each target's type, the starred one's a `list` of the parts left for it where they agree
      (else `None`); or `None` if the tuple hasn't a part for each target.

    """
    if star is None:
        return [*parts] if len(parts) == count else None
    if len(parts) < count - 1:
        return None
    after: int = len(parts) - (count - star - 1)
    rest: set[str] = set(parts[star:after])
    starred: str | None = f"list[{rest.pop()}]" if len(rest) == 1 else None
    return [*parts[:star], starred, *parts[after:]]


def iterator_call(iterable: ast.expr) -> tuple[str, list[ast.expr]] | None:
    """Read a call to one of `ITERATORS` whose elements its positional arguments decide.

    Its keywords must be ones that don't change what it yields (`enumerate`'s `start`, `zip`'s
    `strict`, ...), and no argument starred: `zip(*rows)` yields as many parts as `rows` has.

    Returns:
      The iterator's name and its positional arguments, or `None` if `iterable` isn't such a call.

    """
    name: str
    args: list[ast.expr]
    keywords: list[ast.keyword]
    match iterable:
        case ast.Call(func=ast.Name(id=name), args=[_, *_] as args, keywords=keywords) if (
            name in ITERATORS
            and not any(isinstance(arg, ast.Starred) for arg in args)
            and all(keyword.arg in _ITERATOR_KEYWORDS.get(name, ()) for keyword in keywords)
        ):
            return name, args
        case _:
            return None


def iterated(iterable: ast.expr) -> list[ast.expr]:
    """Find the values `looped` typed a loop over `iterable` from, to judge whether it guessed.

    Through `enumerate` (its first argument), `zip`, `reversed`, `sorted` and a `dict` view to what
    they iterate; a `range()` iterates nothing typed, and a `map()` yields what its function returns.

    Returns:
      Those values.

    """
    call: tuple[str, list[ast.expr]] | None
    if (call := iterator_call(iterable)) is not None:
        return [] if call[0] in {RANGE, MAP} else [part for arg in counted(*call) for part in iterated(arg)]
    receiver: ast.expr
    view: str
    match iterable:
        case ast.Call(func=ast.Attribute(value=receiver, attr=view), args=[]) if view in DICT_VIEWS:
            return [receiver]
        case _:
            return [iterable]
