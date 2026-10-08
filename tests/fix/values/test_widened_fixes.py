# SPDX-License-Identifier: MIT
"""`fix-widen`: wider types than a value's own, each line marked, and replaced once its type is known."""

import json
import textwrap
from pathlib import Path
from typing import Final, TypeAlias

import pytest

from constricter import Checks, FixPolicy, Offence, annotation_coverage, check_source
from constricter.cli import command as cli
from constricter.cli import schedule
from constricter.fix.core import fixes
from constricter.fix.index import linked, project
from constricter.noqa import lines
from constricter.offences import WIDEN_KINDS
from constricter.rules import widened
from constricter.rules.checker import Coverage

_WIDEN: Final = Checks(fixes=FixPolicy(widen=frozenset({"untyped-parameters"})))
_ANY: Final = ("Any", False, frozenset({"untyped-parameters"}))
# Each offence's fix, whether it's a guess, and the mechanisms that decided it.
_Found: TypeAlias = dict[str, tuple[str | None, bool, frozenset[str]]]
_IMPORTED: Final = "from typing import Any\ndef f(reader):\n    a: Any = reader  # constricter: auto\n"
_MARK: Final = "# constricter: auto\n"
_MARKED: Final = [
    "    a: Any = reader  # constricter: auto\n",
    "    b: Any = reader.read()  # constricter: auto\n",
    "    c: Any = count  # constricter: auto\n",
    "    j: Any = only  # constricter: auto\n",
    "    reader2: Any = reader  # note  # constricter: auto\n",
    "        y: Any = other  # constricter: auto\n",
    "        w: Any = given  # constricter: auto\n",
]
_REPLACED: Final = [
    "    a: io.StringIO = reader\n",
    "    b: str = reader.read()  # note\n",
    "    c: Any = count  # constricter: auto\n",
    "    d: Any = Box()  # constricter: auto\n",
]
SOURCE: Final = """
from typing import Any


def f(reader, count, flag=False, *rest, key: str = "k", only, **more):
    a = reader
    b = reader.read()
    c = count
    d = flag
    e = reader.name
    g = reader.read(
        1,
    )
    h = key
    i = rest
    j = only
    k = j
    m = n = count
    reader2 = reader  # note
    reader2 = count.next()


class C:
    def m(self, other):
        x = self
        y = other

    @classmethod
    def make(cls, given):
        z = cls
        w = given


def bound_again(seen, kept):
    seen = list(seen)
    p = seen
    for kept in seen:
        q = kept


top = f
"""


def _found(source: str, checks: Checks = _WIDEN) -> _Found:
    found: list[Offence] = check_source(textwrap.dedent(source), checks=checks)
    return {o.name: (o.fix, o.unsafe, o.edit.kinds if o.edit else frozenset()) for o in found}


def test_what_comes_of_an_untyped_parameter_is_any() -> None:
    """A copy of it, or its method's call, on one line: certain, and its own kind.

    Not a parameter with a default (a checker types it by that), `*args` or `**kwargs`, `self` or
    `cls`, one bound again, an attribute of one, or a chained assignment's names.
    """
    found: _Found = _found(SOURCE)
    assert {name: fix for name, fix in found.items() if fix == _ANY} == dict.fromkeys(
        ["a", "b", "c", "j", "reader2", "y", "w"],
        _ANY,
    )
    assert {name for name, fix in found.items() if fix[0] is None} == {
        "d",
        "e",
        "g",
        "i",
        "k",
        "m",
        "n",
        "p",
        "q",
    }


def test_a_widening_is_off_unless_asked_for() -> None:
    """Without `fix-widen`, nothing; `fix-ignore` drops it as it does any kind."""
    assert _found(SOURCE, Checks())["a"] == (None, False, frozenset())
    ignoring: Checks = Checks(
        fixes=FixPolicy(ignore=frozenset({"untyped-parameters"}), widen=frozenset({"untyped-parameters"})),
    )
    assert _found(SOURCE, ignoring)["a"] == (None, False, frozenset())


def test_a_widening_needs_the_module_to_name_any() -> None:
    """`Any` is imported where it isn't, as `typing.Any` where the name's taken; else there's no fix."""
    source: str = "def f(reader):\n    a = reader\n"
    found: list[Offence] = check_source(source, checks=_WIDEN)
    assert "".join(fixes.apply(lines(source), found)) == _IMPORTED
    assert [fix[0] for fix in _found("Any = 1\n\n\ndef f(reader):\n    a = reader\n").values()] == [
        "typing.Any",
    ]
    assert [fix[0] for fix in _found("Any = typing = 1\n\n\ndef f(reader):\n    a = reader\n").values()] == [
        None,
    ]
    assert [o.fix for o in check_source("a = b\n", checks=_WIDEN._replace(all_scopes=True))] == [None]


