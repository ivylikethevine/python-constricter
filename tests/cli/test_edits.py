# SPDX-License-Identifier: MIT
"""`--infer-with`: what a hint's own edits would write, and the imports they name."""

from pathlib import Path
from typing import Final

import pytest

from constricter.cli import edits
from constricter.cli.protocol import Json, Object
from constricter.fix.known import Offered

_SOURCE: Final = (
    "from shapes import (\n    make,\n)\nfrom . import util\nfrom ..deep.er import one\n\nx = make()\n"
)
_AT: Final[Object] = {"line": 6, "character": 1}  # where `x` ends
_TOP: Final[Object] = {"line": 0, "character": 0}
_LAST: Final = 50  # the last line `_locate` takes for one of the file's


def _locate(position: Object) -> tuple[int, int] | None:
    """Read a position as a line (from 1) and column, one past line `_LAST` as past the file's end.

    Returns:
      Them, or `None`.

    """
    line: int = int(str(position["line"]))
    return None if line > _LAST else (line + 1, int(str(position["character"])))


def _edit(start: Object, text: str) -> Json:
    """Make an edit inserting `text` at `start`.

    Returns:
      It.

    """
    return {"range": {"start": start, "end": start}, "newText": text}


def _offered(*added: Json, text: str = ": Shape", source: str = _SOURCE) -> Offered | None:
    """Read a hint showing `Shape` whose edits write `text` at the name's end, then `added`.

    Returns:
      What they'd write.

    """
    hint: Object = {"position": _AT, "label": ": Shape", "textEdits": [_edit(_AT, text), *added]}
    return edits.offered(hint, "Shape", _locate, edits.FromImports(source.split("\n")))


def test_a_hint_without_edits_offers_nothing() -> None:
    """A hint with no edits, or whose edit is its label alone, says no more than its label."""
    existing: edits.FromImports = edits.FromImports(_SOURCE.split("\n"))
    assert edits.offered({"position": _AT, "label": ": Shape"}, "Shape", _locate, existing) is None
    assert _offered() is None
    assert _offered(text="") is None
    imported: Object = {"position": _AT, "label": ": Shape", "textEdits": [_edit(_TOP, "import shapes\n")]}
    assert edits.offered(imported, "Shape", _locate, existing) is None  # an import for no annotation


def test_the_annotation_is_as_the_edit_writes_it() -> None:
    """The annotation's edit may spell a class through a module the file imports."""
    assert _offered(text=": shapes.Shape") == Offered("shapes.Shape")


@pytest.mark.parametrize(
    ("added", "imports"),
    [
        ("from shapes import Shape\n\n\n", ("from shapes import Shape",)),
        ("from shapes import Shape as S, Box\n", ("from shapes import Shape as S", "from shapes import Box")),
        ("import shapes\nimport a.b as c\n", ("import shapes", "import a.b as c")),
        ("from . import Shape\n", ("from . import Shape",)),
        ("from ..deep import Shape\n", ("from ..deep import Shape",)),
    ],
)
def test_an_added_import_is_a_statement_per_name(added: str, imports: tuple[str, ...]) -> None:
    """Each import an edit adds, wherever it puts it, binds one name."""
    assert _offered(_edit(_TOP, added)) == Offered("Shape", imports)


@pytest.mark.parametrize(
    ("start", "added", "imports"),
    [
        ({"line": 1, "character": 8}, ", Shape", ("from shapes import Shape",)),
        ({"line": 1, "character": 4}, "Shape, Box, ", ("from shapes import Shape", "from shapes import Box")),
        ({"line": 3, "character": 18}, ", Shape", ("from . import Shape",)),
        ({"line": 4, "character": 25}, ", Shape", ("from ..deep.er import Shape",)),
    ],
)
def test_a_name_inserted_into_an_import_is_from_its_module(
    start: Object,
    added: str,
    imports: tuple[str, ...],
) -> None:
    """Names inserted into a `from` import the file has are imported from the module it names."""
    assert _offered(_edit(start, added)) == Offered("Shape", imports)


