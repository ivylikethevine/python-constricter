# SPDX-License-Identifier: MIT
"""Small shapes `--fix` types from their parts' types.

A union the author would write (`a if c else None`, `a or b`), a container or an empty one (`a or []`),
`type(x)`, `d.get(key, default)`, `os.environ[key]`, a module's own `__file__` and `__name__`, and a
call an unpacking alone can use (`partly`). `infer` types a part as
`constricter.fix.values.inference` does.

A part that is a read (`x`, `self.x`, `d[k]`) is taken as its declared type, which a type checker
narrows where the function tests it: it's named in the inference's `reads` (see `doubts`), and one
whose type is a union of two types or more isn't taken at all.
"""

import ast
import re
from collections.abc import Callable
from typing import Final, TypeAlias

from constricter.fix.core.known import ImportPlan, Inference, Known, Partial
from constricter.fix.libraries import stdlib
from constricter.fix.values.members import keyed, may_miss, parsed, partial_method
from constricter.rules.flow import members

Infer: TypeAlias = Callable[[ast.expr], Inference | None]
_NONE: Final = "None"
# The builtin classes an `isinstance` check names that say all there is of a value so checked.
_SCALARS: Final = frozenset({"bool", "bytes", "complex", "float", "int", "str"})
_HOLDS_NONE: Final = re.compile(r"\b(?:None|Optional)\b")
_READS: Final = (ast.Name, ast.Attribute, ast.Subscript)
_CONDITIONAL: Final = "conditional"  # the fix kind of `a if c else b`
_BOOLEAN: Final = "boolean"  # the fix kind of `a or b`
_BUILTIN: Final = "builtin"
_CALL: Final = "call"
_METHOD: Final = "method"
_STDLIB: Final = "stdlib"
_TYPE: Final = "type"
_GET: Final = "get"
_ENVIRON: Final = "os.environ"
_QUOTES: Final = frozenset("'\"")
_GETATTR: Final = "getattr"
_TYPING_ANY: Final = "typing.Any"
_WITH_DEFAULT: Final = 2  # `getattr(obj, name)`'s arguments; a third is its default
_MODULE_TEXTS: Final = frozenset({"__file__", "__name__"})  # a module's own names that hold a `str`
_CLASS_TEXTS: Final = frozenset({"__module__", "__name__", "__qualname__"})  # what a class holds a `str` in
_CLASS: Final = "__class__"


def is_none(node: ast.expr) -> bool:
    """Check whether a value is the literal `None`.

    Returns:
      Whether it is.

    """
    return isinstance(node, ast.Constant) and node.value is None


def typed(node: ast.expr, infer: Infer) -> Inference | None:
    """Type one part of a shape, a read only as the module docstring has it.

    Returns:
      Its inference, a read named in its `reads`; or `None`.

    """
    found: Inference | None = infer(node)
    if found is None or not isinstance(node, _READS):
        return found
    if len((members(found.annotation) or frozenset()) - {_NONE}) > 1:
        return None
    return found._replace(reads=(*found.reads, ast.unparse(node)))


def or_none(annotation: str) -> str | None:
    """Write `annotation`, or `None`: as it is if it allows `None` already.

    Returns:
      The union, or `None` for an annotation that can't be read, or holds a string (a forward
      reference can't take `| None` where it's evaluated).

    """
    found: frozenset[str] | None = members(annotation)
    if found is None or _QUOTES.intersection(annotation):
        return None
    return annotation if _NONE in found else f"{annotation} | {_NONE}"


def optional(value: ast.IfExp, infer: Infer) -> Inference | None:
    """Infer `a if c else None` (or `None if c else a`): `a`'s type, or `None`.

    Returns:
      The inference, or `None` if neither side or both are `None`, the other's type isn't known, or
      `c` tests it (`x if isinstance(x, C) else None`): it's narrowed there.

    """
    sides: list[ast.expr] = [side for side in (value.body, value.orelse) if not is_none(side)]
    tested: set[str] = {ast.unparse(node) for node in ast.walk(value.test) if isinstance(node, _READS)}
    known: bool = len(sides) == 1 and ast.unparse(sides[0]) not in tested
    found: Inference | None = typed(sides[0], infer) if known else None
    annotation: str | None = None if found is None else or_none(found.annotation)
    if found is None or annotation is None:
        return None
    return Inference(
        annotation,
        "one side of a conditional, or `None`",
        found.kinds | {_CONDITIONAL},
        found.reads,
    )


