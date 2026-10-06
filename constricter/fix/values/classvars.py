# SPDX-License-Identifier: MIT
"""`--fix` for a plain class's variables: `limit = 3` in a class body, typed by its literal value.

An annotation in a class body can be more than a type: a dataclass's, a `NamedTuple`'s or a model's
makes the variable a field. So only a plain class's body is fixed: one defined once in its module,
with no decorator or metaclass, every base of which is `object`, a `unittest` test case, a builtin
exception or value class (`ValueError`, `str`: see `BUILTIN_BASES`), a listed one (`listed`: a
framework's that reads no annotations, as `fix-plain-bases` says), or another plain class; and no
class that isn't plain may inherit from it (a mixin of a model's). What the module alone sees is
`plain`; with the CLI, the index of checked files says which bases other files define are plain too
(see `constricter.fix.index.project`).

A variable counts when it's bound once, by a plain `name = value` directly in the body, to a value
whose type its own text decides (a literal, or a display of them), and nothing in the module stores
the attribute any other way (`self.limit = ...`), nor is it one a builtin base has itself (`errno`
under `OSError`) or a class above it annotates as another type (`limit: int | None`): a type checker
holds a variable to what its base declares. Its type is that value's, whatever the module
declares: the same read from the file alone, so the files reading the attribute (`self.limit`,
`cls.limit`) are typed in the same run as the class is fixed. A guess (`member`): a subclass, or
code elsewhere, may bind it to another type.
"""

import ast
import builtins
from collections.abc import Callable, Mapping, Sequence
from typing import Final, TypeAlias, cast

from constricter.fix.core.imports import taken_names
from constricter.fix.core.known import Inference, Known, Outside
from constricter.fix.values.inference import inference
from constricter.rules.annotations import classes as annotated
from constricter.rules.annotations import dotted
from constricter.rules.syntax import import_bindings
from constricter.rules.walked import classes, of_type, once

OBJECT: Final = "object"
# The standard library's test cases: their subclasses' variables are only ever their own.
TEST_CASES: Final = frozenset(
    {
        "unittest.TestCase",
        "unittest.IsolatedAsyncioTestCase",
        "unittest.case.TestCase",
        "unittest.async_case.IsolatedAsyncioTestCase",
    },
)
# The builtin classes of values whose subclasses' variables are their own, as an exception's are.
_VALUES: Final = frozenset(
    {"bytearray", "bytes", "complex", "dict", "float", "frozenset", "int", "list", "set", "str", "tuple"},
)
Bases: TypeAlias = Mapping[str, tuple[str, ...]]  # each class's bases as written (see `bases`)
SPECIAL: Final = ""  # a base no class has: what makes a class one that can't be plain
# What decides a value's type from its own text: nothing the module declares.
_OWN_KINDS: Final = frozenset({"literal", "container", "arithmetic", "compare"})
_NOTHING: Final = Known({}, frozenset(), {}, {})
_NONE: Final = "None"
_NOT: Final = "!"  # an entry that leaves a base out (see `listed`)
_DEFINITIONS: Final = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)


def _builtin_bases() -> dict[str, frozenset[str]]:
    """Find the builtin classes a plain class may inherit from: the exceptions, and `_VALUES`.

    Returns:
      Each one's name, and the names of what it has itself.

    """
    return {
        name: frozenset(dir(cast("object", getattr(builtins, name))))
        for name in dir(builtins)
        if _is_base(name, cast("object", getattr(builtins, name)))
    }


def _is_base(name: str, value: object) -> bool:
    """Check whether a builtin is a class a plain class may inherit from.

    Returns:
      Whether it is.

    """
    return isinstance(value, type) and (name in _VALUES or issubclass(value, BaseException))


BUILTIN_BASES: Final = _builtin_bases()


def member_type(value: ast.expr) -> str | None:
    """Type a class variable's value by its own text: a literal, or a display of them.

    Returns:
      The annotation, or `None` for a value that names anything (a call, a copy), or `None` itself.

    """
    found: Inference | None = inference(value, _NOTHING, {})
    if found is None or found.annotation == _NONE or not found.kinds <= _OWN_KINDS:
        return None
    return found.annotation


