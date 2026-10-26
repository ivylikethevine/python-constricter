"""`fix-widen`'s calls of no known type, each line marked, and replaced once its type is known.

Each call kind; what a loop, an unpacking or a `with` takes of one; and another checked file's
function that declares no return.
"""

import textwrap
from pathlib import Path
from typing import Final, TypeAlias

from constricter import Checks, FixPolicy, Offence, annotation_coverage, check_source
from constricter.fix.core import fixes
from constricter.fix.index import across, linked, project
from constricter.noqa import lines
from constricter.offences import WIDEN_KINDS
from constricter.rules.checker import Coverage

# Each offence's fix, whether it's a guess, and the mechanisms that decided it.
_Found: TypeAlias = dict[str, tuple[str | None, bool, frozenset[str]]]
_MARK: Final = "# constricter: auto\n"
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


def _found(source: str, checks: Checks) -> _Found:
    found: list[Offence] = check_source(textwrap.dedent(source), checks=checks)
    return {o.name: (o.fix, o.unsafe, o.edit.kinds if o.edit else frozenset()) for o in found}


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


def test_a_method_is_found_through_bases_that_cycle_or_share_one() -> None:
    """Each base is looked in once: a cycle ends, no method found, and a base two share gives its own."""
    source: str = (
        "class A(B):\n    def f(self):\n        a = self.m()\n"
        "class B(A):\n    pass\n"
        "class Root:\n    def m(self):\n        return x.y\n"
        "class Left(Root):\n    pass\n"
        "class Right(Root):\n    pass\n"
        "class Both(Left, Right):\n    def g(self):\n        b = self.m()\n"
    )
    found: _Found = _found(source, _CALLS)
    assert (found["a"], found["b"]) == (_UNKNOWN, _UNTYPED)  # the cycle's, no method found


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
        outside=across.outside(catalog, main, {}),
    )
    fixed: _Found = {o.name: (o.fix, o.unsafe, o.edit.kinds if o.edit else frozenset()) for o in found}
    assert {name for name, fix in fixed.items() if fix == _UNTYPED} == {"a", "b", "h"}
    assert {name for name, fix in fixed.items() if fix == _UNKNOWN} == {"e", "g", "i", "j", "k"}
    assert {name: fix[0] for name, fix in fixed.items() if fix[0] != _SPELLED} == {"c": "int", "d": "int"}


REDECLARED: Final = """
from typing import Any


def load() -> list[dict[str, Any]]:
    return []


def f(rows: list[int], other, pairs: dict[str, bytes]):
    x: Any  # constricter: auto
    for x in rows:
        pass
    y: Any  # constricter: auto
    for y in rows:
        pass
    y = "s"
    z: Any  # constricter: auto
    for z in other.load():
        pass
    k: Any  # constricter: auto
    v: Any  # note  # constricter: auto
    for k, v in pairs.items():
        pass
    w: Any  # constricter: auto
    for w in load():
        pass
    a: int | str  # constricter: auto
    a = 1
    a = "s"
"""
_REDECLARED: Final = ["    x: int\n", "    k: str\n", "    v: bytes  # note\n"]


def test_a_marked_declaration_is_replaced_once_its_names_type_is_known() -> None:
    """A loop's target's, certain as its own fix would be; the mark goes with it.

    Not one bound again, one whose value still has no type or none `--fix` may write, nor a union's.
    """
    source: str = textwrap.dedent(REDECLARED)
    found: list[Offence] = check_source(source)
    assert [(o.name, o.code, o.fix, o.unsafe) for o in found] == [
        ("x", "LVA005", "int", False),
        ("k", "LVA005", "str", False),
        ("v", "LVA005", "bytes", False),
    ]
    fixed: list[str] = fixes.apply(lines(source), found)
    assert [line for line in fixed if line in _REDECLARED] == _REDECLARED
    assert check_source("".join(fixed)) == []
