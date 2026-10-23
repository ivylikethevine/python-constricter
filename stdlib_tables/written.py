"""What the generator writes that no one configuration's reading holds.

A class's members apart from its ancestors' (`inherited`), and the modules only some platforms
have (`platform_only`).
"""

from stdlib_tables.reading import Table
from stdlib_tables.stubs import MINORS, PLATFORMS, Imported, ModuleRef, Namespace, Stubs


def inherited(members: dict[str, Table], bases: Table) -> dict[str, dict[str, str | None]]:
    """Write each class's members as it has them apart from its public ancestors (`bases`).

    `--fix` resolves a member as a class's own entry, else its ancestors' in order (each resolved
    the same way): a member the class has as its nearest ancestor does is left out, and one it
    hides (a member it defines that the tables can't hold) is `None`. Checked against the full
    tables, entry by entry.

    Returns:
      Each class's entries.

    Raises:
      RuntimeError: if they don't resolve to the full tables.

    """
    found: dict[str, dict[str, str | None]] = {}
    klass: str
    for klass in dict.fromkeys([*members, *bases]):
        through: dict[str, str] = {}
        ancestor: str
        name: str
        value: str
        for ancestor in bases.get(klass, "").split(",") if klass in bases else []:
            for name, value in members.get(ancestor, {}).items():
                _ = through.setdefault(name, value)
        own: Table = members.get(klass, {})
        entries: dict[str, str | None] = {
            **{name: value for name, value in own.items() if through.get(name) != value},
            **dict.fromkeys(through.keys() - own.keys()),
        }
        if entries:
            found[klass] = entries
    if any(_resolved(found, bases, klass) != table for klass, table in members.items()):
        message: str = "a class's members resolve otherwise than they were read"
        raise RuntimeError(message)
    return found


def _resolved(own: dict[str, dict[str, str | None]], bases: Table, klass: str) -> Table:
    """Resolve a class's members as `--fix` does (`stdlib._member`): its own entries, then each ancestor's.

    Returns:
      Them.

    """
    found: dict[str, str | None] = {}
    ancestor: str
    for ancestor in bases.get(klass, "").split(",") if klass in bases else []:
        name: str
        value: str
        for name, value in _resolved(own, bases, ancestor).items():
            _ = found.setdefault(name, value)
    found.update(own.get(klass, {}))
    return {name: value for name, value in found.items() if value is not None}


def platform_only(stubs: Stubs) -> Table:
    """Find the modules some platform has nothing public in: those a checker there finds nothing in.

    Returns:
      Each one's platforms that have it (`winreg`: `win32`), comma-separated.

    """
    found: Table = {}
    module: str
    for module in stubs.modules():
        has: list[str] = [
            platform
            for platform in PLATFORMS
            if any(_binds(stubs.namespace(module, (platform, minor))) for minor in MINORS)
        ]
        if has and len(has) < len(PLATFORMS):
            found[module] = ",".join(has)
    return found


def _binds(space: Namespace | None) -> bool:
    """Check whether a module's namespace defines a public name of its own.

    Returns:
      Whether it does.

    """
    return space is not None and any(
        not name.startswith("_") and not isinstance(binding, (Imported, ModuleRef))
        for name, binding in space.names.items()
    )
