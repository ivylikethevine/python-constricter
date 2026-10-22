"""What a loop binds each time round, and the targets of comprehensions, typed as `--fix` types values.

`looped` types a `for` loop's target by what its iterable yields; `looped_parts` each part of an
`enumerate` or `zip` loop's tuples on its own; `comprehended` the targets of a value's
comprehensions, as a loop's are. `infer` types a value as `constricter.fix.values.inference` does,
over the names a scope declared.
"""

import ast
import re
from collections.abc import Callable, Mapping, Sequence
from typing import Final, TypeAlias, cast

from constricter.fix.core.known import Inference, Known, kinds_of
from constricter.fix.libraries import generics, walks
from constricter.fix.values import called, shapes
from constricter.fix.values.members import present
from constricter.fix.values.targets import (
    DICT_VIEWS,
    ENUMERATE,
    FILTER,
    ITER,
    MAP,
    RANGE,
    SAME_ELEMENTS,
    ZIP,
    counted,
    dict_parts,
    element_type,
    iterated,
    iterator_call,
    unpacked,
)
from constricter.offences import CONSTRUCTOR
from constricter.rules.flow import members

_GENERIC: Final = "["  # in a type's text: its arguments
COMPREHENSIONS: Final = (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)
_UNION: Final = re.compile(r"\||\b(?:None|Optional|Union)\b")  # an annotation with a union in it
_NONE: Final = "None"
# A predicate's return that narrows what it's given
_NARROWING: Final = re.compile(r"\b(?:TypeGuard|TypeIs)\b")
_CALLABLE: Final = "callable"  # the builtin predicate that narrows (`TypeIs[Callable[..., object]]`)
_PREDICATE: Final = 2  # `filter`'s arguments: the predicate and the iterable
_Comprehension: TypeAlias = ast.ListComp | ast.SetComp | ast.DictComp | ast.GeneratorExp
# Types a value over what a scope declared, as `constricter.fix.values.inference.inference` does.
Infer: TypeAlias = Callable[[ast.expr, Known, Mapping[str, str]], Inference | None]


# One part of a loop target (see `looped_parts`): its inference, and the values it came from.
LoopPart: TypeAlias = tuple[Inference | None, list[ast.expr]]


def rebased(receiver: str, name: str, known: Known) -> str:
    """Read a class of the module's as the generic library class it takes `name` from, given its arguments.

    `Rows`, under `collections.deque[Row]`, as that: what its instance's subscript, loop or view gives.

    Returns:
      The base as the class writes it; `receiver` itself for any other.

    """
    base: str | None = known.class_side.lineage.definer(receiver, name)
    return base if base is not None and _GENERIC in base and _GENERIC not in receiver else receiver


def comprehended(
    value: ast.expr,
    known: Known,
    declared: Mapping[str, str],
    infer: Infer,
) -> Mapping[str, str]:
    """Type the targets of every comprehension in `value`, as a loop's are, over what's `declared`.

    A target whose type isn't known is dropped (it shadows any outer name of the same name).

    Returns:
      `declared`, with the targets' types: `declared` itself, uncopied, where there's none (most values).

    """
    return targets_typed(
        [node for node in ast.walk(value) if isinstance(node, COMPREHENSIONS)],
        known,
        declared,
        infer,
    )


def targets_typed(
    comprehensions: Sequence[ast.AST],
    known: Known,
    declared: Mapping[str, str],
    infer: Infer,
) -> Mapping[str, str]:
    """Type the targets of `comprehensions`, as a loop's are, over what's `declared` (see `comprehended`).

    Returns:
      `declared`, with the targets' types: `declared` itself, uncopied, where there are none.

    """
    if not comprehensions:
        return declared
    inside: dict[str, str] = dict(declared)
    node: ast.AST
    generator: ast.comprehension
    for node in comprehensions:
        for generator in cast("_Comprehension", node).generators:
            found: Inference | None = looped(generator.iter, known, inside, infer)
            name: ast.Name
            part: str | None
            annotation: str | None = None if found is None else found.annotation
            for name, part in unpacked(generator.target, annotation, known.indirect.tuples):
                if part is None:
                    _ = inside.pop(name.id, None)
                else:
                    inside[name.id] = part
    return inside