def sifted(value: ast.ListComp | ast.SetComp | ast.GeneratorExp, element: Inference) -> Inference | None:
    """Type the elements a comprehension keeps of a name it filters, by `is not None` or `isinstance`.

    Returns:
      The element's inference: less `None`, or as the one class it's checked for; `None` where
      that leaves nothing, or it's checked for anything but a class named there.

    """
    tests: list[ast.expr] = [test for each in value.generators for test in each.ifs]
    name: str = value.elt.id if isinstance(value.elt, ast.Name) else ""
    classes: list[ast.expr] = [found for test in tests for found in _instance_of(test, name)]
    named: list[str] = [
        ast.unparse(found) for found in classes if isinstance(found, ast.Name | ast.Attribute)
    ]
    if classes:
        kept: bool = len(classes) == len(named) == 1 and (named[0][:1].isupper() or named[0] in _SCALARS)
        return element._replace(annotation=named[0]) if kept else None
    types: frozenset[str] = members(element.annotation) or frozenset()
    if not (name and _NONE in types and any(_not_none(test) == name for test in tests)):
        return element
    rest: list[str] = sorted(types - {_NONE})
    return element._replace(annotation=" | ".join(rest)) if rest else None


def _not_none(test: ast.expr) -> str:  # the `x` of `x is not None`, else nothing
    name: str
    match test:
        case ast.Compare(left=ast.Name(id=name), ops=[ast.IsNot()], comparators=[ast.Constant(value=None)]):
            return name
        case _:
            return ""


def _instance_of(test: ast.expr, name: str) -> list[ast.expr]:
    """Find what `isinstance(name, C)` checks `name` for, anywhere in a test.

    Returns:
      Each `C`.

    """
    checked: str
    found: ast.expr
    classes: list[ast.expr] = []
    node: ast.AST
    for node in ast.walk(test):
        match node:
            case ast.Call(func=ast.Name(id="isinstance"), args=[ast.Name(id=checked), found]) if (
                name and checked == name
            ):
                classes.append(found)
            case _:
                pass
    return classes


def boolean(value: ast.BoolOp, infer: Infer) -> Inference | None:
    """Infer `a or b` and `a and b` whose operands have one type: that type.

    `or` gives an operand before its last only if it's true, which `None` never is: `a or b` with
    `a: T | None` and `b: T` is a `T`, as `a or []` is with `a: list[T] | None`.

    Returns:
      The last operand's type, or `None` if an operand's isn't known or they differ.

    """
    dropped: frozenset[str] = frozenset({_NONE}) if isinstance(value.op, ast.Or) else frozenset()
    built: str | None = _empty(value.values[-1]) if dropped else None
    parts: list[Inference | None] = [
        typed(operand, infer) for operand in value.values[: -1 if built else None]
    ]
    found: list[Inference] = [part for part in parts if part is not None]
    if len(found) != len(parts):
        return None
    types: set[frozenset[str]] = {(members(part.annotation) or frozenset()) - dropped for part in found}
    if len(types) != 1 or not next(iter(types)):
        return None
    annotation: str = found[-1].annotation
    if built is not None:
        # An empty display takes the type of the container before it.
        annotation = min(next(iter(types)))
        if len(next(iter(types))) != 1 or not annotation.startswith(f"{built}["):
            return None
    operator: str = "or" if dropped else "and"
    return Inference(
        annotation,
        f"the operands of `{operator}`, of one type",
        frozenset({_BOOLEAN}).union(*(part.kinds for part in found)),
        tuple(read for part in found for read in part.reads),
    )


def _empty(node: ast.expr) -> str | None:
    """Name the builtin container an empty display builds: `[]` a `list`, `{}` a `dict`.

    Returns:
      Its name, or `None` for any other value.

    """
    match node:
        case ast.List(elts=[]):
            return "list"
        case ast.Dict(keys=[]):
            return "dict"
        case _:
            return None


