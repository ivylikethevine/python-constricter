"""The compiled wheel's mypyc hook, as `pyproject.toml` sets it."""

import tomllib
from pathlib import Path
from typing import IO, Final, TypeAlias, cast

_PYPROJECT: Final = Path(__file__).resolve().parents[1] / "pyproject.toml"
_Table: TypeAlias = dict[str, object]  # a table, as `tomllib` reads it
_HOOK: Final = ("tool", "hatch", "build", "targets", "wheel", "hooks", "mypyc")


def _table(table: _Table, *keys: str) -> _Table:
    """Read the table under `keys`, one in another.

    Returns:
      It.

    """
    key: str
    for key in keys:
        table = cast("_Table", table[key])
    return table


def test_the_mypyc_hook_is_off_and_asks_for_what_its_group_pins() -> None:
    """A build asks for what a build without isolation has from the `mypyc` dependency group: no more."""
    file: IO[bytes]
    with _PYPROJECT.open("rb") as file:
        project: _Table = tomllib.load(file)
    hook: _Table = _table(project, *_HOOK)
    group: list[str] = cast("list[str]", _table(project, "dependency-groups")["mypyc"])
    assert hook["enable-by-default"] is False
    assert set(cast("list[str]", hook["dependencies"])) <= set(group)
