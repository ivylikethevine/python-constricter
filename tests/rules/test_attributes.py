"""LVA013 (opt-in): an instance attribute first stored by a method's `self.x = value`, unannotated."""

import textwrap
from pathlib import Path
from typing import Final

import pytest

from constricter import Checks, Offence, check_source
from constricter.cli import command as cli
from constricter.fix.core import fixes
from constricter.offences import FixPolicy
from constricter.rules.checker import Coverage, annotation_coverage

UNANNOTATED_ATTRIBUTE: Final = "LVA013"
_ON: Final = Checks(attributes=True)
_STORED: Final = "class C:\n    def __init__(self) -> None:\n        self.count = 0\n        self.count = 1\n"
SOURCE: Final = """
class Base:
    size = 0

    def __init__(self, n: int) -> None:
        self.n = n
        self.items = []
        self.a, self.b = 1, 2
        self.label: str = "x"
        self.commented = 1  # type: int
        self.size = 3
        self.__dict__ = {}
        self.pair = (1, 2)

    def add(self, item: str) -> None:
        self.items.append(item)
        self.a = 3
        self.shown = 2

        def inner() -> None:
            self.hidden = 1

    @staticmethod
    def make(self) -> None:
        self.static = 1

    @property
    def shown(self) -> int:
        return 1


class Sub(Base):
    def __init__(self) -> None:
        self.n = 4
        self.extra = "e"
        del self.gone


class Other(Unknown):
    def __init__(self) -> None:
        self.x = 1


class Meta(metaclass=M):
    def __init__(self) -> None:
        self.x = 1


class Twice:
    pass


class Twice:
    def __init__(self) -> None:
        self.x = 1


class Last(Late):
    def __init__(self) -> None:
        self.y = 1


class Late(object):
    def __init__(self) -> None:
        self.z = 1
"""


def _found(source: str, checks: Checks = _ON) -> list[tuple[int, int, str, str | None, bool]]:
    found: list[Offence] = check_source(textwrap.dedent(source).lstrip("\n"), checks=checks)
    return [(o.line, o.col, o.name, o.fix, o.unsafe) for o in found if o.code == UNANNOTATED_ATTRIBUTE]


def test_undeclared_attributes_of_a_plain_class_are_reported_where_first_stored() -> None:
    """Each at its first plain `self.x = value`, its fix the class's stores joined, as a guess."""
    assert _found(SOURCE) == [
        (5, 8, "self.n", "int", True),
        (6, 8, "self.items", "list[str]", True),
        (7, 16, "self.b", None, False),  # an unpacking is no place for an annotation
        (12, 8, "self.pair", "tuple[int, int]", True),
        (16, 8, "self.a", None, False),  # at its plain store; untyped, as one store isn't
        (34, 8, "self.extra", "str", True),
        (35, 12, "self.gone", None, False),
        (59, 8, "self.y", "int", True),  # a base defined after it is plain too
        (64, 8, "self.z", "int", True),
    ]


def test_off_unless_selected() -> None:
    """Without `Checks(attributes=True)` there's no LVA013 at all."""
    assert _found(SOURCE, Checks()) == []


def test_the_fix_is_its_declaration() -> None:
    """`self.x: T = value`, which a type checker reads as the attribute's; then nothing's left."""
    offences: list[Offence] = check_source(_STORED, checks=_ON)
    fixed: str = "".join(fixes.apply(_STORED.splitlines(keepends=True), offences))
    assert fixed == _STORED.replace("self.count = 0", "self.count: int = 0")
    assert _found(fixed) == []
    assert [o.likely for o in offences] == [True]


OPTIONAL: Final = """
from typing import Literal, cast


class C:
    def __init__(self, v: object) -> None:
        self.conn = None
        self.mixed = None
        self.unknown = None
        self.closed = None
        self.plain = "a"
        self.quoted = None

    def open(self, v: object) -> None:
        self.conn = 3
        self.mixed = "a"
        self.mixed = 1
        self.unknown = f()
        self.plain = 1
        self.quoted = cast(Literal["a"], v)

        def inner() -> None:
            self.closed = 1
"""


