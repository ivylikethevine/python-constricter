# SPDX-License-Identifier: MIT
"""The installed classes and aliases a module names, and the methods a class's lineage declares.

For `constricter.fix.stubbed`, which reads their methods' signatures.
"""

from collections.abc import Iterator, Mapping, Sequence
from typing import TYPE_CHECKING, TypeAlias

from constricter.fix import project
from constricter.fix.known import Origin
from constricter.fix.modules import Module

if TYPE_CHECKING:
    from constricter.fix.declared import Class, Declarations

# A package's classes (or aliases): each as written after the package's name, and where it's defined.
Packaged: TypeAlias = tuple[tuple[str, Origin], ...]


def method_names(modules: Mapping[str, Module], lineage: Sequence[str]) -> frozenset[str]:
    """Name the methods a class or any of its installed ancestors (its lineage) declares.

    Returns:
      Them.

    """
    found: set[str] = set()
    path: str
    for path in lineage:
        module: str
        name: str
        module, _, name = path.rpartition(".")
        declared: Declarations | None = None if module not in modules else modules[module].declared
        klass: Class | None = None if declared is None else declared.classes.get(name)
        found.update(() if klass is None else klass.methods)
    return frozenset(found)


def classes(
    modules: Mapping[str, Module],
    names: Mapping[str, Origin],
    packaged: dict[tuple[str, bool], "Packaged"],
    *,
    aliases: bool = False,
) -> Iterator[tuple[str, Origin]]:
    """Find the installed classes `names` (a module's) name: imported (`ndarray`), or through a package.

    Through a package, what any of its modules defines or re-exports (`numpy.ndarray`), the package
    imported from another module too (`from pandas._typing import npt`). With
    `aliases`, the installed aliases it names instead (`npt.NDArray`). `packaged`: each package's, as
    read so far.

    Yields:
      Each as the module writes it, and where it's defined.

    """
    local: str
    origin: Origin
    for local, origin in names.items():
        where: Origin = project.canonical_origin(modules, origin)
        if where[1] is not None:
            if declares(modules, where, aliases=aliases):
                yield local, where
            continue
        if (where[0], aliases) not in packaged:
            packaged[where[0], aliases] = tuple(_package_classes(modules, where[0], aliases=aliases))
        suffix: str
        found: Origin
        for suffix, found in packaged[where[0], aliases]:
            yield f"{local}{suffix}", found


def _package_classes(
    modules: Mapping[str, Module],
    package: str,
    *,
    aliases: bool,
) -> Iterator[tuple[str, Origin]]:
    """Find the installed classes (or aliases) a package's modules define or re-export.

    Yields:
      Each as written after the package's name (`.ndarray`, `.linalg.LinAlgError`), and where it's defined.

    """
    name: str
    other: Module
    for name, other in modules.items():
        if other.installed and (name == package or name.startswith(f"{package}.")):
            bound: str
            found: Origin
            for bound, found in other.names.items():
                where: Origin = project.canonical_origin(modules, found)
                if declares(modules, where, aliases=aliases):
                    yield f"{name.removeprefix(package)}.{bound}", where


def declares(modules: Mapping[str, Module], origin: Origin, *, aliases: bool = False) -> bool:
    """Check whether an installed module declares a class (or an alias) under `origin`'s name.

    Returns:
      Whether it does.

    """
    module: Module | None = modules.get(origin[0])
    declared: Declarations | None = None if module is None or not module.installed else module.declared
    return declared is not None and origin[1] in (declared.aliases if aliases else declared.classes)