def emptied(value: ast.IfExp, infer: Infer) -> Inference | None:
    """Infer `a if c else []` (or `{} if c else a`): `a`'s type, a `list` (or a `dict`) of something.

    `a if a else []` is never `None`, whatever `a` may be.

    Returns:
      The inference, or `None` if neither side or both are an empty display, the other's type isn't
      that container's, or it may be `None` and `c` tests it another way, or holds what `c` tests
      and may be `None`: it's narrowed there.

    """
    sides: list[ast.expr] = [side for side in (value.body, value.orelse) if _empty(side) is None]
    built: str | None = _empty(value.body) or _empty(value.orelse)
    found: Inference | None = typed(sides[0], infer) if len(sides) == 1 else None
    types: frozenset[str] = frozenset() if found is None else members(found.annotation) or frozenset()
    container: str = min(types - {_NONE}, default="")
    if found is None or len(types - {_NONE}) != 1 or not container.startswith(f"{built}["):
        return None
    annotation: str = found.annotation
    tested: set[str] = {ast.unparse(node) for node in ast.walk(value.test) if isinstance(node, _READS)}
    held: bool = any(
        ast.unparse(node) in tested
        for node in ast.walk(sides[0])
        if node is not sides[0] and isinstance(node, _READS)
    )
    if held and _HOLDS_NONE.search(container):  # `[a] if a else []`: `a` is narrowed in the display
        return None
    if _NONE in types and ast.unparse(sides[0]) in tested:
        if sides[0] is not value.body or ast.unparse(value.test) != ast.unparse(sides[0]):
            return None
        annotation = container
    return Inference(
        annotation,
        "one side of a conditional, the other an empty display",
        found.kinds | {_CONDITIONAL},
        found.reads,
    )


def module_text(value: ast.expr, known: Known) -> Inference | None:
    """Infer a module's own `__file__` or `__name__`: a `str`.

    Returns:
      The inference, or `None` for any other value, or a module that binds the name itself.

    """
    name: str
    match value:
        case ast.Name(id=name) if name in _MODULE_TEXTS and (
            known.names.plan is None or name not in known.names.plan.taken
        ):
            return Inference("str", f"the module's own `{name}`", frozenset({_BUILTIN}))
        case _:
            return None


def _classed(value: ast.expr, known: Known) -> ast.expr | None:
    """Read the `x` of `type(x)` or `x.__class__`.

    Returns:
      It, or `None` for anything else, or a module that binds `type` itself.

    """
    arg: ast.expr
    attr: str
    match value:
        case ast.Call(func=ast.Name(id="type"), args=[arg], keywords=[]) if known.is_builtin(
            _TYPE,
        ) and not isinstance(arg, ast.Starred):
            return arg
        case ast.Attribute(value=arg, attr=attr) if attr == _CLASS:
            return arg
        case _:
            return None


def class_text(value: ast.expr, known: Known) -> Inference | None:
    """Infer a class's `__name__`, `__qualname__` or `__module__`: a `str`.

    Read of `type(x)` or `x.__class__`, whatever `x` is.

    Returns:
      The inference, or `None` for any other value.

    """
    owner: ast.expr
    attr: str
    match value:
        case ast.Attribute(value=owner, attr=attr) if attr in _CLASS_TEXTS and _classed(owner, known):
            return Inference("str", f"a class's `{attr}`", frozenset({_BUILTIN}))
        case _:
            return None


def class_of(value: ast.expr, known: Known, infer: Infer) -> Inference | None:
    """Infer `type(x)` or `x.__class__`, with `x`'s type `C` known: `type[C]`.

    Returns:
      The inference, or `None` for anything else, a module that binds `type` itself, or an `x`
      whose type is a union, `None` or a class itself.

    """
    arg: ast.expr | None
    if (arg := _classed(value, known)) is None:
        return None
    found: Inference | None = typed(arg, infer)
    types: frozenset[str] = frozenset() if found is None else members(found.annotation) or frozenset()
    if found is None or len(types) != 1 or _NONE in types:
        return None
    if isinstance(value, ast.Attribute) and found.annotation.startswith(f"{_TYPE}["):
        return None  # a class's own class is its metaclass
    return Inference(
        f"{_TYPE}[{found.annotation}]",
        f"`type` of {found.reason}",
        found.kinds | {_BUILTIN},
        found.reads,
    )


