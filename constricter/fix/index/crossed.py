"""What crosses into a file from the other checked files it imports, for `--fix`.

`imported` gives a file the return types of the functions it imports (see `project.calls`), and
each imported class's attributes and methods' returns, its plain classes' variables, which are
generic and which are descriptors, each keyed as the file spells the class (`spelled_classes`):
only where every name in a type means the same in the file as where it was written (see
`project.portable`).
"""

from collections.abc import Iterator, Mapping
from pathlib import Path
from typing import Final, NamedTuple, TypeAlias

from constricter.fix.core.known import Classes, Guarded, Origin, Partial, Returns
from constricter.fix.index.modules import (
    SUFFIX,
    Index,
    Memo,
    Module,
    classes_under,
    exported,
    module_name,
)
from constricter.fix.index.project import (
    BUILTINS,
    CLASS,
    HOPS,
    NO_TYPE,
    PARTIAL,
    Imported,
    calls,
    definition,
    generic_portable,
    is_generic,
    portable,
    resolved,
    returned,
    typed_calls,
)
from constricter.rules.annotations import roots
from constricter.rules.declarations import GenericClass

_Named: TypeAlias = tuple[Mapping[str, Origin], frozenset[str] | None]  # see `spelled_classes`
_GET: Final = "__get__"


def imported(
    catalog: Index,
    path: Path,
    seeded: tuple[Mapping[str, Guarded], frozenset[str]] | None = None,
) -> Imported:
    """Return, for the file at `path`, what it imports from other checked files that it can name.

    Each function's return type (`calls`), and each class's attributes and methods' returns, keyed as
    the file spells the class (`Row`, `m.Row`); a type naming the class itself (a `Self` return) is
    spelled that way too. `seeded`: the names its fixtures' types are written with, imported for type
    checking alone (see `fixtures.visible`), whose classes' members it takes as well; and the
    attributes those types take of a module it imports (`MonkeyPatch`, in `pytest.MonkeyPatch`).

    Returns:
      Them, and the names their types need imported for type checking alone (see `Guarded`); nothing
      for a file `catalog` doesn't have (a notebook, standard input).

    """
    taken: _Taken = _Taken({}, {}, {}, {}, set(), {}, {})
    guarded: dict[str, Guarded] = {} if seeded is None else dict(seeded[0])
    target: Module | None
    if path.suffix != SUFFIX or (target := catalog.modules.get(module_name(path))) is None:
        return Imported({}, Classes(taken.attributes, taken.methods))
    # Its own attributes as they are where the fixtures' add none: the index keeps what they find.
    attributes: frozenset[str] = (
        target.attributes
        if seeded is None or seeded[1] <= target.attributes
        else target.attributes | seeded[1]
    )
    checking: dict[str, Origin] = {
        name: found.origin for name, found in guarded.items() if name not in target.names
    }
    named: _Named = ({**checking, **target.names}, attributes)
    _take(catalog, target, (checking, attributes), taken, guarded)
    _take(catalog, target, (target.names, attributes), taken, guarded)
    found: tuple[dict[str, str], Returns, dict[str, str]] = (
        calls(catalog, path, guarded),
        returned(catalog, path, guarded),
        {name: each for name, each, _ in typed_calls(catalog, path, PARTIAL, guarded)},
    )
    known: set[str] = set(named[0])
    for _ in range(HOPS):  # a class those types need imported is a receiver's too, needing more in turn
        fresh: dict[str, Origin] = {name: each.origin for name, each in guarded.items() if name not in known}
        # Any class their packages re-export: the types naming them aren't written in the file yet.
        _take(catalog, target, (fresh, None), taken, guarded)
        known.update(fresh)
    return Imported(
        found[0],
        Classes(taken.attributes, taken.methods),
        found[1],
        guarded,
        frozenset(taken.generics),
        taken.members,
        Partial(found[2], {name: each for name, each in taken.partial.items() if each}),
        taken.generic,
        taken.descriptors,
    )


