"""A checked module's own stub, `mod.pyi` beside `mod.py`, which a type checker reads before the source.

matplotlib ships one for most of its modules, its source declaring next to nothing: its importers'
calls are typed by the stub's returns, and the module's own where it can write the type as it is.
"""

import ast
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Final

from constricter.fix.core.known import Origin
from constricter.fix.index.origins import origins_of
from constricter.fix.values.tables import Tables, module_tables
from constricter.source import parsed

_STUB: Final = ".pyi"  # as `modules.STUB`, which imports this module


def beside(path: Path, named: str, *, is_package: bool) -> tuple[Tables, dict[str, Origin]] | None:
    """Read a checked module's own stub, `mod.pyi` beside `mod.py`, as a type checker reads it first.

    Returns:
      Its tables, and what each name it binds refers to (its imports' too, which may be only its);
      `None` where there's none, or it can't be read or parsed.

    """
    stub: Path = path.with_suffix(_STUB)
    source: str | None
    if not stub.is_file() or (source := _text(stub)) is None:
        return None
    try:
        tree: ast.Module = ast.parse(source, str(stub))
    except (SyntaxError, ValueError):
        return None
    return module_tables(tree), origins_of(tree, named, is_package=is_package)


def stubbed(own: Tables, stub: Tables, keep: Callable[[str], bool] = lambda _: True) -> Tables:
    """Take a module's stub's declared returns and its classes' members before its own source's.

    `keep`: whether a type the stub declares may be written as it is in the module itself.

    Returns:
      Its tables, with the stub's.

    """
    returns: dict[str, str] = {
        **own.returns,
        **{name: text for name, text in stub.returns.items() if keep(text)},
    }
    methods: dict[str, dict[str, str]] = _members(own.methods, stub.methods, keep)
    return own._replace(
        returns=returns,
        classes=_members(own.classes, stub.classes, keep),
        methods=methods,
        partial={name: text for name, text in own.partial.items() if name not in returns},
        partial_methods={
            owner: {name: text for name, text in each.items() if name not in methods.get(owner, {})}
            for owner, each in own.partial_methods.items()
        },
    )


def _members(
    own: Mapping[str, Mapping[str, str]],
    stub: Mapping[str, Mapping[str, str]],
    keep: Callable[[str], bool],
) -> dict[str, dict[str, str]]:
    """Merge each class's members' types, a stub's before the source's (see `stubbed`).

    Returns:
      Them.

    """
    return {
        owner: {
            **own.get(owner, {}),
            **{name: text for name, text in stub.get(owner, {}).items() if keep(text)},
        }
        for owner in {*own, *stub}
    }


def _text(path: Path) -> str | None:
    """Read a stub's text.

    Returns:
      It, or `None` if it can't be read, or decoded.

    """
    try:
        return parsed.text(path.read_bytes())
    except (OSError, SyntaxError, ValueError):  # UnicodeDecodeError is a ValueError
        return None
