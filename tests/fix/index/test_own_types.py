# SPDX-License-Identifier: MIT
"""`--fix` for a checked file's overloads decided by the checked files' own classes."""

import textwrap
from pathlib import Path
from typing import Final

from constricter import Offence, check_source
from constricter.cli import schedule
from constricter.fix.index import own_types, project

_FRAME: Final = """
from collections.abc import Iterable, Mapping
from typing import overload

from elsewhere import Outer


class Base:
    pass


class DataFrame(Base):
    pass


class Series(Base):
    pass


class Wide(DataFrame):
    pass


class Odd(Outer):
    pass


@overload
def concat(objs: Iterable[DataFrame] | Mapping[str, DataFrame], axis: int = ...) -> DataFrame: ...
@overload
def concat(objs: Iterable[Series] | Mapping[str, Series], axis: int = ...) -> Series: ...
def concat(objs, axis=0):
    return next(iter(objs))


@overload
def copy(obj: DataFrame) -> DataFrame: ...
@overload
def copy(obj: Series | None) -> Series: ...
def copy(obj):
    return obj


@overload
def keyed(obj: Mapping[str, DataFrame] | None) -> int: ...
@overload
def keyed(obj: str) -> str: ...
def keyed(obj):
    return obj


@overload
def loose(obj: DataFrame | Outer) -> int: ...
@overload
def loose(obj: Series) -> str: ...
def loose(obj):
    return obj
"""
_MAIN: Final = """
import pkg.frame as fr
from pkg.frame import DataFrame, Odd, Series, Wide, concat, copy, keyed, loose


class Local(Series):
    pass


def f(df: DataFrame, s: Series, wide: Wide, odd: Odd, local: Local, other: fr.Series, unknown) -> None:
    frames = concat([df, df])
    series = concat((s, s), axis=1)
    wides = concat([wide])
    locals_ = concat({local})
    mixed = concat([df, s])
    lost = concat(unknown)
    odds = concat([odd])
    one = copy(df)
    two = copy(s)
    three = copy(wide)
    four = copy(other)
    five = copy(odd)
    six = loose(s)
    seven = keyed([df])
    eight = keyed("k")
"""


def _package(root: Path) -> tuple[project.Index, Path]:
    """Write a package of classes and overloads, and a file calling them.

    Returns:
      Their index, and the calling file.

    """
    (root / "pkg").mkdir()
    name: str
    source: str
    for name, source in (("__init__", ""), ("frame", _FRAME)):
        _ = (root / "pkg" / f"{name}.py").write_text(textwrap.dedent(source), encoding="utf-8", newline="\n")
    main: Path = root / "main.py"
    _ = main.write_text(textwrap.dedent(_MAIN), encoding="utf-8", newline="\n")
    return project.index(sorted(root.rglob("*.py"))), main


def test_each_class_a_file_names_has_its_lineage(tmp_path: Path) -> None:
    """Its own and its bases' paths through the checked files; `?` where one can't be followed."""
    catalog: project.Index
    main: Path
    catalog, main = _package(tmp_path)
    found: dict[str, tuple[str, ...]] = own_types.lineages(catalog, main, {})
    assert found["DataFrame"] == ("pkg.frame.DataFrame", "pkg.frame.Base")
    assert found["Wide"] == ("pkg.frame.Wide", "pkg.frame.DataFrame", "pkg.frame.Base")
    assert found["Local"] == ("main.Local", "pkg.frame.Series", "pkg.frame.Base")
    assert found["fr.Series"] == found["Series"]
    assert found["Odd"] == ("pkg.frame.Odd", "?")
    assert not own_types.lineages(catalog, tmp_path / "missing.py", {})


def test_an_overload_is_picked_by_the_checked_files_classes(tmp_path: Path) -> None:
    """An argument's class, or a sequence's elements', by its lineage: not one that can't be followed."""
    catalog: project.Index
    main: Path
    catalog, main = _package(tmp_path)
    found: list[Offence] = check_source(
        main.read_text(encoding="utf-8"),
        outside=schedule.outside(catalog, main, {}),
    )
    assert {o.name: o.fix for o in found} == {
        "frames": "DataFrame",
        "series": "Series",
        "wides": "DataFrame",
        "locals_": "Series",
        "one": "DataFrame",
        "two": "Series",
        "three": "DataFrame",
        "four": "Series",
        # `loose`'s first takes another package's class too: it says nothing of a `Series`.
        **dict.fromkeys(("mixed", "lost", "odds", "five", "six")),
        "seven": None,  # a mapping's parameter says nothing of a list's elements
        "eight": "str",
    }
