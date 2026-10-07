# SPDX-License-Identifier: MIT
"""`--infer-with`: the names a hint may use are classes and aliases the index knows, no generic one bare."""

import sys
from pathlib import Path
from typing import Final

import pytest

from constricter.fix.core.known import Guarded, Hints, Offered
from constricter.fix.index import offers, project

_SHAPES: Final = """
from typing import Generic, TypeAlias, TypeVar

T = TypeVar("T")
sizes = 3


class Box(Generic[T]):
    pass


class Shape:
    pass


class Line:
    pass


def make() -> Shape:
    return Shape()


Pair = tuple[int, Shape]
Rows: TypeAlias = Shape
Boxes = list[Box[T]]
Same = Shape
if sizes:
    Either = Shape | Line
try:
    Lines = list[Line]
except NameError:
    pass
"""
_USE: Final = """
from typing import TYPE_CHECKING

from .shapes import Line, make

if TYPE_CHECKING:
    from decimal import Decimal
    from operator import itemgetter

    from elsewhere import Thing

    from . import shapes
    from .shapes import T, Box, Boxes, Line, Pair, Shape, make, sizes

x = make()
"""
_AT: Final = (1, 1)


def _package(tmp_path: Path) -> list[Path]:
    """Write `pkg/`: `shapes.py`, an `__init__.py` re-exporting from it, and `use.py`.

    Returns:
      Their paths, `use.py` last.

    """
    package: Path = tmp_path / "pkg"
    package.mkdir()
    paths: list[Path] = [package / "__init__.py", package / "shapes.py", package / "use.py"]
    sources: list[str] = ["from .shapes import Box as Crate\n", _SHAPES, _USE]
    path: Path
    source: str
    for path, source in zip(paths, sources, strict=True):
        _ = path.write_text(source, encoding="utf-8")
    return paths


@pytest.mark.parametrize(
    ("offered", "shown", "kept"),
    [
        (Offered("Shape", ("from .shapes import Shape",)), "Shape", True),
        (Offered("Shape", ("from pkg.shapes import Shape",)), "Shape", True),
        (Offered("Box[int]", ("from .shapes import Box",)), "Box[int]", True),
        (Offered("shapes.Box[int]", ("from .shapes import Box",)), "Box[int]", True),
        (Offered("Decimal", ("from decimal import Decimal",)), "Decimal", True),  # `hinted`'s to judge
        (Offered("Box", ("from .shapes import Box",)), "Box", False),  # a generic class, bare
        (Offered("Crate", ("from pkg import Crate",)), "Crate", False),  # through a re-export
        (Offered("B | None", ("from .shapes import Box as B",)), "B | None", False),
        (Offered("list[Box]", ("from .shapes import Box",)), "list[Box]", False),
        (Offered("shapes.Box[int]", ("from .shapes import Box",)), "Box", False),  # bare as it's shown
        (Offered("sizes", ("from .shapes import sizes",)), "sizes", False),  # not a class
        (Offered("shapes", ("from . import shapes",)), "shapes", False),  # a module
        (Offered("Thing", ("from elsewhere import Thing",)), "Thing", False),  # not a checked file's
        (Offered("pkg.shapes.Shape", ("import pkg.shapes",)), "Shape", False),  # names no class
        (Offered("Shape", ("from v3.0.0.c import Shape",)), "Shape", False),  # no module's name
        (Offered("Pair", ("from .shapes import Pair",)), "Pair", True),  # a type alias: a subscript
        (Offered("Rows", ("from .shapes import Rows",)), "Rows", True),  # one annotated `TypeAlias`
        (Offered("Either | None", ("from .shapes import Either",)), "Either | None", True),  # under an `if`
        (Offered("Lines", ("from .shapes import Lines",)), "Lines", True),  # under a `try`
        (Offered("Boxes[int]", ("from .shapes import Boxes",)), "Boxes[int]", True),
        (Offered("Boxes", ("from .shapes import Boxes",)), "Boxes", False),  # a generic alias, bare
        (Offered("Same", ("from .shapes import Same",)), "Same", False),  # a bare name's: not indexed
    ],
)
def test_an_edits_import_must_name_a_class_and_no_generic_one_bare(
    tmp_path: Path,
    offered: Offered,
    shown: str,
    *,
    kept: bool,
) -> None:
    """A hint's name may be a module's, and a generic class shown bare has arguments unknown: no import.

    A type alias (a name annotated `TypeAlias`, or bound to a subscript or a union) is taken as a class is.
    """
    paths: list[Path] = _package(tmp_path)
    hints: tuple[Hints, ...] = (Hints("basedpyright", {_AT: shown}, {_AT: offered}),)
    found: Hints = offers.vetted(project.index(paths), paths[-1], hints)[0]
    assert found.types == {_AT: shown}
    assert found.offered == ({_AT: offered} if kept else {})


