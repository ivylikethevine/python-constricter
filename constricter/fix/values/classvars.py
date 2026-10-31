"""`--fix` for a plain class's variables: `limit = 3` in a class body, typed by its literal value.

An annotation in a class body can be more than a type: a dataclass's, a `NamedTuple`'s or a model's
makes the variable a field. So only a plain class's body is fixed: one defined once in its module,
with no decorator or metaclass, every base of which is `object`, a `unittest` test case, a builtin
exception or value class (`ValueError`, `str`: see `BUILTIN_BASES`), `Generic[T]` or `abc.ABC`
(`PASSED_OVER`), a listed one (`listed`: a framework's that reads no annotations, as
`fix-plain-bases` says), or another plain class, subscripted or not (`Box[int]`); and no class that
isn't plain may inherit from it (a mixin of a model's). What the module alone sees is
`plain`; with the CLI, the index of checked files says which bases other files define are plain too
(see `constricter.fix.index.project`).

A variable counts when it's bound once, by a plain `name = value` directly in the body, to a value
whose type its own text decides (a literal, or a display of them) or the standard library does, by
the module's imports (`re.compile("x")`, `os.sep`, `len(NAMES)`), and nothing in the module stores
the attribute as anything else (`self.limit = 5` and `self.limit += 1` keep an `int`;
`self.limit = size` may not), nor is it one a builtin base has itself (`errno` under `OSError`) or a
class above it annotates as another type (`limit: int | None`): a type checker holds a variable to
what its base declares. Its type is that value's, whatever the module
declares: the same read from the file alone, so the files reading the attribute (`self.limit`,
`cls.limit`) are typed in the same run as the class is fixed. But one a test case declares itself
(`maxDiff`, an `int | None`) is that type, under any base no checked file defines but a builtin
one, where its value is of it (see `HELD`). A guess (`member`): a subclass, or code elsewhere, may
bind it to another type.
"""

import ast
import builtins
import re
from collections import Counter
from collections.abc import Callable, Mapping, Sequence
from typing import Final, TypeAlias, cast
from weakref import WeakKeyDictionary

from constricter.fix.core.imports import plan, taken_names
from constricter.fix.core.known import Inference, Known, LibraryNames, Outside
from constricter.fix.libraries import stdlib
from constricter.fix.values.inference import inference
from constricter.fix.values.operated import operated
from constricter.fix.values.shapes import is_none
from constricter.fix.values.stored import class_names
from constricter.offences import MAX_LENGTH
from constricter.source.annotations import dotted
from constricter.source.declarations import classes as annotated
from constricter.source.flow import members as union
from constricter.source.inert import inert, judged, marks
from constricter.source.syntax import import_bindings
from constricter.source.walked import classes, of_type