def defaulted(receiver: str, call: ast.Call, infer: Infer, known: Known) -> Inference | None:
    """Infer `d.get(key, default)` on a `dict[K, V]`, by a default of type `V`: `V` (`V | None`, by `None`).

    And on a `TypedDict`'s instance, by the literal key's type `V` (see `members.keyed`), with no
    default too: `V` for a required key, `V | None` for one that may be missing.

    Returns:
      The inference, or `None` for any other call, or a default of another type.

    """
    index: ast.expr
    rest: list[ast.expr]
    attr: str
    match call:
        case ast.Call(func=ast.Attribute(attr=attr), args=[index, *rest], keywords=[]) if (
            attr == _GET and len(rest) <= 1
        ):
            pass
        case _:
            return None
    item: ast.expr
    text: str
    reason: str
    match parsed(receiver):
        case ast.Subscript(value=ast.Name(id="dict" | "Dict"), slice=ast.Tuple(elts=[_, item])) if rest:
            text, reason = ast.unparse(item), "`dict.get` with a default of its values' type"
        case _:
            key: Inference | None
            if (key := keyed(receiver, index, known)) is None:
                return None
            text, reason = key.annotation, f"`get` of {key.reason}"
            if not may_miss(receiver, index, known) and _NONE not in (members(text) or ()):
                if not rest:
                    return Inference(text, reason, frozenset({_METHOD}))
                if is_none(rest[0]):  # `V` to pyright, `V | None` to mypy
                    return None
    if not rest or is_none(rest[0]):
        union: str | None = or_none(text)
        return None if union is None else Inference(union, reason, frozenset({_METHOD}))
    found: Inference | None = infer(rest[0])
    same: bool = found is not None and found.annotation == text
    return Inference(text, reason, found.kinds | {_METHOD}) if found and same else None


def partly(value: ast.expr, known: Known, infer: Infer) -> Inference | None:
    """Infer a call whose declared return has a vague part: no fix past `vague`, but what's read of it is.

    A function's, or a method's on a receiver whose type is known (see `known.Partial`): an
    unpacking splits it, and a loop over it has its elements (`for name in hints()`, a `str`).

    Returns:
      The whole return, vague parts and all; or `None` for any other value.

    """
    func: ast.expr
    receiver: ast.expr
    name: str
    partial: Partial = known.indirect.partial
    match value:
        case ast.Call(func=ast.Name() | ast.Attribute() as func) if (
            partial.calls and ast.unparse(func) in partial.calls
        ):
            callee: str = ast.unparse(func)
            return Inference(partial.calls[callee], f"`{callee}`'s declared return type", frozenset({_CALL}))
        case ast.Call(func=ast.Attribute(value=receiver, attr=name)):
            owner: Inference | None = infer(receiver)
            found: str | None = None if owner is None else partial_method(owner.annotation, name, known)
            if owner is None or found is None:
                return None
            return Inference(
                found,
                f"`{owner.annotation}.{name}`'s declared return type",
                frozenset({_METHOD}) if isinstance(receiver, ast.Name) else owner.kinds | {_METHOD},
            )
        case _:
            return None


def attribute_of(value: ast.expr, known: Known, infer: Infer) -> Inference | None:
    """Infer `getattr(obj, name)`: an `Any`; with a default of a known type `T`, an `Any | T`.

    Where `vague` lets it be written (from 1), `Any` named as the module can.

    Returns:
      The inference, or `None` for anything else, a module that binds `getattr` itself, or a
      default of no known type.

    """
    args: list[ast.expr]
    match value:
        case ast.Call(func=ast.Name(id="getattr"), args=[_, _, *_] as args, keywords=[]) if (
            len(args) <= _WITH_DEFAULT + 1
            and known.is_builtin(_GETATTR)
            and known.limits.vague > 0
            and not any(isinstance(arg, ast.Starred) for arg in args)
        ):
            pass
        case _:
            return None
    plan: ImportPlan | None = known.names.plan
    spelled: str | None = None if plan is None else plan.spell(_TYPING_ANY)
    default: Inference | None = infer(args[2]) if len(args) > _WITH_DEFAULT else None
    if spelled is None or (len(args) > _WITH_DEFAULT and default is None and not is_none(args[2])):
        return None
    union: str = (
        spelled
        if len(args) == _WITH_DEFAULT
        else f"{spelled} | {_NONE if default is None else default.annotation}"
    )
    return Inference(
        union,
        "`getattr`'s return type",
        frozenset({_BUILTIN}) | (default.kinds if default else frozenset()),
    )


def environment(value: ast.expr, known: Known) -> Inference | None:
    """Infer `os.environ[key]`, however the module names `os.environ`: a `str`.

    Returns:
      The inference, or `None` for anything else, a slice included.

    """
    mapping: ast.expr
    index: ast.expr
    match value:
        case ast.Subscript(value=ast.Name() | ast.Attribute() as mapping, slice=index) if (
            not isinstance(index, ast.Slice) and stdlib.resolved(mapping, known.names.stdlib) == _ENVIRON
        ):
            return Inference("str", f"`{_ENVIRON}`'s values", frozenset({_STDLIB}))
        case _:
            return None
