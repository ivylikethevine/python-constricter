"""A checked file's classes' methods defined with `@overload`, or returning a `type[T]`'s class, for calls.

On a receiver typed as the class, as the calling file spells it: read and written as its functions'
overloads are (see `constricter.fix.index.own_overloads`), each under `Class.method`.
"""

from collections.abc import Iterator
from pathlib import Path
from typing import TYPE_CHECKING, Final

from constricter.fix.core.known import Guarded
from constricter.fix.core.signatures import ReadSignature
from constricter.fix.index import crossed, own_overloads, plain, project
from constricter.fix.index.modules import Index, Module, module_at
from constricter.fix.index.stubs import stubbed
from constricter.fix.libraries import stdlib
from constricter.fix.values import classvars
from constricter.source.annotations import roots

if TYPE_CHECKING:
    from constricter.fix.index.stubs.declared import Signature

_SELF: Final = "Self"


def overloaded(
    catalog: Index,
    path: Path,
    guarded: dict[str, Guarded],
) -> dict[str, tuple[ReadSignature, ...]]:
    """Find the overloaded methods the file at `path` calls, of the checked files' classes it names.

    `guarded` records the names their returns need imported for type checking.

    Returns:
      Each one's signatures, by the class as the file writes it and the method (`Frame.get`); none
      for a file `catalog` doesn't have.

    """
    target: Module | None
    if (target := module_at(catalog, path)) is None:
        return {}
    found: dict[str, tuple[ReadSignature, ...]] = {}
    key: str
    defined: tuple[Module, str]
    named: dict[str, tuple[Module, str]] = {
        **dict(crossed.spelled_classes(catalog, target, (target.names, target.attributes), set())),
        **{name: (target, name) for name in target.bases},  # its own
    }
    for key, defined in named.items():
        name: str
        owner: tuple[Module, str]
        for name, owner in _called(catalog, defined, target.method_calls):
            entry: str = f"{owner[1]}.{name}"
            written: tuple[Signature, ...] = owner[0].overloads.get(entry, ())
            # One returning `Self` is its receiver's class: not the type the signature writes; one
            # declaring its `self` is for some receivers alone.
            if not written or any(
                each.self_type is not None or _SELF in roots(each.returns or _SELF) for each in written
            ):
                continue
            found[f"{key}.{name}"] = own_overloads.spelled(
                catalog,
                target,
                (owner[0], entry),
                stubbed.read_signatures(catalog.modules, owner[0], entry),
                guarded,
            )
    return {entry: read for entry, read in found.items() if read}


def _called(
    catalog: Index,
    defined: tuple[Module, str],
    calls: frozenset[str],
) -> Iterator[tuple[str, tuple[Module, str]]]:
    """Find the methods `calls` names that a class or a checked file's base of it overloads.

    A base's stands where no class before it in the line binds the name; the line ends at a base it
    can't follow, which might.

    Yields:
      Each method's name, with the module and class defining it.

    """
    hidden: set[str] = set()
    each: tuple[Module, str] | None
    for each in _line(catalog, defined, project.DEPTH):
        if each is None:
            return
        name: str
        # Those it calls of the class's overloaded ones: few, of the thousands of classes it can name.
        for name in sorted((_methods(catalog, each[0]).get(each[1], frozenset()) & calls) - hidden):
            yield name, each
        hidden |= each[0].bound.get(each[1], frozenset())


def _line(catalog: Index, defined: tuple[Module, str], depth: int) -> Iterator[tuple[Module, str] | None]:
    """Follow a checked file's class up its bases, past its keywords and decorators (`can_focus=True`).

    Yields:
      It, then its bases in turn; `None` for one that isn't a checked file's or the standard library's.

    """
    yield defined
    base: str
    for base in defined[0].bases.get(defined[1], ()):
        path: str = "" if base == classvars.SPECIAL else plain.resolved(catalog.modules, defined[0], base)
        module: Module | None = catalog.modules.get(path.rpartition(".")[0])
        name: str = path.rpartition(".")[2]
        if module is not None and not module.installed and name in module.bases and depth:
            yield from _line(catalog, (module, name), depth - 1)
        elif path and stdlib.held_whole(path) is None:
            yield None


def _methods(catalog: Index, module: Module) -> dict[str, frozenset[str]]:
    """Group the methods a checked module's classes define with `@overload` by class, once for the index.

    Returns:
      Each class's, by its name (`Frame`, of `Frame.get`); none for an installed module.

    """
    key: tuple[str, str] = (module.name, module.folder)
    found: dict[str, frozenset[str]] | None
    if (found := None if catalog.memo is None else catalog.memo.overloaded.get(key)) is None:
        grouped: dict[str, set[str]] = {}
        entry: str
        for entry in () if module.installed else module.overloads:
            owner: str
            method: str
            owner, _, method = entry.rpartition(".")
            if owner:
                grouped.setdefault(owner, set()).add(method)
        found = {owner: frozenset(methods) for owner, methods in grouped.items()}
        if catalog.memo is not None:
            catalog.memo.overloaded[key] = found
    return found
