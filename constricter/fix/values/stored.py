"""What a class's methods store in its attributes, for `--fix` on `self.x` (see `returned.Table`).

Each `self.x = value` and each read of `self.x` its methods make, as the checker saw them
(`Assigned`, `Used`), are joined into the attribute's type: by every value it's assigned in the
class and the classes above and under it in the module (`attribute_types`), and, for an attribute bound
to an empty container, by what's added to it (`_filled`), there or where another file's base binds
it (`hand`). And which of a method's reads of `self` an attribute's type, once known, retypes
(`reads`, `reads_own`).
"""

import ast
from collections import Counter
from collections.abc import Collection, Iterator, Mapping, Sequence
from functools import lru_cache
from typing import Final, TypeAlias
from weakref import WeakKeyDictionary

from constricter.fix.core.known import Inference, Returned
from constricter.fix.values import fills
from constricter.fix.values.inference import ASSIGNED
from constricter.fix.values.shapes import NUMBERS
from constricter.source.syntax import FunctionDef, Start, within
from constricter.source.walked import classes, of_type

# A `return` statement as the checker saw it: its value's inference (`None`: none, or unknown), and
# what that rests on if it's a guess (`FIX_KINDS`; empty: certain). A generator has one: its type.
Recorded: TypeAlias = tuple[Inference | None, frozenset[str]]
# A `self.x = value` as the checker saw it: the attribute, and its value as a `return`'s is recorded.
Assigned: TypeAlias = tuple[str, Recorded]
# What a read of an empty container adds to it, each part as a `return`'s value is recorded (a
# `dict`'s key and value, any other's element): none for one that adds nothing, `None` for one that
# might, unseen.
Added: TypeAlias = tuple[Recorded, ...] | None
# A read of `self.x`, an attribute bound to an empty container, as the checker saw it.
Used: TypeAlias = tuple[str, Added]
# What a class's methods store in its attributes: each one's assigned values, and what's added to it.
_Stored: TypeAlias = tuple[dict[str, list[Recorded]], dict[str, list[Added]]]
_Emptied: TypeAlias = tuple[str, str]  # a `self.x = []`: the attribute, and the container's kind
_Under: TypeAlias = tuple[list[Recorded], list[Added], int]  # see `_under`
_FILLED: Final = "filled"  # the fix kind of an empty container typed by what's added to it
SELF: Final = "self"


_NOT_METHODS: Final = frozenset({"staticmethod", "classmethod"})
FUNCTIONS: Final = (ast.FunctionDef, ast.AsyncFunctionDef)
# The attributes each of a module's classes takes from another file's base that binds them to an
# empty container and does no more with them: each one's kind, by class (see `hand`).
_Handed: TypeAlias = Mapping[str, Mapping[str, str]]
_HANDED: Final[WeakKeyDictionary[ast.Module, _Handed]] = WeakKeyDictionary()


_Uses: TypeAlias = tuple[list[Start], list[str]]  # attributes used: where each starts, and its name
_Listed: TypeAlias = list[tuple[Start, str]]  # attributes used, each where it starts and its name


def hand(tree: ast.Module, emptied: Mapping[str, Mapping[str, str]]) -> None:
    """Tell which attributes `tree`'s classes take bound empty from another file's base (see `_HANDED`).

    Before the module is checked: its classes' methods' fills of one then type it for them, as
    their own empty container's do.
    """
    _HANDED[tree] = emptied


def untouched(tree: ast.Module) -> dict[str, dict[str, str]]:
    """Find the attributes each class binds to an empty container and does no more with, in the module.

    Neither it nor a class of the module's under it reads or stores one again: what fills it is
    another file's to say.

    Returns:
      Each such attribute's kind, by class; a class with none is left out.

    """
    found: dict[str, dict[str, str]] = {}
    node: ast.ClassDef
    for node in classes(tree):
        stored: list[str] = _stored_in(tree, node)
        kinds: dict[str, str] = {
            attr: kind
            for attr, (kind, count) in _emptied(tree, node).items()
            if class_names(tree)[node.name] == 1
            and stored.count(attr) == count
            and not any(_read(tree, each, attr) for each in (node, *subclasses(tree, node)))
            and not any(attr in _emptied(tree, each) for each in subclasses(tree, node))
        }
        if kinds:
            found[node.name] = kinds
    return found


@lru_cache(maxsize=4)  # asked once per round, of the same module
def class_names(tree: ast.Module) -> Mapping[str, int]:
    """Count the classes the module defines by each name.

    Returns:
      Each name's count.

    """
    return Counter(node.name for node in classes(tree))


