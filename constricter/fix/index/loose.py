# SPDX-License-Identifier: MIT
"""What another checked file's unannotated methods return, for the files calling them.

A module's functions' `return`s type their calls in the files importing them (see
`project.returned`); its classes' methods' type `self.method()` under a base of another file's, and
a call on an instance of an imported class, the same way: as guesses, since a subclass may
override one. A file is checked after the modules whose classes it names that have such a method
it calls (`needs`).
"""

from collections.abc import Iterator, Mapping
from pathlib import Path

from constricter.fix.core.known import Guarded, Returns
from constricter.fix.core.signatures import AWAIT
from constricter.fix.index import project
from constricter.fix.index.modules import SUFFIX, Index, Module, module_name


def _classes(catalog: Index, target: Module) -> Iterator[tuple[str, tuple[Module, str]]]:
    """Find the classes `target` names whose module has a method it calls that only `return`s could type.

    Yields:
      Each, as it spells it, and the module defining it and its name there.

    """
    key: str
    defined: tuple[Module, str]
    for key, defined in project.spelled_classes(catalog, target, (target.names, target.attributes), set()):
        if defined[0].name != target.name and defined[0].loose & _called(target):
            yield key, defined


def _called(target: Module) -> frozenset[str]:
    """Name the methods `target` calls on anything, and (after `AWAIT`) those it awaits a call of.

    Returns:
      Them, as `Module.loose` names a class's.

    """
    return target.method_calls | {name for name in target.attributes if name.startswith(AWAIT)}


def needs(catalog: Index, module: Module) -> set[str]:
    """Find the other modules whose classes' unannotated methods `module` may call.

    Returns:
      Their names.

    """
    return {defined[0].name for _, defined in _classes(catalog, module)}


def returned(
    catalog: Index,
    path: Path,
    guarded: dict[str, Guarded] | None = None,
    functions: Returns | None = None,
) -> Returns:
    """Return, for the file at `path`, what `project.returned` does, and the methods it calls too.

    Those of the classes it names, in modules already checked, by each class as it spells it; a
    guessed one's origins as `C.m`. `functions`: `project.returned`'s, if it's worked out already.

    Returns:
      Them; `project.returned`'s alone for a file `catalog` doesn't have.

    """
    found: Returns = functions or project.returned(catalog, path, guarded)
    target: Module | None
    if (target := catalog.modules.get(module_name(path)) if path.suffix == SUFFIX else None) is None:
        return found
    methods: dict[str, dict[str, str]] = {}
    guesses: dict[str, frozenset[str]] = dict(found.guesses)
    key: str
    defined: tuple[Module, str]
    for key, defined in _classes(catalog, target):
        typed: Mapping[str, str] = defined[0].returned.methods.get(defined[1], {})
        wanted: dict[str, str] = {name: each for name, each in typed.items() if name in _called(target)}
        kept: dict[str, str] = (
            project.portable(
                catalog.modules,
                (target, defined),
                key,
                wanted,
                {} if guarded is None else guarded,
            )
            if wanted
            else {}
        )
        if kept:
            methods[key] = kept
        name: str
        for name in kept:
            rests: frozenset[str] | None
            if (rests := defined[0].returned.guesses.get(f"{defined[1]}.{name}")) is not None:
                guesses[f"{key}.{name}"] = rests
    return found._replace(guesses=guesses, methods=methods) if methods else found