def test_a_widenings_line_is_marked_and_its_edits_say_so() -> None:
    """The mark goes at the line's end, after a comment there; each report format's edits carry it."""
    source: str = textwrap.dedent(SOURCE)
    found: list[Offence] = check_source(source, checks=_WIDEN)
    fixed: list[str] = fixes.apply(lines(source), found)
    assert [line for line in fixed if line.endswith(_MARK)] == _MARKED
    first: Offence = next(o for o in found if o.edit and o.edit.kinds)
    edits: tuple[fixes.Replacement, ...] = fixes.replacements(lines(source), first)
    assert [(edit.prefix, edit.deleted, edit.text) for edit in edits] == [
        ("    a", "", ": Any"),
        ("    a = reader", "", "  # constricter: auto"),
    ]


def test_a_marked_annotation_isnt_vague_and_is_counted_apart() -> None:
    """LVA005 passes over it, and `--coverage` counts it widened, not typed."""
    source: str = """
    from typing import Any

    def f(reader, count):
        a: Any = reader  # constricter: auto
        b: Any = reader  # hand-written
        c: int = count
        if count:
            a: Any = count  # constricter: auto
    """
    found: list[Offence] = check_source(textwrap.dedent(source))
    assert [(o.name, o.code, o.fix) for o in found] == [("b", "LVA005", None)]
    assert annotation_coverage(textwrap.dedent(source)) == Coverage(2, 3, 1)
    assert Coverage(2, 3, 1).percent == pytest.approx(200 / 3)


def test_a_marked_annotation_is_replaced_once_its_type_is_known() -> None:
    """Reported LVA005, with the value's own type in its place and the mark dropped; a guess as any is."""
    source: str = textwrap.dedent(
        """
        import io
        from typing import Any

        class Box:
            pass

        def f(reader: io.StringIO, count):
            a: Any = reader  # constricter: auto
            b: Any = reader.read()  # note  # constricter: auto
            c: Any = count  # constricter: auto
            d: Any = Box()  # constricter: auto
            e: Any  # constricter: auto
            g: (
                Any) = reader  # constricter: auto
            h = b
        """,
    )
    found: list[Offence] = check_source(source)
    assert {o.name: (o.code, o.fix, o.unsafe) for o in found} == {
        "a": ("LVA005", "io.StringIO", False),
        "b": ("LVA005", "str", False),
        "d": ("LVA005", "Box", True),
        "h": ("LVA001", "str", False),  # typed by what `b` is now
    }
    fixed: list[str] = fixes.apply(lines(source), [o for o in found if not o.unsafe])
    assert fixed[8:12] == _REPLACED
    ignoring: Checks = Checks(fixes=FixPolicy(ignore=frozenset({"copy"})))
    assert [o.name for o in check_source(source, checks=ignoring)] == ["b", "d", "h"]


def test_a_class_bodys_marked_annotation_is_left() -> None:
    """A class body is no scope `--fix` writes in: the annotation stays, unreported."""
    source: str = "class C:\n    limit: object = 3  # constricter: auto\n"
    assert check_source(source, checks=Checks(all_scopes=True)) == []


def test_marks_are_found_by_their_columns() -> None:
    """The mark and the space before it, in UTF-8 bytes; not a longer word, nor a line without one."""
    found: dict[int, tuple[int, int]] = widened.marks(
        [
            "é: Any = p  # constricter: auto\n",
            "x = 1  # constricter: automatic\n",
            "y = 2\n",
            'z = "# constricter: auto"\n',
            "w: Any = p  # constricter: auto  \r\n",
        ],
    )
    assert found == {1: (11, 32), 5: (10, 31)}