@once
def bases(tree: ast.Module) -> dict[str, tuple[str, ...]]:
    """Map each class the module defines once to its bases, as written.

    Returns:
      Each one's bases (`object` left out, a subscripted one by its name); with `SPECIAL` among
      them for a class that can't be plain: decorated, given a metaclass or another keyword, or with
      a base that isn't a name (`Generic[T]`, `make()`) or is a builtin's the module binds itself.

    """
    taken: frozenset[str] = taken_names(tree)[0]
    counts: dict[str, int] = {}
    node: ast.ClassDef
    for node in classes(tree):
        counts[node.name] = counts.get(node.name, 0) + 1
    found: dict[str, tuple[str, ...]] = {}
    for node in classes(tree):
        if counts[node.name] == 1:
            names: list[str | None] = [dotted(base) for base in node.bases]
            shadowed: bool = any(name in BUILTIN_BASES and name in taken for name in names)
            special: bool = bool(node.keywords or node.decorator_list) or None in names or shadowed
            under: list[str | None] = [
                dotted(base.value) if isinstance(base, ast.Subscript) else dotted(base) for base in node.bases
            ]
            found[node.name] = (
                *([SPECIAL] if special else []),
                *(name for name in under if name and name != OBJECT),
            )
    return found


def imported(tree: ast.Module) -> dict[str, str]:
    """Map each top-level name the module's absolute imports bind to what it is (`models.Model`'s `models`).

    Returns:
      Each bound name's dotted origin, to resolve a base by (see `plain`).

    """
    return {name: origin for name, origin, _ in import_bindings(tree.body)}


def plain(tree: ast.Module, origins: Mapping[str, str], entries: Sequence[str] = ()) -> frozenset[str]:
    """Find the module's plain classes, as far as the module alone sees (see the module docstring).

    `origins`: what each name its imports bind refers to (see `imported`), to know a test case;
    `entries`: the listed bases (see `listed`).

    Returns:
      Their names.

    """
    return settled(bases(tree), lambda base: allowed(_resolved(base, origins), entries))


def allowed(base: str, entries: Sequence[str] = ()) -> bool:
    """Check whether a base no checked file defines is one a plain class may have.

    Returns:
      Whether it's a test case's (`TEST_CASES`), a builtin's (`BUILTIN_BASES`) or a listed one
      (`listed`), by its origin.

    """
    return base in TEST_CASES or base in BUILTIN_BASES or listed(base, entries)


def listed(base: str, entries: Sequence[str]) -> bool:
    """Check whether `entries` list a base, by its dotted origin (`django.db.models.Model`).

    An entry names a class, or a package for every class in it (`django`); one starting `!` leaves
    out what it names, whatever else lists it.

    Returns:
      Whether one lists it, and none leaves it out.

    """
    left_out: list[str] = [entry[1:] for entry in entries if entry.startswith(_NOT)]
    kept: list[str] = [entry for entry in entries if not entry.startswith(_NOT)]
    return _under(base, kept) and not _under(base, left_out)


def _under(base: str, paths: Sequence[str]) -> bool:
    return any(base == path or base.startswith(f"{path}.") for path in paths)


def ancestors(name: str, found: Bases) -> list[str]:
    """Name every class of `found` that `name` inherits from, however far.

    Returns:
      Them, sorted.

    """
    return sorted(_ancestors(name, found, frozenset({name})))


def reserved(name: str, found: Bases) -> frozenset[str]:
    """Name what the builtin classes `name` inherits from have themselves, as far as `found` sees.

    A variable hiding one would be declared another type than its base declares it.

    Returns:
      Those names.

    """
    owners: list[str] = [name, *ancestors(name, found)]
    return frozenset[str]().union(
        *(BUILTIN_BASES.get(base, frozenset[str]()) for owner in owners for base in found[owner]),
    )


def settled(found: Bases, outside: Callable[[str], bool]) -> frozenset[str]:
    """Settle which classes are plain, given each one's bases (see `bases`).

    `outside`: whether a base that isn't one of `found` is one a plain class may have.

    Returns:
      The names of those whose every base is plain, and that no class that isn't inherits from.

    """
    above: dict[str, set[str]] = {name: _ancestors(name, found, frozenset({name})) for name in found}
    rooted: set[str] = {name for name in found if all(base in found or outside(base) for base in found[name])}
    kept: set[str] = {name for name in rooted if above[name] <= rooted}
    # A class that isn't plain makes what it inherits from not plain either: a model's mixin.
    mixed: set[str] = {base for name in found.keys() - kept for base in above[name]}
    return frozenset(kept - mixed)