def attribute_types(
    tree: ast.Module,
    node: ast.ClassDef,
    seen: tuple[Mapping[int, Sequence[Assigned]], Mapping[int, Sequence[Used]]],
) -> Iterator[tuple[str, str, frozenset[str]]]:
    """Find the class's unannotated instance attributes whose every assignment decides their type.

    One counts when every place the class's code stores or deletes it (`self.x`, anywhere in the
    class) is a plain `self.x = value` in one of its own methods, neither the class's body nor a
    class of the module's above it binds the name (a class attribute, a method, a property) or,
    above it, stores it, and every value's type is known and the same, or
    numbers (`int`, then `float`: the widest). One bound to an empty container counts by what the
    class's methods, and those of the module's classes under it, add to it (see `_filled`). A guess:
    another file's subclass or outside code may assign it too.

    `seen`: each checked function's `self.x = value`s, and its reads of `self`'s empty containers.

    Yields:
      Each one's name, type, and what that rests on: `assigned`, and its values' own guesses.

    """
    values: dict[str, list[Recorded]]
    uses: dict[str, list[Added]]
    values, uses = _stored(node, seen)
    yield from _handed(tree, node, uses, seen)
    if not values:
        return
    stores: Counter[str] = Counter(_stored_in(tree, node))
    bound: frozenset[str] = class_bound(node)
    held: frozenset[str] = bound.union(
        *((*class_bound(base), *_stored_in(tree, base)) for base in superclasses(tree, node)),
    )
    attr: str
    found: list[Recorded]
    for attr in sorted(_emptied(tree, node).keys() & values.keys() - bound):
        filled: tuple[str, frozenset[str]] | None
        if (
            stores[attr] == len(values[attr])
            and len(uses.get(attr, ())) == _read(tree, node, attr)
            and (filled := _filled_under(tree, node, attr, (values[attr], uses.get(attr, ())), seen))
            is not None
        ):
            yield attr, *filled
    for attr, found in values.items():
        types: set[str] = {value.annotation for value, _ in found if value is not None}
        widest: str | None
        if (
            stores[attr] == len(found)
            and attr not in held
            and all(value is not None for value, _ in found)
            and (widest := _widest(types)) is not None
        ):
            yield attr, widest, frozenset({ASSIGNED}).union(*(origins for _, origins in found))


def _handed(
    tree: ast.Module,
    node: ast.ClassDef,
    uses: Mapping[str, Sequence[Added]],
    seen: tuple[Mapping[int, Sequence[Assigned]], Mapping[int, Sequence[Used]]],
) -> Iterator[tuple[str, str, frozenset[str]]]:
    """Type the attributes the class takes bound empty from another file's base, by its own methods' fills.

    And those of the module's classes under it, as `_filled_under` gathers them (see `_HANDED`).

    Yields:
      Each one's name, type, and what that rests on.

    """
    attr: str
    kind: str
    for attr, kind in sorted(_HANDED.get(tree, {}).get(node.name, {}).items()):
        more: _Under | None = _under(tree, subclasses(tree, node), attr, seen)
        own: Sequence[Added] = uses.get(attr, ())
        filled: tuple[str, frozenset[str]] | None = (
            None
            if more is None or more[0] or len(own) != _read(tree, node, attr) or attr in class_bound(node)
            else _filled((kind, 0), [], [*own, *more[1]])
        )
        if filled is not None and _stored_in(tree, node).count(attr) == 0:
            yield attr, *filled


def _filled_under(
    tree: ast.Module,
    node: ast.ClassDef,
    attr: str,
    own: tuple[Sequence[Recorded], Sequence[Added]],
    seen: tuple[Mapping[int, Sequence[Assigned]], Mapping[int, Sequence[Used]]],
) -> tuple[str, frozenset[str]] | None:
    # `_filled`, by what the class's `own` methods store and add, and the module's classes' under it.
    more: _Under | None = _under(tree, subclasses(tree, node), attr, seen)
    kind: str
    bare: int
    kind, bare = _emptied(tree, node)[attr]
    return None if more is None else _filled((kind, bare + more[2]), [*own[0], *more[0]], [*own[1], *more[1]])