def looped(iterable: ast.expr, known: Known, declared: Mapping[str, str], infer: Infer) -> Inference | None:
    """Infer what a `for` loop over `iterable` binds each time round, and say how.

    `range()` gives `int`s; `enumerate(x)` `tuple[int, T]` and `zip(x, y)` `tuple[T, U]`, given
    `x`'s and `y`'s; `reversed(x)`, `sorted(x)` and `iter(x)` what `x` does; `map(f, x)` what `f`
    returns; a generator expression its element; a `dict`'s `.keys()`, `.values()` and `.items()`
    its keys, values and pairs; and anything else
    whose type is inferred, its elements: a `list`, `set`, `frozenset` or `tuple[T, ...]`'s `T`, a
    tuple's parts where they agree, a `dict`'s keys, a `str`'s `str`s and a `bytes`'s `int`s, and a
    standard-library class's by its `__iter__` (a file's lines). `os.walk(top)` gives a directory's
    path, with its directories' names and its files', as `top` is typed (see `walks.walked`).

    Returns:
      The element's annotation as source text and its reason, or `None` if it isn't known.

    """
    call: tuple[str, list[ast.expr]] | None = iterator_call(iterable)
    if call is not None and known.is_builtin(call[0]):
        return _iterator(*call, known, declared, infer)
    view: str
    receiver: ast.expr
    match iterable:
        case ast.Call(func=ast.Attribute(value=receiver, attr=view), args=[]) if view in DICT_VIEWS:
            return dict_view(receiver, view, known, declared, infer)
        case ast.GeneratorExp():
            return _generated(iterable, known, declared, infer)
        case _:
            found: Inference | None
            if (found := infer(iterable, known, declared)) is None:
                return walks.walked(iterable, known, lambda top: infer(top, known, declared))
            kinds: frozenset[str] = kinds_of(found, kind="loop")
            # Of an `X | None`, the `X`'s: `None` has none. A builtin container's or an
            # `Iterable[T]`'s, else a standard-library class's own.
            held: str = rebased(present(found.annotation, ""), "__iter__", known)
            element: Inference | None = generics.library_element(held, known)
            return element_type(held, f"the elements of {found.reason}", kinds) or (
                None if element is None else element._replace(kinds=kinds | element.kinds)
            )


def _iterator(
    name: str,
    args: list[ast.expr],
    known: Known,
    declared: Mapping[str, str],
    infer: Infer,
) -> Inference | None:
    """Infer what one of `ITERATORS`, called with `args`, yields.

    Returns:
      Its elements' annotation and reason, or `None` if an argument's elements aren't known.

    """
    if name == RANGE:
        return Inference("int", "`range`, which yields `int`s", frozenset({"loop"}))
    if name == MAP:
        return _mapped(args[0], known)
    if name == FILTER:
        return _filtered(args, known, declared, infer)
    if name in SAME_ELEMENTS or name == ITER:
        return looped(args[0], known, declared, infer) if name != ITER or len(args) == 1 else None
    parts: list[Inference | None] = [looped(arg, known, declared, infer) for arg in counted(name, args)]
    found: list[Inference] = [part for part in parts if part is not None]
    if len(found) != len(parts):
        return None
    annotations: list[str] = ["int"] * (name == ENUMERATE) + [part.annotation for part in found]
    return Inference(f"tuple[{', '.join(annotations)}]", f"`{name}`'s tuples", kinds_of(*found, kind="loop"))


def _filtered(
    args: list[ast.expr],
    known: Known,
    declared: Mapping[str, str],
    infer: Infer,
) -> Inference | None:
    """Infer what `filter(predicate, xs)` yields: `xs`'s elements, less `None` for a `None` predicate.

    Returns:
      The inference, or `None`: where `xs`'s elements aren't known, or the predicate may narrow them
      (see `_keeps`).

    """
    if len(args) != _PREDICATE:
        return None
    found: Inference | None = looped(args[1], known, declared, infer)
    if found is None or not (shapes.is_none(args[0]) or _keeps(args[0], known)):
        return None
    annotation: str = found.annotation
    if shapes.is_none(args[0]):
        types: frozenset[str] | None = members(annotation)
        rest: list[str]
        if not (rest := sorted((types or frozenset()) - {_NONE})):
            return None
        annotation = annotation if types == frozenset(rest) else " | ".join(rest)
    return Inference(annotation, f"`filter`, which keeps {found.reason}", kinds_of(found, kind="loop"))


