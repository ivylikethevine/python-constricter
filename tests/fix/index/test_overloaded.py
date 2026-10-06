# SPDX-License-Identifier: MIT
"""`--fix` for calls to a checked file's function defined with `@overload`, where the arguments decide."""

import textwrap
from pathlib import Path
from typing import Final

from constricter.cli import command as cli
from constricter.fix.index import project, stubbed

FRAME: Final = """
from typing import Generic, Literal, TypeVar, overload

from pkg.kinds import Alias, Imported

T = TypeVar("T")


class Frame: ...


class Series: ...


class Box(Generic[T]): ...


@overload
def concat(objs: list[Frame], axis: int = ...) -> Frame: ...
@overload
def concat(objs: list[Series], axis: int = ...) -> Series: ...
def concat(objs, axis=0):
    return objs[0]


@overload
def load(path: str, *, raw: Literal[True]) -> bytes: ...
@overload
def load(path: str, *, raw: Literal[False] = ...) -> str: ...
def load(path, *, raw=False):
    return ""


@overload
def make(kind: Literal["f"]) -> Frame: ...
@overload
def make(kind: Literal["s"]) -> Series: ...
def make(kind):
    return Frame()


@overload
def wrap(x: int) -> Imported: ...
@overload
def wrap(x: str) -> str: ...
def wrap(x):
    return x


@overload
def named(x: int) -> Alias: ...
@overload
def named(x: str) -> str: ...
def named(x):
    return x


@overload
def boxed(x: int) -> Box[int]: ...
@overload
def boxed(x: str) -> Box: ...
def boxed(x):
    return Box()


@overload
def bare(x: int): ...
@overload
def bare(x: str) -> str: ...
def bare(x):
    return x


def own() -> None:
    k = load("p")
"""
KINDS: Final = """
from typing import TypeVar

Imported = TypeVar("Imported")
Alias = int | str
"""
USE: Final = """
from pkg.frame import Frame, Series, bare, boxed, concat, load, make, named, wrap


def use(frames: list[Frame], other, flag: bool) -> None:
    a = concat(frames)
    b = concat(other)
    c = load("p")
    d = load("p", raw=True)
    e = load("p", raw=flag)
    f = make("f")
    g = wrap("x")
    h = named(1)
    i = boxed(1)
    j = bare("x")
"""
FIXED: Final = (
    "    a = concat(frames)\n",  # a checked file's class: whether a parameter takes it isn't read
    "    b = concat(other)\n",
    "    c: str = load(",
    "    d: bytes = load(",
    "    e = load(",  # a `bool` that isn't a literal: either overload
    "    f: Frame = make(",
    "    g = wrap(",  # an overload returns a type variable: none of them is taken
    "    h: Alias = named(",
    "    i = boxed(",  # a generic class without its arguments
    "    j = bare(",  # an overload declares no return
)
OWN: Final = "    k: str = load("
PLAIN: Final = "from pkg.frame import make\n\n\ndef use() -> None:\n    made = make('s')\n"
PLAIN_FIXED: Final = (
    "if TYPE_CHECKING:\n    from pkg.frame import Series\n",
    "    made: Series = make('s')\n",
)


def _write(root: Path, name: str, source: str) -> Path:
    path: Path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    _ = path.write_text(textwrap.dedent(source), encoding="utf-8", newline="\n")
    return path


def _project(root: Path) -> Path:
    _ = _write(root, "pkg/__init__.py", "")
    _ = _write(root, "pkg/kinds.py", KINDS)
    _ = _write(root, "pkg/frame.py", FRAME)
    return _write(root, "pkg/use.py", USE)


def test_a_call_its_arguments_decide_is_typed(tmp_path: Path) -> None:
    """By the overload they match, in the file defining it and in one importing it: certain fixes."""
    use: Path = _project(tmp_path)
    _ = cli.main(["--fix", "-q", str(tmp_path)])
    fixed: str = use.read_text(encoding="utf-8")
    assert all(line in fixed for line in FIXED), fixed
    assert OWN in (tmp_path / "pkg" / "frame.py").read_text(encoding="utf-8")


def test_a_class_the_file_doesnt_import_is_imported_for_type_checking(tmp_path: Path) -> None:
    """As another file's declared return is."""
    _ = _project(tmp_path)
    plain: Path = _write(tmp_path, "pkg/plain.py", PLAIN)
    _ = cli.main(["--fix", "-q", str(tmp_path)])
    fixed: str = plain.read_text(encoding="utf-8")
    assert all(part in fixed for part in PLAIN_FIXED), fixed


def test_without_imports_to_record_the_signatures_are_read_all_the_same(tmp_path: Path) -> None:
    """Asked without a record of the file's imports for type checking, as its tests do."""
    use: Path = _project(tmp_path)
    catalog: project.Index = project.index(sorted(tmp_path.rglob("*.py")))
    assert stubbed.overloaded(catalog, use).keys() == {"concat", "load", "make", "named"}
