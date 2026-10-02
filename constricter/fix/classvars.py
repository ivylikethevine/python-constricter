# SPDX-License-Identifier: MIT
"""`--fix` for a plain class's variables: `limit = 3` in a class body, typed by its literal value.

An annotation in a class body can be more than a type: a dataclass's, a `NamedTuple`'s or a model's
makes the variable a field. So only a plain class's body is fixed: one defined once in its module,
with no decorator or metaclass, every base of which is `object`, a `unittest` test case, or another
plain class; and no class that isn't plain may inherit from it (a mixin of a model's). What the
module alone sees is `plain`; with the CLI, the index of checked files says which bases other files
define are plain too (see `constricter.fix.project`).

A variable counts when it's bound once, by a plain `name = value` directly in the body, to a value
whose type its own text decides (a literal, or a display of them), and nothing in the module stores
the attribute any other way (`self.limit = ...`). Its type is that value's, whatever the module
declares: the same read from the file alone, so the files reading the attribute (`self.limit`,
`cls.limit`) are typed in the same run as the class is fixed. A guess (`member`): a subclass, or
code elsewhere, may bind it to another type.
"""

import ast
from collections.abc import Callable, Mapping, Sequence
from typing import Final, TypeAlias, cast

from constricter.fix.inference import inference
from constricter.fix.known import Inference, Known, Outside
from constricter.rules.annotations import dotted
from constricter.rules.walked import classes, of_type

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
Bases: TypeAlias = Mapping[str, tuple[str, ...]]  # each class's bases as written (see `bases`)
SPECIAL: Final = ""  # a base no class has: what makes a class one that can't be plain
# What decides a value's type from its own text: nothing the module declares.
_OWN_KINDS: Final = frozenset({"literal", "container", "arithmetic", "compare"})
_NOTHING: Final = Known({}, frozenset(), {}, {})
_NONE: Final = "None"
_DEFINITIONS: Final = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)


def member_type(value: ast.expr) -> str | None:
    """Type a class variable's value by its own text: a literal, or a display of them.

    Returns:
      The annotation, or `None` for a value that names anything (a call, a copy), or `None` itself.

    """
    found: Inference | None = inference(value, _NOTHING, {})
    if found is None or found.annotation == _NONE or not found.kinds <= _OWN_KINDS:
        return None
    return found.annotation


def bases(tree: ast.Module) -> dict[str, tuple[str, ...]]:
    """Map each class the module defines once to its bases, as written.

    Returns:
      Each one's bases (`object` left out, a subscripted one by its name); with `SPECIAL` among
      them for a class that can't be plain: decorated, given a metaclass or another keyword, or with
      a base that isn't a name (`Generic[T]`, `make()`).

    """
    counts: dict[str, int] = {}
    node: ast.ClassDef
    for node in classes(tree):
        counts[node.name] = counts.get(node.name, 0) + 1
    found: dict[str, tuple[str, ...]] = {}
    for node in classes(tree):
        if counts[node.name] == 1:
            names: list[str | None] = [dotted(base) for base in node.bases]
            special: bool = bool(node.keywords or node.decorator_list) or None in names
            under: list[str | None] = [
                dotted(base.value) if isinstance(base, ast.Subscript) else dotted(base) for base in node.bases
            ]
            found[node.name] = (
                *([SPECIAL] if special else []),
                *(name for name in under if name and name != OBJECT),
            )
    return found


def plain(tree: ast.Module, origins: Mapping[str, str]) -> frozenset[str]:
    """Find the module's plain classes, as far as the module alone sees (see the module docstring).

    `origins`: what each name its imports bind refers to (`stdlib.origins`), to know a test case.

    Returns:
      Their names.

    """
    return settled(bases(tree), lambda base: _resolved(base, origins) in TEST_CASES)


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
) -> dict[str, Mapping[str, str]]:
    """Type the plain classes' variables a module reads: its own, and those it imports.

    Which of its own are plain is the index's to say (`Outside.plain`), or else the module's alone.

    Returns:
      Each class's variables' types, as the module spells the class.

    """
    indexed: frozenset[str] | None = None if outside is None else outside.plain
    own: frozenset[str] = plain(tree, origins) if indexed is None else indexed
    typed: dict[str, dict[str, str]] = members(tree) if own else {}
    return {
        **({} if outside is None else outside.members),
        **{name: each for name, each in typed.items() if name in own},
    }


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
    once: dict[str, tuple[str, ...]] = bases(tree)
    typed: dict[str, dict[str, str]] = {
        node.name: _typed(node.body, stored) for node in classes(tree) if node.name in once
    }
    return {name: each for name, each in typed.items() if each}


def _typed(body: Sequence[ast.stmt], stored: frozenset[str]) -> dict[str, str]:
    """Type a class body's variables: each bound once there, to a value its text types.

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