def test_the_command_takes_fix_widen_from_a_flag_and_pyproject(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """`--fix-widen KINDS` (`all`: every one), or `fix-widen` in `[tool.constricter]`, a list or one name."""
    monkeypatch.chdir(tmp_path)
    path: Path = tmp_path / "demo.py"
    source: str = "from typing import Any\n\n\ndef f(reader):\n    a = reader\n"
    fixed: str = source.replace("a = reader", "a: Any = reader  # constricter: auto")
    setting: str
    for setting in ('["untyped-parameters"]', '"all"'):
        _ = path.write_text(source, encoding="utf-8")
        _ = (tmp_path / "pyproject.toml").write_text(f"[tool.constricter]\nfix-widen = {setting}\n", "utf-8")
        assert cli.main(["--fix", "-q", "demo.py"]) == cli.EXIT_CLEAN
        assert path.read_text(encoding="utf-8") == fixed
    (tmp_path / "pyproject.toml").unlink()
    flag: str
    for flag in ("--fix-widen=untyped-parameters", "--fix-widen=all"):
        _ = path.write_text(source, encoding="utf-8")
        assert cli.main(["--fix", "-q", flag, "demo.py"]) == cli.EXIT_CLEAN
        assert path.read_text(encoding="utf-8") == fixed
    assert cli.main(["--coverage", "demo.py"]) == cli.EXIT_CLEAN
    assert capsys.readouterr().out.endswith("Total: 0/1 typed (0.0%), 1 widened in 1 file(s).\n")
    assert cli.main(["--coverage", "--format=json", "demo.py"]) == cli.EXIT_CLEAN
    assert json.loads(capsys.readouterr().out)["widened"] == 1


def test_an_unknown_widening_exits_2(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A name that isn't a widening's id is an error, as a flag or in `[tool.constricter]`."""
    exit_info: pytest.ExceptionInfo[SystemExit]
    with pytest.raises(SystemExit) as exit_info:
        _ = cli.main(["--fix-widen=literal", "-q", "."])
    assert exit_info.value.code == cli.EXIT_ERROR
    assert capsys.readouterr().err.endswith("no wider type is called literal (see docs/FIXES.md)\n")
    monkeypatch.chdir(tmp_path)
    _ = (tmp_path / "pyproject.toml").write_text('[tool.constricter]\nfix-widen = ["nope"]\n', "utf-8")
    with pytest.raises(SystemExit) as exit_info:
        _ = cli.main([])
    assert exit_info.value.code == cli.EXIT_ERROR
    assert capsys.readouterr().err.endswith("[tool.constricter] has an invalid fix-widen = ['nope']\n")


_ALL: Final = Checks(
    fixes=FixPolicy(widen=frozenset({"unions", "vague", "empty-containers", "mixed-containers"})),
)
WIDER: Final = """
from typing import Any


def load() -> dict[str, Any]:
    return {}


def f(flag, other):
    a = 1
    if flag:
        a = "x"
    b = load()
    c = []
    d = {}
    e = set()
    g = [1, "a", other]
    h = (flag, other)
    i = {"k": other, "n": 2}
    j = {
        other: 1,
        **i,
    }
    k = {flag, other}
    m = []
    m.append(3)
    n = 1.5
    n = "s"
    n = None
    p = 1
    p = "s"
    p = b""
    p = 2.5
    q = 1
    q = other
    r = []
    r = other
    s = load()
    s = other
    t = other
    u = v = []
    w = "text"
"""
_WIDER: Final = [
    ("a", "int | str", True, frozenset({"literal", "rebound", "unions"})),
    ("b", "dict[str, Any]", True, frozenset({"call", "vague"})),
    ("c", "list[Any]", False, frozenset({"empty-containers"})),
    ("d", "dict[Any, Any]", False, frozenset({"empty-containers"})),
    ("e", "set[Any]", False, frozenset({"empty-containers"})),
    ("g", "list[Any]", False, frozenset({"mixed-containers"})),
    ("h", "tuple[Any, ...]", False, frozenset({"mixed-containers"})),
    ("i", "dict[str, Any]", False, frozenset({"mixed-containers"})),
    ("j", "dict[Any, Any]", False, frozenset({"mixed-containers"})),
    ("k", "set[Any]", False, frozenset({"mixed-containers"})),
    ("m", "list[int]", True, frozenset({"filled", "literal"})),
    ("n", "float | str | None", True, frozenset({"literal", "rebound", "unions"})),
    ("q", "int", True, frozenset({"literal", "rebound"})),  # a later value of no known type: as it was
    ("w", "str", False, frozenset({"literal"})),
]
_WRITTEN: Final = [
    "    a: int | str  # constricter: auto\n",
    "    b: dict[str, Any] = load()  # constricter: auto\n",
    "    c: list[Any] = []  # constricter: auto\n",
    "    }  # constricter: auto\n",
]


def test_each_wider_type_is_its_own_kind() -> None:
    """A union of two or three types and a vague type are guesses; a container of `Any` is certain.

    Not four types' union, nor one with a value of no known type; and no container or vague type
    for a name bound again, a chained assignment's, or a value of no type at all.
    """
    found: _Found = _found(WIDER, _ALL)
    assert [(name, *fix) for name, fix in found.items() if fix[0] is not None] == _WIDER
    assert {name for name, fix in found.items() if fix[0] is None} == {"p", "r", "s", "t", "u", "v"}
    assert {fix[0] for fix in _found(WIDER, Checks()).values()} == {None, "str", "int", "list[int]"}


def test_a_wider_types_mark_ends_its_statement() -> None:
    """A declaration's own line; an assignment's last line, however many it's on."""
    source: str = textwrap.dedent(WIDER)
    fixed: list[str] = fixes.apply(lines(source), check_source(source, checks=_ALL))
    marked: list[str] = [line for line in fixed if line.endswith(_MARK)]
    assert [marked[0], marked[1], marked[2], marked[8]] == _WRITTEN
    again: list[Offence] = check_source("".join(fixed), checks=_ALL._replace(vague=-1))
    assert {o.name for o in again} == {"p", "r", "s", "t", "u", "v"}


def test_a_widening_types_nothing_read_of_its_name() -> None:
    """What a marked annotation says isn't its value's type: a second pass finds no more than the first."""
    source: str = "def f(other):\n    stack = []\n    top = stack.pop()\n    return top, other\n"
    checks: Checks = Checks(fixes=FixPolicy(widen=frozenset({"vague", "empty-containers"})))
    once: str = "".join(fixes.apply(lines(source), check_source(source, checks=checks)))
    assert [(o.name, o.fix) for o in check_source(once, checks=checks)] == [("top", None)]


def test_late_wider_types_are_for_a_functions_names() -> None:
    """Not a module's or a class's, which something out of sight may bind again; nor without `Any` to name."""
    source: str = "CACHE = {}\n\n\nclass C:\n    seen = []\n"
    checks: Checks = _ALL._replace(all_scopes=True)
    assert [o.fix for o in check_source(source, checks=checks)] == [None, None]
    unnamed: str = "Any = typing = 1\ndef f():\n    c = {}\n"
    assert [o.fix for o in check_source(unnamed, checks=_ALL)] == [None]


_CALLS: Final = Checks(fixes=FixPolicy(widen=frozenset({"untyped-calls", "unknown-calls"})))
_SPELLED: Final = "Any"
_UNTYPED: Final = (_SPELLED, False, frozenset({"untyped-calls"}))
_UNKNOWN: Final = (_SPELLED, False, frozenset({"unknown-calls"}))
CALLS: Final = """
import functools
from typing import Any, TypeVar

import external

T = TypeVar("T")


def helper(x):
    return x.y


def commented(x):
    # type: (T) -> T
    return x.y


def same(x: T) -> T:
    return x


@functools.cache
def cached(x):
    return x.y


async def later(x):
    return x.y


def twice(x):
    return x.y


def twice(x):
    return x.z


class Base:
    def up(self):
        return self.q


class Left(Base):
    pass


class Right(Base):
    def side(self):
        return self.q


class C(Left, Right):
    alias = helper
    if external.FLAG:
        def guarded(self):
            return self.q

    def own(self):
        value = self.q
        return value

    def value(self):
        return self.q

    @staticmethod
    def stat(v):
        return v.w

    @classmethod
    def make(cls):
        made = cls.stat(1)
        return made

    @property
    def prop(self):
        return self.q

    @prop.setter
    def prop(self, new):
        self.q = new

    class Inner:
        def own(self):
            return 1

    async def run(self, other):
        a = helper(other)
        b = self.own()
        c = self.up()
        d = self.side()
        e = self.stat(other)
        f = await later(other)
        g = self.guarded()
        h = self.value()
        i = helper(
            other,
        )
        j = helper(other)
        j = 3
        k = other.method()
        m = external.load(1)
        n = await other.fetch()
        p = later(other)
        q = self.prop()
        r = self.alias()
        s = self.missing()
        t = same(other)
        u = commented(other)
        v = cached(other)
        w = twice(other)
        x = other.factory()()
        y = other.attr
        z = await other
        return a, b, c, d, e, f, g, h, i, j, k, m, n, p, q, r, s, t, u, v, w, x, y, z


class Outside(external.Base):
    def run(self):
        aa = self.up()
        return aa


class Under(Imported):
    def run(self):
        ab = self.up()

        def inner():
            ac = self.run()
            return ac

        return ab, inner


def shadowing(helper, other):
    ad = helper(other)
    return ad


def plain(self):
    ae = self.own()
    return ae
"""


def test_a_call_of_no_known_type_is_any() -> None:
    """Of the module's own function that declares no return, one kind; of anything else, another.

    A top-level function by its name, a method of the class or of its bases in the module on
    `self` or `cls` (a function inside the method's too), awaited where it's an `async def`;
    multi-line, or bound again later. Not one a parameter shadows, one decorated, declared by a type
    comment or defined twice, a class's name bound otherwise, a method the module's classes don't
    define, one under a base from elsewhere, nor a `self` that's no method's.
    """
    found: _Found = _found(CALLS, _CALLS)
    assert {name for name, fix in found.items() if fix == _UNTYPED} == {*"abcdefghij", "made", "ac"}
    assert {name for name, fix in found.items() if fix == _UNKNOWN} == {
        *"kmnpqrstuvwx",
        "aa",
        "ab",
        "ad",
        "ae",
    }
    assert {name: fix[0] for name, fix in found.items() if fix[0] != _SPELLED} == dict.fromkeys(
        ["value", "y", "z"],
    )


def test_each_call_kind_is_asked_for_alone() -> None:
    """One kind writes nothing of the other's; neither, where the module can't name `Any`."""
    kind: str
    for kind in ("untyped-calls", "unknown-calls"):
        checks: Checks = Checks(fixes=FixPolicy(widen=frozenset({kind})))
        assert {fix[2] for fix in _found(CALLS, checks).values() if fix[0] == _SPELLED} == {frozenset({kind})}
    unnamed: str = "Any = typing = 1\ndef helper(x):\n    return x.y\ndef f(o):\n    a = helper(o)\n"
    assert [fix[0] for fix in _found(unnamed, _CALLS).values()] == [None]


def test_a_widened_calls_mark_ends_its_statement() -> None:
    """After the call's last line; a second pass finds nothing more."""
    source: str = textwrap.dedent(CALLS)
    fixed: list[str] = fixes.apply(lines(source), check_source(source, checks=_CALLS))
    marked: list[str] = [line for line in fixed if line.endswith(_MARK)]
    assert [marked[1], marked[9], marked[10]] == [
        "        a: Any = helper(other)  # constricter: auto\n",
        "        )  # constricter: auto\n",
        "        j: Any = helper(other)  # constricter: auto\n",
    ]
    again: list[Offence] = check_source("".join(fixed), checks=_CALLS)
    assert {o.name for o in again if o.fix is not None} == set()


TARGETS: Final = """
from typing import Any


def helper(x):
    return x.y


def load() -> list[dict[str, Any]]:
    return []


def f(other, rows: list[int]):
    for a, b in other.pairs():
        pass
    for c in helper(other):
        pass
    for d, e in enumerate(other.rows()):
        pass
    g, (h, *i) = helper(other)
    j, k = 1, other.load()
    with other.lock(), other.open() as m, helper(1) as (n, p):
        pass
    for q in rows:
        pass
    for r in other:
        pass
    s, t = other
    for u in [other, 1]:
        pass
    v = w = other.load()
    for x in load():
        pass
    y, z = (af := other.load()), 1
    return a, b, c, d, e, g, h, i, j, k, m, n, p, q, r, s, t, u, v, w, x, y, z, af


async def later(other):
    async for aa in other.rows():
        pass
    async with other.open() as ab, helper(1) as (ac, ad):
        pass
    for ae in await other.load():
        pass
    ae = 1
    return aa, ab, ac, ad, ae


for top in helper(1):
    pass
"""
_VAGUE: Final = "    x: dict[str, Any]  # constricter: auto\n"
_DECLARED: Final = [
    "    a: Any  # constricter: auto\n",
    "    b: Any  # constricter: auto\n",
    "    for a, b in other.pairs():\n",
    "        pass\n",
    "    c: Any  # constricter: auto\n",
    "    for c in helper(other):\n",
    "        pass\n",
    "    d: int\n",
    "    e: Any  # constricter: auto\n",
    "    for d, e in enumerate(other.rows()):\n",
    "        pass\n",
    "    g: Any  # constricter: auto\n",
    "    h: Any  # constricter: auto\n",
    "    i: Any  # constricter: auto\n",
    "    g, (h, *i) = helper(other)\n",
    "    j: int\n",
    "    k: Any  # constricter: auto\n",
    "    j, k = 1, other.load()\n",
    "    m: Any  # constricter: auto\n",
    "    n: Any  # constricter: auto\n",
    "    p: Any  # constricter: auto\n",
    "    with other.lock(), other.open() as m, helper(1) as (n, p):\n",
]


def test_what_a_loop_an_unpacking_or_a_with_takes_of_a_call_is_any() -> None:
    """Each name, by the call's kind, whatever it's bound to later; a type too vague to write is `vague`'s.

    A loop's target, an unpacking's names (a display's, each by its own value), a `with`'s, `async`
    or not. Not what's taken of anything but a call (a parameter, a display, which is no
    container's type here), a chained assignment's names, a `:=`'s, nor a module's.
    """
    checks: Checks = Checks(fixes=FixPolicy(widen=WIDEN_KINDS), all_scopes=True)
    found: _Found = _found(TARGETS, checks)
    assert {name for name, fix in found.items() if fix == _UNTYPED} == {*"cghinp"}
    assert {name for name, fix in found.items() if fix == _UNKNOWN} == {*"abekm", "aa", "ab", "ae"}
    assert {name: fix[0] for name, fix in found.items() if fix[0] != _SPELLED} == {
        "d": "int",
        "j": "int",
        "q": "int",
        "x": "dict[str, Any]",
        "z": "int",
        **dict.fromkeys(["r", "s", "t", "u", "v", "w", "y", "af", "ac", "ad", "top"]),
    }
    assert found["x"][1:] == (True, frozenset({"call", "loop", "vague"}))
    source: str = textwrap.dedent(TARGETS)
    assert _VAGUE in fixes.apply(lines(source), check_source(source, checks=checks))


def test_a_widened_targets_declaration_goes_before_its_statement() -> None:
    """Marked on its own line; a second pass finds nothing more, and `--coverage` counts each widened."""
    source: str = textwrap.dedent(TARGETS)
    fixed: list[str] = fixes.apply(lines(source), check_source(source, checks=_CALLS))
    start: int = fixed.index(_DECLARED[0])
    end: int = start + len(_DECLARED)
    assert fixed[start:end] == _DECLARED
    again: list[Offence] = check_source("".join(fixed), checks=_CALLS)
    assert {o.name for o in again if o.fix is not None} == set()
    assert annotation_coverage("".join(fixed)) == Coverage(4, 29, 14)


_UTIL: Final = """
import pytest


def helper(x):
    return x.y


def typed(x) -> int:
    return x.y


def commented(x):
    # type: (int) -> int
    return x.y


async def later(x):
    return x.y


@pytest.fixture
def fixed():
    return object()


def unused(x):
    return x.y
"""
_MAIN: Final = """
import util
from util import commented, fixed, helper, later, typed, unused


async def f(other):
    a = helper(other)
    b = util.helper(other)
    c = typed(other)
    d = commented(other)
    e = await later(other)
    g = fixed()
    for h in helper(other):
        pass
    i = other.helper()
    return a, b, c, d, e, g, h, i, unused


def shadowing(helper, util):
    j = helper(1)
    k = util.helper(1)
    return j, k
"""


def test_another_checked_files_function_declaring_no_return_is_an_untyped_call(tmp_path: Path) -> None:
    """As the file spells its call, by name or through its module; what a loop takes of it too.

    Not one declaring a return, by a `# type:` comment either, an `async def`, a fixture, one the
    file never calls, nor a name its function binds.
    """
    _ = (tmp_path / "util.py").write_text(textwrap.dedent(_UTIL), encoding="utf-8")
    main: Path = tmp_path / "main.py"
    _ = main.write_text(textwrap.dedent(_MAIN), encoding="utf-8")
    catalog: project.Index = project.index(sorted(tmp_path.glob("*.py")))
    assert linked.untyped(catalog, main) == {"helper", "util.helper"}
    assert not linked.untyped(catalog, tmp_path / "missing.py")
    found: list[Offence] = check_source(
        main.read_text(encoding="utf-8"),
        checks=_CALLS,
        outside=schedule.outside(catalog, main, {}),
    )
    fixed: _Found = {o.name: (o.fix, o.unsafe, o.edit.kinds if o.edit else frozenset()) for o in found}
    assert {name for name, fix in fixed.items() if fix == _UNTYPED} == {"a", "b", "h"}
    assert {name for name, fix in fixed.items() if fix == _UNKNOWN} == {"e", "g", "i", "j", "k"}
    assert {name: fix[0] for name, fix in fixed.items() if fix[0] != _SPELLED} == {"c": "int", "d": "int"}
