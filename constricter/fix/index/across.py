"""What a checked file knows from the other checked files: `outside`, read from the index.

Each file is checked knowing what the files it imports declare and return, the hints a type
checker gave it, and what the index's other readers say of the names it imports (see `Outside`).
"""

from collections.abc import Mapping
from pathlib import Path
from typing import TYPE_CHECKING

from constricter.fix.core.known import Guarded, Hints, Origin, Outside, Passed
from constricter.fix.index import (
    awaits,
    beyond,
    callers,
    consistent,
    crossed,
    decorated,
    fixtures,
    linked,
    loose,
    managed,
    offers,
    own_methods,
    own_types,
    plain,
    project,
    sides,
    taken,
    tuples,
)
from constricter.fix.index.modules import module_at
from constricter.fix.index.spelling import canonical_origin
from constricter.fix.index.stubs import stubbed
from constricter.fix.values.aliased import FACTORIES

if TYPE_CHECKING:
    from constricter.fix.core.signatures import ReadSignature


def outside(modules: project.Index, path: Path, hinted: Mapping[Path, tuple[Hints, ...]]) -> Outside:
    """Find what's known of a file from outside it: what it imports from the others, and its hints.

    Returns:
      It.

    """
    seeded: dict[str, Guarded] = {}
    seeds: dict[str, Passed] = fixtures.visible(modules, path, seeded)
    named: dict[str, Passed] = consistent.visible(modules, path, seeded)
    imported: project.Imported = crossed.imported(
        modules,
        path,
        (seeded, fixtures.attributes({**named, **seeds})),
    )
    side_calls: dict[str, str]
    guarded: dict[str, Guarded]
    side_calls, guarded = sides.calls(modules, path, imported.guarded)
    methods: stubbed.Methods = stubbed.methods(modules, path, guarded)
    hints: tuple[Hints, ...] = offers.vetted(modules, path, hinted.get(path, ()))
    # What only a hint can name: the classes the file imports for type checking alone.
    own: offers.Own = offers.own(modules, path) if hints else offers.Own()
    overloaded: dict[str, tuple[ReadSignature, ...]] = {
        **stubbed.overloaded(modules, path, guarded),
        **methods.signatures,
        **own_methods.overloaded(modules, path, guarded),
    }
    return Outside(
        calls={**imported.calls, **side_calls, **decorated.own(modules, path)},
        # With those of the classes the overloaded methods' returns import.
        classes=crossed.guarded_classes(modules, path, imported, guarded),
        hints=hints,
        type_vars=project.type_vars(modules, path),
        defaulted=project.defaulted(modules, path),
        returned=awaits.returned(
            modules,
            path,
            guarded,
            loose.returned(modules, path, guarded, imported.returned),
        ),
        guarded=guarded,
        generics=imported.generics | own.generics,
        generic=dict(imported.generic),
        descriptors=dict(imported.descriptors),
        callees=callers.callees(modules, path),
        resumable=_resumable(modules, path),
        parameters=callers.own_parameters(modules, path),
        overloaded=overloaded,
        installed_classes=stubbed.classes(modules, path),
        read_members=crossed.member_names(modules, path),
        installed_parameters=methods.parameters,
        installed_lineage=own_types.lineages(modules, path, guarded, methods.lineage),
        installed_aliases=methods.aliases,
        checking=own.guarded,
        plain=plain.classes(modules, path),
        members={**imported.members, **plain.members(modules, path)},
        same=linked.same(modules, path, {**offers.imported(path, hints), **guarded}),
        partial=imported.partial,
        tuples=tuples.fields(modules, path, guarded),
        fixtures=seeds,
        named=named,
        beyond=beyond.library_bases(modules, path),
        awaits=awaits.calls(modules, path, guarded),
        values=linked.values(modules, path),
        untyped=linked.untyped(modules, path),
        unions=tuples.unions(modules, path, guarded),
        managers=managed.calls(modules, path, guarded),
        vouched=decorated.vouched(modules, path),
        takers=taken.calls(modules, path, guarded),
        emptied=beyond.emptied(modules, path),
        factories=factories(modules, path),
    )


def factories(modules: project.Index, path: Path) -> frozenset[str]:
    """Find the names the file at `path` imports that are a type's factory where they're defined.

    `TypeVarTuple` as sqlalchemy's `util.typing` re-exports it from `typing_extensions`, followed
    there (`canonical_origin`): what it binds can't be annotated (see `aliased.factory`).

    Returns:
      Them, as the file binds them; none for a file `modules` doesn't have.

    """
    target: project.Module | None
    if (target := module_at(modules, path)) is None:
        return frozenset()
    found: set[str] = set()
    local: str
    origin: Origin
    for local, origin in {**target.guarded, **target.names}.items():
        where: Origin = canonical_origin(modules.modules, origin)
        if where[1] is not None and f"{where[0]}.{where[1]}" in FACTORIES:
            found.add(local)
    return frozenset(found)


def _resumable(modules: project.Index, path: Path) -> bool:
    """Check whether the file at `path`'s check is to be kept for a resume (see `callers.resumable`).

    Returns:
      Whether a checked file calls one of its open functions; yes for a file `modules` doesn't have.

    """
    target: project.Module | None = module_at(modules, path)
    return target is None or target.name in callers.resumable(modules)