def _ancestors(name: str, found: Bases, seen: frozenset[str]) -> set[str]:
    """Name every class of `found` that `name` inherits from, however far.

    Returns:
      Them.

    """
    above: set[str] = {base for base in found[name] if base in found and base not in seen}
    base: str
    for base in sorted(above):
        above |= _ancestors(base, found, seen | above)
    return above


def _resolved(base: str, origins: Mapping[str, str]) -> str:
    """Resolve a base as written through the module's imports (`TestCase`, `unittest.TestCase`).

    Returns:
      Its dotted origin; itself, if its first name isn't one the module imports.

    """
    first: str
    rest: str
    first, _, rest = base.partition(".")
    origin: str = origins.get(first, first)
    return f"{origin}.{rest}" if rest else origin


def variables(
    tree: ast.Module,
    origins: Mapping[str, str],
    outside: Outside | None,
    entries: Sequence[str] = (),
) -> dict[str, Mapping[str, str]]:
    """Type the plain classes' variables a module reads: its own, and those it imports.

    Which of its own are plain is the index's to say (`Outside.plain`), or else the module's alone,
    with `entries` the listed bases (see `listed`).

    Returns:
      Each class's variables' types, as the module spells the class.

    """
    indexed: frozenset[str] | None = None if outside is None else outside.plain
    own: frozenset[str] = plain(tree, origins, entries) if indexed is None else indexed
    typed: dict[str, dict[str, str]] = members(tree) if own else {}
    return {
        **({} if outside is None else outside.members),
        **{name: each for name, each in typed.items() if name in own},
    }


@once
def members(tree: ast.Module) -> dict[str, dict[str, str]]:
    """Type the variables of each class the module defines once (see the module docstring).

    Of every such class, plain or not: which are plain is the caller's to say.

    Returns:
      Each class's variables' types, by name; a class with none is left out.

    """
    stored: frozenset[str] = frozenset(
        node.attr
        for node in cast("list[ast.Attribute]", of_type(tree, ast.Attribute))
        if not isinstance(node.ctx, ast.Load)
    )
    single: dict[str, tuple[str, ...]] = bases(tree)
    typed: dict[str, dict[str, str]] = {
        node.name: _typed(node.body, stored | reserved(node.name, single))
        for node in classes(tree)
        if node.name in single
    }
    if not any(typed.values()):
        return {}
    declared: Mapping[str, Mapping[str, str]] = annotated(tree)
    kept: dict[str, dict[str, str]] = {
        name: agreeing(each, [declared[above] for above in ancestors(name, single)])
        for name, each in typed.items()
    }
    return {name: each for name, each in kept.items() if each}


def agreeing(typed: Mapping[str, str], declared: Sequence[Mapping[str, str]]) -> dict[str, str]:
    """Keep a class's variables that no class above it annotates as another type.

    `declared`: each such class's annotated attributes.

    Returns:
      Those variables' types, by name.

    """
    return {
        name: annotation
        for name, annotation in typed.items()
        if all(above.get(name, annotation) == annotation for above in declared)
    }


def _typed(body: Sequence[ast.stmt], stored: frozenset[str]) -> dict[str, str]:
    """Type a class body's variables: each bound once there, to a value its text types.

    `stored`: the names left alone (stored some other way, or a builtin base's own).

    Returns:
      Their types, by name.

    """
    bound: dict[str, int] = {}
    stmt: ast.stmt
    name: str
    for stmt in body:
        for name in _bound(stmt):
            bound[name] = bound.get(name, 0) + 1
    found: dict[str, str] = {}
    value: ast.expr
    annotation: str | None
    for stmt in body:
        match stmt:
            case ast.Assign(targets=[ast.Name(id=name)], value=value) if (
                bound[name] == 1 and name not in stored and (annotation := member_type(value)) is not None
            ):
                found[name] = annotation
            case _:
                pass
    return found


def _bound(stmt: ast.stmt) -> list[str]:
    """Name what one statement of a class's body binds: a definition's name, or every name it stores.

    Returns:
      Them, each as many times as it's bound.

    """
    if isinstance(stmt, _DEFINITIONS):
        return [stmt.name]
    return [
        node.id
        for node in ast.walk(stmt)
        if isinstance(node, ast.Name) and not isinstance(node.ctx, ast.Load)
    ]
