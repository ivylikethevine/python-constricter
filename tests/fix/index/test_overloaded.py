# SPDX-License-Identifier: MIT
"""`--fix` for calls to a checked file's function defined with `@overload`, where the arguments decide."""

import textwrap
from pathlib import Path
from typing import Final

from constricter.cli import command as cli
from constricter.fix.index import own_methods, project, stubbed

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
    "    a: Frame = concat(frames)\n",  # by the checked files' classes its elements are
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


CLASHING_LIBRARY: Final = """
import types
from typing import overload


@overload
def optional(name: str, errors: str) -> types.ModuleType | None: ...
@overload
def optional(name: str) -> types.ModuleType: ...
def optional(name, errors="raise"):
    return None
"""
CLASHING_USE: Final = """
from pkg.optional import optional


def table() -> None:
    types: list[int] = [1]


def count() -> None:
    found = optional("x", errors="ignore")
"""


def test_an_overloads_return_the_file_cant_import_is_no_fix(tmp_path: Path) -> None:
    """`types` is the file's own local: `types.ModuleType` can't be imported there, nor written."""
    _ = _write(tmp_path, "pkg/__init__.py", "")
    _ = _write(tmp_path, "pkg/optional.py", CLASHING_LIBRARY)
    use: Path = _write(tmp_path, "pkg/use.py", CLASHING_USE)
    _ = cli.main(["--fix", "-q", str(tmp_path)])
    assert use.read_text(encoding="utf-8") == textwrap.dedent(CLASHING_USE)


SHAPES: Final = """
from typing import Protocol, Self, TypeAlias, TypeVar, overload

from pkg.keys import Key

Number = TypeVar("Number", int, float)
Rebound: TypeAlias = str
Rebound = bytes


class Sized(Protocol):
    def __len__(self) -> int: ...


@overload
def pick(key: Key) -> int: ...
@overload
def pick(key: int) -> str: ...
def pick(key):
    return key


@overload
def sized(x: Sized) -> int: ...
@overload
def sized(x: int) -> str: ...
def sized(x):
    return x


@overload
def numeric(x: Number) -> bytes: ...
@overload
def numeric(x: str) -> bool: ...
def numeric(x):
    return x


@overload
def twice(x: Rebound) -> int: ...
@overload
def twice(x: int) -> str: ...
def twice(x):
    return x


class Frame:
    @overload
    def get(self, key: str) -> int: ...
    @overload
    def get(self, key: int) -> "Frame": ...
    def get(self, key):
        return key

    @overload
    def me(self, key: str) -> Self: ...
    @overload
    def me(self, key: int) -> int: ...
    def me(self, key):
        return self

    @overload
    def typed(self: "Frame", key: str) -> int: ...
    @overload
    def typed(self, key: int) -> str: ...
    def typed(self, key):
        return key

    @overload
    def odd(self, key: str): ...
    @overload
    def odd(self, key: int) -> int: ...
    def odd(self, key):
        return key

    @overload
    @staticmethod
    def bare() -> int: ...
    @overload
    @staticmethod
    def bare(key: int) -> str: ...
    @staticmethod
    def bare(key=0):
        return key


class Sub(Frame):
    pass


class Twice:
    pass


class Twice:
    @overload
    def get(self, key: str) -> int: ...
    @overload
    def get(self, key: int) -> str: ...
    def get(self, key):
        return key


def own(frame: Frame, sub: Sub, twice: Twice) -> None:
    held = frame.get("k")
    under = sub.get("k")
    same = sub.get(1)
    again = twice.get("k")
"""
KEYS: Final = "from typing import TypeAlias\n\nKey: TypeAlias = str | bytes\n"
CALLING: Final = """
import pkg.shapes
from pkg import shapes
from pkg.shapes import Frame


def use(frame: Frame, names: list[str], other: shapes.Frame) -> None:
    a = shapes.pick("a")
    b = shapes.pick(1)
    c = shapes.sized(names)
    d = shapes.sized(1)
    e = shapes.numeric(1.5)
    f = shapes.numeric("a")
    g = pkg.shapes.pick(b"a")
    h = shapes.twice(1)
    i = frame.get("k")
    j = frame.get(1)
    k = other.get(1)
    m = frame.me(1)
    n = frame.bare(1)
    o = frame.missing(1)
    p = frame.odd(1)
    q = frame.typed(1)
"""
CALLED: Final = (
    "    a: int = shapes.pick(",  # called through its module, imported from its package
    "    b: str = shapes.pick(",  # an alias another file declares: not what it stands for
    "    c: int = shapes.sized(",  # a protocol, by its members
    "    d: str = shapes.sized(",
    "    e: bytes = shapes.numeric(",  # a type variable's constraints
    "    f: bool = shapes.numeric(",
    "    g: int = pkg.shapes.pick(",
    "    h = shapes.twice(",  # a name bound twice is no alias
    "    i: int = frame.get(",  # a method's overloads, on a receiver typed as its class
    "    j: Frame = frame.get(",
    "    k: Frame = other.get(",
    "    m = frame.me(",  # an overload returns `Self`: none of them is taken
    "    n = frame.bare(",
    "    o = frame.missing(",
    "    p = frame.odd(",  # an overload declares no return
    "    q = frame.typed(",  # or its `self`
)
OWN_METHODS: Final = (
    "    held: int = frame.get(",
    "    under: int = sub.get(",  # its base's
    "    same = sub.get(",  # the base itself: its `Self`, maybe
    "    again = twice.get(",  # a class defined twice
)


def test_an_overload_is_matched_through_what_checked_files_declare(tmp_path: Path) -> None:
    """A parameter's alias, protocol or type variable; a method's overloads; a function through its module."""
    _ = _write(tmp_path, "pkg/__init__.py", "")
    _ = _write(tmp_path, "pkg/keys.py", KEYS)
    shapes: Path = _write(tmp_path, "pkg/shapes.py", SHAPES)
    calling: Path = _write(tmp_path, "pkg/calling.py", CALLING)
    catalog: project.Index = project.index(sorted(tmp_path.rglob("*.py")))
    found: set[str] = set(own_methods.overloaded(catalog, calling, {}))
    assert found == {"Frame.get", "shapes.Frame.get", "pkg.shapes.Frame.get"}
    assert not own_methods.overloaded(catalog, tmp_path / "missing.py", {})
    assert catalog.modules["pkg.keys"].reads("Key")
    assert not catalog.modules["pkg.keys"].reads("TypeAlias")
    assert catalog.modules["pkg.calling"].kinds is None
    _ = cli.main(["--fix", "-q", "--jobs=1", str(tmp_path)])
    fixed: str = calling.read_text(encoding="utf-8")
    assert all(line in fixed for line in CALLED), fixed
    fixed = shapes.read_text(encoding="utf-8")
    assert all(line in fixed for line in OWN_METHODS), fixed
