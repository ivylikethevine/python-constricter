"""`--fix` on the members of a checked file's own generic classes, bound by the receiver's arguments."""

import sys
import textwrap
from pathlib import Path

import pytest

from constricter import Checks, check_source
from constricter.cli import command as cli

_SOURCE: str = """
from typing import Generic, TypeVar

T = TypeVar("T")
K = TypeVar("K")
V = TypeVar("V")
D = TypeVar("D")

class Row: ...

class Result(Generic[T]):
    items: list[T]

    def __init__(self) -> None:
        self.last: T | None = None

    def first(self) -> T | None:
        return None

    def all(self) -> list[T]:
        return self.items

    def count(self) -> int:
        return 0

    def copied(self) -> "Self":
        return self

    def get(self, default: D) -> T | D:
        return default

    @property
    def head(self) -> T:
        return self.items[0]

class Pairs(Generic[K, V]):
    def pair(self) -> tuple[K, V]: ...

class Keyed(Pairs[str, V]):
    def count(self): ...

class Rows(Result[Row]):
    def m(self) -> None:
        own_first = self.first()
        own_items = self.items

def f(
    rows: Result[Row], bare: Result, maybe: Result[int | None], keyed: Keyed[float], wrong: Pairs[int]
) -> None:
    first = rows.first()
    every = rows.all()
    counted = rows.count()
    items = rows.items
    last = rows.last
    head = rows.head
    copied = rows.copied()
    got = rows.get(1)
    bare_first = bare.first()
    bare_count = bare.count()
    once = maybe.first()
    pair = keyed.pair()
    keyed_count = keyed.count()
    wrong_pair = wrong.pair()
"""


def _found(source: str) -> dict[str, tuple[str | None, bool]]:
    return {o.name: (o.fix, o.unsafe) for o in check_source(textwrap.dedent(source), checks=Checks())}


def test_a_generic_classes_members_are_bound_by_the_receivers_arguments() -> None:
    """A member naming its parameters takes the receiver's arguments; one naming none is as declared.

    Not where the receiver is bare (a checker knows nothing of its parameters), nor given another
    number of arguments, nor for a member naming another type variable. A generic base's members are
    bound by the class's own arguments, unless the class binds the name itself.
    """
    assert _found(_SOURCE) == {
        "own_first": ("Row | None", False),
        "own_items": ("list[Row]", False),
        "first": ("Row | None", False),
        "every": ("list[Row]", False),
        "counted": ("int", False),
        "items": ("list[Row]", False),
        "last": ("Row | None", True),  # a read of a union, as any class's
        "head": ("Row", False),
        "copied": ("Result[Row]", False),  # `Self`, quoted
        "got": (None, False),  # `D`, the method's own
        "bare_first": (None, False),
        "bare_count": ("int", False),
        "once": ("int | None", False),
        "pair": ("tuple[str, float]", False),
        "keyed_count": (None, False),  # bound by `Keyed` itself, with no return
        "wrong_pair": (None, False),
    }


def test_a_generic_method_returning_self_gives_the_receiver() -> None:
    """`Self`, bare, is the receiver's own type, its arguments too."""
    source: str = """
    from typing import Generic, Self, TypeVar

    T = TypeVar("T")

    class Box(Generic[T]):
        def again(self) -> Self:
            return self

    def f(box: Box[int]) -> None:
        again = box.again()
    """
    assert _found(source) == {"again": ("Box[int]", False)}


@pytest.mark.skipif(sys.version_info < (3, 12), reason="`class C[T]` is Python 3.12's syntax")
def test_a_type_parameter_list_names_the_parameters() -> None:
    """`class Box[T]`'s parameters are its list's; one with a `ParamSpec` or `TypeVarTuple` has none known."""
    source: str = """
    class Box[T]:
        def get(self) -> T: ...

    class Call[**P, R]:
        def result(self) -> R: ...

    def f(box: Box[int], call: Call[[int], str]) -> None:
        got = box.get()
        result = call.result()
    """
    assert _found(source) == {"got": ("int", False), "result": (None, False)}


def test_a_generic_classes_parameters_are_unknown_past_a_listed_argument_no_type_variable() -> None:
    """`Generic[T, S]`, `S` not a type variable the module defines: its members aren't bound."""
    source: str = """
    from typing import Generic, TypeVar

    from other import S

    T = TypeVar("T")

    class Pair(Generic[T, S]):
        def first(self) -> T: ...

    def f(pair: Pair[int, str]) -> None:
        first = pair.first()
    """
    assert _found(source) == {"first": (None, False)}


def test_a_member_is_looked_for_eight_generic_bases_up_at_most() -> None:
    """Past them, it's left untyped."""
    chain: str = "\n".join(f"class C{at}(C{at - 1}[T]): ..." for at in range(1, 10))
    source: str = f"""
from typing import Generic, TypeVar

T = TypeVar("T")

class C0(Generic[T]):
    def get(self) -> T: ...

{chain}

def f(deep: C8[int], deeper: C9[int]) -> None:
    found = deep.get()
    lost = deeper.get()
"""
    assert _found(source) == {"found": ("int", False), "lost": (None, False)}


_RESULTS: str = """
from typing import Generic, TypeVar

from pkg.rows import Row

T = TypeVar("T")

class Result(Generic[T]):
    def first(self) -> T | None:
        return None

    def rows(self) -> list[tuple[T, Row]]:
        return []

    def count(self) -> int:
        return 0
"""
_USER: str = """
from pkg.results import Result
import pkg.results as r

def f(result: Result[int], other: "r.Result[str]", bare: Result) -> None:
    first = result.first()
    rows = result.rows()
    spelled = other.first()
    counted = bare.count()
    unknown = bare.first()
"""
_USER_FIXED: str = """
from pkg.results import Result
import pkg.results as r
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from pkg.rows import Row

def f(result: Result[int], other: "r.Result[str]", bare: Result) -> None:
    first: int | None = result.first()
    rows: list[tuple[int, Row]] = result.rows()
    spelled: str | None = other.first()
    counted: int = bare.count()
    unknown = bare.first()
"""


def test_another_files_generic_class_is_bound_by_the_receivers_arguments(tmp_path: Path) -> None:
    """As the file's own: its members' other names written as the file can, by an import if need be."""
    (tmp_path / "pkg").mkdir()
    sources: dict[str, str] = {
        "pkg/__init__.py": "",
        "pkg/rows.py": "class Row: ...\n",
        "pkg/results.py": _RESULTS,
        "user.py": _USER,
    }
    name: str
    source: str
    for name, source in sources.items():
        _ = (tmp_path / name).write_text(textwrap.dedent(source), encoding="utf-8")
    _ = cli.main(["--fix", "-q", "--jobs=1", "--select=LVA001", str(tmp_path)])
    assert (tmp_path / "user.py").read_text(encoding="utf-8") == textwrap.dedent(_USER_FIXED)
