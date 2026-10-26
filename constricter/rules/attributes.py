"""LVA013 (opt-in): an instance attribute first stored by a method's `self.x = value`, with no annotation.

Only a plain class's (see `_plain`): an attribute another file's base may declare is that file's to
type. The fix is the class's every store joined (`stored.attribute_types`; `None` and one other
type, their union), written at its first store that can take it: `self.x: int = 0`, which a type
checker takes as the attribute's declaration.
"""

import ast
from collections.abc import Iterator, Mapping, Sequence
from typing import Final, NamedTuple

from constricter.fix.core.known import Inference, Returned
from constricter.fix.values import stored
from constricter.fix.values.doubts import bare
from constricter.fix.values.inference import ASSIGNED
from constricter.fix.values.shapes import or_none
from constricter.offences import UNANNOTATED_ATTRIBUTE, Fix, Offence
from constricter.rules.scope import Scope
from constricter.source.syntax import own_nodes
from constricter.source.walked import classes, walk

_OBJECT: Final = "object"
_OPTIONAL: Final = "optional"  # the fix kind of `None`, then one known type


class _Attribute(NamedTuple):
    """An attribute a plain class's methods store: where first, and its first plain `self.x = value`."""

    owner: ast.ClassDef
    attr: str
    first: ast.Attribute
    plain: tuple[ast.Attribute, int] | None  # the target, and its method's `id()`
    declared: bool  # annotated in a method (`self.x: int = 0`)


def unannotated(
    tree: ast.Module,
    found: Returned,
    assigned: Mapping[int, Sequence[stored.Assigned]],
    scopes: Mapping[int, Scope],
) -> list[Offence]:
    """Report the plain classes' attributes no annotation declares, each where it's first stored.

    `found`: what the module's methods store, joined (see `returned.returned`); `assigned`: each
    function's `self.x = value`s, by its `id()`; `scopes`: each method's checked scope, by its
    `id()`, which offers the fix as its own would be.

    Returns:
      An offence for each, at its first plain `self.x = value` if it has one, with the class's type
      for it as a guess: another file's subclass or outside code may store it too.

    """
    offences: list[Offence] = []
    each: _Attribute
    for each in _attributes(tree):
        if each.declared:
            continue
        target: ast.Attribute = each.first if each.plain is None else each.plain[0]
        fix: Fix | None = None
        typed: tuple[str, frozenset[str]] | None
        scope: Scope
        if (
            each.plain is not None
            and (typed := _typed(each, found, assigned)) is not None
            # A generic class written without its arguments is no fix, as a binding's isn't.
            and not bare(typed[0], (scope := scopes[each.plain[1]]).settings.facts.generics)
        ):
            fix = scope.offer(
                Inference(typed[0], f"`{each.owner.name}.{each.attr}`'s assignments", typed[1]),
                typed[1],
                unsafe=True,
            )
        offences.append(
            Offence(target.lineno, target.col_offset, _spelled(each.attr), UNANNOTATED_ATTRIBUTE, fix),
        )
    return offences


def _typed(
    each: _Attribute,
    found: Returned,
    assigned: Mapping[int, Sequence[stored.Assigned]],
) -> tuple[str, frozenset[str]] | None:
    """Type an attribute by the class's stores: as a read of it is, else `None` and one known `T`.

    The latter only where every store of it in the class is a plain `self.x = value` in one of its
    own methods, each value's type known.

    Returns:
      Its type, and what that rests on; `None` if it has none.

    """
    key: str = f"{each.owner.name}.{each.attr}"
    annotation: str | None
    if (annotation := found.attributes.get(each.owner.name, {}).get(each.attr)) is not None:
        return annotation, found.guesses.get(key, frozenset()) | {ASSIGNED}
    values: list[stored.Recorded] = [
        value
        for method in stored.self_methods(each.owner)
        for attr, value in assigned.get(id(method), ())
        if attr == each.attr
    ]
    stores: int = sum(
        isinstance(part, ast.Attribute)
        and _of_self(part)
        and part.attr == each.attr
        and not isinstance(part.ctx, ast.Load)
        for part in walk(each.owner)
    )
    # A `None` is recorded as a value of no known type is: every such value must be one.
    nones: int = sum(
        isinstance(target, ast.Attribute) and _of_self(target) and target.attr == each.attr
        for method in stored.self_methods(each.owner)
        for part in own_nodes(method.body)
        if isinstance(part, ast.Assign) and isinstance(part.value, ast.Constant) and part.value.value is None
        for target in part.targets
    )
    types: set[str] = {value.annotation for value, _ in values if value is not None}
    joined: str | None
    if (
        len(values) != stores
        or not nones
        or sum(value is None for value, _ in values) != nones
        or len(types) != 1
        or (joined := or_none(next(iter(types)))) is None
    ):
        return None
    return joined, frozenset({ASSIGNED, _OPTIONAL}).union(*(origins for _, origins in values))