@lru_cache(maxsize=1024)  # asked of the same classes once per round, and of each method as it's checked
def subclasses(module: ast.Module, node: ast.ClassDef) -> tuple[ast.ClassDef, ...]:
    """Find the module's classes under `node`, however far: each defined once, by a base named as it is.

    Returns:
      Them, in source order; none for a class whose name another of the module's has.

    """
    counts: Mapping[str, int] = class_names(module)
    names: set[str] = {node.name} if counts[node.name] == 1 else set()
    found: list[ast.ClassDef] = []
    each: ast.ClassDef
    for each in _in_order(module):
        if (
            each is not node
            and counts[each.name] == 1
            and any(isinstance(base, ast.Name) and base.id in names for base in each.bases)
        ):
            names.add(each.name)
            found.append(each)
    return tuple(found)


@lru_cache(maxsize=4)  # asked of each of the module's classes
def _in_order(module: ast.Module) -> tuple[ast.ClassDef, ...]:
    """List the module's classes in source order, once (sorted again for each class, most of `subclasses`).

    Returns:
      Them.

    """
    return tuple(sorted(classes(module), key=lambda one: (one.lineno, one.col_offset)))


def superclasses(module: ast.Module, node: ast.ClassDef) -> list[ast.ClassDef]:
    """Find the module's classes `node` is under, however far (see `subclasses`).

    Returns:
      Them, in `classes`' order.

    """
    return list(_above(module).get(id(node), ()))


@lru_cache(maxsize=4)  # asked of each of the module's classes, and each method, as it's checked
def _above(module: ast.Module) -> dict[int, list[ast.ClassDef]]:
    """Map each of the module's classes to those it's under (see `superclasses`), by its `id()`.

    Once for the module: asking each class of every other was a check's time squared in its classes.

    Returns:
      Each one's, in `classes`' order; none for a class under none.

    """
    found: dict[int, list[ast.ClassDef]] = {}
    each: ast.ClassDef
    under: ast.ClassDef
    for each in classes(module):
        for under in subclasses(module, each):
            found.setdefault(id(under), []).append(each)
    return found


def _under(
    tree: ast.Module,
    family: Sequence[ast.ClassDef],
    attr: str,
    seen: tuple[Mapping[int, Sequence[Assigned]], Mapping[int, Sequence[Used]]],
) -> _Under | None:
    """Gather what the classes under one (`family`) store in its attribute `attr`, an empty container.

    Each one's methods' `self.attr = value`s and reads of it, as the class's own are gathered.

    Returns:
      Their values, their uses, and how many of their assignments bind it empty too; or `None` if
      one binds the name in its body, stores it any other way, or reads it where the checker
      didn't judge the read (a nested function).

    """
    found: _Under = ([], [], 0)
    node: ast.ClassDef
    for node in family:
        values: list[Recorded] = [
            value
            for method in self_methods(node)
            for name, value in seen[0].get(id(method), ())
            if name == attr
        ]
        uses: list[Added] = [
            use for method in self_methods(node) for name, use in seen[1].get(id(method), ()) if name == attr
        ]
        if (
            attr in class_bound(node)
            or _stored_in(tree, node).count(attr) != len(values)
            or _read(tree, node, attr) != len(uses)
        ):
            return None
        found[0].extend(values)
        found[1].extend(uses)
    return found[0], found[1], sum(_emptied(tree, node).get(attr, ("", 0))[1] for node in family)


def _stored(
    node: ast.ClassDef,
    seen: tuple[Mapping[int, Sequence[Assigned]], Mapping[int, Sequence[Used]]],
) -> _Stored:
    """Gather what the class's own methods store in each attribute of `self` (see `attribute_types`).

    Returns:
      Each attribute's assigned values, and each empty container's reads.

    """
    values: dict[str, list[Recorded]] = {}
    uses: dict[str, list[Added]] = {}
    method: FunctionDef
    for method in self_methods(node):
        attr: str
        value: Recorded
        for attr, value in seen[0].get(id(method), ()):
            values.setdefault(attr, []).append(value)
        use: Added
        for attr, use in seen[1].get(id(method), ()):
            uses.setdefault(attr, []).append(use)
    return values, uses