def test_an_installed_packages_private_module_isnt_imported_from(tmp_path: Path) -> None:
    """A class a hint places in an installed package's private module may move with its next release."""
    paths: list[Path] = _package(tmp_path)
    private: Path = paths[1].with_name("_plane.py")
    _ = private.write_text("class Line: ...\n", encoding="utf-8")
    catalog: project.Index = project.index([*paths, private])
    offered: Offered = Offered("Line", ("from pkg._plane import Line",))
    hints: tuple[Hints, ...] = (Hints("pyrefly", {_AT: "Line"}, {_AT: offered}),)
    assert offers.vetted(catalog, paths[-1], hints)[0].offered == {_AT: offered}  # a checked file's
    catalog.modules["pkg._plane"] = catalog.modules["pkg._plane"]._replace(installed=True)
    assert offers.vetted(catalog, paths[-1], hints)[0].offered == {}


def test_hints_without_edits_are_left_as_they_are(tmp_path: Path) -> None:
    """Hints that offer nothing aren't looked at: a file the index doesn't have is no trouble."""
    hints: tuple[Hints, ...] = (Hints("ty", {_AT: "int"}), Hints("basedpyright"))
    assert offers.vetted(project.index([]), tmp_path / "missing.py", hints) is hints


@pytest.mark.skipif(sys.version_info < (3, 12), reason="`type` statements are Python 3.12+")
def test_a_type_statement_is_an_alias(tmp_path: Path) -> None:
    """`type X = ...` is indexed as an alias, generic if it has type parameters of its own."""
    path: Path = tmp_path / "aliases.py"
    _ = path.write_text("type Pair = tuple[int, str]\ntype Many[T] = list[T]\n", encoding="utf-8")
    assert project.index([path]).modules["aliases"].aliases == {"Pair": False, "Many": True}


def test_the_classes_a_file_imports_for_type_checking_are_its_own(tmp_path: Path) -> None:
    """Of a file's `if TYPE_CHECKING:` imports, the classes and aliases: no module, value, or what runs."""
    paths: list[Path] = _package(tmp_path)
    catalog: project.Index = project.index(paths)
    own: offers.Own = offers.own(catalog, paths[-1])
    assert own.guarded == {
        "Decimal": Guarded(("decimal", "Decimal"), None),
        "itemgetter": Guarded(("operator", "itemgetter"), None),
        "Box": Guarded(("pkg.shapes", "Box"), None),
        "Boxes": Guarded(("pkg.shapes", "Boxes"), None),
        "Pair": Guarded(("pkg.shapes", "Pair"), None),
        "Shape": Guarded(("pkg.shapes", "Shape"), None),
    }
    assert own.generics == {"itemgetter", "Box", "Boxes"}
    assert offers.own(catalog, tmp_path / "missing.py") == offers.Own()
    assert offers.own(catalog, tmp_path / "notebook.ipynb") == offers.Own()