@pytest.mark.parametrize(
    ("start", "added"),
    [
        ({"line": 6, "character": 0}, ", Shape"),  # not in an import
        ({"line": 99, "character": 0}, ", Shape"),  # past the file's end
        ({"line": 1, "character": 8}, ", Shape as S"),  # not plain names
        ({"line": 1, "character": 8}, " "),  # nothing
        ({"line": 1, "character": 8}, "x = 1\n"),  # not an import at all
        (_TOP, ": int"),  # an annotation somewhere else
    ],
)
def test_an_edit_that_isnt_understood_offers_nothing(start: Object, added: str) -> None:
    """An edit that is neither the annotation nor an import leaves the hint to its label."""
    assert _offered(_edit(start, added)) is None


def test_a_file_that_doesnt_parse_has_no_imports_to_insert_into() -> None:
    """An insertion can't be placed in a file that doesn't parse; a whole statement still can."""
    broken: str = "from shapes import make\nx = (\n"
    inserted: Json = _edit({"line": 0, "character": 23}, ", Shape")
    assert _offered(inserted, inserted, source=broken) is None
    assert _offered(_edit(_TOP, "import shapes\n"), source=broken) == Offered("Shape", ("import shapes",))


def test_a_files_imports_are_read_once() -> None:
    """Two insertions into one file's imports read it once."""
    inserted: Json = _edit({"line": 1, "character": 8}, ", Shape")
    assert _offered(inserted, inserted) == Offered(
        "Shape",
        ("from shapes import Shape", "from shapes import Shape"),
    )


def _part(name: str, defined: str | None = None) -> Json:
    """Make a label's part: `name`, with the file it's defined in if there's one.

    Returns:
      It.

    """
    part: Object = {"value": name}
    if defined is not None:
        # Absolute on Windows too, where a path without a drive has no file URI.
        part["location"] = {"uri": Path(defined).absolute().as_uri(), "range": {"start": _TOP, "end": _TOP}}
    return part


@pytest.mark.parametrize(
    ("defined", "imports"),
    [
        ("/venv/lib/python3.14/site-packages/shapes/__init__.pyi", ("from shapes import Shape",)),
        ("/venv/lib/python3.14/site-packages/shapes/plane.py", ("from shapes.plane import Shape",)),
        ("/venv/lib/python3.14/site-packages/shapes-stubs/plane.pyi", ("from shapes.plane import Shape",)),
        ("/venv/lib/python3.14/site-packages/shapes.py", ("from shapes import Shape",)),
        ("/cache/pyrefly_bundled_typeshed_4f6b/shapes/__init__.pyi", ("from shapes import Shape",)),
        (
            "/cache/pyrefly_bundled_typeshed_third_party_20/shapes/plane.pyi",
            ("from shapes.plane import Shape",),
        ),
        ("/cache/pyrefly_bundled_typeshed_4f6b/builtins.pyi", None),  # a builtin takes no import
        ("/somewhere/typeshed/stdlib/shapes.pyi", None),  # a stub of who knows what module
    ],
)
def test_a_label_naming_where_a_class_is_defined_imports_it_from_that_module(
    defined: str,
    imports: tuple[str, ...] | None,
) -> None:
    """A hint with no edits whose label's parts carry locations: each class is its file's module's."""
    label: list[Json] = [_part(": "), _part("dict"), _part("["), _part("Shape", defined), _part("]", defined)]
    hint: Object = {"position": _AT, "label": label, "textEdits": []}
    found: Offered | None = edits.offered(hint, "dict[Shape]", _locate, edits.FromImports([]))
    assert found == (None if imports is None else Offered("dict[Shape]", imports))


def test_a_project_files_class_is_imported_from_its_module(tmp_path: Path) -> None:
    """A file outside any installed package is the module its package folders name, once a name."""
    package: Path = tmp_path / "pkg"
    package.mkdir()
    _ = (package / "__init__.py").write_text("", encoding="utf-8")
    defined: str = str(package / "shapes.py")
    hint: Object = {
        "position": _AT,
        "label": [_part("Shape", defined), _part(" | "), _part("Shape", defined)],
    }
    found: Offered | None = edits.offered(hint, "Shape | Shape", _locate, edits.FromImports([]))
    assert found == Offered("Shape | Shape", ("from pkg.shapes import Shape",))
    plain: Object = {"position": _AT, "label": ": Shape"}
    assert edits.offered(plain, "Shape", _locate, edits.FromImports([])) is None
    nowhere: Json = {
        "value": "Shape",
        "location": {"uri": "untitled:", "range": {"start": _TOP, "end": _TOP}},
    }
    assert (
        edits.offered({"position": _AT, "label": [nowhere]}, "Shape", _locate, edits.FromImports([])) is None
    )