def test_none_then_one_type_is_their_union() -> None:
    """`None`, then only ever one known `T`: `T | None`, where every store is a plain one in a method."""
    assert _found(OPTIONAL) == [
        (6, 8, "self.conn", "int | None", True),
        (7, 8, "self.mixed", None, False),
        (8, 8, "self.unknown", None, False),
        (9, 8, "self.closed", None, False),
        (10, 8, "self.plain", None, False),
        (11, 8, "self.quoted", None, False),  # a string can't take `| None` where it's evaluated
    ]


NARROWED: Final = """
class Index: ...


class C:
    def __init__(self, index: Index | None = None, size: int | None = None) -> None:
        if not isinstance(index, Index):
            raise ValueError
        self.index = index
        if size is None:
            return
        self.size = size
"""


def test_a_value_the_tests_narrow_is_stored_as_they_leave_it() -> None:
    """A parameter's union, narrowed by a test before the store: the type it leaves, as a binding's."""
    assert _found(NARROWED) == [(8, 8, "self.index", "Index", True), (11, 8, "self.size", "int", True)]


GENERIC: Final = """
from typing import Generic, TypeVar

T = TypeVar("T")


class Box(Generic[T]):
    def __init__(self, item: T) -> None:
        self.item = item


class Plain: ...


class C:
    def __init__(self, thing) -> None:
        self.box = Box(thing)
        self.plain = Plain()
"""


def test_a_generic_class_is_never_written_bare() -> None:
    """A generic class's instance whose arguments aren't known has no fix, as a binding of it hasn't."""
    assert _found(GENERIC) == [(16, 8, "self.box", None, False), (17, 8, "self.plain", "Plain", True)]


def test_the_fix_policy_holds() -> None:
    """`fix-ignore = assigned` drops the fix, not the offence."""
    policy: Checks = _ON._replace(fixes=FixPolicy(ignore=frozenset({"assigned"})))
    assert _found("class C:\n    def __init__(self) -> None:\n        self.x = 0\n", policy) == [
        (3, 8, "self.x", None, False),
    ]


def test_coverage_counts_them() -> None:
    """With LVA013 asked for, each plain class's attribute is a binding, typed where it's declared."""
    source: str = "class C:\n    def __init__(self) -> None:\n        self.x: int = 0\n        self.y = 1\n"
    assert annotation_coverage(source, _ON) == Coverage(1, 2)
    assert annotation_coverage(source) == Coverage(0, 0)


@pytest.mark.parametrize(
    ("args", "reported"),
    [
        ([], False),
        (["--select=LVA0"], False),  # a prefix never selects an opt-in code
        (["--extend-select=LVA012"], False),  # nor does another opt-in code
        (["--extend-select=LVA013"], True),
    ],
)
def test_the_command_reports_it_only_when_named(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    args: list[str],
    reported: bool,  # ruff: ignore[boolean-type-hint-positional-argument]  # a parameter pytest fills in
) -> None:
    """`--select` or `--extend-select` must name LVA013 in full; it's an error from `strict`."""
    path: Path = tmp_path / "box.py"
    _ = path.write_text("class C:\n    def __init__(self) -> None:\n        self.x = 0\n", encoding="utf-8")
    assert cli.main(["-q", *args, str(path)]) == (cli.EXIT_FOUND if reported else cli.EXIT_CLEAN)
    assert (f"error: {UNANNOTATED_ATTRIBUTE}" in capsys.readouterr().out) == reported


def test_explain_says_it_is_opt_in(capsys: pytest.CaptureFixture[str]) -> None:
    """`--explain LVA013` says it's only reported when selected."""
    with pytest.raises(SystemExit):
        _ = cli.main(["--explain", UNANNOTATED_ATTRIBUTE])
    assert capsys.readouterr().out.endswith("suffocate: error (only when selected)\n")