def guarded_classes(catalog: Index, path: Path, found: Imported, guarded: Mapping[str, Guarded]) -> Classes:
    """Add the members of the classes `guarded` names that `found` hasn't taken, as the file names them.

    Those of the imports later steps add for type checking (an overloaded method's return):
    `df = pd.DataFrame(...).set_index("C")`, typed `DataFrame` by its import: `df.explode()` is one of
    that class's methods in the same pass, not only once the import is written.

    Returns:
      `found`'s classes, with theirs.

    """
    target: Module | None
    if path.suffix != SUFFIX or (target := catalog.modules.get(module_name(path))) is None:
        return found.classes
    fresh: dict[str, Origin] = {
        name: each.origin
        for name, each in guarded.items()
        if name not in found.guarded and name not in target.names and name not in found.classes.methods
    }
    if not fresh:
        return found.classes
    taken: _Taken = _Taken(
        {key: dict(each) for key, each in found.classes.attributes.items()},
        {key: dict(each) for key, each in found.classes.methods.items()},
        {},
        {},
        set(),
        {},
        {},
    )
    _take(catalog, target, (fresh, None), taken, dict(guarded))
    return Classes(taken.attributes, taken.methods)


class _Taken(NamedTuple):
    """What `imported` takes of the classes a file names, each keyed as the file spells the class."""

    attributes: dict[str, dict[str, str]]
    methods: dict[str, dict[str, str]]
    partial: dict[str, dict[str, str]]
    members: dict[str, Mapping[str, str]]
    generics: set[str]
    generic: dict[str, GenericClass]
    descriptors: dict[str, str | None]


def _take(catalog: Index, target: Module, named: _Named, taken: _Taken, guarded: dict[str, Guarded]) -> None:
    """Add to `taken` the members `target` uses of the classes `named` finds (see `spelled_classes`)."""
    key: str
    defined: tuple[Module, str]
    for key, defined in spelled_classes(catalog, target, named, taken.generics):
        if defined[1] in defined[0].generics:
            taken.generics.add(key)
        if defined[1] in defined[0].generic_members:
            klass: GenericClass = defined[0].generic_members[defined[1]]
            taken.generic[key] = generic_portable(catalog.modules, (target, defined), key, klass, guarded)
        if defined[1] in defined[0].plain and defined[1] in defined[0].members:
            taken.members[key] = _variables(catalog.modules, (target, defined), key, guarded)
        if defined[1] in defined[0].descriptors:
            gives: str | None = defined[0].descriptors[defined[1]]
            # What the file can't write is unread, as an overloaded `__get__` is.
            taken.descriptors[key] = (
                None
                if gives is None
                else portable(catalog.modules, (target, defined), key, {_GET: gives}, guarded).get(_GET)
            )
        if _declared_members(catalog, defined).isdisjoint(target.attributes):
            # Most classes it can name: it takes none of their members, and asks whether it names one
            # only by what it writes (`m.Row(...)` constructs one).
            if _written(key, target.attributes):
                taken.attributes[key], taken.methods[key], taken.partial[key] = {}, {}, {}
            continue
        taken.attributes[key], taken.methods[key], taken.partial[key] = (
            _used(catalog.modules, (target, defined), key, table.get(defined[1]), guarded)
            for table in (defined[0].classes, defined[0].methods, defined[0].partial_methods)
        )


def _written(spelled: str, attributes: frozenset[str]) -> bool:
    """Check whether a file can write a class as `spelled`: each part after its first an attribute it takes.

    Returns:
      Whether it can.

    """
    return all(part in attributes for part in spelled.split(".")[1:])


def _variables(
    modules: Mapping[str, Module],
    where: tuple[Module, tuple[Module, str]],
    key: str,
    guarded: dict[str, Guarded],
) -> dict[str, str]:
    """Write a plain class's variables' types as the file (`where[0]`) can (see `portable`).

    Returns:
      Each one's type: its own, made of builtins alone; one naming anything else, as the file
      spells it, or `NO_TYPE` where it can't, which still holds a class under it to no other.

    """
    typed: Mapping[str, str] = where[1][0].members[where[1][1]]
    named: dict[str, str] = {name: text for name, text in typed.items() if not roots(text) <= BUILTINS}
    written: dict[str, str] = portable(modules, where, key, named, guarded) if named else {}
    return {name: written.get(name, NO_TYPE) if name in named else text for name, text in typed.items()}