def _filled(
    emptied: tuple[str, int],
    found: Sequence[Recorded],
    uses: Sequence[Added],
) -> tuple[str, frozenset[str]] | None:
    """Type an attribute bound to an empty container by what its class's methods add to it.

    `emptied`: its kind, and how many of its assignments (`found`) bind it empty; `uses`: every read
    of it in the class, as `fills.stored` judges them. As `fills.filled` types a local: no read may
    add something unseen, and what's added, or assigned to it instead, must be typed alike.

    Returns:
      Its type, and what that rests on (`assigned`, `filled`, and its values' own guesses); or `None`.

    """
    kind: str
    bare: int
    kind, bare = emptied
    values: list[Recorded] = [value for value in found if value[0] is not None]
    added: list[tuple[Recorded, ...]] = [use for use in uses if use]
    parts: list[Recorded] = [*values, *(part for use in added for part in use)]
    if len(values) + bare != len(found) or None in uses or any(part[0] is None for part in parts):
        return None
    types: set[str] = {value.annotation for value, _ in values if value is not None} | {
        f"{kind}[{', '.join(part.annotation for part, _ in use if part is not None)}]" for use in added
    }
    if len(types) != 1:
        return None
    return types.pop(), frozenset({ASSIGNED, _FILLED}).union(*(origins for _, origins in parts))


@lru_cache(maxsize=4)  # asked of the same module's classes, each round
def _empties(module: ast.Module) -> tuple[list[Start], list[_Emptied]]:
    """Find the module's `self.x = []`s: each assignment of an empty container to an attribute of `self`.

    Returns:
      Where each starts, in source order; and its attribute and kind (see `fills.empty`).

    """
    found: list[tuple[Start, _Emptied]] = []
    node: ast.AST
    for node in of_type(module, ast.Assign):
        kind: str | None
        if isinstance(node, ast.Assign) and (kind := fills.empty(node.value)) is not None:
            found.extend(
                ((target.lineno, target.col_offset), (target.attr, kind))
                for target in node.targets
                if isinstance(target, ast.Attribute)
                and isinstance(target.value, ast.Name)
                and target.value.id == SELF
            )
    found.sort()
    return [start for start, _ in found], [each for _, each in found]


@lru_cache(maxsize=1024)  # asked of the same classes once per round, and of each method as it's checked
def _emptied(module: ast.Module, node: ast.ClassDef) -> Mapping[str, tuple[str, int]]:
    """Find the attributes the class's code binds to an empty container, always of one kind.

    Returns:
      Each one's kind, and how many assignments bind it so.

    """
    starts: list[Start]
    found: list[_Emptied]
    starts, found = _empties(module)
    kinds: dict[str, list[str]] = {}
    attr: str
    kind: str
    for attr, kind in found[within(starts, node)]:
        kinds.setdefault(attr, []).append(kind)
    return {attr: (each[0], len(each)) for attr, each in kinds.items() if len(set(each)) == 1}


def empties(module: ast.Module, func: FunctionDef) -> Mapping[str, str]:
    """Find the attributes of `self` a method's class, or one above it, binds to an empty container.

    Returns:
      Each one's kind; none for a function that isn't a class's own method.

    """
    node: ast.ClassDef | None = owners(module).get(id(func))
    return {} if node is None else _class_empties(module, node)


@lru_cache(maxsize=1024)  # asked of each of a class's methods as it's checked
def _class_empties(module: ast.Module, node: ast.ClassDef) -> Mapping[str, str]:
    """Find the attributes of `self` a class, or one above it, binds to an empty container.

    Returns:
      Each one's kind.

    """
    # Its own, and those of the module's classes it's under: their fills are its own too.
    above: list[ast.ClassDef] = superclasses(module, node)
    handed: Mapping[str, Mapping[str, str]] = _HANDED.get(module, {})
    return {
        **{attr: kind for each in (*above, node) for attr, kind in handed.get(each.name, {}).items()},
        **{attr: kind for each in (*above, node) for attr, (kind, _) in _emptied(module, each).items()},
    }


def _read(module: ast.Module, node: ast.ClassDef, attr: str) -> int:
    """Count the class's reads of `self.attr`, anywhere in it: a nested function's too.

    Returns:
      How many.

    """
    starts: list[Start]
    found: list[str]
    starts, found = _uses(module)[0]
    return found[within(starts, node)].count(attr)


def _stored_in(module: ast.Module, node: ast.ClassDef) -> list[str]:
    """List the class's stores to attributes of `self`, anywhere in it: its deletions too.

    Returns:
      Each one's attribute, in source order.

    """
    starts: list[Start]
    found: list[str]
    starts, found = _uses(module)[2]
    return found[within(starts, node)]


def _widest(types: set[str]) -> str | None:
    """Find the one type every value's fits: the only one, or the widest of builtin numbers.

    Returns:
      It, or `None`.

    """
    if len(types) == 1:
        return next(iter(types))
    return max(types, key=NUMBERS.index) if types <= set(NUMBERS) else None  # an attribute takes the widest