def counted(tree: ast.Module) -> tuple[int, int]:
    """Count the plain classes' attributes, for `--coverage`, as `unannotated` reads them.

    Returns:
      How many are declared, and of how many.

    """
    found: list[_Attribute] = list(_attributes(tree))
    return sum(each.declared for each in found), len(found)


def _spelled(attr: str) -> str:
    # The offence's name, as the source spells its target: `--fix` writes `: T` after it.
    return f"{stored.SELF}.{attr}"


def _attributes(tree: ast.Module) -> Iterator[_Attribute]:
    """Find the attributes each plain class's own methods store, that neither it nor a base binds otherwise.

    Not a dunder, nor one its body binds (a class attribute, a method, a property), nor one a class
    of the module's above it binds or stores.

    Yields:
      Each, in source order.

    """
    plain: frozenset[str] = _plain(tree)
    node: ast.ClassDef
    for node in classes(tree):
        if node.name not in plain:
            continue
        held: set[str] = set(stored.class_bound(node))
        base: ast.ClassDef
        for base in stored.superclasses(tree, node):
            held |= stored.class_bound(base)
            held.update(attr for attr, _, _ in _stores(base))
        declared: frozenset[str] = _declared(node)
        firsts: dict[str, ast.Attribute] = {}
        plains: dict[str, tuple[ast.Attribute, int]] = {}
        attr: str
        target: ast.Attribute
        method: int
        for attr, target, method in sorted(_stores(node), key=lambda one: (one[1].lineno, one[1].col_offset)):
            if attr in held or (attr.startswith("__") and attr.endswith("__")):
                continue
            _ = firsts.setdefault(attr, target)
            if method and attr not in plains:
                plains[attr] = (target, method)
        for attr, target in firsts.items():
            yield _Attribute(node, attr, target, plains.get(attr), attr in declared)


def _stores(node: ast.ClassDef) -> Iterator[tuple[str, ast.Attribute, int]]:
    """Find the class's own methods' stores and deletions of `self`'s attributes, not a nested scope's.

    Yields:
      Each one's attribute, its target, and its method's `id()` where it's a plain `self.x = value`
      (one target, not unpacked), else 0.

    """
    method: ast.FunctionDef | ast.AsyncFunctionDef
    for method in stored.self_methods(node):
        parts: list[ast.AST] = list(own_nodes(method.body))
        plain: set[int] = {
            id(part.targets[0]) for part in parts if isinstance(part, ast.Assign) and len(part.targets) == 1
        }
        part: ast.AST
        for part in parts:
            if isinstance(part, ast.Attribute) and _of_self(part) and not isinstance(part.ctx, ast.Load):
                yield part.attr, part, id(method) if id(part) in plain else 0


def _of_self(target: ast.expr) -> bool:
    return (
        isinstance(target, ast.Attribute)
        and isinstance(target.value, ast.Name)
        and target.value.id == stored.SELF
    )


def _declared(node: ast.ClassDef) -> frozenset[str]:
    """Find the attributes an annotation in the class declares, in any method.

    `self.x: int = 0`, or a type comment (`self.x = 0  # type: int`), which a type checker reads as one.

    Returns:
      Them.

    """
    return frozenset(
        target.attr
        for part in walk(node)
        if isinstance(part, ast.AnnAssign) or (isinstance(part, ast.Assign) and part.type_comment)
        for target in ((part.target,) if isinstance(part, ast.AnnAssign) else part.targets)
        if isinstance(target, ast.Attribute) and _of_self(target)
    )


def _plain(tree: ast.Module) -> frozenset[str]:
    """Find the module's plain classes: each defined once, with no keyword, its bases plain or `object`.

    A base of another file's, or one with a metaclass, may declare an attribute itself or read
    annotations at runtime.

    Returns:
      Their names.

    """
    counts: Mapping[str, int] = stored.class_names(tree)
    candidates: list[ast.ClassDef] = [
        node for node in classes(tree) if counts[node.name] == 1 and not node.keywords
    ]
    plain: set[str] = set()
    _pass: ast.ClassDef
    for _pass in candidates:  # each pass adds one at least, or ends: a base may come after its class
        added: set[str] = {
            node.name
            for node in candidates
            if node.name not in plain
            and all(
                isinstance(base, ast.Name) and (base.id == _OBJECT or base.id in plain) for base in node.bases
            )
        }
        if not added:
            break
        plain |= added
    return frozenset(plain)