def _keeps(predicate: ast.expr, known: Known) -> bool:
    """Check whether `filter`'s `predicate` keeps elements as they are, narrowing none.

    A `lambda`; a builtin (but `callable`), or a method of a builtin class (`str.isdigit`); or a
    function the module or another checked file defines, declaring a return other than a
    `TypeGuard` or `TypeIs`, or typed by its `return`s.

    Returns:
      Whether it does; not for any other callable, which may be declared to narrow.

    """
    name: str
    match predicate:
        case ast.Lambda():
            return True
        case ast.Name(id=name) if known.is_builtin(name):
            return name != _CALLABLE
        case ast.Attribute(value=ast.Name(id=name)) if known.is_builtin(name):
            return True
        case ast.Name() | ast.Attribute():
            callee: str = ast.unparse(predicate)
            declared: str | None = known.calls.get(callee)
            return (
                declared is not None and not _NARROWING.search(declared)
            ) or callee in known.returned.calls
        case _:
            return False


def _generated(
    value: ast.GeneratorExp,
    known: Known,
    declared: Mapping[str, str],
    infer: Infer,
) -> Inference | None:
    """Infer what a generator expression yields: its element, its targets typed as a loop's are.

    Not one with a condition whose element's type has a union in it, which the condition may narrow.

    Returns:
      The inference, or `None`.

    """
    found: Inference | None = infer(value.elt, known, comprehended(value, known, declared, infer))
    found = found and shapes.sifted(value, value.elt, found)
    filtered: bool = any(generator.ifs for generator in value.generators)
    if found is None or (filtered and _UNION.search(found.annotation)):
        return None
    loops: list[Inference | None] = [looped(g.iter, known, declared, infer) for g in value.generators]
    return Inference(
        found.annotation,
        "a generator expression's elements",
        kinds_of(found, *loops, kind="comprehension"),
    )


def _mapped(function: ast.expr, known: Known) -> Inference | None:
    """Infer what `map(function, ...)` yields: what `function` returns, whatever it's given.

    Returns:
      A fixed-return builtin's type (`map(int, parts)`), or a function's declared return; `None`
      for any other callable.

    """
    call: ast.Call = ast.copy_location(ast.Call(function, [], []), function)
    found: Inference | None = called.typed_call(call, known)
    if found is None or CONSTRUCTOR in found.kinds:
        return None
    return Inference(found.annotation, f"`map`, which yields {found.reason}", kinds_of(found, kind="loop"))


def looped_parts(
    iterable: ast.expr,
    known: Known,
    declared: Mapping[str, str],
    infer: Infer,
) -> list[LoopPart] | None:
    """Infer each part of the tuples `enumerate` or `zip` yields on its own, even if the others aren't known.

    `enumerate`'s index is always an `int`, whatever it counts.

    Returns:
      Each part's inference (`None` if it isn't known), with the values it came from (to judge
      whether it's a guess, see `iterated`); or `None` if `iterable` isn't such a call.

    """
    call: tuple[str, list[ast.expr]] | None = iterator_call(iterable)
    if call is None or call[0] not in {ENUMERATE, ZIP} or not known.is_builtin(call[0]):
        return None
    index: list[LoopPart] = (
        [(Inference("int", "`enumerate`'s index", frozenset({"loop"})), [])] if call[0] == ENUMERATE else []
    )
    return index + [(looped(arg, known, declared, infer), iterated(arg)) for arg in counted(*call)]


def dict_view(
    receiver: ast.expr,
    view: str,
    known: Known,
    declared: Mapping[str, str],
    infer: Infer,
) -> Inference | None:
    """Infer the elements of a `dict`'s `.keys()`, `.values()` or `.items()`.

    Returns:
      Them, or `None` if the receiver isn't a `dict` whose type is known.

    """
    found: Inference | None = infer(receiver, known, declared)
    types: tuple[str, str] | None
    if (types := None if found is None else dict_parts(rebased(found.annotation, view, known))) is None:
        return None
    by_view: dict[str, str] = {
        "keys": types[0],
        "values": types[1],
        "items": f"tuple[{types[0]}, {types[1]}]",
    }
    return Inference(by_view[view], f"a `dict`'s `.{view}()`", kinds_of(found, kind="loop"))