@lru_cache(maxsize=4)  # asked of each function as it's checked
def owners(module: ast.Module) -> dict[int, ast.ClassDef]:
    """Map each class's own methods (see `self_methods`) to it, by the method's `id()`.

    Returns:
      Each one's class.

    """
    return {id(method): node for node in classes(module) for method in self_methods(node)}


@lru_cache(maxsize=1024)  # asked of the same classes once per round
def self_methods(node: ast.ClassDef) -> tuple[FunctionDef, ...]:
    """Find the class's own methods whose first parameter is `self`: not a static or class method.

    Returns:
      Them.

    """
    return tuple(
        stmt
        for stmt in node.body
        if isinstance(stmt, FUNCTIONS)
        and [arg.arg for arg in (*stmt.args.posonlyargs, *stmt.args.args)][:1] == [SELF]
        and not any(isinstance(d, ast.Name) and d.id in _NOT_METHODS for d in stmt.decorator_list)
    )


@lru_cache(maxsize=1024)  # asked of the same classes once per round
def class_bound(node: ast.ClassDef) -> frozenset[str]:
    """Find the names the class's own body binds: its class attributes, methods and nested classes.

    Returns:
      Them.

    """
    return frozenset(
        name.id
        for stmt in node.body
        for target in _body_targets(stmt)
        for name in ast.walk(target)
        if isinstance(name, ast.Name)
    ) | frozenset(stmt.name for stmt in node.body if isinstance(stmt, (*FUNCTIONS, ast.ClassDef)))


def _body_targets(stmt: ast.stmt) -> list[ast.expr]:
    """List what a class-body statement assigns to.

    Returns:
      Its targets: none but for an assignment.

    """
    targets: list[ast.expr]
    target: ast.expr
    match stmt:
        case ast.Assign(targets=targets):
            return targets
        case ast.AnnAssign(target=target) | ast.AugAssign(target=target):
            return [target]
        case _:
            return []


def reads(module: ast.Module, node: ast.AST, attributes: Collection[str], *, anywhere: bool = False) -> bool:
    """Check whether `node` (a function, or a statement) reads any of `attributes` of `self` (`self.a`).

    `anywhere`: of any value (`x.a`, whatever `x` is), by its name alone, as `called` counts methods.

    Returns:
      Whether it does: otherwise checking it again, knowing their types, would change nothing.

    """
    starts: list[Start]
    found: list[str]
    starts, found = _uses(module)[1 if anywhere else 0]
    return bool(attributes) and any(attr in attributes for attr in found[within(starts, node)])


def reads_own(tree: ast.Module, func: FunctionDef, classes_of: Mapping[int, str], found: Returned) -> bool:
    """Check whether a method reads an attribute of its own class's (`self.a`) that `found` types.

    `classes_of`: each method's class, by the method's `id()`.

    Returns:
      Whether it does: checking it again could type more.

    """
    owner: str | None
    if (owner := classes_of.get(id(func))) is None:
        return False
    node: ast.ClassDef | None = owners(tree).get(id(func))
    above: list[str] = [] if node is None else [each.name for each in superclasses(tree, node)]
    return reads(tree, func, {attr for name in (owner, *above) for attr in found.attributes.get(name, {})})


@lru_cache(maxsize=4)  # asked of the same module's functions and classes, each round
def _uses(module: ast.Module) -> tuple[_Uses, _Uses, _Uses]:
    """Find the module's attribute uses: reads of `self`'s (`self.a`), reads of any, stores to `self`'s.

    A store includes a deletion (`del self.a`).

    Returns:
      Those three: each's starts, in source order, and its attribute's name.

    """
    found: tuple[_Listed, ...] = ([], [], [])
    node: ast.AST
    receiver: ast.expr
    attr: str
    for node in of_type(module, ast.Attribute):
        match node:
            case ast.Attribute(value=receiver, ctx=ast.Load(), attr=attr):
                if isinstance(receiver, ast.Name) and receiver.id == SELF:
                    found[0].append(((node.lineno, node.col_offset), attr))
                found[1].append(((node.lineno, node.col_offset), attr))
            case ast.Attribute(value=ast.Name(id="self"), attr=attr):  # a store or deletion
                found[2].append(((node.lineno, node.col_offset), attr))
            case _:
                pass
    kind: _Listed
    for kind in found:
        kind.sort()
    of_self: _Uses
    of_any: _Uses
    stored: _Uses
    of_self, of_any, stored = (([start for start, _ in kind], [attr for _, attr in kind]) for kind in found)
    return of_self, of_any, stored
