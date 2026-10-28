"""What makes a type, not a value, is bound without an annotation: it isn't reported, nor counted."""

import textwrap
from pathlib import Path
from typing import Final

from constricter import Checks, Coverage, Offence, annotation_coverage, check_source
from constricter.fix.core.known import Outside
from constricter.fix.index import across, project

_SOURCE: Final = """
import collections
import enum
import typing as t
from collections import namedtuple
from typing import NewType, ParamSpec, TypeVar

if sys.version_info >= (3, 12):
    from typing import TypeAliasType
else:
    from typing_extensions import TypeAliasType
from typing_extensions import TypedDict

from other import TypeVar as Unrelated

T = TypeVar("T")
P = ParamSpec("P")
U = t.TypeVar("U")
UserId = NewType("UserId", int)
Plugin = TypeAliasType("Plugin", list[T], type_params=(T,))
Named = t.TypeAliasType("Named", int)
Pair = namedtuple("Pair", "a b")
Other = collections.namedtuple("Other", "a")
Color = enum.Enum("Color", "RED GREEN")
Movie = TypedDict("Movie", {"name": str})
Row = t.NamedTuple("Row", [("a", int)])
V = Unrelated("V")
made = make("y")


def f() -> None:
    W = TypeVar("W")
"""


def test_what_a_type_factory_makes_is_neither_reported_nor_counted() -> None:
    """A `TypeVar`, a `NewType` or a functional class, however `typing`, `enum` or `collections` is imported.

    An annotation would make a type checker take the name for a variable. Another module's
    `TypeVar` is any call.
    """
    source: str = textwrap.dedent(_SOURCE)
    assert [o.name for o in check_source(source, checks=Checks(all_scopes=True))] == ["V", "made"]
    assert annotation_coverage(source, Checks(all_scopes=True)) == Coverage(0, 2)


_USES: Final = """\
from .util.typing import TypeVar, TypeVarTuple
Ts = TypeVarTuple("Ts")
T = TypeVar("T")
"""


def test_a_factory_another_checked_file_re_exports_makes_a_type_too(tmp_path: Path) -> None:
    """`TypeVarTuple` as a package's `util.typing` re-exports it, followed to `typing_extensions`.

    Not a class of the same name that package defines itself.
    """
    package: Path = tmp_path / "pkg"
    (package / "util").mkdir(parents=True)
    written: dict[str, str] = {
        "__init__.py": "",
        "util/__init__.py": "",
        "util/typing.py": "from typing_extensions import TypeVarTuple as TypeVarTuple\nclass TypeVar: ...\n",
        "uses.py": _USES,
    }
    name: str
    text: str
    for name, text in written.items():
        _ = (package / name).write_text(text, encoding="utf-8")
    catalog: project.Index = project.index(sorted(tmp_path.rglob("*.py")))
    uses: Path = package / "uses.py"
    assert across.factories(catalog, uses) == {"TypeVarTuple"}
    assert across.factories(catalog, tmp_path / "missing.py") == set()
    found: list[Offence] = check_source(
        uses.read_text(encoding="utf-8"),
        checks=Checks(all_scopes=True),
        outside=Outside(factories=across.factories(catalog, uses)),
    )
    assert [o.name for o in found] == ["T"]