OBJECT: Final = "object"
# The standard library's test cases: their subclasses' variables are only ever their own.
_TEST_CASES: Final = frozenset(
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
# The standard library's bases that read no annotation in a class body, and bind nothing there.
PASSED_OVER: Final = frozenset({"abc.ABC", "typing.Generic", "typing_extensions.Generic"})
# The functions a call to which, as a base, makes a class of the call's fields: its body is plain.
# `bases` spells such a base with `CALLED` after the function (`collections.namedtuple()`): the class
# under `NamedTuple` itself has fields in its body, and isn't plain.
FUNCTIONAL: Final = frozenset({"namedtuple", "NamedTuple", "TypedDict"})
CALLED: Final = "()"
_FUNCTIONAL_BASES: Final = frozenset(
    {
        f"collections.namedtuple{CALLED}",
        *(
            f"{module}.{name}{CALLED}"
            for module in ("typing", "typing_extensions")
            for name in ("NamedTuple", "TypedDict")
        ),
    },
)
Bases: TypeAlias = Mapping[str, tuple[str, ...]]  # each class's bases as written (see `bases`)
SPECIAL: Final = ""  # a base no class has: what makes a class one that can't be plain
# Each module's classes' bases and variables, for as long as its tree lives: read for the index,
# then for the check.
_Bases: TypeAlias = dict[str, tuple[str, ...]]
_Members: TypeAlias = dict[str, dict[str, str]]
_BASES: Final[WeakKeyDictionary[ast.Module, _Bases]] = WeakKeyDictionary()
_MEMBERS: Final[WeakKeyDictionary[ast.Module, _Members]] = WeakKeyDictionary()
# What decides a value's type from its own text, with what the module imports of the standard
# library: nothing the module declares.
_OWN_KINDS: Final = frozenset(
    {
        "literal",
        "container",
        "arithmetic",
        "compare",
        "stdlib",
        "builtin",
        "builder",
        "loop",
        "method",
        "conditional",
        "boolean",
        "comprehension",
        "open",
    },
)
_NONE: Final = "None"
_TOWER: Final = ("bool", "int", "float", "complex")  # each fits where any after it is declared
_NO_CLASSES: Final = frozenset[str]()
_TUPLE: Final = "tuple"
_NOT: Final = "!"  # an entry that leaves a base out (see `listed`)
_DEFINITIONS: Final = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
# One store of an attribute: its value, and (augmented) its operator.
_Store: TypeAlias = tuple[ast.operator | None, ast.expr]


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
# The bases `allowed` takes by name alone, and those `_may_test` knows aren't a test case's.
_ALLOWED: Final = frozenset({*_TEST_CASES, *BUILTIN_BASES, *PASSED_OVER, *_FUNCTIONAL_BASES})
_NOT_TESTS: Final = frozenset({*BUILTIN_BASES, *PASSED_OVER})
_WORD: Final = re.compile(r"[A-Za-z_][\w.]*")
# What a test case declares of itself, where builtins alone spell it: a subclass's variable of the
# name has that type, to a type checker, whatever its value's is. Not its private attributes, which
# the tables hold too (`_testMethodName`): no subclass sets one as its own variable.
HELD: Final = {
    name: typed
    for name, typed in stdlib.attributes("unittest.TestCase").items()
    if not name.startswith("_")
    and all(word == _NONE or hasattr(builtins, word) for word in cast("list[str]", _WORD.findall(typed)))
}


def _member_type(value: ast.expr, known: Known) -> str | None:
    """Type a class variable's value by its own text: a literal, or a display of them.

    Or, `known` naming the standard library as the module does (see `library`), by what it gives:
    a function's or a class's with a fixed type, an attribute, a builtin's.

    Returns:
      The annotation, or `None` for a value that names anything else (a class, a copy), or `None`
      itself.

    """
    found: Inference | None = inference(value, known, {})
    if found is None or found.annotation == _NONE or not found.kinds <= _OWN_KINDS:
        return None
    return found.annotation


def library(tree: ast.Module) -> Known:
    """Know what a module names of the standard library, and nothing it declares itself.

    Returns:
      What `_member_type` types a value by, the same for every file that reads the module.

    """
    return Known({}, frozenset(), {}, {}, names=LibraryNames(frozenset(), stdlib.origins(tree), plan(tree)))


def bases(tree: ast.Module) -> dict[str, tuple[str, ...]]:
    """Map each class the module defines once to its bases, as written.

    Returns:
      Each one's bases (`object` left out, a subscripted one by its name, a call to a functional
      `namedtuple`, `NamedTuple` or `TypedDict` by the function's: a class with those fields); with
      `SPECIAL` among them for a class that can't be plain: decorated, given a metaclass or another
      keyword, or with a base that isn't a name (`make()`) or is a builtin's the module binds itself.

    """
    found: dict[str, tuple[str, ...]] | None
    if (found := _BASES.get(tree)) is None:
        found = _BASES[tree] = _read_bases(tree)
    return found


def _read_bases(tree: ast.Module) -> dict[str, tuple[str, ...]]:
    taken: frozenset[str] = taken_names(tree)[0]
    counts: Mapping[str, int] = class_names(tree)
    found: dict[str, tuple[str, ...]] = {}
    node: ast.ClassDef
    for node in classes(tree):
        if counts[node.name] == 1:
            names: list[str | None] = [_base_name(base) for base in node.bases]
            shadowed: bool = any(name in BUILTIN_BASES and name in taken for name in names)
            special: bool = bool(node.keywords or node.decorator_list) or None in names or shadowed
            found[node.name] = (
                *([SPECIAL] if special else []),
                *(name for name in names if name and name != OBJECT),
            )
    return found


def _base_name(base: ast.expr) -> str | None:
    """Spell a base: a name, a subscripted one's, or a functional `namedtuple`-like call's function.

    Returns:
      It, or `None` for a base that's anything else (`make()`).

    """
    name: str | None
    value: ast.expr
    func: ast.expr
    match base:
        case ast.Subscript(value=value):
            return dotted(value)
        case ast.Call(func=func) if (name := dotted(func)) is not None and name.rpartition(".")[
            2
        ] in FUNCTIONAL:
            return f"{name}{CALLED}"
        case _:
            return dotted(base)


def imported(tree: ast.Module) -> dict[str, str]:
    """Map each top-level name the module's absolute imports bind to what it is (`models.Model`'s `models`).

    Returns:
      Each bound name's dotted origin, to resolve a base by (see `plain`).

    """
    return {name: origin for name, origin, _ in import_bindings(tree.body)}


def plain(
    tree: ast.Module,
    origins: Mapping[str, str],
    entries: Sequence[str] = (),
    *,
    marked_too: bool = True,
) -> frozenset[str]:
    """Find the module's plain classes, as far as the module alone sees (see the module docstring).

    `origins`: what each name its imports bind refers to (see `imported`), to know a test case;
    `entries`: the listed bases (see `listed`); `marked_too`: whether a class only inert decorators
    and a metaclass keep from it is plain (see `marked`).

    Returns:
      Their names.

    """
    found: dict[str, tuple[str, ...]] = bases(tree)
    local: frozenset[str] = inert(tree) if marked_too else frozenset()
    cleared: dict[str, tuple[str, ...]] = {
        name: tuple(base for base in found[name] if base != SPECIAL)
        for name, each in (marked(tree) if marked_too else {}).items()
        if all(judged(mark, local, origins) for mark in each)
    }
    return settled({**found, **cleared}, lambda base: allowed(_resolved(base, origins), entries))


def marked(tree: ast.Module) -> dict[str, tuple[str, ...]]:
    """Find the classes the module defines once that only their decorators and metaclass keep from plain.

    Returns:
      Each one's, as `inert.marks` spells them: a class with a base `bases` can't spell, or a
      builtin's the module binds itself, left out.

    """
    found: dict[str, tuple[str, ...]] = bases(tree)
    taken: frozenset[str] = taken_names(tree)[0]
    kept: dict[str, tuple[str, ...]] = {}
    node: ast.ClassDef
    for node in classes(tree):
        each: tuple[str, ...] | None
        if SPECIAL not in found.get(node.name, ()) or (each := marks(node)) is None or not each:
            continue
        names: list[str | None] = [_base_name(base) for base in node.bases]
        if None not in names and not any(name in BUILTIN_BASES and name in taken for name in names):
            kept[node.name] = each
    return kept


def allowed(base: str, entries: Sequence[str] = ()) -> bool:
    """Check whether a base no checked file defines is one a plain class may have.

    Returns:
      Whether it's a test case's (`_TEST_CASES`), a builtin's (`BUILTIN_BASES`), one passed over
      (`PASSED_OVER`) or a listed one (`listed`), by its origin.

    """
    return base in _ALLOWED or listed(base, entries)


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
    called: str = CALLED if base.endswith(CALLED) else ""
    first, _, rest = base.removesuffix(CALLED).partition(".")
    origin: str = origins.get(first, first)
    return f"{origin}.{rest}{called}" if rest else f"{origin}{called}"


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
    indexed: Mapping[str, Mapping[str, str]] = {} if outside is None else outside.members
    if outside is not None and outside.plain is not None:  # its own settled too (see `plain.settled`)
        return dict(indexed)
    own: frozenset[str] = own_plain(tree, origins, outside, entries)
    typed: dict[str, dict[str, str]] = members(tree) if own else {}
    bare: dict[str, frozenset[str]] = nulls(tree) if own else {}
    if typed or bare:
        reached: frozenset[str] = own - plain(tree, origins, entries, marked_too=False)
        single: dict[str, tuple[str, ...]] = bases(tree)
        kept: dict[str, dict[str, str]]
        nones: dict[str, frozenset[str]]
        kept, nones = unshadowed(
            {name: typed[name] for name in own if name in typed},
            {name: each for name, each in bare.items() if name in own},
            (defined(tree), single),
            reached,
        )
        typed = joined(kept, nones, single, annotated(tree), reached)
    return {**indexed, **{name: typed[name] for name in own if name in typed}}


def own_plain(
    tree: ast.Module,
    origins: Mapping[str, str],
    outside: Outside | None,
    entries: Sequence[str] = (),
) -> frozenset[str]:
    """Name the module's own plain classes: the index's to say (`Outside.plain`), or else the module's alone.

    Returns:
      Them.

    """
    indexed: frozenset[str] | None = None if outside is None else outside.plain
    return plain(tree, origins, entries) if indexed is None else indexed


def members(tree: ast.Module) -> dict[str, dict[str, str]]:
    """Type the variables of each class the module defines once (see the module docstring).

    Of every such class, plain or not: which are plain is the caller's to say.

    Returns:
      Each class's variables' types, by name; a class with none is left out.

    """
    found: dict[str, dict[str, str]] | None
    if (found := _MEMBERS.get(tree)) is None:
        found = _MEMBERS[tree] = _read_members(tree)
    return found


def _read_members(tree: ast.Module) -> dict[str, dict[str, str]]:
    single: dict[str, tuple[str, ...]]
    if not (single := bases(tree)):
        return {}
    # Only a plain `name = value` is typed (see `_typed`): a module whose classes have none needn't be read.
    if not any(
        isinstance(stmt, ast.Assign) and len(stmt.targets) == 1 and isinstance(stmt.targets[0], ast.Name)
        for node in classes(tree)
        if node.name in single
        for stmt in node.body
    ):
        return {}
    stored: dict[str, list[_Store | None]] = _stores(tree)
    origins: dict[str, str] = imported(tree)
    known: Known = library(tree)
    typed: dict[str, dict[str, str]] = {
        node.name: _typed(
            node.body,
            reserved(node.name, single),
            stored,
            (HELD if _may_test(node.name, single, origins) else {}, known),
        )
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


def nulls(tree: ast.Module) -> dict[str, frozenset[str]]:
    """Find the variables of each class the module defines once that are bound to `None` alone.

    Bound once, directly in the body, by a plain `name = None`; never stored in the module
    (`self.name = ...`), nor one a builtin base has. What `joined` adds `None` to a type by.

    Returns:
      Each class's such variables; a class with none left out.

    """
    single: dict[str, tuple[str, ...]]
    if not (single := bases(tree)):
        return {}
    stored: dict[str, list[_Store | None]] = _stores(tree)
    found: dict[str, frozenset[str]] = {}
    node: ast.ClassDef
    for node in (each for each in classes(tree) if each.name in single):
        counts: Counter[str] = Counter(name for stmt in node.body for name in _bound(stmt))
        left: frozenset[str] = reserved(node.name, single).union(stored)
        names: frozenset[str] = frozenset(
            stmt.targets[0].id
            for stmt in node.body
            if isinstance(stmt, ast.Assign)
            and len(stmt.targets) == 1
            and isinstance(stmt.targets[0], ast.Name)
            and is_none(stmt.value)
            and counts[stmt.targets[0].id] == 1
            and stmt.targets[0].id not in left
        )
        if names:
            found[node.name] = names
    return found


def joined(
    typed: Mapping[str, Mapping[str, str]],
    bare: Mapping[str, frozenset[str]],
    found: Bases,
    declared: Mapping[str, Mapping[str, str]],
    reached: frozenset[str] = _NO_CLASSES,
) -> dict[str, dict[str, str]]:
    """Type a variable alike in every class that binds it under another that does, as a checker holds them.

    A class variable's type is invariant: an override of `priority: int` can't be `priority: float`,
    nor one of `name: str | None` a `str`. So each class of `typed` (its variables' types) and `bare`
    (its variables bound to `None`, see `nulls`), with every class of them above or under it that
    binds the name too (by `found`, each class's bases), takes the one type their values fit: their
    type, if they agree; the widest, if they're numbers (`int`, then `float`); a tuple of any length,
    if they're tuples of one type (`tuple[str, ...]`); with `None`, if one binds it to that. One whose
    values fit no one type, or under a class `declared` annotates the name in, is left as it is, but
    in a class of `reached` (see `unshadowed`), untyped.

    Returns:
      `typed`, each such variable's type joined, those bound to `None` among them.

    """
    out: dict[str, dict[str, str]] = {name: dict(each) for name, each in typed.items()}
    binders: dict[str, list[str]] = {}
    owner: str
    variable: str
    for owner in sorted(typed.keys() | bare.keys()):
        for variable in {*typed.get(owner, {}), *bare.get(owner, ())} if owner in found else ():
            binders.setdefault(variable, []).append(owner)
    above: dict[str, list[str]] = {}
    joins: list[list[str]] = [ancestors(owner, found) for owner, each in found.items() if len(each) > 1]
    owners: list[str]
    for variable, owners in binders.items():
        if len(owners) == 1:
            continue
        for owner in owners:
            if owner not in above:
                above[owner] = ancestors(owner, found)
        group: list[str]
        for group in _groups(owners, above, joins):
            if len(group) > 1 and not any(
                variable in declared.get(base, {})
                for each in group
                for base in above[each]
                if base not in group
            ):
                _join(out, (variable, group), (typed, bare), reached)
    return out


def _join(
    out: dict[str, dict[str, str]],
    line: tuple[str, Sequence[str]],
    values: tuple[Mapping[str, Mapping[str, str]], Mapping[str, frozenset[str]]],
    reached: frozenset[str],
) -> None:
    """Type one variable alike in a group of classes binding it (see `joined`), in `out`.

    `line`: the variable, and the group; `values`: as `joined` takes `typed` and `bare`.
    """
    variable: str
    group: Sequence[str]
    variable, group = line
    atoms: set[str] = {values[0][each][variable] for each in group if variable in values[0].get(each, {})}
    one: str | None = _one(atoms, none=any(variable in values[1].get(each, ()) for each in group))
    each: str
    for each in group if one is not None else ():
        out.setdefault(each, {})[variable] = cast("str", one)
    for each in reached.intersection(group) if one is None else ():
        _ = out.get(each, {}).pop(variable, None)


def _groups(
    owners: Sequence[str],
    above: Mapping[str, Sequence[str]],
    joins: Sequence[Sequence[str]] = (),
) -> list[list[str]]:
    """Split the classes binding a name into those joined by one being above another.

    `above`: every class each one inherits from; `joins`: every class above each class of several
    bases, whose binding of the name a checker holds alike there.

    Returns:
      Each group, sorted.

    """
    group: dict[str, str] = {owner: owner for owner in owners}  # each class's group, by a class in it
    grouped: dict[str, list[str]] = {owner: [owner] for owner in owners}

    def merge(one: str, other: str) -> None:
        kept: str = group[one]
        gone: str = group[other]
        if kept != gone:
            moved: str
            for moved in grouped.pop(gone):
                group[moved] = kept
                grouped[kept].append(moved)

    owner: str
    for owner in owners:
        base: str
        for base in above[owner]:
            if base in group:
                merge(owner, base)
    lines: Sequence[str]
    for lines in joins:
        met: list[str] = [base for base in lines if base in group]
        for base in met[1:]:
            merge(met[0], base)
    return [sorted(each) for each in grouped.values()]


def promoted(annotation: str, held: frozenset[str]) -> bool:
    """Check whether a value's type fits a variable `joined` widened to another type.

    Returns:
      Whether `annotation` is one of the numeric tower's, under one of `held`'s; or a tuple, one of
      `held` the tuple of any length of its element type.

    """
    return (
        annotation in _TOWER
        and any(each in _TOWER and _TOWER.index(each) > _TOWER.index(annotation) for each in held)
    ) or any(each.endswith(", ...]") and _tupled({annotation, each}) == each for each in held)


def _tupled(atoms: set[str]) -> str | None:
    """Write the one tuple type tuples of types `atoms` fit: of any length, of their one element type.

    Returns:
      It (`tuple[str, ...]`), or `None` if one isn't a tuple, or their elements differ.

    """
    elements: set[str] = set()
    atom: str
    for atom in atoms:  # annotations `--fix` wrote: each parses
        node: ast.expr = ast.parse(atom, mode="eval").body
        if not (
            isinstance(node, ast.Subscript) and isinstance(node.value, ast.Name) and node.value.id == _TUPLE
        ):
            return None
        parts: list[ast.expr] = node.slice.elts if isinstance(node.slice, ast.Tuple) else [node.slice]
        if parts[1:] and isinstance(parts[-1], ast.Constant) and parts[-1].value is Ellipsis:
            parts = parts[:-1]
        elements.update(
            ast.unparse(part) for part in parts if not (isinstance(part, ast.Tuple) and not part.elts)
        )
    return f"tuple[{next(iter(elements))}, ...]" if len(elements) == 1 else None


def defined(tree: ast.Module) -> dict[str, frozenset[str]]:
    """Name the methods, properties and nested classes the body of each class the module defines once defines.

    Returns:
      Them, by class; a class with none left out.

    """
    single: dict[str, tuple[str, ...]] = bases(tree)
    found: dict[str, frozenset[str]] = {
        node.name: frozenset(stmt.name for stmt in node.body if isinstance(stmt, _DEFINITIONS))
        for node in classes(tree)
        if node.name in single
    }
    return {name: each for name, each in found.items() if each}


def unshadowed(
    typed: Mapping[str, Mapping[str, str]],
    bare: Mapping[str, frozenset[str]],
    seen: tuple[Mapping[str, frozenset[str]], Bases],
    reached: frozenset[str],
) -> tuple[dict[str, dict[str, str]], dict[str, frozenset[str]]]:
    """Leave out a newly typed class variable that a class above or under it defines.

    A method, a property or a nested class of the name, which an annotation of the variable would make
    an incompatible override. A variable of a class of `reached` (plain only by its decorators' and
    metaclass's being inert, see `marked`), or one bound to `None` (`bare`, which only `joined`
    types) in any class. `typed` and `bare`: as `joined` takes them; `seen`: what each class's body
    defines (see `defined`), and each class's bases.

    Returns:
      `typed` and `bare`, without them.

    """
    bound: Mapping[str, frozenset[str]]
    found: Bases
    bound, found = seen
    kept: dict[str, dict[str, str]] = {name: dict(each) for name, each in typed.items()}
    nones: dict[str, frozenset[str]] = dict(bare)
    if not reached and not bare:
        return kept, nones
    under: dict[str, set[str]] = {name: set() for name in found}
    name: str
    for name in found:
        base: str
        for base in ancestors(name, found):
            under[base].add(name)
    dropped: dict[str, set[str]] = {}
    for name in sorted(reached.intersection(typed).union(bare)):
        line: list[str] = [*ancestors(name, found), *under.get(name, ())]
        other: set[str]
        if other := {variable for each in line for variable in bound.get(each, frozenset())}:
            dropped[name] = other
    for name in sorted(dropped):
        if name in reached:
            kept[name] = {
                variable: annotation
                for variable, annotation in kept.get(name, {}).items()
                if variable not in dropped[name]
            }
        if name in nones:
            nones[name] -= dropped[name]
    return kept, nones


def _one(atoms: set[str], *, none: bool) -> str | None:
    """Write the one type values of types `atoms` fit, with `None` if `none`.

    Returns:
      It, or `None` where there's none: no type, or types that aren't one or the numeric tower's.

    """
    one: str
    each: str | None
    if len(atoms) == 1:
        one = next(iter(atoms))
    elif atoms and atoms <= set(_TOWER):
        one = max(atoms, key=_TOWER.index)
    elif (each := _tupled(atoms)) is not None:
        one = each
    else:
        return None
    return one if not none or _NONE in (union(one) or ()) else f"{one} | None"


def named(tree: ast.Module) -> dict[str, dict[str, str]]:
    """Find the variables of each class the module defines once that are bound to a bare name.

    `form_class = PasswordChangeForm`: a `type[PasswordChangeForm]`, where the index finds a checked
    file's class by that name and no class above or under this one binds the variable
    (`plain.settled`). Bound once, directly in the body, and not one the module stores
    (`self.form_class = ...`), a builtin base has, or its value's own text types already.

    Returns:
      Each class's such variables, with the name each is bound to; a class with none left out.

    """
    single: dict[str, tuple[str, ...]]
    if not (single := bases(tree)):
        return {}
    stored: dict[str, list[_Store | None]] = _stores(tree)
    typed: dict[str, dict[str, str]] = members(tree)
    found: dict[str, dict[str, str]] = {}
    node: ast.ClassDef
    for node in (each for each in classes(tree) if each.name in single):
        counts: Counter[str] = Counter(name for stmt in node.body for name in _bound(stmt))
        kept: frozenset[str] = reserved(node.name, single).union(typed.get(node.name, {}), stored)
        bound: dict[str, str] = {}
        stmt: ast.stmt
        for stmt in node.body:
            variable: str
            value: str
            match stmt:
                case ast.Assign(targets=[ast.Name(id=variable)], value=ast.Name(id=value)) if (
                    counts[variable] == 1 and variable not in kept
                ):
                    bound[variable] = value
                case _:
                    pass
        if bound:
            found[node.name] = bound
    return found


def _may_test(name: str, found: Bases, origins: Mapping[str, str]) -> bool:
    """Check whether a class may be a test case: it has a base no class of the module, nor a builtin, is.

    A test case's own, or a framework's (which this file can't see the bases of).

    Returns:
      Whether it may.

    """
    return any(
        base not in found and _resolved(base, origins) not in _NOT_TESTS
        for owner in (name, *ancestors(name, found))
        for base in found[owner]
    )


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


def _stores(tree: ast.Module) -> dict[str, list[_Store | None]]:
    """Find how the module stores each attribute, whatever it's an attribute of.

    Returns:
      Each stored attribute's name, with its every store: an assignment's value (`self.x = 1`), with
      an augmented one's operator (`self.x += 1`), or `None` for any other (an unpacking, a loop's
      target, a `del`, an annotated one).

    """
    # Only an attribute's own store is looked up: an unpacking's targets are in a tuple.
    assigned: dict[ast.expr, _Store] = {
        target: (None, stmt.value)
        for stmt in cast("list[ast.Assign]", of_type(tree, ast.Assign))
        for target in stmt.targets
        if isinstance(target, ast.Attribute)
    }
    stmt: ast.AugAssign
    for stmt in cast("list[ast.AugAssign]", of_type(tree, ast.AugAssign)):
        assigned[stmt.target] = (stmt.op, stmt.value)
    found: dict[str, list[_Store | None]] = {}
    node: ast.Attribute
    for node in cast("list[ast.Attribute]", of_type(tree, ast.Attribute)):
        if not isinstance(node.ctx, ast.Load):
            found.setdefault(node.attr, []).append(assigned.get(node))
    return found


def _keeps(store: _Store | None, annotation: str, known: Known) -> bool:
    """Check whether a store of an attribute keeps it the type `annotation`.

    Returns:
      Whether its value's own text types it so (see `_member_type`), or (augmented) the operator
      gives that type back.

    """
    if store is None:
        return False
    own: str | None = _of(store[1], annotation, known)
    if store[0] is None:
        return own == annotation
    given: ast.BinOp = ast.BinOp(store[1], store[0], store[1])
    return own is not None and operated(given, annotation, own, MAX_LENGTH) == annotation


def _typed(
    body: Sequence[ast.stmt],
    kept: frozenset[str],
    stored: Mapping[str, Sequence[_Store | None]],
    typing: tuple[Mapping[str, str], Known],
) -> dict[str, str]:
    """Type a class body's variables: each bound once there, to a value its text types.

    `kept`: the names left alone (a builtin base's own); `stored`: how the module stores each
    attribute (see `_stores`), which leaves one alone unless every store keeps its type; `typing`:
    the types a base declares some names (see `HELD`), each its variable's where the value is of
    it, and what the module names of the standard library (see `library`).

    Returns:
      Their types, by name.

    """
    bound: Counter[str] = Counter(name for stmt in body for name in _bound(stmt))
    found: dict[str, str] = {}
    stmt: ast.stmt
    name: str
    value: ast.expr
    annotation: str | None
    for stmt in body:
        match stmt:
            case ast.Assign(targets=[ast.Name(id=name)], value=value) if (
                bound[name] == 1
                and name not in kept
                and (annotation := _of(value, typing[0].get(name), typing[1])) is not None
                and all(_keeps(store, annotation, typing[1]) for store in stored.get(name, ()))
            ):
                found[name] = annotation
            case _:
                pass
    return found


def _of(value: ast.expr, held: str | None, known: Known) -> str | None:
    """Type a variable by its `value`, under a base that declares it `held` (`None`: none does).

    Returns:
      `held`, where its value is of it, `None` too (`maxDiff = None`); its value's own type (see
      `_member_type`) where no base declares it; else `None`.

    """
    own: str | None = _NONE if is_none(value) and held is not None else _member_type(value, known)
    if own is None or held is None:
        return own
    return held if own in (union(held) or ()) else None


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