def _declared_members(catalog: Index, defined: tuple[Module, str]) -> frozenset[str]:
    """Name the members a class declares a type for, once for the index.

    Returns:
      Its attributes' and methods' names.

    """
    module: Module
    name: str
    module, name = defined
    memo: Memo | None = catalog.memo
    found: frozenset[str] | None
    if (found := None if memo is None else memo.members.get((module.name, name))) is None:
        found = frozenset[str]().union(
            *(table.get(name, ()) for table in (module.classes, module.methods, module.partial_methods)),
        )
        if memo is not None:
            memo.members[module.name, name] = found
    return found


def _used(
    modules: Mapping[str, Module],
    where: tuple[Module, tuple[Module, str]],
    key: str,
    members: Mapping[str, str] | None,
    guarded: dict[str, Guarded],
) -> dict[str, str]:
    """Keep the types of a class's `members` that the file (`where[0]`) takes of something, and can write.

    Returns:
      Each kept member's type (see `portable`): none for most classes it can name, whose members it
      doesn't use.

    """
    used: frozenset[str] = where[0].attributes
    taken: dict[str, str] = {name: typed for name, typed in (members or {}).items() if name in used}
    return portable(modules, where, key, taken, guarded) if taken else {}


def spelled_classes(
    catalog: Index,
    target: Module,
    named: _Named,
    generics: set[str],
) -> Iterator[tuple[str, tuple[Module, str]]]:
    """Find the classes other checked files define that `target` names, each as it spells it.

    `named`: the names it's to find them by, and the attributes it takes of anything (`None`: any).
    `Row` after `from m import Row`; `m.Row`, or `pkg.m.Row` after `import pkg.m`, for a module's,
    and `pkg.Row` for one `pkg` re-exports, where `Row` is such an attribute.
    The generic classes a module it imports re-exports are added to `generics`, as it spells them.

    Yields:
      Each spelling, and the module defining the class and its name there.

    """
    memo: Memo | None = catalog.memo
    if memo is None or named[0] is not target.names or named[1] is not target.attributes:
        yield from _spelled_classes(catalog, target, named, generics)
        return
    kept: tuple[str, str]  # with its folder: several `conftest.py`s share the one name
    if (kept := (target.name, target.folder)) not in memo.spelled:
        added: set[str] = set()
        memo.spelled[kept] = (
            [
                (key, defined[0].name, defined[1])
                for key, defined in _spelled_classes(catalog, target, named, added)
            ],
            sorted(added),
        )
    generics.update(memo.spelled[kept][1])
    key: str
    module: str
    name: str
    for key, module, name in memo.spelled[kept][0]:
        yield key, (catalog.modules[module], name)


def _spelled_classes(
    catalog: Index,
    target: Module,
    named: _Named,
    generics: set[str],
) -> Iterator[tuple[str, tuple[Module, str]]]:
    """Find the classes `spelled_classes` yields, from the index itself.

    Yields:
      Each spelling, and the module defining the class and its name there.

    """
    local: str
    origin: Origin
    for local, origin in resolved(catalog, named[0]):
        spelled: list[tuple[str, Origin]] = []
        if origin[1] is not None and origin[0] != target.name:
            spelled = [(local, origin)]
            generics.update([local] * is_generic(catalog.modules, origin))
        elif origin[1] is None:
            package: Module | None = catalog.modules.get(origin[0])
            spelled = [
                *classes_under(catalog, local, origin[0], CLASS),
                *(
                    (f"{local}.{name}", where)
                    for name, where in (() if package is None else exported(package).items())
                    if (named[1] is None or name in named[1])
                    and where[1] is not None
                    and where[0] != origin[0]
                ),
            ]
            generics.update(_reexported_generics(catalog.modules, local, origin[0]))
        key: str
        where: Origin
        for key, where in spelled:
            defined: tuple[Module, str] | None
            if (defined := definition(catalog.modules, where, CLASS)) is not None:
                yield key, defined


def _reexported_generics(modules: Mapping[str, Module], local: str, name: str) -> Iterator[str]:
    """Spell the generic classes module `name` re-exports (`from ._c import OrderedSet`) as `local.C`.

    Only its own names, not its submodules': a package's `__init__` is where they're re-exported,
    for type checking alone too, where it imports them only when they're asked for (pydantic's).

    Yields:
      Each spelling.

    """
    module: Module | None = modules.get(name)
    reexported: str
    origin: Origin
    for reexported, origin in ({} if module is None else {**module.guarded, **module.names}).items():
        if origin[1] is not None and origin[0] != name and is_generic(modules, origin):
            yield f"{local}.{reexported}"
